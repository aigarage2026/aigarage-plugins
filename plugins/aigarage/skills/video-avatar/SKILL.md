---
name: video-avatar
description: Produz vídeos com avatar falante a partir do código, do changelog ou de um documento do repositório, usando o MCP do HeyGen. Use sempre que o usuário pedir vídeo, videozinho, demo em vídeo, release note em vídeo, changelog narrado, onboarding, tutorial, explicativo, treinamento, vídeo para cliente, vídeo para o LinkedIn, reels, avatar, digital twin, ou disser "grava isso", "manda em vídeo", "faz um vídeo disso". Use também quando o usuário quiser clonar voz, criar ou trocar avatar, traduzir ou dublar um vídeo existente, ou conferir saldo de créditos do HeyGen. Na dúvida entre responder em texto e produzir vídeo, consulte esta skill primeiro — ela contém os IDs, o tom de voz e o controle de custo da consultoria, e produzir vídeo sem ela gera saída fora do padrão e queima créditos à toa.
---

# Produção de vídeo com avatar

Esta skill transforma o que já existe no repositório (commits, CHANGELOG, PRs, docs, propostas) em vídeo com avatar, sem sair do Claude Code e sem passar por editor nenhum.

O ganho não é gerar vídeo. É gerar vídeo **consistente**: mesmo avatar, mesma voz, mesmo tom, mesma pronúncia dos termos de produto, toda vez, sem o usuário precisar decidir nada disso.

## Antes de qualquer coisa

O MCP do HeyGen precisa estar conectado. Verifique chamando `get_current_user`.

Se não estiver, pare e instrua:

```bash
claude mcp add --transport http heygen https://mcp.heygen.com/mcp/v1/
```

Depois `/mcp` para autenticar via OAuth. Não há chave de API neste fluxo e nenhuma credencial deve ser escrita em arquivo.

---

## DEFAULTS

Estes são os valores padrão da consultoria. **Nunca invente um ID.** Se algum estiver como `PREENCHER`, chame a tool correspondente, mostre as opções ao usuário e peça para escolher — depois atualize este bloco.

**Este bloco se preenche por instalação e nunca é versionado.** A cópia publicada no
marketplace fica em `PREENCHER` permanentemente, de propósito: os IDs pertencem à conta
HeyGen de quem instalou, e nome de brand kit costuma carregar nome de cliente — este
repositório é público. Preencha em `~/.claude/skills/video-avatar/SKILL.md`, na máquina,
e não mande o bloco preenchido de volta para cá: nem inteiro, nem "só o `avatar_id`",
nem como exemplo dentro de outra alteração. Quem for editar a skill aqui mexe no texto e
deixa o bloco intacto.

```yaml
avatar_id:        PREENCHER    # de list_avatar_looks (o look id, não o group id)
avatar_tipo:      PREENCHER    # photo | digital_twin
engine:           PREENCHER    # avatar_v se suportado, senão avatar_iv
voice_id:         PREENCHER    # de list_voices, pt-BR
brand_kit_id:     PREENCHER    # de list_brand_kits (pode ser vazio)
brand_glossary_id: PREENCHER   # de list_brand_glossaries
inventario:       ~/.claude/skills/video-avatar/inventario.md
registro:         videos/registro.md
```

O inventário mora junto da skill, e não em `docs/` do projeto, porque lista IDs da sua
conta HeyGen e brand kits com nome de cliente — dado que não pertence ao repositório de
cliente nenhum.

Antes de usar `avatar_id`, confira em `get_avatar_look` se ele suporta o engine escolhido. Um look treinado só para Avatar III falha silenciosamente com qualidade pior se você forçar outro engine.

Se `avatar_tipo` for `photo`, avise o usuário uma vez por sessão: avatar de foto tem qualidade visivelmente inferior a digital twin, e refazer como digital twin (2 minutos de vídeo contínuo) é a maior melhoria disponível por menos esforço.

---

## Perfis de saída

Escolha o perfil pelo pedido do usuário. Se ambíguo, pergunte — é uma pergunta só e evita retrabalho caro.

| Perfil | Duração alvo | Formato | Uso |
|---|---|---|---|
| `release-note` | 60–90s | 16:9 | O que mudou na versão e por que importa |
| `onboarding` | 2–4 min | 16:9 | Como usar uma funcionalidade, passo a passo |
| `social` | 30–45s | 9:16 | LinkedIn, Reels, Shorts |
| `demo-cliente` | 3–5 min | 16:9 | Apresentação de solução, com brand kit do cliente |

Duração alvo é alvo, não teto rígido. Mas passar muito dela custa créditos proporcionalmente, então corte o roteiro em vez de aceitar o excesso.

Para `demo-cliente`, o `brand_kit_id` é o do cliente, não o nosso. Se não existir, ofereça criar com `create_brand_kit` a partir do site do cliente — ele importa cores, logos e fontes automaticamente. Confirme com o usuário que temos direito de uso desses ativos antes de chamar.

---

## Perímetro

Esta skill produz vídeo **sobre** o projeto. Ela não modifica o projeto.

Ao executar esta skill, não edite código, configuração, dependência, schema ou infraestrutura, seja qual for o repositório. As únicas escritas permitidas são `videos/registro.md` e `docs/heygen-inventario.md`. Se o pedido envolver alterar a aplicação, saia da skill e trate como tarefa normal de desenvolvimento.

**Revisão de conteúdo antes de enviar.** O roteiro sai da nossa infraestrutura no momento em que vai para o HeyGen. Antes de gerar, verifique se ele contém algum destes:

- nome de cliente ou de projeto sob acordo de confidencialidade
- credencial, token, chave ou string de conexão
- URL, endpoint ou host interno
- dado de usuário real (nome, e-mail, CPF, valor de contrato)
- funcionalidade ainda não anunciada publicamente

Se contiver, mostre o trecho ao usuário e pergunte antes de gerar. Não decida sozinho que é inofensivo: numa consultoria, o que parece detalhe técnico costuma ser informação de cliente.

Isso vale especialmente quando a fonte é `git log` ou `git diff`, onde mensagem de commit frequentemente carrega nome de cliente e caminho interno sem ninguém perceber.

**Chatbots e agentes da aplicação não são assunto desta skill.** Se o pedido for dar rosto, voz ou presença visual a um chatbot ou assistente do produto, isso é avatar em tempo real (LiveAvatar): plataforma separada, plano separado, créditos separados, e os avatares não são intercompatíveis com os do HeyGen. Diga isso e pare, em vez de tentar adaptar o fluxo de vídeo gravado.

---

## Fluxo obrigatório

Siga nesta ordem. O passo (b) existe porque gerar vídeo custa dinheiro e é irreversível: uma vez renderizado, o crédito foi.

### a) Ler o contexto real

Nunca escreva o roteiro a partir do que você imagina que o produto faz. Leia a fonte:

- `git log --oneline -n 20` e `git diff` para release note
- `CHANGELOG.md` se existir
- O arquivo, PR ou documento que o usuário apontar
- Para `demo-cliente`, a proposta ou o documento de escopo

Se a fonte estiver pobre demais para render um roteiro honesto, diga isso em vez de preencher com genérico.

### b) Escrever o roteiro e mostrar para aprovação

Mostre o roteiro no chat, em texto puro, com a contagem estimada de duração (cerca de 150 palavras por minuto em português falado).

**Espere aprovação explícita. Não gere vídeo no mesmo turno em que escreveu o roteiro.**

Se o usuário pedir ajustes, ajuste e mostre de novo. Iterar em texto é grátis; iterar em vídeo não é.

### c) Estimar custo e avisar

Calcule os créditos estimados pela duração e pelo engine (ver seção Custo). Informe antes de gerar.

Se a estimativa passar de **40 créditos**, peça confirmação explícita, mesmo que o usuário já tenha aprovado o roteiro.

Se `get_current_user` mostrar saldo insuficiente para a estimativa, pare e avise. Não tente gerar torcendo para dar certo.

### d) Gerar

Chame `create_video` com os DEFAULTS, o perfil escolhido e o `brand_glossary_id`.

Prefira passar o roteiro como script. Use áudio pronto com `create_lipsync` apenas quando o usuário quiser voz de outra fonte (ex.: ElevenLabs) ou quando a voz do HeyGen estiver errando prosódia de forma que o glossário não resolve.

Para lote (vários vídeos de uma vez, um por cliente ou por idioma), use `create_video_batch` em vez de chamar `create_video` em loop.

### e) Acompanhar e entregar

Faça polling com `get_video`. Espace as chamadas: 10 segundos nas primeiras, depois 30 segundos. Não fique chamando em rajada.

Entregue a `video_url` ao usuário. Não descreva o vídeo, não resuma o que ele contém — o usuário vai assistir.

### f) Registrar

Anexe uma linha em `videos/registro.md`:

```
| data | perfil | título | video_id | duração | créditos gastos | fonte |
```

O campo "créditos gastos" é o valor **real**, medido por `get_current_user` antes e depois. Esse registro é o que permite calibrar a estimativa com o tempo e é o que sustenta a precificação para cliente.

---

## Roteiro em português falado

O erro mais comum é escrever texto de blog e mandar o avatar ler. Fica robótico e denuncia a origem.

**Regras:**

- Frases curtas. Se uma frase tem duas vírgulas, quebre em duas.
- Abra pelo problema que a mudança resolve, não pelo nome da mudança.
- Sem "neste vídeo vamos ver", "espero que tenham gostado", "sem mais delongas".
- Sem jargão de release note lido em voz alta: "refatoramos o módulo de persistência" vira "o sistema agora salva mais rápido".
- Versões se falam por extenso e agrupadas: "versão dois ponto três", nunca "v-dois-ponto-três-ponto-zero".
- Números grandes por extenso: "cerca de doze mil", não "12.437".
- Siglas que o usuário fala no dia a dia ficam como sigla; o resto se explica na primeira menção.
- Terminar com uma ação concreta, não com despedida.

**Exemplo 1 — release-note**

Fonte: `feat(auth): implement JWT-based authentication with refresh token rotation`

Ruim: "Nesta versão implementamos autenticação baseada em JWT com rotação de refresh tokens."

Bom: "Antes, quem ficava muito tempo logado era desconectado do nada. Isso acabou. A sessão agora se renova sozinha em segundo plano, e continua segura. Você não precisa fazer nada, já está no ar."

**Exemplo 2 — social**

Ruim: "Hoje vamos falar sobre eficiência operacional."

Bom: "Sua equipe passa seis horas por semana copiando dado de um sistema para outro. Ninguém mediu isso, mas todo mundo sente. Foi o que a gente foi atrás de descobrir."

---

## Glossário de pronúncia

O TTS erra nomes próprios, siglas e estrangeirismos. O `brand_glossary_id` corrige isso na fala sem alterar a legenda.

Termos mapeados hoje:

```
# termo → pronúncia
PREENCHER
```

Quando o usuário reclamar de uma pronúncia, adicione aqui **e** atualize o glossário com `update_brand_glossary`. Atenção: `update_brand_glossary` substitui a lista inteira de termos — leia o glossário atual, acrescente o termo novo, e mande a lista completa de volta. Mandar só o termo novo apaga todos os outros.

---

## Custo

Créditos são a moeda única do HeyGen e o consumo varia por modelo e duração.

**Estimativa de trabalho** (calibrar com dados reais de `videos/registro.md` assim que houver três ou mais registros):

- Avatar IV/V: ~20 créditos por minuto
- Avatar III: ~3 créditos por minuto
- Tradução com lip-sync: ~5–10 créditos por minuto

Esses números vêm de fontes de terceiros, não da documentação oficial, e o HeyGen já alterou taxas sem aviso. **Meça sempre.** Na primeira geração de cada sessão, chame `get_current_user` antes e depois e registre a diferença real.

Regras de contenção:

- Nunca regenerar o vídeo inteiro para testar um ajuste de tom. Gere 15 segundos do trecho em questão, aprove, aí renderize o todo.
- Nunca gerar duas variações "para comparar" sem o usuário pedir.
- Avatar III é suficiente para rascunho interno e custa uma fração. Reserve Avatar V para o que sai para cliente.

---

## Erros comuns e o que fazer

| Sintoma | Causa provável | Ação |
|---|---|---|
| Vídeo com cara de boneco | `avatar_tipo: photo` | Propor digital twin |
| Boca dessincronizada em "p" e "b" | Fala rápida demais | Encurtar frases, reduzir velocidade |
| Nome de produto falado errado | Glossário sem o termo | Adicionar e atualizar |
| `create_video` retorna erro de consentimento | Avatar privado sem consentimento | `create_avatar_consent`, mandar o link ao dono do rosto; expira em 24h |
| Geração travada em processing | Fila normal | Aguardar; só reportar falha depois de 10 min |
| Saldo sumiu rápido | Engine premium em rascunho | Conferir `videos/registro.md` e migrar rascunhos para Avatar III |

---

## Limites desta skill

Esta skill cuida de **vídeo gravado**, em qualquer repositório, sem alterar nenhum deles. Ver a seção Perímetro.

Fora do escopo: avatar em tempo real em chatbot (LiveAvatar), edição de vídeo filmado com câmera, legendagem de material de terceiros, e qualquer coisa que exija mexer no código da aplicação.
