---
name: telemetry
description: >-
  Instala em uma aplicação a camada de telemetria/uso que um painel CENTRAL de
  gestão consome: registra sessões, tempo por tela/funcionalidade, ações por
  usuário, e cada chamada de LLM (provedor, modelo, função, tokens, custo,
  usuário, data/hora) — e expõe um endpoint de EXPORTAÇÃO INCREMENTAL (por
  cursor) para o painel buscar só o que é novo. Use quando o usuário pedir
  "telemetria", "exportar dados de uso", "estatísticas da aplicação", "uso e
  custo de LLM", "tempo por tela/opção", "métricas por usuário", ou "conecta esta
  app ao meu painel central de gestão / aplica o telemetry aqui".
---

# telemetry — métricas de uso + exportação incremental para um painel central

Cada aplicação que recebe este skill passa a:
1. **Registrar eventos** de uso num log append-only local.
2. **Expor um endpoint padrão** que o painel central consome de forma **incremental**
   (por cursor `seq`), trazendo só o que é novo — nunca re-baixar tudo.

O CONTRATO abaixo é **idêntico em todas as apps**, para o painel central falar igual com todas.

## Conceito central: log append-only + cursor
- Tabela **`telemetry_events`** somente-append, com **`seq` (inteiro auto-incremento)** como
  CURSOR estável e monotônico. O painel guarda o último `seq` que viu por app; na próxima vez
  pede `?since_seq=<último>` e recebe só os novos. Ordenado por `seq`. Sem duplicar, sem re-buscar.
- Cada evento também tem `event_id` (UUID) para idempotência.

### Esquema do evento (envelope padrão)
| Campo | Descrição |
|------|-----------|
| `seq` | BIGSERIAL — cursor incremental (PK) |
| `event_id` | UUID — idempotência |
| `app_id` | identifica a aplicação (env `TELEMETRY_APP_ID`) |
| `ts` | timestamp UTC de quando ocorreu |
| `tipo` | `login` `logout` `session_heartbeat` `feature_time` `action` `llm_call` `error` |
| `user_id` / `user_email` / `role` | quem executou (nuláveis) |
| `session_id` | sessão (nulável) |
| `feature` | tela/opção/rota (ex.: "dashboard", "auditoria") |
| `duration_ms` | tempo gasto (para `feature_time`/`session`) |
| `provider` `model` `funcao` | para `llm_call` (ex.: anthropic / claude-sonnet-4-6 / "chat_qa") |
| `tokens_in` `tokens_out` `cache_read` `cost_usd` `latency_ms` | métricas de LLM |
| `meta` | JSON livre para extras |
| `created_at` | quando foi gravado |

> **Privacidade por padrão:** NÃO gravar prompt/resposta de LLM nem PII além do necessário —
> só metadados (tokens, custo, função, usuário, modelo). Conteúdo só se o dono pedir explicitamente.

## O que instalar na app

### 1) Tabela + migração
Crie `telemetry_events` (acima) com índice em `seq` e `ts`. Migração no padrão do projeto
(Alembic/Prisma/Knex). Append-only.

### 2) Função de registro (backend) + ingestão (frontend)
- `registrar_evento(tipo, **campos)` insere uma linha (não-bloqueante / try-except — telemetria
  NUNCA pode quebrar a aplicação).
- **`POST /telemetry/ingest`** (autenticado pelo usuário logado): o FRONT envia eventos de
  `feature_time`/`session_heartbeat` (tempo por tela). Servidor carimba `user_id`/`ts`.

### 3) Capturar LLM (provedor, modelo, tokens, custo, função, usuário)
Envolva a chamada ao provedor (ex.: o `llm.py` deste ecossistema) para emitir `llm_call` com
`provider`, `model`, `funcao`, `tokens_in/out`, `cache_read`, `latency_ms` e `user_id`.
Pegue tokens do `usage_metadata` (langchain) ou do `usage` da resposta. **Custo**: prefira
mandar os TOKENS e deixar o painel central calcular o `cost_usd` por uma tabela de preços única
(preço muda num lugar só); opcionalmente calcule um `cost_usd` local com uma tabela de preços.

### 4) Sessão e tempo por tela ("quanto tempo em cada opção")
- No login → evento `login` + abre `session_id`. No logout/expiração → `logout` com `duration_ms`.
- No FRONT: ao trocar de rota (ou desmontar a tela), envie `feature_time` `{feature, duration_ms,
  session_id}` para `/telemetry/ingest`. Opcional: `session_heartbeat` a cada N min para sessões longas.

### 5) Ações relevantes
Instrumente os handlers/rotas importantes para emitir `action` `{feature, meta}` por usuário.

## Endpoint de EXPORTAÇÃO (o que o painel central consome)
**`GET /telemetry/events?since_seq={n}&limit={k}`** (default limit 1000, máx 5000)
- Autenticação **máquina-a-máquina** por chave dedicada no header `X-Telemetry-Key`
  (env `TELEMETRY_EXPORT_KEY`), separada do login de usuário. **Somente leitura.**
- Resposta:
  ```json
  {
    "app_id": "auditai",
    "events": [ { "seq": 101, "event_id": "...", "ts": "...", "tipo": "llm_call", ... } ],
    "next_seq": 980,        // o painel guarda isto e manda no próximo since_seq
    "has_more": true        // pagine até has_more=false
  }
  ```
- (Opcional) **`GET /telemetry/summary?from=&to=`** → agregados prontos (custo por modelo,
  por usuário, por dia, minutos por tela) para dashboards rápidos do painel.
- (Opcional) **`GET /telemetry/health`** → `{app_id, eventos_total, ultimo_seq}`.

### Como o painel central usa (incremental, por app)
1. Guarda `cursor[app]` (último `next_seq`). Começa em 0.
2. `GET /telemetry/events?since_seq={cursor}` repetidamente até `has_more=false`, acumulando.
3. Atualiza `cursor[app] = next_seq`. Próxima sincronização traz só o novo.
4. Calcula custo a partir dos tokens com sua tabela de preços central.

## Regras (não-negociáveis)
- Telemetria **nunca derruba a aplicação**: todo registro é best-effort (try/except, fila/async).
- **Append-only** + `seq` monotônico → incremental confiável (nunca pule/duplique).
- Export é **read-only**, autenticado por chave própria, com `limit` (paginação) e rate-limit.
- **Sem conteúdo sensível** por padrão (sem prompt/resposta; tokens e metadados, sim).
- `TELEMETRY_EXPORT_KEY` forte, em env, **nunca** versionado (use a fonte de segredos — ver skill `llm-keys`).
- Não apagar eventos não exportados. (Pruning por idade é opcional e só após confirmação de leitura.)

## Padrão para TODAS as apps (para o painel ser genérico)
- Mesmo caminho `/telemetry/events`, mesmo envelope de evento, mesmo cursor `seq`, mesmo header de auth.
- `app_id` único por aplicação (`TELEMETRY_APP_ID`). Assim o painel central integra qualquer app sem código específico.

## Resumo ao terminar
- Onde ficam os eventos (`telemetry_events`), como o painel puxa (`/telemetry/events?since_seq=`),
  e qual a chave de export. Lembre de definir `TELEMETRY_APP_ID` e `TELEMETRY_EXPORT_KEY`.
- Confirme que o registro é best-effort (não quebra a app) e que nenhum conteúdo sensível é enviado.

> Companheiro: o skill `llm-keys` (segredos centrais) guarda `TELEMETRY_EXPORT_KEY`; o `auth-kit`
> fornece `user_id`/`role`/`session` usados nos eventos.
