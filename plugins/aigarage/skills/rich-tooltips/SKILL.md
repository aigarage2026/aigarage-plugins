---
name: rich-tooltips
description: >-
  Cria um componente de tooltip rico e bonito no mesmo padrão do AuditAI: balão
  com título destacado, conteúdo formatado (descrição, listas, pares chave:valor),
  posicionado via portal (não é cortado por overflow), com auto-flip, delay e um
  gatilho de ajuda (ícone "?"/info). Use quando o usuário pedir "tooltip",
  "dica/balão de ajuda", "ajuda contextual", "ícone de informação", "tooltip
  bonito/formatado" ou "aplica os tooltips aqui".
---

# rich-tooltips — tooltips ricos, organizados e bonitos (padrão AuditAI)

Substitui o `title=""` nativo (linha única, feio) por um **balão formatado**: título em
destaque + conteúdo estruturado (texto, listas, pares chave:valor), renderizado via
**portal no `body`** (não é cortado por `overflow` de cards), com **auto-flip** de posição,
**delay** anti-flicker e **acessível** (abre no foco/hover).

## Quando usar
Em qualquer rótulo/ícone que precise de explicação: parâmetros, colunas de tabela, KPIs,
campos de formulário, badges. Sempre via componente — **nunca** o `title=` nativo.

## Passo 0 — Detectar o stack
- React + (Tailwind ou CSS)? Tem `lucide-react`/algum set de ícones? Tem `clsx`?
- Se já existir um Tooltip, **estenda/padronize** em vez de duplicar.
- Descubra os **tokens de cor do projeto** (tema claro/escuro, paleta). O exemplo abaixo usa
  os tokens do AuditAI (`ink-*` = navy escuro, `brand-*` = teal). **Adapte** para a paleta do
  projeto (ou use cinzas neutros + uma cor de destaque).

## Componente de referência (React + Tailwind)
Crie `src/components/Tooltip.tsx`. Ajuste as classes de cor ao tema do projeto.

```tsx
import { useEffect, useRef, useState, type ReactNode } from "react";
import { createPortal } from "react-dom";
import clsx from "clsx";

interface Props {
  title?: string;                 // título destacado no topo
  content: ReactNode;             // conteúdo: texto, listas, linhas chave:valor…
  maxWidth?: number;              // largura máx. do balão (px). Default 320 → formato vertical
  placement?: "top" | "bottom" | "right" | "left";  // default "top"
  delay?: number;                 // ms antes de abrir (anti-flicker). Default 250
  children: ReactNode;            // o elemento que dispara o hover/foco
}

export function Tooltip({ title, content, maxWidth = 320, placement = "top",
                          delay = 250, children }: Props) {
  const triggerRef = useRef<HTMLSpanElement>(null);
  const tipRef = useRef<HTMLDivElement>(null);
  const [open, setOpen] = useState(false);
  const [pos, setPos] = useState({ top: 0, left: 0 });
  const timer = useRef<number | null>(null);

  const show = () => { if (timer.current) clearTimeout(timer.current);
                       timer.current = window.setTimeout(() => setOpen(true), delay); };
  const hide = () => { if (timer.current) clearTimeout(timer.current); setOpen(false); };

  useEffect(() => {
    if (!open || !triggerRef.current) return;
    const compute = () => {
      const t = triggerRef.current!.getBoundingClientRect();
      const w = Math.min(maxWidth, window.innerWidth - 16);
      const h = tipRef.current?.offsetHeight ?? 80;
      const gap = 8;
      let place = placement;
      if (place === "top" && t.top - h - gap < 0) place = "bottom";
      if (place === "bottom" && t.bottom + h + gap > window.innerHeight) place = "top";
      let top = place === "top" ? t.top - h - gap
              : place === "bottom" ? t.bottom + gap
              : t.top + t.height / 2 - h / 2;
      let left = (place === "top" || place === "bottom") ? t.left + t.width / 2 - w / 2
               : place === "right" ? t.right + gap : t.left - w - gap;
      left = Math.max(8, Math.min(window.innerWidth - w - 8, left));
      top = Math.max(8, Math.min(window.innerHeight - h - 8, top));
      setPos({ top, left });
    };
    compute();
    window.addEventListener("scroll", compute, true);
    window.addEventListener("resize", compute);
    return () => { window.removeEventListener("scroll", compute, true);
                   window.removeEventListener("resize", compute); };
  }, [open, maxWidth, placement]);

  return (
    <>
      <span ref={triggerRef} onMouseEnter={show} onMouseLeave={hide}
            onFocus={show} onBlur={hide} className="inline-flex">
        {children}
      </span>
      {open && createPortal(
        <div ref={tipRef} role="tooltip"
             style={{ position: "fixed", top: pos.top, left: pos.left, maxWidth, width: "max-content", zIndex: 9999 }}
             className={clsx(
               "rounded-lg shadow-2xl border border-ink-600/80 bg-ink-900/95 backdrop-blur",
               "text-ink-100 px-3.5 py-2.5 text-xs leading-relaxed",
               "animate-in fade-in zoom-in-95 duration-150")}>
          {title && <div className="font-semibold text-sm text-brand-300 mb-1.5">{title}</div>}
          <div className="text-ink-200 space-y-1">{content}</div>
        </div>, document.body)}
    </>
  );
}

/** Gatilho discreto de ajuda (ícone "?"). Use ao lado de um rótulo. */
export function HelpDot({ title, content, placement = "top" }:
  { title?: string; content: ReactNode; placement?: Props["placement"] }) {
  return (
    <Tooltip title={title} content={content} placement={placement}>
      <span className="inline-flex items-center justify-center w-3.5 h-3.5 rounded-full
                       bg-ink-700 text-ink-300 text-[9px] font-bold cursor-help
                       hover:bg-brand-500/30 hover:text-brand-200">?</span>
    </Tooltip>
  );
}
```

> **Sem Tailwind?** Replique o mesmo visual com CSS (caixa arredondada, sombra, fundo
> semitransparente com blur, título em destaque) e `position: fixed` calculado igual.
> **Tema do projeto:** troque `ink-*`/`brand-*` pelas cores do projeto (ou neutros + 1 destaque).

## Padrões de conteúdo (organizado e formatado)
- **Descrição simples:** `content={<p>Texto explicativo.</p>}`
- **Com lista / linhas:** use `<div className="space-y-1">` com `<p>`/itens.
- **Pares chave:valor** (ex.: "Regras afetadas: BV-TETO"): rótulo em cinza + valor destacado.
- **Tipo/faixa** (ex.: campos de formulário): rodapé menor com `border-t` separando.
- Use um **ícone de info** (lucide `Info`) como gatilho quando o rótulo já existe:
  ```tsx
  <Tooltip title="Teto em pacotes" content={<><p>Acima disso → Irregular.</p>
    <p className="text-ink-400">Regras: <span className="font-mono text-brand-300">BV-TETO</span></p></>}>
    <Info className="w-3.5 h-3.5 text-ink-500 hover:text-brand-300 cursor-help" />
  </Tooltip>
  ```

## Regras de qualidade
- **Sempre via portal** (`createPortal` no body) → nunca cortado por `overflow-hidden`/cards.
- **Auto-flip** + clamp nas bordas → nunca sai da tela.
- **Acessível**: abre em `focus` (teclado), não só hover; `role="tooltip"`.
- **Delay** ~250ms para não piscar em mouseover acidental.
- **Não** usar `title=""` nativo para ajuda formatada (deixe `title` só como fallback simples).
- **Conteúdo curto e estruturado**: título + 1–3 linhas. Nada de parágrafos enormes.

## Resumo ao terminar
- Onde está o `Tooltip`/`HelpDot`, exemplos de uso (texto, lista, chave:valor), e a nota de
  que as cores foram adaptadas ao tema do projeto.
