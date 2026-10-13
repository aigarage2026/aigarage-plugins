# Humanizar a copy (obrigatório)

A apresentação vende pela credibilidade. Texto com cara de IA faz o leitor desconfiar do
número que está ao lado, então **toda a copy passa por esta etapa antes de entrar no HTML**.

Se a skill `humanizer` estiver instalada (`/humanizer` ou `anthropic-skills:humanizer`),
use-a em modo embutido sobre a copy. Sem ela, siga este guia, que é a adaptação para
português e para página de venda das mesmas regras (base: Wikipedia, "Signs of AI writing").

## Processo

1. Escreva a copy inteira (passo 3 do SKILL.md).
2. Faça duas perguntas sobre o texto e responda por escrito, para você:
   - **"O que faz este texto parecer escrito por IA?"**
   - **"Algum número, nome, prazo, cliente ou citação aqui não veio do material real?"**
     Fato inventado é defeito, mesmo quando soa mais humano que a versão vaga.
3. Reescreva até as duas respostas ficarem vazias.
4. Depois de montar o HTML, rode `python scripts/checar_copy.py <arquivo>.html`. Ele acha o
   que é mecânico (travessão, emoji, fórmulas, vocabulário). Saída com sinal = não entregue.

## Sinais a eliminar

**Travessão (— e –).** Proibido na copy. Troque por ponto, vírgula, dois-pontos ou parênteses.
Também vale para ` -- `. Inclui o `<title>`.

**Paralelismo negativo.** "Não é X, é Y", "não só X, mas Y", "X, não Y" como frase de efeito.
- Antes: "Saiba quem fez, não só quem pode."
- Depois: "Descubra quem fez o que não devia no seu SAP."

**Frase de efeito em série e staccato.** Cada bloco terminando em frase de impacto, ou várias
frases curtas seguidas para criar drama ("O mesmo sistema. Outro resultado."). Uma frase curta
para ênfase é normal; três seguidas viram roteiro.
- Antes: "O mesmo SAP. Outra conversa com o auditor."
- Depois: "Com os mesmos dados do SAP, a conversa com o auditor muda."

**Aforismo.** "X é a linguagem de Y", "risco que não sai, fica coberto". Diga a coisa concreta.
- Antes: "Risco que não sai, fica coberto."
- Depois: "Quando o acesso precisa ficar, o risco ganha um controle."

**Trio forçado.** Tudo em grupos de três: três chips, três bullets em toda tela, "rápido,
simples e seguro". Varie: dois itens onde só há dois, quatro onde há quatro. O template pede
pontos por tela, não exatamente três.

**Mesma construção em sequência.** Quatro etapas seguidas no formato "A coisa acontece, a outra
coisa acontece". Varie a abertura e o ritmo.

**Emoji decorativo.** Em cartão, selo, título ou lista. Use ícone desenhado (SVG ou símbolo
tipográfico neutro) ou nada. Marcação de interface dentro de mockup (✓ de item concluído) não
conta.

**Fragmento sem sujeito.** "Sem instalação.", "Sem projeto de integração.", "por regra e sem
adivinhação". Escreva a frase com sujeito e verbo.
- Antes: "Sem projeto de integração."
- Depois: "Não há projeto de integração para começar."

**Vocabulário de IA e promocional.** crucial, fundamental, essencial, potencializar,
alavancar, impulsionar, jornada, ecossistema, robusto, sinergia, revolucionário, disruptivo,
de ponta, inovador, transformador, incrível, "no mundo de hoje", "cenário atual",
"elevar a outro patamar". Troque pelo efeito concreto ou corte.

**Cópula evitada.** "atua como", "se posiciona como", "conta com", "oferece" onde cabe "é" ou
"tem".

**Anúncio em vez de conteúdo.** "Vamos explorar", "confira a seguir", "é importante destacar".
Diga a coisa.

**Atribuição vaga.** "Especialistas apontam", "o mercado reconhece". Cite a fonte real ou corte.

**Encerramento genérico.** "O futuro é agora", "leve sua empresa ao próximo nível". Termine no
último fato concreto ou no pedido de ação.

**Negrito mecânico e Title Case.** Títulos em caixa de frase ("Como funciona", não "Como
Funciona"). Negrito só onde o leitor precisa parar.

**Aspas curvas.** Use aspas retas.

## O que NÃO mexer

- Nome de produto, nome de tela, rótulo real de botão (copie como está no sistema).
- Número que veio do material, com a fonte.
- Uma frase curta isolada para dar ênfase. O problema é a série, não a frase.

## Voz certa para apresentação de produto

Segunda pessoa, voz ativa, frases de tamanhos variados. Fale do resultado do cliente com o
vocabulário dele (na área de GRC: achado, controle compensatório, evidência, exposição,
comitê, ressalva). Prefira o detalhe específico que só esse produto tem ao adjetivo que
serve para qualquer produto.
