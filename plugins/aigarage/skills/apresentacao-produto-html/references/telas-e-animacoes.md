# Telas e Animações

## Parte 1 — Obtendo as telas

### Opção A: capturas reais (padrão)
Use `scripts/capturar_sistema.py` com um roteiro JSON (ver `roteiro-captura.exemplo.json` e o passo 2 do SKILL.md). Ele faz login com credencial vinda de variável de ambiente, navega e clica até cada tela, aplica a máscara, fotografa (tela inteira ou recorte), baixa os relatórios que o sistema gera e converte as páginas do PDF em imagem.

Dicas que evitam retrabalho:
- Modal de boas-vindas ou tour cobrindo a tela: grave a flag de "visto" pelo campo `tema`.
- Botão com texto repetido na página (ex.: "Relatórios" na aba e na sub-aba): use `button:has-text('Relatórios') >> nth=-1` ou um seletor mais específico.
- Telas que carregam dados devagar: `esperar_seletor` no elemento que só existe depois do carregamento, não `esperar` fixo longo.
- Revise cada captura. Dado sensível que escapou: acrescente à máscara (`regex`, `seletores`, `ocultar`) e rode de novo, em vez de editar a imagem à mão.
- `select` genérico costuma pegar o seletor de idioma do cabeçalho. Ancore pelo conteúdo: `select:has(option:has-text('exec'))`.
- Relatório que abre em janela (modal) cobre os botões da tela: comece o passo seguinte com `{"clicar": "button[aria-label='Fechar']", "opcional": true}`.
- Painel lateral que não fecha com Escape: clique no botão de fechar dele, não na tecla.
- Tela que falha não derruba as outras: o script grava `_falhou-<nome>.png` e segue. Olhe esse print para ajustar o seletor.
- Login que não passa: o script grava `_login-falhou.png`. Credencial colada com o prefixo repetido (`APP_USER=APP_USER=...`) é corrigida sozinha.
- Código técnico com formato fora do padrão escapa da máscara (ex.: com hífen). Leia as capturas procurando isso e acrescente o padrão.
- Print de tela inteira fica pequeno dentro da moldura. Na montagem, recorte a área que importa (sem menu lateral e cabeçalho, ou só a janela do relatório) e use a proporção do recorte na moldura (`style="aspect-ratio:L/A"` no `.device__screen`); recalcule os hotspots para o recorte.
- Captura longa: rode em segundo plano gravando um log, e confira o log no fim.
- Letra pequena nos relatórios: recorte justo nas colunas que importam (só a tabela, não a janela inteira). Menos área de origem por pixel = texto maior na moldura.
- Nada cortado: dê a cada `.device__screen` a proporção exata da imagem (`aspect-ratio:L/A`) e `object-fit:contain`; nunca proporção fixa com `cover`.

### Modo apresentação: uma seção por tela
Quem apresenta usa tela cheia, então cada seção precisa caber em `100vh`:
- `section{min-height:100vh;display:flex;align-items:center}` e títulos/leads com `clamp()` ligado à altura (`vh`).
- Seção longa (cartões + passos, galeria + lista, páginas + descrições, cartões + FAQ) vira duas seções.
- Limite a moldura pela altura: `.device{max-width:calc((100vh - <altura do resto>px) * var(--ar))}` com `--ar` = proporção da imagem; imagem vertical ganha limite próprio.
- Meça antes de entregar, em 1920×1080 e 1440×900: nenhuma `section` mais alta que `innerHeight`, clicando em todas as abas da galeria.

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
