---
name: apresentacao-produto-html
description: Gera uma página HTML única, persuasiva e animada de marketing que apresenta uma solução/produto — narrativa de venda, dores, benefícios, funcionalidades, ROI e as principais telas do sistema (capturas reais ou mockups fiéis em HTML/CSS). Use quando pedirem "apresentação do produto", "html de marketing", "landing de apresentação", "vitrine da solução", "mostrar as telas pro cliente", "pitch em html", "apresentação comercial da solução", ou ao transformar um repositório, proposta, PRD ou documento de escopo em uma apresentação que vende.
---

# Apresentação de Produto em HTML (Marketing)

Você vai transformar uma solução (código, documentação, proposta ou descrição) em **uma única página HTML self-contained** que funciona como apresentação comercial: conta uma história, gera desejo, prova valor e mostra as **telas principais** do produto com animações.

Saída padrão: `apresentacao-<nome-do-produto>.html` na raiz do projeto (ou em `./apresentacao/`), em **português do Brasil**, salvo pedido contrário.

Leia antes de construir:
- `references/narrativa-e-copy.md` — estrutura das seções e regras de copy persuasiva
- `references/telas-e-animacoes.md` — como capturar/recriar telas e o catálogo de animações
- `assets/template-base.html` — esqueleto com design tokens, componentes e motor de animação. **Parta dele**, não do zero.

Scripts de apoio:
- `scripts/capturar_telas.py <url-base> <rota1> <rota2>...` — screenshots via Playwright em `./telas/`
- `scripts/embutir_imagem.py <arquivo>` — imprime o data URI base64 para colar no `<img src>`

---

## Fluxo de trabalho

### 1. Descobrir a solução (não invente nada)
Colete material real antes de escrever qualquer linha de HTML.

**Se houver código no diretório:**
- `README*`, `docs/`, `*.md`, PRD, propostas, `package.json` / `pyproject.toml` (nome, descrição, stack)
- Rotas e páginas: `app/`, `pages/`, `src/routes`, `router.*`, `urls.py`, controllers
- Componentes de tela: `*Page.tsx`, `*Screen.*`, `views/`, `templates/`
- Tema visual: `tailwind.config.*`, `globals.css`, `theme.*`, tokens — **use as cores e fontes reais do produto**
- Modelos de dados / entidades (para usar dados de exemplo realistas nos mockups)
- Logos e imagens em `public/`, `assets/`, `static/`

**Se houver documento (PDF, docx, md, proposta):** leia inteiro e extraia problema, público, solução, módulos, números.

**Se só houver descrição verbal:** faça no máximo 3 perguntas objetivas (público-alvo, principal dor, 3 a 5 telas mais importantes) e siga.

Produza internamente um **briefing** antes de construir:
```
Produto: | Tagline: | Público/ICP: | Dor principal (com custo): |
Promessa central: | 3–5 benefícios (resultado, não feature): |
Funcionalidades-chave: | Telas principais (5–8) e o que cada uma prova: |
Números/provas disponíveis: | Diferenciais (IA, automação, integração...): |
CTA desejado: | Cores/fonte da marca:
```
Se faltar número real, use linguagem qualitativa ou marque como "estimativa" — **nunca fabrique depoimentos, logos de clientes ou métricas como se fossem reais.**

### 2. Definir as telas
Escolha 5 a 8 telas que contam a jornada do usuário (ex.: login/onboarding → dashboard → fluxo principal → resultado da IA → relatório → configurações/integrações). Para cada uma defina: título persuasivo, 1 frase de benefício, 3 hotspots (callouts) apontando o que importa.

Obtenha as telas por ordem de preferência (detalhes em `references/telas-e-animacoes.md`):
1. **Capturas reais** — se o app sobe localmente, use Playwright para tirar screenshots e embuta em base64.
2. **Mockups fiéis em HTML/CSS** — reconstruídos a partir do código dos componentes, com o tema real e dados de exemplo plausíveis.
3. **Mockups conceituais** — quando não há código, desenhe telas coerentes com o briefing, no estilo do produto.

### 3. Escrever a narrativa
Siga a estrutura de seções de `references/narrativa-e-copy.md` (Hero → Dor → Virada → Solução → Telas → Como funciona → Benefícios/ROI → Diferenciais → Segurança/Confiança → Implantação → CTA). Escreva toda a copy **antes** de montar o HTML.

### 4. Construir o HTML
- Copie `assets/template-base.html` e preencha. Arquivo **único**: CSS e JS inline; externo só Google Fonts e, se necessário, CDN (cdnjs/jsdelivr).
- Substitua os tokens `--brand*` pelas cores reais do produto.
- Cada tela vai dentro do componente `.device` (moldura de navegador ou celular) com hotspots.
- Inclua a galeria de telas com abas + autoplay e a seção "tour" com scroll.
- Navegação fixa com âncoras, barra de progresso de leitura, modo apresentação (setas ← → avançam seção a seção; tecla `F` = tela cheia).

### 5. Verificar (obrigatório)
- Abra o arquivo com Playwright (se disponível) em 1440px e 390px, tire screenshots e **olhe** para elas; corrija sobreposição, texto cortado, contraste, rolagem horizontal.
- Console sem erros.
- Checklist final:
  - [ ] Nenhum lorem ipsum, "TODO" ou placeholder visível
  - [ ] Toda tela tem título, benefício e hotspots
  - [ ] Copy fala de resultado para o cliente, não de tecnologia
  - [ ] Nenhuma métrica/depoimento inventado apresentado como real
  - [ ] Funciona offline (exceto fontes), responsivo, sem scroll horizontal
  - [ ] `prefers-reduced-motion` respeitado
  - [ ] Tamanho < 15 MB (comprima screenshots: JPEG/WebP, largura ≤ 1600px)

### 6. Entregar
Informe o caminho do arquivo, as telas incluídas, e liste em 2–3 linhas o que foi estimado/conceitual e precisa de validação do usuário.

---

## Opções que o usuário pode pedir
- **"blindar o como"**: mostre capacidades e resultados, oculte algoritmos, prompts, arquitetura interna, nomes de modelos e esquemas de banco. Fluxos internos viram "caixas mágicas" com nome de benefício.
- **"tema claro/escuro"**: o template já suporta os dois; padrão é escuro premium.
- **"versão para enviar por e-mail"**: reduza animações pesadas e garanta que tudo seja legível sem JS.
- **"com preço"**: adicione seção de planos/investimento antes do CTA.
- **idioma**: troque `lang` e toda a copy.
