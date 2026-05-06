# Hermes CLI Commands (Condensed Reference)

Generated from Hermes Agent v0.12.0 (2026.4.30). One line per command, key flags only.
For full per-command help, see `cli-reference.md` or run `hermes <cmd> --help`.

---

## 1. Top-level form

```
hermes [-h] [--version] [-z PROMPT] [-m MODEL] [--provider PROVIDER]
       [-t TOOLSETS] [--resume SESSION] [--continue [SESSION_NAME]]
       [--worktree] [--accept-hooks] [--skills SKILLS] [--yolo]
       [--pass-session-id] [--ignore-user-config] [--ignore-rules]
       [--tui] [--dev] {<subcommand>} ...
```

Bare `hermes` → interactive chat (REPL).

---

## 2. Channels & Messaging

```
gateway run                       Foreground (debug, WSL, Termux)
gateway start / stop / restart    Service lifecycle
gateway status                    Show status
gateway install / uninstall       Manage launchd/systemd service
gateway setup                     Configure Telegram/Discord/WhatsApp/Slack (interactive)
gateway migrate-legacy            Remove pre-rename hermes.service units

whatsapp                          WhatsApp helpers (QR pairing)
slack                             Slack manifest generation + helpers
webhook                           Configure inbound webhooks
pairing                           Approve inbound pair requests
```

---

## 3. Models & Providers

```
model                             Interactive: pick provider + default model
fallback                          Manage fallback provider chain
login                             OAuth login to Nous portal
logout                            Clear provider auth
auth                              Manage pooled provider credentials (Codex OAuth, etc.)
```

Per-call overrides:
- `-m, --model <provider/model>`
- `--provider <name>`
- `HERMES_INFERENCE_PROVIDER=<name>` env var

Default model location: `~/.hermes/config.yaml` → `model.default`.
API keys: `~/.hermes/.env`.

---

## 4. Skills & Plugins

```
skills                            Manage local skills (~/.hermes/skills/)
plugins                           Manage Hermes plugins (Python modules)
curator                           Skill curation tooling
tools                             Toggle agent tools on/off
mcp                               Manage MCP server registrations
```

Skills location: `~/.hermes/skills/<category>/<name>/SKILL.md`
Optional skills (heavier): `~/.hermes/hermes-agent/optional-skills/`
Plugins: `~/.hermes/hermes-agent/plugins/` (managed by Hermes)

---

## 5. Cron & Hooks

```
cron                              Scheduled jobs (see `hermes cron --help`)
hooks                             Lifecycle/shell hooks
```

Cron state: `~/.hermes/cron/`
Hooks state: `~/.hermes/hooks/`

---

## 6. Memory & Insights

```
memory                            Long-term memory store
insights                          What Hermes has learned about you
sessions                          Session management (~/.hermes/sessions/)
```

---

## 7. Status / Diagnostics

```
status                            Show status of all components
doctor                            Health checks + auto-fix
debug                             Lower-level debug helpers
dump                              Dump diagnostic info
logs                              View ~/.hermes/logs/
```

---

## 8. Config

```
config                            View current config
config edit                       Open ~/.hermes/config.yaml in $EDITOR
```

Config file: `~/.hermes/config.yaml` (YAML)
Personality: `~/.hermes/SOUL.md`

---

## 9. Backup / Import / Update / Uninstall

```
backup                            Local backup of ~/.hermes/
import                            Import from Claude Code, Claude Desktop, etc.
update                            Update Hermes to latest
uninstall                         Remove Hermes
```

---

## 10. Other

```
chat                              Interactive chat (default behavior)
setup                             First-run wizard
profile                           Manage profile / personality
kanban                            Per-session task board
acp                               ACP harness bridge
claw                              OpenClaw compatibility layer
dashboard                         Open web Control UI
completion                        Print shell completion script
version                           Print version
```

---

## Quick Common Recipes

**One-shot prompt (no chat):**
```bash
hermes -z "your prompt" -m anthropic/claude-opus-4.6
```

**Resume last session:**
```bash
hermes --continue
```

**Run gateway in foreground (debug):**
```bash
hermes gateway run
```

**Check what's running:**
```bash
hermes status
hermes doctor
```

**Add an API key (non-interactive):**
```bash
echo 'OPENROUTER_API_KEY=sk-or-...' >> ~/.hermes/.env
```

**Switch default model (non-interactive):**
```bash
sed -i.bak 's|^  default: ".*"|  default: "anthropic/claude-opus-4.7"|' ~/.hermes/config.yaml
hermes gateway restart
```
