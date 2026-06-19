---
name: multilang
description: >-
  Adiciona suporte multilíngue (i18n) a um projeto web: seletor de idioma fixo
  no topo da tela + idioma preferido no cadastro/perfil do usuário, já com
  Inglês, Português (Brasil), Espanhol e Francês — e fácil de adicionar novos
  idiomas depois. Use quando o usuário pedir "suporte a idiomas",
  "internacionalização", "i18n", "multilíngue", "traduzir a interface",
  "seletor de idioma", "trocar idioma", ou "adicionar mais uma língua".
---

# Multilang — internacionalização (i18n) com seletor no topo + idioma do usuário

Objetivo: deixar a UI de um projeto **multilíngue**, com:
1. **Seletor de idioma fixo no topo da tela** (header/top bar), em todas as telas.
2. **Idioma preferido no cadastro/perfil do usuário** (vem pré-selecionado ao logar).
3. Idiomas iniciais: **`en`, `pt-BR`, `es`, `fr`** — e um caminho **trivial** para
   adicionar novos idiomas no futuro (só um arquivo a mais).

Princípios:
- **Não quebrar o que já existe:** todo texto sem tradução cai no idioma padrão (fallback).
- **Uma fonte de verdade por idioma** (um arquivo de dicionário por idioma).
- **Adicionar idioma = adicionar 1 arquivo + 1 linha** numa lista central.

---

## Passo 0 — Detectar o stack
1. Leia `package.json` (front) e o backend (Python/FastAPI? Node? etc.).
2. Identifique o framework de UI: **React**, **Vue**, **Svelte**, **Next**, ou HTML puro.
3. Veja se já existe i18n (`react-i18next`, `vue-i18n`, `i18next`, `next-intl`…).
   - Se já existir, **estenda** o que há (adicione idiomas + seletor + preferência do
     usuário) em vez de recriar.
4. Veja se há autenticação/cadastro de usuário (para o passo do idioma preferido).

## Convenção de idiomas (central, reutilizável)
Crie uma lista única de idiomas suportados — **a única coisa a editar para adicionar um novo**:
```
LANGUAGES = [
  { code: "en",    label: "English",            flag: "🇺🇸" },
  { code: "pt-BR", label: "Português (Brasil)", flag: "🇧🇷" },
  { code: "es",    label: "Español",            flag: "🇪🇸" },
  { code: "fr",    label: "Français",           flag: "🇫🇷" },
]
DEFAULT_LANGUAGE = "pt-BR"   // ou "en"; alinhe com o usuário
```
> **Para adicionar um idioma no futuro:** crie `locales/<code>.json` e acrescente uma
> linha nesta lista. Nada mais.

## Ordem de detecção do idioma (na inicialização)
1. Preferência do **usuário logado** (campo `preferred_language` no perfil), se houver.
2. Escolha salva no **localStorage** (`app.lang`).
3. **Idioma do navegador** (`navigator.language`), casado com a lista suportada.
4. **DEFAULT_LANGUAGE**.

---

## Implementação por framework

### React (recomendado: `react-i18next`)
1. Instale: `react-i18next i18next i18next-browser-languagedetector`.
2. Crie `src/i18n/locales/{en,pt-BR,es,fr}.json` com as chaves por funcionalidade
   (ex.: `{"nav": {"dashboard": "Dashboard"}, "auth": {"login": "Entrar"}}`).
   Comece extraindo os textos visíveis das telas atuais para as chaves.
3. Crie `src/i18n/index.ts` que registra os recursos a partir da lista `LANGUAGES`,
   configura `fallbackLng: DEFAULT_LANGUAGE`, e o detector (localStorage → navigator).
4. Importe o i18n no entrypoint (`main.tsx`).
5. Troque textos fixos por `t("chave")` via `useTranslation()`.
6. **Seletor no topo:** componente `LanguageSwitcher` (dropdown com flag+label) montado
   no **header/top bar** do layout, presente em todas as telas. Ao trocar:
   `i18n.changeLanguage(code)` + salva no localStorage + (se logado) persiste no perfil.

> ⚠️ **Armadilha do i18next (códigos regionais como `pt-BR`):** NÃO use
> `nonExplicitSupportedLngs: true` junto com `supportedLngs` quando os recursos estiverem
> sob código regional (`pt-BR`, `en-US`). O i18next colapsa `pt-BR`→`pt` na busca, erra
> **todas** as chaves e mostra o texto cru (`nav.dashboard`, `auth.login`…) em todas as
> telas — parece "bugado/em inglês", mas é a chave aparecendo. Faça o mapeamento
> `pt`→`pt-BR` / `en-US`→`en` **antes** do init (helper `matchSupported(code)`) e passe um
> `lng` exato e suportado. Saneie também o `localStorage` (ex.: valor `cimode`, que é o
> modo do i18next que devolve as chaves) antes de inicializar.

> Alternativa **sem dependências** (projeto pequeno): um `LanguageContext` próprio com
> `t(key)` lendo JSONs e um `<LanguageSwitcher/>`. Use só se o usuário não quiser libs.

### Vue → `vue-i18n` (mesma estrutura de `locales/*.json` + `<LanguageSwitcher>` no header).
### Next → `next-intl` ou `next-i18next` (mesma lista central + switcher no layout).
### HTML/vanilla → um `t()` simples sobre objetos JSON + `<select>` no topo.

---

## Idioma preferido do usuário (cadastro/perfil)
Só se o projeto tiver usuários/auth. Faça ponta a ponta:
1. **Banco:** adicione coluna `preferred_language` (string curta, ex. `varchar(8)`) à
   tabela de usuários, com default = `DEFAULT_LANGUAGE`. Crie **migração** no padrão do
   projeto (Alembic/Prisma/Knex/…). Nunca apague dados.
2. **API:** inclua `preferred_language` no schema de criar/editar usuário e no `GET /me`.
   Valide contra a lista de idiomas suportados.
3. **Cadastro/Perfil (UI):** adicione um seletor de idioma no formulário de criar usuário
   e na edição de perfil (mesma lista `LANGUAGES`).
4. **No login:** ao receber o usuário, aplique `i18n.changeLanguage(user.preferred_language)`.
5. **Ao trocar pelo seletor do topo logado:** persista a escolha no perfil (PATCH) além do
   localStorage, para seguir o usuário em outros dispositivos.

## Backend (opcional, se a API devolve textos ao usuário)
- Aceite o header `Accept-Language` (ou um campo `lang`) e traduza mensagens com
  dicionários equivalentes no backend. Mantenha as MESMAS chaves do front quando fizer sentido.
- Vereditos/dados determinísticos não mudam; só os **rótulos/mensagens** são traduzidos.

---

## Qualidade e regras
- **Cobertura:** garanta que toda chave exista nos 4 idiomas; o que faltar cai no fallback
  (e, idealmente, logue as chaves faltantes em dev).
- **Sem hardcode:** não deixe texto fixo nas telas novas — sempre `t(...)`.
- **Acessibilidade:** atualize `<html lang="...">` ao trocar idioma.
- **Datas/números/moeda:** use `Intl` com o locale ativo (datas e R$/€/$ corretos por idioma).
- **Idempotente:** se rodar de novo, detecte o que já existe e só complete o que falta.
- **Teste rápido:** após aplicar, troque o idioma no topo e confira 2–3 telas + o login
  respeitando a preferência do usuário.

## Resumo a dar ao usuário ao terminar
- Onde está o **seletor no topo** e como trocar.
- Onde fica a **preferência de idioma** no cadastro/perfil.
- **Como adicionar um novo idioma:** "crie `locales/<code>.json` e adicione 1 linha em
  `LANGUAGES`" — mais nada.
