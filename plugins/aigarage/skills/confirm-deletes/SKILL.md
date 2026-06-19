---
name: confirm-deletes
description: >-
  Garante que NENHUMA ação destrutiva ou irreversível seja executada sem
  confirmação explícita — vale para comandos que o agente roda (rm, DROP, DELETE,
  TRUNCATE, docker down -v, volume rm, prune, git push --force/reset --hard,
  sobrescrever arquivos) E para features de exclusão que construímos nas apps
  (diálogo de confirmação, soft-delete, type-to-confirm, undo). Use sempre que
  houver "deletar", "apagar", "remover", "excluir", "drop", "truncate", "limpar
  dados/base", "resetar", ou ao implementar um botão/endpoint de exclusão.
---

# confirm-deletes — sempre confirmar antes de apagar

Regra-mãe: **toda ação destrutiva ou irreversível PARA e pede confirmação explícita ANTES
de executar**, mostrando exatamente o que será afetado. Nunca assuma "sim". Na dúvida,
prefira a opção reversível e pergunte.

## A) Quando EU (agente) for executar um comando
Antes de rodar qualquer coisa que apague/sobrescreva dados, **pare e confirme**:
- Apagar/sobrescrever arquivos: `rm`, `rm -rf`, `mv` por cima, `>` truncando, `find … -delete`.
- Banco: `DROP TABLE/DATABASE/SCHEMA`, `TRUNCATE`, `DELETE`/`UPDATE` **sem `WHERE`** (ou com escopo amplo), `alembic downgrade`.
- Docker/infra: `docker compose down -v`, `docker volume rm/prune`, `docker system prune`, remover volumes/PVCs.
- Git: `git push --force`, `git reset --hard`, `git clean -fd`, deletar branch remota.
- Negócio: deletar/desativar usuários, registros em massa, jobs, backups, segredos.

**Protocolo (sempre nesta ordem):**
1. **Mostre o alvo concreto**: o quê, **quantos** itens, identificadores (ex.: "vai apagar
   3 tabelas: X, Y, Z" / "DELETE afeta ~12.480 linhas" / "remove o volume `pgdata` = banco inteiro").
2. **Diga o impacto e se é reversível** (tem backup? dá pra desfazer?).
3. **Peça confirmação explícita.** Para algo **irreversível ou em massa**, peça uma
   confirmação **forte** (ex.: o usuário digitar o nome do recurso ou "CONFIRMO").
4. **Só então execute.** Se a resposta não for um sim claro, **não faça**.
5. **Prefira o caminho seguro**: backup antes; `DELETE` com `WHERE` e `LIMIT`; soft-delete;
   `down` (sem `-v`) em vez de `down -v`; mover para lixeira em vez de `rm`.

Nunca "otimize" pulando a confirmação porque "parece óbvio". Aprovação para uma ação
**não** vale para a próxima.

## B) Quando CONSTRUIR uma feature de exclusão (UI + API)
Implemente exclusão segura por padrão:
- **Confirmação na UI**: diálogo "Tem certeza?" nomeando o item ("Excluir o papel **X**?").
  Botão destrutivo em vermelho, ação separada do clique acidental.
- **Soft-delete por padrão** quando fizer sentido (`ativo=false`/`deleted_at`) em vez de apagar
  fisicamente; mantém histórico e permite desfazer.
- **Type-to-confirm** para destrutivo/irreversível ou em massa: exigir digitar o nome do recurso
  (ex.: GitHub-style "digite `meu-projeto` para confirmar").
- **Guardas de integridade no backend**: não excluir recurso **em uso** (FK/dependências);
  não permitir excluir a si mesmo / o último admin; validar escopo (sem DELETE sem filtro).
- **Undo / lixeira** quando viável; **auditoria** (quem excluiu, quando, o quê).
- **Nunca** endpoints que apagam em massa sem filtro + sem confirmação; rate-limit em destrutivos.

## C) Padrão de mensagem de confirmação (exemplos)
- "⚠️ Isso vai **apagar o volume `pgdata`** = **todo o banco** (irreversível, sem backup). Confirma? Digite `apagar pgdata`."
- "O `DELETE` sem WHERE afeta **todas as ~48k linhas** de `eventos`. Quer mesmo? Posso fazer um backup antes."
- "Excluir o usuário **maria@x.com**? Ele será **desativado** (soft-delete) e pode ser reativado."

## Regras
- **Default-deny** em destrutivo: sem confirmação clara → não executa.
- **Mostre números/identificadores reais** (não "alguns registros").
- **Backup antes** de operações de grande impacto, quando possível (ver skill `safe-stack`).
- Comandos proibidos só com confirmação forte e ciência do usuário (ex.: `down -v`, `prune --volumes`).

> Para tornar isto um hábito SEMPRE-ativo (e não só quando o skill é lembrado), dá para
> reforçar com uma preferência/memória ou um hook do Claude Code — peça que eu configuro.
