---
name: hermes-configure
description: "Configure any aspect of Hermes Agent (Nous Research) via CLI. Channels, models, plugins, gateway, skills, cron, hooks, memory, MCP, and the ACP bridge. Mirrors the openclaw-configure skill structure."
version: 0.21.3
hermes_version: 0.21.3
last_verified: 2026-09-15
---

# Hermes-Configure Skill

Configure any aspect of **Hermes Agent** (by Nous Research) via CLI. This skill is the Hermes counterpart to `openclaw-configure` — same structure, parallel concepts, but real Hermes commands and config paths.

**Trigger on:** "hermes", "hermes setup", "add channel to hermes", "hermes gateway", "hermes model", "switch hermes provider", "hermes skill", "hermes plugin", "hermes cron", "hermes hooks", "hermes doctor", "hermes mcp", "hermes acp", or any Hermes Agent configuration task.

**Reference files** (same directory as this skill):
- `commands.md` — condensed CLI reference for the current top-level command surface
- `cli-reference.md` — full `--help` for the CLI and every nested subcommand (depth-limited recursive capture)
- `scripts/regen-cli-reference.py` — depth-safe reference generator; writes beside this skill, preserves the existing reference on failure, and aborts above 5 MB

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
| Skill registry | `clawhub install` | `hermes skills install` (browses skills.sh / GitHub / ClawHub / well-known endpoints — full registry surface, not just bundled) |
| Multi-agent | `agents add`, bindings | Named profiles via `hermes profile`; one agent identity per profile |
| Importer | `openclaw migrate` (imports Hermes) | `hermes import` (imports Claude Code, etc.) |
| OpenClaw bridge | n/a | `hermes claw` — compatibility layer |
| Service | `openclaw gateway install` (LaunchAgent) | `hermes gateway install` (LaunchAgent/systemd) |

**Key differences from OpenClaw to keep in mind:**
1. **Config is YAML**, not JSON. You can edit `~/.hermes/config.yaml` directly, or use `hermes config` / `hermes config edit`.
2. **API keys live in `~/.hermes/.env`**, not inside the main config. Set them via env-style `KEY=value` lines (or `hermes login` / `hermes auth` for OAuth providers).
3. **Named profiles**. Current Hermes supports `hermes profile create/list` and temporary `hermes --profile <name> ...` selection. Each profile has its own model, personality and state; do not assume OpenClaw agent commands exist.
4. **`hermes skills` IS the ClawHub equivalent** — `browse / search / install / inspect / audit / update / uninstall / publish / tap` against skills.sh, GitHub, ClawHub, and other well-known agent skill registries. Plus `hermes curator` for pruning agent-created skills.
5. **Different default model**: `anthropic/claude-opus-4.6` (vs OpenClaw's `openai-codex/gpt-5.5`).

---

## Core Principles

### Config Files
- **Main config:** `~/.hermes/config.yaml` (YAML)
- **API keys / env vars:** `~/.hermes/.env`
- **Personality:** `~/.hermes/SOUL.md`
- **Skills:** `~/.hermes/skills/` (58 bundled skills across 12 categories on 2026-09-15)
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
hermes auth {add,list,remove,reset,priority,refresh,
             status,logout,upgrade,spotify}     Non-interactive subcommands
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
hermes auth status openai-codex                 # inspect Codex auth state
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

### Named profile with OpenAI OAuth (verified 2026-09-15, v0.21.3)

`hermes profile create tia --no-alias --description "Tia desktop companion"` creates an isolated personality/model/state. Use `hermes --profile tia acp` for a profile-specific ACP child without changing the sticky default. `hermes profile list` is human-readable; there is no `--json` flag in this build.

**First OAuth credential gotcha:** on an empty named profile, `auth add openai-codex --type oauth` may say Added but persist no credential. In upstream a982d2c8, the empty profile follows the borrowed-root update-only pool path, discarding the new row. Supported workaround: run `hermes --profile default auth add openai-codex --type oauth`, then use the native global credential fallback. Do not edit source or forge token files. Verify with `hermes --profile tia auth status openai-codex` and an actual model/tool request.

Set the selected profile’s model explicitly:
```sh
hermes --profile tia config set model.provider openai-codex
hermes --profile tia config set model.default gpt-5.6-sol
hermes --profile tia config set model.base_url https://chatgpt.com/backend-api/codex
```
ACP then advertised `openai-codex:gpt-5.6-sol`; a live Python create/readback test succeeded. Authentication and sessions remain managed by Hermes. Sol access still depends on the account.

### Default model (current install)
`gpt-5.6-sol`, provider `openai-codex`, configured through OpenAI OAuth on 2026-09-15. The `tia` profile uses the same model and Hermes’s native shared-credential fallback. Confirm locally with:
```bash
grep '^  default:' ~/.hermes/config.yaml
```

---

## Skills

This fresh install seeded **58 bundled skills** across 12 categories under `~/.hermes/skills/` (apple, autonomous-ai-agents, creative, data-science, devops, diagramming, dogfood, domain, email, gaming, …).

`hermes skills` is a **full registry surface** — the closest Hermes equivalent to ClawHub. It can search, install, inspect, audit, update, uninstall, publish, and snapshot skills from multiple registries (skills.sh, well-known agent skill endpoints, GitHub, ClawHub).

### Commands

```
skills browse         Browse all available skills (paginated)
skills search         Search skill registries
skills install        Install a skill from a registry
skills inspect        Preview a skill without installing
skills list           List installed skills
skills check          Check installed hub skills for updates
skills update         Update installed hub skills
skills audit          Re-scan installed hub skills (refresh local index)
skills uninstall      Remove a hub-installed skill
skills reset          Reset a bundled skill — clears 'user-modified' tracking so updates work again
skills publish        Publish a skill to a registry
skills snapshot       Export/import skill configurations
skills tap            Manage skill sources (add/remove registries)
skills config         Interactive enable/disable per-skill
```

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

### Curator (auxiliary-model background reviewer)

`hermes curator` is **not the same as `hermes skills`**. It's an auxiliary-model background task that periodically reviews **agent-created** skills, prunes stale ones, consolidates overlaps, and archives obsolete skills. **Bundled and hub-installed skills are never touched.** Archives are recoverable; auto-deletion never happens.

```
curator status        Show curator status and skill stats
curator run           Trigger a curator review now
curator pause         Pause the curator until resumed
curator resume        Resume a paused curator
curator pin           Pin a skill so the curator never auto-transitions it
curator unpin         Unpin a skill
curator restore       Restore an archived skill
curator archive       Manually archive a skill (move to .archive/, excluded from prompt)
curator prune         Bulk-archive agent-created skills idle for >= N days (config default 30)
curator backup        Take a manual tar.gz snapshot of ~/.hermes/skills/
curator rollback      Roll back the most recent curator action
```

(Curator runs auto-backup before every real run — no surprise data loss.)

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
hermes doctor   # diagnostics; --fix applies supported repairs
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
memory setup          Interactive provider selection and configuration
memory status         Show current memory provider config
memory off            Disable external provider (built-in only)
memory reset          Erase all built-in memory (MEMORY.md and USER.md)
```

**Two layers of memory**, both can be active at once:

1. **Built-in (always on)**: `MEMORY.md` (agent-curated cross-session facts) and `USER.md` (model-of-you) live in `~/.hermes/memories/`. Edit by hand or let the agent maintain them.
2. **External provider (optional, one at a time)**: Hermes integrates with **honcho, openviking, mem0, hindsight, holographic, retaindb, byterover** as pluggable memory backends. Switch via `hermes memory setup`.

Bonus: `hermes insights` surfaces the patterns Hermes has accumulated about you across sessions. Worth running periodically to see what's been learned.

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
doctor                Health checks (--fix applies supported repairs)
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
| `console` *(new by v0.18)* | Console management surface. Verify current flags with `hermes console --help`. |
| `setup` | First-run wizard (combo of `model` + `tools` + channel setup) |
| `whatsapp` | WhatsApp-specific helpers (QR pairing, etc.) |
| `slack` | Slack manifest generator + Slack helpers |
| `webhook` | Configure inbound webhooks |
| `kanban` | Per-session task board |
| `tools` | Enable/disable agent tools |
| `config` | View/edit YAML config |
| `pairing` | Approve inbound pairing requests |
| `claw` | OpenClaw compatibility layer (interesting!) |
| `--version` / `-V` | Print version; global flag, not a subcommand. |
| `completion` | Shell completion script |
| `dashboard` | Open the web dashboard / Control UI |
| `acp` | ACP harness bridge |
| `profile` | Manage Hermes profile / personality |
| `proxy` | Local HTTP server forwarding OpenAI-compatible requests to an OAuth provider (e.g. Nous Portal). External apps point at the proxy with any bearer token; proxy attaches real creds. Subs: `start`, `status`, `providers`. |
| `lsp` | LSP layer that powers post-write semantic diagnostics in `write_file`/`patch`. Subs: `status`, `list`, `install`, `install-all`, `restart`, `which`. |
| `send` | Pipe text from any shell script to any messaging platform Hermes is configured for. No LLM, no agent loop, no running gateway required for bot-token platforms. `hermes send -t telegram:<chat_id> "msg"` or pipe via stdin. |
| `checkpoints` | Manage the filesystem checkpoint store — shadow git repo snapshotting working dirs before `write_file`/`patch`/`terminal` calls. Subs: `status`, `prune`, `clear`, `clear-legacy`. |
| `bundles` | Skill bundles — load several skills under one slash command. `/<bundle>` from CLI or gateway loads every referenced skill. Subs: `list`, `show`, `create`, `delete`, `reload`. |
| `computer-use` | Install/check the `cua-driver` binary used by the `computer_use` toolset. macOS-only. Subs: `install`, `status`. |

| `moa` *(new by v0.17)* | Mixture-of-agents orchestration surface. Verify current flags with `hermes moa --help`. |
| `secrets` *(new by v0.17)* | Secret/config key management surface. Verify current flags with `hermes secrets --help`. |
| `migrate` *(new by v0.17)* | Migration helpers distinct from `import`. Verify current flags with `hermes migrate --help`. |
| `whatsapp-cloud` *(new by v0.17)* | WhatsApp Cloud API helpers, separate from the WhatsApp Web helper. |
| `portal` *(new by v0.17)* | Nous Portal auth/status helpers replacing older top-level login assumptions. |
| `project` *(new by v0.17)* | Project/workspace helpers exposed as a top-level CLI domain. |
| `pets` *(new by v0.17)* | Desktop pet/companion control surface. |
| `serve` *(new by v0.17)* | Headless backend server entrypoint; desktop no longer has to launch the dashboard. |
| `desktop` / `gui` *(new by v0.17)* | Desktop app control surfaces. |
| `prompt-size` *(new by v0.17)* | Prompt/context sizing diagnostics. |
| `journey` *(new by v0.18)* | Cross-session journey/history surface. `learning` and `memory-graph` are aliases on the same timeline surface by v0.20.5. |
| `worktree` *(new by v0.20)* | Audit and reclaim accumulated git worktrees and merged branches. |
| `egress` *(new by v0.20)* | Manage the iron-proxy credential-injection firewall. |
| `pause` / `resume` *(new by v0.20)* | Emergency-stop or resume cron/kanban dispatch and new gateway turns. |
| `sync` *(new by v0.20)* | Sync skills across devices and teams. |
| `peer` *(new by v0.20)* | Bot-to-bot DMs across Hermes gateways. |
| `verify` *(new by v0.20)* | Detect a project's run recipe and execute a smoke test. |
| `approvals` *(new by v0.20)* | Mine approval history into allowlist proposals. |
| `import-agent` *(new by v0.20)* | Import Claude Code or Codex CLI setup; `import` now restores Hermes backups. |
| `skin` *(new by v0.20)* | List, switch, and tweak UI skins. |
| `monitoring` *(new by v0.20)* | Inspect gateway health and export diagnostics. |
| `browser` *(new by v0.21.3)* | Real-profile browsing helpers. `close-profile` closes the browser holding a profile; run only with explicit user consent because unsaved tabs can be lost. |
| `vault` *(new by v0.21.3)* | Local encrypted autofill vault. Subs: `add`, `list`, `rm`, `sources`; passwords are injected server-side, while the agent sees metadata. |

---

## What's new in v0.21.3 (vs v0.20.5)

_Fresh install verified locally on 2026-09-15. Hermes had been removed from this Mac. Installed `Hermes Agent v0.21.3 (2026.9.14) · upstream a982d2c8` using the official installer._

### Local Install Results
- **Installer:** downloaded and inspected `https://hermes-agent.nousresearch.com/install.sh`, then ran the saved script with `--skip-setup --non-interactive --skip-computer-use < /dev/null`. No Homebrew packages needed.
- **Runtime:** existing Git, Python, uv, ripgrep, ffmpeg, and compiler were present. Installer added managed uv `0.12.13`, reused Python `3.11.16`, and installed managed Node `26.8.2` / npm `11.19.1` because existing npm `11.12.1` cannot honor the repository's release-age exemptions. Python dependencies installed from `uv.lock` with hash verification. SQLite is `3.53.1`.
- **Latest-tip refresh:** upstream changed during verification; `hermes update --yes --no-backup < /dev/null` moved the initial `2179a279` install to `a982d2c8` and rebuilt the web UI. Update plan confirmed no running Hermes services. The updater preserved the initial HEAD at `refs/hermes-update-backups/orphan-main-20260915-022307-2179a279ae04` after a shallow background fetch made ancestry unavailable; no backup zip was created.
- **Upstream:** fetched history back to 2026-08-20; **10,400 commits** since `14c59f0b`. Installed HEAD matches `origin/main` (0 ahead / 0 behind). No release CHANGELOG found; the two changelog-named files implement desktop commit display/tests.
- **Config/doctor:** `hermes config migrate < /dev/null` moved fresh template schema **0 → 45**. Final `hermes config check` exited 0 with `Config version: 45 ✓`. Migration emitted Teams/Google Chat unknown-toolset warnings; final config check did not repeat them. `hermes doctor --fix` installed the missing macOS TCC anchor and warmed the agent-browser cache. Final doctor exited 0, with three outstanding issues: `Browser tools (agent-browser) has 2 npm vulnerabilities`; `web workspace has 6 npm vulnerabilities`; `Run 'hermes setup' to configure missing API keys for full tool access`. Optional auth/integration warnings remain.
- **Web/browser:** installer provisioned Chromium and Browser Use CLI. `env NODE_ENV=development npm --workspace web run build` passed and wrote `hermes_cli/web_dist`; no missing-dev-dependency workaround was needed. Vite warned about future native config loading and `__dirname`.
- **Skills/tools:** 58 bundled skills seeded; `hermes skills check` returned `No hub-installed skills to check.` and update returned `No updates available.` No security override. `cua-driver: not installed`; LSP enabled with no active clients, clangd installed, remaining listed servers missing/manual-only. `hermes postinstall --help` failed with `invalid choice: 'postinstall'`; skipped.
- **Not yet configured:** template model `anthropic/claude-opus-4.6`, provider `auto`; no nonempty credential values in `.env`, no OAuth performed, no model smoke test, no gateway installation/start. Gateway status: `✗ Gateway is not running`. Final status exits 0 without the earlier shutdown `RecursionError` (below).
- **CLI reference:** regenerated with a command index, depth limit 4, visited paths, 20-second help timeouts, and a 5 MB abort guard. Parser verified against the live argparse tree without mismatches; **310,133 bytes, 481 command nodes**, actual maximum depth 3.

### Notable CLI Additions Observed
- **New top-level commands:** `browser` (`close-profile`, requires explicit consent) and `vault` (`add`, `list`, `rm`, `sources`). No top-level commands removed or global flags added/removed versus the old live v0.20.5 reference. Stale documented `version` and `postinstall` entries were corrected; they were already absent from that old top-level help.
- **Auth/skills:** current help includes `auth priority`, `auth refresh`, and `auth upgrade`; skills help includes trust/untrust, modified-skill inspection, opt-in/out, and official-skill repair. These commands were inspected through `--help`, not executed.
- **Curator:** `curator prune --help` now confirms a config default of 30 idle days.
- **Commit-subject review (not live feature tests):** cron delivery/ticker recovery; curator rollback and retention; Codex refresh-store handling; gateway profile isolation/multiplex migration; desktop handoffs/fonts/link attachment; skill-scanner refinements; sparse config writes; credential redaction/OAuth callback escaping; and browser/vault/provider work.

### New Troubleshooting Entries (v0.21 fresh install)
| Symptom | Observed cause | Action / outcome |
|---|---|---|
| Background shallow fetch made history appear divergent | Updater reported no common ancestor after `fetch --depth 1 origin main` | Official updater preserved the old HEAD in a backup ref and aligned the clean checkout with upstream; fetched history again for the delta count |
| Existing npm `11.12.1` rejected by installer | Installer reports npm 11.10–11.16 ignore `min-release-age-exclude` | Official installer provisioned managed Node 26.8.2/npm 11.19.1 automatically |
| Fresh config reported schema `0 → 45` | Installer copied the example config without a current schema marker | `hermes config migrate < /dev/null`; final check shows schema 45 |
| `macOS TCC anchor missing` | Fresh uv venv had not installed the stable interpreter anchor | `hermes doctor --fix`; subsequent doctor reports anchor active |
| Reference walker missed commands / rejected an undersized capture | Aliased rows, wrapped descriptions, and `COMMAND` / `<subcommand>` headings need parsing; old reference also contained repeated setup value-enum paths | Updated the maintained generator, checked it against live argparse, and added a navigation index. No fake setup paths are generated |
| `invalid choice: 'postinstall'` or `invalid choice: 'version'` | Current CLI does not accept these documented legacy commands | Skip postinstall; use `hermes --version` |
| `hermes status` prints `RecursionError: maximum recursion depth exceeded while calling a Python object` after its report | Observed traceback is in urllib3 pool finalization → queue → threading lock entry; root cause unverified | Seen before the latest-tip refresh; final status exited 0 without this traceback. Root cause remains unverified; no local source patch applied |
| Doctor says `API key or custom endpoint configured` on an unconfigured fresh install | Its file-content check matches credential names in template comments | Inspect actual nonempty assignments and auth status; this run had none. Some status plugin rows also say configured despite no channel tokens/service |

---

## What's new in v0.20.5 (vs v0.18.2)

_Maintenance/update verified locally on 2026-08-22. Local install upgraded from `Hermes Agent v0.18.2 (2026.7.7.2) · upstream b8880f12` to `Hermes Agent v0.20.5 (2026.8.19) · upstream 14c59f0b`._

### Local Upgrade Results
- **Core upgraded:** `hermes update --yes --backup` applied 9411 upstream commits and saved `~/.hermes/backups/pre-update-2026-08-22-163507.zip`.
- **Runtime repaired:** updater replaced the SQLite 3.50.4 environment with private Python 3.11.15 + SQLite 3.53.1 and upgraded `cua-driver` from 0.7.1 to 0.21.0.
- **Config migrated:** `hermes config migrate` moved config version `33 → 38`; `hermes config check` passed with only an existing optional Teams toolset warning.
- **Web UI rebuilt:** global `NODE_ENV=production` / npm `omit=dev` caused missing `vitest`, Node types, and Vite plugin errors. Root-level `env NODE_ENV=development npm install --include=dev` followed by `npm --workspace web run build` produced a clean build.
- **Gateway restored:** `hermes gateway start` refreshed the launchd service definition and returned it to supervised operation.
- **Codex OAuth repaired:** a stored credential reported logged-in state but live calls returned HTTP 401 malformed-token errors. A fresh `hermes auth add openai-codex --type oauth` device flow passed live one-shot tests; the exhausted old credential was removed.
- **Registry skills refreshed:** all six hub-installed skills are current. The Minecraft server skill remains security-blocked because its instructions include `sudo`, firewall, and cron commands; do not bypass that audit casually.
- **CLI reference regenerated:** `cli-reference.md` now targets v0.20.5 and is 849,838 bytes, covering the expanded command surface without recursive runaway.
- **New top-level surfaces:** `worktree`, `egress`, `pause`, `resume`, `sync`, `peer`, `verify`, `approvals`, `import-agent`, `skin`, and `monitoring`; new global flags include `--reasoning`, `--no-restore-cwd`, `--in`, `--safe-mode`, and `--cli`.

### New Troubleshooting Entries (v0.20 local)
| Symptom | Cause | Fix |
|---|---|---|
| Web build fails on missing `vitest`, `@vitejs/plugin-react`, Node types, or other dev-only packages | Shell exports `NODE_ENV=production`, making npm omit development dependencies even during updater builds | From `~/.hermes/hermes-agent`, run `env NODE_ENV=development npm install --include=dev`, then `env NODE_ENV=development npm --workspace web run build` |
| `hermes auth status openai-codex` says logged in but a live turn returns HTTP 401 `Could not parse your authentication token` | A legacy/exhausted pooled credential survived the upgrade and no longer satisfies the current runtime | Add a fresh device credential with `hermes auth add openai-codex --type oauth`, verify with a real `hermes -z` turn, then remove the stale entry with `hermes auth remove openai-codex <index>` |
| `hermes doctor` reports high-severity npm findings only in `web` or `ui-tui` build tooling | Upstream transitive build dependencies remain in the lockfile; runtime bundles are not affected | Do not use `npm audit fix --force` blindly. Track the upstream lockfile bump and re-run `hermes doctor` after updates |
| `hermes skills audit` blocks an official skill after update because it contains `sudo`, firewall, or cron examples | Re-audited hub skills are treated as community content and CAUTION findings are blocked by default | Leave it blocked unless that exact skill is needed and its instructions have been manually reviewed; only then consider the explicit force override |

---

## What's new in v0.18.2 (vs v0.17.0)

_Maintenance/update verified locally on 2026-07-10. Local install upgraded from `Hermes Agent v0.17.0 (2026.6.19) · upstream f3d2dfbe` to `Hermes Agent v0.18.2 (2026.7.7.2) · upstream b8880f12`._

### Local Upgrade Results
- **Core upgraded:** `hermes update --yes --backup` applied 1550 commits and saved `~/.hermes/backups/pre-update-2026-07-10-111707.zip`.
- **Config migrated:** `hermes config migrate` moved config version `32 → 33`; `hermes config check` reports only an existing optional Teams toolset warning.
- **Gateway restored:** `hermes gateway start` reloaded the current launchd service definition and returned to supervised operation.
- **CLI reference regenerated:** `cli-reference.md` regenerated for v0.18.2 at 557.3 KB, covering 626 command nodes to depth 4.
- **New top-level surfaces:** `console`, `journey`, `learning`, and `memory-graph`; top-level `--usage-file PATH` is also present.
- **GPT-5.6 catalog support:** Hermes registers `gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna`, and their `-pro` variants for OpenAI/Codex routing.
- **Codex OAuth entitlement is account-specific:** One ChatGPT Pro account returned HTTP 400 for `gpt-5.6-sol` and later exhausted quota, but switching Hermes to another eligible ChatGPT Pro account resolved both issues.
- **GPT-5.6 Sol smoke test passed:** After fresh device OAuth, explicit `model.default: gpt-5.6-sol` plus `model.provider: openai-codex`, and a gateway restart, `hermes -z "Reply with exactly: HERMES_GPT56_SOL_OK"` returned `HERMES_GPT56_SOL_OK`.
- **Account switching workflow:** Back up `~/.hermes/auth.json`, run `hermes auth logout openai-codex`, then `hermes auth add openai-codex --type oauth`; complete the device flow in a browser using the intended ChatGPT account, verify the email/plan from token metadata if necessary, remove duplicate credentials, restart the gateway, and run a real one-shot test.

### New Troubleshooting Entries (v0.18 local)
| Symptom | Cause | Fix |
|---|---|---|
| `gpt-5.6-sol` appears in Hermes but Codex OAuth returns `The 'gpt-5.6-sol' model is not supported when using Codex with a ChatGPT account` | The signed-in ChatGPT account lacks Sol entitlement even though Hermes supports the model | Switch Hermes OAuth to an eligible ChatGPT account, set `model.default: gpt-5.6-sol` and `model.provider: openai-codex`, restart, then verify with a real one-shot test |
| `hermes gateway start` initially says it cannot find `ai.hermes.gateway` after an update | The plist exists but launchd unloaded the job during the upgrade | Let `hermes gateway start` reload it, then verify `hermes gateway status` shows a supervised PID |
| A known-working Codex model returns HTTP 429 `The usage limit has been reached` after valid OAuth | The ChatGPT/Codex account quota is exhausted; this is upstream account state, not a Hermes config failure | Wait for the quota window to reset or use another authorized account/provider, then rerun a one-shot smoke test |

---

## What's new in v0.17.0 (vs v0.14.0)

_Maintenance/update verified locally on 2026-06-30. Local install upgraded from `Hermes Agent v0.14.0 (2026.5.16)` to `Hermes Agent v0.17.0 (2026.6.19) · upstream f3d2dfbe`._

### Local Upgrade Results
- **Core upgraded:** `hermes update --yes --backup` installed `hermes-agent==0.17.0`, updated Python deps, synced bundled skills, upgraded `cua-driver` from `0.2.0` to `0.6.8`, and saved backup `~/.hermes/backups/pre-update-2026-06-30-082220.zip`.
- **Config migrated:** `hermes config migrate` moved config version `23 → 32`, lowered `model_catalog.ttl_hours` to `1`, seeded `curator.consolidate: false`, and set `agent.verify_on_stop: false`.
- **Gateway repaired:** After update, `hermes gateway status` reported the launchd service definition stale/not loaded. Running `hermes gateway install` then `hermes gateway start` repaired the plist and started launchd supervision.
- **Web UI build repaired:** Update initially failed web build with `sh: tsc: command not found` because `NODE_ENV=production` caused `npm` to omit dev dependencies. Fix: `npm --prefix ~/.hermes/hermes-agent/web install --include=dev`, then `npm --prefix ~/.hermes/hermes-agent/web run build`.
- **CLI reference regenerated:** `cli-reference.md` regenerated for v0.17.0; size around `541 KB`, which is within the expected safe range and indicates no recursive help-walker runaway.
- **Smoke test passed:** `hermes -z "Reply with exactly: HERMES_OK"` returned `HERMES_OK` using the configured `openai-codex/gpt-5.5` route.

### Notable v0.17 CLI Additions Observed
- **New/expanded top-level domains:** `moa`, `secrets`, `migrate`, `whatsapp-cloud`, `portal`, `project`, `pets`, `serve`, `desktop`, `gui`, and `prompt-size` now appear in top-level help.
- **Gateway/event-loop hardening:** Recent commits offload blocking gateway/session DB paths via `AsyncSessionDB`, skip confirmed-dead delivery targets, and suppress shutdown home-channel broadcasts on flagged drains.
- **Desktop improvements:** Desktop gained read-replies-aloud / auto-speak controls, roaming pet behavior, read-only subagent watch windows, persisted terminal tabs/scrollback, live gateway popout, and a headless `hermes serve` backend.
- **Security/config hardening:** Recent changes sanitize session IDs and artifact paths, cap WeCom callback body size pre-auth, redact browser CDP endpoint logs, tighten skill path containment, and migrate config to v32.
- **Tool/provider updates:** Camofox/browser fixes, NVIDIA auxiliary max-token preservation, lazy install for supermemory/mem0 SDKs, Ollama vision detection via `/api/show`, and custom-provider `key_env` propagation.

### New Troubleshooting Entries (v0.17 local)
| Symptom | Cause | Fix |
|---|---|---|
| `hermes update` says Web UI build failed with `sh: tsc: command not found` | `NODE_ENV=production` or npm config `omit=dev` skipped web workspace dev dependencies, including TypeScript | Run `npm --prefix ~/.hermes/hermes-agent/web install --include=dev`, then `npm --prefix ~/.hermes/hermes-agent/web run build` |
| `hermes gateway status` says service definition is stale or service is not loaded after update | LaunchAgent plist still points at old install metadata or launchd has not loaded the repaired service | Run `hermes gateway install`, then `hermes gateway start`; verify `Service definition matches the current Hermes install` |
| `hermes update` warns lazy backends failed to refresh with `cannot import name apply_subprocess_home_env` | Mid-update backend refresh loaded stale modules while source/dependencies were being replaced | Finish the update, then rerun `hermes update --yes --no-backup`; if already up to date and `hermes doctor` passes required packages, treat as non-blocking |
| `hermes doctor` warns `model.default 'openai-codex/gpt-5.5' uses a vendor/model slug but provider is 'openai-codex'` | v0.17 doctor now flags vendor-prefixed slugs outside aggregators, but the configured Codex OAuth route may still work | Verify with a real smoke test (`hermes -z ...`). If it works, leave as a warning; if it fails, select the model interactively with `hermes model` or update config to the v0.17 canonical model id |

---

## What's new in v0.14.0 (vs v0.12.0)

Major additions (1682 commits, 4 new bundled skills + 79 updated, 4 removed):

1. **`hermes proxy`** — OpenAI-compatible local proxy. Point any external tool that speaks OpenAI API (Cursor, Continue, Aider, etc.) at `http://localhost:<port>` with any dummy bearer; Hermes injects the real OAuth creds for Nous/Codex/etc. upstream. Run `hermes proxy providers` to see what's wired, `hermes proxy start` to launch.

2. **`hermes lsp`** — Post-write semantic diagnostics. When the agent writes or patches code, Hermes spawns the appropriate LSP and surfaces real errors back to the model. `hermes lsp install-all` installs every server with a known auto-recipe.

3. **`hermes send`** — Side-channel notification tool. `echo "build done" | hermes send -t telegram` to push a message through Hermes's configured Telegram (or Discord/Slack/Signal) bot **without** waking the agent loop. Perfect for cron/scripts.

4. **`hermes checkpoints`** — Replaces ad-hoc snapshot logic with a real shadow-git checkpoint store. Every `write_file`/`patch`/`terminal` call gets a checkpoint; `/rollback` restores. `hermes checkpoints status` shows disk usage; `prune` to GC.

5. **`hermes bundles`** — Group multiple skills under one `/slash` command. E.g. create a `/data-eng` bundle that loads dspy + huggingface-hub + jupyter-live-kernel in one shot.

6. **`hermes computer-use`** — First-class `computer_use` toolset (macOS). Installs the `cua-driver` binary that the toolset shells out to. Re-runnable target for repair.

7. **`hermes postinstall`** *(historical; absent in v0.21.3)* — Closes the gap for `pip install hermes-agent` users on platforms where pip can't provide system deps.

8. **Bundled-skill sync** — 79 bundled skills got updates on this upgrade, 4 new (`macos-computer-use`, `baoyu-article-illustrator`, `kanban-codex-lane`, `teams-meeting-pipeline`), 4 removed. The updater syncs them to all profiles automatically.

9. **`/rollback`** is now a real first-class command backed by `checkpoints` — use it inside chat to undo the agent's last filesystem-touching action.

10. **Update flow** — `hermes update --check` is the official way to peek before installing. Pre-update backups are off by default; pass `--backup` to force one (saves to `~/.hermes/backups/`). `--no-backup` overrides any config opt-in.

---

## Top-Level Flags (apply to most subcommands)

```
-z PROMPT              One-shot prompt (non-interactive turn)
--usage-file PATH       Write usage accounting details to a file
-m MODEL               Override model for this run
--provider PROVIDER    Override provider for this run
--reasoning LEVEL      Override reasoning effort for this run
-t TOOLSETS            Override which toolsets are active
--resume SESSION       Resume an existing session by ID
--no-restore-cwd       Keep the current directory when resuming
--in DIR               Change directory before starting or resuming
--continue [NAME]      Continue most recent session (or named)
--worktree             Use a git worktree for the run
--accept-hooks         Auto-approve unseen shell hooks (no TTY)
--skills SKILLS        Override which skills are loaded
--yolo                 Skip prompts/confirmations
--pass-session-id      Pass the session ID through
--ignore-user-config   Ignore user-level config overrides
--ignore-rules         Ignore custom rules
--safe-mode            Disable custom config, rules, plugins, and MCP servers
--tui                  Force the TUI mode
--cli                  Force the classic prompt-toolkit REPL
--dev                  Dev mode
```

Quick one-shot example:
```bash
hermes -z "summarize the last commit" -m anthropic/claude-opus-4.6
```

---

## Common Workflows

### Fresh install (no prior ~/.hermes)

Verified on macOS on 2026-09-15. Fetch and read the official installer before running it:
```bash
export HOME=/Users/adamcohen
export PATH="$HOME/.local/bin:$PATH"
mkdir -p /Users/adamcohen/.cache/hermes-install-20260915
curl -fsSL https://hermes-agent.nousresearch.com/install.sh -o /Users/adamcohen/.cache/hermes-install-20260915/install.sh
cat /Users/adamcohen/.cache/hermes-install-20260915/install.sh
bash /Users/adamcohen/.cache/hermes-install-20260915/install.sh --skip-setup --non-interactive --skip-computer-use < /dev/null
hermes config migrate < /dev/null
hermes doctor --fix < /dev/null
cd /Users/adamcohen/.hermes/hermes-agent
env NODE_ENV=development npm --workspace web run build
hermes config check
hermes status
```
The installer provisions managed uv/Node when needed, a uv-managed Python venv,
CLI shims, template config, and bundled skills. This run required no Homebrew
packages. `--skip-setup` is required to avoid the wizard even when `/dev/tty` is
available. The fresh template contains no active messaging tokens; no gateway
was installed or started. `postinstall` is not a command in v0.21.3.

**Next steps for the user:** run `hermes setup`, or `hermes model` plus
`hermes auth add <provider> --type oauth` / `--type api-key` as appropriate.
For messaging, run `hermes gateway setup`, then `hermes gateway install` and
`hermes gateway start`. These interactive/auth/service steps were not performed.

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
hermes update          # in-place upgrade (reuses ~/.hermes/.env and config)
hermes config migrate  # apply any new config fields the new version added
hermes config check    # warn on outdated keys
hermes doctor          # run health checks after upgrade
hermes gateway restart # pick up new code
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

## "Refresh" — what to use for what

There's no single `hermes refresh` command; refresh is contextual. Mapping the common asks:

| Want to refresh… | Use |
|---|---|
| **Hub skill catalog + installed versions** | `hermes skills check` (find updates) → `hermes skills update` (apply) |
| **Local skill index** (re-scan filesystem after manual edits) | `hermes skills audit` |
| **Curator-managed skills** (auxiliary background reviewer) | `hermes curator run` (trigger now) |
| **Config** (after editing `~/.hermes/config.yaml` or `.env`) | `hermes gateway restart` — there is **no hot-reload** |
| **Config schema** (after a Hermes upgrade adds new fields) | `hermes config migrate` |
| **Codex OAuth tokens** | **Auto** — happens in background; `last_refresh` field in `~/.hermes/auth.json` shows when. Force re-auth: `hermes auth logout openai-codex && hermes auth add openai-codex --type oauth` |
| **Channel state** (Telegram polling stuck, etc.) | `hermes gateway restart` |
| **Anything weird** | `hermes doctor` (auto-fix where possible) |

**No refresh exists for:**
- **Provider model catalog** — fetched on-demand per request from each provider's API.
- **Sessions** — append-only JSONL files; "refresh" = `--continue` to pick up the latest entry.
- **Built-in memory** (`MEMORY.md` / `USER.md`) — always live, no caching to invalidate.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `hermes` command not found and `~/.hermes` missing | Hermes is absent, rather than just missing from PATH | Follow the **Fresh install (no prior ~/.hermes)** recipe; configure model/auth and messaging afterward |
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
| `gpt-5.6-sol` is listed but Codex OAuth returns HTTP 400 saying the ChatGPT account is unsupported | Sol entitlement is account-specific; the active OAuth account may not have access | Sign out of `openai-codex`, authorize an eligible ChatGPT account with the device flow, set explicit Codex routing, restart, and smoke-test |
| Codex OAuth returns HTTP 429 `The usage limit has been reached` | The OpenAI account quota is exhausted even though OAuth is valid | Wait for quota reset or authorize another eligible account/provider; config changes cannot bypass the upstream limit |
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

**Claude MUST update this SKILL.md** at `/Users/adamcohen/.agents/skills/hermes-configure/SKILL.md` (sync a separate `.claude` copy only if it exists):
- Add the workflow/recipe to the appropriate section
- Add new gotchas to the troubleshooting table
- Update provider/channel sections if Hermes adds support
- Bump the version footer if behavior depends on a specific Hermes release
- Keep concise and well-organized

This skill grows with every use. Never let hard-won knowledge be lost.

---

## Version Check & Auto-Update Protocol

**This skill was last updated for:** `Hermes v0.21.3 (build 2026.9.14, upstream a982d2c8)`

**Fresh install sync — 2026-09-15:** Hermes had been removed from this Mac (no `~/.hermes`, executable, or LaunchAgent). The official installer restored v0.21.3 at `a982d2c8`. After fetching `origin/main`, the checkout was **0 commits ahead / 0 behind**; 10,400 commits separate it from historical `14c59f0b`. Model authentication and gateway setup remain for the user.

The canonical skill is `/Users/adamcohen/.agents/skills/hermes-configure`; `/Users/adamcohen/.claude/skills/hermes-configure` does not exist. The generator writes beside this skill, accepts real aliased subparser listings, rejects positional value enums without command listings, and preserves the existing reference on capture failure.

### Version Check (run at start of every Hermes session)

Before answering any Hermes question, Claude SHOULD run this in parallel with the user's actual task (lightweight, fast):

```bash
# Installed version
hermes --version 2>&1 | head -1
```

Use `hermes update --check` to check for updates, or compare the managed checkout with upstream:

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

2. **Regenerate `cli-reference.md` (exhaustive, recursive, depth-safe).**

   **Critical bug to avoid:** A naive regex like `\{([^}]+)\}` matches BOTH real subparser choice lists AND flag-value enums (e.g. `--type {oauth,api-key}`). Recursing on the latter causes a runaway — `hermes auth add oauth --help` returns the same help (argparse swallows the unknown positional), so the walker loops. A previous incident generated an 80 MB file before being killed.

   **Fix:** Parse subcommand choices ONLY from the `positional arguments:` block, and only when the choice list is followed by an indented `name   description` listing. Cap depth at 4. Track visited paths.

   Run the maintained generator; it writes to this skill directory:
   ```bash
   export HOME=/Users/adamcohen
   export PATH="$HOME/.local/bin:$PATH"
   python3 /Users/adamcohen/.agents/skills/hermes-configure/scripts/regen-cli-reference.py
   ```

   **Parser contract:** read only `positional arguments:`; require an indented command/description listing after a `{choice,...}`, `<subcommand>`, or `COMMAND` header. Support aliases and wrapped descriptions. Never recurse into an enum without actual command rows (e.g. `setup` sections). Keep `MAX_DEPTH = 4`, a visited set, and a 20-second timeout per help call. The maintained script preserves the previous reference on failures, adds a command index, and aborts above 5 MB.

   **Sanity check:** expect roughly **300 KB–2 MB**. Validate command coverage against the live parser when fixing capture logic; size alone cannot detect duplicated/invalid paths.

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
6. Don't use a naive `\{([^}]+)\}` regex when walking `--help` subcommands. Flag enums like `--type {oauth,api-key}` look identical to subparser choice lists and will cause an infinite-recursion runaway. Always anchor the parse to the `positional arguments:` block plus an indented description block (see Skill Refresh Procedure step 2).
