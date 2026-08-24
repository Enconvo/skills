# Hermes CLI Commands (Condensed Reference)

Generated from Hermes Agent v0.20.5 (2026.8.19) · upstream 14c59f0b. One line per command, key flags only.

**Top-level additions observed by v0.20.5:** `worktree`, `egress`, `pause`, `resume`, `sync`, `peer`, `verify`, `approvals`, `import-agent`, `skin`, and `monitoring`. v0.18 additions remain: `console`, `journey`, `learning`, and `memory-graph`; earlier additions include `moa`, `secrets`, `migrate`, `whatsapp-cloud`, `portal`, `project`, `pets`, `serve`, `desktop`, `gui`, `prompt-size`, `proxy`, `lsp`, `send`, `checkpoints`, `bundles`, and `computer-use`.

For full per-command help, see `cli-reference.md` or run `hermes <cmd> --help`.

---

## 1. Top-level form

```
hermes [-h] [--version] [-z PROMPT] [--usage-file PATH] [-m MODEL] [--provider PROVIDER]
       [--reasoning LEVEL] [-t TOOLSETS] [--resume SESSION] [--no-restore-cwd] [--in DIR]
       [--continue [SESSION_NAME]] [--worktree] [--accept-hooks] [--skills SKILLS]
       [--yolo] [--pass-session-id] [--ignore-user-config] [--ignore-rules]
       [--safe-mode] [--tui] [--cli] [--dev]
       {chat,model,moa,fallback,worktree,secrets,egress,migrate,gateway,...} ...
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

whatsapp                          WhatsApp Web helpers (QR pairing)
whatsapp-cloud                    WhatsApp Cloud API helpers
slack                             Slack manifest generation + helpers
webhook                           Configure inbound webhooks
pairing                           Approve inbound pair requests
peer                              Bot-to-bot DMs across Hermes gateways
send                              Send side-channel messages to configured platforms
```

---

## 3. Models & Providers

```
model                             Interactive: pick provider + default model
fallback                          Manage fallback provider chain
portal                            Nous Portal auth/status helpers
login                             Removed/runtime legacy; prefer portal/auth/model
auth                              Manage pooled provider credentials (Codex OAuth, etc.)
logout                            Clear provider auth
proxy                             OpenAI-compatible local proxy to OAuth providers
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
bundles                           Group multiple skills under one slash command
plugins                           Manage Hermes plugins (Python modules)
curator                           Skill curation tooling
sync                              Sync skills across devices and teams
tools                             Toggle agent tools on/off
mcp                               Manage MCP server registrations
lsp                               Manage language servers for semantic diagnostics
computer-use                      Install/check cua-driver for computer_use
```

Skills location: `~/.hermes/skills/<category>/<name>/SKILL.md`
Optional skills (heavier): `~/.hermes/hermes-agent/optional-skills/`
Plugins: `~/.hermes/hermes-agent/plugins/` (managed by Hermes)

---

## 5. Cron & Hooks

```
cron                              Scheduled jobs (see `hermes cron --help`)
hooks                             Lifecycle/shell hooks
pause / resume                    Emergency-stop or resume cron, kanban, and gateway turns
```

Cron state: `~/.hermes/cron/`
Hooks state: `~/.hermes/hooks/`

---

## 6. Memory & Insights

```
memory                            Long-term memory store
memory-graph                      Memory graph inspection and management
learning                          Learning/review workflows
journey                           Cross-session journey/history surface
insights                          What Hermes has learned about you
sessions                          Session management (~/.hermes/sessions/)
prompt-size                       Prompt/context sizing diagnostics
```

---

## 7. Status / Diagnostics

```
status                            Show status of all components
doctor                            Health checks + auto-fix
security                          Security checks/advisories
egress                            Credential-injection firewall management
approvals                         Mine approval history into allowlist proposals
verify                            Detect and smoke-test a project's run recipe
monitoring                        Gateway health and diagnostic exports
debug                             Lower-level debug helpers
dump                              Dump diagnostic info
logs                              View ~/.hermes/logs/
```

---

## 8. Config

```
config                            View current config
config edit                       Open ~/.hermes/config.yaml in $EDITOR
secrets                           External secret-source management
skin                              List, switch, and tweak UI skins
```

Config file: `~/.hermes/config.yaml` (YAML)
Personality: `~/.hermes/SOUL.md`

---

## 9. Backup / Import / Update / Uninstall

```
backup                            Local backup of ~/.hermes/
checkpoints                       Filesystem checkpoint store + rollback support
import                            Restore a Hermes backup archive
import-agent                      Import Claude Code or Codex CLI setup
migrate                           Migration helpers distinct from import
worktree                          Audit/reclaim accumulated git worktrees
update                            Update Hermes to latest
uninstall                         Remove Hermes
```

---

## 10. Other

```
chat                              Interactive chat (default behavior)
console                           Console management surface
setup                             First-run wizard
profile                           Manage profile / personality
project                           Project/workspace helpers
kanban                            Per-session task board
moa                               Mixture-of-agents orchestration surface
acp                               ACP harness bridge
claw                              OpenClaw compatibility layer
dashboard                         Open web Control UI
serve                             Headless backend server entrypoint
desktop / gui                     Desktop app control surfaces
pets                              Desktop pet/companion control surface
completion                        Print shell completion script
version                           Print version
```

---

## Quick Common Recipes

**One-shot prompt (no chat):**
```bash
hermes -z "your prompt" -m openai-codex/gpt-5.5
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
