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
- `references/humanizer-ptbr.md` — **obrigatório**: como tirar da copy os sinais de texto escrito por IA
- `assets/template-base.html` — esqueleto com design tokens, componentes e motor de animação. **Parta dele**, não do zero.

Scripts de apoio:
- `scripts/capturar_sistema.py roteiro.json --saida telas` — **padrão**: abre o sistema, faz login, navega, clica, mascara o que não pode aparecer, fotografa telas e relatórios e baixa documentos gerados (PDF vira imagem de página). Roteiro de exemplo em `references/roteiro-captura.exemplo.json`
- `scripts/capturar_telas.py <url-base> <rota1> <rota2>...` — versão mínima, só rotas públicas sem login
- `scripts/embutir_imagem.py <arquivo>` — imprime o data URI base64 para colar no `<img src>`
- `scripts/checar_copy.py <arquivo>.html` — acha travessão, emoji, fórmulas e vocabulário de IA no texto visível; sai com erro se encontrar

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

**Padrão: abrir o sistema e fotografar como ele é.** A apresentação mostra o produto real, telas e relatórios, e não uma reconstrução. Mockup só entra quando o sistema não pode ser aberto, e então a entrega diz isso.

1. **Suba o sistema** (ou use um ambiente de homologação/dev que já esteja no ar). Prefira ambiente com dados de demonstração ou já anonimizados.
2. **Credencial fora do roteiro.** Use o usuário de seed do projeto quando existir. Para ambiente remoto, peça ao usuário que crie um arquivo só dele (`install -m 600 /dev/null ~/.config/<app>-captura.env` com `APP_USER=` e `APP_PASS=`) e carregue com `set -a; . arquivo; set +a` na mesma linha do comando. Nunca peça a senha no chat e nunca grave a senha no roteiro: o roteiro usa `${APP_USER}` e `${APP_PASS}`.
3. **Escreva o roteiro** (`roteiro.json`, ver `references/roteiro-captura.exemplo.json`): login, uma entrada por tela com os cliques que levam até ela, e um passo `baixar` para cada relatório que o sistema gera. Inclua as telas de relatório **e** os documentos gerados (PDF, planilha exportada como PDF): relatório é o que o gestor compra.
4. **Máscara antes do print.** Em `mascarar`, liste o que não pode aparecer: dado pessoal e de cliente (nomes, documentos, nomes de arquivo enviados) e, quando o pedido for "blindar o como", termos do método (códigos técnicos, nomes de tabelas, nomes de regras). Monte a lista a partir do próprio código ou catálogo do produto, não de memória. `ocultar` remove o código técnico e mantém o nome de negócio ao lado.
5. **Rode** `python scripts/capturar_sistema.py roteiro.json --saida telas`. Modais de boas-vindas e tours: desligue pelo campo `tema` (script que roda antes de cada página, ex.: gravar a flag de "tour concluído" no localStorage).
6. **Olhe cada imagem.** A máscara cobre o que o roteiro manda cobrir, e só isso. Achou vazamento (nome de cliente, sigla do sistema, código técnico), acrescente à máscara e rode de novo. Não embuta imagem que você não abriu.
7. **Embuta** as imagens (`<img src="data:image/jpeg;base64,...">`) dentro do `.device__screen`, com os hotspots apontando para o que importa na tela real. Documento gerado entra como página (moldura de documento, não de navegador). Comprima: JPEG q82, largura até 1600px (o script já faz).

Se o sistema não puder ser aberto: mockup fiel em HTML/CSS reconstruído dos componentes (tema real, dados plausíveis), e a entrega avisa que as telas são reconstruções.

### 3. Escrever a narrativa
Siga a estrutura de seções de `references/narrativa-e-copy.md` (Hero → Dor → Virada → Solução → Telas → Como funciona → Benefícios/ROI → Diferenciais → Segurança/Confiança → Implantação → CTA). Escreva toda a copy **antes** de montar o HTML.

### 3b. Humanizar a copy (obrigatório, antes do HTML)
A apresentação vende pela credibilidade, e texto com cara de IA faz o leitor desconfiar do número ao lado. Passe **toda** a copy pela skill `humanizer` em modo embutido, se ela estiver instalada; sem ela, siga `references/humanizer-ptbr.md`, que traz as mesmas regras adaptadas para português e para página de venda. O mínimo: nenhum travessão, nenhum "não é X, é Y" ou "X, não Y" de efeito, nenhuma série de frases de impacto, nenhum trio forçado, nenhum emoji decorativo, nenhum fato que não veio do material. Copy nova ou alterada depois desta etapa volta para ela.

### 4. Construir o HTML
- Copie `assets/template-base.html` e preencha. Arquivo **único**: CSS e JS inline; externo só Google Fonts e, se necessário, CDN (cdnjs/jsdelivr).
- Substitua os tokens `--brand*` pelas cores reais do produto.
- Cada tela vai dentro do componente `.device` (moldura de navegador ou celular) com hotspots.
- Inclua a galeria de telas com abas + autoplay e a seção "tour" com scroll.
- Navegação fixa com âncoras, barra de progresso de leitura, modo apresentação (setas ← → avançam seção a seção; tecla `F` = tela cheia).

### 5. Verificar (obrigatório)
- Abra o arquivo com Playwright (se disponível) em 1440px e 390px, tire screenshots e **olhe** para elas; corrija sobreposição, texto cortado, contraste, rolagem horizontal.
- Console sem erros.
- Rode `python scripts/checar_copy.py <arquivo>.html` e corrija até sair sem sinais; depois leia o texto procurando o que o script não pega (trio forçado, frases de efeito em sequência, mesma construção repetida).
- Checklist final:
  - [ ] Nenhum lorem ipsum, "TODO" ou placeholder visível
  - [ ] Toda tela tem título, benefício e hotspots
  - [ ] Telas e relatórios são capturas do sistema real (ou a entrega diz que são reconstruções) e cada imagem foi aberta e conferida contra vazamento
  - [ ] Copy fala de resultado para o cliente, não de tecnologia
  - [ ] Copy humanizada: `checar_copy.py` sem sinais e leitura humana feita
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
