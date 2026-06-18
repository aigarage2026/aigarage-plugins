# ai-garage — plugins do Claude Code

Marketplace de skills do ecossistema **ai-garage**, distribuído por git para qualquer
máquina/projeto do time. Tudo num único plugin chamado `aigarage`, então as skills ficam
namespaced pelo ecossistema: `/aigarage:<skill>`.

## Skills (dentro do plugin `aigarage`)

| Skill | Comando | O que faz |
|---|---|---|
| **telemetria** | `/aigarage:telemetria` | Instrumenta qualquer app para telemetria de uso e a conecta ao painel central **ai-garage Pulse** (auto-enroll: captura sessões/tempo/ações/LLM, gera a `export_key`, cadastra via `POST /enroll` e liga polling ou push). |

> Em linguagem natural (ex.: "aplica o telemetria aqui") a skill também dispara sozinha pela
> `description`, sem precisar do slash.

## Como usar (em qualquer máquina/projeto)

Uma vez por máquina, dentro do Claude Code:

```
/plugin marketplace add aigarage2026/aigarage-plugins
/plugin install aigarage@aigarage
```

Atualizar quando este repo mudar:

```
/plugin marketplace update aigarage
```

## Estrutura

```
.claude-plugin/marketplace.json        # lista o plugin 'aigarage'
plugins/aigarage/
  .claude-plugin/plugin.json            # metadados do plugin (name: aigarage)
  skills/
    telemetria/SKILL.md                 # uma pasta por skill
```

Para adicionar uma nova skill (auditai-ui, rich-tooltips, multilang...): crie
`plugins/aigarage/skills/<nome>/SKILL.md`. Ela fica disponível como `/aigarage:<nome>` —
não precisa mexer no `marketplace.json`.
