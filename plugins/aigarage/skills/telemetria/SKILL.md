---
name: telemetria
description: >-
  Instrumenta QUALQUER aplicação para telemetria de uso E a CONECTA ao painel central
  ai-garage Pulse automaticamente. Ao rodar, a skill: (1) detecta a stack; (2) instala a
  captura best-effort de sessões, tempo por tela, ações e chamadas de LLM (tokens/custo);
  (3) gera a chave de export; (4) AUTO-CADASTRA a app no Pulse via POST /enroll (empresa,
  app_id, ambiente prod/dev/local); (5) liga o transporte certo — POLLING (Pulse puxa o
  contrato /telemetry/events em prod/dev) ou PUSH (a app envia eventos pro /telemetry/push
  quando roda local, atrás de NAT). Resultado: depois de rodar, a app já aparece no Pulse e
  começa a ser monitorada sem cadastro manual. Use quando o usuário pedir "telemetria",
  "monitorar esta app no Pulse", "conectar ao painel Pulse", "instrumentar telemetria",
  "aplica o telemetria aqui", "captura uso e custo de LLM e manda pro painel central".
---

# telemetria — instrumenta a app E conecta no painel Pulse (auto-enroll)

Objetivo: rodar UMA vez nesta aplicação e ela passa a **capturar tudo o que o Pulse precisa**
e a **aparecer no painel sozinha**. Dois transportes, escolhidos pelo ambiente:

- **prod / dev** (tem URL pública): a app EXPÕE o contrato `/telemetry/*`; o Pulse PUXA por cursor.
- **local** (máquina do dev, atrás de NAT): a app EMPURRA eventos para `POST {PULSE}/telemetry/push`.

> Companheira da skill `telemetry` (genérica). Esta é **Pulse-aware**: além de instrumentar,
> faz o **auto-enrollment** e o **push** para conectar diretamente ao painel.

## Checklist rápido — onboarding de app nova → Pulse
A skill resolve o LADO DO CÓDIGO (captura + contrato/push + auto-enroll). Pra a app **aparecer e
ficar verde**, garanta também o LADO OPERACIONAL:
1. **Chaves centrais** em `~/.config/llm-keys/keys.env`: `PULSE_BASE_URL` + `PULSE_ENROLL_TOKEN`
   (+ por app: `TELEMETRY_APP_ID`, `TELEMETRY_EMPRESA`). A skill gera `TELEMETRY_EXPORT_KEY` se faltar.
2. **Roteamento de `/telemetry/*` pro backend** (nginx/Cloudflare) — pegadinha nº 1: se cair no SPA,
   o Pulse recebe HTML → "fora do ar". Nunca usar host interno de Docker como `base_url`.
3. **Deploy** pra o enroll rodar; a `export_key` do container RODANDO deve bater com a cadastrada
   (a do `.env` do repo pode divergir → 401). Rode a skill **uma vez POR ambiente** (dev e prod = registros separados).
4. Ambiente é **inferido da URL pública** (não precisa setar à mão); o backend do Pulse auto-corrige
   `prod`-em-`-dev` e recusa (400) o que não der pra inferir.
5. **Conferir**: `GET {base_url}/telemetry/health` com `X-Telemetry-Key` → 200; e a app aparece em Soluções.

## Passo 0 — Parâmetros de conexão (do ecossistema)
Tudo vem do arquivo central de chaves (`~/.config/llm-keys/keys.env`, fora do repo — skill
`llm-keys`). A skill garante/escreve lá:

| Chave | O que é |
|---|---|
| `PULSE_BASE_URL` | URL do painel. Dev local: `http://localhost:8091`. Prod: `https://pulse-dev.ai-garage.com.br` |
| `PULSE_ENROLL_TOKEN` | segredo compartilhado p/ auto-cadastro (`AIGARAGE_PULSE_ENROLL_TOKEN` do Pulse) |
| `TELEMETRY_APP_ID` | id curto da app (ex.: `auditai`, `crmai`) |
| `TELEMETRY_EXPORT_KEY` | chave do contrato/push DESTA app (a skill gera se faltar: `secrets.token_urlsafe(32)`) |
| `TELEMETRY_AMBIENTE` | `prod` \| `dev` \| `local` (default: `local` em dev de máquina; `dev`/`prod` no deploy) |
| `TELEMETRY_BASE_URL` | **(prod/dev)** URL PÚBLICA por onde o Pulse PUXA o contrato — onde `/telemetry/*` está roteado. dev: `https://app-dev.ai-garage.com.br/api/v1` · prod: `https://app.ai-garage.com.br/api/v1`. **NUNCA** host interno de Docker (`http://app-backend:8000`): o Pulse roda noutra rede e não resolve. |
| `TELEMETRY_EMPRESA` | nome da empresa/cliente dono (ex.: `CVC`, `Direto ao Ponto`) |

## Passo 1 — Detectar a stack e o ambiente
- Backend: FastAPI/SQLAlchemy? Express/Prisma? Django? Laravel? Identifique onde criar a tabela,
  a função de registro e as rotas. **O código de referência abaixo é FastAPI+SQLAlchemy** (padrão
  do ecossistema AuditAI); adapte para outras stacks mantendo o MESMO contrato.
- Ambiente: **inferido da URL pública** pela convenção do ecossistema (não chute): host `*-dev.*`
  → `dev`; outro domínio público → `prod`; `localhost`/loopback → `local` (push). `TELEMETRY_AMBIENTE`
  só como override explícito. O backend do Pulse aplica a MESMA regra e **auto-corrige** quem se
  declarar `prod` rodando em `-dev` (fail-closed se não der pra inferir).
- **`base_url` (polling) = a URL PÚBLICA alcançável pelo Pulse**, com o path onde o contrato vive
  (ex.: `https://app-dev.ai-garage.com.br/api/v1`). **Cada ambiente é um registro próprio** no Pulse
  (chave única empresa+app_id+ambiente) — rode a skill em CADA deploy (dev e prod) p/ monitorar os dois.
  ⚠️ Nunca registre host interno de Docker (`http://app-backend:8000`): o Pulse não o resolve → "fora do ar".
  Garanta que o túnel/nginx da app roteia `/…/telemetry/*` pro backend (senão volta o SPA → 503/HTML).

## Passo 2 — Log de eventos (append-only) + registro best-effort
Tabela `telemetry_events` (somente-append). `seq` BIGSERIAL é o **cursor** estável; `event_id`
UUID dá idempotência. **Sem conteúdo sensível** (sem prompt/resposta; só metadados).

Esquema do evento (idêntico ao que o Pulse consome):
`seq, event_id, app_id, ts(UTC), tipo, user_id, user_email, role, session_id, feature,
duration_ms, provider, model, funcao, agente, tokens_in, tokens_out, cache_read, cost_usd, latency_ms, meta`

Tipos: `login`, `feature_time`, `session_heartbeat`, `session_end`, `action`, `llm_call`.

> **Campo `agente` (Vitrine de Agentes):** quando a solução tem agentes/personas nomeados
> (ex.: CRM → "Michelle", "John"; jurídico → "defensor", "vigia"), preencha `agente` com o
> NOME LIMPO do agente em CADA evento de trabalho (`llm_call`/`action`). É o que faz o agente
> aparecer na Vitrine como "funcionário", com a solução como contexto. NÃO use nome de modelo
> (sonnet/haiku) nem função genérica (rag_answer) em `agente` — isso é `model`/`funcao`.
> Fallback aceito pelo Pulse: `funcao` no formato `solução:agente` (ex.: `crm:michelle`).

```python
# app/telemetry/service.py  — best-effort: NUNCA levanta, nunca derruba a app.
import os, uuid, logging
from datetime import datetime, timezone
log = logging.getLogger("telemetria")

def app_id() -> str: return os.getenv("TELEMETRY_APP_ID", "app")

def registrar(tipo, *, user_id=None, user_email=None, role=None, session_id=None,
              feature=None, duration_ms=None, provider=None, model=None, funcao=None,
              tokens_in=None, tokens_out=None, cache_read=None, cost_usd=None,
              latency_ms=None, meta=None):
    try:
        from app.db import Session            # adapte ao seu acesso a banco
        from app.telemetry.models import TelemetryEvent
        with Session() as s:
            s.add(TelemetryEvent(
                event_id=str(uuid.uuid4()), app_id=app_id(),
                ts=datetime.now(timezone.utc), tipo=tipo, user_id=user_id,
                user_email=user_email, role=role, session_id=session_id, feature=feature,
                duration_ms=duration_ms, provider=provider, model=model, funcao=funcao,
                tokens_in=tokens_in, tokens_out=tokens_out, cache_read=cache_read,
                cost_usd=cost_usd, latency_ms=latency_ms, meta=meta))
            s.commit()
    except Exception as e:                     # telemetria nunca quebra a app
        log.debug("telemetria ignorada (%s): %s", tipo, e)
```

> **Custo de LLM:** prefira mandar só os TOKENS e deixar o Pulse recalcular o `cost_usd` pela
> tabela de preços central (preço muda num lugar só). Opcional: estime local também.

## Passo 3 — Capturar os 4 sinais
1. **Login/sessão:** no login → `registrar("login", user_id=..., session_id=...)`. No logout/fim →
   `session_end` com `duration_ms`.
2. **Tempo por tela (frontend):** ao trocar de rota, manda `feature_time {feature, duration_ms,
   session_id}` para `POST /telemetry/ingest` (carimba o usuário logado). React:
   ```tsx
   // no Layout: envia o tempo da tela anterior ao mudar de rota (best-effort)
   useEffect(() => {
     const prev = ref.current; const dur = Date.now() - prev.t;
     if (prev.feature && dur > 1000)
       fetch("/api/telemetry/ingest", {method:"POST", headers:{"Content-Type":"application/json",
         Authorization:`Bearer ${token}`}, body: JSON.stringify({events:[
         {tipo:"feature_time", feature: prev.feature.replace(/^\//,"")||"inicio", duration_ms:dur}]})
       }).catch(()=>{});
     ref.current = { feature: location.pathname, t: Date.now() };
   }, [location.pathname]);
   ```
3. **Ações relevantes:** nos handlers importantes → `registrar("action", feature=..., meta={...})`.
4. **Chamadas de LLM:** envolva o provider (langchain/openai/anthropic) e emita `llm_call` com
   `provider, model, funcao, tokens_in, tokens_out, cache_read, latency_ms, user_id`. Pegue tokens
   do `usage`/`usage_metadata` da resposta.

## Passo 4 — Expor o contrato (modo POLLING: prod/dev)
Auth M2M por header `X-Telemetry-Key` (== `TELEMETRY_EXPORT_KEY`), comparada em tempo constante
(`hmac.compare_digest`), **fail-closed**. Somente leitura.

- `POST /telemetry/ingest` — front manda feature_time/sessão/ações (auth do usuário logado).
- `GET  /telemetry/events?since_seq=N&limit=L` → `{app_id, events[], next_seq, has_more}`.
  Devolve eventos com `seq > since_seq`, ordenados, paginando até `has_more=false`.
- `GET  /telemetry/health` → `{app_id, eventos_total, ultimo_seq}`.
- `GET  /telemetry/summary?desde=ISO` → agregados (custo por modelo/usuário, minutos por tela).

(Use o `api/telemetry.py` do AuditAI como referência exata — mesmo envelope, mesmo cursor.)

## Passo 5 — Auto-enrollment (a app se cadastra no Pulse)
Rode no **boot** (best-effort, idempotente) OU como script de deploy. Faz a app aparecer no painel:

```python
# app/telemetry/enroll.py
import os, httpx, logging
log = logging.getLogger("telemetria.enroll")

def _infere_ambiente(*urls):
    """Deriva prod|dev|local pela convenção do ecossistema (mesma regra do Pulse):
    loopback/sem URL pública → local; host ``*-dev.*`` → dev; outro domínio → prod.
    Host interno de Docker (sem ponto, ex.: ``api``) é ignorado (não dá sinal)."""
    import re
    from urllib.parse import urlparse
    for u in urls:
        if not u: continue
        h = (urlparse(u if "://" in u else f"//{u}").hostname or "").lower()
        if not h: continue
        if h in ("localhost", "127.0.0.1", "0.0.0.0", "::1"): return "local"
        if "." not in h: continue
        return "dev" if re.search(r"(^|[.-])dev([.-]|$)", h) else "prod"
    return "local"

def enroll_no_pulse(base_url_publica: str | None):
    """Cadastra/atualiza esta app no Pulse. base_url_publica = None em ambiente local (push)."""
    pulse = os.getenv("PULSE_BASE_URL"); token = os.getenv("PULSE_ENROLL_TOKEN")
    if not pulse or not token: return
    # base_url (polling) = URL PÚBLICA que o Pulse alcança. Preferir TELEMETRY_BASE_URL
    # explícito; cair no argumento só como fallback. NUNCA host interno de Docker.
    base_url = os.getenv("TELEMETRY_BASE_URL") or (base_url_publica or "")
    pub = os.getenv("TELEMETRY_PUBLIC_URL", "") or base_url
    # Ambiente: env explícita vence; senão INFERE da URL pública (não chuta 'local'/'prod').
    # Isso evita o clássico bug de etiquetar um deploy -dev como prod.
    amb = os.getenv("TELEMETRY_AMBIENTE") or _infere_ambiente(pub, base_url)
    body = {
        "empresa": os.getenv("TELEMETRY_EMPRESA", "Direto ao Ponto"),
        "app_id": os.getenv("TELEMETRY_APP_ID", "app"),
        "nome": os.getenv("TELEMETRY_APP_NOME", os.getenv("TELEMETRY_APP_ID", "app")),
        "ambiente": amb,
        "base_url": base_url if amb != "local" else "",
        # url_publica: endereço PÚBLICO/humano só p/ EXIBIÇÃO no painel (distingue prod/dev/local
        # de relance). Default = o próprio base_url público.
        "url_publica": pub,
        "export_key": os.getenv("TELEMETRY_EXPORT_KEY", ""),
        "responsavel_nome": os.getenv("TELEMETRY_RESPONSAVEL"),
        "responsavel_email": os.getenv("TELEMETRY_RESPONSAVEL_EMAIL"),
    }
    try:
        r = httpx.post(f"{pulse.rstrip('/')}/enroll", json=body,
                       headers={"X-Enroll-Token": token}, timeout=10)
        log.info("enroll Pulse: %s %s", r.status_code, r.text[:200])
    except Exception as e:
        log.warning("enroll Pulse falhou (segue mesmo assim): %s", e)
```
Chame `enroll_no_pulse(PUBLIC_URL)` no startup (FastAPI: no `lifespan`).

## Passo 6 — PUSH (modo local)
Local não pode ser puxado → a app empurra. Um loop/worker manda os eventos novos por cursor
local para o Pulse, autenticado pela MESMA `TELEMETRY_EXPORT_KEY` (o Pulse casa pela chave do
cadastro `ambiente=local`):

```python
# envia lotes a cada ~30s; guarda o último seq enviado (em arquivo/tabela local)
import os, httpx
def push_novos(eventos: list[dict]):
    pulse = os.getenv("PULSE_BASE_URL"); key = os.getenv("TELEMETRY_EXPORT_KEY")
    if not (pulse and key and eventos): return 0
    r = httpx.post(f"{pulse.rstrip('/')}/telemetry/push", json={"events": eventos[:5000]},
                   headers={"X-Telemetry-Key": key}, timeout=20)
    r.raise_for_status(); return r.json().get("novos", 0)
```
Cada evento no push segue o MESMO esquema (inclua `event_id` para idempotência; `seq` é opcional).

## Passo 7 — Env e segredos
Escreva no arquivo central de chaves (nunca no repo): `TELEMETRY_APP_ID`, `TELEMETRY_EXPORT_KEY`
(gere se faltar), `TELEMETRY_AMBIENTE`, `TELEMETRY_EMPRESA`, `PULSE_BASE_URL`, `PULSE_ENROLL_TOKEN`.
Garanta `.env`/segredos no `.gitignore`.

## Regras (não-negociáveis)
- Telemetria **nunca derruba a app** (tudo try/except, best-effort, assíncrono/lote).
- **Sem conteúdo sensível**: só metadados (tokens, custo, modelo, função, usuário). Nunca prompt/resposta.
- Append-only + `seq` monotônico (export incremental confiável). Export read-only, chave forte fail-closed.
- `prod`/`dev` = polling (expõe contrato). `local` = push (a app envia). O ambiente define o transporte.
- O e-mail do usuário é o que permite o Pulse atribuir o uso à empresa certa (mapa domínio→empresa).

## Verificação ao terminar (prove que conectou)
1. Auto-enroll: `curl -s -XPOST $PULSE_BASE_URL/enroll -H "X-Enroll-Token: $PULSE_ENROLL_TOKEN" -d '{...}'`
   → `{"ok":true,"criado":...,"modo":"polling|push"}`.
2. prod/dev: `curl -s -H "X-Telemetry-Key: $TELEMETRY_EXPORT_KEY" $BASE/telemetry/health` →
   `{app_id, eventos_total, ultimo_seq}`. O Pulse já deve listar a app em **Soluções**.
3. local: gere um evento e confirme `POST $PULSE_BASE_URL/telemetry/push` → `{"ok":true,"novos":N}`.
4. Abra o Pulse → a app aparece em **Soluções/Ao Vivo** e os usuários no **Auditoria de Uso**.

## Resumo ao terminar
- Onde ficam os eventos, qual o `app_id`/`ambiente`, qual transporte (polling/push), e que o
  auto-enroll cadastrou a app no Pulse. Confirme best-effort + sem PII de conteúdo.
