---
name: support-chat
description: >-
  Adiciona a QUALQUER aplicação web um chat de SUPORTE OPERACIONAL com IA: botão flutuante
  presente em todas as telas que ensina o usuário a usar o sistema, encontra funcionalidades
  e ajuda a resolver problemas de uso. O diferencial é que o CONHECIMENTO se sincroniza sozinho
  com o app — a lista de módulos/telas vem do MENU VIVO (a navegação manda menu + tela atual em
  cada pergunta) e o backend monta a base de conhecimento dinamicamente; só o papel, segurança/
  LGPD e tom ficam num system prompt curado e estável. Resultado: adicionar/renomear/remover um
  item de menu reflete no suporte SEM editar prompt. Conversas persistidas e escopadas por
  tenant + usuário (anti-IDOR), tier de LLM barato. Use quando o usuário pedir "chat de suporte",
  "assistente de ajuda", "suporte com IA", "ajuda contextual na tela", "bot de suporte
  operacional", "widget de suporte", ou "aplica o support-chat aqui".
---

# support-chat — chat de suporte operacional (IA) com conhecimento auto-sincronizado

Objetivo: rodar nesta app e ela passa a ter um **assistente de suporte de uso** (não jurídico,
não comercial) num botão flutuante em **todas as telas autenticadas**. Ele ensina onde clicar,
encontra funcionalidades e resolve dúvidas de uso.

> **A ideia central (não negociável):** o conhecimento sobre "quais telas existem e onde ficam"
> NÃO vive num texto escrito à mão. Ele é **derivado do menu de navegação do próprio app**. O
> widget envia, em cada pergunta, o menu visível (rótulo + ajuda, já no idioma atual) e a tela
> onde o usuário está; o backend monta a seção de módulos a partir disso. Assim, mexer no menu
> reflete no suporte automaticamente. Só o que muda pouco — papel do bot, segurança/LGPD, tom —
> fica num system prompt curado. **Nunca** reintroduza uma lista de módulos hardcoded no prompt:
> isso recria a manutenção manual que esta skill existe para eliminar.

O código de referência abaixo é **FastAPI + SQLAlchemy 2.0 (async) + React/Vite/TS** (padrão do
ecossistema). Em outra stack, mantenha o MESMO contrato e os MESMOS princípios.

## Passo 0 — Detectar a stack e os pré-requisitos
Identifique e reaproveite o que já existe — **não duplique infra**:
- **Auth:** como se obtém o usuário autenticado (dependência tipo `get_current_user`) e, se a app
  for multi-tenant, o `tenant_id`. Se não houver auth, o chat fica só por usuário.
- **LLM:** já existe um cliente/roteador de LLM? Use-o no **tier mais barato** (haiku/mini). Se não
  existir, crie um wrapper mínimo lendo a chave de `~/.config/llm-keys/keys.env` (skill `llm-keys`).
- **Menu/navegação:** ONDE está a lista de itens de menu do app? É a **fonte da verdade** desta
  skill. Se estiver embutida num componente de layout, **extraia para um módulo compartilhado**
  (ex.: `src/config/nav.ts`) para que layout e widget usem o mesmo array.
- **i18n:** se a app é multilíngue, o suporte responde no idioma da pergunta e o menu enviado já
  vem traduzido. Reaproveite as chaves de ajuda do menu (são os mesmos textos dos tooltips).

## Passo 1 — Fonte única do menu (o que torna o conhecimento automático)
Garanta um único array de navegação, compartilhado entre o layout e o widget. Cada item tem rota,
rótulo e um texto de **ajuda** curto (o "o que faz / como usar" daquele módulo — também serve de
tooltip). Esse texto de ajuda é o ÚNICO lugar a editar quando o comportamento de um módulo muda.

```ts
// src/config/nav.ts — FONTE ÚNICA da estrutura do app (layout + chat de suporte)
import type { LucideIcon } from "lucide-react";
export interface NavItem {
  to: string;
  labelKey: string;   // chave i18n do rótulo
  icon: LucideIcon;
  helpKey: string;    // chave i18n da ajuda (tooltip E base do suporte)
  perm?: string;      // permissão p/ ver o item (omitida = sempre visível)
}
export const NAV_ITEMS: NavItem[] = [
  { to: "/dashboard", labelKey: "nav.dashboard", icon: LayoutDashboard, helpKey: "nav.dashboardHelp" },
  // ...demais módulos
];
```

O layout importa `NAV_ITEMS` (em vez de declarar inline) e renderiza a sidebar a partir dele.

## Passo 2 — Backend: modelos de conversa (persistência + isolamento)
Duas tabelas: `support_conversa` e `support_mensagem`. Se a app é multi-tenant, ambas levam
`tenant_id` (com o mixin de tenant do projeto) e tudo é escopado por **tenant_id + user_id** —
cada usuário só acessa as próprias conversas (**anti-IDOR**, exige teste de isolamento).

```python
# models/support.py
ROLE_USER, ROLE_ASSISTANT = "user", "assistant"

class SupportConversa(TenantMixin, Base):           # TenantMixin: só se multi-tenant
    __tablename__ = "support_conversa"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), index=True)
    title: Mapped[str | None] = mapped_column(String(200))
    # created_at / updated_at

class SupportMensagem(TenantMixin, Base):
    __tablename__ = "support_mensagem"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    conversa_id: Mapped[str] = mapped_column(String(36), index=True)
    role: Mapped[str] = mapped_column(String(16))   # user | assistant
    content: Mapped[str] = mapped_column(Text)
    # created_at
```
Gere a migration (Alembic ou equivalente).

## Passo 3 — Backend: schema do contexto vivo
O request de chat carrega um `context` opcional com o menu (no idioma do cliente) e a tela atual.

```python
# schemas/support.py
class SupportMenuItem(BaseModel):
    path: str = Field(max_length=200)
    label: str = Field(max_length=200)
    help: str = Field(default="", max_length=1000)

class SupportContext(BaseModel):
    current_path: str | None = Field(default=None, max_length=200)
    current_screen: str | None = Field(default=None, max_length=200)
    menu: list[SupportMenuItem] = Field(default_factory=list, max_length=50)

class SupportChatRequest(BaseModel):
    content: str = Field(min_length=1, max_length=4000)
    conversa_id: str | None = None
    context: SupportContext | None = None
```

## Passo 4 — Backend: service (prompt curado + bloco dinâmico)
O system prompt curado descreve SÓ o que muda pouco: papel, segurança/LGPD, regras de resposta.
A lista de módulos é montada de `context.menu` em `_build_context_block()`. **Não** duplique
módulos no prompt curado.

```python
# services/support.py
SUPPORT_SYSTEM_PROMPT = """\
Você é o assistente de suporte do <APP>, focado em SUPORTE OPERACIONAL: ensinar o usuário a
usar o sistema, onde clicar e resolver problemas de uso.

A relação de módulos disponíveis e onde ficam no menu é fornecida abaixo, em "Contexto atual
do sistema", e é a FONTE DA VERDADE sobre o que existe. Quando souber a tela atual, contextualize.

# Segurança e LGPD
- Acesso por login com papéis; cada empresa só vê os próprios dados; dados sensíveis cifrados.
- Pedidos de exclusão/retenção (direitos do titular LGPD) → orientar a falar com o administrador.

# Como responder
- Responda NO MESMO IDIOMA da pergunta. Seja objetivo: passo a passo curto ("Vá em X → clique em Y"),
  usando os nomes de menu exatamente como no contexto.
- NÃO invente telas/botões que não estejam no contexto. Fora do escopo de uso (ex.: decisão de
  negócio/jurídica) → diga que não tem a informação e oriente procurar o administrador.
- Nunca peça nem repita senhas, tokens ou dados sensíveis.
"""

def _build_context_block(context: SupportContext | None) -> str:
    if context is None or not context.menu:
        return ("\n# Contexto atual do sistema\n(menu não informado) — oriente de forma geral "
                "e, se preciso, pergunte em que tela o usuário está.")
    linhas = [f'- **{i.label}** (menu "{i.path}"): {i.help}'.rstrip(": ") for i in context.menu]
    bloco = "\n# Contexto atual do sistema\n## Módulos disponíveis (menu)\n" + "\n".join(linhas)
    if context.current_screen:
        bloco += (f"\n\n## Tela atual\nO usuário está em **{context.current_screen}** "
                  f"({context.current_path}). Contextualize a resposta a partir dela quando fizer sentido.")
    return bloco

async def chat(db, *, tenant_id, user_id, content, conversa_id=None, context=None):
    # 1. carrega/cria a conversa (validando tenant_id + user_id — anti-IDOR)
    # 2. persiste a pergunta (role=user)
    # 3. monta o diálogo dos últimos _MAX_HISTORY=16 turnos (limita custo)
    # 4. chama o LLM no tier barato:
    resposta = await llm.complete(
        prompt, tier="haiku",
        system=SUPPORT_SYSTEM_PROMPT + _build_context_block(context),
        funcao="support:chat",
    )
    # 5. persiste a resposta (role=assistant) e retorna (conversa, mensagem)
```

## Passo 5 — Backend: endpoints (escopados por tenant + usuário)
```python
# apis/.../support.py  — prefixo /support, exige usuário autenticado
POST /support/chat                              -> {conversa_id, message}
GET  /support/conversas                         -> conversas DO usuário
GET  /support/conversas/{id}/mensagens          -> mensagens (valida que a conversa é do usuário)
```
Toda query filtra por `tenant_id` (se multi-tenant) **e** `user_id`. Conversa de outro usuário →
404. O endpoint repassa `body.context` para o service.

## Passo 6 — Frontend: lib + widget
`lib/support.ts` define `SupportContext` e envia em cada pergunta:
```ts
export interface SupportMenuItem { path: string; label: string; help: string; }
export interface SupportContext { current_path: string; current_screen: string | null; menu: SupportMenuItem[]; }
export const sendSupportMessage = (content: string, conversaId?: string | null, context?: SupportContext) =>
  apiPost("/support/chat", { content, conversa_id: conversaId ?? null, context: context ?? null });
```

`components/support/SupportWidget.tsx` — botão flutuante (portal + animação), montado UMA vez no
layout raiz. Ao enviar, constrói o contexto a partir do menu vivo e da rota atual:
```ts
const buildContext = (): SupportContext => {
  const visible = NAV_ITEMS.filter((i) => !i.perm || can(i.perm));   // respeita permissões
  const current = visible.find((i) => i.to === "/" + location.pathname.split("/")[1]);
  return {
    current_path: location.pathname,
    current_screen: current ? t(current.labelKey) : null,
    menu: visible.map((i) => ({ path: i.to, label: t(i.labelKey), help: t(i.helpKey) })),
  };
};
// submit(): sendSupportMessage(content, conversaId, buildContext())
```
Monte o widget no layout raiz (uma vez, fora do `<Outlet/>`), para aparecer em todas as telas.

## Passo 7 — i18n
Adicione as chaves do widget (`support.button/title/subtitle/greeting/placeholder/...`) em TODOS
os idiomas suportados pelo projeto, com paridade de chaves. A ajuda do menu (`nav.*Help`) já
existe e é reaproveitada — é o "como usar" que o suporte consome.

## Passo 8 — Rede de segurança (opcional, recomendado)
- **Teste de isolamento** (multi-tenant): usuário A não enxerga conversa de B; tenant X não vê Y.
- O acoplamento "menu → suporte" dispensa atualizar prompt ao mudar telas. Documente no
  `CLAUDE.md`/README do projeto que o "como usar" de cada módulo se edita no texto de ajuda do
  menu (`nav.*Help`), nunca numa lista solta dentro do prompt.

## Princípios (resumo do que NÃO pode regredir)
1. **Conhecimento de "o que existe" = menu vivo**, enviado a cada request. Zero lista hardcoded no prompt.
2. **Só papel + segurança + tom são curados** (mudam pouco).
3. **Tela atual no contexto** → respostas contextuais.
4. **Escopo por tenant + usuário** em toda query (anti-IDOR) + teste de isolamento.
5. **Tier de LLM barato** + histórico limitado (≈16 turnos) para conter custo.
6. **Suporte de USO**, não jurídico/comercial; nunca manipula segredos.
