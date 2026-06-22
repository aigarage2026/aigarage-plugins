---
name: auth-kit
description: >-
  Monta toda a camada de autenticação, usuários, perfil, papéis/permissões (RBAC)
  e segurança de um projeto web: login (JWT), cadastro/CRUD de usuário, hash de
  senha seguro, papéis dinâmicos com permissões granulares por funcionalidade,
  guardas de rota/endpoint, reset de senha por e-mail (link com token) e "esqueci
  minha senha", além do admin inicial (bootstrap). Use quando o usuário pedir
  "autenticação", "login", "cadastro/gestão de usuários", "perfil", "papéis e
  permissões", "RBAC", "controle de acesso", "reset de senha", "segurança de
  acesso" ou "aplica o auth-kit aqui".
---

# Auth Kit — autenticação, usuários, RBAC e segurança (reutilizável)

Monta, ponta a ponta, a mesma arquitetura de acesso comprovada no projeto AuditAI:
login + JWT, CRUD de usuário, perfil, **papéis dinâmicos com permissões granulares**,
guardas de rota/endpoint, **reset de senha por e-mail** e admin inicial. Adapta-se ao
stack do projeto; se for FastAPI + SQLAlchemy + Alembic + React, use os contratos abaixo
literalmente (são a referência testada).

## ⛔ Regras de segurança (NÃO-negociáveis)
- **Nunca** armazenar senha em texto puro. Hash com algoritmo forte (scrypt/argon2/bcrypt),
  salt aleatório por senha, verificação em **tempo constante**.
- **Login genérico**: nunca revelar se foi e-mail ou senha que errou (evita enumeração de usuários).
- **Segredo do token (JWT) vem de variável de ambiente**; em produção, recusar subir com
  segredo fraco/placeholder. Tokens com expiração curta (ex.: 8h).
- **Reset por link com token de uso único** que expira (ex.: 30 min); guardar só o **hash**
  do token (nunca o valor cru). Resposta do "esqueci senha" é sempre genérica.
- **Proteções de integridade**: não permitir o usuário se autodesativar nem rebaixar o
  próprio papel; nunca deixar o sistema sem admin; papel em uso não pode ser excluído.
- **admin é soberano**: o papel `admin` sempre tem todas as permissões (não dá para se trancar para fora).
- Nunca commitar segredos nem dumps; HTTPS em produção.

## Passo 0 — Detectar o stack e o que já existe
1. Backend: FastAPI/Django/Flask/Express/NestJS? ORM (SQLAlchemy/Prisma/Django ORM)?
   Ferramenta de migração (Alembic/Prisma/Knex)?
2. Frontend: React/Vue/Next/Svelte? Há roteador? Há provider de estado global?
3. Já existe auth? **Estenda** (não recrie). Mapeie o que falta deste kit.
4. Há provedor de e-mail? (Resend/SMTP/SES). Se não, crie uma abstração com fallback
   "dry-run" (loga no console) para funcionar sem credencial.

## Modelo de dados (3 tabelas; crie migração no padrão do projeto)
- **users**: `id` (uuid), `email` (único, índice), `name`, `role` (string → nome do papel),
  `password_hash`, `ativo` (bool), `preferred_language` (opcional, p/ i18n), `last_login_at`,
  `created_at`, `updated_at`.
- **roles**: `name` (PK), `description`, `permissions` (JSON: lista de chaves de permissão),
  `is_system` (bool, não-excluível), `locked` (bool, só o `admin`), timestamps.
- **password_reset_tokens**: `id`, `user_id`, `token_hash` (sha256, único), `created_at`,
  `expires_at`, `used_at` (nulo até consumir).

## Senha (referência: scrypt da stdlib, zero deps)
- Formato armazenado: `scrypt$<n>$<r>$<p>$<salt_b64>$<hash_b64>` (N=2^15, r=8, p=1, salt 16B, dklen 32).
- `hash_password(senha)` gera com salt aleatório; `verify_password(senha, stored)` compara
  com `hmac.compare_digest`. (Se preferir argon2/bcrypt e houver lib, ok — mantenha a interface.)

## Token (JWT HS256)
- `issue_token(user_id, email, role, name) -> (token, expires_at)`; payload
  `{iss, sub, email, name, role, iat, exp}`. Segredo de `AUTH_SECRET` (env). TTL configurável.
- `decode_token(token)` valida assinatura/expiração/issuer.

## Permissões / RBAC dinâmico
- **Catálogo de permissões** (fonte única): lista de `{chave, grupo, rotulo, descricao}`,
  uma por funcionalidade/subfuncionalidade (ex.: `dashboard`, `relatorios.read`,
  `relatorios.write`, `admin.users`, `admin.roles`, `config`). Granular o suficiente para
  criar papéis sob medida (ex.: "vê dashboard, não vê configurações").
- **Defaults-semente** (fallback se o banco cair) + os papéis vivem na tabela `roles`.
- `has_perm(role, perm)`: se `role == "admin"` → True; senão lê as permissões do papel no
  **banco com cache curto** (TTL ~20s) e cai no default em erro. NUNCA lança exceção.
- **Gates**: dependência/middleware `require_perm("chave")` (401 sem token, 403 sem permissão).
- O objeto do usuário devolvido ao front inclui `permissions: string[]` (as efetivas do papel),
  para o front esconder/mostrar UI. **A barreira real é o servidor** (401/403); o front só espelha.

## Endpoints (contratos)
Público:
- `POST /auth/login` {email, senha} → {access_token, expires_at, user}
- `GET /auth/me` → usuário atual (+ permissions)
- `POST /auth/change-password` {senha_atual, senha_nova}
- `PATCH /auth/me/language` {preferred_language}  (auto-serviço, opcional p/ i18n)
- `POST /auth/forgot-password` {email} → 202 genérico (não vaza existência)
- `POST /auth/reset-password` {token, senha_nova} → 204 (valida token único/expira)
Admin de usuários (`admin.users`):
- `GET/POST/PATCH/DELETE /auth/users[/{id}]` (DELETE = soft delete `ativo=false`)
- `POST /auth/users/{id}/send-reset` → dispara e-mail de reset para o usuário
Admin de papéis (`admin.roles`):
- `GET /auth/roles` (papéis + catálogo de permissões; leitura p/ qualquer autenticado)
- `POST/PATCH/DELETE /auth/roles[/{name}]` (guardas: admin imutável, sistema/“em uso” não exclui)

## Reset de senha por e-mail
- `criar_token(user)`: invalida tokens antigos, gera `secrets.token_urlsafe(32)`, salva só o
  sha256, devolve o cru; monta link `{PUBLIC_URL}/app/reset-password?token=<cru>` e envia por e-mail.
- `consumir_token(raw, senha_nova)`: valida (existe, não usado, não expirado, usuário ativo),
  troca a senha, marca `used_at`.
- Template de e-mail simples e claro (admin-iniciado vs auto-serviço). **Sanitize tags do
  provedor** (ex.: Resend rejeita ponto em tag).

## Bootstrap (idempotente, no startup)
- Semear os papéis padrão (admin/…); criar o **admin inicial** a partir de env
  (`BOOTSTRAP_ADMIN_EMAIL/PASSWORD/NAME`), com warning bem visível se a senha for default.

## Frontend (React; adapte se Vue/etc.)
- **AuthProvider/contexto**: `user`, `login`, `logout`, `can(perm)` (= `user.permissions.includes`),
  `refresh`. Token em `localStorage`; em 401 limpa e manda pro login.
- **Guardas de rota**: `RequireAuth perm="..."` que checa `can(perm)`.
- **Telas**: Login (com "Esqueci minha senha"), página pública **/reset-password** (token na URL),
  **Admin** com CRUD de usuário (todos os campos + reset por e-mail) e **CRUD de papéis com
  toggles de permissão agrupados** pelo catálogo. Menu/itens filtrados por `can(perm)`.
- Aplicar o idioma do usuário ao logar, se houver i18n (ver skill `multilang`).

## Migrações & qualidade
- Sempre via a ferramenta de migração do projeto (nunca `create_all` em prod). Nunca apague dados.
- Testes: hash/verify, has_perm (admin tudo / papel sem perm / fallback), token reset
  (ok/expirado/usado), e gates de API (401/403). Login genérico.
- Idempotente: se rodar de novo, complete só o que falta.

## Resumo a dar ao usuário ao terminar
- URLs/credenciais do admin inicial e como trocar a senha.
- Como criar papéis sob medida (ex.: "Dashboard sim, Config não").
- Como o reset por e-mail funciona (e que precisa do provedor configurado para entregar de verdade).
- Lembrar de definir `AUTH_SECRET` forte e trocar a senha do admin antes de produção.

> Referência testada deste kit: o projeto **AuditAI** (FastAPI+SQLAlchemy+Alembic+React),
> migrações de `users`, `roles` e `password_reset_tokens`, e a tela Admin com RBAC dinâmico.

---

## 🏢 Multi-tenant + Multi-empresa (extensão SaaS)

> Camada de isolamento por **tenant** (inquilino/organização-cliente da plataforma) e por
> **empresa** (cliente final dentro do tenant). Referência testada: projeto **Propostai**
> (FastAPI+SQLAlchemy+Alembic+React). Combine com a base de auth/RBAC acima.

### Modelo de dados (3 peças)
- **tenants**: `id`, `name`, `slug` (único), `plan_slug`, limites (`max_users`,
  `max_proposals_per_month`/`max_*`), branding (`logo_url`, `primary_color`),
  `is_active` (bool) + `suspended_at`/`suspension_reason`, timestamps.
- **companies** (empresa-cliente dentro do tenant): `id`, `tenant_id`, `name`, `cnpj`,
  `razao_social`, `is_default` (bool), campos do domínio, timestamps.
- **user_company_access**: `id`, `tenant_id`, `user_id` (FK), `company_id` (FK), `role`
  (admin/editor/viewer) — atribui um usuário a uma empresa. Unique(`tenant_id`,`user_id`,`company_id`).
- **users** ganham `tenant_id` (FK) e `is_platform_admin` (bool — super-admin cross-tenant).
- **TenantMixin**: todo modelo de domínio carrega `tenant_id` — *"toda query DEVE filtrar por tenant_id"*.

### Isolamento por TENANT (não-negociável)
- `tenant_id` viaja **dentro do JWT** (no payload, junto de `sub`/`role`). Toda query de
  domínio filtra `WHERE tenant_id = user.tenant_id`. Nunca confie em `tenant_id` vindo do body.
- **Login bloqueia tenant suspenso** (`is_active=False` → 403); o platform admin passa.

### Isolamento por EMPRESA (dentro do tenant)
Regra recomendada: **owner/admin (e platform admin) enxergam TODAS as empresas do tenant;
editor/viewer só as atribuídas** em `user_company_access`. Helpers (núcleo reutilizável):
- `accessible_company_ids(db, user) -> set[str] | None` — `None` = todas (admin); senão o conjunto atribuído.
- `assert_company_access(db, user, company_id)` — empresa existe no tenant **e** o usuário tem acesso (404/403).
- `assert_resource_access(db, user, recurso)` — bloqueia recurso de empresa fora do escopo (**404 p/ não vazar** — anti-IDOR).
- Aplicar em **toda** query escopada: listas filtram por `company_id IN ids` (se `ids` vazio → retorna vazio);
  endpoints `/{id}` chamam `assert_resource_access` após carregar.

### Endpoints (contratos)
Empresas (gestão exige owner/admin):
- `GET /api/v1/companies` → empresas que o usuário acessa (admin: todas; demais: as atribuídas)
- `POST/PATCH/DELETE /api/v1/companies[/{id}]` (DELETE bloqueia a `is_default` e empresa com dados vinculados)
- `GET/POST/DELETE /api/v1/companies/{id}/users[/{uid}]` → atribuir/revogar acesso (user_company_access)
Usuários do tenant (owner/admin):
- `GET/POST/PATCH /api/v1/users[/{id}]` — mínimo p/ atribuir gente às empresas (não se autodesativa nem rebaixa o próprio papel)
Plataforma (restrito a `is_platform_admin`, dependência `get_platform_admin`):
- `GET /api/v1/platform/tenants` → tenants + contagens (usuários/empresas)
- `POST /api/v1/platform/tenants` → **onboarding**: cria tenant + usuário `owner` (senha hash) + empresa padrão (`is_default`)
- `PATCH /api/v1/platform/tenants/{id}` → planos/limites e **suspender/reativar** (`is_active` + `suspended_at`)

### Frontend (React)
- **CompanyContext**: carrega `/api/v1/companies`, mantém a **empresa ativa** (persistida em
  localStorage; default = `is_default` ou a 1ª). Expõe `companies`, `activeCompanyId`, `setActiveCompany`.
- **Seletor de empresa** no header (aparece quando há +de 1 empresa). Telas de criação e
  listas usam a empresa ativa (`company_id`).
- **Guardas de rota**: `RequireAdmin` (owner/admin) p/ a tela de Empresas; `RequireAdmin platform`
  (`is_platform_admin`) p/ a tela de Plataforma. Itens de menu condicionais ao papel.
- Telas: **Empresas** (CRUD + atribuir usuários por empresa) e **Plataforma** (lista/cria/suspende tenants).

### Bootstrap / cuidados
- Designar ao menos **um `is_platform_admin`** (via env de bootstrap ou seed) — é quem cria os tenants.
- Onboarding self-service (signup público) é opcional; o `POST /platform/tenants` já cobre o onboarding assistido.
- Limites de plano (`max_users`/etc.) ficam no tenant — aplicar na criação de usuários/recursos quando quiser cobrar/limitar.

> Referência testada desta extensão: **Propostai** — `core/access.py`, `apis/v1/companies.py`,
> `apis/v1/users.py`, `apis/v1/platform.py`, `CompanyContext` + seletor no header.
