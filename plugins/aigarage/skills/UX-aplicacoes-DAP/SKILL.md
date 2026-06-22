---
name: UX-aplicacoes-DAP
description: >-
  Padrao de UX das aplicacoes da Direto ao Ponto (DAP) — "claro premium" com
  accent teal: fundo claro frio com glow radial (teal + um toque de indigo),
  tokens de cor (ink/brand + danger/warn/ok), tipografia Inter, sombras suaves,
  e as classes de componente (.btn/.card/.pill/.input/.label). Inclui o layout
  (sidebar + header com breadcrumb), KPI cards com sparkline e delta, ChartCard,
  formularios/inputs com icone, modais e os principios de UX (animacoes discretas,
  estados de loading/erro, acessibilidade). Use quando o usuario pedir "deixa com
  a cara das nossas apps", "aplica o padrao de UX da DAP", "design system",
  "padroniza a UI", "tema claro premium", ou "aplica o UX-aplicacoes-DAP aqui".
---

# UX-aplicacoes-DAP — design system padrao das apps DAP (light premium + teal)

Reproduz a identidade visual e os padroes de UX padrao das aplicacoes da **Direto
ao Ponto** em **qualquer projeto web**: **fundo claro frio premium** com glow
radial (teal + leve indigo), accent **teal `#22997a`**, tipografia **Inter**,
cards brancos com borda sutil, sombras suaves, classes de componente prontas e os
componentes-chave (Layout, KPI, ChartCard, Tooltip, formularios, modais).

> **Identidade em uma frase:** claro sobrio e corporativo, fundo frio com um brilho
> teal/indigo discreto, um unico accent (teal `#22997a`), cards brancos, bordas
> sutis, cantos arredondados, animacoes curtas de entrada (fade + slide-up), texto
> em escala de cinza-azulado escuro. Nada de cores berrantes; semaforo so em status
> (vermelho/amarelo/verde).

## Quando usar
Ao iniciar a UI de um projeto novo, ou para **padronizar/retematizar** um existente
com a cara das apps DAP. Combina com os skills irmaos: **rich-tooltips** (tooltips),
**multilang** (i18n no header), **auth-kit** (login/perfil na sidebar).

## Passo 0 — Detectar o stack
- **Ideal:** React + Vite + Tailwind + `lucide-react` + `framer-motion` + `clsx`.
- **Sem Tailwind?** Use o bloco "Sem Tailwind" no fim — os mesmos tokens viram CSS variables.
- **Outro framework (Vue/Svelte/HTML puro)?** Os tokens e o CSS de componentes sao
  portaveis; so as classes utilitarias do JSX mudam. Mantenha **as mesmas cores,
  raios, sombras e fontes**.
- Se ja existir um tema, **pergunte** antes de sobrescrever cores globais.

## Passo 1 — Dependencias (stack React/Tailwind)
```bash
npm i lucide-react framer-motion clsx
npm i -D tailwindcss postcss autoprefixer
```
`recharts` so se for usar sparkline no KPI / graficos.

## Passo 2 — Tokens de cor + tema (Tailwind)
Crie/atualize `tailwind.config.js` com a paleta **exata** do padrao DAP. Note que
no tema claro a rampa `ink` segue a semantica normal (numeros altos = mais escuro:
`ink-900` = texto, `ink-200` = borda), e o canvas claro vive no token `surface`.

```js
/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: { sans: ["Inter", "system-ui", "Segoe UI", "Roboto", "sans-serif"] },
      colors: {
        // accent principal (teal) — CTAs, links ativos, destaques.
        // Em fundo claro, prefira brand-600/700 para TEXTO/links (contraste).
        brand: {
          50: "#eefaf6", 100: "#d3f1e6", 200: "#a7e1cf", 300: "#6fcab1", 400: "#3eb393",
          500: "#22997a", 600: "#177964", 700: "#136251", 800: "#114e42", 900: "#0f4138",
        },
        // cinza-azulado (slate) — textos, bordas, superficies neutras (semantica normal)
        ink: {
          50: "#f8fafc", 100: "#f1f5f9", 200: "#e2e8f0", 300: "#cbd5e1", 400: "#94a3b8",
          500: "#64748b",  // texto mudo
          600: "#475569",  // texto secundario
          700: "#334155",
          800: "#1e293b",  // texto primario
          900: "#0f172a",  // titulos / texto forte
        },
        // canvas/card — o fundo claro premium e os cards brancos
        surface: { DEFAULT: "#eef2f8", card: "#ffffff", dark: "#1e293b" },
        danger: { DEFAULT: "#e11d48", soft: "#fff1f2" },  // irregular / erro
        warn:   { DEFAULT: "#d97706", soft: "#fffbeb" },  // pendente / atencao
        ok:     { DEFAULT: "#059669", soft: "#ecfdf5" },  // regular / sucesso
      },
      boxShadow: {
        // accent (teal) para hover/destaque
        glow: "0 0 32px -10px rgba(34,153,122,.35)",
        // sombra suave de card no tema claro (sem inset branco)
        card: "0 1px 2px rgba(16,24,40,.04), 0 10px 28px -16px rgba(16,24,40,.18)",
      },
      backgroundImage: {
        "grid-fade": "radial-gradient(ellipse 80% 50% at 50% -20%, rgba(34,153,122,.14), transparent 60%)",
      },
      keyframes: {
        fadeIn: { "0%": { opacity: 0, transform: "translateY(6px)" }, "100%": { opacity: 1, transform: "translateY(0)" } },
      },
      animation: { fadeIn: "fadeIn .25s ease-out both" },
    },
  },
  plugins: [],
};
```

> **Mapa mental das cores:** `surface` (#eef2f8, via gradiente) = canvas claro,
> `surface.card`/`white` = card, `ink-200` = borda, `ink-300` = borda forte/divisor,
> `ink-900/800` = texto principal, `ink-600` = secundario, `ink-400/500` = mudo,
> `brand-500` = accent (fills/CTA), `brand-600/700` = accent em TEXTO/links sobre
> claro, `danger/warn/ok` = so status.

## Passo 3 — CSS base + classes de componente
`src/styles.css` (importe no entrypoint). Define o fundo claro premium com duplo
glow (teal + indigo), foco acessivel, selecao, e as classes reutilizaveis
`.btn* / .card* / .pill* / .input / .label`:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  html, body, #root { height: 100%; }
  body {
    @apply bg-surface text-ink-800 antialiased;
    font-family: 'Inter', system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
    -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale;
    text-rendering: optimizeLegibility;
    /* Fundo claro premium: glow teal (esq) + toque de indigo (dir) sobre base fria. */
    background-image:
      radial-gradient(820px 460px at 12% -8%, rgba(34,153,122,.16), transparent 55%),
      radial-gradient(820px 460px at 88% -4%, rgba(99,102,241,.12), transparent 55%),
      linear-gradient(180deg, #f4f7fc 0%, #e8eef7 100%);
    background-attachment: fixed;
  }
  svg text { text-rendering: geometricPrecision; }       /* texto nitido em graficos/SVG */
  ::selection { background: rgba(34,153,122,.22); color: #0f172a; }
  *:focus-visible { outline: 2px solid #22997a; outline-offset: 2px; border-radius: 6px; }
  ::-webkit-scrollbar { width: 6px; height: 6px; }
  ::-webkit-scrollbar-thumb { @apply bg-ink-300 rounded; }
}

@layer components {
  .btn {
    @apply inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2 font-medium
           transition-all duration-150 disabled:opacity-50 disabled:cursor-not-allowed;
  }
  .btn-primary { @apply btn bg-brand-500 text-white hover:bg-brand-600 shadow-glow; }
  .btn-ghost   { @apply btn bg-white text-ink-700 border border-ink-200 hover:bg-ink-100; }
  .btn-danger  { @apply btn bg-danger text-white hover:opacity-90; }

  /* Card SOLIDO (sem backdrop-blur: blur+filter borra texto no Chrome/Edge). */
  .card       { @apply bg-white border border-ink-200 rounded-xl shadow-card; }
  .card-hover { @apply card transition-all duration-200 hover:border-brand-500/50 hover:shadow-glow hover:-translate-y-0.5; }

  .pill           { @apply inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium; }
  .pill-irregular { @apply pill bg-danger/10 text-danger border border-danger/25; }
  .pill-regular   { @apply pill bg-ok/10 text-ok border border-ok/25; }
  .pill-pendente  { @apply pill bg-warn/10 text-warn border border-warn/25; }
  .pill-fora      { @apply pill bg-ink-100 text-ink-500 border border-ink-200; }

  .input { @apply bg-white border border-ink-200 rounded-lg px-3 py-2 text-ink-900
                  placeholder:text-ink-400 focus:border-brand-500 focus:ring-2 focus:ring-brand-500/15 focus:outline-none; }
  .label { @apply text-xs font-medium text-ink-500 uppercase tracking-wider; }
}
```

Carregue a fonte Inter no `index.html` (`<head>`):
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
```

## Passo 4 — Layout: sidebar + header com breadcrumb
Padrao de app: **sidebar fixa (w-64)** clara com logo+itens de nav (icone lucide +
label, item ativo em teal) e bloco de usuario/logout embaixo; **header (h-14)** com
breadcrumb a esquerda e acoes a direita (versao/seletor de idioma). Conteudo via
`<Outlet/>` rola sozinho.

```tsx
import { Link, NavLink, Outlet, useLocation } from "react-router-dom";
import { LayoutDashboard, ShieldCheck, LogOut, Home } from "lucide-react";
import clsx from "clsx";

const NAV = [{ to: "/dashboard", label: "Dashboard", icon: LayoutDashboard }];

export function Layout() {
  const loc = useLocation();
  const itemCls = ({ isActive }: { isActive: boolean }) =>
    clsx("flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium",
      isActive ? "bg-brand-50 text-brand-700 border border-brand-500/20"
               : "text-ink-600 hover:bg-ink-100 hover:text-ink-900");
  return (
    <div className="min-h-screen flex">
      <aside className="w-64 shrink-0 border-r border-ink-200 bg-white/80 backdrop-blur-md flex flex-col">
        <Link to="/" className="px-5 py-5 flex items-center gap-2 border-b border-ink-200">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-brand-400 to-brand-600 grid place-items-center shadow-glow">
            <ShieldCheck className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="font-bold tracking-tight text-ink-900">MeuApp</div>
            <div className="text-[11px] text-ink-400 -mt-0.5">subtitulo</div>
          </div>
        </Link>
        <nav className="flex-1 px-3 py-4 space-y-1">
          <NavLink to="/" end className={itemCls}><Home className="w-4 h-4" /> Inicio</NavLink>
          {NAV.map(({ to, label, icon: Icon }) => (
            <NavLink key={to} to={to} className={itemCls}><Icon className="w-4 h-4" /> {label}</NavLink>
          ))}
        </nav>
        <div className="p-3 border-t border-ink-200">
          <button className="btn-ghost w-full text-sm"><LogOut className="w-4 h-4" /> Sair</button>
        </div>
      </aside>
      <main className="flex-1 min-w-0 flex flex-col">
        <header className="h-14 px-6 border-b border-ink-200 bg-white/60 backdrop-blur-md flex items-center justify-between">
          <div className="text-sm text-ink-600">
            <span className="text-ink-400">MeuApp</span>
            <span className="mx-2 text-ink-300">/</span>
            <span className="text-ink-900 font-medium capitalize">{loc.pathname.replace("/", "") || "Inicio"}</span>
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
- Fonte do valor **encolhe sozinha** conforme o comprimento (nao corta).
- `delta` colore verde/vermelho (com `deltaIsBad` para inverter quando "subir e ruim").
- Icone vira badge no canto; `tabular-nums` alinha os digitos; entrada com framer-motion.
- Tooltip rico (icone "i") no label — ver skill **rich-tooltips**.

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
        <div className="absolute top-3 right-3 w-7 h-7 rounded-lg grid place-items-center opacity-90"
             style={{ background: color + "1a", color }}><Icon className="w-3.5 h-3.5" /></div>
      )}
      <div className="text-[11px] text-ink-500 uppercase font-semibold leading-tight pr-9 mb-2">{label}</div>
      <div className={`${valueClass} font-bold tabular-nums truncate text-ink-900`}>{value}</div>
      {has && (
        <div className={clsx("mt-2 flex items-center gap-0.5 text-xs font-semibold", dc)}>
          <DI className="w-3.5 h-3.5" /> {Math.abs(delta!).toFixed(1)}%
        </div>
      )}
    </motion.div>
  );
}
```

### ChartCard (moldura padrao de qualquer painel/grafico)
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
          <div className="text-sm font-semibold text-ink-900 flex items-center gap-1.5">
            {title}
            {hint && <span title={hint} className="inline-flex"><Info className="w-3.5 h-3.5 text-ink-400 cursor-help" /></span>}
          </div>
          {subtitle && <div className="text-[11px] text-ink-500 mt-0.5">{subtitle}</div>}
        </div>
        {actions}
      </div>
      {children}
    </motion.div>
  );
}
```

### Status pills
Use as classes prontas para qualquer maquina de estado (mapeie os nomes ao seu dominio):
```tsx
<span className="pill-regular">Regular</span>
<span className="pill-irregular">Irregular</span>
<span className="pill-pendente">Pendente</span>
<span className="pill-fora">Fora de escopo</span>
```

### Tooltip rico
Para ajuda contextual formatada (titulo + lista + chave:valor, via portal, auto-flip),
**use o skill `rich-tooltips`** — e o componente irmao deste design system.

## Passo 6 — Padroes de pagina

### Tela de login/auth split (hero a esquerda + form a direita)
Hero (`hidden lg:flex`) com `bg-grid-fade` + um *blob* `bg-brand-500/15 blur-3xl`, logo,
headline `text-4xl font-extrabold text-ink-900`, bullets com pontinho teal; form
`max-w-md` com inputs que tem **icone lucide a esquerda** (`pl-10`), erro em caixa
`bg-danger/10 border-danger/25`, CTA `btn-primary w-full`.

```tsx
// input com icone (padrao em todo formulario)
<label className="label block mb-1.5">E-mail</label>
<div className="relative">
  <Mail className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-ink-400" />
  <input type="email" className="input w-full pl-10" placeholder="voce@empresa.com" />
</div>

// bloco de erro
{err && (
  <div className="flex items-start gap-2 text-sm text-danger bg-danger/10 border border-danger/25 rounded-lg px-3 py-2">
    <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" /> {err}
  </div>
)}
```

### Modal (overlay escuro + card centralizado, fecha no backdrop)
```tsx
<div className="fixed inset-0 z-50 bg-ink-900/40 backdrop-blur-sm grid place-items-center p-4" onClick={onClose}>
  <div className="card p-6 max-w-sm w-full" onClick={(e) => e.stopPropagation()}>
    <div className="flex items-center justify-between mb-1">
      <h3 className="font-semibold text-ink-900 flex items-center gap-2"><Lock className="w-4 h-4 text-brand-600" /> Titulo</h3>
      <button onClick={onClose} className="text-ink-400 hover:text-ink-700"><X className="w-4 h-4" /></button>
    </div>
    {/* conteudo */}
  </div>
</div>
```

### Seletor de tema claro/escuro (preferencia do usuario no admin/Settings)
O DAP e **claro premium por padrao**, mas suporta **escuro** (mesma identidade: accent
teal, fundo escuro frio). Sempre ofereca a escolha em **dois lugares**: um toggle rapido
no header (icone sol/lua) **e** uma opcao explicita na tela de **Configuracoes/admin**
(o cliente decide e fica salvo). Em stack shadcn (variaveis HSL), o tema vive em `:root`
(claro) e `.dark` (escuro) — veja Passo 2/3; aqui so trocamos a classe no `<html>`.

**1) ThemeContext** — persiste no `localStorage`, alterna a classe `.dark` no
`documentElement`, e expoe `theme` + `toggle` + **`setTheme`** (este ultimo e o que a
tela de Settings usa para escolha explicita):
```tsx
type Theme = "light" | "dark";
const KEY = "app.theme";
// dentro do ThemeProvider:
const [theme, setTheme] = useState<Theme>(() =>
  (localStorage.getItem(KEY) as Theme | null)
  ?? (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light"));
useEffect(() => {
  document.documentElement.classList.toggle("dark", theme === "dark");
  localStorage.setItem(KEY, theme);
}, [theme]);
const value = { theme, toggle: () => setTheme(t => t === "dark" ? "light" : "dark"), setTheme };
```
> **Sem shadcn/variaveis?** O `.dark` no `<html>` ainda funciona: defina os tokens DAP
> claros em `:root` e os escuros em `.dark` (Passo "Sem Tailwind") — o accent teal e o
> mesmo nos dois; muda fundo (claro premium vs escuro frio) e a rampa de cinzas.

**2) Card "Aparencia" no Settings/admin** — duas opcoes selecionaveis (nada de dropdown
escondido), o item ativo com borda/realce teal:
```tsx
const { theme, setTheme } = useTheme();
// ...
<div className="card p-5">
  <div className="text-sm font-semibold text-ink-900 mb-1">Aparencia</div>
  <p className="text-[11px] text-ink-500 mb-3">Escolha o tema. Fica salvo neste navegador.</p>
  <div className="flex flex-wrap gap-3">
    {([
      { v: "light", label: "Claro", desc: "Fundo claro premium (padrao)" },
      { v: "dark",  label: "Escuro", desc: "Fundo escuro, accent teal" },
    ] as const).map(opt => (
      <button key={opt.v} type="button" onClick={() => setTheme(opt.v)}
        className={clsx("flex-1 min-w-[180px] rounded-lg border p-4 text-left transition-colors",
          theme === opt.v ? "border-brand-500 bg-brand-50 ring-2 ring-brand-500/20"
                          : "border-ink-200 hover:border-brand-500/50")}>
        <div className="flex items-center justify-between">
          <span className="font-medium text-ink-900">{opt.label}</span>
          {theme === opt.v && <span className="pill-fora">selecionado</span>}
        </div>
        <p className="mt-1 text-xs text-ink-500">{opt.desc}</p>
      </button>
    ))}
  </div>
</div>
```
> Mantenha **tambem** o toggle do header (descoberta rapida). A opcao no Settings e a
> "fonte da verdade" da preferencia — ambos chamam o mesmo `ThemeContext`.

## Principios de UX (o "jeito DAP")
- **Um accent so (teal).** Cor extra apenas para **status** (vermelho/amarelo/verde).
  Nunca colorir por enfeite — cor carrega significado. Em fundo claro, links/itens
  ativos usam `brand-600/700` (texto) para garantir contraste.
- **Hierarquia por cinza.** Texto principal `ink-900/800`, secundario `ink-600`, mudo
  `ink-400/500`. Titulos de secao em `text-sm font-semibold`; labels em `.label`
  (uppercase, tracking, `ink-500`).
- **Animacoes curtas e discretas:** entrada `opacity+y` 0.35-0.4s (framer-motion),
  `delay` escalonado por indice em listas/grids; hover de card sobe 0.5px + glow.
  Nada de bounce/spring chamativo.
- **Bordas e raios consistentes:** borda `ink-200`, hover `brand-500/50`; raios
  `rounded-lg` (controles) e `rounded-xl` (cards); sombra `card` em repouso, `glow`
  no destaque/hover.
- **Numeros:** sempre `tabular-nums`; valores longos encolhem a fonte (ver KPI) em
  vez de cortar.
- **Estados sempre visiveis:** loading (`Loader2 animate-spin`), erro (caixa
  `danger/10`), vazio, sucesso (`CheckCircle2` verde). Botao desabilitado =
  `opacity-50 cursor-not-allowed` (ja no `.btn`).
- **Acessibilidade:** `focus-visible` com anel teal global; icones com texto ao lado;
  modal/tooltip com `role`; foco do teclado abre tooltips (ver rich-tooltips).
- **Icones:** biblioteca unica (**lucide-react**), tamanho `w-4 h-4` (inline) /
  `w-3.5 h-3.5` (badge).
- **Sem `backdrop-blur` em cards de conteudo** (borra texto no Chrome/Edge). Blur so
  em barras fixas translucidas (sidebar/header).

## Sem Tailwind? (CSS variables — mesmo tema)
Defina os tokens como variaveis e use nas suas classes:
```css
:root{
  --surface:#eef2f8; --card:#ffffff;
  --ink-900:#0f172a; --ink-800:#1e293b; --ink-600:#475569; --ink-400:#94a3b8;
  --ink-200:#e2e8f0; --brand-500:#22997a; --brand-600:#177964; --brand-700:#136251;
  --danger:#e11d48; --warn:#d97706; --ok:#059669;
  --shadow-card:0 1px 2px rgba(16,24,40,.04),0 10px 28px -16px rgba(16,24,40,.18);
  --shadow-glow:0 0 32px -10px rgba(34,153,122,.35);
}
body{ color:var(--ink-800); font-family:Inter,system-ui,sans-serif;
  background-image:radial-gradient(820px 460px at 12% -8%,rgba(34,153,122,.16),transparent 55%),
                   radial-gradient(820px 460px at 88% -4%,rgba(99,102,241,.12),transparent 55%),
                   linear-gradient(180deg,#f4f7fc,#e8eef7); background-attachment:fixed; }
.card{ background:var(--card); border:1px solid var(--ink-200); border-radius:.75rem; box-shadow:var(--shadow-card); }
.btn-primary{ background:var(--brand-500); color:#fff; border-radius:.5rem; padding:.5rem 1rem; box-shadow:var(--shadow-glow); }
```

## Checklist ao aplicar
1. `tailwind.config.js` com `brand`/`ink`/`surface`/`danger`/`warn`/`ok`,
   `boxShadow.glow|card`, fonte Inter, gradiente claro.
2. `styles.css` com base (fundo gradiente claro, focus, selection) + classes
   `.btn*/.card*/.pill*/.input/.label`.
3. Inter carregada no `index.html`.
4. Layout sidebar+header; paginas usando `.card`, `Kpi`, `ChartCard`, pills de status.
5. **Tema claro/escuro**: `ThemeContext` (persiste, alterna `.dark`, expoe `setTheme`),
   toggle no header **e** card "Aparencia" no Settings/admin para o usuario escolher.
6. (Opcional) `rich-tooltips` para ajuda contextual, `multilang` no header,
   `auth-kit` na sidebar.

## Resumo ao terminar
Diga o que foi criado/alterado (config, CSS, componentes), confirme que e o **padrao
de UX claro premium da DAP** (teal `#22997a` + fundo claro frio com glow), que existe a
**escolha de tema claro/escuro** (toggle no header + opcao no Settings/admin) e aponte os
skills irmaos que combinam (rich-tooltips, multilang, auth-kit). Mostre 1 print/rota
de exemplo se subir o app.
