---
name: llm-keys
description: >-
  Centraliza as chaves de API de LLM/serviços (OpenAI, Anthropic, Resend, etc.)
  num único arquivo seguro, para que TODOS os projetos usem a mesma fonte: trocou
  a chave uma vez → vale em todos; adicionou um provedor novo → já fica disponível.
  Use quando o usuário pedir "minhas chaves de LLM", "centralizar API keys",
  "trocar a chave da OpenAI/Anthropic", "adicionar provedor de LLM", "conectar este
  projeto às minhas chaves" ou "aplica o llm-keys aqui".
---

# llm-keys — chaves de LLM centralizadas (fonte única para todos os projetos)

As chaves vivem em UM arquivo seguro fora dos repositórios:
**`~/.config/llm-keys/keys.env`** (permissão `600`). Trocar/adicionar ali reflete em todos
os projetos que carregam esse arquivo. NUNCA coloque o valor das chaves dentro deste skill,
de um repositório, ou em qualquer arquivo versionado.

> Caminho absoluto (para usos que não expandem `~`): `/home/rogerio_ribeiro/.config/llm-keys/keys.env`
> — ajuste o usuário se for outra máquina.

## ⛔ Regras de segurança
- O arquivo central tem permissão **`600`** (só o dono lê). Mantenha assim.
- **Nunca** ecoe/print os VALORES das chaves (em logs, terminal, respostas). Para conferir,
  mostre só o NOME da chave e se está preenchida (ex.: "OK / vazio"), nunca o valor.
- **Nunca** versione chaves: garanta `*.env` e o caminho central no `.gitignore` de cada projeto.
- Ao migrar chaves de um `.env` de projeto para o central, faça file-to-file (sem imprimir).

## Ações

### 🔑 LISTAR ("quais chaves eu tenho")
- Mostre só os NOMES presentes em `~/.config/llm-keys/keys.env` (linhas `^[A-Z_]+=`),
  indicando preenchida/vazia — nunca o valor.

### ➕ ADICIONAR / 🔄 TROCAR uma chave ("adiciona a GEMINI", "troca a chave da OpenAI")
- Edite SOMENTE `~/.config/llm-keys/keys.env`, acrescentando/atualizando a linha `CHAVE=valor`.
  Se o usuário forneceu o valor no chat, escreva no arquivo mas NÃO repita o valor de volta.
- Confirme mostrando só o nome da chave e "atualizada". Lembre que projetos rodando precisam
  recarregar (reiniciar a stack/processo) para pegar o novo valor.

### 🔌 CONECTAR ESTE PROJETO ("aplica o llm-keys aqui", "conecta este projeto às minhas chaves")
Faça o projeto LER do arquivo central (sem duplicar chaves):
- **Docker Compose**: em cada serviço que usa as chaves, adicione o arquivo central em `env_file`
  (caminho absoluto), p.ex.:
  ```yaml
  services:
    api:
      env_file:
        - /home/rogerio_ribeiro/.config/llm-keys/keys.env
        - .env            # mantém as variáveis específicas do projeto
  ```
  (Compose injeta as KEY=VALUE; trocar o arquivo central + `restart` atualiza tudo.)
- **Node/Vite/Next ou Python sem Docker**: carregue o arquivo central no boot —
  `set -a; source ~/.config/llm-keys/keys.env; set +a` antes de rodar, ou (Python)
  `from dotenv import load_dotenv; load_dotenv(os.path.expanduser("~/.config/llm-keys/keys.env"))`.
- **Importante**: NÃO duplique as chaves no `.env` do projeto. Deixe no `.env` local só o que é
  específico do projeto (ex.: `AUDITAI_LLM_PROVIDER`, `DATABASE_URL`). Garanta `.env` no `.gitignore`.

### 🧹 MIGRAR ("tira as chaves duplicadas deste projeto e usa o central")
- Mova as linhas de chave do `.env` do projeto para o central (se ainda não estiverem lá),
  deduplicando, file-to-file (sem imprimir valores). Depois REMOVA essas linhas do `.env` do
  projeto e conecte via `env_file`/source (ação acima). Confirme que o app ainda lê as chaves.

## Como adicionar um provedor novo no futuro (resumo p/ o usuário)
- "Edite `~/.config/llm-keys/keys.env`, adicione `XAI_API_KEY=...` — pronto, disponível em
  todos os projetos conectados (reinicie a stack do projeto para recarregar)."

## Conteúdo atual (gerenciado)
O arquivo central já contém: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `RESEND_API_KEY`,
`AUDITAI_NOTIF_FROM`, com placeholders comentados para GEMINI/GROQ/MISTRAL/DEEPSEEK/XAI.
