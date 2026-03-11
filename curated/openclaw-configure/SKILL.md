---
name: openclaw-configure
description: "Expert-level OpenClaw CLI configuration skill. Covers channels, models, plugins, gateway, agents, hooks, cron, security, sandbox, memory, browser, nodes, DNS, webhooks, approvals, ClawHub skill registry, and more. Self-evolving: updates itself after learning new patterns."
version: 1.8.0
author: zanearcher
category: infrastructure
---

# OpenClaw-Configure Skill

Configure any aspect of OpenClaw via CLI. Battle-tested from real setup sessions.

**Trigger on:** "openclaw", "clawhub", "add channel", "switch model", "configure gateway", "openclaw setup", "add telegram", "switch to claude", "openclaw cron", "openclaw hooks", "openclaw doctor", "install skill", "publish skill", "search skills", "enconvo deeplink", "enconvo setup", "add enconvo agent", `enconvo://` URLs, or any OpenClaw/ClawHub configuration task.

**Reference files** (same directory as this skill):
- `commands.md` — condensed CLI reference, all 25 domains
- `cli-reference.md` — full `--help` for 142+ commands
- `oauth2-setup.md` — OAuth2 model setup guide

**IMPORTANT — Auto-Update Check:** Before answering any OpenClaw question, Claude MUST run the **Version Check Protocol** (see bottom of this file) to detect if a newer OpenClaw version is installed than what this skill documents. If yes, refresh the skill files first.

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
- `"enconvo"` — EnConvo via proxy: use `"openai-completions"` + proxy at `127.0.0.1:54536` (see EnConvo section below)

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

**EnConvo (macOS AI agent platform via proxy):**
- EnConvo runs at `http://localhost:54535` but doesn't speak OpenAI format
- **Solution:** a bundled proxy at `~/.claude/skills/enconvo-openclaw-setup/enconvo-proxy.mjs` translates OpenAI ↔ EnConvo
- Proxy listens on `http://127.0.0.1:54536`, forwards to EnConvo at `:54535`
- api: `"openai-completions"` (stock OpenClaw, no custom build needed)
- Deeplink format: `enconvo://{ext}/{cmd}` → model ID = `{ext}/{cmd}`
- No API key needed; use dummy `"token": "n/a"` in auth profiles
- **Proxy must be running** before the gateway starts

Start proxy: `nohup node ~/.claude/skills/enconvo-openclaw-setup/enconvo-proxy.mjs > /tmp/enconvo-proxy.log 2>&1 &`
Check proxy: `curl -s http://127.0.0.1:54536/health`

**EnConvo API Parameters** (full spec from extension schemas):

| Parameter | Type | Description |
|---|---|---|
| `user_input_text` | string | **Required** — primary user input |
| `input_text` | string | Secondary input (also accepted as primary) |
| `context_files` | string[] | File paths to include as context |
| `user_input_files` | string[] | User-uploaded file paths |
| `structure_output` | boolean | Return structured JSON output |
| `sessionId` | string | Session ID for conversation continuity |

**Discovering available EnConvo commands:**
```bash
# List all commands an extension exposes (source of truth)
python3 -c "
import json
d = json.load(open('$HOME/.config/enconvo/extension/{ext}/skills/schemas.json'))
for cmd in d:
    print(f'{cmd[\"route\"]:40s} | {cmd[\"title\"]}')
"
```
Schema files: `~/.config/enconvo/extension/{ext}/skills/schemas.json`

**Creating EnConvo agents programmatically** (no UI needed):
```bash
# CRITICAL: all fields must be wrapped in a "params" object
curl -X POST http://localhost:54535/enconvo_webapp/create_new_agent \
  -H "Content-Type: application/json" \
  -d '{
    "params": {
      "title": "My Agent",
      "commandName": "my_agent",
      "description": "A helpful agent",
      "run_mode": "agent",
      "prompt": "You are a helpful assistant.",
      "user_prompt_1": "{{input_text}}",
      "llm": {"isUseGlobalDefaultCommand": true},
      "tools": [{"tool_name": "file_system|read_file"}, {"tool_name": "code_runner|bash"}],
      "tts_providers": {"isUseGlobalDefaultCommand": true}
    }
  }'
# Creates: ~/.config/enconvo/installed_commands/custom_bot|my_agent.json
# Model ID for OpenClaw: custom_bot/my_agent
```

```json
"enconvo": {
  "baseUrl": "http://127.0.0.1:54536/v1",
  "apiKey": "n/a",
  "api": "openai-completions",
  "authHeader": false,
  "models": [
    {
      "id": "chat_with_ai/chat",
      "name": "Mavis (Team Lead)",
      "api": "openai-completions",
      "reasoning": false,
      "input": ["text"],
      "cost": {"input":0,"output":0,"cacheRead":0,"cacheWrite":0},
      "contextWindow": 128000,
      "maxTokens": 8192
    }
  ]
}
```

### EnConvo Agent Setup from Deeplink — Full Recipe

When user provides an `enconvo://` deeplink, follow this complete procedure. **Self-contained — no custom OpenClaw build needed.**

**Input needed:** deeplink (`enconvo://{ext}/{cmd}`), agent display name, agent ID (slug), optional Telegram bot token, optional Discord bot token.

**Step 1 — Parse deeplink:** Extract `{ext}/{cmd}` from `enconvo://{ext}/{cmd}`. This is the model ID.

**Step 2 — Verify EnConvo reachable:**
```bash
curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:54535/command/call/{ext}/{cmd} \
  -H "Content-Type: application/json" -d '{"input_text":"ping","sessionId":"setup-test"}'
```

**Step 3 — Start the EnConvo proxy (if not running):**
```bash
curl -s http://127.0.0.1:54536/health > /dev/null 2>&1 || \
  nohup node ~/.claude/skills/enconvo-openclaw-setup/enconvo-proxy.mjs > /tmp/enconvo-proxy.log 2>&1 &
sleep 2 && curl -s http://127.0.0.1:54536/health
```

**Step 4 — Edit `~/.openclaw/openclaw.json`:**

a) **Ensure enconvo provider exists** in `models.providers`. If missing, add the full block (see EnConvo provider recipe above — baseUrl `http://127.0.0.1:54536/v1`, api `"openai-completions"`).

b) **Add model** to `models.providers.enconvo.models[]` (skip if same `id` exists):
```json
{"id":"{ext}/{cmd}","name":"{displayName}","api":"openai-completions","reasoning":false,
 "input":["text"],"cost":{"input":0,"output":0,"cacheRead":0,"cacheWrite":0},
 "contextWindow":128000,"maxTokens":8192}
```

c) **Add agent** to `agents.list[]`:
```json
{"id":"{agentId}","name":"{agentId}",
 "workspace":"~/.openclaw/workspace-{agentId}",
 "agentDir":"~/.openclaw/agents/{agentId}/agent",
 "model":{"primary":"enconvo/{ext}/{cmd}"},
 "identity":{"name":"{displayName}","emoji":"\ud83d\udce6"},
 "subagents":{"allowAgents":["main","dev","content","ops","law","finance"]}}
```

d) **Add agent ID** to every other agent's `subagents.allowAgents` and to `tools.agentToAgent.allow`.

e) **Add Telegram account** (if token provided) to `channels.telegram.accounts`:
```json
"{agentId}":{"enabled":true,"dmPolicy":"pairing","botToken":"{token}","groupPolicy":"allowlist","streaming":"off"}
```

f) **Add Discord account** (if token provided) to `channels.discord.accounts`:
```json
"{agentId}":{"enabled":true,"token":"{token}","groupPolicy":"allowlist","streaming":"off","guilds":{copy from existing accounts}}
```

g) **Add bindings** to `bindings[]`:
```json
{"agentId":"{agentId}","match":{"channel":"telegram","accountId":"{agentId}"}}
{"agentId":"{agentId}","match":{"channel":"discord","accountId":"{agentId}"}}
```

h) **Enable plugin:** Ensure `plugins.entries.enconvo` is `{"enabled":true}`.

**Step 5 — Create agent directory + auth profile:**
```bash
mkdir -p ~/.openclaw/agents/{agentId}/agent ~/.openclaw/workspace-{agentId}
```
Write (or merge into existing) `~/.openclaw/agents/{agentId}/agent/auth-profiles.json`:
```json
{
  "version": 1,
  "profiles": {
    "enconvo:local": {"type":"token","provider":"enconvo","token":"n/a"}
  },
  "lastGood": {"enconvo":"enconvo:local"}
}
```
**IMPORTANT:** If auth-profiles.json already exists, READ it first and ADD the `enconvo:local` profile — don't overwrite other profiles.

**Step 6 — Restart gateway:**
```bash
pkill -9 -f "openclaw gateway" 2>/dev/null; sleep 1
openclaw gateway --force &
# Or: nohup pnpm openclaw gateway run --bind loopback --port 18789 --force > /tmp/openclaw-gateway.log 2>&1 &
sleep 8 && lsof -i :18789 | head -3
```

**Step 7 — Confirm:** Print summary of what was configured.

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
Auth: minimax-portal-auth, google-gemini-cli-auth, google-antigravity-auth, copilot-proxy, enconvo
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
```
**NEW in v2026.2.26:** ACP agents are now first-class runtimes for thread sessions with `acp` spawn/send dispatch integration, acpx backend bridging, lifecycle controls, startup reconciliation, runtime cleanup, and coalesced thread replies. Thread-bound subagents can now be dispatched via ACP for enhanced realtime capabilities.

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
| EnConvo agent "No API key found for provider enconvo" | Missing `enconvo:local` auth profile | Add `{"type":"token","provider":"enconvo","token":"n/a"}` to agent's `auth-profiles.json` + `lastGood.enconvo` |
| EnConvo agent returns empty/502 | Proxy not running | Start: `nohup node ~/.claude/skills/enconvo-openclaw-setup/enconvo-proxy.mjs > /tmp/enconvo-proxy.log 2>&1 &` then check: `curl -s http://127.0.0.1:54536/health` |
| EnConvo agent returns garbled response | Provider baseUrl points to EnConvo directly instead of proxy | Fix: `baseUrl` must be `http://127.0.0.1:54536/v1` (proxy), not `http://localhost:54535` |
| `create_new_agent` API returns `run_mode` error | Missing `params` wrapper in request body | Wrap all fields in `{"params": {...}}` — see EnConvo section above |
| `create_new_bot` returns success but no file created | Wrong API endpoint | Use `create_new_agent` instead — `create_new_bot` doesn't persist properly |
| Can't find available EnConvo commands | Need to discover command routes | Read `~/.config/enconvo/extension/{ext}/skills/schemas.json` for each extension's API schema |
| EnConvo curl works but OpenClaw agent fails | Proxy or EnConvo not running, or model ID mismatch | Test proxy: `curl -s -X POST http://127.0.0.1:54536/v1/chat/completions -H "Content-Type: application/json" -d '{"model":"{ext}/{cmd}","messages":[{"role":"user","content":"test"}]}'` |
| **BREAKING** Node exec approval fails (v2026.3.1+) | Approval payloads now require `systemRunPlan` | Add `systemRunPlan` to node `host=node` approval requests |
| **BREAKING** Node `system.run` path mismatch (v2026.3.1+) | Commands now pinned to canonical `realpath` | Update allowlists/tests to use canonical paths (e.g. `/usr/bin/tr` not `tr`) |
| OpenAI streaming fails silently (v2026.3.1+) | WebSocket transport is now default for OpenAI | Set `params.openaiWsWarmup: false` per-model if WS issues; or configure `transport: "sse"` to force SSE |
| Gateway WS insecure on private network (v2026.3.1+) | Plaintext `ws://` now loopback-only by default | Set `OPENCLAW_ALLOW_INSECURE_PRIVATE_WS=1` for private network access |
| Cron job runs at ~1/3 of configured timeout (v2026.3.1+) | Stale CLI session ID reused | Fixed in v2026.3.1 — isolated cron runs use fresh watchdog profiles |
| `cron run` returns 0 on failure | Exit code was always 0 | Fixed in v2026.3.1 — returns exit 1 for non-run/error outcomes |

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

**This skill was last updated for:** `v2026.3.7`

### Version Check (MANDATORY — run at start of every OpenClaw session)

Before answering any OpenClaw question, Claude MUST check both installed AND registry versions:

```bash
# 1. Get installed version
INSTALLED=$(openclaw --version 2>&1 | head -1)

# 2. Check latest available version from official registry
LATEST=$(openclaw update status --json 2>&1 | python3 -c "import sys,json; print(json.load(sys.stdin).get('registry',{}).get('latestVersion','unknown'))" 2>/dev/null || echo "unknown")

# 3. Check what this skill documents
SKILL_VERSION="v2026.3.7"
```

**Decision matrix:**
- If `INSTALLED` matches `SKILL_VERSION` AND no newer `LATEST` → proceed normally
- If `INSTALLED` is NEWER than `SKILL_VERSION` → trigger **Skill Refresh** (local update already happened)
- If `LATEST` is NEWER than `INSTALLED` → inform user: "OpenClaw vX.X.X available. Update with `openclaw update --yes`"
- If `LATEST` is NEWER than `SKILL_VERSION` AND `INSTALLED` matches `LATEST` → trigger **Skill Refresh** (user updated outside this session)

### Skill Refresh Procedure

When a newer OpenClaw version is detected (installed or available):

1. **Notify the user:** "OpenClaw updated to vX.X.X — refreshing skill knowledge..."

2. **Regenerate `cli-reference.md`:**
   ```bash
   # Capture top-level help
   openclaw --help > /tmp/oc-help.txt

   # For each command with subcommands (*), capture subcommand help too
   for cmd in acp agents approvals browser channels config cron devices directory dns gateway hooks memory message models node nodes pairing plugins sandbox security skills system update webhooks; do
     openclaw $cmd --help >> /tmp/oc-help.txt 2>/dev/null
   done
   ```
   Then write the formatted output to `~/.claude/skills/openclaw-configure/cli-reference.md`.

3. **Update `commands.md`:**
   - Update the version header line
   - Add any new commands or flags discovered from the help output
   - Remove any commands that no longer exist

4. **Check the CHANGELOG:**
   ```bash
   # The changelog lives in the npm package directory
   CHANGELOG_PATH=$(dirname $(which openclaw))/../lib/node_modules/openclaw/CHANGELOG.md
   # Read the section between the new version and the skill's old version
   ```
   Use the changelog to identify:
   - New features, channels, or providers to add to SKILL.md
   - Breaking changes or renamed commands
   - New config paths or options
   - Security changes

5. **Update this SKILL.md:**
   - Update `SKILL_VERSION` in the Version Check section above to the new version
   - Add new features/channels/providers to appropriate sections
   - Update troubleshooting table if needed
   - Bump the `version:` in the YAML frontmatter

6. **Confirm:** "Skill refreshed for vX.X.X. Ready."
