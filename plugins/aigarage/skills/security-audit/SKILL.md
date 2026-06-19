---
name: security-audit
description: >-
  Auditoria de segurança (AppSec) de qualquer projeto, focada no OWASP Top 10 e
  secure coding + conformidade LGPD. Detecta linguagem/framework/ORM automaticamente,
  procura SQL Injection, XSS, CSRF, falhas de validação, headers de segurança, segredos
  hardcoded, broken access control/IDOR, autenticação/hashing fraco, flags de cookie,
  dependências vulneráveis, SSRF/path traversal/open redirect/CORS, upload inseguro,
  vazamento de dados, cripto fraca, e os deveres da LGPD (direitos do titular, retenção,
  cripto em repouso, transferência internacional, trilha de acesso). Gera SECURITY_AUDIT.md
  por projeto + resumo consolidado por severidade. NUNCA corrige sozinho: audita, reporta e
  só aplica correção após confirmação; depois verifica AO VIVO. Use quando o usuário pedir
  "auditoria de segurança", "security audit", "revisão de segurança", "OWASP", "LGPD",
  "tem vulnerabilidade?", "secure coding", "pentest de código" ou "aplica o security-audit aqui".
---

# Security Audit — auditoria AppSec (OWASP Top 10 + LGPD) por projeto

Objetivo: produzir uma auditoria de segurança **acionável e honesta** de um ou mais
projetos, e — após confirmação — **aplicar e verificar** as correções. Foco: secure coding,
OWASP Top 10 e LGPD. Resultado: relatório por projeto + resumo consolidado.

## Princípios (não-negociáveis)

1. **Detecte a stack ANTES de analisar.** Padrões seguros variam por linguagem/framework/ORM.
   Concatenar string em SQL é fatal no driver cru, mas seguro num ORM com bind. Classifique
   pela stack real.
2. **Evidência ou silêncio.** Todo achado aponta `arquivo:linha` e o trecho que o prova. Sem
   evidência concreta → no máximo "A REVISAR". **Reverifique antes de afirmar** (ver armadilha
   do `.env` abaixo): um `grep`/`ls` pode enganar — confirme com o comando autoritativo.
3. **Confiança explícita.** Cada achado tem confiança (Alta/Média/Baixa). Incerto → **A REVISAR**.
4. **Minimize falso positivo.** Antes de reportar: "existe ORM/sanitizador/middleware/framework
   que já trata isto no caminho?" Se sim, não é achado.
5. **NUNCA corrija sozinho.** Audita → relatório → espera o "ok" → aplica só o aprovado, um a um.
6. **Verifique a correção AO VIVO.** Depois de aplicar, prove com requisição real (401/429,
   headers presentes, token forjado rejeitado, dado cifrado no banco). Rode a suíte de testes.
7. **Sem dados/segredos no relatório nem no commit.** Redija (`****`). Antes de commitar, faça
   `git diff --cached | grep` pelos nomes de segredo e confirme que nenhum VALOR entrou.

## Fluxo

- **Passo 0 — Descobrir e classificar projetos.** Liste raízes com manifesto (`package.json`,
  `pyproject.toml`/`requirements*.txt`, `go.mod`, `pom.xml`, `composer.json`, `Gemfile`,
  `Cargo.toml`, `*.csproj`). Para cada um anote **linguagem, framework(s), ORM/driver e como as
  queries são escritas, autenticação, gestão de segredos**. **Apresente projeto→stack ANTES de auditar.**
- **Passo 1 — Auditar (só leitura).** Rode as verificações; use busca por padrões de risco e
  **leia o contexto** de cada hit. Rode os scanners de dependência. Se possível, **teste ao vivo**
  os endpoints suspeitos (ex.: `curl` sem token → era 200?).
- **Passo 2 — Relatório.** `SECURITY_AUDIT.md` na raiz de cada projeto + resumo consolidado.
- **Passo 3 — Correção (só após confirmação).** Para itens com decisão de negócio/jurídica
  (retenção, esquecimento, base legal), **pergunte** antes. Aplique, verifique ao vivo, re-teste.

## Severidade
- **Crítica** — exploração remota direta e grave: SQLi exposto, RCE/deserialização, auth bypass,
  segredo de produção versionado/previsível, IDOR em dado sensível, **dado sensível servido sem auth**.
- **Alta** — XSS armazenado explorável, CSRF em ação sensível, hashing fraco (MD5/SHA1/plaintext),
  SSRF, path traversal, CORS `*` com credenciais.
- **Média** — headers ausentes, cookie sem flags, validação só no cliente, sem rate-limit no login,
  dependência com CVE médio.
- **Baixa** — hardening ausente (HSTS/Referrer-Policy), verbosidade de erro, melhoria defensiva.

## Verificações OBRIGATÓRIAS
1. **SQL Injection** — tudo parametrizado/ORM. 🚩 f-strings/`%`/`+`/`.format()`/template literals
   em SQL; `text("..."+var)`. ✅ bind params, `.filter(Model.x==v)`. (Atenção: `WHERE {cond}` é
   seguro SE `cond` for só fragmentos estáticos e os valores forem bind `?` — leia o contexto.)
2. **XSS** — conteúdo do usuário escapado. 🚩 `innerHTML`, `dangerouslySetInnerHTML`, `v-html`,
   `[innerHTML]`/`bypassSecurityTrust*`, `|safe`/`mark_safe`, auto-escape off, `eval`.
3. **CSRF** — token em ações de estado + `SameSite`. APIs **stateless com Bearer** → CSRF N/A
   (**registre esse raciocínio**); cookie de sessão sem token → achado.
4. **Validação de input** — frontend **E** backend; tipo/tamanho/formato/allowlist.
5. **Headers** — CSP, X-Frame-Options, X-Content-Type-Options (+HSTS/Referrer-Policy/
   Permissions-Policy). Procure no app **e** no proxy. Se a API é publicada direto numa porta
   (sem o proxy), os headers precisam existir **no app**.

## Verificações COMPLEMENTARES
6. Segredos hardcoded (código/versionados; `git log`/`.env`). 7. Broken access control / IDOR /
autorização ausente. 8. Auth: hashing forte (bcrypt/argon2/scrypt/PBKDF2 — nunca MD5/SHA1),
anti-brute-force, sessão/JWT com expiração e segredo forte. 9. Flags de cookie (HttpOnly/Secure/
SameSite). 10. Dependências (npm audit / pip-audit / govulncheck / composer audit / cargo audit /
bundler-audit; sem scanner → A REVISAR, não invente CVE). 11. SSRF/path traversal/open redirect/
CORS. 12. Upload (tipo por conteúdo, tamanho, destino, nome). 13. Vazamento de PII/segredo em logs
e erros (`debug=True`). 14. Cripto fraca & deserialização insegura (`pickle`/`yaml.load`/`eval`).

## Conformidade LGPD (Lei 13.709/2018)
Achado quando ausente/inadequado; itens jurídicos/organizacionais → **[A REVISAR]**. Para cada um,
cite **artigo** e **correção técnica concreta**.
15. **Mapeamento de PII** (nome, CPF, e-mail, telefone, IP, geo) e dados sensíveis. Liste os pontos.
16. **Minimização** — só o necessário (Art. 6º). 17. **Consentimento** — registro/granularidade/
revogação (Arts. 7º-9º). 18. **Direitos do titular** — acesso/correção/exclusão/portabilidade,
rotas de export e deleção (Art. 18). 19. **Retenção/descarte** — TTL/expurgo (Art. 15/16).
20. **Cripto em repouso** — PII cifrada em disco/coluna + TLS (Art. 46). 21. **Anonimização/
pseudonimização** em analytics/logs/dev/treino de IA (Art. 12). 22. **Trilha de acesso** a dado
pessoal sem gravar o dado (Art. 37). 23. **Compartilhamento/transferência internacional** a
subprocessadores/IA (Art. 33). 24. **Cookies/rastreadores** (consentimento). 25. **Crianças**
(Art. 14). 26. **Privacy by design/default** (Art. 46 §2º). 27. **Resposta a incidentes** (Art. 48).

## Cookbook de correção (padrões testados em campo)

- **Segredo fail-closed (JWT/cifra):** NUNCA caia num placeholder. Exija `>=32` chars do env e
  levante erro se ausente. Gere com `python -c "import secrets;print(secrets.token_urlsafe(48))"`
  e injete fora do repo (arquivo central de chaves / secret do deploy). Trocar o segredo invalida
  os tokens antigos (desejável). Em testes, injete um segredo fixo no `conftest`/setup.
- **Access control em massa:** routers montados sem `dependencies=` ficam públicos. Exija auth no
  router (`include_router(r, dependencies=[Depends(get_current_user)])`) e/ou por endpoint. Deixe
  só o healthcheck público. **Prove com `curl` sem token → 401.**
- **Anti-brute-force no login:** limitador por IP+identificador (ex.: 8 falhas/5 min → 429),
  zera no sucesso. Em memória serve p/ 1 processo; **multi-instância → mover para Redis** (e diga isso).
- **Headers de segurança:** um middleware no app (cobre porta direta + proxy). CSP calibrada p/ a
  SPA (bundle próprio, estilos inline, fontes externas); HSTS só com TLS (deixe pronto/comentado).
- **Cifra de PII em repouso:** `TypeDecorator` transparente (ex.: Fernet/AES) keyed por env.
  ⚠️ **NÃO cifre coluna que é filtrada/ordenada/indexada/agregada** (dado analítico) — quebra a app;
  proteja-a com **disco/volume cifrado + backups cifrados + access control**. Para coluna cifrada
  **pesquisável por igualdade** (ex.: e-mail de login) use **blind index** (HMAC determinístico
  normalizado) numa coluna paralela `*_hash` (única/indexada), preenchida por listener
  `before_insert/before_update`; troque as queries `== valor` por `== blind_index(valor)`.
- **Pseudonimização p/ LLM/terceiros (Art. 33):** mascare nomes/PII ANTES de enviar ao provedor
  externo e **restaure na resposta** ao usuário (mapa em memória, nomes maiores primeiro p/ não
  quebrar compostos).
- **Direitos do titular (Art. 18):** `GET /me/data` (export) + `DELETE /me/data` (anonimizar:
  PII→anônimo, desativa conta, zera PII em telemetria — preserva integridade dos registros).
- **Retenção (Art. 15/16):** job/cron que expurga/anonimiza além de N dias (N configurável por env).
- **Trilha de acesso (Art. 37):** tabela só de metadados (ator, método, rota, status, ts — **sem o
  dado**), preenchida por middleware nas rotas de PII; endpoint admin para leitura.
- **Erro de auth genérico:** responda "token inválido" e logue o detalhe só internamente.

## Armadilhas / lições (evite retrabalho e falso positivo)
- **`.env` "versionado":** `git ls-files <path>` pode listar por casamento de padrão — confirme com
  `git ls-files --error-unmatch <path>` e `git check-ignore -v <path>`. Já vimos isso virar FP.
- **Falhas de teste pré-existentes:** antes de culpar sua mudança, rode os testes que falharam com
  suas alterações **no stash** (`git stash`); se já falhavam, são pré-existentes — diga isso no relatório.
- **Não teste endpoint destrutivo em dado real** (ex.: `DELETE /me/data` no admin). Crie usuário
  descartável ou só verifique que a rota está registrada (OpenAPI) + revise a lógica.
- **Recriar container ≠ rebuild de imagem.** Mudança de código volume-montado: recriar basta.
  Nova dependência (ex.: `cryptography`): **rebuild** da imagem. E confira QUAL requirements o
  Dockerfile copia (pode haver um na raiz e outro em `deployment/`).
- **`nonExplicitSupportedLngs` (i18next):** fora do escopo de segurança, mas: com recursos sob
  código regional (`pt-BR`) ele colapsa p/ `pt` e some com as traduções. (lição de um projeto irmão.)
- **Fail-closed quebra testes:** ao tornar um segredo obrigatório, injete-o no `conftest`/CI.

## Heurísticas de busca (ponto de partida — sempre ler o contexto)
```
# SQLi      grep -rniE "execute\(|cursor\.|\.raw\(|text\(|query\(" ... ; f-string com SELECT/INSERT/UPDATE/DELETE
# XSS       grep -rniE "innerHTML|dangerouslySetInnerHTML|v-html|\|\s*safe|mark_safe|bypassSecurityTrust|eval\("
# segredos  grep -rniE "(api[_-]?key|secret|password|token|aws_|private_key)\s*[:=]\s*['\"][^'\"]{8,}"
# cookies/headers/CORS  grep -rniE "set_cookie|httponly|samesite|secure=|Access-Control-Allow-Origin|CSP|X-Frame|HSTS"
# cripto/deserial.      grep -rniE "md5|sha1|DES|ECB|pickle\.load|yaml\.load\(|eval\(|exec\("
# access control        liste rotas e veja quais NÃO têm dependência de auth; cheque include_router sem dependencies=
# PII/LGPD              grep -rniE "email|cpf|telefone|nome|gerente|user_email|ip_addr" nos modelos/logs/prompts de LLM
```

## Template do `SECURITY_AUDIT.md`
```markdown
# Security Audit — <projeto>
- Data · Auditor: security-audit · Stack detectada · Escopo · Fora de escopo
## Resumo por severidade  (tabela 🔴🟠🟡🔵⚪ × qtde)
### Status de remediação  (item × sev × ✅/⏳/falso-positivo)
## Achados
### [SEV] <título> — <categoria OWASP/LGPD + artigo>
- Local `arquivo:linha` · Confiança · Risco · Evidência (redigida) · Correção (ANTES/DEPOIS na linguagem do projeto)
## Conformidade LGPD  (achados 15–27 com artigo + correção; [A REVISAR] p/ jurídico)
## Runbook — cripto em repouso/trânsito  (disco cifrado, backups, TLS/HSTS, DB restrito)
## Verificações sem achados (escopo coberto)  — mostra abrangência
## Fechamento  — o que ficou pendente (infra/jurídico) + lembretes operacionais
```

## Resumo consolidado (multi-projeto)
Tabela projeto × severidade, total ordenado por severidade, caminhos dos relatórios. Críticos primeiro.

## Lembrete final
Auditar ≠ corrigir. Relatório → confirmação → correção um-a-um → **verificação ao vivo** → re-teste.
O que não é código (cifra de disco, base legal, resposta a incidentes) entra como **pendência** no relatório.
