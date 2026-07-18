---
name: auditai-ui
description: >-
  Aplica em qualquer projeto web o MESMO sistema de design do AuditAI — "dark
  profissional" com accent teal: tokens de cor (ink/brand + danger/warn/ok),
  tipografia Inter, sombras (glow/card), fundo com gradiente radial, e as classes
  de componente (.btn/.card/.pill/.input/.label). Inclui o layout (sidebar + header
  com breadcrumb), KPI cards com sparkline e delta, ChartCard, formulários/inputs
  com ícone, modais e os princípios de UX (animações framer-motion discretas,
  estados de loading/erro, acessibilidade). Use quando o usuário pedir "deixa com a
  cara do AuditAI", "aplica o design/UI do AuditAI", "mesmo visual/tema do AuditAI",
  "cores e layout do AuditAI", "design system", "padroniza a UI" ou "aplica o
  auditai-ui aqui".
---

# auditai-ui — sistema de design do AuditAI (dark pro + teal) reutilizável

Reproduz fielmente a identidade visual e os padrões de UX do AuditAI em **qualquer
projeto web**: paleta **navy escuro (`ink-*`) + teal (`brand-*`)**, tipografia **Inter**,
fundo com **gradiente radial**, sombras **glow/card**, classes de componente prontas e os
componentes-chave (Layout, KPI, ChartCard, Tooltip, formulários, modais).

> **Identidade em uma frase:** dark sóbrio e corporativo, um único accent (teal `#22997a`),
> bordas sutis, cantos arredondados, animações curtas de entrada (fade + slide-up), texto
> em escala de cinza-azulado. Nada de cores berrantes; semáforo só em status (vermelho/amarelo/verde).

## Quando usar
Ao iniciar a UI de um projeto novo, ou para **padronizar/retematizar** um existente com a
cara do AuditAI. Combina com os skills irmãos: **rich-tooltips** (tooltips), **multilang**
(i18n no header), **auth-kit** (login/perfil na sidebar).

## Passo 0 — Detectar o stack
- **Ideal:** React + Vite + Tailwind + `lucide-react` + `framer-motion` + `clsx` (stack do AuditAI).
- **Sem Tailwind?** Use o bloco "Sem Tailwind" no fim — os mesmos tokens viram CSS variables.
- **Outro framework (Vue/Svelte/HTML puro)?** Os tokens e o CSS de componentes são portáveis;
  só as classes utilitárias do JSX mudam. Mantenha **as mesmas cores, raios, sombras e fontes**.
- Se já existir um tema, **pergunte** antes de sobrescrever cores globais.

## Passo 1 — Dependências (stack React/Tailwind)
```bash
npm i lucide-react framer-motion clsx
npm i -D tailwindcss postcss autoprefixer
```
`recharts` só se for usar sparkline no KPI / gráficos.

## Passo 2 — Tokens de cor + tema (Tailwind)
Crie/atualize `tailwind.config.js` com a paleta **exata** do AuditAI:

```js
/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: { sans: ["Inter", "system-ui", "Segoe UI", "Roboto", "sans-serif"] },
      colors: {
        // accent principal (teal) — usado em CTAs, links ativos, destaques
        brand: {
          50: "#eefaf6", 100: "#d3f1e6", 200: "#a7e1cf", 300: "#6fcab1", 400: "#3eb393",
          500: "#22997a", 600: "#177964", 700: "#136251", 800: "#114e42", 900: "#0f4138",
        },
        // navy/cinza-azulado — textos, superfícies, bordas
        ink: {
          50: "#f3f5f9", 100: "#e2e6ee", 200: "#c3cad7", 300: "#94a0b4", 400: "#5e6e88",
          500: "#3f4d63", 600: "#2c374a", 700: "#1f2839",
          800: "#141b29",  // superfície de cards
          900: "#0b0f1a",  // canvas (fundo primário)
          950: "#070a13",  // hero / extra escuro
        },
        danger: { DEFAULT: "#f43f5e", soft: "#3b1620" },  // irregular / erro
        warn:   { DEFAULT: "#fbbf24", soft: "#3a2a08" },  // pendente / atenção
        ok:     { DEFAULT: "#34d399", soft: "#0e2e22" },  // regular / sucesso
      },
      boxShadow: {
        glow: "0 0 40px -8px rgba(34,153,122,.35)",
        card: "0 1px 0 rgba(255,255,255,.04) inset, 0 8px 24px -12px rgba(0,0,0,.5)",
      },
      backgroundImage: {
        "grid-fade": "radial-gradient(ellipse 80% 50% at 50% -20%, rgba(34,153,122,.18), transparent 60%)",
      },
    },
  },
  plugins: [],
};
```

> **Mapa mental das cores:** `ink-900` = fundo, `ink-800` = card, `ink-700/600` = bordas,
> `ink-100/200` = texto principal, `ink-300/400` = texto secundário/mudo, `brand-500` = accent,
> `brand-300` = accent sobre fundo escuro (links/labels), `danger/warn/ok` = só status.

## Passo 3 — CSS base + classes de componente
`src/styles.css` (importe no entrypoint). Define o fundo com gradiente, foco acessível, seleção,
e as classes reutilizáveis `.btn* / .card* / .pill* / .input / .label`:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  html, body, #root { height: 100%; }
  body {
    @apply bg-ink-900 text-ink-100 antialiased;
    font-family: 'Inter', system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
    -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale;
    text-rendering: optimizeLegibility;
    background-image:
      radial-gradient(ellipse 1200px 600px at 50% -10%, rgba(34,153,122,.10), transparent 60%),
      linear-gradient(180deg, #070a13 0%, #0b0f1a 100%);
    background-attachment: fixed;
  }
  svg text { text-rendering: geometricPrecision; }       /* texto nítido em gráficos/SVG */
  ::selection { background: rgba(34,153,122,.35); color: #fff; }
  *:focus-visible { outline: 2px solid #22997a; outline-offset: 2px; border-radius: 6px; }
}

@layer components {
  .btn {
    @apply inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2 font-medium
           transition-all duration-150 disabled:opacity-50 disabled:cursor-not-allowed;
  }
  .btn-primary { @apply btn bg-brand-500 text-white hover:bg-brand-400 shadow-glow; }
  .btn-ghost   { @apply btn bg-ink-800 text-ink-100 border border-ink-700 hover:bg-ink-700; }
  .btn-danger  { @apply btn bg-danger text-white hover:opacity-90; }

  /* Card SÓLIDO (sem backdrop-blur): blur+filter borra o texto em Chrome/Edge com aceleração. */
  .card       { @apply bg-ink-800 border border-ink-700 rounded-xl shadow-card; }
  .card-hover { @apply card transition-all duration-200 hover:border-brand-500/50 hover:shadow-glow hover:-translate-y-0.5; }

  .pill           { @apply inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium; }
  .pill-irregular { @apply pill bg-danger/15 text-danger border border-danger/30; }
  .pill-regular   { @apply pill bg-ok/15 text-ok border border-ok/30; }
  .pill-pendente  { @apply pill bg-warn/15 text-warn border border-warn/30; }
  .pill-fora      { @apply pill bg-ink-700 text-ink-300 border border-ink-600; }

  .input { @apply bg-ink-900 border border-ink-700 rounded-lg px-3 py-2 text-ink-100
                  placeholder:text-ink-400 focus:border-brand-500 focus:outline-none; }
  .label { @apply text-xs font-medium text-ink-300 uppercase tracking-wider; }
}
```

**Se usar Recharts, adicione também** (fora de `@layer`) — sem isto o tooltip nasce com
texto escuro sobre fundo escuro ("preto no preto") em todos os gráficos, porque o
`contentStyle` inline de cada chart escurece o fundo mas não a cor do texto:

```css
.recharts-default-tooltip {
  background: #0b0f1a !important;
  border: 1px solid #1f2839 !important;
  border-radius: 8px !important;
  padding: 8px 10px !important;
  box-shadow: 0 8px 24px rgba(0, 0, 0, .45) !important;
}
.recharts-tooltip-wrapper { outline: none !important; z-index: 50; }
.recharts-tooltip-label { color: #e5e9f0 !important; font-weight: 600 !important; margin-bottom: 4px !important; }
.recharts-tooltip-item,
.recharts-tooltip-item-name,
.recharts-tooltip-item-value,
.recharts-tooltip-item-separator { color: #cbd5e1 !important; }
```

> Nota de armadilha já resolvida: **não use `backdrop-blur` no `.card`**. Em Chrome/Edge com
> aceleração de hardware o `filter` quebra o anti-alias sub-pixel e o texto dentro do card
> fica borrado. O `.card` é sólido (`bg-ink-800`) de propósito.

Carregue a fonte Inter no `index.html` (`<head>`):
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
```

## Passo 4 — Layout: sidebar + header com breadcrumb
Padrão de app: **sidebar fixa (w-64)** com logo+itens de nav (ícone lucide + label, item ativo
em teal) e bloco de usuário/logout embaixo; **header (h-14)** com breadcrumb à esquerda e
ações à direita (versão/seletor de idioma). Conteúdo via `<Outlet/>` rola sozinho.

```tsx
import { Link, NavLink, Outlet, useLocation } from "react-router-dom";
import { LayoutDashboard, ShieldCheck, LogOut, Home } from "lucide-react";
import clsx from "clsx";

const NAV = [{ to: "/dashboard", label: "Dashboard", icon: LayoutDashboard }];

export function Layout() {
  const loc = useLocation();
  const itemCls = ({ isActive }: { isActive: boolean }) =>
    clsx("flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium",
      isActive ? "bg-brand-500/10 text-brand-300 border border-brand-500/20"
               : "text-ink-300 hover:bg-ink-800 hover:text-ink-100");
  return (
    <div className="min-h-screen flex">
      <aside className="w-64 shrink-0 border-r border-ink-800 bg-ink-900/80 backdrop-blur-md flex flex-col">
        <Link to="/" className="px-5 py-5 flex items-center gap-2 border-b border-ink-800">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-brand-400 to-brand-600 grid place-items-center shadow-glow">
            <ShieldCheck className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="font-bold tracking-tight">MeuApp</div>
            <div className="text-[11px] text-ink-400 -mt-0.5">subtítulo</div>
          </div>
        </Link>
        <nav className="flex-1 px-3 py-4 space-y-1">
          <NavLink to="/" end className={itemCls}><Home className="w-4 h-4" /> Início</NavLink>
          {NAV.map(({ to, label, icon: Icon }) => (
            <NavLink key={to} to={to} className={itemCls}><Icon className="w-4 h-4" /> {label}</NavLink>
          ))}
        </nav>
        <div className="p-3 border-t border-ink-800">
          <button className="btn-ghost w-full text-sm"><LogOut className="w-4 h-4" /> Sair</button>
        </div>
      </aside>
      <main className="flex-1 min-w-0 flex flex-col">
        <header className="h-14 px-6 border-b border-ink-800 bg-ink-900/60 backdrop-blur-md flex items-center justify-between">
          <div className="text-sm text-ink-300">
            <span className="text-ink-500">MeuApp</span>
            <span className="mx-2 text-ink-600">/</span>
            <span className="text-ink-100 font-medium capitalize">{loc.pathname.replace("/", "") || "Início"}</span>
          </div>
        </header>
        <div className="flex-1 overflow-auto"><Outlet /></div>
      </main>
    </div>
  );
}
```

## Passo 5 — Componentes-assinatura

### KPI card (valor + delta colorido + sparkline)
- Fonte do valor **encolhe sozinha** conforme o comprimento (não corta).
- `delta` colore verde/vermelho (com `deltaIsBad` para inverter quando "subir é ruim").
- Ícone vira badge no canto; `tabular-nums` alinha os dígitos; entrada com framer-motion.
- Tooltip rico (ícone "i") no label — ver skill **rich-tooltips**.

```tsx
import { motion } from "framer-motion";
import { ArrowDownRight, ArrowUpRight, Minus, type LucideIcon } from "lucide-react";
import clsx from "clsx";

export function Kpi({ label, value, delta, deltaIsBad, icon: Icon, color = "#22997a", delay = 0, onClick }:
  { label: string; value: string | number; delta?: number; deltaIsBad?: boolean;
    icon?: LucideIcon; color?: string; delay?: number; onClick?: () => void }) {
  const txt = String(value);
  const valueClass = txt.length >= 14 ? "text-base" : txt.length >= 11 ? "text-lg"
                   : txt.length >= 8 ? "text-xl" : "text-2xl";
  const has = typeof delta === "number" && Number.isFinite(delta);
  const pos = (delta ?? 0) > 0, neg = (delta ?? 0) < 0;
  const good = deltaIsBad ? neg : pos, bad = deltaIsBad ? pos : neg;
  const dc = !has || delta === 0 ? "text-ink-400" : good ? "text-ok" : bad ? "text-danger" : "text-ink-400";
  const DI = !has || delta === 0 ? Minus : pos ? ArrowUpRight : ArrowDownRight;
  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, delay }} whileHover={onClick ? { y: -3 } : undefined} onClick={onClick}
      className={clsx("card-hover p-4 relative overflow-hidden",
        onClick ? "cursor-pointer select-none" : "cursor-default hover:!translate-y-0 hover:!shadow-card")}>
      {Icon && (
        <div className="absolute top-3 right-3 w-7 h-7 rounded-lg grid place-items-center opacity-80"
             style={{ background: color + "22", color }}><Icon className="w-3.5 h-3.5" /></div>
      )}
      <div className="text-[11px] text-ink-400 uppercase font-semibold leading-tight pr-9 mb-2">{label}</div>
      <div className={`${valueClass} font-bold tabular-nums truncate`}>{value}</div>
      {has && (
        <div className={clsx("mt-2 flex items-center gap-0.5 text-xs font-semibold", dc)}>
          <DI className="w-3.5 h-3.5" /> {Math.abs(delta!).toFixed(1)}%
        </div>
      )}
    </motion.div>
  );
}
```

### ChartCard (moldura padrão de qualquer painel/gráfico)
```tsx
import type { ReactNode } from "react";
import { motion } from "framer-motion";
import { Info } from "lucide-react";
import clsx from "clsx";

export function ChartCard({ title, subtitle, hint, actions, className, children, delay = 0 }:
  { title: string; subtitle?: string; hint?: string; actions?: ReactNode;
    className?: string; children: ReactNode; delay?: number }) {
  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay }} className={clsx("card p-5", className)}>
      <div className="flex items-start justify-between gap-2 mb-4">
        <div>
          <div className="text-sm font-semibold text-ink-100 flex items-center gap-1.5">
            {title}
            {hint && <span title={hint} className="inline-flex"><Info className="w-3.5 h-3.5 text-ink-400 cursor-help" /></span>}
          </div>
          {subtitle && <div className="text-[11px] text-ink-400 mt-0.5">{subtitle}</div>}
        </div>
        {actions}
      </div>
      {children}
    </motion.div>
  );
}
```

### Status pills
Use as classes prontas para qualquer máquina de estado (mapeie os nomes ao seu domínio):
```tsx
<span className="pill-regular">Regular</span>
<span className="pill-irregular">Irregular</span>
<span className="pill-pendente">Pendente</span>
<span className="pill-fora">Fora de escopo</span>
```

### Tooltip rico
Para ajuda contextual formatada (título + lista + chave:valor, via portal, auto-flip),
**use o skill `rich-tooltips`** — é o componente irmão deste design system.

## Passo 6 — Padrões de página

### Tela de login/auth split (hero à esquerda + form à direita)
Hero (`hidden lg:flex`) com `bg-grid-fade` + um *blob* `bg-brand-500/20 blur-3xl`, logo, headline
`text-4xl font-extrabold`, bullets com pontinho teal; form `max-w-md` com inputs que têm **ícone
lucide à esquerda** (`pl-10`), erro em caixa `bg-danger/10 border-danger/30`, CTA `btn-primary w-full`.

```tsx
// input com ícone (padrão em todo formulário)
<label className="label block mb-1.5">E-mail</label>
<div className="relative">
  <Mail className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-ink-400" />
  <input type="email" className="input w-full pl-10" placeholder="voce@empresa.com" />
</div>

// bloco de erro
{err && (
  <div className="flex items-start gap-2 text-sm text-danger bg-danger/10 border border-danger/30 rounded-lg px-3 py-2">
    <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" /> {err}
  </div>
)}
```

### Modal (overlay escuro + card centralizado, fecha no backdrop)
```tsx
<div className="fixed inset-0 z-50 bg-black/60 grid place-items-center p-4" onClick={onClose}>
  <div className="card p-6 max-w-sm w-full" onClick={(e) => e.stopPropagation()}>
    <div className="flex items-center justify-between mb-1">
      <h3 className="font-semibold flex items-center gap-2"><Lock className="w-4 h-4 text-brand-300" /> Título</h3>
      <button onClick={onClose} className="text-ink-500 hover:text-ink-200"><X className="w-4 h-4" /></button>
    </div>
    {/* conteúdo */}
  </div>
</div>
```

## Princípios de UX (o "jeito AuditAI")
- **Um accent só (teal).** Cor extra apenas para **status** (vermelho/amarelo/verde). Nunca
  colorir por enfeite — cor carrega significado.
- **Hierarquia por cinza.** Texto principal `ink-100/200`, secundário `ink-300/400`, mudo `ink-500`.
  Títulos de seção em `text-sm font-semibold`; labels em `.label` (uppercase, tracking, `ink-300`).
- **Animações curtas e discretas:** entrada `opacity+y` 0.35–0.4s (framer-motion), `delay` escalonado
  por índice em listas/grids; hover de card sobe 0.5px + glow. Nada de bounce/spring chamativo.
- **Bordas e raios consistentes:** borda `ink-700`, hover `brand-500/50`; raios `rounded-lg`
  (controles) e `rounded-xl` (cards); sombra `card` em repouso, `glow` no destaque/hover.
- **Números:** sempre `tabular-nums`; valores longos encolhem a fonte (ver KPI) em vez de cortar.
- **Estados sempre visíveis:** loading (`Loader2 animate-spin`), erro (caixa `danger/10`), vazio,
  sucesso (`CheckCircle2` verde). Botão desabilitado = `opacity-50 cursor-not-allowed` (já no `.btn`).
- **Acessibilidade:** `focus-visible` com anel teal global; ícones com texto ao lado; modal/tooltip
  com `role`; foco do teclado abre tooltips (ver rich-tooltips).
- **Ícones:** biblioteca única (**lucide-react**), tamanho `w-4 h-4` (inline) / `w-3.5 h-3.5` (badge).
- **Sem `backdrop-blur` em cards de conteúdo** (borra texto no Chrome/Edge). Blur só em barras
  fixas translúcidas (sidebar/header).

## Sem Tailwind? (CSS variables — mesmo tema)
Defina os tokens como variáveis e use nas suas classes:
```css
:root{
  --ink-900:#0b0f1a; --ink-800:#141b29; --ink-700:#1f2839; --ink-400:#5e6e88;
  --ink-300:#94a0b4; --ink-100:#e2e6ee; --brand-500:#22997a; --brand-300:#6fcab1;
  --danger:#f43f5e; --warn:#fbbf24; --ok:#34d399;
  --shadow-card:0 1px 0 rgba(255,255,255,.04) inset,0 8px 24px -12px rgba(0,0,0,.5);
  --shadow-glow:0 0 40px -8px rgba(34,153,122,.35);
}
body{ background:#0b0f1a; color:var(--ink-100); font-family:Inter,system-ui,sans-serif;
  background-image:radial-gradient(ellipse 1200px 600px at 50% -10%,rgba(34,153,122,.10),transparent 60%),
                   linear-gradient(180deg,#070a13,#0b0f1a); background-attachment:fixed; }
.card{ background:var(--ink-800); border:1px solid var(--ink-700); border-radius:.75rem; box-shadow:var(--shadow-card); }
.btn-primary{ background:var(--brand-500); color:#fff; border-radius:.5rem; padding:.5rem 1rem; box-shadow:var(--shadow-glow); }
```

## Checklist ao aplicar
1. `tailwind.config.js` com `brand`/`ink`/`danger`/`warn`/`ok`, `boxShadow.glow|card`, fonte Inter.
2. `styles.css` com base (fundo gradiente, focus, selection) + classes `.btn*/.card*/.pill*/.input/.label`.
3. Inter carregada no `index.html`.
4. Layout sidebar+header; páginas usando `.card`, `Kpi`, `ChartCard`, pills de status.
5. (Opcional) `rich-tooltips` para ajuda contextual, `multilang` no header, `auth-kit` na sidebar.

## Resumo ao terminar
Diga o que foi criado/alterado (config, CSS, componentes), confirme que as **cores são as do
AuditAI** (teal `#22997a` + navy `ink-*`) e aponte os skills irmãos que combinam (rich-tooltips,
multilang, auth-kit). Mostre 1 print/rota de exemplo se subir o app.
