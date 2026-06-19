---
name: test-pack
description: Build a complete POC test pack for the current application — fictitious-but-realistic source files, multi-persona discovery answers, a phase-by-phase walkthrough README, and a validation checklist mapping each feature to a phase. Use whenever the user asks for a test/demo/POC pack, evidence pack, smoke test scenario, or wants to "exercise all features end-to-end" with realistic data.
---

# Test Pack Builder

You are building a **single-shot test pack** that lets a user (or client) exercise an application end-to-end with realistic-looking data. The pack must be self-contained: someone with zero context should be able to follow the README and execute every recent feature.

## Step 1 — Discover what to test

Before writing anything, gather:

1. **Inventory of features.** Read `git log --oneline -50`, `CHANGELOG.md`, `ROADMAP.md`, recent PR titles. Identify the last 1–3 "waves" of work (W1, W2, W3, etc.) or the last N feature commits. Cap at ~15 features per pack — beyond that, split into multiple packs.
2. **Application domain.** Read `README.md`, `package.json`/`pyproject.toml` description, `CLAUDE.md`. What does this app DO? Who uses it?
3. **Existing test packs.** `find . -path '*/tests/poc-*' -name 'README.md'` — if any exist, mirror their tone, file naming, and section order.
4. **Inventory of agents/services that should fire.** If the app has multiple agents, AI workers, or background services, list them. The pack must exercise as many as possible — agents that stay idle after a full walkthrough are a bug or a missing pack feature.
5. **Ask the user briefly** (one short message, ≤4 questions): target sector/scenario, persona names if they care, output language (pt-BR? en?), how many packs (one per scenario or one comprehensive), real binary files vs. textual placeholders.

If features are obvious from git, you can skip the user question and just confirm the scenario.

## Step 2 — Plan the scenario

Pick **one believable real-world story** and lock the details in writing before producing any file:

- Company: name, segment, headcount, revenue, geography
- Legacy stack: 4–6 specific systems (TOTVS, Salesforce, ClearSale, etc.) — names matter
- KPIs table: current value vs. industry benchmark for 5–8 metrics
- 5–10 specific pain points, each tied to a number (R$ X lost/year, N% rate, etc.)
- 1 hard external deadline that creates urgency (audit, regulation, client deadline)

Write down 4–8 personas with: name, role, what they own, **one quirk that affects their answers**. Reuse names across files (Daniel must always be the Diretor Comercial, with the same job, in every document). Lock who reports to whom.

**Plant 3–6 contradictions deliberately.** These are the seeds the conflict/gap/review features will detect. Build a table during planning so you don't lose track:

| Topic | Persona A says | Persona B says | Where it appears |
|---|---|---|---|
| PPM | Ricardo: 1.800 | Excel: 2.300 | discovery-ricardo.md + planilha.xlsx |
| Setup time | Eduardo: 90 min | Carla: 120 min on line B | transcript.txt + discovery-carla.md |

Without this table, you will generate inconsistent contradictions and the pack stops being trustworthy.

## Step 3 — Generate the artifacts

Create one folder under `tests/poc-<short-slug>/` (or `tests/<lang>/<slug>/` if multi-lingual). Inside, produce **all of the following**, in order:

| File | Purpose |
|---|---|
| `01-…md` to `0N-…` | 5–10 source documents the user will upload. **Mix formats**: 1+ transcript (.txt), 1+ procedure (.md), 1 spreadsheet (.xlsx), 1 PDF (regulation/standard), 1 audio placeholder (.mp3.md or note). The files must contradict each other in the points planted in Step 2. |
| `respostas-discovery-<persona>.md` | One per persona that will respond — answers grouped per question. Make the personas disagree on the points planted. |
| `perguntas-chat.md` | 10–15 questions to validate RAG/chat. **Three sections required:** (A) factual — answer in 1 doc, (B) synthetic — needs combining 2+ docs, (C) out-of-scope — model should refuse. |
| `README.md` | Master walkthrough — see Step 4. **Generate this LAST**, after every other file exists, so you can reference real filenames. |

### Source document conventions

Each source doc opens with a **consistent header** that makes it feel corporate and lets the parser extract metadata:

```
# DOC-CODE — Title

**Empresa:** [name]
**Versão:** N.N · revisado em mês/ano
**Responsável:** [persona who owns it]
**Aplicação:** [scope — which sites, products, processes]
```

Then standard sections: Objective, Systems involved, Actors, Flow, KPIs, Pain points, Previous attempts, Annex. This structure helps the extraction agent identify entities consistently across docs.

### Binary file generation

Never ship a fake-but-broken binary. Use one of:

**xlsx via openpyxl** (most consistent with real spreadsheets):
```bash
python3 -c "
import openpyxl
wb = openpyxl.Workbook()
ws = wb.active; ws.title = 'KPI_Mensal'
ws.append(['Mes', 'OEE', 'PPM', 'Aderencia'])
for row in [...data...]: ws.append(row)
wb.save('06-planilha-...xlsx')
"
```

**pdf via reportlab** (good for circulars, regulations, certifications):
```bash
python3 << 'PYEOF'
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
# ... build pages ...
PYEOF
```

**mp3** (rarely worth real audio): create `08-meeting-name.mp3.md` placeholder with the **transcript inside**, marked as "this represents an .mp3 you would upload to Whisper". Whisper-style transcript with timestamps `[00:00]` works great for the extraction agent.

If openpyxl/reportlab aren't installed, install them in a venv before generating: `pip install --user --break-system-packages openpyxl reportlab`.

## Step 4 — Write the README

Required sections, in this order:

1. **Title + one-line scenario.** "Roteiro POC — Diagnóstico X em Y." The first sentence below the title states explicitly what features this exercises (e.g., "Foco do roteiro: exercitar ponta a ponta os 22 agentes que hoje estão ociosos no projeto Z").

2. **Cenário fictício.** Company name, segment, plants/locations, revenue, headcount. KPIs table (current vs. benchmark) with 5–8 rows. Personagens table. Sistemas atuais bullet list. Dores conhecidas (numbered, each one tied to specific numbers planted in the docs).

3. **Contradições plantadas table.** Same one from Step 2. Critical for the user to verify the conflict-detection feature actually catches what was planted.

4. **Roteiro de execução (~N min, M fases)** — numbered phases. Each phase:
   - Pre-requisites in 1 line at the top of the section
   - **🤖 marker** with the specific agent/service the phase exercises (when the app has multiple agents)
   - Step-by-step UI clicks ("Administração → Banco de perguntas → + Novo banco")
   - Exact field values to type
   - "**✅ O que validar**" — specific assertions the user can check, with expected numerical values where possible

5. **Checklist de validação table** — every shipping feature → which phase exercises it → ☐ box. One row per feature so the user can tick them off.

6. **Custo estimado** — if the app makes LLM calls, table per-agent: model tier, expected calls, US$ rough total. Sum at the bottom + BRL conversion if Brazilian.

7. **Anexo** listing every other file in the folder with one-line "what for".

The README ends here. **Do not** include a "Highlights da execução" or "O que ficou pra trás" section in the original README — these are filled in *after* the user executes the pack (see Step 6).

## Step 5 — Hand-off

End your turn with:
- The folder path you created and total size
- A 3-bullet summary of what's covered
- The contradiction count (so the user knows how many conflicts the AI should detect)
- An offer to create additional scenarios for other sectors

Example:
> Test pack pronto em `tests/poc-cvc-antifraude/` (120 KB, 12 arquivos). Coverage: 8 source docs heterogêneos, 3 personas com 6 contradições plantadas, 12 perguntas de chat (4 factuais + 5 sintéticas + 3 fora-de-escopo), 14 fases no roteiro mapeando os 24 agentes. Quer que eu crie outro cenário (saúde / varejo / logística)?

## Step 6 — After execution: post-run review (only if asked)

If the user later runs the pack and wants to capture findings, **append (don't replace)** these sections to the README:

- **Highlights da execução** — what worked well, sample LLM outputs that impressed (cite the actual reasoning text the agent produced)
- **O que ficou pra trás** — agents/features that stayed idle, with one-line explanation per item (missing catalog config, requires manual UI step, depends on SMTP, etc.)
- **Custo real** — actual US$ from the dashboard, vs. the estimate in section 6

These additions document gaps the pack revealed, which is exactly what a test pack is for.

## Hard rules

- **Never invent product features.** Only test what's actually shipping. If you're unsure a feature exists, grep for it before writing the phase. If found in code but no UI exposure, note that in the phase ("via API only — no UI yet").
- **Realism over cleverness.** A boring distributor with believable numbers beats a flashy fictional unicorn. Real-sounding company names, actual industry KPI ranges, plausible legacy stacks.
- **Self-contained.** A new dev should follow the README without asking the author anything. Including how to log in, where to find the URL, how to create the project entity if needed.
- **Write in the project's primary language** (check `README.md` / commit messages — pt-BR if that's the convention). Personas, document content, README, and validation steps all in the same language.
- **Plant contradictions, but keep the math right.** If Eduardo says R$ 480k loss and Carla says 510k, the planilha should show one of them, never a third number. Inconsistencies the AI is *supposed* to find should be discoverable and resolvable; inconsistencies the AI *can't* explain look like sloppy writing.
- **Don't gold-plate.** No CI workflow, no deploy script, no "future ideas" section. The pack is for one walkthrough. Skip versioning, multi-language variants, alternative paths.
- **One persona name per role per pack.** If Eduardo is the Diretor Industrial, do not introduce Eduarda as another director two files later. Cross-document consistency is what makes the pack feel real.
