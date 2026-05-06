---
name: hermes-configure
description: "Configure any aspect of Hermes Agent (Nous Research) via CLI. Channels, models, plugins, gateway, skills, cron, hooks, memory, MCP, and the ACP bridge. Mirrors the openclaw-configure skill structure."
version: 0.3.0
hermes_version: 0.12.0
last_verified: 2026-05-06
---

# Hermes-Configure Skill

Configure any aspect of **Hermes Agent** (by Nous Research) via CLI. This skill is the Hermes counterpart to `openclaw-configure` — same structure, parallel concepts, but real Hermes commands and config paths.

**Trigger on:** "hermes", "hermes setup", "add channel to hermes", "hermes gateway", "hermes model", "switch hermes provider", "hermes skill", "hermes plugin", "hermes cron", "hermes hooks", "hermes doctor", "hermes mcp", "hermes acp", or any Hermes Agent configuration task.

**Reference files** (same directory as this skill):
- `commands.md` — condensed CLI reference, all 39 top-level subcommands
- `cli-reference.md` — full `--help` for the CLI and every nested subcommand

**IMPORTANT — Auto-Update Check:** Before answering any Hermes question, Claude MUST run the **Version Check & Auto-Update Protocol** (see bottom of this file). It compares installed vs latest vs skill versions, asks the user about an update if a newer version exists, and auto-syncs the skill files to match the installed version.

---

## Hermes vs OpenClaw — quick mental map

Hermes and OpenClaw share a lot of surface area (almost certainly forks of the same lineage). When in doubt, **map an OpenClaw concept to its Hermes parallel**:

| Concept | OpenClaw | Hermes |
|---|---|---|
| Main config | `~/.openclaw/openclaw.json` | `~/.hermes/config.yaml` (YAML, not JSON) |
| API keys | inline in JSON / auth-profiles | `~/.hermes/.env` (env-style file) |
| Personality | `~/.openclaw/workspace/SOUL.md` | `~/.hermes/SOUL.md` |
| Sessions | `~/.openclaw/agents/<id>/sessions/` | `~/.hermes/sessions/` |
| Skills | `clawhub install` | bundled + `hermes skills` |
| Multi-agent | `agents add`, bindings | **single-agent design** — no equivalent |
| Importer | `openclaw migrate` (imports Hermes) | `hermes import` (imports Claude Code, etc.) |
| OpenClaw bridge | n/a | `hermes claw` — compatibility layer |
| Service | `openclaw gateway install` (LaunchAgent) | `hermes gateway install` (LaunchAgent/systemd) |

**Key differences from OpenClaw to keep in mind:**
1. **Config is YAML**, not JSON. You can edit `~/.hermes/config.yaml` directly, or use `hermes config` / `hermes config edit`.
2. **API keys live in `~/.hermes/.env`**, not inside the main config. Set them via env-style `KEY=value` lines (or `hermes login` / `hermes auth` for OAuth providers).
3. **No multi-agent**. Hermes is one agent per install. If you need multiple Hermeses, run multiple installs in different `HERMES_HOME` dirs.
4. **No `clawhub` equivalent**. Skills ship bundled and synced from the repo; user-authored skills go in `~/.hermes/skills/`.
5. **Different default model**: `anthropic/claude-opus-4.6` (vs OpenClaw's `openai-codex/gpt-5.5`).

---

## Core Principles

### Config Files
- **Main config:** `~/.hermes/config.yaml` (YAML)
- **API keys / env vars:** `~/.hermes/.env`
- **Personality:** `~/.hermes/SOUL.md`
- **Skills:** `~/.hermes/skills/` (24 categories at install time)
- **Project code:** `~/.hermes/hermes-agent/` (actual Python source — uv-managed venv)
- **Logs:** `~/.hermes/logs/` (incl. `logs/curator/`)
- **Sessions:** `~/.hermes/sessions/`
- **Memories:** `~/.hermes/memories/`
- **Cron jobs:** `~/.hermes/cron/`
- **Hooks:** `~/.hermes/hooks/`

### Gateway Restart
Config changes that affect the messaging gateway (Telegram/Discord/WhatsApp/Slack) require restart:
```bash
hermes gateway restart
```
Or stop+start:
```bash
hermes gateway stop && sleep 2 && hermes gateway start
```
Gateway runs as a launchd service on macOS / systemd on Linux. For foreground (debug, WSL, Termux): `hermes gateway run`.

### Config Editing
```bash
hermes config           # view current config
hermes config edit      # open ~/.hermes/config.yaml in $EDITOR
```
Direct edits work — `~/.hermes/config.yaml` is just YAML. Hermes re-reads it on next process start (or gateway restart for gateway-side changes).

### `.env` for credentials
The default config has env-var fallbacks, e.g.:
```yaml
model:
  provider: "auto"
  base_url: "https://openrouter.ai/api/v1"
  # api_key: "..."  # uncomment to set inline
```
Per the config comments, **environment variables in `.env` take precedence** over inline `config.yaml` values. Set keys via:
```bash
echo 'OPENROUTER_API_KEY=sk-or-...' >> ~/.hermes/.env
echo 'ANTHROPIC_API_KEY=sk-ant-...' >> ~/.hermes/.env
```
Or use the OAuth flows: `hermes login` (Nous portal), `hermes auth` (other providers).

### Interactive vs non-interactive
- **Non-interactive (Claude can run):** `hermes status`, `hermes doctor`, `hermes config` (read), direct `~/.hermes/.env` edits, direct YAML edits, `hermes skills <subcommand>`, `hermes cron list`, `hermes gateway start/stop/restart/status`.
- **Interactive (need TTY — instruct user):** `hermes setup`, `hermes model`, `hermes login`, `hermes auth`, `hermes pairing`, `hermes chat`, `hermes config edit`, `hermes whatsapp` (QR), `hermes slack` (manifest).

---

## Channels (Messaging Gateway)

Hermes ships with **Telegram, Discord, WhatsApp, Slack** as first-class messaging channels, managed by `hermes gateway`.

### Add Channel Workflow (high-level)
```
1. hermes gateway setup            # interactive: pick channel, paste tokens
2. hermes gateway install          # install as LaunchAgent/systemd service
3. hermes gateway start
4. hermes gateway status           # verify probe
5. hermes pairing                  # approve incoming pairing requests
```

### Channel-Specific Notes

**Telegram:** Bot token from @BotFather. Two paths:

1. **Interactive (canonical):** `hermes gateway setup` — prompts for token, allowlist, home channel.
2. **Non-interactive** (verified working 2026-05-06): three keys go directly into `~/.hermes/.env`:
   ```
   TELEGRAM_BOT_TOKEN=<botid>:<secret>          # from @BotFather
   TELEGRAM_ALLOWED_USERS=<your_telegram_uid>   # comma-separated for multiple
   TELEGRAM_HOME_CHANNEL=<your_telegram_uid>    # where heartbeats/announcements go
   ```
   Then `hermes gateway restart`. The bot is **not in `config.yaml`** — it's all env-var driven.

   **Always verify a bot token BEFORE wiring it** — pasting the wrong one wires the wrong bot and produces polling conflicts:
   ```bash
   curl -sS https://api.telegram.org/bot<TOKEN>/getMe | python3 -m json.tool
   ```
   The `username` field in the response confirms which bot the token belongs to.

   **Find your Telegram user ID**: DM `@userinfobot` on Telegram — it instantly replies with your numeric `Id`. (Alternative: `@RawDataBot`.)

   **⚠️ Silent-deny default**: with no `TELEGRAM_ALLOWED_USERS` set, the gateway denies **every** message with no user-facing error. The startup log warns once (`No user allowlists configured. All unauthorized users will be denied`), then is silent. To open the bot to anyone (NOT recommended — every turn runs on your model subscription): `GATEWAY_ALLOW_ALL_USERS=true`.

   **End-to-end smoke test for Telegram channel:**
   ```bash
   # 1. Send any message to your bot from the allowlisted user
   # 2. Watch the gateway log:
   tail -f ~/.hermes/logs/gateway.log
   # Expected sequence:
   #   "inbound message: platform=telegram user=... chat=<your_uid> msg='...'"
   #   "response ready: platform=telegram chat=<your_uid> time=N.Ns api_calls=1 response=N chars"
   #   "[Telegram] Sending response (N chars) to <your_uid>"
   ```

**WhatsApp:** Hermes has a dedicated `hermes whatsapp` subcommand for setup. WhatsApp Web QR-pairing flow.

**Discord:** Bot token from Developer Portal. Set via `hermes gateway setup`.

**Slack:** Hermes has a `hermes slack` subcommand that helps generate the Slack app manifest:
```bash
hermes slack    # outputs manifest JSON to paste into api.slack.com/apps
```

### Channel Commands
```
gateway setup        Configure messaging platforms (interactive)
gateway run          Run gateway in foreground (debug, WSL, Termux)
gateway start        Start installed launchd/systemd service
gateway stop         Stop service
gateway restart      Restart service
gateway status       Show gateway status
gateway install      Install as LaunchAgent/systemd background service
gateway uninstall    Uninstall the service
gateway migrate-legacy   Remove legacy hermes.service units from pre-rename installs
```

### Pairing
```
hermes pairing       Manage pending pair requests from inbound chats
```

---

## Models

Hermes calls the model router `hermes model` (interactive) and supports a wide provider list out of the box.

### Provider list (from default config.yaml)
| Provider key | Auth method | Required env / step |
|---|---|---|
| `auto` | Auto-detect from credentials | (default) |
| `nous` | Nous Portal OAuth | `hermes login` |
| `nous-api` | Nous Portal API key | `NOUS_API_KEY` |
| `openrouter` | API key | `OPENROUTER_API_KEY` or `OPENAI_API_KEY` |
| `anthropic` | Direct API | `ANTHROPIC_API_KEY` |
| `openai-codex` | Codex OAuth | `hermes auth` |
| `copilot` | GitHub Models | `GITHUB_TOKEN` |
| `gemini` | Google AI Studio | `GOOGLE_API_KEY` / `GEMINI_API_KEY` |
| `zai` | z.ai / ZhipuAI GLM | `GLM_API_KEY` |
| `kimi-coding` | Kimi / Moonshot | `KIMI_API_KEY` |
| `minimax` / `minimax-cn` | MiniMax | `MINIMAX_API_KEY` / `MINIMAX_CN_API_KEY` |
| `huggingface` | HF Inference | `HF_TOKEN` |
| `nvidia` | NVIDIA NIM | `NVIDIA_API_KEY` |
| `xiaomi` | Xiaomi MiMo | `XIAOMI_API_KEY` |
| `arcee` | Arcee Trinity | `ARCEEAI_API_KEY` |
| `ollama-cloud` | Ollama Cloud | `OLLAMA_API_KEY` |
| `kilocode` | KiloCode gateway | `KILOCODE_API_KEY` |
| `ai-gateway` | Vercel AI Gateway | `AI_GATEWAY_API_KEY` |
| `lmstudio` | LM Studio (local) | optional `LM_API_KEY`, defaults to `http://127.0.0.1:1234/v1` |
| `custom` | Any OpenAI-compatible (Ollama, vLLM, llama.cpp) | set `base_url` |

Aliases: `ollama`, `vllm`, `llamacpp` all map to `custom`.

### Set the default model

**Interactive (recommended):**
```bash
hermes model    # menu of providers, then list of models
```
The CLI flags on `hermes model` (Nous portal URL, OAuth scope, etc.) are only relevant when picking the Nous provider.

**Non-interactive — edit YAML directly:**
```yaml
# ~/.hermes/config.yaml
model:
  default: "anthropic/claude-opus-4.6"
  provider: "anthropic"   # explicit, instead of "auto"
```
Or override per-call via flags:
```bash
hermes -m anthropic/claude-opus-4.7 chat
hermes --provider openrouter -m openai/gpt-5.5 chat
```
Or env vars: `HERMES_INFERENCE_PROVIDER=...`.

### Fallbacks
```
hermes fallback       Manage fallback providers (tried when primary fails)
```
Use this when the primary provider is rate-limited or down — Hermes will rotate through fallbacks.

### Auth
```
hermes auth                             Pooled credential menu (interactive)
hermes auth {add,list,remove,reset,
             status,logout,spotify}     Non-interactive subcommands
hermes auth add <provider> --type {oauth,api-key} [--api-key <key>]
                                        Add credentials for a provider
hermes auth status <provider>           Show auth state for a SPECIFIC provider
                                        (positional arg required — bare `auth status` errors)
hermes auth list                        List all pooled credentials (no arg)
hermes auth logout <provider>           Clear stored creds for a provider
hermes logout                           Top-level logout (still works)
hermes setup                            Full first-run wizard (interactive)
```

⚠️ **`hermes login` is REMOVED at runtime as of v0.12.0** even though it still appears in `--help`. Running it prints:
> "The 'hermes login' command has been removed. Use 'hermes auth' to manage credentials, 'hermes model' to select a provider, or 'hermes setup' for full setup."

**Codex OAuth specifically:**
```bash
hermes auth add openai-codex --type oauth     # browser opens; OAuth device flow
hermes auth status                             # confirm openai-codex shows ✓
```
**Do NOT** copy `~/.codex/auth.json` to `~/.hermes/auth.json` — Hermes uses an entirely different schema. After a successful OAuth, the real on-disk shape is:
```json
{
  "version": 1,
  "providers": {},
  "credential_pool": {
    "openai-codex": [
      { "id": "...", "label": "...", "auth_type": "oauth",
        "access_token": "...", "refresh_token": "...",
        "base_url": "...", "last_refresh": "...",
        "priority": 0, "source": "...", "request_count": 0 }
    ]
  },
  "updated_at": "..."
}
```
The pool format is per-credential (not `providers.openai-codex.tokens.*` like the reader function suggests — there's a translation layer). Forging this manually is brittle and would race with the Codex CLI's refresher anyway.

**Sharing a ChatGPT sub between OpenClaw + Hermes**: each tool keeps its own auth file (`~/.openclaw/agents/main/agent/auth-profiles.json` vs `~/.hermes/auth.json`). Run `hermes auth add openai-codex --type oauth` once on the Hermes side; OpenClaw stays untouched. They refresh tokens independently — no conflict.

**Running OpenClaw + Hermes side-by-side on one host (verified 2026-05-06)**: this is a supported configuration. Each tool:
- has its own gateway service (`ai.openclaw.gateway` and `ai.hermes.gateway` LaunchAgents)
- uses its own Telegram bot (different `id:secret` pairs — don't share one bot between them, or they'll fight `getUpdates`)
- holds its own Codex OAuth tokens for the same ChatGPT account
- listens on its own port / socket

The **only** shared thing is the upstream model (Codex catalog). When you upgrade the model on one side, do it on both for consistency.

**Other provider examples:**
```bash
hermes auth add anthropic   --type api-key --api-key sk-ant-...
hermes auth add openrouter  --type api-key --api-key sk-or-...
hermes auth add nous        --type oauth      # Nous Portal
```

### Default model (current install)
`anthropic/claude-opus-4.6` (fresh-install default). Confirm with:
```bash
grep '^  default:' ~/.hermes/config.yaml
```

---

## Skills

Hermes ships with **89 bundled skills** out of the box, organized into 24 categories under `~/.hermes/skills/` (apple, autonomous-ai-agents, creative, data-science, devops, diagramming, dogfood, domain, email, gaming, …).

### Commands
```
skills                Manage skills (list, sync, etc. — see hermes skills --help)
curator               Skill curation tooling (Hermes-specific — see hermes curator --help)
```

The `curator` command is the closest Hermes thing to ClawHub — a skill curation/management tool. It does NOT expose a public registry the way ClawHub does (as of v0.12.0), but it manages the local skill collection and may sync from upstream sources.

### Skill structure
A Hermes skill is a folder under `~/.hermes/skills/<category>/<skill-name>/` with a `SKILL.md` (same convention as Claude / OpenClaw). After adding/changing a skill:
```bash
hermes gateway restart   # restart so the agent picks up the new skill
```

### Optional skills
The repo also ships an `optional-skills/` directory inside `~/.hermes/hermes-agent/optional-skills/` — heavier skills that aren't installed by default. Inspect with:
```bash
ls ~/.hermes/hermes-agent/optional-skills/
```

---

## Plugins

Hermes has its own plugin system at `~/.hermes/hermes-agent/plugins/` (separate from skills). Manage via:
```
plugins               List/install/uninstall Hermes plugins (see hermes plugins --help)
```

Plugins are heavier than skills — they're Python modules that can register tools, channel runtimes, hooks, etc. Skills are markdown-instruction-based; plugins are code.

---

## Gateway

```
gateway run             Run in foreground (good for debugging / WSL / Termux)
gateway start           Start the launchd/systemd background service
gateway stop            Stop service
gateway restart         Restart service
gateway status          Show status
gateway install         Install as background service
gateway uninstall       Uninstall service
gateway setup           Interactive: configure messaging platforms
gateway migrate-legacy  Remove legacy hermes.service units (pre-rename installs)
```

The gateway is the **always-on process** that listens for inbound channel messages, runs cron, and routes to the agent. It's separate from the `hermes chat` REPL.

### Foreground vs service
- `hermes gateway run` — foreground, you watch logs scroll by, kills on Ctrl-C. Best for debugging, or for environments without launchd/systemd (Termux, Docker, WSL).
- `hermes gateway install` + `hermes gateway start` — background service, persists across reboot. Default for macOS/Linux.

### Status check
```bash
hermes gateway status
hermes status   # full system status (gateway + components)
hermes doctor   # diagnostics + auto-fix
```

---

## Cron

```
cron                  Manage scheduled jobs (see hermes cron --help for subcommands)
```
Cron job state lives at `~/.hermes/cron/`. Schedule recurring agent turns, message fan-outs, etc. Subcommands mirror typical cron CLIs (`list`, `add`, `remove`, `enable/disable`, `run`, etc.) — confirm with `hermes cron --help`.

---

## Hooks

```
hooks                 Manage shell/lifecycle hooks
```
Hermes hooks live at `~/.hermes/hooks/`. Auto-approve unseen shell hooks via `--accept-hooks` flag or the `HERMES_ACCEPT_HOOKS=1` env var (or `hooks_auto_accept: true` in YAML).

---

## Memory

```
memory                Manage long-term memory store
```
Memory state at `~/.hermes/memories/`. Hermes' "self-improving" claim — the agent searches its own past conversations and builds a model of you across sessions. Inspect/curate with `hermes memory`.

Bonus: `hermes insights` — likely surfaces the patterns Hermes has learned about you across sessions. Worth running periodically to see what's accumulated.

---

## MCP (Model Context Protocol)

```
mcp                   Manage MCP servers
```
Add MCP servers that Hermes can call as external tool sources. Subcommands likely mirror Claude/OpenClaw MCP patterns (`list`, `add`, `remove`, `enable`, `disable`).

---

## ACP (Agent Control Protocol)

```
acp                   ACP bridge / harness integration
```
Hermes has an `acp_adapter/` and `acp_registry/` in its source tree, parallel to OpenClaw's ACP support. Use this for spawning Hermes from other agent harnesses (Codex, Claude Code, etc.).

---

## Sessions

```
sessions              Manage chat sessions
```
Sessions stored as files in `~/.hermes/sessions/`. Use `hermes --resume <session>` or `hermes --continue [name]` to pick up where you left off.

---

## Status / Diagnostics

```
status                Show status of all components
doctor                Health checks and auto-fix
debug                 Lower-level debug helpers
dump                  Dump diagnostic info (config, state, etc.)
logs                  View Hermes logs (~/.hermes/logs/)
```

Run `hermes doctor` after upgrades or weird behavior — it's the equivalent of `openclaw doctor`.

---

## Backup / Import / Update / Uninstall

```
backup                Local backup of Hermes state (~/.hermes/)
import                Import config/state from other tools (Claude Code, etc.)
update                Update Hermes Agent to latest version
uninstall             Remove Hermes
```

`hermes import` is the parallel to `openclaw migrate`. It can pull settings/credentials/skills/MCP servers from Claude Code, Claude Desktop, and other agent CLIs.

---

## Other Subcommands

| Command | Purpose |
|---|---|
| `chat` | Interactive chat (default if you just type `hermes`) |
| `setup` | First-run wizard (combo of `model` + `tools` + channel setup) |
| `whatsapp` | WhatsApp-specific helpers (QR pairing, etc.) |
| `slack` | Slack manifest generator + Slack helpers |
| `webhook` | Configure inbound webhooks |
| `kanban` | Per-session task board |
| `tools` | Enable/disable agent tools |
| `config` | View/edit YAML config |
| `pairing` | Approve inbound pairing requests |
| `claw` | OpenClaw compatibility layer (interesting!) |
| `version` | Print version |
| `completion` | Shell completion script |
| `dashboard` | Open the web dashboard / Control UI |
| `acp` | ACP harness bridge |
| `profile` | Manage Hermes profile / personality |

---

## Top-Level Flags (apply to most subcommands)

```
-z PROMPT              One-shot prompt (non-interactive turn)
-m MODEL               Override model for this run
--provider PROVIDER    Override provider for this run
-t TOOLSETS            Override which toolsets are active
--resume SESSION       Resume an existing session by ID
--continue [NAME]      Continue most recent session (or named)
--worktree             Use a git worktree for the run
--accept-hooks         Auto-approve unseen shell hooks (no TTY)
--skills SKILLS        Override which skills are loaded
--yolo                 Skip prompts/confirmations
--pass-session-id      Pass the session ID through
--ignore-user-config   Ignore user-level config overrides
--ignore-rules         Ignore custom rules
--tui                  Force the TUI mode
--dev                  Dev mode
```

Quick one-shot example:
```bash
hermes -z "summarize the last commit" -m anthropic/claude-opus-4.6
```

---

## Common Workflows

### First-time setup (after install)
```bash
hermes setup           # full wizard: model + tools + channels
# or piecemeal:
hermes model           # pick provider + default model
hermes auth            # add API keys / OAuth tokens
hermes tools           # toggle which tools are enabled
hermes gateway setup   # configure Telegram/Discord/Slack/WhatsApp
hermes gateway install # install as service
hermes gateway start   # start it
hermes status          # verify everything is up
```

### Codex OAuth jumpstart with `openai-codex/gpt-5.5` ✓ verified end-to-end (2026-05-06, Hermes v0.12.0)

The fastest non-interactive-as-much-as-possible path to a Hermes that mirrors OpenClaw's `main` agent (ChatGPT/Codex subscription, gpt-5.5). **Tested and working** — the smoke-test below returned `PONG from gpt-5.5` from a live model turn.

```bash
# 1. Back up current config (in case of regret)
cp ~/.hermes/config.yaml ~/.hermes/config.yaml.bak

# 2. Edit YAML directly (no TTY needed) — sets default model + provider
python3 -c "
import re, pathlib
p = pathlib.Path.home() / '.hermes/config.yaml'
t = p.read_text()
t = re.sub(r'^(  default: \").*?\"', r'\1openai-codex/gpt-5.5\"', t, count=1, flags=re.M)
t = re.sub(r'^(  provider: \").*?\"', r'\1openai-codex\"', t, count=1, flags=re.M)
p.write_text(t)
"

# 3. Install + start gateway (auth not required for gateway lifecycle itself)
hermes gateway install
hermes gateway start

# 4. ⚠️ INTERACTIVE — must run in a real terminal (browser opens for OAuth device flow)
hermes auth add openai-codex --type oauth

# 5. Verify wiring
hermes auth status openai-codex      # → "openai-codex: logged in"
hermes status | grep -A1 "OpenAI Codex"  # → ✓ logged in

# 6. Smoke test — actually invoke the model
hermes -z "respond with EXACTLY one line: PONG from \$MODEL_NAME (replace with your actual model id)"
# Expected: "PONG from gpt-5.5"
```

**What ends up where:**
- `~/.hermes/config.yaml`: `model.default = openai-codex/gpt-5.5`, `model.provider = openai-codex`
- `~/.hermes/auth.json`: tokens written under `credential_pool.openai-codex[]` (separate from Codex CLI's `~/.codex/auth.json` — the two refresh independently)
- `~/Library/LaunchAgents/ai.hermes.gateway.plist`: gateway service plist

**Sharing the ChatGPT subscription with OpenClaw**: both tools maintain their own auth files but can hold valid OAuth tokens for the same Codex account simultaneously. No conflict — they refresh on independent schedules.

**Picking a different/newer model from Codex catalog** (e.g. when gpt-5.5 → gpt-5.6 lands):
```bash
# Replace the model id in step 2's regex, OR use sed:
sed -i.bak 's|^  default: ".*"|  default: "openai-codex/gpt-5.6"|' ~/.hermes/config.yaml
hermes gateway restart
hermes -z "what model are you?"   # confirm the new id
```
You can also list what Codex OAuth currently exposes via `hermes model` (interactive) — the menu shows the live catalog.

### Add a Telegram bot — non-interactive (verified 2026-05-06)
```bash
# 0. Get bot token from @BotFather, get user id from @userinfobot, then:

# 1. Verify the token is for the bot you THINK it is
curl -sS "https://api.telegram.org/bot<TOKEN>/getMe" | python3 -m json.tool
# → confirm result.username matches your bot

# 2. Write to .env
python3 <<EOF
import re, pathlib, os, stat
p = pathlib.Path.home() / '.hermes/.env'
text = p.read_text()
keys = ('TELEGRAM_BOT_TOKEN', 'TELEGRAM_ALLOWED_USERS', 'TELEGRAM_HOME_CHANNEL')
lines = [l for l in text.splitlines() if not any(re.match(rf'^\s*#?\s*{k}\s*=', l) for k in keys)]
lines += [
    'TELEGRAM_BOT_TOKEN=<TOKEN>',
    'TELEGRAM_ALLOWED_USERS=<your_uid>',
    'TELEGRAM_HOME_CHANNEL=<your_uid>',
]
p.write_text('\n'.join(lines) + '\n')
os.chmod(p, stat.S_IRUSR | stat.S_IWUSR)   # 0600
EOF

# 3. Restart and confirm
hermes gateway restart
sleep 5
tail -20 ~/.hermes/logs/gateway.log | grep -iE "telegram|allowlist"
# Should see "✓ telegram connected" and NO "No user allowlists configured" warning

# 4. DM the bot from your allowlisted account to smoke-test
```

### Add a Telegram bot — interactive (alternative)
```bash
hermes gateway setup    # prompts for token, allowlist, home channel
hermes gateway restart
```

### Switch default model (CLI-only)
```bash
hermes model            # interactive
# or:
sed -i.bak 's|^  default: ".*"|  default: "anthropic/claude-opus-4.7"|' ~/.hermes/config.yaml
hermes gateway restart
hermes -z "what model are you?" --json    # verify
```

### Change provider (e.g. switch to OpenRouter)
```bash
echo 'OPENROUTER_API_KEY=sk-or-...' >> ~/.hermes/.env
# Then either: hermes model --provider openrouter
# Or edit YAML: model.provider: "openrouter"
hermes gateway restart
```

### Upgrade Hermes
```bash
hermes update    # in-place upgrade (reuses ~/.hermes/.env and config)
hermes doctor    # run health checks after upgrade
```

### Backup state before risky changes
```bash
hermes backup    # snapshot ~/.hermes/
```

### Run gateway in foreground for debugging
```bash
hermes gateway stop
hermes gateway run    # foreground; Ctrl-C to stop
```

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `command not found: hermes` | `~/.local/bin` not on PATH | Add to PATH via shell rc, or run `~/.local/bin/hermes` directly |
| `hermes setup` skipped during install | No TTY during installer | Run `hermes setup` manually in a real terminal |
| `hermes login` exits with "command has been removed" | `hermes login` is a removed-but-still-in-help artifact in v0.12.0 | Use `hermes auth add <provider> --type oauth` instead (or `hermes model` / `hermes setup` for interactive flows). |
| Codex OAuth: copying `~/.codex/auth.json` → `~/.hermes/auth.json` rejected as "No Codex credentials stored" | Hermes wraps tokens under `providers.openai-codex.tokens.{access,refresh}_token` in its auth store — flat Codex CLI schema is incompatible | Run `hermes auth add openai-codex --type oauth` (proper OAuth device flow). Don't forge auth.json — it races with Codex CLI's refresher. |
| Want OpenClaw and Hermes to share a ChatGPT subscription | They each maintain a separate `auth.json`, but both can hold valid OAuth tokens for the same Codex account | Run `hermes auth add openai-codex --type oauth` once on Hermes side; OpenClaw stays as-is. They refresh independently. |
| `hermes status` shows wrong "Provider" line | `model.provider: "auto"` picks first provider with any creds (e.g. NVIDIA NIM if that's all you have) | Set `model.provider` explicitly in `~/.hermes/config.yaml` to force the right provider |
| `--accept-hooks` warning on every run | Unseen shell hooks need approval | Run interactively once to approve, or set `HERMES_ACCEPT_HOOKS=1` |
| Gateway starts but no inbound messages | Channel tokens not set / dmPolicy too strict | `hermes gateway setup` to reconfigure; check `hermes pairing` for queued handshakes |
| Telegram bot connects (`✓ telegram connected`) but every message gets no reply, no user-facing error | **Silent deny** — default behavior with no allowlist configured. Look for `No user allowlists configured` warning at gateway startup. | Set `TELEGRAM_ALLOWED_USERS=<uid>` in `~/.hermes/.env` (find your uid via `@userinfobot` in Telegram), then `hermes gateway restart` |
| Telegram log spams `Conflict: terminated by other getUpdates request; make sure that only one bot instance is running` | Two processes polling the same bot id (e.g. quickly switched tokens; another Hermes instance; OpenClaw + Hermes both pointed at the same bot) | `pgrep -fl "gateway run"` — kill duplicates. If you swapped tokens recently, wait ~30s for the old long-poll session to die. Confirm only one bot per token via `curl .../getMe` for each token. |
| Wired the wrong bot — config says one bot, logs/replies look like a different bot | Token belonged to a different bot — visually similar token (same digit length, similar prefix), different `id:secret` pair | **Always** `curl https://api.telegram.org/bot<TOKEN>/getMe` BEFORE wiring. The `result.username` field confirms which bot the token authenticates. |
| Wrong model used despite `--model` flag | Provider for that model isn't configured | Check `~/.hermes/.env` has the right `*_API_KEY`; run `hermes auth` for OAuth providers |
| `hermes update` fails or partial | Was running gateway, files in use | `hermes gateway stop && hermes update && hermes gateway start` |
| `hermes claw` errors / unclear | OpenClaw compatibility surface — depends on local OpenClaw install | Run `hermes claw --help` for current scope; not all OpenClaw commands are bridged |
| `hermes import` doesn't see Claude Code | Importer scans known paths; non-default install missed | Pass explicit path: `hermes import --help` to see flags |

(This table will grow as the skill is exercised — see Self-Evolution Protocol below.)

---

## Self-Evolution Protocol

After completing any Hermes task that involved:
1. A new workflow not documented above
2. A gotcha or failure not in the troubleshooting table
3. A new provider, channel, plugin, or skill configuration
4. A correction to existing information
5. A version-specific behavior change

**Claude MUST update this SKILL.md** at `~/.claude/skills/hermes-configure/SKILL.md`:
- Add the workflow/recipe to the appropriate section
- Add new gotchas to the troubleshooting table
- Update provider/channel sections if Hermes adds support
- Bump the version footer if behavior depends on a specific Hermes release
- Keep concise and well-organized

This skill grows with every use. Never let hard-won knowledge be lost.

---

## Version Check & Auto-Update Protocol

**This skill was last updated for:** `Hermes v0.12.0 (build 2026.4.30)`

### Version Check (run at start of every Hermes session)

Before answering any Hermes question, Claude SHOULD run this in parallel with the user's actual task (lightweight, fast):

```bash
# Installed version
hermes --version 2>&1 | head -1
```

Hermes does not (as of v0.12.0) ship an `update status --json` equivalent of OpenClaw. To check for upstream updates:

```bash
# Run the bundled updater in dry/check mode if available
hermes update --help 2>&1 | head -10
# If a --check flag exists, use it; else just compare against upstream:
git -C ~/.hermes/hermes-agent log -1 --format="%H %s" 2>/dev/null
git -C ~/.hermes/hermes-agent fetch origin --quiet 2>/dev/null
git -C ~/.hermes/hermes-agent log HEAD..origin/main --oneline 2>/dev/null | head -5
```

Extract:
- `INSTALLED` — `hermes --version` output (e.g. `0.12.0 (2026.4.30)`)
- `LATEST` — most recent commit on `origin/main` of the cloned repo
- `SKILL_VERSION` — the version line above

### Decision matrix

| Comparison | Action |
|---|---|
| `INSTALLED` == `SKILL_VERSION`, no upstream commits ahead | All in sync. Proceed. |
| Upstream commits ahead of `INSTALLED` | Ask the user: "Hermes commits available upstream — want me to run `hermes update`?" |
| `INSTALLED` > `SKILL_VERSION` (e.g. user updated outside this session) | Trigger **Skill Refresh** automatically. |

### Skill Refresh Procedure

When the local Hermes version is newer than `SKILL_VERSION`:

1. **Notify the user**: "Syncing hermes-configure skill to match Hermes v<X.Y.Z>..."

2. **Regenerate `cli-reference.md`:**
   ```bash
   HERMES=$(which hermes)
   {
     echo "# Hermes CLI Full Reference"
     echo "_Auto-generated $(date '+%Y-%m-%d') for $($HERMES --version 2>&1 | head -1)_"
     echo
     echo "## hermes (top-level)"
     echo '```'
     $HERMES --help 2>&1
     echo '```'
   } > ~/.claude/skills/hermes-configure/cli-reference.md

   SUBS=$($HERMES --help 2>&1 | python3 -c "
   import sys, re
   m = re.search(r'\{([^}]+)\}', sys.stdin.read())
   print('\n'.join(s.strip() for s in m.group(1).split(',') if s.strip()) if m else '')
   ")
   for cmd in $SUBS; do
     {
       echo
       echo "## hermes $cmd"
       echo '```'
       $HERMES $cmd --help 2>&1
       echo '```'
     } >> ~/.claude/skills/hermes-configure/cli-reference.md

     NESTED=$($HERMES $cmd --help 2>&1 | python3 -c "
   import sys, re
   m = re.search(r'\{([^}]+)\}', sys.stdin.read())
   print('\n'.join(s.strip() for s in m.group(1).split(',') if s.strip()) if m else '')
   ")
     for sub in $NESTED; do
       {
         echo
         echo "### hermes $cmd $sub"
         echo '```'
         $HERMES $cmd $sub --help 2>&1
         echo '```'
       } >> ~/.claude/skills/hermes-configure/cli-reference.md
     done
   done
   ```

3. **Read the project changelog** for delta between old and new:
   ```bash
   ls ~/.hermes/hermes-agent/CHANGELOG* ~/.hermes/hermes-agent/changelog* 2>/dev/null
   git -C ~/.hermes/hermes-agent log --oneline --since="last skill update date" 2>/dev/null | head -50
   ```

4. **Update `commands.md`:** version header and any new/removed commands.

5. **Update this SKILL.md:**
   - Bump the `hermes_version` line in the YAML frontmatter
   - Bump the `**This skill was last updated for:**` line
   - Add a "What's new in vX.Y.Z" section if there are notable changes
   - Add new troubleshooting rows for any new gotchas

6. **Verify** by re-running `hermes --version` and confirming the skill marker matches.

7. **Confirm to user:** "Skill synced to Hermes v<X.Y.Z>."

---

## Don'ts (mirror of openclaw-configure conventions)

1. Don't pretend Hermes commands work like OpenClaw without verifying. The surfaces look similar but have diverged — some things differ subtly (config format, single-agent vs multi-agent, env-var precedence).
2. Don't edit `~/.hermes/.env` to put a key in plaintext if there's an OAuth flow available — prefer `hermes login` / `hermes auth`.
3. Don't run `hermes uninstall` to "fix" a config issue — `hermes doctor`, `hermes backup`, then targeted edits.
4. Don't manually edit files inside `~/.hermes/hermes-agent/` (the project source). It's an `uv`-managed venv and edits will be wiped on update. User customization belongs in `~/.hermes/` root.
5. Don't assume `hermes claw` is a complete OpenClaw bridge — verify per-command before relying on it.
