---
name: openclaw-configure
description: "Expert-level OpenClaw CLI configuration skill. Covers channels, models, plugins, gateway, agents, hooks, cron, security, sandbox, memory, browser, nodes, DNS, webhooks, approvals, backup, ACP provenance, ClawHub skill registry, tasks, and more. Self-evolving: updates itself after learning new patterns."
version: 2026.4.27
author: zanearcher
category: infrastructure
openclaw_version: "2026.4.27"
tags:
  - openclaw
  - cli
  - gateway
  - channels
  - models
  - plugins
  - agents
  - hooks
  - cron
  - security
  - sandbox
  - memory
  - browser
  - nodes
  - dns
  - webhooks
  - approvals
  - backup
  - acp
  - clawhub
  - skills
  - secrets
  - tasks
---

# OpenClaw-Configure Skill

Configure any aspect of OpenClaw via CLI. Battle-tested from real setup sessions.

**Trigger on:** "openclaw", "clawhub", "add channel", "switch model", "configure gateway", "openclaw setup", "add telegram", "switch to claude", "openclaw cron", "openclaw hooks", "openclaw doctor", "install skill", "publish skill", "search skills", or any OpenClaw/ClawHub configuration task.

**Reference files** (same directory as this skill):
- `commands.md` — condensed CLI reference, all 25 domains
- `cli-reference.md` — full `--help` for 142+ commands
- `oauth2-setup.md` — OAuth2 model setup guide

**IMPORTANT — Auto-Update Check:** Before answering any OpenClaw question, Claude MUST run the **Version Check & Auto-Update Protocol** (see bottom of this file). This checks installed vs latest vs skill versions, asks the user whether to update if a newer version exists, and auto-syncs the skill to match the local installed version.

---

## Core Principles

### Config Files
- **Main config:** `~/.openclaw/openclaw.json`
- **Agent models:** `~/.openclaw/agents/<agent>/agent/models.json` (auto-synced)
- **Auth profiles:** `~/.openclaw/agents/<agent>/agent/auth-profiles.json`
- **Workspace:** `~/.openclaw/workspace/` (AGENTS.md, SOUL.md, IDENTITY.md, etc.)

### The Plugin Gate
Many features are plugins. Before adding a channel or auth provider, check `openclaw plugins list`. If disabled, run `openclaw plugins enable <id>` first. Forgetting this causes **"Unknown channel"** errors.

### Gateway Restart
Config changes require gateway restart:
```bash
openclaw gateway stop && sleep 2 && openclaw gateway
```
Or: `openclaw gateway --force` (kills existing, starts fresh).

### Config Validation
`openclaw.json` is schema-validated. Provider blocks need the full object (baseUrl, apiKey, api, models[]). For simple values use `openclaw config set`. For complex objects, edit JSON directly.

### Non-Interactive vs Interactive
- **Non-interactive:** `channels add`, `models set`, `config set`, direct JSON edits
- **Interactive (needs TTY):** `configure`, `models auth setup-token`, `models auth paste-token`, `onboard`
- When Claude can't run interactive commands, instruct user to run manually.

---

## Channels

### Supported
telegram, whatsapp, discord, irc, googlechat, slack, signal, imessage, feishu, nostr, msteams, mattermost, nextcloud-talk, matrix, bluebubbles, line, zalo, zalouser, tlon, twitch

### Add Channel Workflow
```
1. openclaw plugins list                          # check plugin status
2. openclaw plugins enable <channel>              # enable if disabled
3. openclaw channels add --channel <name> --token <token>  # add
4. openclaw gateway stop && sleep 2 && openclaw gateway    # restart
5. openclaw channels status                       # verify
6. openclaw pairing list <channel>                # check pending pairing
7. openclaw pairing approve <channel> <code>      # approve
```

### Channel-Specific Notes

**Telegram:** Bot token from @BotFather. `--token <token>`. Default dmPolicy: "pairing" (users /start then get approved). Streaming: `channels.telegram.streaming: "partial"` (default since v2026.3.2; uses `sendMessageDraft` for live preview with separated reasoning/answer lanes). Lifecycle status reactions: configurable emoji for queued/thinking/tool/done/error phases. Per-topic `agentId` overrides for forum groups and DM topics (v2026.3.7). Voice mention gating: `disableAudioPreflight` to skip transcription-based mention detection. Plugin: `telegram`.

**WhatsApp:** `openclaw channels login --channel whatsapp` (QR code). dmPolicy: "allowlist" with E.164 numbers. `selfChatMode: true` for self-messaging. Plugin: `whatsapp`.

**Discord:** Bot token from Developer Portal. `--token <token>`. Configure guild/channel access in `channels.discord.guilds`. Plugin: `discord`.
- **Stream preview mode** (v2026.2.21): Live draft replies with `partial` or `block` options, configurable chunking
- **Lifecycle status reactions**: Configurable emoji feedback during agent processing (queued/thinking/tool/done/error phases)
- **Voice channels**: Join/leave/status via `/vc`, auto-join for realtime voice conversations
- **Ephemeral defaults**: Configurable ephemeral responses for slash commands
- **Forum tag management**: `available_tags` editing
- **Channel topics**: Included in trusted inbound metadata
- **Thread-bound subagents**: Per-thread sessions with focus/list controls
- **Thread lifecycle (v2026.3.1+)**: Inactivity-based lifecycle (`idleHours` default 24h) + optional `maxAgeHours` hard limit, `/session idle` + `/session max-age` commands

**Telegram DM Topics (v2026.3.1+):** Per-DM `direct` + topic config (allowlists, `dmPolicy`, `skills`, `systemPrompt`, `requireTopic`). DM topics route as distinct sessions.

**Feishu (v2026.3.1+):** Docx table creation/cell writing, image/file uploads, reactions, chat tooling, group session scopes (`group`/`group_sender`/`group_topic`/`group_topic_sender`), `replyInThread` config, multi-account `defaultAccount` routing.

**iMessage:** Uses `imsg` CLI. `--cli-path imsg`. dmPolicy: "allowlist". Plugin: `imessage`.

**Signal:** Needs `signal-cli`. `--signal-number <e164>`. Plugin: `signal`.

**Matrix:** `--homeserver <url> --user-id <id> --password <pw>` or `--access-token`. Plugin: `matrix`.

**Slack:** `--bot-token <xoxb-...> --app-token <xapp-...>`. Plugin: `slack`.

### Per-Channel Model Overrides (v2026.2.21+)

Route different models to different channels via `channels.modelByChannel`:
```json
"channels": {
  "modelByChannel": {
    "discord": "anthropic/claude-opus-4-6",
    "telegram": "google/gemini-3.1-pro-preview",
    "whatsapp": "openai/gpt-5.3-codex"
  }
}
```
This overrides the default model on a per-channel basis without needing separate agents.

### Per-Account defaultTo Routing (v2026.2.21+)

Set outbound routing fallback per account: `channels.<ch>.accounts.<id>.defaultTo` for `openclaw agent --deliver`.

### Channel Commands
```
channels add          --channel <name> --token <token> --account <id>
channels remove       --channel <name> --account <id> --delete
channels login        --channel <ch> --account <id> --verbose
channels logout       --channel <ch> --account <id>
channels list         --json --no-usage
channels status       --probe --json --timeout <ms>
channels capabilities --channel <name> --json --target <dest>
channels resolve      --channel <name> --kind <auto|user|group> --json
channels logs         --channel <name> --lines <n> --json
```

---

## Models

### Provider Format
`provider/model-id`: `anthropic/claude-opus-4-6`, `ollama/minimax-m2.5:cloud`, `openai-codex/gpt-5.3-codex`

### Provider Config Block (openclaw.json -> models.providers)
```json
"<provider-id>": {
  "baseUrl": "<endpoint>",
  "apiKey": "<key-or-placeholder>",
  "api": "<api-type>",
  "models": [{
    "id": "<model-id>", "name": "<display>", "reasoning": bool,
    "input": ["text"] or ["text","image"],
    "cost": {"input":0,"output":0,"cacheRead":0,"cacheWrite":0},
    "contextWindow": 200000, "maxTokens": 8192
  }]
}
```

### API Types
- `"anthropic-messages"` — Anthropic direct + MiniMax Portal
- `"ollama"` — Ollama native (baseUrl WITHOUT /v1)
- `"openai-completions"` — OpenAI-compatible
### Provider Setup Recipes

**Ollama (local):**
```json
"ollama": {
  "baseUrl": "http://127.0.0.1:11434",  // NO /v1
  "apiKey": "ollama-local",              // dummy, required
  "api": "ollama",                       // NOT "openai-chat"
  "models": [{"id":"minimax-m2.5:cloud", ...}]
}
```

**Anthropic (API key):**
```json
"anthropic": {
  "baseUrl": "https://api.anthropic.com",
  "apiKey": "sk-ant-api03-...",
  "api": "anthropic-messages",
  "models": [{"id":"claude-opus-4-6", ...}]
}
```

**Anthropic (Claude subscription via setup-token):**
- REQUIRES `claude` CLI logged in with Pro/Max (`/login` first!)
- Generate: `claude setup-token` -> token starts with `sk-ant-oat01-`
- Register: `openclaw models auth setup-token --provider anthropic` (interactive, user must run)
- Or paste into `auth-profiles.json` -> `anthropic:manual.token`
- GOTCHA: Unauthenticated session -> invalid token -> 401 error
- Same `api: "anthropic-messages"` — OpenClaw handles bearer auth internally

**OpenAI (GPT Plus via Codex OAuth):**
- Install: `npm i -g @openai/codex`
- Run: `openclaw configure` -> select **"OpenAI Codex"** (OAuth, NOT API key)
- Browser opens for OAuth
- Models: GPT 5.2, GPT 5.2 Codex, GPT 5.3 Codex

**Google Gemini (subscription):**
- Install: `npm install -g @google/gemini-cli`
- Enable: `openclaw plugins enable google-gemini-cli-auth`
- Run: `openclaw configure` -> Google -> "Google Gemini CLI Auth"
- Models: Gemini 3 Pro, Gemini 3 Flash (~1M context), Gemini 3.1 Pro Preview (v2026.2.21+)

**Volcano Engine / Doubao (v2026.2.21+):**
- Run: `openclaw configure` -> Volcano Engine -> follow onboarding auth flow
- Models: Doubao series
- api: `"openai-completions"` (OpenAI-compatible)

**BytePlus (v2026.2.21+):**
- Run: `openclaw configure` -> BytePlus -> follow onboarding auth flow
- api: `"openai-completions"` (OpenAI-compatible)

**MiniMax Portal (free OAuth):**
- Enable: `openclaw plugins enable minimax-portal-auth`
- Run: `openclaw configure` or `openclaw models auth login --provider minimax-portal`
- api: `"anthropic-messages"` (Anthropic-compatible)

**Kilo Code Gateway (v2026.2.23+):**
- Run: `openclaw configure` → Kilo Gateway → follow onboarding auth flow
- Default model: `kilocode/anthropic/claude-opus-4.6`
- api: `"anthropic-messages"` (Anthropic-compatible routing)

**Vercel AI Gateway (v2026.2.23+):**
- Accepts Claude shorthand refs: `vercel-ai-gateway/claude-*` (auto-normalized to canonical Anthropic IDs)
- Configure like any OpenAI-compatible provider

### Model Switching — Full Workflow
Switching the default model requires more than `models set`:
```bash
# 1. Set the new default
openclaw models set "provider/model-id"

# 2. Configure fallback chain (order matters!)
openclaw models fallbacks clear
openclaw models fallbacks add "fallback1/model"
openclaw models fallbacks add "fallback2/model"

# 3. Delete existing main session (or model identity will be stale)
#    Session files: ~/.openclaw/agents/<agent>/sessions/
#    Session index: ~/.openclaw/agents/<agent>/sessions/sessions.json
python3 -c "
import json, os
path = os.path.expanduser('~/.openclaw/agents/main/sessions/sessions.json')
with open(path) as f: data = json.load(f)
sid = data.pop('agent:main:main', {}).get('sessionId','')
with open(path, 'w') as f: json.dump(data, f, indent=2)
print(f'Removed session {sid}')
"
rm ~/.openclaw/agents/main/sessions/<session-id>.jsonl

# 4. Restart gateway to pick up config
openclaw gateway stop && sleep 2 && openclaw gateway

# 5. Verify
openclaw agent --agent main --message "What model are you?" --json --local 2>&1 | grep '"model"'
```

### Purging Models
To remove a model entirely:
1. Remove from `openclaw.json` -> `models.providers.<provider>` block
2. Remove from `openclaw.json` -> `agents.defaults.models` entries
3. Remove from fallbacks: `openclaw models fallbacks remove "provider/model"`
4. Also clean `~/.openclaw/agents/<agent>/agent/models.json` (agent-level copy)
5. Restart gateway

### Fallback Chain Gotcha — Model Identity Leak
**CRITICAL:** When model A is in the fallback chain and OpenClaw uses it for the first API turn (system prompt delivery), the agent's identity gets baked as model A — even if model B is the configured default. Subsequent turns use model B, but the agent self-reports as model A because that's what the system prompt said.

**Fix:** Remove unwanted models from the fallback chain. Only keep models you're OK with the agent identifying as. The fallback chain should only contain models you actually want to fall back to.

### Session Architecture
- **Session index:** `~/.openclaw/agents/<agent>/sessions/sessions.json` — maps session keys to metadata
- **Session history:** `~/.openclaw/agents/<agent>/sessions/<uuid>.jsonl` — JSONL with full conversation
- **Session keys:** `agent:<agent>:main` (DM/CLI), `agent:<agent>:discord:channel:<id>` (per-channel), etc.
- **System prompt:** NOT stored in JSONL — dynamically generated from workspace files (IDENTITY.md, SOUL.md, etc.) and injected at runtime
- **`systemSent` flag:** Tracks whether system prompt was already sent. Set to `false` to force re-injection.
- **`authProfileOverride`:** If set, LOCKS the session to a specific auth provider regardless of default model. Clear it (set to `null`) if session is stuck on wrong provider.

### Key Session Fields (sessions.json)
```
sessionId           → links to .jsonl file
model / modelProvider → current model (metadata, not authoritative)
systemSent          → true = system prompt already sent
authProfileOverride → LOCKS provider (set null to clear)
deliveryContext     → where replies go (channel, target)
totalTokens         → context usage
```

### JSONL Entry Types
```
type: "session"              → header (version, ID, timestamp)
type: "model_change"         → records active model/provider switch
type: "thinking_level_change" → reasoning level
type: "custom" / "model-snapshot" → model metadata at request time
type: "message" role: "user"     → incoming message
type: "message" role: "assistant" → agent response (thinking + text)
type: "message" role: "toolResult" → tool/skill output
```

### Verifying Actual Model vs Reported Model
The agent's text response may not match the actual model (due to system prompt identity). Always check JSON:
```bash
openclaw agent --message "hi" --json --local 2>&1 | grep '"model"'
```
The `"model"` field in JSON is the truth. The agent's text response is just what it thinks it is based on the system prompt.

### Model Commands
```
models set <provider/model>              Set default model
models set-image <provider/model>        Set image model
models list [--all] [--provider <name>]  List models
models status [--probe]                  Full model + auth status
models scan                              Scan OpenRouter free models
models aliases [add|list|remove]         Manage aliases
models fallbacks [add|list|remove|clear] Manage fallback chain
models image-fallbacks                   Manage image fallbacks
models auth add                          Interactive auth helper
models auth login --provider <id>        Run OAuth flow
models auth paste-token --provider <id>  Paste token (interactive)
models auth setup-token --provider anthropic  Claude Code token flow
models auth order                        Manage auth priority
```

---

## Plugins

### Commands
```
plugins list [--enabled] [--json]        List all plugins
plugins enable <id>                      Enable plugin
plugins disable <id>                     Disable plugin
plugins install <spec>                   Install from npm/path/archive
plugins uninstall <id>                   Remove plugin
plugins update [id] [--all]              Update npm plugins
plugins info <id>                        Show plugin details
plugins doctor                           Report load issues
```

### Key Plugin IDs
Channels: telegram, whatsapp, discord, imessage, signal, slack, matrix, googlechat, msteams, mattermost, irc, nostr, feishu, line, zalo, zalouser, tlon, bluebubbles, nextcloud-talk, twitch
Auth: minimax-portal-auth, google-gemini-cli-auth, google-antigravity-auth, copilot-proxy
Features: memory-core, memory-lancedb, device-pair, phone-control, talk-voice, diagnostics-otel, voice-call, open-prose, lobster, llm-task, thread-ownership

---

## Gateway

### Commands
```
gateway                                  Start gateway (foreground)
gateway --port 18789 --force             Specify port, kill existing
gateway start                            Start as service (launchd/systemd)
gateway stop                             Stop service
gateway restart                          Restart service
gateway install / uninstall              Manage service installation
gateway status [--deep]                  Show status + probe
gateway health                           Fetch health
gateway call                             Call RPC method directly
gateway discover                         Discover via Bonjour
gateway probe                            Reachability + health summary
gateway usage-cost                       Usage cost from session logs
```

### Container Probes (v2026.3.1+)
Built-in HTTP liveness/readiness endpoints for Docker/Kubernetes:
- `/health`, `/healthz` — liveness
- `/ready`, `/readyz` — readiness
Fallback routing preserves existing handlers on those paths.

### Config (openclaw.json -> gateway)
```json
"gateway": {
  "port": 18789, "mode": "local", "bind": "loopback",
  "auth": {"mode":"token","token":"<token>"},
  "tailscale": {"mode":"off"},
  "nodes": {"denyCommands":["camera.snap","screen.record",...]}
}
```

---

## Agents

```
agents list [--bindings] [--json]        List agents
agents add                               Add new agent (interactive)
agents delete <id> [--force]             Delete agent
agents set-identity                      Update name/theme/emoji/avatar
agents bindings                          List routing bindings
agents bind                              Add routing binding for an agent
agents unbind                            Remove routing binding for an agent
```

### Thinking Defaults (v2026.3.1+)
Claude 4.6 models now default to `adaptive` thinking level. Other reasoning-capable models default to `low` unless configured.

### Config (openclaw.json -> agents.defaults)
```json
"agents": {
  "defaults": {
    "model": {"primary":"anthropic/claude-opus-4-6"},
    "models": {"<provider/model>": {"alias":"opus"}},
    "workspace": "~/.openclaw/workspace",
    "compaction": {
      "mode": "safeguard",
      "reserveTokens": 4096,
      "keepRecentTokens": 8192
    },
    "maxConcurrent": 4,
    "subagents": {"maxConcurrent": 8, "maxSpawnDepth": 2}
  }
}
```

---

## Multi-Agent Setup (Multiple Bots, One Instance)

Run N agents from one OpenClaw instance, each with their own Telegram bot, workspace, and identity.

### Full Recipe: Add a New Agent

```bash
# 1. Create a Telegram bot via @BotFather, get the token

# 2. Register the Telegram account
openclaw channels add --channel telegram --account <agent-id> --token "<bot-token>"

# 3. Create the agent (auto-creates workspace + agent dir)
openclaw agents add --workspace ~/.openclaw/workspace-<agent-id> --bind telegram:<agent-id> --non-interactive

# 4. Name the agent
openclaw agents set-identity  # interactive — pick the agent, set name/emoji/avatar
```

### Agent Routing via Bindings (v2026.2.26+)

Route channel messages to specific agents with the top-level `bindings` array in `openclaw.json`:
```json
"bindings": [
  {"agentId": "main",    "match": {"channel": "telegram", "accountId": "main"}},
  {"agentId": "dev",     "match": {"channel": "telegram", "accountId": "dev"}},
  {"agentId": "content", "match": {"channel": "telegram", "accountId": "content"}}
]
```
Each Telegram account routes to the matching agent. The `main` agent also serves as the default (no explicit rules needed beyond the binding).

**CLI Management (v2026.2.26+):**
```bash
openclaw agents bindings                 # List all bindings
openclaw agents bind --agentId <id> --channel <ch> --accountId <id>
openclaw agents unbind <agentId> --channel <ch> --accountId <id>
```
**Features:** Account-scoped route management, channel-only to account-scoped binding upgrades, role-aware binding identity handling, plugin-resolved binding account IDs, and optional account-binding prompts in `openclaw channels add`.

### Telegram Multi-Account Config

```json
"channels": {
  "telegram": {
    "enabled": true,
    "botToken": "<main-bot-token>",
    "dmPolicy": "pairing",
    "accounts": {
      "main":    {"enabled": true, "dmPolicy": "pairing", "botToken": "<main-token>", "groupPolicy": "open", "streamMode": "partial"},
      "dev":     {"enabled": true, "dmPolicy": "pairing", "botToken": "<dev-token>",  "groupPolicy": "open", "streamMode": "partial"},
      "content": {"enabled": true, "dmPolicy": "pairing", "botToken": "<content-token>", "groupPolicy": "open", "streamMode": "partial"}
    }
  }
}
```
The top-level `botToken` is for the default account. Each `accounts.<id>` entry gets its own bot.

### Inter-Agent Communication

Agents can delegate tasks to each other via `sessions_spawn` / `sessions_send`. Requires TWO config blocks:

**1. agentToAgent (global):**
```json
"tools": {
  "agentToAgent": {
    "enabled": true,
    "allow": ["main", "dev", "content", "ops", "law"]
  }
}
```

**2. subagents.allowAgents (per-agent):**
Each agent in `agents.list` needs its own `subagents.allowAgents` listing which agents IT can reach:
```json
{
  "id": "dev",
  "workspace": "~/.openclaw/workspace-dev",
  "agentDir": "~/.openclaw/agents/dev/agent",
  "identity": {"name": "Timothy", "emoji": "💻", "avatar": "portrait.png"},
  "subagents": {"allowAgents": ["main", "content", "ops", "law"]}
}
```
**GOTCHA:** If only `main` has `allowAgents`, communication is one-way. For full mesh (any agent can reach any other), ALL agents need `allowAgents`.

### Agent Workspace Structure

Each agent's workspace (`~/.openclaw/workspace-<id>/`) should contain:

| File | Purpose |
|------|---------|
| `SOUL.md` | Personality, work style, boundaries |
| `IDENTITY.md` | Name, role, appearance description, self-intro, resume info |
| `AGENTS.md` | Team roster with names, workspace guide, media rules |
| `TOOLS.md` | Local tool notes, media path instructions |
| `MEMORY.md` | Long-term memory (agent updates this) |
| `portrait.png` | Agent's portrait for selfie generation |

### Agent Self-Awareness (Portraits & Selfies)

For agents to generate selfies from their portrait:
1. Place `portrait.png` in the agent's workspace
2. Copy to `~/.openclaw/media/<name>-portrait.png` (for sending)
3. In `IDENTITY.md`, add a `## My Appearance` section with detailed physical description
4. In `SOUL.md`, add a `## Self-Awareness` section explaining how to generate selfies and resumes
5. Set `identity.avatar` to `portrait.png` in `openclaw.json`

### Media Path Security

**CRITICAL:** OpenClaw's `assertLocalMediaAllowed()` BLOCKS `workspace-*` directories from outbound media sending. This is hardcoded — no config override exists.

Allowed directories for outbound media:
- `~/.openclaw/media/` (canonical shared media dir)
- `~/.openclaw/agents/`
- `~/.openclaw/workspace/` (default workspace ONLY, not workspace-*)
- `~/.openclaw/sandboxes/`
- `/tmp/`

**Workaround:** Agents save files in their own workspace for storage, but copy/save to `~/.openclaw/media/` when they need to SEND media via Telegram/WhatsApp.

### Device Scope for sessions_spawn

`sessions_spawn` requires `operator.write` scope on the device. If the device was paired before multi-agent was configured, it may only have `operator.admin`, `operator.approvals`, `operator.pairing`, `operator.read`.

**Fix:** Edit `~/.openclaw/devices/paired.json` — add `operator.write` to both the top-level `scopes` array AND `tokens.operator.scopes`. Also update `~/.openclaw/identity/device-auth.json`. Clear `~/.openclaw/devices/pending.json` (`{}`). Restart gateway.

### Clearing Stale Agent Sessions

After config changes (identity, workspace files), clear agent sessions so they pick up fresh context:
```bash
echo '{}' > ~/.openclaw/agents/<agent>/sessions/sessions.json
```
This forces a new session with updated SOUL.md/IDENTITY.md on next message.

### Running an Agent Turn via CLI

```bash
openclaw agent \
  --agent <agent-id> \
  --message "Your message" \
  --channel telegram \
  --deliver \
  --reply-account <agent-id> \
  --to <user-phone-or-chat-id>
```
- `--agent` overrides routing bindings
- `--deliver` sends the reply to the channel (not just stdout)
- `--reply-account` selects which Telegram bot sends the reply
- `--channel` defaults to `whatsapp` if not specified

---

## Config

```
config get <dot.path>                    Read config value
config set <dot.path> <value>            Set config value
config unset <dot.path>                  Remove config value
config file                              Print active config file path (v2026.3.1+)
configure [--section <name>]             Interactive wizard
```
Sections: workspace, model, web, gateway, daemon, channels, skills, health

### Common Paths
```
agents.defaults.model.primary            Default model
channels.<ch>.enabled                    Channel on/off
channels.<ch>.dmPolicy                   pairing|allowlist|open
channels.<ch>.allowFrom                  Allowed senders
gateway.port                             Gateway port
plugins.entries.<id>.enabled             Plugin on/off
messages.tts.edge.enabled                TTS on/off
```

---

## Cron

```
cron list [--all] [--json]               List jobs
cron add --name <n> --cron <expr> --message <text> [--deliver] [--tz <iana>]
cron rm <id>                             Remove job
cron enable/disable <id>                 Toggle job
cron run <id>                            Run now (debug)
cron edit                                Patch fields
cron runs                                Run history
cron status                              Scheduler status
```
Schedule types: `--at` (one-shot ISO 8601), `--every` (interval ms), `--cron` (5-field expr)

---

## Hooks

```
hooks list [--eligible] [--json]         List hooks
hooks enable / disable                   Toggle hook
hooks info                               Hook details
hooks install <spec>                     Install hook pack
hooks check                              Check eligibility
hooks update                             Update npm hooks
```

---

## Security

```
security audit [--deep] [--fix] [--json] Audit config + state
```
Best practices: `chmod 700 ~/.openclaw`, bind gateway to loopback, use allowlist/pairing dmPolicy, restrict node commands with denyCommands.

### Security Hardening (v2026.2.21+)
Major security overhaul with 40+ fixes:
- Owner-ID obfuscation uses dedicated HMAC secret (decoupled from gateway token)
- SHA-256 replaces SHA-1 for gateway lock and tool-call synthetic IDs
- Heredoc substitution allowlist bypass blocked
- Shell startup-file env injection blocked (`BASH_ENV`, `ENV`, `BASH_FUNC_*`, `LD_*`, `DYLD_*`)
- Browser local file reads via `file:`, `data:`, `javascript:` protocols blocked
- ACP resource link prompt injection prevention
- TTS model-driven provider switching now opt-in by default
- Sandbox browser containers default to dedicated Docker network

### Security Hardening (v2026.3.8+)
- `system.run` approved scripts pinned to on-disk file snapshots — post-approval rewrites denied before execution
- Skills download installs pin validated per-skill tools root — path rebinding cannot redirect writes outside tools dir
- MS Teams `groupPolicy: "allowlist"` now enforces sender allowlists even when route allowlists are configured
- Browser SSRF: private-network intermediate redirect hops blocked in strict navigation flows
- Cron files enforced to owner-only (`0600`), directories to `0700`

### Heartbeat DM Delivery Control (v2026.2.25+)
Replace the old boolean DM toggle with explicit policy field:
```json
"agents": {
  "defaults": {
    "heartbeat": {
      "directPolicy": "allow"   // "allow" (default) | "block"
    }
  }
}
```
Also supported per-agent via `agents.list[].heartbeat.directPolicy`. Default is `allow` (DMs permitted).

### Slack Session Thread Token Limit (v2026.2.25+)
Cap parent-session token inheritance for thread sessions to avoid bricking new threads:
```json
"session": {
  "parentForkMaxTokens": 100000   // default 100000; set 0 to disable limit
}
```

### Multi-User / Shared Runtime Hardening (v2026.2.24+)
For shared-user setups (multiple people using one OpenClaw instance):
```json
"security": {
  "trust_model": {
    "multi_user_heuristic": true
  }
}
```
When enabled, flags likely shared-user ingress and provides hardening guidance. For intentional multi-user deployments: `sandbox.mode="all"`, workspace-scoped FS, reduced tool surface, avoid personal/private identities on shared runtimes.

---

## Sandbox

```
sandbox list [--browser] [--json]        List containers
sandbox recreate [--all] [--session <id>] Force recreation
sandbox explain                          Explain effective policy
```

Config: `tools.sandbox.tools.allow` / `tools.sandbox.tools.deny`

---

## Memory

```
memory search <query> [--query <text>] [--max-results <n>]  Search memory (positional or --query)
memory index [--force]                    Reindex files
memory status [--json]                    Index status
```
Requires embedding provider (OpenAI/Gemini key or local). Plugin: memory-core (default), memory-lancedb (advanced).

### QMD Improvements (v2026.2.21+)
- Per-agent enable/disable for QMD
- Per-collection search splitting for targeted queries
- Boot retry on transient embedding/provider failures
- BM25-only mode support (no embedding provider needed)
- Global embed serialization (prevents parallel embed races)
- Mixed-source search ranking diversification (session transcripts no longer crowd out memory files)
- Explicit `unavailable` warnings from `memory_search` on embedding/provider failures

---

## Message

```
message send --channel <ch> --target <dest> --message <text> [--media <path>] [--json]
message read --channel <ch> --target <dest> [--limit <n>]
message edit / delete / broadcast / search
message react --emoji <emoji> --message-id <id>
message poll --poll-question <text> --poll-option <opt>
message pin / unpin / pins
message ban / kick / timeout              Moderation
message thread / channel / member / role / emoji / sticker / event / voice
```

---

## Pairing & Devices

```
pairing list [channel]                   Pending requests
pairing approve <channel> <code>         Approve sender

devices list [--json]                    List devices
devices approve / reject                 Handle pairing
devices remove <id>                      Remove device
devices revoke / rotate                  Token management
devices clear                            Clear all
```

---

## Directory

```
directory self [--channel <name>]        Own IDs
directory peers list [--channel <name> --query <text>]
directory groups list [--channel <name>]
directory groups members [--channel <name> --group-id <id>]
```

---

## Browser (40+ subcommands)

```
browser start/stop/status                Lifecycle
browser open <url> / close / tabs / focus / navigate
browser screenshot [--full-page] / snapshot [--format ai|aria]
browser click <ref> / type <ref> <text> / press <key> / hover / drag / select
browser fill --fields <json> / upload <path> / dialog --accept
browser wait --text <text> / evaluate --fn <js>
browser console / errors / requests / cookies / storage
browser resize <w> <h> / pdf / download
browser profiles / create-profile / delete-profile / reset-profile
browser extension / responsebody / waitfordownload / trace
```

**v2026.3.8 config:**
- `browser.relayBindHost` — bind Chrome relay to explicit non-loopback address for WSL2/cross-namespace setups (default: loopback only)

---

## Nodes

```
node run [--host <ip> --port <port>]     Start node host (foreground)
node install / uninstall / restart / stop / status

nodes list [--connected]                 List gateway nodes
nodes status / pending                   Connection + pairing status
nodes approve / reject / rename          Manage pairing
nodes describe                           Node capabilities
nodes invoke --node <id> --command <cmd> --params <json>
nodes run --node <id> --raw <cmd>        Shell command (mac only)
nodes camera / canvas / screen / location / notify / push
```

---

## Other Domains

### Secrets (v2026.2.26+)
```
secrets audit [--deep] [--fix]           Audit secrets storage
secrets configure                        Interactive secrets setup
secrets apply [--file <path>]            Apply secrets snapshot (target-path validation)
secrets reload                           Hot-reload running gateway secrets
```
**Features:** Full external secrets management workflow with runtime snapshot activation, strict target-path validation, safer migration scrubbing, ref-only auth-profile support, and dedicated docs.

### DNS
```
dns setup --domain <domain> [--apply]    CoreDNS for wide-area Bonjour
```

### Approvals
```
approvals get                            Fetch exec approvals
approvals set                            Replace from JSON file
approvals allowlist                      Edit per-agent allowlist
```

### System
```
system event                             Enqueue system event
system heartbeat [enable|disable|last]   Heartbeat controls
system presence [--json]                 Presence entries
```

### Webhooks
```
webhooks gmail                           Gmail Pub/Sub hooks (via gogcli)
```

### ACP (Agent Control Protocol) (v2026.2.26+)
```
acp [--url --token --session --verbose]  Run ACP bridge
acp client                               Interactive ACP client
acp --provenance off|meta|meta+receipt   ACP provenance mode (v2026.3.8+)
```
**NEW in v2026.2.26:** ACP agents are now first-class runtimes for thread sessions with `acp` spawn/send dispatch integration, acpx backend bridging, lifecycle controls, startup reconciliation, runtime cleanup, and coalesced thread replies. Thread-bound subagents can now be dispatched via ACP for enhanced realtime capabilities.

**NEW in v2026.3.8:** ACP provenance metadata — agents can retain and report ACP-origin context with session trace IDs. Modes: `off` (disabled), `meta` (ingress metadata only), `meta+receipt` (metadata + visible receipt injection).

### Skills (Runtime — `openclaw skills`)

OpenClaw's built-in skill commands manage **locally installed** skills at runtime:
```
skills list [--eligible] [--json]        List skills available to agents
skills info <name>                       Skill details + requirements
skills check                             Check which skills are ready vs missing requirements
```

**Relationship to ClawHub:** `openclaw skills` reads from the local skills directory. `clawhub` (separate CLI) manages the **registry** — install, publish, search, update. Typical flow:
```bash
clawhub install <slug>          # download skill from ClawHub registry
openclaw skills list            # verify it appears locally
openclaw skills check           # confirm requirements met
openclaw gateway stop && openclaw gateway  # restart to pick up new skill
```
See the **ClawHub** section below for the full registry CLI.

### Update
```
update [--channel stable|beta|dev --yes] Update OpenClaw
update status                            Version + channel status
update wizard                            Interactive update
```

### Diagnostics
```
doctor [--fix] [--deep]                  Health checks + fixes
health [--json]                          Gateway health
status [--deep] [--usage]                Channel health + sessions
logs [--follow] [--limit <n>]            Tail gateway logs
```

### Backup (v2026.3.8+)
```
backup create [--only-config] [--no-include-workspace]   Create local state archive
backup verify <path>                     Validate manifest + payload of archive
```
**Features:** Full local backup of OpenClaw state (config, workspace, agents). `--only-config` for config-only snapshots. Archives named for date sorting. Guidance shown in destructive flows (reset, uninstall).

### Web Search Configuration (v2026.3.8)

The `web_search` tool is configured via `tools.web.search`. The config path is `tools.web.search`, NOT `tools.webSearch` (which is rejected by schema validation).

**Supported providers (v2026.3.8):** `brave`, `perplexity`, `grok`, `gemini`, `kimi`

**GOTCHA:** Tavily is NOT a valid native provider in v2026.3.8. A community PR (#11978) adds Tavily support — expected in v2026.3.9+. Until then, use the `openclaw-tavily` plugin from ClawHub or set `TAVILY_API_KEY` env var with the plugin installed.

**Default behavior:** If no provider is configured, agents use whatever search grounding their model provider offers (e.g., Gemini uses Google Search grounding natively).

**Setting a provider:**
```bash
openclaw config set tools.web.search.provider gemini
```

**Provider-specific config:**
```bash
# Brave with LLM Context mode
openclaw config set tools.web.search.provider brave
openclaw config set tools.web.search.brave.mode llm-context

# Perplexity
openclaw config set tools.web.search.provider perplexity
# Requires PERPLEXITY_API_KEY env var or config

# Grok
openclaw config set tools.web.search.provider grok
# Requires GROK_API_KEY env var or config

# Kimi
openclaw config set tools.web.search.provider kimi
```

### New Config Keys (v2026.3.8+)

| Config Path | Type | Description |
|---|---|---|
| `talk.silenceTimeoutMs` | number | How long Talk mode waits for silence before auto-sending transcript. Platform default used when unset. |
| `tools.web.search.provider` | string | Web search provider: `brave`, `perplexity`, `grok`, `gemini`, `kimi`. NOT `tavily` in v2026.3.8. |
| `tools.web.search.brave.mode` | string | Set to `"llm-context"` to use Brave's LLM Context endpoint (returns extracted grounding snippets with source metadata instead of raw search results). |
| `browser.relayBindHost` | string | Bind Chrome relay to non-loopback address for WSL2/cross-namespace setups. Default: loopback only. |

**TUI theme (v2026.3.8+):** Auto-detects light terminal backgrounds via `COLORFGBG` and picks a WCAG AA-compliant light palette. Override with `OPENCLAW_THEME=light|dark`.

### Other
```
dashboard                                Open Control UI
tui [--session <key>]                    Terminal UI
sessions [--active <min>]               List sessions
sessions cleanup [--agent <id>] [--max-disk-bytes <n>]  Clean up old sessions (v2026.2.23+)
agent --to <num> --message <text> [--deliver] [--thinking <level>]  Run agent turn
onboard [--flow quickstart|advanced]     Onboarding wizard
setup [--mode local|remote]              Init config + workspace
reset [--scope config|full]              Reset state
uninstall [--all]                        Remove gateway + data
qr [--json]                              iOS pairing QR
completion                               Shell completion
docs <query>                             Search live docs
```

---

## External Secrets Management (v2026.2.26+)

Manage credentials and auth profiles via external secrets providers (HashiCorp Vault, AWS Secrets Manager, etc.)

```bash
openclaw secrets audit                   # Audit current secrets storage
openclaw secrets configure               # Interactive setup wizard
openclaw secrets apply --file <path>     # Apply snapshot with strict target-path validation
openclaw secrets reload                  # Hot-reload running gateway
```

**Key Features:**
- **Runtime snapshot activation:** Secrets applied at runtime without restart
- **Strict target-path validation:** Prevents accidental overwrites to wrong config paths
- **Safer migration scrubbing:** Cleaner transitions from inline keys to external refs
- **Ref-only auth-profiles:** Auth profiles can now reference external secret values via `$secret:provider/path` syntax
- **Built-in providers:** Vault, AWS Secrets Manager, GCP Secret Manager, Azure Key Vault

**Example Auth Profile with External Secret:**
```json
"auth-profiles.json": {
  "anthropic:vault": {
    "type": "anthropic-bearer",
    "key": "$secret:vault/secret/data/anthropic#api_key"
  }
}
```

---

## ClawHub (Skill Registry CLI)

**Separate CLI** from OpenClaw. Manages the ClawHub skill marketplace — install, search, publish, and browse community skills.

**CLI:** `clawhub` (v0.6.1)
**Trigger on:** "clawhub", "install skill", "publish skill", "search skills", "browse skills", "skill registry"

### Global Options
```
--workdir <dir>       Working directory (default: cwd)
--dir <dir>           Skills directory (relative to workdir, default: skills)
--site <url>          Site base URL (for browser login)
--registry <url>      Registry API base URL
--no-input            Disable prompts
```

### Environment Variables
```
CLAWHUB_SITE          Site base URL
CLAWHUB_REGISTRY      Registry API base URL
CLAWHUB_WORKDIR       Working directory
(CLAWDHUB_* also supported)
```

### Authentication

```
login [--token <token>] [--label <label>] [--no-browser]
                         Log in (opens browser or stores token)
                         --token: API token (skip browser)
                         --label: Token label for browser flow (default: "CLI token")
                         --no-browser: Don't open browser (requires --token)
logout                   Remove stored token
whoami                   Validate token
auth login [options]     Same as top-level login
auth logout              Same as top-level logout
auth whoami              Same as top-level whoami
```

### Discovery & Browsing

```
explore [--limit <n>] [--sort <order>] [--json]
                         Browse latest updated skills from the registry
                         --limit: Number of skills (max 200, default 25)
                         --sort: newest|downloads|rating|installs|installsAllTime|trending (default: newest)

search <query...> [--limit <n>]
                         Vector search skills by query string

inspect <slug> [options]
                         Fetch skill metadata and files without installing
                         --version <version>   Version to inspect
                         --tag <tag>           Tag to inspect (default: latest)
                         --versions            List version history (first page)
                         --limit <n>           Max versions to list (1-200)
                         --files               List files for the selected version
                         --file <path>         Fetch raw file content (text <= 200KB)
                         --json                Output JSON
```

### Install & Update

```
install <slug> [--version <version>] [--force]
                         Install skill into <dir>/<slug>
                         --version: Specific version to install
                         --force: Overwrite existing folder

update [slug] [--all] [--version <version>] [--force]
                         Update installed skills
                         --all: Update all installed skills
                         --version: Update to specific version (single slug only)
                         --force: Overwrite when local files don't match any version

list                     List installed skills (from lockfile)
```

### Publishing

```
publish <path> [options]
                         Publish skill from folder
                         --slug <slug>               Skill slug
                         --name <name>               Display name
                         --version <version>          Version (semver)
                         --fork-of <slug[@version]>  Mark as fork of existing skill
                         --changelog <text>           Changelog text
                         --tags <tags>                Comma-separated tags (default: "latest")

sync [options]           Scan local skills and publish new/updated ones
                         --root <dir...>     Extra scan roots (one or more)
                         --all               Upload all new/updated without prompting
                         --dry-run           Show what would be uploaded
                         --bump <type>       Version bump: patch|minor|major (default: patch)
                         --changelog <text>  Changelog for updates (non-interactive)
                         --tags <tags>       Comma-separated tags (default: "latest")
                         --concurrency <n>   Concurrent registry checks (default: 4)
```

### Social

```
star <slug> [--yes]      Add a skill to your highlights
unstar <slug> [--yes]    Remove a skill from your highlights
```

### Moderation (moderator/admin only)

```
delete <slug> [--yes]              Soft-delete a skill
hide <slug> [--yes]                Hide a skill
undelete <slug> [--yes]            Restore a deleted skill
unhide <slug> [--yes]              Unhide a hidden skill
ban-user <handleOrId> [options]    Ban user and delete owned skills
                                   --id: Treat argument as user id
                                   --fuzzy: Fuzzy user search (admin only)
                                   --reason <reason>: Ban reason
                                   --yes: Skip confirmation
set-role <handleOrId> <role>       Change user role: user|moderator|admin (admin only)
                                   --id: Treat argument as user id
                                   --fuzzy: Fuzzy user search (admin only)
                                   --yes: Skip confirmation
```

### Common Workflows

**Browse and install a skill:**
```bash
clawhub explore --sort trending --limit 10    # browse popular skills
clawhub inspect <slug> --files                # preview files before install
clawhub install <slug>                        # install to ./skills/<slug>
```

**Publish a skill:**
```bash
clawhub login                                 # authenticate first
clawhub publish ./my-skill --slug my-skill --name "My Skill" --version 1.0.0
```

**Bulk sync local skills:**
```bash
clawhub sync --dry-run                        # preview what would be published
clawhub sync --all --bump patch               # publish all new/updated
```

**Update all installed skills:**
```bash
clawhub update --all
```

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| "Unknown channel: X" | Plugin disabled | `openclaw plugins enable X` |
| 401 Invalid bearer token | setup-token from unauthenticated Claude Code | `/login` in Claude Code first, regenerate token |
| "Config validation failed" | Incomplete provider block | Need full: baseUrl, apiKey, api, models[] |
| Gateway won't start / port in use | Existing process | `openclaw gateway --force` |
| Channel status: no messages | Gateway not restarted | Restart after config changes |
| Ollama "Unknown model" | Missing apiKey | `apiKey: "ollama-local"` (dummy) |
| Ollama wrong api | Used "openai-chat" | Must be `"ollama"`, baseUrl without /v1 |
| "BOT_COMMANDS_TOO_MUCH" (Telegram) | Too many slash commands | Non-blocking, ignore |
| OAuth token expired | Past expiry | Re-run: `openclaw models auth login --provider <id>` |
| "Gateway service not loaded" | Service vs foreground mismatch | Use `gateway --force` or install service |
| Agent reports wrong model after switch | Old session has stale system prompt | Delete session from sessions.json + remove .jsonl file, restart gateway |
| Model switched but agent still uses old one | `authProfileOverride` locked to old provider | Set `authProfileOverride: null` in sessions.json, or delete session |
| Fallback model used for first turn | OpenClaw tries fallback for system prompt delivery | Remove unwanted models from fallback chain (`models fallbacks remove`) |
| `models set` works but agent ignores it | Gateway cached old config in memory | Full restart: `gateway stop && sleep 2 && gateway install` |
| JSON shows correct model but text says wrong | System prompt identity baked from first-turn model | Delete session for clean start; check `grep '"model"'` in JSON for truth |
| `sessions_spawn` fails "pairing required" (1008) | Device missing `operator.write` scope | Add `operator.write` to `devices/paired.json` (scopes + tokens.operator.scopes) and `identity/device-auth.json`, clear `devices/pending.json`, restart gateway |
| Agent refuses to retry after prior failure | Persistent session remembers past errors | Clear session: `echo '{}' > ~/.openclaw/agents/<agent>/sessions/sessions.json` |
| Media "not under an allowed directory" | `workspace-*` dirs blocked by `assertLocalMediaAllowed()` | Save media to `~/.openclaw/media/` for sending. No config override exists |
| Agent defaults to wrong channel (e.g. WhatsApp) | `openclaw agent` defaults to `--channel whatsapp` | Always specify `--channel telegram --reply-account <id>` |
| `sessions_spawn` works from main but not between other agents | Only main has `subagents.allowAgents` | Add `subagents.allowAgents` to ALL agents that need to spawn others |
| `openclaw gateway stop` doesn't kill old process | PID still holding port | `kill -9 <pid>` then `openclaw gateway install --force` |
| Config changes not taking effect after restart | Old gateway process still running on port | Check `lsof -i :18789`, kill stale PID, then restart |
| iMessage `imsg rpc exited (code 1)` in gateway health | Node.js LaunchAgent lacks Full Disk Access to `chat.db` | System Settings → Privacy & Security → Full Disk Access → add `/opt/homebrew/bin/node` (symlink survives upgrades) |
| Heartbeat sending to DMs (v2026.2.25+) | Default is `allow` again (v2026.2.24 block is reverted) | To block DM heartbeat: set `agents.defaults.heartbeat.directPolicy: "block"` (or per-agent `agents.list[].heartbeat.directPolicy`) |
| Browser `network: "container:<id>"` blocked | **BREAKING**: Docker container-namespace join blocked by default | Set `agents.defaults.sandbox.docker.dangerouslyAllowContainerNamespaceJoin: true` to re-enable |
| Browser SSRF private network errors (v2026.2.23+) | **BREAKING**: `browser.ssrfPolicy.allowPrivateNetwork` renamed | Use `browser.ssrfPolicy.dangerouslyAllowPrivateNetwork`; run `openclaw doctor --fix` to auto-migrate |
| `memory search "query"` errors | v2026.2.24+ accepts both positional and `--query <text>` | Both forms work: `memory search "text"` or `memory search --query "text"` |
| Secrets `apply` fails with "invalid target" | Target path doesn't exist or is restricted | Run `openclaw secrets audit` to see valid paths; use `--fix` to auto-correct |
| Secrets not reloading after `apply` | Gateway not responding to reload signal | Run `openclaw secrets reload` or restart gateway manually |
| ACP agent won't initialize in thread | Missing startup reconciliation config | Ensure agent has `subagents.allowAgents` includes the ACP agent ID |
| Thread-bound subagent spawns to wrong channel | ACP dispatch not honoring thread context | Check `acp` config in agent workspace and verify thread session metadata |
| Bindings command errors with "account not found" | Plugin registry hasn't populated account IDs | Run `openclaw plugins doctor` to check plugin health and retry bindings command |
| **BREAKING** Node exec approval fails (v2026.3.1+) | Approval payloads now require `systemRunPlan` | Add `systemRunPlan` to node `host=node` approval requests |
| **BREAKING** Node `system.run` path mismatch (v2026.3.1+) | Commands now pinned to canonical `realpath` | Update allowlists/tests to use canonical paths (e.g. `/usr/bin/tr` not `tr`) |
| OpenAI streaming fails silently (v2026.3.1+) | WebSocket transport is now default for OpenAI | Set `params.openaiWsWarmup: false` per-model if WS issues; or configure `transport: "sse"` to force SSE |
| Gateway WS insecure on private network (v2026.3.1+) | Plaintext `ws://` now loopback-only by default | Set `OPENCLAW_ALLOW_INSECURE_PRIVATE_WS=1` for private network access |
| Cron job runs at ~1/3 of configured timeout (v2026.3.1+) | Stale CLI session ID reused | Fixed in v2026.3.1 — isolated cron runs use fresh watchdog profiles |
| `cron run` returns 0 on failure | Exit code was always 0 | Fixed in v2026.3.1 — returns exit 1 for non-run/error outcomes |

---

## What's New in v2026.4.24–4.27

### Breaking / Noteworthy Defaults
- **Discord group/channel reply visibility default = silent** (v2026.4.27): Group/channel replies are private by default unless the agent explicitly uses the message tool. Always-on rooms can lurk without leaking automatic finals, blocks, previews, or status reactions. Restore legacy auto-posting with `messages.groupChat.visibleReplies: "automatic"`.
- **`/reset` and `/new` no longer fall through** (v2026.4.27): Bare `/reset` / `/new` stop after reset hooks acknowledge — no empty provider call. `/reset <message>` and `/new <message>` still seed the next turn.
- **WebChat New Session button now confirms** (v2026.4.27): Toolbar New Session button asks for confirmation before dispatching `/new`. Typed `/new` and `/reset` commands stay immediate.
- **`session.maintenance.rotateBytes` deprecated** (v2026.4.27): Auto-rotation of oversized `sessions.json` removed. `openclaw doctor --fix` strips the ignored key.
- **Discord interaction listener owned by OpenClaw** (v2026.4.27): Carbon interaction listener handed off async. Compaction or long session locks no longer trip listener timeouts.
- **CLI parent commands return exit 0** (v2026.4.27): `openclaw <parent>` (memory, channels, plugins, approvals, devices, cron, mcp) without subcommand now prints help and exits 0 (was 1). Fixes shell `&&` chains and pnpm wrappers.

### New Features

**Providers / Models:**
- **DeepInfra bundled provider** (v2026.4.27): `DEEPINFRA_API_KEY` onboarding, dynamic OpenAI-compatible model discovery, image generation/editing, image/audio media understanding, TTS, text-to-video, memory embeddings.
- **Cerebras bundled plugin** (v2026.4.26): Onboarding, static model catalog, manifest-owned endpoint metadata.
- **Tencent Yuanbao channel** (v2026.4.27): External plugin (`openclaw-plugin-yuanbao`) registered in official channel catalog. WebSocket bot DMs and group chats.
- **QQBot full group chat** (v2026.4.27): History tracking, @-mention gating, activation modes, per-group config, FIFO message queue, C2C `stream_messages` streaming, unified `sendMedia` with chunked upload.
- **Codex Computer Use** (v2026.4.27): `/codex computer-use status/install`, marketplace discovery, optional auto-install, fail-closed MCP server checks before Codex-mode turns.
- **Matrix encryption setup** (v2026.4.26): `openclaw matrix encryption setup` enables E2EE, bootstraps recovery, prints verification status from one flow.
- **Claude Code migration importer** (v2026.4.26): `openclaw migrate` with plan/dry-run/JSON, pre-migration backup, archive-only reports. Imports Claude Code/Desktop instructions, MCP servers, skills, command prompts. Bundled Hermes importer for config, memory/plugin hints, model providers, MCP, skills, credentials.

**Gateway / Security:**
- **Operator-managed outbound proxy** (v2026.4.27): `proxy.enabled` + `proxy.proxyUrl` / `OPENCLAW_PROXY_URL` with strict `http://` forward-proxy validation, loopback-only Gateway bypass, cleanup on exit.
- **Sandbox GPU passthrough** (v2026.4.27): Opt-in `sandbox.docker.gpus` for Docker sandbox containers when host Docker supports `--gpus`.
- **`trustedProxy.allowLoopback`** (v2026.4.27): Explicit support for same-host loopback reverse proxies. Loopback trusted-proxy auth fails closed by default.
- **`models.pricing.enabled`** (v2026.4.27): Set false to skip startup OpenRouter and LiteLLM pricing-catalog fetches. Useful for offline / restricted-network installs.

**Memory:**
- **`memorySearch.inputType`** (v2026.4.26): Optional `inputType`, `queryInputType`, `documentInputType` for asymmetric embedding endpoints. Includes direct query embeddings + provider batch indexing.
- **Ollama retrieval query prefixes** (v2026.4.26): Model-specific prefixes for `nomic-embed-text`, `qwen3-embedding`, `mxbai-embed-large` queries. Document batches unchanged.
- **`memorySearch.recallMaxChars`** (v2026.4.27): Bound memory recall embedding queries. Auto-recall now prefers the latest user message over channel prompt metadata. Helps small Ollama embedding models avoid context-length failures.

**Telegram / Channels:**
- **`--thread-id` for cron** (v2026.4.27): `openclaw cron add` / `cron edit` accept `--thread-id` for Telegram forum topic delivery preservation across scheduled announcements.
- **Native typing cue on inbound** (v2026.4.27): Best-effort typing cue immediately after inbound accept, before queueing/compaction/model/tool work starts. Shows liveness on slow pre-dispatch turns.
- **TTS → BlueBubbles voice memo** (v2026.4.27): Pre-transcoded MP3 → opus-in-CAF (mono, 24 kHz) on macOS so iMessage renders TTS as native voice-memo bubble (proper duration + waveform UI). Opt-in via `tts.voice.preferAudioFileFormat`.
- **Per-WhatsApp-group system prompts** (v2026.4.27): `channels.whatsapp.accounts.<id>.groups.<id>.systemPrompt` and `direct.<id>.systemPrompt` forwarded as `GroupSystemPrompt` (`"*"` wildcard supported).

**Compaction / Sessions:**
- **`compaction.maxActiveTranscriptBytes` preflight trigger** (v2026.4.26): Opt-in. Runs normal local compaction when active JSONL grows too large. Successful compaction moves future turns onto a smaller successor file instead of raw byte-splitting.
- **`compaction.memoryFlush.model` override** (v2026.4.27): Use exact override (e.g. `ollama/qwen3:8b`) without inheriting active session fallback chain. Lets local housekeeping avoid paid conversation models.

### Key Fixes (highlights)
- **DeepSeek V4 reasoning replay** (v2026.4.27): `reasoning_content` backfilled on plain assistant replay messages, not just tool-call turns. Fixes thinking sessions with prior tool use failing follow-up requests.
- **Slack auto-reply leak** (v2026.4.27): Fully consumed text reset triggers like `new session` no longer leak into the fresh model turn.
- **Slack Socket Mode timeouts** (v2026.4.27): 15s pong timeout default + new `clientPingTimeout` / `serverPingTimeout` / `pingPongLoggingEnabled` overrides. Stale-websocket handling decoupled from app-event health heuristics.
- **WebChat New Session race** (v2026.4.27): Pending run + typing state attached to the active client run. Unowned final/inject/announce events no longer unlock unrelated active runs.
- **WebChat large attachment crash** (v2026.4.27): Lit state no longer holds large attachment payloads. Object URL previews + send-time payload serialization. Fixes `RangeError: Maximum call stack size exceeded` on PDF/image uploads.
- **Telegram polling watchdog token failures** (v2026.4.27): Fail fast when Telegram rejects startup `getMe` with 401. Surface as token auth failure instead of misleading `deleteWebhook` cleanup error.
- **Telegram `/bot<TOKEN>` apiRoot fix** (v2026.4.27): Normalize accidental full-token `apiRoot` values at runtime. `openclaw doctor --fix` strips the suffix.
- **Cron Telegram thread routing** (v2026.4.27): Session-derived Telegram topic thread IDs preserved when isolated cron explicitly targets parent chat. Bare chat targets stay in active forum topic.
- **Cron agentId inference** (v2026.4.27): `cron.add` infers creating session's agentId when omitted. Scheduled agentTurn jobs route to session agent.
- **Cron local provider preflight** (v2026.4.27): Probe local Ollama / OpenAI-compatible endpoints before isolated cron turns. Records unreachable as skipped, caches dead-endpoint probes.
- **CLI parent commands exit 0** (v2026.4.27): `openclaw memory` / `channels` / `plugins` / etc. without subcommand prints help and exits 0.
- **Memory pre-compaction flush prompts** (v2026.4.27): Kept runtime-only. Session transcripts and `chat.history` no longer expose them as normal user turns.
- **Plugin runtime mirror** (v2026.4.27): Reuse unchanged bundled plugin runtime mirrors instead of rebuilding on every load. Cuts I/O on slow storage. Restart no longer reinstalls full retained dependency set when one is absent.
- **Auto-reply pending tool-result drain** (v2026.4.27): Bounded with progress-aware idle timeout. Never-settling tool tasks no longer leave session active forever. Slow healthy deliveries can still drain.
- **Backup excludes plugin `node_modules`** (v2026.4.27): Skips installed plugin dependency trees but keeps manifests + source files. Avoids rebuildable npm payload bloat.
- **OTEL diagnostic events** (v2026.4.27): Privacy-safe model-call request payload bytes, streamed response bytes, first-response latency, total duration captured in events, plugin hooks, stability snapshots, OTEL spans/metrics. Raw model content not logged.

### New Config Keys (v2026.4.24–4.27)
| Config Path | Type | Description |
|---|---|---|
| `proxy.enabled` | boolean | Enable operator-managed outbound proxy routing |
| `proxy.proxyUrl` (or `OPENCLAW_PROXY_URL` env) | string | Forward proxy URL (must be `http://`) |
| `sandbox.docker.gpus` | string | GPU passthrough for Docker sandbox containers |
| `models.pricing.enabled` | boolean | Skip startup OpenRouter/LiteLLM pricing fetches |
| `messages.groupChat.visibleReplies` | string | `"silent"` (default v2026.4.27) or `"automatic"` |
| `tts.voice.preferAudioFileFormat` | string | Opt-in opus-in-CAF for iMessage native voice memo |
| `agents.defaults.compaction.maxActiveTranscriptBytes` | number | Preflight trigger for transcript rotation |
| `agents.defaults.compaction.memoryFlush.model` | string | Override flush model without inheriting session fallback chain |
| `memorySearch.inputType` / `queryInputType` / `documentInputType` | string | Asymmetric embedding endpoint hints |
| `memorySearch.recallMaxChars` | number | Cap memory recall embedding query size |
| `streaming.preview.toolProgress` | boolean | Stream tool-progress into Matrix preview edits (default true) |
| `channels.slack.socketMode.clientPingTimeout` | number | Slack pong timeout (default 15s) |
| `channels.slack.socketMode.serverPingTimeout` | number | Server ping timeout |
| `channels.slack.socketMode.pingPongLoggingEnabled` | boolean | Enable ping/pong logging |
| `channels.whatsapp.accounts.<id>.groups.<id>.systemPrompt` | string | Per-WhatsApp-group system prompt |
| `channels.whatsapp.accounts.<id>.direct.<id>.systemPrompt` | string | Per-direct-chat system prompt |

### New Troubleshooting Entries (v2026.4.24–4.27)
| Symptom | Cause | Fix |
|---|---|---|
| Discord group replies stopped showing automatic finals/blocks/previews | v2026.4.27 default flipped to silent | Set `messages.groupChat.visibleReplies: "automatic"` to restore auto-posting |
| Bare `/reset` produces empty model reply | Pre-v2026.4.27 fell through to provider call | Upgrade to v2026.4.27+; use `/reset <message>` to seed next turn |
| WebChat New Session button instantly resets | Pre-v2026.4.27 dispatched immediately | Upgrade — toolbar button now confirms first |
| `openclaw memory` / `channels` returns exit 1 in `&&` chains | Pre-v2026.4.27 missing-subcommand exit code | Upgrade — parent commands exit 0 with help text |
| `sessions.json` rotation backups still appearing | `session.maintenance.rotateBytes` deprecated | Run `openclaw doctor --fix` to strip ignored key |
| DeepSeek V4 follow-up fails with missing reasoning content | Pre-v2026.4.27 backfill only ran on tool-call turns | Upgrade to v2026.4.27+ |
| Telegram bot shows `deleteWebhook` cleanup error on startup with bad token | Misleading 401 surface | v2026.4.27 reports as token auth failure instead |
| WebChat `RangeError: Maximum call stack size exceeded` on large file upload | Lit state held large attachment payloads | Upgrade to v2026.4.27+ |
| Cron job lost Telegram forum topic on next run | Session-derived thread ID overrode explicit target | Upgrade to v2026.4.27+; use `--thread-id` to pin explicit topic |
| Slack stale-websocket reconnect storm | Pong timeout coupled to app-event heuristics | v2026.4.27 default 15s + `clientPingTimeout` override |
| Always-on Discord channel leaking automatic replies | v2026.4.27 default change | Either upgrade and rely on silent default, or set `messages.groupChat.visibleReplies: "automatic"` for legacy behavior |
| Codex `gpt-5.4-mini` fails through Codex OAuth | OAuth route doesn't support that model | v2026.4.27 suppresses the row with API-key-route hint; use direct `openai/gpt-5.4-mini` |
| Auto-recall using channel prompt metadata instead of latest user message | Pre-v2026.4.27 priority order | Upgrade — latest user message preferred; tune `recallMaxChars` for small Ollama embeds |

---

## What's New in v2026.4.22–4.23

### Breaking / Noteworthy Defaults
- **Codex CLI auth import removed** (v2026.4.22): Onboarding and provider discovery no longer copy `~/.codex` OAuth material into agent auth stores. Use browser login or device pairing instead.
- **OpenAI image gen routes through Codex OAuth** (v2026.4.23): `openai/gpt-image-2` now works without `OPENAI_API_KEY` when an `openai-codex` profile is active. The provider tries Codex OAuth first before falling back to public OpenAI API routes.
- **Plain OpenAI uses native `web_search`** (v2026.4.22): Direct OpenAI Responses models automatically use OpenAI's native `web_search` tool when web search is enabled and no managed search provider is pinned. Explicit Brave/Perplexity/etc. still take precedence.
- **GPT-5 prompt overlay is shared** (v2026.4.22): Moved from OpenAI plugin to shared provider runtime. Toggle via `agents.defaults.promptOverlays.gpt5.personality` — applies across OpenAI, OpenRouter, OpenCode, Codex, etc.

### New Features

**Providers / Models:**
- **xAI multimodal** (v2026.4.22): `grok-imagine-image` / `grok-imagine-image-pro` for image gen + edits, six live xAI voices, MP3/WAV/PCM/G.711 TTS, `grok-stt` audio transcription, realtime STT for Voice Call streaming.
- **Voice Call streaming STT** (v2026.4.22): Now includes Deepgram, ElevenLabs, and Mistral alongside OpenAI/xAI. ElevenLabs adds Scribe v2 batch transcription for inbound media.
- **OpenRouter image generation** (v2026.4.23): Image gen + reference-image edits via `image_generate` using `OPENROUTER_API_KEY`.
- **Image generation hints** (v2026.4.23): Agents can now request quality, output format, background, moderation, compression, and user hints through the `image_generate` tool.
- **Tencent Cloud provider** (v2026.4.22): Bundled plugin with TokenHub onboarding, `hy3-preview` model catalog, tiered Hy3 pricing.
- **Bedrock Mantle Claude Opus 4.7** (v2026.4.22): Mantle's Anthropic Messages route with provider-owned bearer-auth streaming.
- **Codex `gpt-5.5` synthetic row** (v2026.4.23): When Codex catalog discovery omits it, OpenClaw now synthesizes the `openai-codex/gpt-5.5` OAuth row so cron and subagent runs don't fail with `Unknown model` while authenticated. **Important:** This means `openai-codex/gpt-5.5` may now work again as default model — you no longer need to swap to `gpt-5.4` if it was just unavailable due to catalog drift.
- **Local embedding context size** (v2026.4.23): `memorySearch.local.contextSize` (default 4096) for tuning local embeddings on constrained hosts.
- **Pi 0.70.0 + GPT-5.5 catalog** (v2026.4.23): Bundled Pi packages updated; OpenAI/Codex catalogs now use Pi's upstream `gpt-5.5` metadata.

**Agents / Tools:**
- **Per-call `timeoutMs` for media tools** (v2026.4.23): Agents can extend provider request timeouts for individual image/video/music/TTS generations without changing global config.
- **Forked context for `sessions_spawn`** (v2026.4.23): Optional flag lets a child inherit the requester transcript instead of starting clean.
- **Tokenjuice** (v2026.4.22): Opt-in plugin compacting noisy `exec`/`bash` results in Pi embedded runs.
- **`sessions_list` filters** (v2026.4.22): Mailbox-style filtering by label, agent, search; visibility-scoped derived titles + last-message previews.
- **`/export-trajectory`** (v2026.4.22): Default-on local trajectory capture; bundles redacted transcripts, runtime events, prompts, metadata, artifacts for reproducible debugging.
- **`/models add <provider> <modelId>`** (v2026.4.22): Register a model from chat without restarting the gateway.
- **TUI local embedded mode** (v2026.4.22): Run terminal chats without a Gateway while keeping plugin approval gates enforced.
- **Onboarding auto-installs plugins** (v2026.4.22): First-run setup now installs missing provider/channel plugins automatically.
- **`Runner:` field in `/status`** (v2026.4.22): Reports whether session runs on embedded Pi, CLI-backed provider, or ACP harness (e.g. `codex (acp/acpx)`).

**Channels:**
- **WhatsApp `replyToMode`** (v2026.4.22): Configurable native reply quoting; per-group/per-direct `systemPrompt` forwarded as `GroupSystemPrompt` (supports `"*"` wildcard) under `channels.whatsapp.accounts.<id>.{groups,direct}`.
- **WeCom channel plugin** (v2026.4.22): Surfaced during setup with refreshed display name/description.
- **Telegram media reply markdown parsing** (v2026.4.23): Remote markdown image syntax `![...](...)` is now parsed into outbound media payloads instead of falling back to plain-text URLs.
- **WhatsApp outbound media unification** (v2026.4.23): Direct sends and auto-replies use the same media normalization path.

**Codex Harness:**
- **`/status` shows active harness id** (v2026.4.23): Embedded harness selection pinned per session; non-PI harness ids like `codex` shown in `/status`. Legacy transcripts stay on PI until `/new` or `/reset`.
- **Native `request_user_input` routing** (v2026.4.23): Prompts return to originating chat; queued follow-up answers preserved.
- **Codex tool/MCP approvals through OpenClaw** (v2026.4.22+): Codex-tagged MCP tool approval elicitations route through OpenClaw plugin approvals.

**Memory:**
- **CLI `local` embedding provider** (v2026.4.23): Standalone `openclaw memory status/index/search` can now resolve local embeddings just like the gateway runtime (declared in memory-core manifest).
- **Root memory canonicalization** (v2026.4.23): Doctor now canonicalizes root durable memory on `MEMORY.md`; lowercase `memory.md` no longer treated as runtime fallback. `--fix` merges split-brain root files with backup.
- **QMD startup repair** (v2026.4.23): Stale managed QMD collections recreated when name already exists, so root memory narrows back to `MEMORY.md`.

**Macro / Other:**
- **macOS Voice Wake** (v2026.4.22): Talk Mode now supports voice wake on macOS.
- **`claude-cli` warm stdio** (v2026.4.22): Default Claude CLI runs use warm stdio sessions; resume from stored Claude session after gateway restart/idle.
- **Dreaming runs without heartbeat** (v2026.4.23): Managed dreaming cron decoupled from heartbeat; runs as isolated lightweight agent turn even when heartbeat is disabled. Doctor `--fix` migrates stale main-session dreaming jobs.
- **Failover classifies undici/Codex sentinels as `timeout`** (v2026.4.22): Bare transport failures (`terminated`, `UND_ERR_SOCKET`, etc.) and Codex `Request failed` sentinel now enter the configured fallback chain instead of surfacing as unclassified errors.

### Security Hardening (v2026.4.23 — large batch)
- Gateway agent-driven `gateway config.apply/patch` fail closed except for narrow allowlist of agent-tunable prompt/model/mention-gating paths
- Webhook `SecretRef` re-resolved per request — `secrets reload` now revokes immediately
- Teams shared Bot Framework audience tokens require verified `appid`/`azp`
- Anthropic CLI `bypassPermissions` derived from existing YOLO exec policy (no silent fallback)
- Android cleartext gateway requires loopback only; `.local`/dotless hostnames no longer treated as safe cleartext
- Pairing requires private-IP/loopback hosts for cleartext mobile pairing
- ACPX OpenClaw tools bridge no longer lists/invokes owner-only tools (e.g. `cron`)
- QQBot `/bot-approve` requires framework auth
- Discord native slash-command channel policy honors owner/member restrictions
- Android `ASK_OPENCLAW` intents only prefill draft, never auto-send

### Key Fixes (highlights)
- **WhatsApp duplicate cron sends** (v2026.4.23): In-memory active-delivery claim prevents concurrent reconnect drain from re-driving same pending entry. Fixes 7-12x duplicate sends after 30-min inbound-silence watchdog.
- **CLI streaming state preserved during CLI-backed runs** (v2026.4.22+): WebChat keeps visible response state until the backend finishes.
- **Webchat image attachments preserved for text-only models** (v2026.4.23): Offloaded as media refs instead of dropped, so configured image tools can still inspect originals.
- **OpenAI/Codex transcript replay** (v2026.4.23): No longer synthesizes missing tool results (preserved on Anthropic/Gemini/Bedrock).
- **Cache tokens included in context %** (v2026.4.22): Footer no longer shows `0% ctx` while `/status` reports substantial use.
- **`models auth login` merges defaults** (v2026.4.22): Re-authenticating an OAuth provider no longer wipes other providers' aliases/per-model params (use `replaceDefaultModels` to opt into replace).
- **Kimi tool_call IDs preserved** (v2026.4.22): Stop strict-sanitizing `functions.<name>:<index>` IDs on OpenAI-compatible transport — fixes multi-turn agentic flows breaking after 2-3 rounds.
- **Stainless SDK Retry-After capped** (v2026.4.22): Long retry windows surface immediately for OpenClaw failover instead of blocking.
- **Config `--merge` and `--replace`** (v2026.4.22): `config set --merge` for additive provider model allowlist updates; `--replace` for intentional full clobbers.

### New Config Keys (v2026.4.22–4.23)
| Config Path | Type | Description |
|---|---|---|
| `agents.defaults.promptOverlays.gpt5.personality` | boolean | Global friendly-style toggle for GPT-5 prompt overlay (was OpenAI-plugin-only) |
| `channels.whatsapp.accounts.<id>.groups.<id>.systemPrompt` | string | Per-WhatsApp-group system prompt forwarded as `GroupSystemPrompt` |
| `channels.whatsapp.accounts.<id>.direct.<id>.systemPrompt` | string | Per-direct-chat system prompt forwarded as `GroupSystemPrompt` |
| `channels.whatsapp.replyToMode` | string | Configurable native WhatsApp reply quoting mode |
| `memorySearch.local.contextSize` | number | Local embedding context size (default 4096) |
| `tools.exec.allowPrivateNetwork` (per-provider) | boolean | Opt-in for private-network image gen endpoints (LocalAI, etc.) |

### New Troubleshooting Entries (v2026.4.22–4.23)
| Symptom | Cause | Fix |
|---------|-------|-----|
| `Unknown model: openai-codex/gpt-5.5` even though account is authenticated | Codex catalog discovery omitted the row pre-v2026.4.23 | v2026.4.23 synthesizes the `gpt-5.5` OAuth row when discovery skips it. Upgrade and the model becomes available again. |
| `openai/gpt-image-2` fails with no `OPENAI_API_KEY` | Image gen previously required API-key auth path | v2026.4.23 routes through Codex OAuth when an `openai-codex` profile is active |
| `~/.codex` OAuth material copied into agent auth stores | Codex CLI auth import was on by default | v2026.4.22 removes import path. Use browser login or device pairing |
| `models auth login` wipes other providers' model aliases | Default-model addition replaced full map | Fixed v2026.4.22 — additions merge by default. Use `replaceDefaultModels` for intentional clobber |
| WhatsApp cron sends duplicate 7-12x after silence watchdog | Reconnect drain re-drove pending entries during live delivery | Fixed v2026.4.23 — in-memory active-delivery claim added |
| Multi-turn Kimi tool calls break after 2-3 rounds | Strict sanitization mangled `functions.<name>:<index>` IDs | Fixed v2026.4.22 — Moonshot now opts out via `sanitizeToolCallIds: false` in OpenAI-compat transport |
| Footer shows `0% ctx` but `/status` reports high usage | Cache-read/write tokens excluded from message footer | Fixed v2026.4.22 |
| Telegram group images sent as plain-text URLs | Markdown image syntax not parsed into outbound media | Fixed v2026.4.23 — `![...](...)` now produces media payloads |
| OpenAI/Codex replay synthesizes missing tool results | Synthetic repair was applied across all providers | Fixed v2026.4.23 — only Anthropic/Gemini/Bedrock get synthetic repair now |
| `lowercase memory.md` overrides root MEMORY.md | Doctor previously treated lowercase as runtime fallback | Fixed v2026.4.23 — root canonicalizes on `MEMORY.md`; `--fix` merges with backup |
| Long Stainless SDK `Retry-After` blocks failover | 60s+ retry sleeps weren't capped | Fixed v2026.4.22 — capped, surfaces for OpenClaw failover |

---

## What's New in v2026.4.5–4.21

### Breaking / Noteworthy Defaults
- **Plugins require matching host** (v2026.4.10+): Bundled plugins now declare a minimum OpenClaw version. A gateway older than the plugin refuses to load that plugin with `plugin requires OpenClaw >=X.Y.Z`. Always upgrade the core and restart the gateway in one pass — running `openclaw update --yes` followed by `openclaw gateway stop && openclaw gateway start` avoids the transient validation failure.
- **Default Anthropic model = Claude Opus 4.7** (v2026.4.15): Anthropic selections, `opus` alias, Claude CLI defaults, and bundled image understanding all default to `claude-opus-4.7`. Opus 4.7 also supports a new `xhigh` reasoning effort that is separate from `adaptive`.
- **Default image generator = `gpt-image-2`** (v2026.4.21): Bundled OpenAI image provider and live smoke tests default to `gpt-image-2`; 2K/4K OpenAI size hints are now advertised.
- **Dreaming storage default = `separate`** (v2026.4.15): `dreaming.storage.mode` defaults to `separate` — dream phase blocks now land in `memory/dreaming/{phase}/YYYY-MM-DD.md` instead of being injected into daily memory files. Opt back in with `plugins.entries.memory-core.config.dreaming.storage.mode: "inline"`.
- **OpenAI Codex canonical alias** (v2026.4.14): `openai-codex/gpt-5.4-codex` is now a runtime alias for `openai-codex/gpt-5.4`. Per-model overrides still work on either id.
- **Config `$schema` preservation** (v2026.4.15): Partial config rewrites preserve a root-authored `$schema` field instead of stripping or rewriting it. Safe to pin in `openclaw.json`.
- **Enforced owner identity for owner-only commands** (v2026.4.21): When `enforceOwnerForCommands=true` and `commands.ownerAllowFrom` is unset, non-owner senders with wildcard `allowFrom` are no longer treated as owners. Set explicit `commands.ownerAllowFrom` if you relied on the permissive fallback.
- **`browser.cdpUrl` now redacted** (v2026.4.14): Base `browser.cdpUrl` and per-profile `browser.profiles.*.cdpUrl` are redacted in `config.get` output and availability errors. Safe to inspect config.

### New Features

**Providers / Models:**
- **LM Studio provider** (v2026.4.12): Bundled provider with onboarding, runtime model discovery, stream preload, and memory-search embeddings for local/self-hosted OpenAI-compatible models.
- **Codex as dedicated provider** (v2026.4.12): `codex/gpt-*` uses Codex-managed auth, native threads, model discovery, and compaction. `openai/gpt-*` stays on the normal OpenAI provider path.
- **OpenAI `gpt-5.4-pro`** (v2026.4.14): Forward-compat support with Codex pricing/limits.
- **Claude Opus 4.7 `xhigh` reasoning** (v2026.4.18): New highest-reasoning mode, distinct from `adaptive`.
- **Google Gemini TTS** (v2026.4.15): Bundled `google` plugin now includes TTS with voice selection, WAV reply output, and PCM telephony output.
- **GitHub Copilot memory embeddings** (v2026.4.15): Dedicated Copilot embedding provider for memory search; plugins can reuse the transport.
- **Moonshot Kimi K2.6** (v2026.4.20): New default for Moonshot setup, web search, and media understanding. `thinking.keep = "all"` supported on `kimi-k2.6`.
- **LanceDB cloud storage** (v2026.4.15): `memory-lancedb` supports remote object-storage indexes.
- **macOS MLX speech provider** (v2026.4.12): Experimental local Talk Mode provider with utterance playback and interruption handling.

**Agents / Memory:**
- **Active Memory plugin** (v2026.4.12): Dedicated memory sub-agent that runs right before the main reply — auto-pulls preferences and prior context without manual "remember this" prompts. Configurable message/recent/full modes with `/verbose` inspection. Docs: https://docs.openclaw.ai/concepts/active-memory.
- **Experimental local-model lean mode** (v2026.4.15): Set `agents.defaults.experimental.localModelLean: true` to drop heavyweight default tools (`browser`, `cron`, `message`) for weaker local models.
- **Subagent registry lazy runtime** (v2026.4.14): Published `dist/agents/subagent-registry.runtime.js` so `runtime: "subagent"` no longer stalls queued.
- **Streaming watchdog** (v2026.4.15): Client-side `streamingWatchdogMs` (default 30s, `0` to disable) resets the TUI `streaming` indicator to `idle` when deltas stop arriving, so lost final events don't wedge the UI.

**Channels:**
- **Feishu document-thread sessions** (v2026.4.11): Rich comment parsing, comment reactions, and typing feedback for doc-comment conversations.
- **Microsoft Teams reactions** (v2026.4.11): Add/list reactions via delegated OAuth while keeping application-auth read paths.
- **Matrix MSC4357 live markers** (v2026.4.12): Draft previews emit live/typewriter markers for supporting clients.
- **Mattermost draft preview streaming** (v2026.4.20): Thinking, tool activity, and partial reply all stream into a single draft post that finalizes in place.
- **Discord auto-archive for threads** (confirmed): `channels.discord.guilds.<id>.channels.<id>.autoArchiveDuration` with `1h`/`1d`/`3d`/`1w`.
- **Telegram forum topic names in context** (v2026.4.14): Human topic names learned from Telegram service messages appear in agent context, prompt metadata, and plugin hook metadata. Persisted to the Telegram session sidecar so topic names survive restarts.
- **BlueBubbles per-group `systemPrompt`** (v2026.4.20): Forwarded into inbound context as `GroupSystemPrompt` (supports `"*"` wildcard). BlueBubbles also gets `channels.bluebubbles.sendTimeoutMs` (default 30s, was 10s) for macOS 26 setups, method pinning (`private-api` vs `apple-script`) to prevent silent drops, and a persistent file-backed GUID dedupe so webhook replays after restart don't re-reply.
- **BlueBubbles catchup** (v2026.4.15): Per-account cursor + `/api/v1/message/query?after=<ts>` replay of missed messages after gateway downtime. Includes `catchup.maxFailureRetries` (default 10) so a malformed message can't wedge the cursor forever.
- **WhatsApp multi-account hardening** (v2026.4.18): Centralized named-account inbound policy with per-account group activation, scoped session keys, and legacy activation backfill.

**Control / UI:**
- **Control UI webchat rich bubbles** (v2026.4.11): Media/reply/voice directives render as structured bubbles; new `[embed ...]` tag with external URL gate.
- **Control UI Overview - Model Auth status card** (v2026.4.15): Shows OAuth token health + provider rate-limit pressure. Backed by a new `models.authStatus` RPC.
- **Dashboard v2** (earlier, consolidated v2026.4): Overview, chat, config, agent, session views plus command palette and mobile bottom tabs.

**Cron / Tasks:**
- **Cron state file split** (v2026.4.20): Runtime state lives in `jobs-state.json` so `jobs.json` can be git-tracked cleanly.
- **Cron `--tools` per-job allowlists** (confirmed): Embedded run tool policy + explicit targeting + internal events all take effect at runtime again.
- **Opt-in compaction notices** (v2026.4.20): `agents.defaults.compaction.notifyUser: true` sends start and completion messages during context compaction.

**Gateway / Infra:**
- **`gateway commands.list` RPC** (v2026.4.12): Remote clients can discover runtime-native, text, skill, and plugin commands with serialized argument metadata.
- **`exec-policy` CLI** (v2026.4.12): New local `openclaw exec-policy show|preset|set` subcommand to sync requested `tools.exec.*` config with the local exec approvals file.
- **Per-provider `allowPrivateNetwork`** (v2026.4.12): `models.providers.*.request.allowPrivateNetwork` for trusted self-hosted OpenAI-compatible endpoints.
- **Plugin setup descriptors** (v2026.4.11): Plugin manifests can declare activation and setup descriptors so setup flows describe required auth and pairing without hardcoded core branches.
- **Bundled plugin platform-native repair** (v2026.4.14): Repackaged Windows installs can recover dependencies packed on another host OS.
- **Doctor systemd hardening** (v2026.4.14): `openclaw doctor --repair` stops re-embedding dotenv-backed secrets in user systemd units.

### Key Fixes (highlights)
- **Unknown-tool stream guard always on** (v2026.4.15): Previously `tools.loopDetection.enabled=true` was required; now on by default. Hallucinated/removed tools no longer loop `Tool X not found` until timeout. Per-run override: `tools.loopDetection.unknownToolThreshold` (default 10).
- **Skills cache invalidation on config write** (v2026.4.15): Removing a bundled skill from `skills.allowBundled` now invalidates per-session `skillsSnapshot` so the model stops calling the disabled tool.
- **Ollama provider-policy defaults** (v2026.4.20): Implicit local discovery runs before config validation rejects minimal Ollama configs. Chat requests no longer 404 because of stale `ollama/` prefix forwarding (v2026.4.15 fix).
- **Telegram polling watchdog raised 90s → 120s** (v2026.4.20): Long-running Telegram work no longer trips false stall restarts. Configurable per-account: `channels.telegram.pollingStallThresholdMs`.
- **Telegram undici dispatcher lifecycle** (v2026.4.18): Every recoverable network error + watchdog trip previously abandoned the dispatcher pool, accumulating hundreds of `api.telegram.org` connections. Fixed with per-origin pool caps and an explicit `close()` lifecycle.
- **Telegram DM binding survives restarts** (v2026.4.18): Stale ACP DM bindings are dropped on restart; plugin-owned bindings preserved.
- **Feishu webhook fail-closed** (v2026.4.15): Webhook transport refuses to start without `encryptKey`, rejects unsigned requests instead of accepting them.
- **Active Memory graceful degradation** (v2026.4.20): When memory recall fails during prompt building, the reply continues without memory context instead of failing the whole turn. Recall timeout ceiling raised to 120s.
- **Dreaming narrative cleanup** (v2026.4.12+): Transient narrative cleanup retries timed-out deletes; stale dreaming session artifacts cleaned through lock-aware path; narrative session keys isolated per workspace.
- **OpenAI Codex OAuth stability** (v2026.4.18): External CLI OAuth imports are runtime-only, canonical imported CLI profiles preserved, refresh recovery stable, legacy identity-less main-store OAuth upgrades cleanly.
- **Gateway/pairing loopback** (v2026.4.20): Loopback shared-secret node-host, TUI, and gateway clients treated as local for pairing, so trusted local tools no longer fail with `pairing required` after reconnect.
- **Sessions/reset clearing** (v2026.4.20): `/new` and `/reset` now clear auto-sourced model/provider/auth-profile overrides while preserving explicit user selections.
- **Auto-reply billing classification** (v2026.4.14): Pure billing cooldown fallbacks show billing guidance instead of the generic failure reply.
- **Claude CLI session expiration** (v2026.4.14): `No conversation found with session ID` now classified as `session_expired` — stale binding clears and recovers next turn.
- **Third-party context engine tolerance** (v2026.4.15): Plugins whose `info.id` differs from registered slot id are accepted again (v2026.4.14 tightening is relaxed back).

### New Config Keys (v2026.4.5–4.21)
| Config Path | Type | Description |
|---|---|---|
| `agents.defaults.experimental.localModelLean` | boolean | Drop heavyweight default tools (`browser`, `cron`, `message`) for weak local models |
| `agents.defaults.compaction.notifyUser` | boolean | Opt-in start + completion notices during context compaction (note: some earlier mentions called this an alternative path; confirmed as opt-in) |
| `channels.bluebubbles.sendTimeoutMs` | number | Outbound `/api/v1/message/text` send timeout (default 30s, was 10s). Per-account supported. |
| `channels.discord.guilds.<id>.channels.<id>.autoArchiveDuration` | string | `1h` \| `1d` \| `3d` \| `1w` — auto-archive for auto-created threads |
| `channels.matrix.network.dangerouslyAllowPrivateNetwork` | boolean | Honored when creating Matrix clients for private-network homeservers |
| `channels.telegram.pollingStallThresholdMs` | number | Polling watchdog threshold (default 120s). Per-account supported. |
| `commands.ownerAllowFrom` | array | Explicit owner identity allowlist when `enforceOwnerForCommands=true` |
| `dreaming.storage.mode` | string | `separate` (new default) \| `inline`. In `memory-core.config.dreaming.storage`. |
| `dreaming.timezone` | string | Host-local TZ for dream diary timestamps |
| `models.providers.*.request.allowPrivateNetwork` | boolean | Per-provider opt-in for private-network request targets |
| `models.providers.*.models.*.compat.supportsPromptCacheKey` | boolean | OpenAI-compat proxies: forward vs strip `prompt_cache_key` |
| `plugins.entries.memory-core.config.dreaming.storage.mode` | string | Opt-in `inline` dreaming storage |
| `plugins.slots.memory` | string | `"none"` to explicitly disable bundled memory-core |
| `tools.loopDetection.unknownToolThreshold` | number | Per-run unknown-tool retry guard threshold (default 10) |
| `streamingWatchdogMs` | number | Client-side streaming watchdog (default 30s, `0` to disable) |

### New Troubleshooting Entries (v2026.4.5–4.21)
| Symptom | Cause | Fix |
|---|---|---|
| `plugin requires OpenClaw >=X.Y.Z, but this host is Y.Y.Y` after `openclaw update` | Plugin updated to a version newer than the currently-running gateway | Restart gateway: `openclaw gateway stop && openclaw gateway start`. If the binary didn't upgrade, re-run `openclaw update --yes` and verify with `openclaw --version` |
| `install.runtime-*.js` module-not-found during plugin update | Stale hashed dist chunks from prior install | v2026.4.12+ prunes stale chunks after npm upgrades; re-run `openclaw update` |
| Agent reports wrong/old model after Opus 4.7 rollout | Session's `authProfileOverride` pinned to old auth profile | Set `authProfileOverride: null` in `sessions.json` or delete the session |
| GPT model replies empty on OpenAI with `/think low` | `low` reasoning not supported on GPT-5.4 mini models | v2026.4.14 remaps `low`/`minimal` → `medium` for affected mini models. Upgrade to v2026.4.14+ |
| Telegram polling shows healthy but messages stop flowing | Transport dispatcher pool leaked sockets on every recoverable error | Upgrade to v2026.4.18+ (bounded keep-alive + strict per-origin pool caps) |
| `Tool X not found` loop until embedded-run timeout | Disabled bundled skill still cached in session snapshot | v2026.4.15+ invalidates snapshot when `skills.*` config changes. Force a reset: `echo '{}' > ~/.openclaw/agents/<agent>/sessions/sessions.json` |
| BlueBubbles: 10s `private-api` send aborts on macOS 26 | Default timeout too aggressive | Upgrade to v2026.4.20+ (default 30s) or set `channels.bluebubbles.sendTimeoutMs` explicitly |
| BlueBubbles: agent replies twice after BB Server restart | Message replays through webhook + gateway lost dedupe state | v2026.4.15+ adds persistent file-backed GUID dedupe — upgrade to recover automatically |
| Matrix `requireMention` breaks when user types `@displayName` | Display-name mentions weren't matching the gating rule | Fixed v2026.4.14 — accepts visible `@displayName` Matrix URI labels |
| Ollama chat 404s with `ollama/qwen3:14b-q8_0` | Legacy `ollama/` prefix sent to Ollama API | Fixed v2026.4.15 — prefix is stripped before request |
| Feishu webhook transport silently starts without `encryptKey` | Fail-open default accepted unsigned requests | v2026.4.15 fail-closes — configure `encryptKey` or transport refuses to start |
| Dreaming entries render as `confidence: 0.00` | Light-sleep confidence computed from recall-only counts | Fixed v2026.4.12 — uses all recorded short-term signals |
| Daily memory file dominated by dream phase blocks | `dreaming.storage.mode` was `inline` | v2026.4.15 defaults to `separate`. Set to `inline` to opt back in |
| `agent.json` rewrites lose custom `$schema` field | Partial config rewrites stripped root `$schema` | Fixed v2026.4.15 — root `$schema` preserved |
| `models list --probe` reports invalid models as `unknown` | Misclassification of format errors | Fixed v2026.4.15 — returns `format` now |
| Codex/gpt-5.4 hits `/backend-api/responses` and 404s | Alias removed upstream | Fixed v2026.4.20 — routes through `/backend-api/codex` |
| `/think off` sends `reasoning.effort: "none"` to GPT reasoning models | Unsupported payload on OpenAI Responses | Fixed v2026.4.20 — disabled reasoning payloads omitted entirely |
| Kimi reasoning re-enables after `/new` | Stale session `/think` state | v2026.4.20 defaults bundled Kimi thinking to off and normalizes Anthropic-compat `thinking` payloads |
| TUI stuck on `streaming` after gateway restart | Lost `state: "final"` event | v2026.4.15 adds 30s streaming watchdog (configurable via `streamingWatchdogMs`) |
| Non-owner senders can trigger owner-only commands | `enforceOwnerForCommands=true` with wildcard `allowFrom` and unset `commands.ownerAllowFrom` | v2026.4.21 requires explicit owner identity — set `commands.ownerAllowFrom` to restore access |

---

## What's New in v2026.3.14–4.2

### Breaking Changes
- **`x_search` config path** (v2026.4.2): Moved from `tools.web.x_search.*` to `plugins.entries.xai.config.xSearch.*`. Auth moved to `plugins.entries.xai.config.webSearch.apiKey` / `XAI_API_KEY`. Run `openclaw doctor --fix` to migrate.
- **Firecrawl `web_fetch` config** (v2026.4.2): Moved from `tools.web.fetch.firecrawl.*` to `plugins.entries.firecrawl.config.webFetch.*`. Run `openclaw doctor --fix` to migrate.
- **`nodes.run` removed** (v2026.3.31): Shell wrapper removed from CLI and agent tools. Use `exec host=node` instead; keep media/location/notify on `nodes invoke`.
- **Plugin SDK compat shims deprecated** (v2026.3.31): Legacy provider compat subpaths emit migration warnings. Use `openclaw/plugin-sdk/*` entrypoints going forward.
- **`trusted-proxy` auth** (v2026.3.31): Rejects mixed shared-token configs; local-direct fallback now requires the configured token.
- **Node commands disabled until pairing** (v2026.3.31): Node commands stay disabled until node pairing is approved (device pairing alone no longer enough).
- **Qwen `qwen-portal-auth` removed** (v2026.3.28): Migrate to Model Studio with `openclaw onboard --auth-choice modelstudio-api-key`.
- **Config doctor drops old migrations** (v2026.3.28): Auto-migrations older than two months now fail validation instead of being rewritten.
- **Exec defaults to YOLO** (v2026.4.2): Gateway/node host exec now defaults to `security=full` with `ask=off`.

### New Features

**Background Tasks** (v2026.3.31–4.2): Full durable task control plane with SQLite-backed ledger. Unifies ACP, subagent, cron, and CLI execution. New `openclaw tasks list|show|cancel` CLI. `/tasks` chat command shows session task board. Task Flow substrate for managed orchestration with durable state tracking.

**New Channels:**
- **QQ Bot** (v2026.3.31): Bundled channel plugin with multi-account setup, SecretRef-aware credentials, slash commands, reminders, media send/receive.
- **Microsoft Teams** (v2026.3.24): Migrated to official Teams SDK with streaming 1:1 replies, welcome cards, prompt starters, feedback/reflection, native AI labeling, edit/delete support.

**CLI Changes:**
- `openclaw config schema` — Print JSON schema for `openclaw.json` (v2026.3.28).
- `openclaw config set` — Now supports `--ref-provider`, `--batch-file`, and SecretRef builder modes (v2026.4.2).
- `openclaw skills install/search/update` — ClawHub skills management integrated into main CLI (v2026.3.24+).
- `openclaw tasks` — Inspect durable background task state (v2026.3.31+).
- `openclaw plugins inspect` — Replaces `plugins info` (v2026.4.2).
- `openclaw plugins marketplace` — Browse Claude-compatible plugin marketplaces (v2026.4.2).
- `openclaw --container <name>` — Run CLI inside a Docker/Podman container (v2026.3.24+).
- `gateway --cli-backend-logs` — Replaces `--claude-cli-logs` (deprecated alias kept) (v2026.3.28).
- `hooks install/update` — Deprecated; use `plugins install/update` instead (v2026.4.2).

**Plugins:**
- `before_tool_call` hooks can now `requireApproval` (v2026.3.28) — plugins can pause tool execution for user approval.
- `before_agent_reply` hook (v2026.4.2) — plugins can short-circuit LLM with synthetic replies.
- `before_dispatch` hook (v2026.3.24) — canonical inbound metadata with routed delivery.
- Plugin marketplace browsing via `plugins marketplace` (v2026.4.2).
- xAI/Grok: Moved to Responses API with first-class `x_search` (v2026.3.28).

**Agents/Models:**
- `agents.defaults.params` for global default provider parameters (v2026.4.2).
- `agents.defaults.compaction.notifyUser` — opt-in compaction start notice (v2026.4.2).
- `auth.cooldowns.rateLimitedProfileRotations` — configurable retry count for same-provider rate-limit retries (v2026.4.2).
- Per-job tool allowlists for cron: `openclaw cron --tools` (v2026.4.2).
- Amazon Bedrock Guardrails support (v2026.4.2).
- SearXNG web search provider plugin (v2026.4.2).
- macOS Voice Wake for Talk Mode (v2026.4.2).

**Channels:**
- Telegram: Configurable `errorPolicy` and `errorCooldownMs` per account/chat/topic (v2026.4.2).
- WhatsApp: `reactionLevel` guidance for agent emoji reactions; inbound message timestamps in model context (v2026.4.2).
- Matrix: `blockStreaming` opt-in, `channels.matrix.proxy` config, `historyLimit` for group context, DM `threadReplies` overrides, draft streaming (v2026.3.31).
- Feishu: Drive comment-event flow with `feishu_drive` comment actions (v2026.4.2).
- Slack: Native exec approval routing, `upload-file` action (v2026.3.28–3.31).
- Discord: Voice channel guild/member allowlist enforcement on spoken ingress (v2026.3.31).

**Gateway:**
- `gateway.webchat.chatHistoryMaxChars` for configurable chat history truncation (v2026.4.2).
- `/v1/models` and `/v1/embeddings` OpenAI compatibility endpoints (v2026.3.24).
- MCP: Remote HTTP/SSE server support in `mcp.servers` with auth headers (v2026.3.31).

### New Config Keys (v2026.3.14–4.2)
| Config Path | Type | Description |
|---|---|---|
| `agents.defaults.params` | object | Global default provider parameters |
| `agents.defaults.compaction.notifyUser` | boolean | Opt-in compaction start notice (default: shown) |
| `auth.cooldowns.rateLimitedProfileRotations` | number | Same-provider rate-limit retries before fallback |
| `channels.matrix.proxy` | string | HTTP(S) proxy for Matrix traffic |
| `channels.matrix.historyLimit` | number | Room history context lines for group triggers |
| `channels.matrix.blockStreaming` | boolean | Opt-in block streaming for Matrix |
| `gateway.webchat.chatHistoryMaxChars` | number | Chat history text truncation limit |
| `plugins.entries.xai.config.xSearch.*` | object | xAI x_search settings (moved from `tools.web.x_search`) |
| `plugins.entries.firecrawl.config.webFetch.*` | object | Firecrawl web_fetch settings (moved from `tools.web.fetch.firecrawl`) |

### New Troubleshooting Entries (v2026.3.14–4.2)
| Symptom | Cause | Fix |
|---------|-------|-----|
| `x_search` config rejected after upgrade to v2026.4.2 | Config path moved to plugin-owned path | Run `openclaw doctor --fix` to auto-migrate |
| Firecrawl `web_fetch` config rejected after upgrade | Config path moved to plugin-owned path | Run `openclaw doctor --fix` to auto-migrate |
| `nodes.run` command not found | Removed in v2026.3.31 | Use `exec host=node` for shell execution |
| Exec runs without asking for approval | Default changed to YOLO mode (`ask=off`) in v2026.4.2 | Set `tools.exec.ask: "always"` to restore prompts |
| Task registry hangs gateway after startup | SQLite maintenance sweep stalling event loop | Fixed in v2026.4.1 |
| `openclaw gateway stop` leaves loopback pairing errors | Legacy role fallback missing for empty paired-device maps | Fixed in v2026.4.2 |
| `sessions_spawn` fails with `pairing required` (1008) after v2026.3.31 | Admin-only subagent calls not pinned to `operator.admin` | Fixed in v2026.4.2 |
| `qwen-portal-auth` OAuth broken | Deprecated in v2026.3.28 | Use `openclaw onboard --auth-choice modelstudio-api-key` |

---

## What's New in v2026.3.12–3.13

### Security (v2026.3.12 — Major Security Release)
- **Workspace plugins**: Disable implicit workspace plugin auto-load — cloned repos can't execute workspace plugin code without explicit trust (GHSA-99qw-6mr3-36qr)
- **Exec detection**: Normalize compatibility Unicode and strip invisible formatting code points before obfuscation checks (GHSA-9r3v-37xh-2cf6)
- **Exec allowlist**: Preserve POSIX case sensitivity, keep `?` within single path segment (GHSA-f8r2-vg7x-gh8m)
- **Device pairing**: Bootstrap setup codes now short-lived and single-use (v2026.3.13); device-token scopes capped to approved baseline (GHSA-2pwv-x786-56f8)
- **WebSocket preauth**: Shorten unauthenticated handshake retention, reject oversized pre-auth frames (GHSA-jv4g-m82p-2j93)
- **Browser.request**: Block persistent browser profile create/delete from write-scoped `browser.request` (GHSA-vmhq-cqm9-6p7q)
- **Agent spawn**: Reject public spawned-run lineage fields, keep workspace inheritance on internal path (GHSA-2rqg-gjgv-84jm)
- **Session status**: Enforce sandbox session-tree visibility and agent-to-agent access guards (GHSA-wcxr-59v9-rxr8)
- **Feishu webhook**: Require `encryptKey` alongside `verificationToken` in webhook mode (GHSA-g353-mgv3-8pcj)
- **LINE webhook**: Require signatures for empty-event POST probes (GHSA-mhxh-9pjm-w7q5)
- **Zalo webhook**: Rate limit invalid secret guesses before auth (GHSA-5m9r-p9g7-679c)
- **Slack/Teams routing**: Require stable channel/team IDs for allowlist routing; mutable name matching via `dangerouslyAllowNameMatching` break-glass flag
- **iMessage/remote attachments** (v2026.3.13): Reject unsafe remote attachment paths before spawning SCP
- **Telegram/webhook auth** (v2026.3.13): Validate secret before reading request bodies
- **Exec approvals** (v2026.3.12–3.13): Multiple hardening rounds — unwrap `pnpm`/`npm exec`/`npx` runners, fail closed for Ruby/Perl/PowerShell loaders, bind macOS skill trust to both name and path, treat backslash-newline as line continuation

### New Features

**Dashboard v2** (v2026.3.12): Modular overview, chat, config, agent, session views + command palette + mobile bottom tabs + slash commands + search/export/pinned messages.

**Fast Mode** (v2026.3.12): `/fast` toggle for OpenAI GPT-5.4 and Anthropic Claude, with `params.fastMode` mapping to `service_tier` requests. Configurable per-session via TUI, Control UI, and ACP.

**Agents:**
- `sessions_yield` (v2026.3.12): End current turn immediately, skip queued tool work, carry hidden follow-up payload into next turn.

**Browser** (v2026.3.13):
- Chrome DevTools MCP attach mode for signed-in live Chrome sessions (`chrome://inspect/#remote-debugging`)
- Built-in `profile="user"` (logged-in host browser) and `profile="chrome-relay"` (extension relay)
- Batched actions, selector targeting, delayed clicks for browser act requests

**Channels:**
- Slack Block Kit: `channelData.slack.blocks` in reply delivery path (v2026.3.12)
- Slack interactive replies: Opt-in button and select directives via `channels.slack.capabilities.interactiveReplies` (v2026.3.12)

**Models/Plugins** (v2026.3.12): Ollama, vLLM, SGLang moved to provider-plugin architecture with provider-owned onboarding and discovery.

**Docker** (v2026.3.13): `OPENCLAW_TZ` env var to pin gateway/CLI containers to chosen IANA timezone.

### Key Fixes (v2026.3.12–3.13)
- Ollama: Stop promoting native `thinking`/`reasoning` fields into final assistant text (v2026.3.13)
- Dashboard v2: Stop reloading full chat history on every live tool result (v2026.3.13)
- Gateway: Reject unanswered RPC calls after bounded timeout; preserve `lastAccountId`/`lastThreadId` across session resets (v2026.3.13)
- Config validation: Accept `agents.list[].params`, `tools.web.fetch.readability`, `tools.web.fetch.firecrawl`, `channels.signal.groups`, `discovery.wideArea.domain` (v2026.3.13)
- Telegram: Thread proxy transport policy into SSRF-guarded file fetches; redact file URLs in error logs (v2026.3.13)
- Discord: Treat transient `/gateway/bot` failures as transient startup errors; honor raw `guild_id` for allowlists (v2026.3.13)
- Agents: Classify z.ai `network_error` as retryable; recognize Venice/Poe billing errors for fallback; preserve blank API keys for loopback providers (v2026.3.13)
- Windows: Bound `schtasks` calls and fall back to Startup-folder; resolve fallback listeners for gateway stop (v2026.3.13)

### New Config Keys (v2026.3.12–3.13)
| Config Path | Type | Description |
|---|---|---|
| `channels.slack.capabilities.interactiveReplies` | boolean | Opt-in Slack button and select reply directives (default: false) |
| `params.fastMode` | boolean | Per-session fast mode for OpenAI/Anthropic |
| `channels.zalouser.dangerouslyAllowNameMatching` | boolean | Break-glass for mutable Zalouser group-name matching |
| `channels.slack.dangerouslyAllowNameMatching` | boolean | Break-glass for mutable Slack channel-name matching |
| `channels.teams.dangerouslyAllowNameMatching` | boolean | Break-glass for mutable Teams channel-name matching |
| `OPENCLAW_TZ` | env var | Docker timezone pinning (IANA format) |
| `agents.list[].params` | object | Per-agent runtime overrides (cacheRetention, temperature, maxTokens) |
| `tools.web.fetch.readability` | object | Web fetch readability config |
| `tools.web.fetch.firecrawl` | object | Web fetch Firecrawl config |
| `channels.signal.groups` | object | Per-group Signal overrides (requireMention, tools, toolsBySender) |
| `discovery.wideArea.domain` | string | Unicast DNS-SD gateway config |
| `openclaw gateway status --require-rpc` | CLI flag | Fail hard on RPC probe misses |

### New Troubleshooting Entries (v2026.3.12–3.13)
| Symptom | Cause | Fix |
|---------|-------|-----|
| Ollama local reasoning model leaks thinking in replies | Native `thinking`/`reasoning` fields promoted to assistant text | Fixed in v2026.3.13 — internal thoughts no longer leak |
| Dashboard v2 UI freezes during tool-heavy runs | Full chat history reloaded on every live tool result | Fixed in v2026.3.13 |
| `agents.list[].params` rejected by config validation | Schema didn't accept per-agent runtime overrides | Fixed in v2026.3.13 |
| `tools.web.fetch.readability` rejected as unrecognized | Schema validation missing for web fetch config | Fixed in v2026.3.13 |
| `channels.signal.groups` rejected by config validation | Schema didn't support per-group Signal overrides | Fixed in v2026.3.13 |
| `discovery.wideArea.domain` rejected by config validation | Schema missing for unicast DNS-SD config | Fixed in v2026.3.13 |
| Slack/Teams allowlists bypassed by channel name changes | Name-based matching allowed mutable IDs | v2026.3.12: Use stable IDs; opt into name matching via `dangerouslyAllowNameMatching` |
| Telegram inbound media fails on IPv6-broken hosts | SSRF-guarded file downloads didn't retry with IPv4 | Fixed in v2026.3.13 — IPv4 fallback applied |
| Discord gateway crashes on startup | Plain-text `/gateway/bot` failures treated as fatal | Fixed in v2026.3.13 — treated as transient |
| Windows `openclaw gateway install` hangs forever | `schtasks` call blocks indefinitely | Fixed in v2026.3.13 — bounded + Startup-folder fallback |

---

## What's New in v2026.3.8–3.11

### Security
- **Gateway/WebSocket origin validation** (v2026.3.11): Browser-originated connections in `trusted-proxy` mode now enforce origin validation (GHSA-5wcw-8jjv-m286).

### Breaking Changes
- **Cron/doctor: isolated cron delivery** (v2026.3.11): Cron jobs can no longer notify through ad hoc agent sends or fallback main-session summaries. Run `openclaw doctor --fix` for migration.

### New Features
- **OpenRouter models** (v2026.3.11): Temporary Hunter Alpha and Healer Alpha entries.
- **iOS/Home canvas** (v2026.3.11): Bundled welcome screen + docked toolbar replacing floating controls.
- **macOS/chat UI** (v2026.3.11): Chat model picker, persistent thinking-level selections.
- **Onboarding/Ollama** (v2026.3.11): First-class Ollama setup with Local or Cloud+Local modes, browser-based cloud sign-in, curated model suggestions.
- **OpenCode/onboarding** (v2026.3.11): New OpenCode Go provider (Zen and Go treated as one setup).
- **Memory multimodal** (v2026.3.11): Opt-in multimodal image and audio indexing for `memorySearch.extraPaths` with Gemini `gemini-embedding-2-preview`.
- **Memory/Gemini embeddings** (v2026.3.11): `gemini-embedding-2-preview` support with configurable output dimensions.
- **Discord/auto threads** (v2026.3.11): `autoArchiveDuration` channel config (1h, 1d, 3d, 1w).
- **ACP/sessions_spawn** (v2026.3.11): Optional `resumeSessionId` for `runtime: "acp"` to resume existing ACPX/Codex conversations.
- **Gateway/node pending work** (v2026.3.11): Narrow in-memory pending-work queue primitives.
- **Exec/child commands** (v2026.3.11): `OPENCLAW_CLI` env var marks child command environments.
- **Git/runtime state** (v2026.3.11): `.dev-state` file auto-ignored.

### Key Fixes (v2026.3.9–3.11)
- Agents/text sanitization: strip leaked model control tokens (`<|...|>` and full-width variants) from user-facing text (GLM-5, DeepSeek).
- Discord/reply chunking: resolve effective `maxLinesPerMessage` config.
- Models/Kimi Coding: send tools in native Anthropic format again.
- Telegram/outbound HTML: chunk long HTML messages properly.
- Signal/config schema: accept `channels.signal.accountUuid` in strict validation.
- Telegram/config schema: accept `channels.telegram.actions.editMessage` and `createForumTopic`.
- Discord/config typing: expose channel-level `autoThread` on guild-channel config type.
- Tools/web search: treat Brave `llm-context` grounding snippets as plain strings (fix empty arrays).
- Tools/web search: recover OpenRouter Perplexity citation extraction from `message.annotations`.

### New Config Keys
- `channels.discord.guilds.<id>.channels.<id>.autoArchiveDuration` — auto-archive duration for auto-created threads (1h, 1d, 3d, 1w)
- `memorySearch.extraPaths` — paths for multimodal image/audio indexing
- `OPENCLAW_CLI` env var — set in child command environments

### New Troubleshooting Entries
| Symptom | Cause | Fix |
|---------|-------|-----|
| **BREAKING** Cron job no longer delivers to ad hoc targets (v2026.3.11) | Isolated cron delivery tightened — no fallback to agent sends or main-session summaries | Run `openclaw doctor --fix` to migrate cron jobs to explicit delivery targets |
| Gateway rejects browser WebSocket in `trusted-proxy` mode (v2026.3.11) | Origin validation now enforced for browser connections (GHSA-5wcw-8jjv-m286) | Ensure browser origin matches allowed origins in gateway config |
| Leaked `<\|...\|>` tokens in agent replies | GLM-5/DeepSeek model control tokens not stripped | Fixed in v2026.3.9+ — upgrade to v2026.3.9 or later |
| Discord `maxLinesPerMessage` ignored | Config not resolved effectively for reply chunking | Fixed in v2026.3.10+ |
| Kimi Coding tools broken | Tools sent in wrong format | Fixed in v2026.3.10+ — tools now sent in native Anthropic format |
| Telegram long HTML messages truncated | Outbound HTML not chunked properly | Fixed in v2026.3.11 |
| Signal config rejected with `accountUuid` | Strict validation didn't accept `channels.signal.accountUuid` | Fixed in v2026.3.11 |
| Brave web search returns empty results | `llm-context` grounding snippets returned as empty arrays | Fixed in v2026.3.11 — treated as plain strings |

---

## What's New in v2026.3.2–3.7

### Breaking Changes
- **`tools.profile` default** (v2026.3.2): Now defaults to `messaging` for new local installs (was broad). Set `tools.profile: "coding"` to restore.
- **ACP dispatch** (v2026.3.2): Now enabled by default. Set `acp.dispatch.enabled: false` to disable.
- **Plugin HTTP registration** (v2026.3.2): `api.registerHttpHandler(...)` removed. Use `api.registerHttpRoute({ path, auth, match, handler })`.
- **Zalo Personal** (v2026.3.2): No longer depends on external `zca` CLI. Run `openclaw channels login --channel zalouser` after upgrade.
- **Gateway auth mode** (v2026.3.7): Explicit `gateway.auth.mode` required when both `token` and `password` are configured. Set to `"token"` or `"password"`.

### New Features
- **ContextEngine plugin** (v2026.3.7): Pluggable context management with lifecycle hooks (`bootstrap`, `ingest`, `assemble`, `compact`, `afterTurn`, `prepareSubagentSpawn`, `onSubagentEnded`). Config: `agents.defaults.contextEngine`.
- **PDF tool** (v2026.3.2): First-class with Anthropic/Google provider support. Config: `agents.defaults.pdfModel`, `pdfMaxBytesMb`, `pdfMaxPages`.
- **Session attachments** (v2026.3.2): Inline file attachments for `sessions_spawn`. Config: `tools.sessions_spawn.attachments`.
- **Audio echo** (v2026.3.2): Pre-agent transcript confirmation. Config: `tools.media.audio.echoTranscript` + `echoFormat`.
- **ACP persistent bindings** (v2026.3.7): Durable Discord/Telegram topic bindings that survive restarts.
- **Telegram topic agent routing** (v2026.3.7): Per-topic `agentId` overrides for forum groups and DM topics.
- **Telegram streaming default** (v2026.3.2): `channels.telegram.streaming` now defaults to `"partial"` with `sendMessageDraft` live preview.
- **Config validation CLI** (v2026.3.7): `openclaw config validate [--json]` to check config before starting gateway.
- **Compaction tuning**: `agents.defaults.compaction.postCompactionSections`, `recentTurnsPreserve`, `qualityGuard`.
- **Custom provider headers**: `models.providers.<name>.headers` propagated across all resolution paths.
- **Ollama improvements**: Custom headers, compaction/summarization support, memory embeddings (`memorySearch.provider: "ollama"`).
- **Plugin SDK extensions**: `channelRuntime`, `runtime.stt.transcribeAudioFile()`, `runtime.system.requestHeartbeatNow()`, `runtime.events.onAgentEvent`, `runtime.events.onSessionTranscriptUpdate`.
- **Plugin context injection**: `prependSystemContext` and `appendSystemContext` for static system prompt guidance.
- **Hook lifecycle events**: `session:compact:before/after`, `message:transcribed`, `message:preprocessed`, `message:sent`, sessionKey in session events.
- **Banner control**: `cli.banner.taglineMode` (`random` | `default` | `off`).
- **OpenAI-compatible TTS**: `messages.tts.openai.baseUrl` config.
- **MiniMax-M2.5-highspeed**: First-class support across catalogs.
- **Google Gemini 3.1 Flash-Lite**: `google/gemini-3.1-flash-lite-preview`.
- **Docker improvements**: Multi-stage builds, `OPENCLAW_VARIANT=slim`, `OPENCLAW_EXTENSIONS` for preinstalling deps, health checks.

### New Troubleshooting Entries
| Symptom | Cause | Fix |
|---------|-------|-----|
| **BREAKING** Gateway auth ambiguous (v2026.3.7) | Both token and password configured without mode | Set `gateway.auth.mode: "token"` or `"password"` |
| **BREAKING** Tools profile too restrictive (v2026.3.2) | Default changed to `messaging` | Set `tools.profile: "coding"` for dev tools |
| **BREAKING** ACP dispatch unexpected | Enabled by default in v2026.3.2 | Set `acp.dispatch.enabled: false` to disable |
| Zalo Personal broken after upgrade | CLI dependency removed | Run `openclaw channels login --channel zalouser` |
| Plugin HTTP handler "unknown route" | `registerHttpHandler` removed | Use `registerHttpRoute({ path, auth, match, handler })` |
| Telegram streaming not working | Old `streaming: true` format | Use `streaming: "partial"` (new default) |
| Telegram DM duplicate replies (v2026.3.8) | Both `agent:main:main` and `agent:main:telegram:direct:<id>` match | Fixed: DMs now deduped per agent, not per session key |
| `system.run` script modified post-approval | Security: script rewrites after approval | v2026.3.8 pins approved scripts to on-disk snapshots; rewrites denied |
| MS Teams group policy bypassed by route match | `groupPolicy: "allowlist"` ignored when route allowlist set | v2026.3.8 fix: sender allowlists enforced even with route allowlists |
| Cron announce says `delivered: true` but no message sent | Text-only Telegram announce not routed through adapters | v2026.3.8 fix: routes through real outbound adapters |
| Config validation: `tools: Unrecognized key: "webSearch"` | Wrong config path for web search | Use `tools.web.search.provider`, NOT `tools.webSearch`. Schema-validated. |
| `tools.web.search.provider` rejects "tavily" | Tavily not a native provider in v2026.3.8 | Allowed: `brave`, `perplexity`, `grok`, `gemini`, `kimi`. For Tavily: install `openclaw-tavily` plugin via ClawHub, or wait for v2026.3.9+ |
| `openclaw doctor --fix` removes custom config keys | Unrecognized keys are stripped by schema validation | Only use documented config paths. Check with `openclaw config set` first (it validates before writing). |

---

## Self-Evolution Protocol

After completing any OpenClaw task that involved:
1. A new workflow not documented above
2. A gotcha or failure not in the troubleshooting table
3. A new provider, channel, or feature configuration
4. A correction to existing information

**Claude MUST update this SKILL.md** at `~/.claude/skills/openclaw-configure/SKILL.md`:
- Add new workflow/recipe to appropriate section
- Add new gotchas to troubleshooting table
- Update provider/channel sections
- Keep concise and well-organized

This skill grows with every use. Never let hard-won knowledge be lost.

---

## Version Check & Auto-Update Protocol

**This skill was last updated for:** `v2026.4.27`

### Version Check (MANDATORY — run at start of every OpenClaw session)

Before answering any OpenClaw question, Claude MUST run these two commands **in parallel**:

```bash
# Command 1: Get installed version
openclaw --version 2>&1 | head -1

# Command 2: Get latest registry version + update availability
openclaw update status --json 2>&1
```

From the JSON output, extract:
- `INSTALLED` — the locally installed version (e.g. `2026.4.2`)
- `LATEST` — `registry.latestVersion` from the JSON (e.g. `2026.4.5`)
- `SKILL_VERSION` — the version in this section header above (e.g. `v2026.4.2`)

### Decision Matrix

Present the user a clear comparison table:

```
| Component      | Version    |
|----------------|------------|
| Installed      | vX.X.X     |
| Latest (npm)   | vX.X.X     |
| Skill synced   | vX.X.X     |
```

Then follow the appropriate path:

**Path A — All in sync** (`INSTALLED` == `LATEST` == `SKILL_VERSION`):
→ "Everything is up to date." Proceed normally.

**Path B — Update available** (`LATEST` > `INSTALLED`):
→ **Ask the user:** "OpenClaw vX.X.X is available (you have vX.X.X). Would you like to update?"
- If **yes**: run `openclaw update --yes`, then proceed to **Skill Refresh** below.
- If **no**: proceed normally with current version. Note the skill may not cover newer features.

**Path C — Installed ahead of skill** (`INSTALLED` > `SKILL_VERSION`):
→ OpenClaw was updated outside this session. Trigger **Skill Refresh** automatically.

**Path D — Installed matches latest, but skill is behind** (`INSTALLED` == `LATEST` > `SKILL_VERSION`):
→ Same as Path C — trigger **Skill Refresh** automatically.

### Skill Refresh Procedure

When the local OpenClaw version is newer than `SKILL_VERSION`, sync the skill:

1. **Notify the user:** "Syncing skill to match OpenClaw vX.X.X..."

2. **Regenerate `cli-reference.md`:**
   ```bash
   # Capture top-level help
   openclaw --help > /tmp/oc-help.txt

   # For each command domain, capture subcommand help
   for cmd in acp agents approvals browser channels config cron devices directory dns gateway hooks memory message models node nodes pairing plugins sandbox security skills system tasks update webhooks; do
     echo -e "\n\n=== openclaw $cmd ===" >> /tmp/oc-help.txt
     openclaw $cmd --help >> /tmp/oc-help.txt 2>/dev/null
   done
   ```
   Write the formatted output to `~/.claude/skills/openclaw-configure/cli-reference.md`.

3. **Read the CHANGELOG** for delta between old and new version:
   ```bash
   CHANGELOG_PATH=$(dirname $(which openclaw))/../lib/node_modules/openclaw/CHANGELOG.md
   ```
   Extract the section between the new version and `SKILL_VERSION`. Identify:
   - New features, channels, or providers
   - Breaking changes or renamed commands
   - New config paths or options
   - Security changes

4. **Update `commands.md`:**
   - Update the version header line
   - Add any new commands or flags from the help output
   - Remove any commands that no longer exist

5. **Update this SKILL.md:**
   - Update `SKILL_VERSION` in this section header to the new version
   - Update `openclaw_version` in the YAML frontmatter to the new version
   - Set `version:` in the YAML frontmatter to match the OpenClaw version (e.g. `2026.4.5`)
   - Add new "What's New" section for the version range if there are notable changes
   - Update troubleshooting table if changelog mentions new gotchas

6. **Verify sync:** Confirm the three versions now match:
   ```bash
   # Installed version
   openclaw --version 2>&1 | head -1
   # Skill frontmatter
   grep 'openclaw_version' ~/.claude/skills/openclaw-configure/SKILL.md
   ```

7. **Confirm to user:** "Skill synced to vX.X.X. Installed, registry, and skill are now aligned."
