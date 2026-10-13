# Telas e Animações

## Parte 1 — Obtendo as telas

### Opção A: capturas reais (preferida)
Se o projeto tem app web que sobe localmente:

1. Descubra o comando (`package.json` → `dev`/`start`; `manage.py runserver`; `docker compose up`).
2. Suba em background e espere a porta responder.
3. Se exigir login, use usuário de **seed/fixture** do próprio projeto (nunca credenciais reais do usuário). Se não houver, peça ao usuário ou vá para a Opção B.
4. Capture com Playwright:

```python
# scripts/capturar_telas.py  — uso: python capturar_telas.py http://localhost:3000 /dashboard /pedidos /relatorios
import sys, base64, asyncio
from playwright.async_api import async_playwright

async def main(base, rotas):
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
        for r in rotas:
            await pg.goto(base + r, wait_until="networkidle")
            await pg.wait_for_timeout(800)
            nome = r.strip("/").replace("/", "_") or "home"
            await pg.screenshot(path=f"telas/{nome}.jpg", type="jpeg", quality=82)
            print("ok", nome)
        await b.close()

asyncio.run(main(sys.argv[1], sys.argv[2:]))
```

5. Embuta como `data:image/jpeg;base64,...` dentro de `<img>` no `.device__screen`. Largura ≤ 1600px, qualidade ~80.
6. **Revise cada captura**: remova dados sensíveis (nomes, CPFs, e-mails reais) — se houver, troque por mockup (Opção B) ou desfoque com CSS `filter: blur()` sobre a região.

### Opção B: mockups fiéis em HTML/CSS
Quando não dá para subir o app, reconstrua a tela lendo os componentes:
- Mesma estrutura (sidebar, header, cards, tabela, gráfico), mesmas cores e fontes do tema.
- Dados de exemplo **plausíveis e coerentes** com o domínio (nomes fictícios, valores em R$, datas recentes).
- Gráficos em SVG inline simples (barras/linhas), sem bibliotecas.
- Use as classes utilitárias do template: `.ui-sidebar`, `.ui-top`, `.ui-kpi`, `.ui-table`, `.ui-chart`, `.ui-chip`, `.ui-ai` (bolha de resposta da IA).
- Escala: projete a tela a 1280×800 e deixe o `.device` escalar via CSS.

### Opção C: mockups conceituais
Sem código nem app: desenhe as telas a partir do briefing. Avise na entrega que são conceituais.

### Telas que costumam vender melhor
1. **Dashboard / visão geral** — prova controle ("tudo num lugar")
2. **Fluxo principal** (cadastro, pedido, atendimento) — prova facilidade
3. **Momento IA** (sugestão, classificação, resposta, extração) — prova inteligência; anime a resposta "digitando"
4. **Automação / workflow** — prova economia de tempo
5. **Relatório / análise** — prova resultado para o gestor
6. **Mobile** (se existir) — prova mobilidade
7. **Integrações / configurações** — prova que encaixa no que o cliente já usa

### Hotspots
Cada tela tem 2–4 hotspots: ponto pulsante posicionado em `%` (`style="--x:62%;--y:30%"`) + balão com microcopy. Aparecem em sequência quando a tela entra em foco.

---

## Parte 2 — Catálogo de animações (já no template)

| Atributo / classe | Efeito | Onde usar |
|---|---|---|
| `data-reveal` | fade + sobe ao entrar na viewport | qualquer bloco |
| `data-reveal="left"` / `"right"` / `"zoom"` | variações de entrada | colunas, mockups |
| `data-delay="200"` | atraso em ms | escalonar cartões |
| `data-count="87" data-suffix="%"` | contador animado | ROI / números |
| `data-parallax="0.15"` | parallax suave no scroll | mockup do hero |
| `data-tilt` | inclinação 3D seguindo o mouse | device do hero |
| `.typing` + `data-text` | texto digitando | resposta da IA |
| `.gallery` | abas + autoplay + barra de progresso | seção Telas |
| `.tour` | scroll sticky com troca de tela por etapa | seção Tour |
| `.steps` | linha de progresso que preenche | Como funciona |
| `.marquee` | faixa rolando infinitamente | chips de capacidades/integrações |
| `.glow` | gradiente animado de fundo | hero e CTA |

### Regras de movimento
- Durações 400–900ms, `cubic-bezier(.2,.7,.2,1)`. Nada piscando.
- No máximo 1 animação contínua por viewport (glow **ou** marquee **ou** autoplay).
- `@media (prefers-reduced-motion: reduce)` desliga tudo — já implementado.
- Animações nunca escondem conteúdo sem JS: o template adiciona `.js` no `<html>` e só então aplica os estados iniciais ocultos.

### Modo apresentação
- `←` / `→` ou `PageUp`/`PageDown`: seção anterior/próxima
- `F`: tela cheia
- Ponto de navegação lateral mostra a seção atual
