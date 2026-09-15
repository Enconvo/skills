---
name: openclaw-configure
description: "Expert-level OpenClaw CLI configuration skill. Covers channels, models, plugins, gateway, agents, hooks, cron, security, sandbox, memory, browser, nodes, DNS, webhooks, approvals, backup, ACP provenance, ClawHub skill registry, tasks, and more. Self-evolving: updates itself after learning new patterns."
metadata:
  version: "2026.9.4"
  author: "zanearcher"
  category: "infrastructure"
  openclaw_version: "2026.9.4"
  last_verified: "2026-09-13"
  tags: "openclaw,cli,gateway,channels,models,plugins,agents,hooks,cron,security,sandbox,memory,browser,nodes,dns,webhooks,approvals,backup,acp,clawhub,skills,secrets,tasks"
---

# OpenClaw-Configure Skill

Configure any aspect of OpenClaw via CLI. Battle-tested from real setup sessions.

**Trigger on:** "openclaw", "clawhub", "add channel", "switch model", "configure gateway", "openclaw setup", "add telegram", "switch to claude", "openclaw cron", "openclaw hooks", "openclaw doctor", "install skill", "publish skill", "search skills", or any OpenClaw/ClawHub configuration task.

**Reference files** (same directory as this skill):
- `commands.md` — generated command entry-point usage and first-level subcommands
- `cli-reference.md` — installed CLI root and entry-point help; use nested `--help` for leaf options
- `oauth2-setup.md` — OAuth2 model setup guide
- `references/release-history.md` — preserved March–August release notes; historical, not current authority
- `scripts/refresh-cli-reference.mjs` — discover and regenerate the CLI references

**IMPORTANT — Version check:** Run the **Version Check & Auto-Update Protocol** below at the start of an OpenClaw task. An explicit update request already authorizes the update; otherwise report availability and ask before changing the installation. Never downgrade or change release channels without authorization.

**Current authority:** Installed `--help`, config schema, and matching release documentation outrank older examples below. Do not delete sessions, widen permissions, expose the gateway, or clear fallback chains as a generic troubleshooting step. Preserve custom integrations and user policy during updates.

---

## Core Principles

### Config Files
- **Main config:** `~/.openclaw/openclaw.json`
- **Agent models:** `~/.openclaw/agents/<agent>/agent/models.json` (auto-synced)
- **Auth profiles:** `~/.openclaw/agents/<agent>/agent/auth-profiles.json`
- **Workspace:** `~/.openclaw/workspace/` (AGENTS.md, SOUL.md, IDENTITY.md, etc.)

### The Plugin Gate
Many features are plugins. Before adding a channel or auth provider, check `openclaw plugins list`. If disabled, inspect and enable the intended plugin. Since v2026.8.1, install/update/enable can require artifact-bound capability consent. Review `openclaw plugins inspect <id> --runtime --json` and obtain any needed user authorization before using `--accept-capabilities`; `--yes` is not blanket capability consent. Forgetting the plugin gate causes **"Unknown channel"** errors.

### Gateway Restart
Validate config and inspect `openclaw gateway status --deep` before deciding whether a restart is needed. Use the installed service manager for an existing managed gateway:
```bash
openclaw config validate --json
openclaw gateway restart
openclaw health --json
```
Some config hot-reloads; plugin/package changes require restart. For authorized maintenance that needs a stopped service, v2026.8.1 non-interactive `gateway stop` requires `--force`, followed by `gateway start` when repairs finish. This is different from `gateway run --force`, which replaces a process occupying the port: do not use that as a generic restart or kill an unidentified listener. Never run migration/Doctor/update mutations concurrently.

### Config Validation
`openclaw.json` is schema-validated. Provider blocks need the full object (baseUrl, apiKey, api, models[]). For simple values use `openclaw config set`. For complex objects, edit JSON directly.

### Non-Interactive vs Interactive
- **Non-interactive:** `channels add`, `models set`, `config set`, direct JSON edits
- **Interactive (needs TTY):** `configure`, `models auth setup-token`, `models auth paste-token`, `onboard`
- When the agent cannot run interactive commands, ask the user to complete only the required interactive step.

---

## Channels

### Supported
telegram, whatsapp, discord, irc, googlechat, slack, signal, imessage, feishu, nostr, msteams, mattermost, nextcloud-talk, matrix, bluebubbles, line, zalo, zalouser, tlon, twitch

### Add Channel Workflow
```
1. openclaw plugins list                          # check plugin status
2. openclaw plugins enable <channel>              # enable if disabled
3. openclaw channels add --channel <name> --token <token>  # add
4. openclaw gateway restart                     # restart managed service if needed
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
Change only the requested model setting and inspect the result:
```bash
openclaw models set "provider/model-id"
openclaw models status --json
openclaw config validate --json
openclaw sessions --all-agents --json
```
Preserve fallback order, auth profiles, model aliases, and session history unless changing them is explicitly in scope. Existing sessions can have overrides; use supported session/model controls to inspect or change the intended session, not raw state edits. A paid probe or agent turn is not necessary for a read-only status request. On v2026.8.1, `modelPolicy.allow` is separate from aliases/per-model settings; Doctor migrates shipped `codex/*` and `openai-codex/*` references to `openai/*` while retaining Codex runtime intent. Review conflicts instead of rewriting custom routes blindly.

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
- **Current state (v2026.8.1):** Per-agent SQLite, normally `~/.openclaw/agents/<agent>/agent/openclaw-agent.sqlite`. Inspect the reported store path; do not assume a legacy JSON file is authoritative.
- **Legacy state:** `sessions/sessions.json` plus `<uuid>.jsonl` are migration inputs/archives. Doctor imports and verifies them before retirement. Never truncate them to force a reset.
- **Session keys:** `agent:<agent>:main` (DM/CLI), `agent:<agent>:discord:channel:<id>` (per-channel), etc.
- **Safe diagnostics:** `openclaw sessions --all-agents --json`; `openclaw doctor --session-sqlite inspect --session-sqlite-all-agents --json` checks integrity without importing/deleting state.
- **Session controls:** `sessions archive`, `compact`, and `delete` act through the running gateway. Inspect each `--help` and obtain explicit authorization for deletion. Do not edit `systemSent` or `authProfileOverride` in raw state.
- **Lifecycle:** v2026.8.1 does not automatically reset sessions daily/on idle unless explicitly configured.

### Legacy Session Fields (for migration diagnosis only)
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

**Fix:** Inspect the exact requesting device and required scope through the supported devices/pairing CLI. Ask the user to authorize any widened access, then approve or re-pair that specific device through the supported flow. Never hand-edit device tokens/scopes or clear pending approvals to bypass pairing.

### Clearing Stale Agent Sessions

After config changes, inspect the affected session first. If the user wants a fresh conversation, use the supported new-session/reset conversation action for that specific session. Preserve existing history; do not empty JSON indexes, delete transcripts, or write directly to SQLite as routine maintenance.

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
openclaw gateway restart  # restart managed gateway if a reload is required
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
| Gateway won't start / port in use | Existing process or wrong service/profile | Inspect `gateway status --deep` and the port owner; restart only the intended managed gateway |
| Channel status: no messages | Gateway not restarted | Restart after config changes |
| Ollama "Unknown model" | Missing apiKey | `apiKey: "ollama-local"` (dummy) |
| Ollama wrong api | Used "openai-chat" | Must be `"ollama"`, baseUrl without /v1 |
| "BOT_COMMANDS_TOO_MUCH" (Telegram) | Too many slash commands | Non-blocking, ignore |
| OAuth token expired | Past expiry | Re-run: `openclaw models auth login --provider <id>` |
| "Gateway service not loaded" | Service vs foreground mismatch | If already installed, `gateway start` can re-bootstrap it; inspect service configuration before reinstalling |
| Agent reports wrong model after switch | Self-description is not execution metadata | Inspect `models status --json` and the actual session/run metadata; preserve history |
| Model switched but agent still uses old one | Session override or route configuration | Inspect the affected session and change it through supported model/session controls, not raw state files |
| Fallback model used for first turn | OpenClaw tries fallback for system prompt delivery | Remove unwanted models from fallback chain (`models fallbacks remove`) |
| `models set` works but agent ignores it | Existing override or config not reloaded | Inspect active session/config and restart the managed gateway if required; do not reinstall the service by default |
| JSON shows correct model but text says wrong | Conversation text is not runtime identity | Trust execution metadata; do not delete a session just to change its self-description |
| `sessions_spawn` fails "pairing required" (1008) | Requesting device lacks required scope | Inspect the exact device and use an authorized supported pairing/scope approval flow; never hand-edit tokens or clear pending approvals |
| Agent refuses to retry after prior failure | Conversation context or unresolved error | Diagnose the error; offer a fresh conversation for the specific session without erasing history |
| Media "not under an allowed directory" | `workspace-*` dirs blocked by `assertLocalMediaAllowed()` | Save media to `~/.openclaw/media/` for sending. No config override exists |
| Agent defaults to wrong channel (e.g. WhatsApp) | `openclaw agent` defaults to `--channel whatsapp` | Always specify `--channel telegram --reply-account <id>` |
| `sessions_spawn` works from main but not between other agents | Only main has `subagents.allowAgents` | Add `subagents.allowAgents` to ALL agents that need to spawn others |
| `openclaw gateway stop` refuses a non-interactive maintenance call | v2026.8.1 requires explicit stop intent | After confirming maintenance is authorized and work is idle, use `gateway stop --force`; inspect any remaining listener before touching it |
| `openclaw update` says "Node X is too old for openclaw@Y" | Registry release raised the engine floor; managed runtime is pinned | Upgrade the managed runtime via `install-cli.sh --prefix ~/.openclaw --version latest --no-onboard`, then follow the service handoff sequence in the 2026.9.4 observations. Do not `npm i -g openclaw` bare — it may silently pick an older release |
| "refused shared state schema mutation … another Gateway owns that state directory" | Old Gateway still running while new CLI needs a schema migration | `gateway stop --force`, then `gateway install --force` / `update repair --yes` from a fresh shell, then `gateway start` |
| `update repair` fails: "Doctor could not enter maintenance. The update parent owns Gateway activation" | Doctor refuses to stop a live managed Gateway | Stop the service yourself first; rerun `update repair --yes`; start afterwards (repair never restarts) |
| Config changes not taking effect after restart | Wrong profile/service or old process | Inspect service command, config path, and port ownership, then restart the intended gateway |
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

## What's New in v2026.9.4

Verified against the installed CLI and packaged changelog on 2026-09-13 (update performed 2026.8.1 → 2026.9.4). See the [official release notes](https://docs.openclaw.ai/releases/2026.9.4) and [rollback and recovery](https://docs.openclaw.ai/install/updating/rollback-and-recovery).

- **Node engine bump:** 2026.9.4 requires Node `>=24.16.0 <25 || >=26.1.0` (24.15.0 is rejected: `node:sqlite` truncates TEXT at embedded NUL). `openclaw update` refuses with a clear message instead of installing an older compatible release. Upgrade the managed runtime first (see Recovery Observations).
- **Update rollback:** schema-neutral failed updates can restore the retained package, shim, service, and pre-activation config. Migration-bearing upgrades (this one: state v16/v17) block automatic rollback — a verified `backup create --verify` beforehand is mandatory. New `update cleanup` retires recovery originals after acknowledging rollback loss; do not run it as routine tidy-up.
- **Service ownership gates:** the new CLI refuses shared-state schema mutation while an older Gateway owns `~/.openclaw/state/openclaw.sqlite`. `update repair` will not stop/restart the Gateway itself; Doctor must run from an independent shell with the service stopped.
- **Plugins workspace:** bundled + ClawHub plugins discoverable/installable from the Control UI. Plugin cohort convergence no longer re-updates unchanged installs (`0 updated, N unchanged`).
- **Read-only deployments:** `OPENCLAW_CONFIG_READONLY=1` blocks config rewrites across setup, Doctor, plugin changes, and updates.
- **Cloud ready workers / snapshots:** prepared workers incur running-machine charges until deleted; `cloudWorkers.profiles.<id>.readyWorkers` / `cloudWorkers.preparedPool.maxTotal` set to 0 disables reserves. Do not enable during routine maintenance.
- **SDK:** `buildCredentialSafetyPrompt` string argument deprecated (supported through 2026-11-30; pass `{ controlToolsAvailable }`). Untrusted-context identifier aliases remain `removal-pending`.
- **CLI surface:** 73 root entry points, no additions/removals vs 2026.8.1. `update` gained `cleanup`; `repair` now also reconciles abandoned updates.
- **Models:** GPT Image 2.5 (Flare/Sunburst) selectable via OpenAI or fal; Deepgram Flux voice-note models need `ffmpeg`.

## Historical Release Notes

For March–August 2026 release details (including 2026.8.1), read `references/release-history.md` only when diagnosing an older installation or a version-specific migration.

### OpenClam Connector Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Local `openclaw openclam status` still says paired, but `openclaw openclam pair-device --json` fails with `not_found` after a code was never redeemed | The bridge retires the unredeemed remote connector after the pairing TTL and cleanup grace, while the local plugin configuration and credentials remain | Treat local status as configuration-only, not remote health. Reconnect with the bridge setup key using `openclaw openclam pair --replace ...`, then immediately redeem the fresh iPhone code; never log or persist the one-shot setup key |
| `openclaw openclam pair --replace` says the previous connection could not be revoked, and direct connector DELETE returns `400 invalid_request` | The bridge rejected a production zero-byte DELETE body stream because it checked `request.body !== null` instead of checking whether the stream contained bytes | Read the DELETE stream safely, accept exactly zero bytes, reject any real payload, add an external empty-stream regression test, deploy the bridge, then retry replacement |
| Pairing returns `unauthorized` even though the freshly rotated bootstrap token succeeds against `POST /v1/pairings` directly | The default `OPENCLAM_BRIDGE_BOOTSTRAP_TOKEN` name may collide with or be overlaid by local OpenClaw startup environment handling | Pass the same token through a neutral one-shot variable and select it explicitly, for example `ARA_PAIRING_SECRET_TEMP="$token" openclaw openclam pair ... --bootstrap-secret-env ARA_PAIRING_SECRET_TEMP` |
| OpenClam shows an OpenClaw server path such as `/Users/.../image.png`, or a media-only reply becomes `empty_reply` | A text-only channel adapter ignored `ReplyPayload.mediaUrl` / `mediaUrls` and relayed model text literally | Use the official agent-scoped outbound-media loader, capability-gate `attachments-v1`, redact all local `file://`, POSIX, Windows-drive, and UNC paths from partial and final text, and never infer or read an arbitrary model-supplied path |
| A generated local Markdown file link stays text, and the generic `message` tool reports `Channel unavailable: openclam` | Core static deliverable-channel discovery does not include the custom OpenClam channel, even when its plugin is connected | Promote supported local Markdown links inside OpenClam's channel-owned active turn, load them through scoped outbound-media access, and emit authenticated `assistant.attachment` frames; do not route them through the generic message tool |
| OpenClam attachment upload fails before reaching the relay with `UND_ERR_INVALID_ARG: invalid content-length header` | OpenClaw's guarded network layer rejects a manually supplied `Content-Length` header | Pass a bounded `Buffer` body and let `fetch` calculate `Content-Length`; keep relay-side exact length, MIME, and SHA-256 validation |
| OpenClam does not show what the agent is doing, or progress exposes tool details | Raw tool events were omitted or forwarded too literally | Capability-gate `activity-v1` and map supported reply callbacks to a fixed status enum only; never relay reasoning, commentary, tool arguments, commands, output, working directories, URLs, or arbitrary status text |
| A generated file disappears after relaunch or after the relay receives an ACK | The client acknowledged attachment metadata before the file and its turn association were durably stored | Enforce download -> MIME/length/SHA-256 verification -> protected local file -> durable turn association -> ACK; retain relay blobs privately until ACK, revoke, expiry, or a bounded 24-hour alarm |
| A transient OpenClaw connection failure leaves every later message stuck on recovery | A new turn was saved before socket delivery, then the UI attempted fresh turns instead of recovering the immutable outbox entry | Retry or cancel the exact saved turn ID and bytes, preserve the new composer draft, block deletion of its original chat, and clear the outbox only after the terminal result is saved to history |
| Activity/files work in development but not after a clean relay deployment | The attachment Durable Object class or rebuilt plugin runtime was omitted | Deploy the Worker migration that adds the private attachment class before enabling the new app/plugin, rebuild the plugin `dist/`, then restart the Gateway; clients that omit the new capabilities must remain text-only |

## Self-Evolution Protocol

After learning a verified workflow, failure mode, or correction, update the skill that was actually invoked. Resolve its directory from the supplied `SKILL.md` path; do not assume `~/.claude/skills`, `~/.codex/skills`, or `~/.agents/skills` is always correct. Preserve local OpenClam and other custom integration knowledge. Record the version and verification date, keep secrets out of the skill, and move historical detail to references rather than expanding the main instructions indefinitely.

## Version Check & Auto-Update Protocol

**This skill was last refreshed for:** `v2026.9.4`  
**Version check — 2026-09-13:** installed `2026.9.4` (3a9d69d) on managed Node 24.19.0 · npm latest `2026.9.4` · stable channel. Updated from 2026.8.1 (ea80657) this date; state migrations v16 (Skill Workshop ownership) and v17 (prepared worker ownership) applied, shared-state indexes rebuilt. `update status` still reports package-manager/dependency status as `unknown` for the managed-runtime layout; this is not a verified dependency failure.

### Version Check (at the start of an OpenClaw task)

Run these read-only checks, in parallel when practical:

```bash
openclaw --version
openclaw update status --json
```

Read the actual JSON shape: v2026.8.1+ (unchanged in 2026.9.4) uses `update.registry.latestVersion`, `channel.value`, and `availability`. Compare installed, selected-channel registry, and `metadata.openclaw_version` from this skill. Present a compact three-row version comparison.

- **In sync:** proceed, without asserting runtime health from version equality alone.
- **Newer version available:** an explicit update request is sufficient authorization. Otherwise report it and ask before updating.
- **Registry older than local, unavailable, or errored:** do not downgrade, switch channels, or call it up to date. Keep the installation and explain the uncertainty.
- **Skill differs from installed:** refresh against the actual installed version, preserving version-specific history and local notes.
- Use semantic version/channel information, not lexical string ordering. Check the release notes for the exact update range.

### Safe Update Procedure

1. Inspect `gateway status --deep`, `health --json`, `plugins list --json`, `channels status --json`, and active work. Identify the package root, executable/runtime, service manager, profile, and installation channel. Avoid stopping busy work without resolving its impact.
2. Back up the actual skill and config, and create a verified state backup outside the state directory:
   `openclaw backup create --output <private-backup-directory> --verify --json`.
   Use a private directory, restrictive permissions, and the installed command help. Backups contain credentials and conversations; never publish them.
3. Run `openclaw update --yes` for the existing channel. Do not mix npm/manual reinstall paths into a running updater or run Doctor/plugin migrations concurrently.
4. If the core changed but finalization failed, diagnose the exact failure before rerunning the package update. `openclaw update repair --yes` runs Doctor/plugin convergence but **never restarts the gateway**. Doctor can change unrelated optional skill settings; compare with the pre-update config and preserve the user's prior choices.
5. Review plugin capability changes. `--yes` does not imply `--accept-capabilities`. Inspect the actual plugin/runtime, explain capabilities, and obtain any needed permission before accepting. Do not silently replace a custom archive plugin with an unrelated registry package.
6. Validate config, restart the existing managed gateway if required, and verify both gateway/CLI versions, live channel connectivity, plugin load errors, and session integrity. Do not send test chat messages or run paid inference merely to prove a service is alive unless authorized.
7. Report the actual outcome and remaining warnings. Core version equality is not proof that plugins converged. Retired legacy files must be verified imported/archived, with a recoverable backup.

### Skill Refresh Procedure

1. Announce the refresh and resolve the **invoked skill directory**. Back it up before changing anything.
2. Regenerate both references using the installed CLI:
   `node <skill-directory>/scripts/refresh-cli-reference.mjs`.
   Use `--extra <command>` only for a plugin entry point verified to exist but absent from root help. The script captures all pages before writing and checks that the CLI version stayed constant. It discovers root commands rather than freezing an old domain list.
3. Read the matching packaged `CHANGELOG.md` and official release/update documentation. Discover the installation root from update status or the resolved executable; wrapper paths may not imply the npm root.
4. Summarize meaningful changes: migrations, removed/renamed commands, config/policy changes, plugin SDK changes, default behavior, and security boundaries. Update active recipes that conflict with current behavior. Preserve older release observations in `references/release-history.md`.
5. Update `metadata.version`, `metadata.openclaw_version`, `metadata.last_verified`, and the version record above. Keep custom metadata nested under `metadata` so skill validation succeeds.
6. Validate the skill, verify generated headings/coverage against fresh help, and confirm custom OpenClam notes remain. Recheck installed and registry versions. Claim registry alignment only when that lookup succeeded.

### v2026.9.4 Update Observations (verified 2026-09-13)

- **Managed-runtime layout:** this install uses the user-space layout from `https://openclaw.ai/install-cli.sh`: `~/.openclaw/tools/node-v<ver>/` (Node + global openclaw package), `~/.openclaw/tools/node` symlink, and wrapper `~/.openclaw/bin/openclaw`. It is not Homebrew/nvm. `openclaw update` cannot bump this runtime itself.
- **Runtime upgrade path that worked:** stop nothing first; run `bash install-cli.sh --prefix ~/.openclaw --version latest --no-onboard` (defaults to Node 24.19.0). It installs the new Node side-by-side, relinks `tools/node`, installs openclaw@latest, rewrites the wrapper, and leaves the old `node-v24.15.0` dir as rollback. Its own `gateway install --force` step fails while the old Gateway runs (state-ownership gate) — expected.
- **Service handoff sequence:** `gateway stop --force` → confirm port free → `gateway install --force --port 18789` (Doctor runs migrations here and replaces the unsupported Node path in the LaunchAgent plist; it also adds `--max-old-space-size`) → `gateway start`. Then `gateway stop --force` again → `update repair --yes` (Doctor + plugin convergence, needs stopped service) → `gateway start`. Verify `health --json`, `plugins list --json`, and `doctor --session-sqlite inspect --session-sqlite-all-agents --json` (`integrityCheck: ok`, session count unchanged).
- **Doctor prompts to leave alone:** it offers to disable 34 unusable allowed skills and flags a pending CLI device re-approval (scope widening `operator.read` → `admin,read,write`). Both are user policy decisions; report, do not apply.
- **Custom plugins:** `codex` (global) converged to 2026.9.4 automatically; `openclam` (global archive, 0.1.0) loaded without SDK errors and was correctly skipped by plugin update.
- **Pre-existing OpenClam recovery loop:** `handshake_rejected status=404` + `connection_retired` was present before the update; local `openclam status` still says paired. This is the retired-connector case — needs `openclam pair --replace` with the bridge setup key, not an update fix.

### v2026.8.1 Recovery Observations (verified 2026-08-31)

- **Legacy approvals can block Doctor itself.** On build ea80657, the repair sequence attempted obsolete generated-approval repair before importing `exec-approvals.json`. Trace the exact installed error; do not delete the file, disable the gate, or manually manufacture SQLite rows. A backed-up, stopped-gateway recovery used the shipping `state-migrations.exec-approvals-*.js` module's verified detect/import routine. It locks state, validates and checks the imported payload, records a durable migration receipt, and retires the legacy file only after success. Internal export names/hashes are version-specific: inspect the installed module before using this narrow fallback. Then retry `update repair`.
- **Custom OpenClam media import moved.** If loading fails because `media-runtime` no longer exports `getAgentScopedMediaLocalRootsForSources`, import that helper from `openclaw/plugin-sdk/media-local-roots`; keep MIME helpers on `media-runtime`. Preserve the same scoped loader and file-access checks. Back up the installed plugin, change only the import, and verify runtime inspection plus live connection. An installed `dist/` correction must also be ported to the source before the next rebuild/reinstall.
- **Capability consent is separate from compatibility.** A plugin may load with a consent warning while its replacement is deferred. Do not confuse “loaded” with “updated” or silently accept widened capabilities.
- **Scoped post-update consent:** After approval for specific plugins, use `plugins enable <id> --accept-capabilities` and targeted `plugins update <id> --accept-capabilities` for the reviewed replacement. Rerun `update repair --yes` without a blanket consent flag to verify convergence. The v2026.8.1 Codex plugin adds a `codex` CLI entry; regenerate help after plugin convergence, not only after the core update.
- **Session migration verification:** `doctor --session-sqlite inspect --session-sqlite-all-agents --json` should report the migrated sessions and `integrityCheck: ok`. Do not delete archived JSON/JSONL files to quiet historical notices.
