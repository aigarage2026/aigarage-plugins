# ai-garage — plugins do Claude Code

Marketplace de plugins/skills do ecossistema **ai-garage**, distribuído por git para
qualquer máquina/projeto do time.

## Plugins

| Plugin | O que faz |
|---|---|
| **telemetria** | Instrumenta qualquer app para telemetria de uso e a conecta ao painel central **ai-garage Pulse** (auto-enroll: captura sessões/tempo/ações/LLM, gera a `export_key`, cadastra via `POST /enroll` e liga polling ou push). |

## Como usar (em qualquer máquina/projeto)

Uma vez por máquina, dentro do Claude Code:

```
/plugin marketplace add aigarage2026/aigarage-plugins
/plugin install telemetria@aigarage
```

Depois disso, em **qualquer** projeto daquela máquina é só pedir a skill (ex.: "aplica o
telemetria aqui" / `/telemetria`).

Para atualizar quando este repo mudar:

```
/plugin marketplace update aigarage
```

## Estrutura

```
.claude-plugin/marketplace.json     # lista os plugins deste marketplace
plugins/telemetria/
  .claude-plugin/plugin.json         # metadados do plugin
  skills/telemetria/SKILL.md         # a skill em si
```

Para adicionar um novo plugin/skill: crie `plugins/<nome>/` com seu `plugin.json` e
`skills/`, e registre-o em `.claude-plugin/marketplace.json`.
