---
name: tenant
description: >-
  Sobe toda a camada multi-tenant de um SaaS web: TENANT (cliente da plataforma),
  EMPRESAS dentro do tenant, USUÁRIOS com papéis, isolamento por linha (tenant_id +
  company), onboarding (criar tenant → owner + empresa padrão), cadastro self-service
  com código de convite, platform admin (super-admin cross-tenant), e a gestão (CRUD
  de empresas/usuários, atribuição usuário↔empresa, suspender tenant). Use quando o
  usuário pedir "multi-tenant", "multi-empresa", "tenant", "cadastro de tenant/empresa/
  usuário", "onboarding", "platform admin", "isolamento por cliente", "SaaS B2B", ou
  "aplica o tenant aqui / cria igual ao Propostai". Para login/JWT/reset de senha/RBAC
  use junto o skill **auth-kit** (este skill foca na multi-tenancy e gestão).
---

# Tenant — multi-tenant + empresas + usuários (reutilizável)

Sobe, ponta a ponta, a mesma arquitetura multi-tenant comprovada no Propostai/Recrutamento:
um **Tenant** (o cliente da plataforma) contém várias **Empresas** (clientes finais) e
vários **Usuários**; tudo isolado por `tenant_id` em toda query, com uma segunda camada de
escopo por **empresa**. Inclui onboarding, cadastro self-service com convite, platform admin
e as telas de gestão. Adapta-se ao stack; se for **FastAPI + SQLAlchemy + Alembic + React**,
use os contratos abaixo literalmente (são a referência testada).

> **Relação com o auth-kit:** o `auth-kit` cuida de login (JWT), hash de senha, reset por
> e-mail, RBAC e bootstrap do admin. Este skill cuida da **multi-tenancy**: o que o JWT
> carrega, como isolar por tenant/empresa, onboarding, convites, platform admin e a gestão.
> Aplique os dois juntos num SaaS B2B.

## ⛔ Isolamento (NÃO-negociável)
- **Toda query filtra `tenant_id`.** Sem exceção. O `tenant_id` vem do JWT, **nunca** do body/query
  do cliente. Um usuário jamais lê/escreve linha de outro tenant.
- **Segunda camada por EMPRESA:** owner/admin (e platform admin) enxergam **todas** as empresas do
  tenant; editor/viewer só as **atribuídas** (`UserCompanyAccess`). Recurso filho (proposta, doc…)
  herda o escopo da empresa.
- **Anti-IDOR:** acesso a recurso fora do escopo retorna **404** (não 403) para não vazar existência.
- **Platform admin é cross-tenant** e perigoso: `is_platform_admin` só por promoção manual no banco;
  endpoints de plataforma exigem `get_platform_admin`.
- **Soft-delete** em empresa (`is_active=False`) para preservar histórico; a empresa padrão não se exclui.
- **Suspender tenant** bloqueia login de todos os seus usuários (checar `tenant.is_active` no login).

## Passo 0 — Detectar o stack e o que já existe
1. Backend: FastAPI/Django/Express? ORM + migração (Alembic/Prisma)? Já há `User`/auth? **Estenda.**
2. Já existe `tenant_id` nas tabelas? Se o app nasceu single-tenant, planeje a migração (adicionar
   `tenant_id` NOT NULL com `server_default` temporário + backfill — ver "Gotchas").
3. Frontend: React/Vue? Há provider de auth? Roteador? Onde fica o header de API?
4. Aplique o **auth-kit** antes/junto (login, senha, reset). Este skill assume que o login existe.

## Modelo de dados (5 peças)
Mixins padrão: `UUIDMixin` (id String(36)), `TimestampMixin` (created_at/updated_at),
`TenantMixin` (tenant_id String(36) FK→tenants.id ondelete CASCADE, **index**). Entidades de
tenant herdam os 3; entidades de plataforma (Tenant, InviteCode) **não** têm tenant_id.

1. **Tenant** (raiz; SEM tenant_id) — `name`, `slug` (unique, index), `plan_slug`, limites
   (`max_users`, `max_*`, `features` JSON), branding (`logo_url`, `primary_color`), status
   (`is_active`, `suspended_at`, `suspension_reason`), prefs (`default_language`, `timezone`).
2. **Company** (TenantMixin) — `name`, `cnpj?`, `razao_social?`, `is_default` (bool), `is_active`
   (bool, soft-delete), `logo_url?`, campos do domínio, contato, `notes`, `tags`. Recursos do
   domínio são filhos da Company (`company_id` FK).
3. **User** (TenantMixin) — além dos campos do auth-kit (email, full_name, password_hash, role,
   is_active, campos de reset/last_login), **dois extras de multi-tenancy**: `role` (owner/admin/
   editor/viewer) e `is_platform_admin` (bool, default False). Email **não** é único global — é
   único **por tenant** (o mesmo e-mail pode existir em tenants diferentes → login resolve qual).
4. **UserCompanyAccess** (TenantMixin) — N:N User↔Company com `role` por empresa
   (admin/editor/viewer). `UniqueConstraint(user_id, company_id)`. Owner/admin do tenant NÃO
   precisam de linha aqui (acesso implícito a tudo).
5. **InviteCode** (plataforma, SEM tenant_id) — gate do cadastro self-service: `code` (unique),
   `max_uses`/`times_used`, `expires_at?`, `is_active`, `assigned_plan`, `trial_days`. Propriedade
   `is_valid` (ativo + dentro de usos + não expirado).

```python
# models/user_company_access.py — o coração do escopo por empresa
class UserCompanyAccess(Base, UUIDMixin, TimestampMixin, TenantMixin):
    __tablename__ = "user_company_access"
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    company_id = Column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False, default="editor")
    __table_args__ = (UniqueConstraint("user_id", "company_id", name="uq_user_company_access"),)
```

## O que o JWT carrega + helpers de segurança
Access token traz: `sub` (user_id), `tenant_id`, `email`, `role`, `is_platform_admin`, `exp`.
O `tenant_id` do token é a **fonte da verdade** do escopo.

```python
# core/security.py
def create_access_token(user_id, tenant_id, email, role, is_platform_admin=False): ...
async def get_current_user(...) -> User           # decodifica o JWT, carrega o User do tenant
def get_current_tenant_id(request) -> str          # só o tenant_id, sem carregar o User
def require_role(allowed: list[str]):               # 403 se role não permitido; platform admin passa
    def dep(user=Depends(get_current_user)):
        if user.is_platform_admin: return user
        if (user.role or "").lower() not in allowed: raise HTTPException(403, "Sem permissão")
        return user
    return dep
def get_platform_admin(user=Depends(get_current_user)):
    if not user.is_platform_admin: raise HTTPException(403, "Apenas platform admin")
    return user
```

## Camada de acesso por empresa (`core/access.py`)
A peça que centraliza o escopo por empresa. Copie quase literal:

```python
ADMIN_ROLES = ("owner", "admin")
def is_tenant_admin(user) -> bool:
    return bool(getattr(user, "is_platform_admin", False)) or (user.role or "").lower() in ADMIN_ROLES

async def accessible_company_ids(db, user) -> set[str] | None:
    """IDs de empresa do usuário. None = TODAS (admin/owner/platform)."""
    if is_tenant_admin(user): return None
    rows = (await db.execute(select(UserCompanyAccess.company_id).where(
        UserCompanyAccess.tenant_id == user.tenant_id, UserCompanyAccess.user_id == user.id))).scalars().all()
    return set(rows)

async def assert_company_access(db, user, company_id) -> Company:
    comp = (await db.execute(select(Company).where(
        Company.id == company_id, Company.tenant_id == user.tenant_id, Company.is_active == True))).scalar_one_or_none()
    if not comp: raise HTTPException(404, "Empresa nao encontrada")
    ids = await accessible_company_ids(db, user)
    if ids is not None and company_id not in ids: raise HTTPException(403, "Sem acesso a esta empresa")
    return comp

async def assert_resource_access(db, user, resource) -> None:
    """Recurso filho de empresa fora do escopo → 404 (não vaza)."""
    ids = await accessible_company_ids(db, user)
    if ids is not None and getattr(resource, "company_id", None) not in ids:
        raise HTTPException(404, "Nao encontrado")
```

**Padrão de listagem** (toda lista de recurso do domínio):
```python
q = select(Recurso).where(Recurso.tenant_id == user.tenant_id)
ids = await accessible_company_ids(db, user)
if ids is not None:
    if not ids: return []          # não-admin sem empresa atribuída → vazio
    q = q.where(Recurso.company_id.in_(ids))
active = company_id or x_company_id  # empresa ativa (query param ou header X-Company-Id)
if active: q = q.where(Recurso.company_id == active)
```

## Endpoints (contratos)
### Auth (com o auth-kit) — login multi-tenant + cadastro com convite
- `POST /auth/register` — **gated por código de convite**. Valida `invite.is_valid`, incrementa
  `times_used`, cria **Tenant + User owner + Company padrão** (`is_default=True`) numa transação,
  devolve access+refresh. (Self-service = o próprio usuário vira owner do seu novo tenant.)
- `POST /auth/login` — e-mail pode existir em **vários tenants**. Busca todos os Users ativos com
  aquele e-mail cuja senha confere; se houver mais de um tenant (ou faltar escolha), responde
  `{requires_company_selection: true, companies: [{tenant_id, tenant_name, company_name, user_role}]}`.
  O front mostra a escolha e re-chama com `tenant_id`. Recusa login se `tenant.is_active == False`.
  Mensagem de erro **genérica** (não revela e-mail vs senha). Combine com brute-force (auth-kit).
- `POST /auth/refresh`, `forgot/reset/change-password` — ver auth-kit (o refresh re-emite com o
  mesmo `tenant_id`).

### Empresas — `/api/v1/companies` (escopo de tenant; gestão exige owner/admin)
- `GET ""` — empresas que o usuário acessa (admin/owner: todas ativas; demais: as atribuídas).
- `POST ""` / `PATCH /{id}` — criar/editar (owner/admin). `DELETE /{id}` — **soft-delete**
  (`is_active=False`); a empresa padrão não pode ser excluída.
- `GET /{id}/users` · `POST /{id}/users` `{user_id, role}` · `DELETE /{id}/users/{uid}` — atribuição
  usuário↔empresa (upsert do `UserCompanyAccess`).

### Usuários do tenant — `/api/v1/users` (owner/admin)
- `GET ""` (lista do tenant) · `POST ""` `{email, full_name, role, password}` (cria já com senha;
  dup por e-mail **no tenant** → 409) · `PATCH /{id}` (nome/role/is_active).
- `POST /{id}/reset-password` `{password}` — admin define nova senha e marca `must_change_password`.
- **Integridade:** não se autodesativar nem rebaixar o próprio papel.

### Plataforma — `/api/v1/platform` (apenas `is_platform_admin`)
- `GET /tenants` (com `users_count`/`companies_count`) · `POST /tenants` — **onboarding**: cria
  Tenant + User owner + Company padrão · `PATCH /tenants/{id}` (plano/limites/suspender — setar
  `suspended_at`).
- `GET/POST/DELETE /invite-codes` — gerir os códigos de convite (define plano, usos, validade).

## Onboarding (a transação que cria um tenant)
```python
tenant = Tenant(name=..., slug=_slugify(name), plan_slug=..., max_users=..., is_active=True); db.add(tenant); await db.flush()
db.add(User(tenant_id=tenant.id, email=admin_email, full_name=admin_name, role="owner",
            password_hash=hash_password(admin_password), is_active=True))
db.add(Company(tenant_id=tenant.id, name=company_name or name, is_default=True))
await db.flush()
```
Dois caminhos para isso: **self-service** (`/auth/register` com convite → o cadastrante vira owner)
e **platform admin** (`POST /platform/tenants` → cria para um cliente). Mesmo bloco nos dois.

## Frontend (React; adapte se Vue/etc.)
- **Header de escopo:** o interceptor injeta `Authorization: Bearer <token>` e
  `X-Company-Id: <empresa ativa>` (de `localStorage`). O backend usa o header como "empresa ativa".
```ts
api.interceptors.request.use(c => {
  const t = localStorage.getItem('app_token'); if (t) c.headers.Authorization = `Bearer ${t}`
  const cid = localStorage.getItem('app.activeCompany'); if (cid) c.headers['X-Company-Id'] = cid
  return c
})
```
- **CompanyContext** — carrega `GET /companies`, guarda `activeCompanyId` em localStorage, expõe
  `setActiveCompany`. Um seletor de empresa no header troca o escopo ativo. Não-admin só vê as suas.
- **Login com seleção** — se a resposta tem `requires_company_selection`, renderiza a lista de
  `{tenant_name, company_name, user_role}` e re-loga com o `tenant_id` escolhido.
- **Tela de Administração** (owner/admin) com abas:
  - **Empresas** — tabela + modal (criar/editar/excluir) + modal de **Acesso** (atribuir usuários,
    inclusive criar usuário novo direto ali). Upload de logo (resize → data URL).
  - **Usuários** — tabela (papel inline, último login, status) + criar (com gerador de senha) +
    resetar senha.
  - **Plataforma** (só platform admin) — tenants (criar/suspender) + códigos de convite.

## Migrações & qualidade
- Crie as tabelas no padrão do projeto. Em coluna NOT NULL nova sobre tabela com dados, **sempre**
  `server_default` (senão a migração quebra nas linhas existentes). Migração **idempotente** quando
  possível (`ADD COLUMN IF NOT EXISTS`).
- **Nunca edite a migração inicial já aplicada** para adicionar coluna — crie uma nova (editar a
  0001 causa schema-drift: o banco diz estar no head mas a coluna não existe → 500).
- Teste o isolamento: usuário do tenant A **não** lê dado do tenant B (esperado 404); editor só vê
  empresas atribuídas; suspender tenant bloqueia login.

## Gotchas (aprendidos na prática)
- `tenant_id` **sempre do JWT**, jamais do request. Esqueça um filtro e vaza entre tenants.
- E-mail é único **por tenant**, não global — o login resolve múltiplos tenants por escolha.
- Recurso fora do escopo → **404**, não 403 (anti-enumeração).
- Promover platform admin é manual no banco (`UPDATE users SET is_platform_admin=true WHERE email=...`);
  não exponha endpoint para isso.
- Serviço de migração com imagem própria (Docker) precisa ser **rebuildado** junto do backend, senão
  roda código velho ("can't locate revision").

## Resumo a dar ao usuário ao terminar
- As 5 tabelas criadas/estendidas (Tenant, Company, User+is_platform_admin, UserCompanyAccess, InviteCode).
- Onde está o isolamento (`core/access.py`) e que toda query filtra `tenant_id` + escopo de empresa.
- Endpoints: auth (register com convite, login multi-tenant), companies, users, platform (onboarding+convites).
- Frontend: header X-Company-Id, CompanyContext/seletor, login com seleção de tenant, tela de Administração.
- Como promover o primeiro platform admin e como testar o isolamento.
- Lembrar de aplicar o **auth-kit** para login/senha/reset/RBAC.
