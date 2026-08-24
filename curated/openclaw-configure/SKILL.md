---
name: openclaw-configure
description: "Expert-level OpenClaw CLI configuration skill. Covers channels, models, plugins, gateway, agents, hooks, cron, security, sandbox, memory, browser, nodes, DNS, webhooks, approvals, backup, ACP provenance, ClawHub skill registry, tasks, and more. Self-evolving: updates itself after learning new patterns."
version: 2026.7.1-2
author: zanearcher
category: infrastructure
openclaw_version: "2026.7.1-2"
last_verified: 2026-08-24
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

### Custom Mobile Channel Relay

For a first-party mobile app that should behave like an OpenClaw channel without exposing the Gateway or an operator token:

1. Implement a compiled OpenClaw channel plugin and bind canonical account IDs to agents through normal `{channel, accountId}` bindings.
2. Keep the Gateway connection outbound-only to a dedicated relay. The mobile app also connects outbound to that relay with a narrow, per-connection token stored in device-only secure storage.
3. Use short-lived, single-use pairing codes. Keep bridge bootstrap credentials only on the operator/Gateway side; never put them in the app.
4. Persist sequence/ACK cursors and replay only bounded encrypted pending frames. Fully validate unrelated retired-turn frames before ACK-and-discard so one abandoned turn cannot poison the next.
5. Serialize connector mutation, WebSocket handling, revocation, and expiry within one durable session transaction lane. Revocation must close sockets and delete session metadata.
6. A replacement must fail closed: create and persist the new connector, positively revoke the old connector (`204` or idempotent `404`), then commit new OpenClaw config. On revoke failure, retain the old config/credential, clean up the new connector, and return an error without printing a pairing code.
7. Package compiled runtime files (`dist/`) as the plugin entrypoint; verify with an isolated install and `openclaw plugins doctor` before touching live state. Back up config and approvals, install, restart once, and verify the existing channel reconnects.
8. Treat a socket write as transport handoff, not durable delivery. The relay must return a strict sequence-free persistence receipt only after durable storage; until it arrives, retain and replay the exact encoded frame with the same sequence, message ID, and bytes. Exact replay re-receipts without forwarding or applying lifecycle twice, while altered identifier reuse fails closed. Never replay stale receipts proactively on reconnect.
9. Make pairing redemption idempotent for the same short-lived code and installation identity so HTTP-response or device-secure-storage failures return the same client credential. Reject every other installation, retain the retry credential only as bounded authenticated ciphertext, and clear it at pairing expiry or connector revocation.

Keep connector transports isolated from each other and from unrelated realtime/audio services. A shared relay can be considered later only after the connector contract is stable.

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

## What's New in v2026.7.1–7.1-2

_(Synced from the installed v2026.7.1-2 CLI, official v2026.7.1 release notes, and the packaged v2026.7.1-2 correction changelog on 2026-08-03.)_

### Highlights
- **Control UI overhaul:** Multi-pane conversations, live Tasks, denser session management, usage/cost views, file previews, downloads, pairing, approvals, Gateway health, and stronger mobile/responsive behavior.
- **Onboarding and repair:** Guided first-chat setup verifies model connections before saving, preserves interrupted choices, protects unreadable config, and completes migrations/plugin repairs before reporting readiness.
- **Models and providers:** Expanded GPT-5.6 compatibility across supported OpenAI/Codex routes, full Tencent Hy3 setup, Meta Muse Spark 1.1, and broader Claude, Ollama, ClawRouter, LongCat, and provider support.
- **Connected coding agents:** New `openclaw attach` grants Claude Code temporary scoped access to a selected Gateway session; Codex delegation, native subagents, long-running sessions, and goals recover more reliably.
- **Channels:** Major Telegram, Slack, Discord, and Apple Messages work, plus reliability and capability improvements across Signal, WhatsApp, Teams, Matrix, Feishu, and other adapters.
- **Gateway reliability:** Repeated startup failures now stop in a stable repair state instead of looping forever; remote browser control, workspace terminals, scheduled work, sessions, and downloads gain safer recovery paths.
- **Official apps:** iOS/iPadOS, Android, macOS, and Apple Watch add richer setup, offline reading, queued sends, native session controls, voice, file, permission, and reconnection behavior.
- **v2026.7.1-2 correction:** Official npm plugin updates now accept singleton-array metadata returned by newer npm clients, allowing tracked plugins to install correction releases.

### CLI Surface Changes
- **New top-level commands:** `attach`, `audit`, `capability`, `commitments`, `mcp`, `promos`, `transcripts`, and `worktrees`.
- **Convenience entry points:** `chat` and `terminal` open local TUI mode; `exec-approvals` aliases `approvals`; `setup` aliases `onboard`; `clawbot` keeps legacy aliases.
- **Generated references:** `commands.md` and `cli-reference.md` now enumerate every top-level command exposed by v2026.7.1-2, including current usage and first-level subcommands.

### Runtime and Upgrade Notes
- **Node runtime gate:** v2026.7.1 blocks unsafe runtimes before they open SQLite state. Supported lines observed by the CLI are Node `>=22.22.3 <23`, `>=24.15.0 <25`, or `>=25.9.0`.
- **Plugin correction skew:** The OpenClaw core may carry a correction suffix while individual official plugins publish only the latest compatible base or first correction version. Check the package's published versions rather than assuming every plugin matches the core suffix exactly.
- **Migration ownership:** Update, Doctor, plugin migration, and Gateway startup share an exclusive state-migration lease. Do not run these mutation paths concurrently.
- **Launchd backoff:** A freshly reinstalled LaunchAgent can briefly report `loaded` but `stopped` while a migration lease clears or launchd waits for its next retry. Verify the current log and probe again before treating it as a permanent failure.

### New Troubleshooting Entries (v2026.7.1–7.1-2)
| Symptom | Cause | Fix |
|---|---|---|
| `OpenClaw startup migrations are already running` | Another `openclaw doctor`, update, plugin migration, or Gateway process owns the migration lease; a stalled interactive Doctor can hold it | Find the owning OpenClaw/Doctor process, let valid work finish or terminate only the confirmed stale process, then retry. Do not delete state databases or lock files blindly. |
| LaunchAgent is loaded but Gateway reports `stopped (state active)` immediately after reinstall | launchd startup backoff or a still-active migration lease delayed the next launch | Inspect the newest Gateway log lines, confirm no stale Doctor/update process remains, allow the next launchd retry, then verify with `openclaw gateway status --deep` and `openclaw health --json`. |
| Core is v2026.7.1-2 but `plugins update` requests an unpublished `@openclaw/*@2026.7.1-2` | Official plugin packages can publish compatible versions without the core correction suffix | Query the package's published versions, install the newest compatible published version, run `openclaw plugins registry --refresh`, then `openclaw plugins doctor`. v2026.7.1-2 also fixes newer npm singleton-array metadata handling. |
| CLI refuses Node 22.22.0 or Node 25.6.1 before startup | Runtime is below the safe patch level for its Node line | Upgrade to Node `>=22.22.3 <23`, `>=24.15.0 <25`, or `>=25.9.0`, reinstall the Gateway service if its LaunchAgent points at the old executable, and verify CLI/Gateway versions match. |
| Plugin list says persisted registry policy is stale even though plugins load | Persisted registry metadata predates the final plugin/config state | Run `openclaw plugins registry --refresh`; if `openclaw plugins doctor` reports no issues and the Gateway loads plugins without errors, treat retained legacy-index conflict notices as non-blocking and do not delete them blindly. |

---

## What's New in v2026.6.11

_(Synced from the packaged v2026.6.11 changelog and local CLI help on 2026-07-10.)_

### Highlights
- **Channel control:** Slack relay mode, native Mattermost `/oc_queue`, and `directUserId`-aware per-DM model overrides improve routing and automation.
- **Operator workflows:** `openclaw agent --message-file` supports file-driven prompts; the RAFT CLI wake bridge adds remote wake-up paths.
- **Plugin distribution:** More official plugins are externalized, bundled plugin icon metadata is exposed, and ClawHub update policy is hardened.
- **Agent reliability:** Codex partial deltas, selected harness activation, long-context prompt-cache stability, bounded provider responses, and improved fallback classification reduce lost progress.
- **Channel reliability:** Telegram progress/webhook/spool handling and WhatsApp durable reply/quote routing received substantial fixes.

### New CLI Notes
- `openclaw agent --message-file <path>` reads the agent message from a file.
- `openclaw gateway usage-cost --agent <id>` scopes usage-cost reporting to one agent.
- The regenerated `cli-reference.md` includes current help for core domains plus `proxy`, `migrate`, `infer`, `ltm`, `matrix`, `qqbot`, `googlemeet`, and `raft` where available.

### New Troubleshooting Entries (v2026.6.11)
| Symptom | Cause | Fix |
|---|---|---|
| Telegram inbound work stalls until gateway restart | A live worker can leave an ingress spool/release claim stuck | Upgrade to v2026.6.11; stalled ingress claims now recover automatically |
| Claude CLI credit exhaustion returns as final text instead of trying fallback | Credit failures were not classified for model fallback | Upgrade to v2026.6.11; credit failures now continue through the fallback chain |
| Per-DM model override routes the wrong direct chat | Direct-user identity was unavailable to model override resolution | Use v2026.6.11 and configure the override with `directUserId` |
| `configure --non-interactive` proceeds without a usable TTY | Older configure paths could continue ambiguously | v2026.6.11 fails closed; use explicit onboarding/config flags or an interactive TTY |

---

## What's New in v2026.6.10

_(Maintenance update verified locally on 2026-06-30. The packaged CHANGELOG section for 2026.6.10 is empty, so this section records observed CLI/runtime deltas from the upgraded installation.)_

### Observed Changes
- **Package manager after update:** `openclaw update --yes` may switch the global install metadata from pnpm to npm with `npm-shrinkwrap.json`; this is expected when `openclaw update status --json` reports deps status `ok`.
- **Plugin dependency command removed:** `openclaw plugins deps --repair` is no longer recognized in v2026.6.10. Use `openclaw plugins doctor`, `openclaw plugins registry --refresh`, and `openclaw plugins update --all` for plugin health/update work.
- **External plugins verified:** Official external packages such as `brave`, `codex`, and `discord` report v2026.6.10 through `openclaw plugins update --all`.
- **Skill reference regenerated:** `cli-reference.md` was regenerated from v2026.6.10 command help and includes newer domains observed locally: `proxy`, `migrate`, `infer`, `ltm`, `matrix`, `qqbot`, and `googlemeet`.

### Local Upgrade Notes
- **Gateway restart false alarm:** `openclaw update --yes` can finish core/package upgrade but exit nonzero if the post-update gateway health wait races with an already-running LaunchAgent. Verify with `openclaw gateway status --deep`; if CLI and gateway versions match and connectivity probe is OK, the gateway is healthy.
- **Legacy state warning:** Doctor may leave `~/.openclaw/plugins/installs.json` in place when shared SQLite state has conflicting metadata for `brave` or `discord`. If `openclaw plugins doctor` says "No plugin issues detected" and `plugins update --all` says those packages are current, treat as a non-blocking migration warning.
- **Auth profile SQLite migration warning:** Doctor may leave per-agent `auth-profiles.json` in place when expired OAuth entries cannot be verified in SQLite. Re-auth with `openclaw models auth login --provider openai` or `google-gemini-cli` when those providers are needed.

### New Troubleshooting Entries (v2026.6.10 local)
| Symptom | Cause | Fix |
|---|---|---|
| `openclaw plugins deps --repair` returns "does not recognize option" | `plugins deps` was removed or hidden in v2026.6.10 | Use `openclaw plugins doctor`, `openclaw plugins registry --refresh`, and `openclaw plugins update --all` |
| `openclaw update --yes` exits 1 after "After: 2026.6.10" with gateway health wait failure | Gateway LaunchAgent is already running and the restart waiter loses the race | Run `openclaw gateway status --deep`; if gateway version is 2026.6.10 and connectivity probe is OK, continue with doctor/verification |
| Doctor repeats plugin install index conflict for `brave`, `discord` | Legacy JSON install index conflicts with shared SQLite metadata | If `plugins doctor` reports no issues and `plugins update --all` reports current packages, leave it alone; do not delete blindly |

---

## What's New in v2026.5.6–5.7

_(Fix-focused maintenance releases. No major breaking defaults flipped. Heavy emphasis on Codex/OAuth route preservation, Telegram/Discord polish, cron correctness, channel CLI restructure, and plugin install lifecycle hardening.)_

### Breaking / Noteworthy Defaults
- **`openclaw channels list` is now channel-only** (v2026.5.7): Lists configured channels only. New `--all` flag includes bundled and catalog channels. Renders installed/configured/enabled state. Model auth/usage details moved to `openclaw models auth list`, `openclaw status`, and `openclaw models list`. (#78456)
- **Doctor preserves working `openai-codex/*` PI routes** (v2026.5.5–5.7 carry-forward, hardened in 5.6): `doctor --fix` no longer rewrites working `openai-codex/*` Codex OAuth subscription routes to `openai/*`. v2026.5.5's aggressive migration is reversed for setups with only Codex OAuth auth. Recovers 2026.5.5-rewritten `openai/*` GPT-5 routes back to `openai-codex/*` when only Codex OAuth is available. Mixed Codex OAuth + direct OpenAI PI routes get a warning, no rewrite. Fixes #78407. **If your `main`/`content` agents got migrated to `openai/*` by 2026.5.5's doctor and then started erroring with `No API key found for provider "openai"`, upgrade to 2026.5.7 and re-run `openclaw doctor --fix` — it will move you back to the working `openai-codex/*` route.**
- **Native command owner enforcement** (v2026.5.7): Native command handlers now honor owner enforcement. (#78864)
- **Active Memory global memory toggles require admin scope** (v2026.5.7). (#78863)
- **OpenAI `chat-latest` explicit override** (v2026.5.7): `openai/chat-latest` now supported as an explicit direct API-key model override for trying the moving ChatGPT Instant API alias without changing the stable default model. Note: only on the direct OpenAI API-key route, not Codex OAuth.

### New Features

**CLI:**
- `openclaw channels list --all` (v2026.5.7): Include bundled and catalog channels in the listing, with installed/configured/enabled state rendered inline.
- `cron list --json` / `cron show --json` now include computed `status` (disabled/running/ok/error/skipped/idle) (v2026.5.7) so external tooling can read state without reimplementing cron status derivation. (#78701)

**Cron / Doctor:**
- **Cron model override repair** (v2026.5.7): `openclaw doctor --fix` repairs persisted cron jobs whose `payload.model` was stored as `"default"`, `"null"`, blank, or JSON `null` by removing the bad override. Cron runtime model validation stays strict. Fixes #78549.
- **Cron isolated runs fail fast on missing delivery target** (v2026.5.7): When `delivery.channel=last` has no previous route, the implicit announce delivery fails before model execution — so recurring jobs do not spend tokens before hitting a permanent delivery-target error. Fixes #78608.

**Channels:**
- **Telegram polling watchdog tied to `getUpdates` liveness** (v2026.5.7): Unrelated outbound Bot API calls can no longer mask a wedged inbound poller. Fixes #78422.
- **Telegram `accessGroup:*` sender allowlists** (v2026.5.7): Honor `accessGroup:*` in DMs, groups, native commands, and callback authorization before applying Telegram's numeric sender-ID checks. Fixes #78660.
- **Telegram same-chat message-tool outbound treated as delivered** (v2026.5.7): During an inbound Telegram turn, successful `message` tool sends to the same chat now count as delivered when deciding whether to emit the rewritten silent reply fallback. (#78685)
- **Discord voice capabilities audit** (v2026.5.7): `channels capabilities` and `channels status --probe` audit Discord voice-channel permissions (including auto-join targets) so missing Connect/Speak/Read Message History permissions show up *before* `/vc join`.
- **Discord voice capture less choppy** (v2026.5.7): Default post-speech silence grace extended to 2.5s. New `voice.captureSilenceGraceMs` config for noisy Discord sessions. Spoken-output prompt tightened around live STT fragments.
- **Discord channel-target message routing** (v2026.5.7): `discord:channel:<id>` provider-prefixed targets now parse as channel sends instead of legacy Discord DM targets. Cross-channel `message(action="send")` calls no longer misroute as misleading `Unknown Channel` failures. Fixes #78572.
- **WhatsApp LID forward routing** (v2026.5.7): Proactive phone-number sends routed through Baileys LID forward mappings when available, so LID-addressed contacts receive agent messages instead of creating sender-only ghost chats. Fixes #67378.
- **WhatsApp captioned MEDIA auto-replies** (v2026.5.7): Captioned `MEDIA:` directive auto-replies send once instead of emitting an empty media message before the captioned media reply. (#78770)

**Codex:**
- **Codex pre-guardian PermissionRequest hook removed by default** (v2026.5.7): In Codex approval modes, the pre-guardian native `PermissionRequest` hook is no longer installed by default — Codex's reviewer approves safe commands before OpenClaw surfaces an approval. `allow-always` decisions remembered for identical Codex native `PermissionRequest` payloads within the active session window. Plugin approval requests validate/render their actual allowed decisions so Telegram and other native approval UIs cannot offer stale actions.

**Agents:**
- **Context engine cache invalidation** (v2026.5.7): Cached assembled context views invalidated when source history shrinks or assembly fails, preventing stale pre-reset history from being reused. Fixes #77968. (#78163)
- **Compaction summary reserve clamp** (v2026.5.7): Compaction summary reserve tokens clamped to each model's output limit so high-context compaction no longer requests invalid `max_tokens` values. (#54392)
- **Skills snapshot cleared on `/new` and `sessions.reset`** (v2026.5.7): Long-lived channel sessions rebuild the visible skill list after skills change. (#78873)
- **Auto-reply inline skill dispatch gated through `before_tool_call` hooks** (v2026.5.7). (#78517)
- **Agent delivery reports honest failures** (v2026.5.7): `deliverySucceeded=false` reported when outbound delivery returns no adapter result, so claimed/empty delivery paths no longer masquerade as successful sends. Fixes #78532.

**Gateway:**
- **Session transcript rollover persists** (v2026.5.7): When daily gateway-agent session rollover changes the session id, a new generated transcript file is persisted while preserving custom transcript paths. Fixes #78607.
- **Stale task / channel hot-reload reconciliation** (v2026.5.7): Stale CLI run-context tasks whose live run context disappeared are reconciled. Bound channel hot-reload deferrals reconciled so stale task records cannot block Discord/Slack/Telegram reloads forever.

**Providers:**
- **OpenAI `chat-latest`** (v2026.5.7): Explicit direct API-key model override. Use to try the moving ChatGPT Instant API alias without changing your stable default model.
- **Tavily SecretRef resolution** (v2026.5.7): `tavily_search` and `tavily_extract` tool credentials resolved from the active runtime config snapshot, so `exec` SecretRef-backed API keys reach the tools resolved. (#78610)
- **Snake_case tool-call transcript sanitization repaired** (v2026.5.7). Plus: APNG-sniffed PNG uploads normalized, Gemini 3 tool-call thought-signature replay with fallback signatures, legacy `__env__:VAR` custom-provider keys accepted. Fixes #51881, #48915, #77566, #42858.

**Plugins / Install:**
- **Plugin npm lifecycle on absolute POSIX shell** (v2026.5.7): Managed plugin install, rollback, repair, and uninstall npm operations use the same absolute POSIX npm lifecycle shell as staged package updates, preventing restricted PATH shells from breaking cleanup.
- **Subagent registry archiveAfterMinutes honored across modes** (v2026.5.7): Completed session-mode subagent registry rows now honor `agents.defaults.subagents.archiveAfterMinutes` instead of a hardcoded 5-minute TTL. (#78263)
- **External channel plugin runtime forwarded** (v2026.5.7): `setChannelRuntime` forwarded from non-bundled external plugin setup entries so deferred external channel runtime initializers are installed before startup polling. Fixes #77779. (#77799)

**v2026.5.6 (small fix release):**
- **Doctor/OpenAI config:** Doctor `--fix` keeps the 2026.5.6 release branch clear of the legacy Codex route rewrite — preserves existing OpenAI routes unless a supported repair path applies. Companion to the 2026.5.5 → 2026.5.7 fixes preserving Codex OAuth routes.
- **Plugins/runtime fetch header sanitization:** Third-party symbol metadata dropped from plain request header dictionaries before passing into native `fetch` or `Headers`, so SDK and guarded/proxy fetch paths do not reject otherwise valid plugin requests. Fixes #77846.
- **Debug proxy header normalization:** Captured fetch header dictionaries normalized before replaying requests so symbol metadata from caller-owned header objects cannot make debug-proxy fetches fail.
- **Web fetch bounded dispatcher cleanup:** Guarded dispatcher cleanup after request timeouts bounded so timed-out fetches return tool errors instead of leaving Gateway tool lanes active. (#78439)

### Key Fixes (v2026.5.6–5.7)
- **Codex/Telegram tool progress visibility** (v2026.5.7): Message-tool-only progress drafts stay visible.
- **Telegram bot `/models` callback buttons with dotted provider ids** (v2026.5.7): Parse provider ids containing dots (`hf.co/...`) in `/models` callback buttons so `hf.co` model lists render as inline keyboard buttons. Fixes #38745.
- **`/btw` placeholder visibility** (v2026.5.7): Missing-question usage placeholder shown with brackets so outbound channel sanitization keeps it visible. Fixes #62877.
- **Release/plugin publishing** (v2026.5.7): Retry transient ClawHub CLI dependency install failures, keep preview-passing plugins publishable when one preview cell flakes, verify every expected ClawHub package version after publish.

### New Config Keys (v2026.5.6–5.7)
| Config Path | Type | Description |
|---|---|---|
| `voice.captureSilenceGraceMs` | number | Discord voice capture post-speech silence grace (default 2.5s in v2026.5.7) |

### New Troubleshooting Entries (v2026.5.6–5.7)
| Symptom | Cause | Fix |
|---|---|---|
| `No API key found for provider "openai". You are authenticated with OpenAI Codex OAuth. Use openai-codex/gpt-5.5, or set OPENAI_API_KEY` | v2026.5.5 doctor `--fix` rewrote working `openai-codex/*` PI routes to `openai/*` for Codex-OAuth-only setups | Upgrade to v2026.5.7 and re-run `openclaw doctor --fix` — it now recovers 2026.5.5-rewritten `openai/*` routes back to `openai-codex/*` when only Codex OAuth is available. Or manually edit `~/.openclaw/openclaw.json`: set agents' `model.primary` back to `openai-codex/gpt-5.5`. Fixes #78407 |
| Cron job lost its forum topic on next run | Pre-5.7 model override stored as `"default"`/`"null"`/blank/JSON `null` | Run `openclaw doctor --fix` (v2026.5.7) to remove the bad override |
| `cron list --json` external tooling can't read disabled/running/error state | Status wasn't in JSON output pre-5.7 | Upgrade to v2026.5.7 — computed `status` field now included |
| `openclaw channels list` no longer shows model auth/usage details | Moved out of `channels list` in v2026.5.7 | Use `openclaw models auth list` and `openclaw status`. `openclaw channels list --all` for bundled + catalog channels |
| Discord cross-channel `message(action="send")` returns `Unknown Channel` | Pre-5.7 misrouted `discord:channel:<id>` as DM target | Fixed v2026.5.7 — provider-prefixed targets parsed as channel sends. Fixes #78572 |
| Telegram polling claims healthy but inbound messages stop flowing | Pre-5.7 unrelated outbound Bot API calls could mask a wedged poller | Fixed v2026.5.7 — polling watchdog tied to `getUpdates` liveness. Fixes #78422 |
| Plugin install fails with `ERESOLVE` after installing a peer-based plugin (e.g. Opik) | Pre-5.5 npm peer resolution pulled a stale registry `openclaw` copy beside Codex/Discord/WhatsApp | Fixed v2026.5.5 — managed plugin roots skip npm peer resolution |
| WhatsApp LID contacts get sender-only ghost chats instead of receiving agent messages | Pre-5.7 didn't route through Baileys LID forward mappings | Fixed v2026.5.7. Fixes #67378 |
| Long-lived channel session keeps showing skills that were just disabled | Pre-5.7 didn't invalidate `skillsSnapshot` on `/new` or `sessions.reset` | Fixed v2026.5.7. (#78873) |
| Daily gateway-agent session rollover loses transcript | Pre-5.7 didn't persist new transcript file when session id changed | Fixed v2026.5.7. Fixes #78607 |
| Discord voice channel `/vc join` fails with cryptic permission errors at runtime | Pre-5.7 didn't audit voice perms ahead of time | Upgrade to v2026.5.7 — `channels capabilities` and `channels status --probe` audit Connect/Speak/Read Message History before join |
| Recurring cron job burns tokens then errors on missing delivery target | Pre-5.7 ran the model before checking `delivery.channel=last` had a previous route | Fixed v2026.5.7 — fails fast before model execution. Fixes #78608 |
| Compaction request fails with invalid `max_tokens` on high-context turn | Pre-5.7 didn't clamp summary reserve to model's output limit | Fixed v2026.5.7. (#54392) |

---

## What's New in v2026.5.3–5.5

_(Mostly fixes and incremental features — no major breaking defaults flipped, but lots of polish on streaming, Codex, plugin externalization recovery, and security hardening.)_

### Breaking / Noteworthy Defaults
- **xAI grok-4.3 thinking clamped to `off`** (v2026.5.5): Bundled xAI thinking profile clamped so live Gateway runs cannot send unsupported reasoning levels to native Grok Responses models. Prevents `Invalid reasoning effort` failures.
- **Sandbox registry sharded per-runtime** (v2026.5.4): Container/browser registry now stored as per-runtime shard files. `openclaw doctor --fix` migrates legacy monolithic registry files. Reduces unrelated session lock contention.
- **Bundled provider discovery + restrictive `plugins.allow`** (v2026.5.4): New configs with restrictive `plugins.allow` now hide bundled providers by default. Doctor migrates legacy configs to `plugins.bundledDiscovery: "compat"`.
- **Default Talk-back is agent mode** (v2026.5.4): Google Meet `mode: "agent"` is now the default Chrome talk-back path (STT → OpenClaw → TTS). `mode: "bidi"` available for direct realtime voice. Legacy `realtime` is a hidden alias for `agent`.
- **WhatsApp group visible-replies** (v2026.5.4): Group replies stay message-tool-only by default (matches Discord v2026.4.27 behavior). Direct chats unaffected.

### New Features

**CLI:**
- `openclaw models auth list [--provider <id>] [--json]` (v2026.5.4): Inspect saved per-agent auth profiles without dumping secrets.
- `openclaw proxy validate --apns-reachable` (v2026.5.4): Verify APNs is reachable through the configured managed proxy before deployment.
- `openclaw sessions --limit <n|all>` (v2026.5.4): Cap output to newest 100 rows by default; pagination metadata in JSON output.

**Plugins / Channels:**
- **WhatsApp Channel/Newsletter outbound** (v2026.5.4): Explicit `@newsletter` outbound message targets with channel session metadata (no longer routed as DM).
- **Telegram numeric forum-topic targets** (v2026.5.4): Plugin-owned numeric topic targets accepted in agent message tool.
- **Discord interactive replies render in Telegram** (v2026.5.4): Plugin approval messages show inline keyboards on Telegram.
- **Slack rich progress drafts** (v2026.5.4): `streaming.progress.render: "rich"` for Block Kit progress drafts backed by structured progress line data.
- **Slack thread participation** (v2026.5.4): Successful visible threaded sends record bot participation, so unmentioned replies in bot-participated threads bypass mention gating as documented.

**Streaming:**
- `streaming.preview.commandText: "status"` (v2026.5.4): Hide command/exec text in preview progress lines while keeping released raw command text default.
- `streaming.progress.commandText: "status"` (v2026.5.4): Same for progress drafts.
- `agents.defaults.toolProgressDetail: "raw"` (v2026.5.4): Per-agent override for raw command/detail output in tool-start lines (Slack/Discord/Telegram/Matrix/Teams progress drafts).
- **Compact verbose mode** (v2026.5.4): `/verbose` and progress drafts default to compact explain-mode tool summaries.

**Agents / Tools:**
- **Post-compaction loop guard** (v2026.5.4): `pi-embedded-runner` arms after auto-compaction-retry and aborts with `compaction_loop_persisted` if the same `(tool, args, result)` triple repeats `windowSize` times (default 3). Disable via `tools.loopDetection.enabled`; tune via `tools.loopDetection.postCompactionGuard.windowSize`.
- **`before_agent_finalize` hook** (v2026.5.4): Bounded retry instructions so workflow plugins can request one more model pass.
- **Plugin SDK additions** (v2026.5.4): `registerIfAbsent` for atomic keyed-store dedupe; plugin-owned `SessionEntry` slot projection; scoped trusted-policy session extension reads.

**Memory / Active Memory:**
- **Graceful skip when no memory plugin loaded** (v2026.5.4): Active-memory now skips the recall sub-agent silently if neither `memory-core` nor `memory-lancedb` is loaded (was previously logging confusing "No callable tools remain" warnings).
- **Latest-message recall query** (v2026.5.4): Active Memory sends bounded latest-message search query to recall worker so channel/runtime metadata doesn't become the search string.
- **Memory + wiki corpus balance** (v2026.5.4): `corpus=all` searches preserve representation from both corpora — memory hits no longer starved by numerically higher wiki integer scores.

**Providers:**
- **DeepSeek V4 `xhigh`/`max` thinking** (v2026.5.4): Exposed through lightweight provider-policy surface so Control UI `/think` pickers show max reasoning options even when runtime plugin registry isn't active.
- **OpenRouter response caching** (v2026.5.4): Opt-in params send `X-OpenRouter-Cache`, `X-OpenRouter-Cache-TTL`, and cache-clear headers only on verified OpenRouter routes.
- **OpenRouter app-attribution categories** (v2026.5.4): Coding, programming, writing, chat, personal-agent usage advertised on verified OpenRouter routes.
- **Codex auth recovery** (v2026.5.4): Invalidated per-agent Codex auth-order/session profile overrides rewritten toward healthy relogin profile, so revoked OAuth accounts don't stay pinned after signing in again.

**Google Meet:**
- **Realtime split into transcription + voice** (v2026.5.4): `realtime.transcriptionProvider` and `realtime.voiceProvider` now separate. Doctor migrates legacy Gemini Live bidi configs.
- **`realtime.strategy: "agent"` default** (v2026.5.4): Replaces direct bidirectional model behavior. `bidi` available as opt-in.
- **`chrome.audioBufferBytes` config** (v2026.5.4): Default lowered from 8192 to 4096 bytes to reduce Chrome talk-back latency.
- **Twilio dial-in via realtime Gemini bridge** (v2026.5.4): Paced audio streaming, backpressure-aware buffering, barge-in queue clearing.

**Codex:**
- **Doctor migrates legacy `openai-codex/*` to `openai/*`** (v2026.5.5): `doctor --fix` repairs primary models, fallbacks, heartbeat/subagent/compaction overrides, hooks, channel overrides, and stale session pins. Selects `agentRuntime.id: "codex"` only when Codex plugin is installed/enabled with usable OAuth; otherwise selects `agentRuntime.id: "pi"`.
- **Codex audio transcription** (v2026.5.4): Active Codex chat models route to OpenAI transcription default instead of sending chat model ids to audio transcription.
- **Codex bound-thread recovery** (v2026.5.4): Recreates missing bound app-server threads once when stale `/codex bind` sidecar survives a restart.
- **Codex output sanitization** (v2026.5.4): App-server command readouts, failure replies, approval prompts, elicitation prompts, and `request_user_input` text sanitized before posting to chat.

**Performance:**
- **Workspace-scoped plugin metadata snapshots** (v2026.5.4): BTW, compaction, embedded-run model generation, PDF model setup all reuse current workspace-compatible plugin metadata snapshot instead of cold scans.
- **Native fast path for compiled plugins** (v2026.5.4): Avoid `jiti` import on native-loadable plugin startup.
- **Defer non-readiness sidecars** (v2026.5.4): Push past ready signal; fast-path trusted bundled plugin metadata during startup.

### Security (v2026.5.4)
- **Windows env hardening**: `SystemRoot`/`WINDIR`/`LOCALAPPDATA` env values validated through Windows install-root validator. `cmd.exe`/`reg.exe`/`icacls.exe`/`whoami.exe` resolution pinned to canonical Windows install root.
- **Browser SSRF current-URL enforcement**: Existing-tab URL navigation policy enforced before tab-scoped debug/export/read routes (console, page errors, network requests, trace, response body, screenshot, snapshot, storage). Blocked tabs return policy error instead of being read first and redacted later.
- **Codex hardening**: Malformed `/codex` control commands fail closed before changing bindings/permissions/model overrides/active turns/feedback uploads. Local bound-turn image paths preserved; stale same-thread turn notifications rejected.
- **Direct APNs**: HTTP/2 delivery routed through active managed proxy with redacted proxy diagnostics.
- **Debug proxy isolation**: Debug proxy direct upstream forwarding disabled when managed proxy mode is active (override with `OPENCLAW_DEBUG_PROXY_ALLOW_DIRECT_CONNECT_WITH_MANAGED_PROXY=1`).
- **Plugin install scanner**: Suppresses dangerous-pattern warnings for trusted official OpenClaw npm installs and trusted catalog `/plugins install` commands.

### Key Fixes (v2026.5.3–5.5)
- **Discord IPv4 startup** (v2026.5.4): IPv4 preferred for Discord REST and gateway WebSocket startup paths so IPv4-only networks don't stall before READY.
- **Discord heartbeat ACK timeout** (v2026.5.5): Measured from actual heartbeat send, preventing late initial heartbeats from triggering false reconnect loops.
- **Discord `/steer` plain text** (v2026.5.5): Routed through normal authorization and mention gate instead of silently dropped.
- **Telegram tool-only draft cleanup** (v2026.5.4): Transient `Surfacing...` tool-status bubbles cleaned up after assistant message boundaries.
- **Telegram streaming chunk continuity** (v2026.5.4): Active preview reused as first chunk for long text finals — multi-chunk replies no longer create transient extra bubbles.
- **Slack `unknown error` in startup retry logs** (v2026.5.4): Now reports concrete error reason explicitly.
- **WhatsApp digit-only allowlists** (v2026.5.4): Setup/pairing canonicalized to WhatsApp's digit-only phone ids while accepting E.164/JID/`whatsapp:` inputs.
- **WhatsApp QR via runtime** (v2026.5.4): `openclaw channels login --channel whatsapp` no longer loses QR behind direct stdout writes.
- **Mattermost streaming** (v2026.5.4): Standalone default tool-progress messages suppressed while draft previews active.
- **Feishu shared progress formatter** (v2026.5.4): Streaming-card tool status lines use shared formatter with raw command/detail output.
- **`@openclaw/discord` 5.3+ failed to load** (v2026.5.4): External channel plugins whose compiled artifacts live under `dist/` now contribute their channel SecretRef contracts properly.
- **Plugin discovery: source-only TS warnings demoted** (v2026.5.4): Single broken installed source-only package no longer blocks `plugins install` for unrelated plugins (warning instead of config-blocking error). Install-time rejection of newly-installed source-only packages unchanged.
- **Pi-embedded transcript retry** (v2026.5.4): Context-overflow compaction retried from current transcript only after inbound user turn was actually persisted. Fixes #76424.
- **WebChat duplicate Pi assistant turns** (v2026.5.4): Live delivery no longer writes duplicate Pi-managed assistant turns.
- **Active Memory partial recall headroom** (v2026.5.4): Timeout partial transcript recovery has enough abort-settle headroom so temporary recall summaries are returned before cleanup.
- **Cron failed-tool diagnostics** (v2026.5.4): `cron show`/status/run history surface actual tool-policy failure when blocked, instead of misleading green result.
- **Heartbeat-poisoned `agent:main:main`** (v2026.5.5): `doctor --fix` moves heartbeat-poisoned default main session entries to recovery keys and clears stale TUI restore pointers.
- **TUI session picker** (v2026.5.5): Bound to recent rows; exact lookup-style refreshes for active session — dusty stores no longer hydrate weeks-old transcripts.
- **Reset memory hooks off reply path** (v2026.5.5): `/new` and `/reset` no longer block WhatsApp reset replies on hook housekeeping. `llmSlug: true` opt-in for model-generated memory filename slugs.
- **Codex/Telegram tool progress dedup** (v2026.5.5): Native Codex tool progress rendered once per tool instead of duplicating item/tool draft lines.
- **`/codex bind` Codex OAuth preserved** (v2026.5.4): Bound sessions keep selected Codex auth profile instead of falling back to public OpenAI credentials.

### New Config Keys (v2026.5.3–5.5)
| Config Path | Type | Description |
|---|---|---|
| `tools.loopDetection.postCompactionGuard.windowSize` | number | Triple-repeat window for post-compaction loop guard (default 3) |
| `streaming.progress.render` | string | `"rich"` for Slack Block Kit structured progress drafts |
| `streaming.preview.commandText` | string | `"status"` to hide command/exec text in preview |
| `streaming.progress.commandText` | string | `"status"` to hide command text in progress drafts |
| `agents.defaults.toolProgressDetail` | string | `"raw"` for raw command/detail output in tool-start lines |
| `googlemeet.realtime.transcriptionProvider` | string | Agent-mode STT provider (split from realtime voice provider) |
| `googlemeet.realtime.voiceProvider` | string | Bidi-mode realtime voice provider |
| `googlemeet.realtime.strategy` | string | `"agent"` (default) \| `"bidi"` |
| `googlemeet.chrome.audioBufferBytes` | number | Chrome talk-back audio buffer (default 4096, was SoX 8192) |
| `voiceCall.postDtmfSpeechDelayMs` | number | Twilio DTMF delay in plugin manifest schema |
| `plugins.bundledDiscovery` | string | `"compat"` to preserve legacy bundled provider discovery for restrictive allowlists |

### New Troubleshooting Entries (v2026.5.3–5.5)
| Symptom | Cause | Fix |
|---|---|---|
| `xai/grok-4.3` fails with `Invalid reasoning effort` | Pre-v2026.5.5 sent OpenAI-style reasoning effort to native Grok Responses | Upgrade to v2026.5.5 — thinking clamped to `off` |
| `@openclaw/discord` channel reports `not configured` after 5.3 upgrade | External channel plugin's `dist/` contracts not loaded | Upgrade to v2026.5.4+ |
| Plugin install fails with `package directory is missing` after `openclaw update` | Plugin install payload missing post-update | `openclaw plugins install <spec> --force` to reinstall (the v2026.5.4 `plugins deps` subcommand was renamed/removed; use direct install) |
| `openai-codex/gpt-*` model still references after 5.5 upgrade | Legacy routes pinned in primary models, fallbacks, hooks | Run `openclaw doctor --fix` to migrate to canonical `openai/*` with appropriate `agentRuntime.id` |
| Active Memory logs "No callable tools remain" warnings | No memory plugin loaded; pre-v2026.5.4 logged confusingly | Upgrade to v2026.5.4+ — silently skipped now. Or install `memory-core`/`memory-lancedb`. |
| Discord IPv4-only network stalls before READY | Pre-v2026.5.4 didn't prefer IPv4 for REST/gateway startup | Upgrade to v2026.5.4+ |
| Memory wiki integer scores starve memory hits in `corpus=all` | Wiki numeric scores ranked higher than memory hits | Fixed v2026.5.4 — backfill preserves both corpora |
| Cron shows green result but no output delivered | Tool-policy blocked the run; pre-v2026.5.4 hid failure | Upgrade to v2026.5.4+ — `cron show` surfaces actual tool-policy failure |
| TUI hydrates weeks-old transcripts before becoming responsive | Session picker fetched all rows | Fixed v2026.5.5 — bounded to recent rows |
| `/new`/`/reset` blocks WhatsApp reset reply | Reset memory hooks ran on reply path | Fixed v2026.5.5 — runs off command reply path; `llmSlug: true` opt-in |
| `gateway restart --force --wait <duration>` errors | Mutually exclusive flags | Use one or the other (`--force` OR `--wait`, not both) |
| Repeated `/new` or `/reset` in same minute overwrites prior session archive | Memory filename collision | Fixed v2026.5.5 — collision suffixes added |
| Pre-compaction prompts leak into chat.history | Memory pre-compaction prompts surfaced as user turns | Fixed v2026.5.4 — kept runtime-only |

---

## What's New in v2026.5.2

_(Polish/architecture release. No major breaking changes; focus on plugin externalization, perf, and bug fixes.)_

### Architectural Shift — Plugin Externalization

The big structural change in 5.2: many plugins are being **moved out of the core npm package** into separately-published `@openclaw/*` packages. They will still ship pre-installed for now, but the cutover begins in `2026.5.1-beta.1`/`2026.5.1-beta.2`.

Plugins being externalized: `@openclaw/acpx`, `@openclaw/diagnostics-otel`, plus Google Chat, LINE, Matrix, Mattermost, BlueBubbles, Diagnostics Prometheus, Google Meet, Nextcloud Talk, Nostr, Zalo, Zalo Personal, Discord, Diffs, Lobster, Memory LanceDB, Microsoft Teams, QQ Bot, Voice Call, WhatsApp, Brave, Codex, Feishu, Synology Chat, Tlon, and Twitch.

**Why it matters:** Heavier runtime stacks stay out of core. Plugin runtime preloads are now scoped to effective IDs from your config rather than every discoverable plugin (faster startup, smaller memory footprint).

### Breaking / Noteworthy Defaults
- **`threadBindings.spawnSessions` replaces split toggles** (v2026.5.2): The previous separate subagent and ACP thread-spawn toggles are unified under `threadBindings.spawnSessions`. Thread-bound spawns are now ON by default. Run `openclaw doctor --fix` to migrate the legacy keys.
- **xAI default chat model = Grok 4.3** (v2026.5.2): Bundled xAI catalog adds Grok 4.3 and makes it the default.
- **Codex runtime guidance** (v2026.5.2): For ChatGPT/Codex subscription setups, prefer `openai/gpt-*` with `agentRuntime.id: "codex"` for the **native Codex runtime**. `openai-codex/*` remains the **PI OAuth route**. Both work; native Codex runtime is more first-class for non-subscription paths.
- **Codex app-server tools default native-first** (v2026.5.2): Codex sessions keep OpenClaw integration tools but leave file/patch/exec/process ownership to the Codex harness. Codex-harness direct source replies default to the OpenClaw `message` tool when visible reply delivery is not explicitly configured.

### New Features

**Plugin / CLI Management:**
- **`openclaw plugins deps --repair`** (v2026.5.2): Dedicated subcommand for repairing missing/incomplete bundled plugin dependencies. Routine plugin inspection and channel maintenance commands no longer auto-download plugin deps — explicit repair is the new pattern.
- **`openclaw plugins list --json` includes dependency state** (v2026.5.2): Scripts can detect missing plugin deps without runtime-loading the plugin.
- **`git:` plugin installs** (v2026.5.2): First-class `git:<url>#<ref>` plugin specs with ref checkout, commit metadata, scanner/staging, and `plugins update` support for recorded git sources.
- **ClawPack metadata** (v2026.5.2): Diagnostics, onboarding, doctor repair, and channel setup carry ClawPack metadata through install records. Versioned ClawPack artifacts preferred when ClawHub publishes digest metadata; ClawPack response headers + downloaded bytes are verified.
- **Plugins/Crestodian** (v2026.5.2): New ClawHub plugin search + Crestodian list/search/install/uninstall ops, with approval and audit coverage.
- **Beta channel plugin fallback** (v2026.5.2): On the beta OpenClaw update channel, default-line plugin updates try `@beta` first and fall back to default/latest when no plugin beta release exists.

**Gateway:**
- **`openclaw gateway restart --force` and `--wait <duration>`** (v2026.5.2): New flags for forced/timed restart. Timeout restarts now report as explicit forced restarts, not silently coerced.
- **Faster gateway/agent hot paths** (v2026.5.2): Startup secrets preflight skips plugin-backed auth-profile overlays (reload + OAuth recovery still go through them). Session listing, task maintenance, prompt prep, plugin loading, tool descriptor planning, filesystem guards, and large runtime configs are all leaner.
- **SDK `tools.invoke` RPC** (v2026.5.2): SDK-facing tools.invoke RPC with shared HTTP policy, typed approval/refusal results, and SDK helper support.
- **`openclaw proxy validate`** (v2026.5.2): Verify effective proxy config, proxy reachability, and expected allow/deny destination behavior before deploying proxy-routed OpenClaw commands.

**Channels:**
- **WhatsApp Channel/Newsletter outbound targets** (v2026.5.2): Explicit `@newsletter` outbound message targets with channel session metadata (no longer routed as DM).
- **Discord access groups** (v2026.5.2): Reusable message-channel access groups + Discord channel-audience DM authorization. Allowlists can now reference `accessGroup:<name>` across channel auth paths.
- **Discord interaction persistence** (v2026.5.2): Active buttons, selects, and forms work across Gateway restarts until they expire. Multi-step Discord interactions less likely to break during upgrades.
- **Slack App Home + thread continuity** (v2026.5.2): Default App Home tab view on `app_home_opened`. Bot-participated threads tracked across restarts so ongoing threaded conversations continue auto-replying after Gateway restart.
- **BlueBubbles `replyContextApiFallback`** (v2026.5.2): Opt-in fetch from BlueBubbles HTTP API when in-memory reply-context cache misses (multi-instance deployments, post-restart, after long-lived TTL/LRU eviction). Off by default; concurrent webhooks for the same `replyToId` coalesce into one fetch.
- **Telegram benign delete-400s** (v2026.5.2): Treated as no-op warnings instead of errors. Stale or already-removed messages don't create noisy delete failures.

**Providers:**
- **xAI Grok 4.3** (v2026.5.2): Added to bundled catalog, default xAI chat model.
- **OpenAI-compatible TTS `extraBody`/`extra_body` passthrough** (v2026.5.2): Custom speech servers can receive fields like `lang` in `/audio/speech` requests.

**Google Meet:**
- **`googlemeet end-active-conference`** (v2026.5.2): Close managed spaces after a call.
- **`googlemeet test-listen` + `google_meet test_listen` action** (v2026.5.2): Transcribe-mode joins wait for real caption/transcript movement before reporting listen-first health.
- **API-created room control** (v2026.5.2): Set `accessType` and `entryPointAccess` on API-created rooms.
- **Live caption health for Chrome transcribe mode** (v2026.5.2): Caption observer state, transcript counters, last caption text, and recent transcript lines in status/doctor.

**Agents / Workspace:**
- **`agents.defaults.skipOptionalBootstrapFiles`** (v2026.5.2): Skip selected optional workspace files during bootstrap without disabling required workspace setup.

**Control UI / WebChat:**
- **UTC quarter-hour token buckets** (v2026.5.2): Usage Mosaic uses quarter-hour buckets, reused for hour filtering.
- **More resilient long-running sessions** (v2026.5.2): Sessions, Cron, long-running Gateway WebSockets, grouped-message width, slash-command feedback, iOS PWA bounds, selection contrast, and Talk diagnostics all hardened.

### Key Fixes (v2026.5.2)
- **Plugin SDK reply helpers restored** (v2026.5.2): `openclaw/plugin-sdk` reply-prefix and reply-pipeline helpers re-exposed on the deprecated root/compat surface so external plugins do not fail message dispatch after update.
- **Forced update restart on swap** (v2026.5.2): Non-deferred, no-cooldown update restarts after package-manager updates requested through the live Gateway control plane. Release validation fails on post-swap stale chunk import crashes (no more Telegram/Discord imports pointing at removed dist files).
- **Plugin runtime-deps repair** (v2026.5.2): No-main and export-map package sentinels without reachable entry files treated as incomplete. Gateway startup, doctor, and lazy plugin loads repair interrupted bundled dependency installs (no more package.json-only partial installs).
- **Provider/media stability** (v2026.5.2): Fixes for OpenAI-compatible TTS/Realtime, OpenRouter/DeepSeek replay, Anthropic-compatible streaming, LM Studio reasoning metadata, Brave/SearXNG/Firecrawl web search, media paths, music, and voice-call routing.
- **BlueBubbles attachment download failures** (v2026.5.2): Promoted from verbose to runtime error so silently-dropped inbound images are visible at default log level.
- **`sanitizeForLog`** (v2026.5.2): Now redacts `?password=…` / `?token=…` query params and `Authorization:` headers (CWE-532).

### New Config Keys (v2026.5.2)
| Config Path | Type | Description |
|---|---|---|
| `threadBindings.spawnSessions` | object | Unified replacement for split subagent/ACP thread-spawn toggles. Default ON. |
| `agents.defaults.skipOptionalBootstrapFiles` | array | Skip selected optional workspace files during bootstrap |
| `channels.bluebubbles.replyContextApiFallback` | boolean | Opt-in HTTP-API fetch when reply-context cache misses (default: off) |
| `auth.test` (env) | env | New auth test env var surface (referenced in 5.2 changelog) |
| `gateway.controlUi.chatMessageMaxWidth` | number | Cap grouped-message width in WebChat |
| `agents.defaults.compaction.midTurnPrecheck` | boolean | Mid-turn compaction precheck toggle |

### New Troubleshooting Entries (v2026.5.2)
| Symptom | Cause | Fix |
|---|---|---|
| Plugin install fails with "package directory is missing" | Bundled plugin payload missing/incomplete (npm-first cutover) | `openclaw plugins deps --repair`, then re-run `openclaw plugins update <id>` |
| Stale `plugins.entries.<id>` config warnings on startup | Config still references plugin that's now externalized or removed | `openclaw config unset plugins.entries.<id>` |
| `openclaw gateway restart` hangs on long-running tasks | Active task run holding restart deferral | Use `openclaw gateway restart --force` (new in 5.2) or `--wait <duration>` to bound the deferral |
| ChatGPT/Codex subscription setup unclear: `openai/*` vs `openai-codex/*` | Two routes with overlapping model IDs | `openai/gpt-*` + `agentRuntime.id: "codex"` = native Codex runtime (preferred for subscriptions). `openai-codex/*` = PI OAuth route. |
| Plugin from external `@openclaw/*` not loading | Plugin externalized in 5.2 (e.g. `@openclaw/acpx`) | Install explicitly: `openclaw plugins install @openclaw/<name>` |
| Subagent/ACP thread spawning behaves differently after upgrade | `threadBindings.spawnSessions` replaces legacy split toggles, default ON | Run `openclaw doctor --fix` to migrate. Toggle OFF via `threadBindings.spawnSessions: false` |
| Discord buttons stop working after gateway restart | Pre-5.2 didn't persist active interactions | Fixed in 5.2 — interactions persist until expiry |
| Slack threaded conversations stop auto-replying after restart | Bot-participated threads not tracked across restart | Fixed in 5.2 — threads tracked persistently |
| BlueBubbles silently drops inbound images | Attachment download failures logged at verbose level | Fixed in 5.2 — promoted to runtime error |
| WhatsApp Newsletter target routes as DM instead | Pre-5.2 didn't recognize `@newsletter` as channel session | Fixed in 5.2 — explicit channel session metadata |
| `openclaw proxy validate` not found | Pre-5.2 | Upgrade to v2026.5.2; `openclaw proxy validate` is new |
| `gateway restart --force` not recognized | Pre-5.2 | Upgrade to v2026.5.2; flag is new |

---

## What's New in v2026.4.29

_(npm jumped 4.27 → 4.29; no 4.28 published.)_

### Breaking / Noteworthy Defaults
- **Restrictive profiles no longer auto-widen** (v2026.4.29): Configured `tools.exec` / `tools.fs` sections **stop implicitly widening** the `messaging` and `minimal` profiles. Add explicit `alsoAllow` entries to keep behavior. Startup warning identifies affected configs.
- **Active-run queue default = `steer`** (v2026.4.29): `messages.queue` now defaults to `steer` (drains all pending Pi steering messages at the next model boundary) with a 500ms followup-fallback debounce. Legacy one-at-a-time behavior is `queue`.
- **Doctor migrates legacy TTS toggles** (v2026.4.29): `openclaw doctor --fix` now migrates legacy `messages.tts.enabled`, agent TTS, channel TTS, and voice-call plugin TTS toggles to `auto` mode.
- **`agents.defaultId` no longer accepted** (v2026.4.29): Use `agents.list[].default` for Set Default. Old field is rejected by config validation.

### New Features

**Providers / Models:**
- **NVIDIA bundled provider** (v2026.4.29): `NVIDIA_API_KEY` onboarding, setup docs, static catalog metadata, literal model-ref picker support so NVIDIA-hosted models can be selected with prefix intact. Bundled NVIDIA Chat Completions models marked as string-content compatible (fixes NIM model loading and OpenAI-compatible subagent calls).
- **DeepSeek V4 `xhigh` / `max` thinking** (v2026.4.29): Native thinking levels exposed through `resolveThinkingProfile`. `/think xhigh|max` now applies intended effort instead of falling back.
- **Bedrock Opus 4.7 thinking parity** (v2026.4.29): Full `xhigh`, `adaptive`, and `max` thinking profile exposed for Bedrock Claude Opus 4.7. Sonnet/Opus 4.6 stay on adaptive-by-default. Bedrock omits deprecated `temperature` for Opus 4.7 model ids.
- **Vercel AI Gateway xhigh** (v2026.4.29): Provider-owned `/think xhigh` for trusted OpenAI/Codex upstream refs; Claude adaptive thinking for Anthropic upstream refs.
- **Custom OpenAI-compat xhigh** (v2026.4.29): Honor `models.providers.<id>.models.<id>.compat.supportedReasoningEfforts` entries that include `xhigh` so `/think xhigh` is exposed and validated consistently across command menus, Gateway sessions, agent CLI, and `llm-task`.
- **`openai-codex/gpt-5.4-mini` restored** (v2026.4.29): Live OAuth proof restored for ChatGPT/Codex OAuth PI runs. Manifest, forward-compat metadata, docs, and regression tests aligned. Stale cron and heartbeat configs resolve again.
- **Codex `gpt-5.4-mini` inline suppression** (v2026.4.29): Explicitly configured `openai-codex/gpt-5.4-mini` inline entries are suppressed so a stale `models` config written by `openclaw doctor --fix` cannot bypass the manifest capability block.
- **Yuanbao alias** (v2026.4.29): Channel catalog adds `"yuanbao"` alias; plugin moved to `YuanbaoTeam/yuanbao-openclaw-plugin`.

**Memory / People Wiki:**
- **People wiki** (v2026.4.29): Agent-facing people metadata, canonical aliases, person cards, relationship graphs, privacy/provenance reports, evidence-kind drilldown, search modes for person lookup, question routing, source evidence, raw claims.
- **Active Memory chat-id filters** (v2026.4.29): Optional per-conversation `activeMemory.allowedChatIds` / `deniedChatIds` filters so operators enable recall only for selected DMs, groups, or channels.
- **Active Memory partial recall on timeout** (v2026.4.29): When the hidden memory sub-agent times out, returns bounded partial recall summaries (default temporary-transcript path) so useful recovered context isn't discarded.
- **REM dreaming preview RPC** (v2026.4.29): Read-only `doctor.memory.remHarness` RPC for previewing bounded REM dreaming output without running mutation paths.
- **`memory.qmd.update.startup`** (v2026.4.29): Make gateway-start QMD refresh opt-in. Normal memory access stays lazy.
- **`openclaw ltm list`** (v2026.4.29): Returns real memory records (with `--limit` and createdAt ordering) instead of placeholder.

**Agents / Commitments:**
- **Inferred follow-up commitments** (v2026.4.29): Opt-in `commitments.enabled` / `commitments.maxPerDay` config. Hidden batched extraction, per-agent/per-channel scoping, heartbeat delivery, CLI management, and heartbeat-interval due-time clamping (so check-ins don't echo immediately).
- **`messages.visibleReplies`** (v2026.4.29): Global require-visible-output gate. Forces replies through `message(action=send)` for any source chat. `messages.groupChat.visibleReplies` stays as group/channel override.
- **`spawnedBy` on subagent events** (v2026.4.29): Subagent chat and agent broadcast payloads now carry `spawnedBy` so clients can route child session events without an extra session lookup.
- **`heartbeat.skipWhenBusy`** (v2026.4.29): Defer heartbeat turns while cron is active or queued. Retries busy skips without advancing the schedule. Local Ollama hosts no longer run heartbeat and cron concurrently.

**Gateway / Diagnostics:**
- **Startup diagnostics timeline** (v2026.4.29): Opt-in config flag emits gateway lifecycle and plugin-load phase timing so slow-start diagnosis no longer needs bespoke instrumentation.
- **Event loop in `/readyz`** (v2026.4.29): Local or authenticated `/readyz` now includes `eventLoop` block (delay p99/max, utilization, CPU core ratio, `degraded` flag).
- **`gateway.handshakeTimeoutMs`** (v2026.4.29): Configurable WebSocket pre-auth handshake timeout (env `OPENCLAW_HANDSHAKE_TIMEOUT_MS` still wins). Loaded/low-powered hosts can tune without patching dist files. Pre-auth timeout raised to 15s.
- **Stuck-session recovery** (v2026.4.29): Conservative recovery releases only stale session lanes while active embedded runs, reply ops, and lane tasks remain serialized.
- **Bounded restart deferral** (v2026.4.29): Default restart-deferral and SIGUSR1 drain bounded to 5 min (explicit `deferralTimeoutMs: 0` still indefinite).

**CLI / Migration:**
- **`openclaw plugins deps`** (v2026.4.29): New inspection and repair subcommand with script-free package-manager defaults so operators can repair missing bundled runtime deps without corrupting JSON output.
- **`openclaw infer image describe` flags** (v2026.4.29): `--prompt` and `--timeout-ms` for media-understanding providers (Ollama, OpenAI, Google, OpenRouter).
- **`openclaw infer model run` images** (v2026.4.29): Repeatable `--file` inputs for local/gateway multimodal model smokes (Ollama Qwen VL, Gemini, etc.).
- **NVIDIA + Yuanbao docs entries** (v2026.4.29): Channel listing and sidebar nav.
- **`OPENCLAW_SKIP_ONBOARDING`** Docker env (already in 4.27, restated): Automated Docker installs skip interactive onboarding while still applying gateway defaults.

**Channels:**
- **Telegram polling/webhook liveness** (v2026.4.29): Channel status and doctor warn when a long-poller has not completed `getUpdates` after startup grace, transport activity is stale, or `setWebhook` has not completed after grace.
- **Telegram durable edit streaming** (v2026.4.29): Streaming previews use durable message edits instead of native draft state, eliminating draft-to-message flicker that looked like duplicates.
- **Telegram quote retry** (v2026.4.29): On `QUOTE_TEXT_INVALID`, retries native quote replies without `reply_parameters.quote` so stale/truncated excerpts don't drop the whole reply.
- **Telegram exec approvers from owner allowlist** (v2026.4.29): Telegram now infers native exec approvers from `commands.ownerAllowFrom` and auto-enables the approval client when an owner resolves. Owner-only `/diagnostics` etc. can be approved in Telegram without per-channel approver config.
- **Discord rate-limit cooldown** (v2026.4.29): Cloudflare/Error 1015 HTML 429s during startup application lookup and `/gateway/bot` metadata fetches now cool down properly. New `channels.discord.applicationId` for app-id lookup bypass. HTML bodies sanitized before logging.
- **Discord text-only intent drop** (v2026.4.29): Text-only configs can drop `GuildVoiceStates` gateway intent. Bounded `/gateway/bot` metadata timeout with rate-limited fallback logs.
- **Discord CJK chunking** (v2026.4.29): Long CJK replies split at punctuation and code-point-safe boundaries.
- **WhatsApp keepalive timings** (v2026.4.29): Explicit Baileys socket timings on every WhatsApp Web socket. New `web.whatsapp.*` keepalive, connect, and query timeout settings.
- **WhatsApp recovery on quiet sockets** (v2026.4.29): Recovers recently active listeners when post-408 reconnect keeps receiving transport frames but stops delivering app messages. Forces earlier reconnects on silent transport stalls.
- **Slack Block Kit limits** (v2026.4.29): Auto-truncates buttons/selects/fallback text to Slack's value, count, and message limits across native commands, exec approvals, message sends/edits, command argument menus, and confirmation dialogs.
- **Slack `already_reacted` idempotent** (v2026.4.29): Repeated reaction adds no longer surface as tool failures.
- **Mattermost ping/pong keepalive** (v2026.4.29): Protocol ping/pong with stale-pong reconnect.
- **Matrix verify confirm-sas** (v2026.4.29): `openclaw matrix verify confirm-sas` now completes the cross-signing handshake.
- **WhatsApp pairing tightened** (v2026.4.29): Pairing verification replies restricted to real inbound user content; receipts/typing/presence ignored.

**Security:**
- **OpenGrep rulepack** (v2026.4.29): Precise OpenGrep rulepack, source-rule compiler, provenance metadata check, and PR/full scan workflows uploading SARIF to GitHub Code Scanning.
- **GHSA triage policy** (v2026.4.29): Media/base64 decode and format-conversion overhead after configured acceptance limits classified as performance-only unless a report demonstrates a limit bypass, crash, exhaustion, data exposure, or boundary bypass.
- **`<system-reminder>` strip on outbound** (v2026.4.29): Internal runtime scaffolding stripped at the final channel delivery boundary so degraded harness replies can't leak those tags.
- **Telegram DM `dmPolicy="open"` tightened** (v2026.4.29): Fails closed when account-level public DM settings conflict with restrictive top-level `allowFrom`. Requires effective wildcard before `dmPolicy="open"` is public.
- **All-channels DM open semantics aligned** (v2026.4.29): Discord, Slack, Mattermost, Matrix, Feishu, LINE, IRC, Google Chat, Zalo, Zalo User, QQ Bot, Synology Chat — `dmPolicy="open"` is public only with effective wildcard; otherwise still respects sender allowlists.
- **Group-scoped tool policy auth** (v2026.4.29): Validates caller group IDs against session/spawned context before applying group-scoped tool policies. Forged group IDs can't unlock more permissive tools.
- **Subagent `/focus` boundary** (v2026.4.29): Leaf subagents rejected from `/focus`; fallback target resolution scoped to requesting subagent's children.
- **Bootstrap pairing scopes capped** (v2026.4.29): Bootstrap handoff token issuance, redemption, and approved pairing baselines bounded to documented per-role scope allowlist. Bootstrap approvals can't persistently grant `operator.admin`, `operator.pairing`, or `node.exec`.

### Key Fixes (highlights)
- **Telegram `ALL_PROXY` / `OPENCLAW_PROXY_URL`** (v2026.4.29): Honored when constructing the HTTP/1-only Telegram Bot API transport so Windows/service installs don't fall back to direct egress.
- **Anthropic Meridian content_block_start preservation** (v2026.4.29): Text and thinking content seeded on `content_block_start` is preserved so `[thinking, text]` replies don't persist as empty turns.
- **Codex Responses input items** (v2026.4.29): Sends a non-empty Responses input item when a turn only has systemPrompt-backed instructions (avoids ChatGPT 400 on `input: []`).
- **OpenAI-compat malformed SSE** (v2026.4.29): Malformed event-only or blank-data SSE frames dropped before the OpenAI SDK stream parser sees them. No more `Unexpected end of JSON input` from split proxies.
- **`<final>` tag splitting on streaming** (v2026.4.29): Stripped before reaching SSE clients so `/v1/chat/completions` no longer emits tag remnants when final-answer wrappers cross chunk boundaries.
- **Ollama `:cloud` model resolution** (v2026.4.29): Resolves explicitly selected signed-in `:cloud` models through `/api/show` when `/api/tags` omits them. Models like `gemini-3-flash-preview:cloud` and `deepseek-v4-pro:cloud` no longer fail dynamic resolution.
- **Ollama provider-prefixed tool calls** (v2026.4.29): Normalizes `functions.exec` to `exec` at the native stream boundary.
- **Local model context-window guard** (v2026.4.29): Derives thresholds from effective model window with 4k/8k safety floors. Small local models no longer rejected by fixed 16k/32k preflight cutoffs.
- **Plugin Windows fast path** (v2026.4.29): Native `require()` for bundled plugin modules on Windows. Startup ~39s → ~2s on typical 6-plugin setups.
- **macOS attach-only mode** (v2026.4.29): `--attach-only` / `--no-launchd` no longer uninstall the Gateway LaunchAgent or drop active sessions.
- **PDF.js standard fonts** (v2026.4.29): Resolves from installed package root with filesystem path fallback. Built-in font PDFs render without `file://` lookup failures.
- **Cron timeout cleanup** (v2026.4.29): Aborts and bounded-cleans timed-out isolated agent turns before recording the timeout. Stale cron sessions can't leave Discord/etc. stuck in `processing`.
- **Cron heartbeat coordination** (v2026.4.29): Defers missed isolated agent-turn catch-up out of the channel startup window.

### New Config Keys (v2026.4.29)
| Config Path | Type | Description |
|---|---|---|
| `commitments.enabled` | boolean | Opt-in inferred follow-up commitments |
| `commitments.maxPerDay` | number | Cap on commitments per day |
| `messages.queue` | string | `steer` (default v2026.4.29) \| `queue` \| `replace` \| `coalesce` \| `drop` |
| `messages.visibleReplies` | string | Global require-visible-output gate (`auto` \| `tool-only`) |
| `activeMemory.allowedChatIds` | array | Per-conversation Active Memory recall whitelist |
| `activeMemory.deniedChatIds` | array | Per-conversation Active Memory recall blacklist |
| `memory.qmd.update.startup` | boolean | Opt-in QMD refresh at gateway start (default off) |
| `gateway.handshakeTimeoutMs` | number | WebSocket pre-auth handshake timeout (default 15s) |
| `tools.web.fetch.ssrfPolicy.allowIpv6UniqueLocalRange` | boolean | Allow `fc00::/7` for trusted fake-IP proxy stacks |
| `web.whatsapp.keepalive.*` / `connect.*` / `query.*` | numbers | WhatsApp Web Baileys socket timings |
| `channels.discord.applicationId` | string | Bypass `/gateway/bot` app-id lookup |
| `heartbeat.skipWhenBusy` | boolean | Defer heartbeat while cron/subagent lanes are busy |
| `agents.list[].default` | boolean | Set the default agent (replaces deprecated `agents.defaultId`) |

### New Troubleshooting Entries (v2026.4.29)
| Symptom | Cause | Fix |
|---|---|---|
| `tools.exec` / `tools.fs` config under `messaging` profile silently no-ops | v2026.4.29 stops implicit profile widening | Add explicit `alsoAllow` entries; check startup warning for affected configs |
| `agents.defaultId` rejected by config validation | Field deprecated in v2026.4.29 | Use `agents.list[].default: true` instead |
| Telegram messages flicker between draft and message | Pre-v2026.4.29 used native draft state for streaming previews | Upgrade to v2026.4.29+ — uses durable message edits |
| Telegram polling claims healthy but messages stop flowing | Silent polling failure | v2026.4.29 surfaces polling liveness warnings in channel status / doctor |
| Slack message rejected with `msg_too_long` | Long context fallback not capped | v2026.4.29 caps Block Kit fallback while preserving rendered blocks |
| Discord startup failing on Cloudflare 429 HTML | Pre-v2026.4.29 didn't cool down HTML 429s | v2026.4.29 honors Retry-After + falls back to conservative cooldown; set `channels.discord.applicationId` to bypass |
| WhatsApp transport silently dies after 408 reconnect | Listeners didn't recover when frames kept arriving but app messages stopped | Fixed v2026.4.29 |
| `Unknown package 'sqlite-vec'` after upgrade | Memory bundled-plugin dep not mirrored | Fixed v2026.4.29 — mirrored into runtime deps |
| Ollama signed-in `:cloud` model fails to load | `/api/tags` omitted the model | v2026.4.29 falls through to `/api/show` |
| `[assistant copied inbound metadata omitted]` in chat output | Metadata-only assistant replay turns leaked as model output | Fixed v2026.4.29 — dropped before provider replay |
| Discord/Slack `dmPolicy="open"` allowing all senders despite `allowFrom` | Pre-v2026.4.29 inconsistent semantics | v2026.4.29 — `dmPolicy="open"` is public only with effective wildcard; otherwise still respects allowlists |
| Group-scoped tool policy applied to forged group ID | Caller group IDs not validated | Fixed v2026.4.29 — validated against session/spawned context |
| Bootstrap approval persistently grants `operator.admin` | Pairing scopes weren't capped | Fixed v2026.4.29 — bounded to documented per-role allowlist |
| `<final>` or `<system-reminder>` tag remnants in user-facing replies | Pre-v2026.4.29 didn't strip across chunk boundaries | Fixed v2026.4.29 |
| Bedrock Opus 4.7 `/think xhigh` doesn't take effect | Pre-v2026.4.29 only adaptive exposed | Fixed v2026.4.29 — full xhigh/adaptive/max profile |
| `models list` shows providers user has not authenticated | UI was always-show | Fixed v2026.4.29 — hides unauthenticated providers from default; use `models list --all` to browse all |

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

### OpenClam Connector Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `openclaw openclam pair --replace` says the previous connection could not be revoked, and direct connector DELETE returns `400 invalid_request` | The bridge rejected a production zero-byte DELETE body stream because it checked `request.body !== null` instead of checking whether the stream contained bytes | Read the DELETE stream safely, accept exactly zero bytes, reject any real payload, add an external empty-stream regression test, deploy the bridge, then retry replacement |
| Pairing returns `unauthorized` even though the freshly rotated bootstrap token succeeds against `POST /v1/pairings` directly | The default `OPENCLAM_BRIDGE_BOOTSTRAP_TOKEN` name may collide with or be overlaid by local OpenClaw startup environment handling | Pass the same token through a neutral one-shot variable and select it explicitly, for example `ARA_PAIRING_SECRET_TEMP="$token" openclaw openclam pair ... --bootstrap-secret-env ARA_PAIRING_SECRET_TEMP` |
| OpenClam shows an OpenClaw server path such as `/Users/.../image.png`, or a media-only reply becomes `empty_reply` | A text-only channel adapter ignored `ReplyPayload.mediaUrl` / `mediaUrls` and relayed model text literally | Use the official agent-scoped outbound-media loader, capability-gate `attachments-v1`, redact all local `file://`, POSIX, Windows-drive, and UNC paths from partial and final text, and never infer or read an arbitrary model-supplied path |
| OpenClam does not show what the agent is doing, or progress exposes tool details | Raw tool events were omitted or forwarded too literally | Capability-gate `activity-v1` and map supported reply callbacks to a fixed status enum only; never relay reasoning, commentary, tool arguments, commands, output, working directories, URLs, or arbitrary status text |
| A generated file disappears after relaunch or after the relay receives an ACK | The client acknowledged attachment metadata before the file and its turn association were durably stored | Enforce download -> MIME/length/SHA-256 verification -> protected local file -> durable turn association -> ACK; retain relay blobs privately until ACK, revoke, expiry, or a bounded 24-hour alarm |
| A transient OpenClaw connection failure leaves every later message stuck on recovery | A new turn was saved before socket delivery, then the UI attempted fresh turns instead of recovering the immutable outbox entry | Retry or cancel the exact saved turn ID and bytes, preserve the new composer draft, block deletion of its original chat, and clear the outbox only after the terminal result is saved to history |
| Activity/files work in development but not after a clean relay deployment | The attachment Durable Object class or rebuilt plugin runtime was omitted | Deploy the Worker migration that adds the private attachment class before enabling the new app/plugin, rebuild the plugin `dist/`, then restart the Gateway; clients that omit the new capabilities must remain text-only |

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

**This skill was last updated for:** `v2026.7.1-2`  
**Version check — 2026-08-24:** installed `2026.7.1-2` (0790d9f) · npm latest `2026.7.1-2` · deps ok — no drift. The skill matches the shipping release; `openclaw update status` reports up to date on the stable channel.

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
