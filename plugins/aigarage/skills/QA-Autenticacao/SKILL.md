---
name: QA-Autenticacao
description: >-
  Auditoria de QA de Autenticação & Autorização (AuthN/AuthZ) de qualquer projeto.
  Verifica os 5 pilares: (1) rotas sensíveis exigem token válido e NÃO expirado;
  (2) há verificação de papel (admin/editor/viewer/moderador) antes de operações de
  escrita/exclusão; (3) cada leitura/edição/exclusão valida ownership do recurso
  (anti-IDOR e isolamento de tenant/projeto); (4) tokens são invalidados no logout e
  após inatividade (denylist/jti/rotação de refresh/timeout); (5) endpoints admin
  estão isolados por middleware/dependência específica. Detecta a stack automaticamente,
  mapeia TODOS os endpoints, classifica cada um (auth? papel? ownership? severidade) e
  identifica rotas desprotegidas ou sem checagem de permissão. Aplica o princípio do
  menor privilégio. Gera relatório ANALISE_AUTH_AUTORIZACAO.md + plano de refatoração
  com tarefas e subtarefas (EPICs). NUNCA corrige sozinho: audita, reporta e só aplica
  após confirmação; depois verifica AO VIVO. Use quando o usuário pedir "analise a
  autenticação/autorização", "QA de auth", "checar permissões", "RBAC", "tem endpoint
  desprotegido?", "IDOR", "menor privilégio", "tokens invalidam no logout?" ou
  "aplica o QA-Autenticacao aqui".
---

# QA-Autenticação — auditoria de AuthN/AuthZ por projeto

Objetivo: produzir uma auditoria **acionável e honesta** do sistema de autenticação e
autorização, endpoint a endpoint, contra os **5 pilares** abaixo, e — após confirmação —
**aplicar e verificar** as correções aplicando o **princípio do menor privilégio**.
Resultado: `ANALISE_AUTH_AUTORIZACAO.md` na raiz do projeto + plano de refatoração
(EPICs com tarefas/subtarefas).

> Complementa o `security-audit` (OWASP/LGPD amplo). Esta skill é o **mergulho profundo**
> só em AuthN/AuthZ, com cobertura endpoint-a-endpoint e plano de refatoração.

## Princípios (não-negociáveis)

1. **Mapeie a stack ANTES.** O que conta como "protegido" depende do framework: FastAPI
   `Depends`, Express middleware, Django `@permission_classes`/`LoginRequiredMixin`,
   Spring `@PreAuthorize`, Laravel `middleware('auth')`/Policies, NestJS `Guards`. Identifique:
   mecanismo de token (JWT/sessão/cookie), onde mora a dependência/guard de auth, como papéis
   são checados, e se há RLS/tenant-scoping no banco.
2. **Cobertura total.** Liste **TODOS** os endpoints (grep por decorators de rota / tabela de
   rotas). Nenhum pode ficar sem veredito. Endpoint sem nenhuma dep de auth (e que não seja
   health/login/refresh/reset público) = **DESPROTEGIDO**.
3. **Evidência ou silêncio.** Todo achado aponta `arquivo:linha` e o trecho que o prova.
   Sem evidência → no máximo "A REVISAR". **Reverifique no service-layer** antes de afirmar:
   uma query "sem `tenant_id`" pode estar protegida por RLS, ou o filtro pode estar no service.
4. **Distinga os eixos.** AuthN (tem token válido?) ≠ AuthZ-papel (tem o papel certo?) ≠
   AuthZ-ownership (o recurso é dele?). Um endpoint pode passar num e falhar noutro.
5. **Cuidado com falso positivo.** Antes de reportar "sem ownership", confira: o ORM aplica
   RLS? o service filtra por tenant/owner? há um guard global no router? Se sim, não é achado
   (ou é só defesa-em-profundidade = BAIXO).
6. **NUNCA corrija sozinho.** Audita → relatório → espera "ok" → aplica só o aprovado, um a um.
7. **Verifique AO VIVO.** Após corrigir, prove com requisição real: `viewer` recebe 403,
   token expirado recebe 401, token de outro tenant/projeto recebe 404, logout invalida o token.
   Rode a suíte de testes.

## Os 5 pilares (o checklist central)

### Pilar 1 — Rotas sensíveis exigem auth válida (token não expirado)
- Toda rota não-pública tem dependência/guard de auth? Liste as **sem** (DESPROTEGIDAS).
- O token valida **assinatura + expiração (`exp`) + audience/escopo**? `exp` é obrigatório?
- Há rota pública que **não deveria** ser (vaza dado sensível sem auth)?
- `/health`/`/login`/`/refresh`/`/password-reset` públicos são legítimos — mas health não
  pode vazar versão/env/backends/erros internos.

### Pilar 2 — Verificação de papel antes de operações de escrita (least privilege)
- Regra-guia: **leitura** → autenticado; **escrita** → `editor`+; **delete/aprovação/
  geração de credencial/operação cara (LLM)** → `admin`/`owner`.
- Procure mutações (`POST`/`PUT`/`PATCH`/`DELETE`) que rodam só com "usuário autenticado"
  sem checar papel → gap de **menor privilégio**.
- **Privilege escalation:** endpoint que seta papel/role do usuário sem checar que o ator
  tem papel ≥ ao concedido (ex.: `users.update` promovendo alguém a `owner`).
- Operações que geram **custo** (LLM, e-mail, fetch externo) sem papel nem rate-limit.

### Pilar 3 — Ownership por recurso (anti-IDOR + isolamento tenant/projeto)
- Endpoint recebe `{id}` no path e busca o recurso **sem filtrar por tenant/owner/projeto**?
  → **IDOR**. Distinga:
  - **cross-tenant** (grave; mitigado por RLS se houver — confirme que RLS existe e cobre a tabela).
  - **cross-project intra-tenant** (RLS não pega; filtro por `tenant_id` ignorando `project_id`
    do path = vazamento entre projetos do mesmo cliente).
- **Tabelas globais** (sem coluna tenant) escritas por admin de tenant comum = broken access
  control cross-tenant a nível de dado compartilhado.
- **Portais/atores externos:** derivar `tenant_id`/`project_id` da **linha do ator** (autoritativa),
  nunca de ID vindo do cliente; e comparar o escopo do token com a linha.

### Pilar 4 — Invalidação de token (logout + inatividade)
Este é o pilar mais frequentemente **NÃO satisfeito** em apps JWT-stateless. Verifique:
- **Logout** tem efeito no servidor? (Se só "client descarta token" → token roubado continua
  válido até expirar.)
- Há **denylist/blocklist** de tokens (via `jti` em Redis/DB) consultada a cada request?
- **Timeout de inatividade**: refresh rejeita se `now - last_active > idle_timeout`? Há
  duração máxima de sessão? `last_active` é atualizado?
- **Rotação de refresh** (one-time-use) com detecção de reuse → revoga a família?
- Desativar/deletar usuário ou trocar senha **invalida tokens vivos** (ex.: `tokens_valid_after`
  comparado ao `iat`)? Ou o token continua válido até expirar?

### Pilar 5 — Endpoints admin isolados por middleware/dep específica
- Rotas admin/plataforma usam dependência **própria** (`require_super_admin`/`PlatformAdmin`/
  guard de admin), não só "autenticado"?
- Export/telemetria/métricas M2M usam segredo forte comparado em **tempo constante**
  (`hmac.compare_digest`) e **fail-closed** (nega se a chave faltar)?
- Webhooks de **entrada** verificam assinatura (HMAC)? Webhooks de saída protegem o signing secret?

## Fluxo

- **Passo 0 — Stack & modelo de auth.** Detecte framework/ORM/token. Leia os arquivos core de
  auth (deps/guards/middleware, criação/validação de token, hashing). Documente o modelo numa
  tabela (primitiva → onde → o que garante). **Apresente o modelo ANTES de auditar.**
- **Passo 1 — Inventário de endpoints.** Liste todos os routers/controllers e enumere cada rota.
  Para fan-out em projetos grandes (20+ routers), **dispare subagentes em paralelo**, cada um
  com um grupo de arquivos e o mesmo rubrico (template abaixo).
- **Passo 2 — Auditar (só leitura).** Para cada endpoint preencha: auth? papel adequado à
  criticidade? ownership/tenant/projeto na query? severidade? recomendação. **Confirme no
  service-layer** os pontos marcados "verificar" (RLS, filtros, validações).
- **Passo 3 — Relatório.** `ANALISE_AUTH_AUTORIZACAO.md` com: modelo de auth, veredito dos 5
  pilares (✅/⚠️/❌), achados por severidade (tabela com `arquivo:linha`), e o **plano de
  refatoração** (EPICs → tarefas → subtarefas, cada uma com teste de regressão).
- **Passo 4 — Correção (só após confirmação).** Aplique menor privilégio um item por vez,
  verifique ao vivo, rode os testes.

## Rubrico por endpoint (template para subagentes)

Para CADA `@route`/handler reporte uma linha:
`arquivo:linha | método + path | dep de auth (qual) | papel adequado à criticidade? | ownership/tenant/projeto na query? (sim/não/N/A — destaque IDOR) | SEVERIDADE | recomendação curta`

Agrupe por arquivo (tabela markdown) + lista priorizada dos GAPS (não-OK) por severidade.

## Severidade
- **Crítica** — rota sensível **sem auth**; auth bypass; IDOR cross-tenant em dado sensível
  sem RLS; token forjável (segredo fraco/`alg=none`).
- **Alta** — mutação destrutiva/aprovação/credencial **sem papel**; IDOR cross-project;
  privilege escalation; logout/inatividade ausentes (ponto 4); admin acessível a não-admin.
- **Média** — escrita comum sem papel; listagem de objetos de gestão a viewer; dado global
  editável por admin de tenant; operação cara sem rate-limit; IDOR mitigado só por RLS.
- **Baixa** — defesa-em-profundidade ausente (filtro redundante), inconsistência de papel,
  vazamento de PII leve, info leak em health, docstring enganosa.

## Plano de refatoração (estrutura recomendada de EPICs)

Organize as correções em EPICs ordenados por **risco × esforço**:
- **EPIC A — Least-privilege:** `require_role`/`require_permission` em todas as mutações
  (escrita→editor; delete/aprovação/credencial→admin). ⭐ maior risco, menor esforço.
- **EPIC B — Invalidação de token:** `jti` + denylist (Redis) + logout efetivo + timeout de
  inatividade + rotação de refresh + revogação em massa (pilar 4).
- **EPIC C — IDOR/escopo:** helper `get_owned_or_404(model,id,tenant,project)`; cruzar
  `project_id` nos GET/DELETE de item único.
- **EPIC D — Dados globais/admin:** permissões de catálogos/global restritas à plataforma;
  gestão (api-keys/webhooks) a owner/admin.
- **EPIC E — Privilege escalation:** ator não concede papel > o próprio; reset de senha de
  terceiro restrito.
- **EPIC F — Hardening:** health enxuto, rate-limit em LLM, PII em lookups, bugs de runtime.
- **EPIC G — Testes de regressão:** suíte parametrizada `viewer→403 / editor→2xx /
  cross-tenant→404 / cross-project→404 / sem token→401 / expirado→401`; rodar em **Postgres**
  (não só SQLite) para exercitar RLS; testes de logout/inatividade.

Cada subtarefa **deve** vir com seu teste de regressão.

## Verificação ao vivo (depois de corrigir)
- `curl` sem token → 401; token expirado → 401; logout depois reusar token → 401.
- `viewer` numa mutação → 403; `editor`/`admin` → 2xx.
- token do tenant A pedindo recurso do tenant B → 404; projeto A pedindo recurso do projeto B → 404.
- Rode a suíte de testes de autorização (idealmente contra Postgres, para RLS).

## Armadilhas comuns (evite falso positivo / falso negativo)
- "Query sem `tenant_id`" pode estar coberta por **RLS** — confirme que RLS existe, está
  ativo por request, e cobre aquela tabela (e que não é SQLite/teste).
- Filtro de ownership pode estar no **service**, não no handler — leia o service antes de acusar.
- `aud`/escopo do JWT: um token de portal externo não deve abrir endpoint de workspace e
  vice-versa — verifique a audience.
- Logout que retorna 200/204 **não** significa invalidação — leia o que ele faz de fato.
- Não confie em validação só no cliente (front esconde botão de admin ≠ backend protege a rota).
