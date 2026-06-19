---
name: safe-stack
description: >-
  Liga, para, faz backup e mostra o status de uma stack Docker Compose de
  desenvolvimento COM SEGURANÇA, sem nunca apagar dados. Use quando o usuário
  disser coisas como "paramos aqui", "aqui paramos", "parar o ambiente",
  "desligar", "stop", "pausar", OU "iniciar", "voltar", "subir o ambiente",
  "ligar", "start", OU "backup do banco", "status da stack", OU "aplica o
  safe-stack aqui" / "configura a resiliência deste projeto" (para preparar um
  projeto novo com auto-restart, atalhos e backup). Funciona em qualquer projeto
  que tenha um docker-compose (e opcionalmente um Makefile com atalhos).
---

# Safe Stack — ligar / parar / backup de stack Docker Compose sem perder dados

Este skill executa o ciclo de vida de uma stack Docker Compose de forma **segura
e idempotente**. A prioridade nº 1 é **NUNCA perder ou corromper dados**.

## ⛔ Regra absoluta (NUNCA quebrar, em nenhuma hipótese)
Estes comandos são **proibidos** neste skill — nunca sugira, nunca execute:
- `docker compose down -v` / `docker-compose down --volumes` (apaga os volumes = perde o banco)
- `docker volume rm ...`, `docker volume prune`
- `docker system prune` (com `--volumes` ou `-a`)
- `rm -rf` em diretórios de dados/volumes
- `DROP DATABASE`, `TRUNCATE`, `DELETE FROM` sem o usuário pedir explicitamente
Parar **sempre** é graceful e **preserva** os volumes. Se em dúvida, prefira a opção
que mantém os dados e confirme com o usuário antes de qualquer coisa irreversível.

## Passo 0 — Localizar a stack (sempre primeiro)
1. Ache o arquivo compose (nesta ordem): `docker-compose.yml`, `compose.yml`,
   `deployment/docker-compose.yml`, `docker/docker-compose.yml`,
   `deploy/docker-compose.yml`. Use o primeiro que existir.
   - Defina internamente `COMPOSE = docker compose -f <caminho-encontrado>`.
2. Veja se há `Makefile` com alvos úteis: rode `grep -E "^(start|stop|backup|status|up|down):" Makefile` (se existir).
   - **Se houver os alvos, PREFIRA `make <alvo>`** (start/stop/backup/status) — eles já
     encapsulam o caminho correto do compose. Senão, use `$COMPOSE` direto.
3. Se não achar nenhum compose nem Makefile, avise o usuário que não há stack
   detectada e pergunte o caminho.

## Detectar a intenção e agir
Pelo que o usuário disse, escolha UMA ação:

### ▶️ PARAR ("paramos aqui", "parar", "stop", "desligar", "pausar")
1. **Backup antes de parar** (se houver serviço de banco — postgres/mysql/mariadb):
   execute a ação BACKUP abaixo. É barato e é a maior proteção contra perda.
   (Se o usuário pedir para pular o backup, pule.)
2. Pare de forma graceful, mantendo os dados:
   - `make stop` se existir, senão `$COMPOSE stop`.
   - (`stop` é melhor que `down` aqui: para os containers sem removê-los, religa mais rápido.)
3. Confirme: `$COMPOSE ps` (containers parados) e diga ao usuário, em uma frase:
   "Parado com segurança — os dados estão preservados nos volumes."

### ⏯️ INICIAR ("iniciar", "voltar", "subir", "ligar", "start")
1. **Cheque o Docker:** `docker info >/dev/null 2>&1`.
   - Se falhar (daemon desligado), tente nesta ordem e avise o que está fazendo:
     a) `sudo service docker start`
     b) se "unrecognized service", `sudo nohup dockerd > ~/dockerd.log 2>&1 &` e
        aguarde ~8s (`docker info` até responder).
     c) se nada funcionar, peça ao usuário para iniciar o Docker e pare aqui.
2. Suba em segundo plano (sem prender o terminal):
   - `make start` se existir, senão `$COMPOSE up -d`.
3. Verifique a saúde: `$COMPOSE ps`. Aguarde os healthchecks ficarem `healthy`/`Up`.
   - Se um serviço de API tiver porta publicada, teste o endpoint de health se souber
     (ex.: `curl -sf http://localhost:<porta>/health`).
4. Informe ao usuário que está no ar e, se aplicável, a URL de acesso (leia as `ports`
   do compose para descobrir a porta publicada).

### 💾 BACKUP ("backup", "fazer cópia do banco")
1. Se existir `make backup`, use-o. Senão, faça manualmente:
   - Descubra o serviço de banco e credenciais lendo o compose (procure
     `POSTGRES_USER`, `POSTGRES_DB`, ou `MYSQL_*`).
   - Postgres: `mkdir -p backups && $COMPOSE exec -T <svc_db> pg_dump -U <user> -Fc <db> > backups/<db>_$(date +%Y%m%d_%H%M%S).dump`
   - MySQL/MariaDB: `mkdir -p backups && $COMPOSE exec -T <svc_db> mysqldump -u <user> -p<senha> <db> > backups/<db>_$(date +%Y%m%d_%H%M%S).sql`
2. **Garanta que `backups/` está no `.gitignore`** (dumps contêm dados — nunca versionar).
   Se não estiver, adicione.
3. Confirme o arquivo gerado (`ls -lh backups/ | tail -1`).

### 📊 STATUS ("status", "como está a stack")
- `$COMPOSE ps` e um resumo de quais serviços estão `Up`/`healthy`.

### 🛡️ APLICAR / CONFIGURAR RESILIÊNCIA ("aplica o safe-stack aqui", "configura a resiliência deste projeto", "deixa esse projeto à prova de perder dados")
Use quando o usuário quiser **preparar um projeto novo** para parar/voltar com segurança.
Faça, mostrando um resumo do que mudou e nunca tocando em dados:
1. **Auto-restart:** adicione `restart: unless-stopped` a CADA serviço do compose
   (que ainda não tenha). Assim a stack volta sozinha após reboot/crash do Docker.
2. **Atalhos no Makefile** (se houver Makefile; senão, ofereça criar um simples):
   garanta os alvos `start` (`up -d`), `stop` (`stop`), `status` (`ps`),
   `logs` (`logs -f`), `backup` (pg_dump/mysqldump → `backups/`), e `down` (`down`
   SEM `-v`). Defina um `COMPOSE = docker compose -f <caminho>` no topo.
3. **Proteja os backups:** adicione `backups/` ao `.gitignore` (dumps têm dados —
   nunca versionar). Adicione também `/*.dump` e `/*.sql` se fizer sentido.
4. **NUNCA** adicione nenhum alvo/comando com `-v`, `volume rm` ou `prune`.
5. (WSL) Lembre o usuário, se aplicável, de ativar systemd (`[boot] systemd=true`
   em `/etc/wsl.conf`) para o Docker subir sozinho no boot.
6. Resuma: "Projeto configurado — agora `make start`/`make stop`/`make backup` e a
   stack volta sozinha após reboot. Nenhum comando destrutivo foi adicionado."

## Boas práticas a reforçar para o usuário (quando fizer sentido)
- Os dados vivem nos **volumes** do Docker e sobrevivem a `stop`/`down`/reboot.
- `restart: unless-stopped` no compose faz a stack **voltar sozinha** após reboot/crash.
- No WSL, ativar **systemd** (`[boot] systemd=true` em `/etc/wsl.conf`) faz o Docker
  subir sozinho no boot — combinado com o restart policy, a stack volta sem comando.
- Postgres é **crash-safe** (WAL): mesmo um desligamento abrupto recupera ao ligar.
  Ainda assim, `make stop` antes de fechar o PC é a parada mais limpa.

## Estilo de execução
- Rode os comandos você mesmo (via shell) quando o usuário pedir a ação, não só explique.
- Seja conciso no retorno: o que foi feito + estado final + (se iniciar) a URL.
- Em qualquer passo destrutivo ou ambíguo, **pare e pergunte** antes.
