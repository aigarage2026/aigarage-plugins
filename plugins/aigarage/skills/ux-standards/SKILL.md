---
name: ux-standards
description: >-
  Padroniza a microUX de um projeto web no padrão AuditAI: AUDITA toda a UI em
  busca de tooltips inconsistentes (title= nativo feio vs balão rico), MIGRA os
  de ajuda para o componente rico (Tooltip/InfoTip/TipText), mantém title= nativo
  só onde é truncamento, e impõe regras de "padronização de letras" (capitalização,
  pontuação, voz, paridade de chaves i18n nos 4 idiomas). Inclui checklist de
  auditoria e verificação com tsc. Use quando o usuário pedir "padroniza a UX",
  "padroniza os tooltips", "padronização de letras/texto", "deixa os tooltips
  uniformes", "audita a UI", "microcopy", "tooltip padronizado" ou "aplica o
  ux-standards aqui".
---

# ux-standards — padronização de microUX, tooltips e letras (padrão AuditAI)

Skill **guarda-chuva** para deixar a UI *consistente nos detalhes*: tooltips uniformes,
textos com a mesma capitalização/voz, e nada de `title=` nativo feio onde deveria haver um
balão rico. Não é o sistema visual (cores/layout) — isso é a **[[auditai-ui]]**; nem só o
componente de balão — isso é a **[[rich-tooltips]]**. Esta skill é o **processo de auditar e
padronizar** uma base existente + as **regras de microcopy**.

> Relação com as irmãs:
> - **auditai-ui** = tokens de cor, layout, KPI/ChartCard, princípios de UX visual.
> - **rich-tooltips** = o componente `Tooltip` base (portal, auto-flip, delay, acessível).
> - **ux-standards** (esta) = AUDITAR a UI inteira, MIGRAR title→rico com critério, e as
>   REGRAS DE LETRAS/TEXTO. Se o projeto ainda não tem o componente, rode a rich-tooltips antes.

---

## Passo 0 — Detectar o stack e mapear
- React + Tailwind? Tem `lucide-react` e `clsx`? Tem i18n (`react-i18next`)?
- Já existe um `components/Tooltip.tsx`? Se **não**, crie pela skill **[[rich-tooltips]]** primeiro.
- Rode a varredura inicial (ajuste as extensões/pastas):

```bash
# 1) Todo title= nativo (candidatos a auditar)
grep -rn 'title=' src --include="*.tsx" | grep -vi "contentStyle"
# 2) Onde o Tooltip rico JÁ é usado (para manter o padrão)
grep -rn "Tooltip\|InfoTip\|HelpDot" src --include="*.tsx" | grep -v "components/Tooltip.tsx"
# 3) Anti-padrão a NUNCA deixar: Tooltip envolvendo td/th
grep -rEn '<Tooltip[^>]*>\s*<t[dh]|</t[dh]>\s*</Tooltip>' src --include="*.tsx"
```

---

## Passo 1 — Classificar cada `title=` (a regra central)

Nem todo `title=` deve virar balão rico. Classifique **um por um**:

| Natureza | Como reconhecer | Ação |
|---|---|---|
| **Ajuda / explicação** | chave i18n `_tip`/`_title`/`_help`/`_hint`; frase que ensina sobre um campo, métrica, coluna ou botão | **MIGRAR** → `Tooltip`/`InfoTip` + `TipText` |
| **Truncamento / overflow** | `title={x}` espelhando texto dinâmico que aparece cortado: `title={r.recomendacao}`, `title={m.motivo}`, `title={l.assunto}`, `title={k}` | **MANTER** `title=` nativo (é o uso correto) |
| **Affordance trivial** | botão de fechar `✕`, ícone óbvio | manter nativo (ou migrar só se ficar limpo) |
| **Prop de componente** | `<Modal title=…>`, `<ChartCard title=…>`, `<Tooltip title=…>` — não é atributo HTML | **NÃO TOCAR** |
| **Lib de gráfico** | `<Tooltip>` do Recharts/Chart.js | **NÃO TOCAR** |

> Regra de ouro: **migra-se ajuda; preserva-se truncamento.** Converter um `title` de
> truncamento em balão rico piora a UX em tabelas densas e não agrega — o nativo já mostra
> o texto cortado no hover.

---

## Passo 2 — Padronizar o componente (3 acréscimos ao Tooltip base)

Sobre o `Tooltip` da **[[rich-tooltips]]**, adicione estes três para padronizar o uso:

```tsx
// 1) className opcional no wrapper do gatilho — para não encolher elementos full-width
//    (botões/inputs/selects em grid). Sem isso, o wrapper inline-flex colapsa a largura.
interface Props { /* …título, content, placement, delay… */ className?: string }
// no JSX do gatilho:
<span ref={triggerRef} /* …handlers… */ className={clsx("inline-flex", className)}>
  {children}
</span>

// 2) InfoTip — ícone (i) de ajuda ao lado de um rótulo já existente (caso mais comum)
export function InfoTip({ title, content, placement = "top", className }:
  { title?: string; content: ReactNode; placement?: Props["placement"]; className?: string }) {
  return (
    <Tooltip title={title} content={content} placement={placement}>
      <Info className={clsx("w-3.5 h-3.5 text-ink-400 hover:text-brand-300 cursor-help shrink-0", className)} />
    </Tooltip>
  );
}

// 3) TipText — FORMATA texto livre de forma padronizada: >1 frase (split ".") vira
//    bullets verticais; senão, parágrafo. Use SEMPRE para texto vindo do i18n.
export function TipText({ text }: { text: string }) {
  const partes = text.split(".").map(s => s.trim()).filter(Boolean);
  if (partes.length <= 1) return <p>{text}</p>;
  return <ul className="space-y-1 list-disc pl-4">{partes.map((p, i) => <li key={i}>{p}.</li>)}</ul>;
}
```

Padronize também os **gatilhos** (ChartCard, KPI, FieldGroup) para usarem `InfoTip`/`TipText`
em vez de `title=` nativo — assim o upgrade vale para a tela inteira de uma vez.

---

## Passo 3 — Padrões de migração SEGUROS (sem quebrar HTML/layout)

- **Elemento inline com label/ícone visível** (`<button>`, `<span>`): envolva inteiro
  `<Tooltip content={<TipText text={X} />}>{elemento}</Tooltip>` e remova o `title`.
- **Elemento full-width** (`w-full` em grid: botão/select/input): use `className="w-full"` no
  Tooltip para não encolher: `<Tooltip className="w-full" content={…}>…</Tooltip>`.
- **`<label className="… block …">`**: NÃO envolva (o wrapper inline-flex quebra o bloco).
  Adicione um `InfoTip` **dentro** do label, após o texto:
  `<label …>Texto <InfoTip content={<TipText text={X} />} /></label>`.
- **`<td>` / `<th>` / `<tr>` / `<option>`**: NUNCA envolva a célula. Se for ajuda, envolva só o
  **conteúdo interno**; se for arriscado, deixe nativo.
- **Cabeçalho do balão**: quando houver um rótulo natural (label do campo/coluna), passe
  `title="…"` ao `Tooltip`/`InfoTip` para o balão ter título destacado.
- **Conflito de nome com a lib** (ex.: Recharts também exporta `Tooltip`): importe o seu com
  alias — `import { Tooltip as RichTip, TipText } from "../components/Tooltip";`.
- **Dentro de `.map`**: a `key` vai no elemento mais externo — passe `key` ao `Tooltip`.

---

## Passo 4 — Padronização de LETRAS / microcopy

Regras de texto (valem para tooltips, labels, botões, placeholders):

1. **Frase completa → Sentence case + ponto final.** "Soma do impacto financeiro dos recibos."
2. **Título/rótulo curto (≤3 palavras) → Sentence case, SEM ponto.** "Casos fora do padrão",
   "Forma de pagamento". Títulos de balão e cabeçalhos não levam ponto.
3. **Listas/labels técnicos compactos → como são, sem virar frase.** `Baixo / Médio / Alto`,
   `.xlsx · .tsv · .csv`, `resend = via API · console = só log`. Não force ponto.
4. **Fragmentos concatenados (i18n `_1a`/`_1b`/`_2`) → NÃO normalizar.** Têm espaço nas pontas
   e minúscula no meio de propósito (a frase é montada com um `<bold>`/valor no meio).
   Mexer quebra o espaçamento/sentido. Detecte: chaves numeradas ou que começam/terminam com
   espaço.
5. **Voz consistente:** imperativo curto em ações ("Clique para abrir", "Limpar filtros");
   descritivo em explicações. Uma ideia por tooltip — título + 1–3 linhas, nada de parágrafo.
6. **Termos do produto com a mesma grafia** em todo lugar (Regular/Irregular/Pendente, R$,
   nomes de regras em `font-mono`). Acrônimos preservados (RBAC, PIX, UTC).
7. **Paridade de chaves i18n:** todo idioma tem EXATAMENTE as mesmas chaves. Verifique:

```bash
# paridade de chaves entre locales (ajuste a pasta)
python3 - <<'PY'
import json,glob,os
def flat(o,p=''):
    for k,v in (o.items() if isinstance(o,dict) else []):
        kk=f"{p}.{k}" if p else k
        if isinstance(v,dict): yield from flat(v,kk)
        else: yield kk
locs={os.path.basename(f)[:-5]:set(flat(json.load(open(f)))) for f in glob.glob("src/i18n/locales/*.json")}
base=next(iter(locs)); ref=locs[base]
for l,ks in locs.items():
    print(l,"faltando:",sorted(ref-ks)[:10],"extra:",sorted(ks-ref)[:10])
PY
```

> **Importante:** NÃO faça reescrita em massa de capitalização/pontuação por script. Numa base
> madura a maioria dos "candidatos" (títulos curtos, fragmentos, listas) está **correta de
> propósito** — o script destruiria isso. Audite, reporte, e corrija só o que é claramente
> errado (ex.: uma frase completa começando minúscula). A consistência de **chaves** é o que se
> garante sempre.

---

## Passo 5 — Verificar
- **Type/JSX:** `npx tsc -b` (ou `tsc --noEmit`) deve dar exit 0. Pega aninhamento e imports.
- **Anti-padrão:** rode de novo o grep `<Tooltip>` envolvendo `td/th` → deve ser vazio.
- **`title=` remanescentes:** confirme que só sobraram truncamento, props de componente,
  affordances triviais e Recharts.
- Se houver build (Vite), rode-o; falhas de **permissão** em `node_modules/.vite-temp`
  (dir `root:root`) são ambientais, não do código — o `tsc` já valida o que importa.

---

## Como aplicar em escala (base grande)
Arquivos de página são independentes → dá para **paralelizar**: um subagente por página, todos
com **a MESMA especificação** dos Passos 1 e 3 (migrar ajuda, preservar truncamento, nunca
envolver td/th, usar `className="w-full"` em full-width, alias se conflitar com a lib). Cada
agente roda `tsc -b` ao final e reporta: migrados / mantidos nativos (e por quê) / props
intactas. Depois revise os relatórios e rode o `tsc` global + os greps de sanidade.

## Resumo ao terminar
- Quantos `title=` migrados vs mantidos nativos (e o critério), os acréscimos ao `Tooltip`
  (`className`, `InfoTip`, `TipText`), o resultado do `tsc`, e o veredito da auditoria de texto
  (paridade de chaves + se houve correção de letras ou se já estava padronizado).
