---
name: team-configure
description: "End-to-end team member lifecycle management: create channel bots (Telegram/Discord), configure AI agents (OpenClaw/EnConvo), pair channels to agents, set up agent2agent mesh, manage group allowlists. Supports ad-hoc add/remove and full team setup from scratch. Self-contained: bundles enconvo-gw, auto-installs OpenClaw, walks through all first-time setup."
version: 2.0.0
author: zanearcher
category: infrastructure
---

# Team Configure Skill

Orchestrate full team member lifecycle — from channel bot creation to AI agent configuration to pairing. Fully self-contained: bundles enconvo-gw, detects/installs OpenClaw, walks users through first-time setup of all dependencies.

**Trigger on:** "team configure", "team setup", "add team member", "remove team member", "team mesh", "setup team from scratch", "team pairing", "new agent setup", "full team setup", "team member lifecycle"

---

## Skill Contents

```
team-configure/
  SKILL.md                          # This file (all instructions)
  scripts/
    setup.sh                        # Bootstrap: install/update all dependencies
  enconvo-gw/                       # Bundled enconvo-gw source (not publicly available)
    bin/enconvo-gw.js               # CLI entry point
    src/                            # Full source (Node.js ESM)
    package.json                    # grammy + discord.js + commander
    package-lock.json
```

---

## FIRST THING: Bootstrap Check

**Before ANY operation**, run the bootstrap check. This ensures all tools are ready.

```bash
# Quick status check
bash <SKILL_DIR>/scripts/setup.sh status
```

Where `<SKILL_DIR>` = the directory containing this SKILL.md (e.g., `~/.claude/skills/team-configure`).

If anything is missing, run:
```bash
bash <SKILL_DIR>/scripts/setup.sh all
```

This handles:
1. **OpenClaw** — publicly available, installed via `npm install -g openclaw`. If missing, auto-installs. If present, checks for updates.
2. **enconvo-gw** — NOT public, bundled in this skill at `<SKILL_DIR>/enconvo-gw/`. Deployed to `~/enconvo-gw/`, npm-linked globally. Always syncs latest source from bundle.
3. **BotFather** — checks if `~/.claude/skills/botfather/` exists and Telethon is authenticated.
4. **Discord Dev** — checks if `~/.claude/skills/discord-dev/` exists and user token is saved.

---

## FROM-SCRATCH SETUP (First-Time User)

When the user has NOTHING installed and wants to build a team from zero, follow this complete walkthrough:

### Phase 0A: Install Node.js (if missing)

```bash
# Check
node --version && npm --version

# If missing:
# macOS:  brew install node
# Ubuntu: sudo apt install nodejs npm
# Or:     https://nodejs.org/ (official installer, all platforms)
```

### Phase 0B: Install OpenClaw

```bash
# Check if installed
openclaw --version

# If missing:
npm install -g openclaw

# First-time setup — interactive wizard
openclaw onboard --flow quickstart

# Or non-interactive minimal setup:
openclaw setup --mode local
```

After onboarding, verify: `openclaw status`

### Phase 0C: Deploy enconvo-gw (from bundled source)

```bash
bash <SKILL_DIR>/scripts/setup.sh enconvo-gw
```

This copies source from `<SKILL_DIR>/enconvo-gw/` to `~/enconvo-gw/`, runs `npm install`, and `npm link` for global CLI.

If the user already has enconvo-gw installed, this **updates** it to the version bundled in the skill (syncs source files, preserves node_modules if version matches).

Verify: `enconvo-gw gateway status`

### Phase 0D: Setup BotFather (Telegram bot management)

BotFather requires Telegram API credentials + Telethon authentication.

**Option 1: Playwright-assisted (recommended)**
1. Use Playwright MCP to navigate to `https://my.telegram.org/auth`
2. User enters phone number, completes SMS/2FA login
3. AI clicks "API development tools"
4. AI scrapes `api_id` and `api_hash` from the page (or fills the create-app form if no app exists)
5. Save credentials:
   ```bash
   ~/.claude/skills/botfather/scripts/botfather.sh save-creds --api-id <ID> --api-hash <HASH> --skip-auth
   ```
6. Run Telethon auth (INTERACTIVE — user must type phone + code in terminal):
   ```bash
   ~/.claude/skills/botfather/scripts/botfather.sh auth
   ```

**Option 2: Manual**
```bash
~/.claude/skills/botfather/scripts/botfather.sh setup
```
Prompts for api_id, api_hash, then authenticates interactively.

Verify: `~/.claude/skills/botfather/scripts/botfather.sh status`

### Phase 0E: Setup Discord Dev (Discord bot management)

Discord Dev requires a user session token extracted from the browser.

1. Use Playwright MCP to navigate to `https://discord.com/login`
2. User logs in
3. Navigate to `https://discord.com/developers/applications`
4. Extract token via `browser_evaluate`:
   ```js
   (webpackChunkdiscord_app.push([[''],{},e=>{m=[];for(let c in e.c)m.push(e.c[c])}]),m).find(m=>m?.exports?.default?.getToken!==void 0).exports.default.getToken()
   ```
   Fallback: `document.body.appendChild(document.createElement('iframe')).contentWindow.localStorage.token?.replace(/"/g, '')`
   Fallback 2: Check `browser_network_requests` for `Authorization` header
5. Save token:
   ```bash
   ~/.claude/skills/discord-dev/scripts/discord-dev.sh save-token --token "<TOKEN>"
   ```

Verify: `~/.claude/skills/discord-dev/scripts/discord-dev.sh status`

---

## Concepts

### Team Member = Agent + Channel Bot(s)
A team member consists of:
1. An **AI agent** on the platform (OpenClaw agent entry, workspace, identity)
2. One or more **channel bots** (Telegram bot, Discord bot) that route messages to that agent
3. **Bindings** that connect channel accounts to agents
4. **Pairing** that authorizes specific users to talk to the bot
5. **Agent2agent mesh** that allows inter-agent communication

### Platforms
- **Channel platforms:** Telegram, Discord (future: Slack, WhatsApp, Signal, etc.)
- **AI agent platforms:** OpenClaw (default), enconvo-gw (alternative)

---

## COMMAND REFERENCE (Self-Contained)

All commands needed by this skill, so it works without reading other skill files.

### BotFather (Telegram Bot Management)

Script: `~/.claude/skills/botfather/scripts/botfather.sh`

```bash
# Auth & Status
botfather.sh setup                              # Interactive setup (manual)
botfather.sh save-creds --api-id ID --api-hash HASH [--skip-auth]  # Save API creds
botfather.sh auth                               # Telethon auth (interactive terminal)
botfather.sh status                             # Check auth status

# Bot CRUD
botfather.sh list                               # List all bots
botfather.sh create "Display Name" "username_bot"  # Create new bot
botfather.sh delete @mybot                      # Delete a bot
botfather.sh info @mybot                        # Get bot info

# Bot Settings
botfather.sh set name @mybot "New Name"
botfather.sh set description @mybot "Description"
botfather.sh set about @mybot "About text"
botfather.sh set commands @mybot "cmd1 - Desc\ncmd2 - Desc"
botfather.sh set userpic @mybot /path/to/photo.jpg
botfather.sh set inline @mybot "Enable"|"Disable"
botfather.sh set joingroups @mybot "Enable"|"Disable"
botfather.sh set privacy @mybot "Enable"|"Disable"   # Disable = bot reads all group msgs

# Token
botfather.sh token @mybot                       # Get current token
botfather.sh token @mybot --revoke              # Revoke and get new token

# Raw
botfather.sh send "/mybots" [--follow-up TEXT] [--click] [--timeout N]
```

All commands support `--json` for machine-readable output.

### Discord Dev (Discord Application/Bot Management)

Script: `~/.claude/skills/discord-dev/scripts/discord-dev.sh`

```bash
# Auth
discord-dev.sh save-token --token "<user_session_token>"
discord-dev.sh status

# App CRUD
discord-dev.sh list                             # List all apps
discord-dev.sh create "App Name" [--bot]        # --bot adds bot user immediately
discord-dev.sh delete "App Name"
discord-dev.sh info "App Name"
discord-dev.sh update "App Name" --name "New" --description "..." --icon /path --public true|false

# Bot Management
discord-dev.sh bot-add "App Name"               # Add bot user (returns token ONCE)
discord-dev.sh bot-reset "App Name"             # Reset token (returns new token ONCE)

# Intents
discord-dev.sh intents "App Name"               # View current intents
discord-dev.sh intents "App Name" --enable MESSAGE_CONTENT GUILD_MEMBERS
discord-dev.sh intents "App Name" --disable PRESENCE

# OAuth2 / Invite
discord-dev.sh oauth2-url "App Name" --permissions 8 --scopes "bot applications.commands"

# Slash Commands
discord-dev.sh commands-list "App Name"
discord-dev.sh commands-set "App Name" '[{"name":"ping","description":"Pong!"}]'
```

Apps referenced by name (case-insensitive) or Discord snowflake ID. All support `--json`.

### OpenClaw (AI Agent Platform)

CLI: `openclaw` (installed globally via npm)

```bash
# Channels
openclaw channels add --channel telegram --account <id> --token "<bot_token>"
openclaw channels add --channel discord --account <id> --token "<bot_token>"
openclaw channels remove --channel <ch> --account <id> --delete
openclaw channels list [--json]
openclaw channels status [--probe]

# Agents
openclaw agents list [--bindings] [--json]
openclaw agents add [--workspace <dir> --bind telegram:<id> --non-interactive]
openclaw agents delete <id> [--force]
openclaw agents set-identity                    # Interactive: name/emoji/avatar

# Bindings (route channel accounts to agents)
openclaw agents bindings                        # List all bindings
openclaw agents bind --agentId <id> --channel <ch> --accountId <id>
openclaw agents unbind <agentId> --channel <ch> --accountId <id>

# Pairing
openclaw pairing list [--channel <ch>]
openclaw pairing approve <code> --channel <ch> [--account <id>] [--notify]

# Config (dot-path access to openclaw.json)
openclaw config get <dot.path>
openclaw config set <dot.path> <value>

# Plugins
openclaw plugins list [--enabled]
openclaw plugins enable <id>                    # e.g., telegram, discord

# Gateway
openclaw gateway                                # Start foreground
openclaw gateway --force                        # Kill existing + start
openclaw gateway stop
openclaw gateway restart
openclaw gateway status [--deep]

# Agent Execution
openclaw agent --agent <id> --message "text" [--deliver] [--local]

# Setup / Onboard
openclaw setup [--mode local|remote]
openclaw onboard [--flow quickstart|advanced]
openclaw --version
openclaw doctor [--fix]
```

**Key config paths in `~/.openclaw/openclaw.json`:**
```
agents.list[N].id                        Agent ID
agents.list[N].identity.name             Display name
agents.list[N].identity.emoji            Emoji
agents.list[N].subagents.allowAgents     Which agents this one can call
agents.list[N].workspace                 Workspace directory
agents.list[N].agentDir                  Agent state directory
agents.list[N].model.primary             Model (e.g., "anthropic/claude-opus-4-6")
tools.agentToAgent.enabled               Enable inter-agent comms (boolean)
tools.agentToAgent.allow                 Global list of callable agent IDs
channels.telegram.accounts.<id>          Telegram account config
channels.discord.accounts.<id>           Discord account config
bindings[]                               Channel-to-agent routing rules
plugins.entries.<id>.enabled             Plugin toggle
```

**Agent entry structure (agents.list[]):**
```json
{
  "id": "<agentId>",
  "name": "<agentId>",
  "workspace": "~/.openclaw/workspace-<agentId>",
  "agentDir": "~/.openclaw/agents/<agentId>/agent",
  "model": {"primary": "anthropic/claude-opus-4-6"},
  "identity": {"name": "<DisplayName>", "emoji": "<emoji>", "avatar": "portrait.png"},
  "subagents": {"allowAgents": ["main", "dev", "content", ...]}
}
```

**Binding entry structure (bindings[]):**
```json
{"agentId": "<agentId>", "match": {"channel": "telegram", "accountId": "<agentId>"}}
```

**Telegram account structure (channels.telegram.accounts.<id>):**
```json
{
  "enabled": true,
  "dmPolicy": "pairing",
  "botToken": "<token>",
  "groupPolicy": "open",
  "streaming": "partial"
}
```

**Discord account structure (channels.discord.accounts.<id>):**
```json
{
  "enabled": true,
  "token": "<bot_token>",
  "groupPolicy": "allowlist",
  "streaming": "off",
  "guilds": {"<guildId>": {"channels": {"<channelId>": {}}}}
}
```

### enconvo-gw (Alternative Gateway — Bundled)

CLI: `enconvo-gw` (deployed from `<SKILL_DIR>/enconvo-gw/`, npm-linked globally)
Source: `~/enconvo-gw/` | Data: `~/.enconvo-gw/`

```bash
# Gateway
enconvo-gw gateway                              # Start foreground
enconvo-gw gateway --force                      # Kill existing + start
enconvo-gw gateway stop
enconvo-gw gateway status

# Channels
enconvo-gw channels list
enconvo-gw channels status                      # Probe live connections
enconvo-gw channels add \
  --channel telegram|discord \
  --account <id> \
  --token <bot_token> \
  --agent <agentId> \
  [--dm-policy pairing|allowlist|open] \
  [--group-policy open]
enconvo-gw channels remove --channel <ch> --account <id>

# Agents
enconvo-gw agents list
enconvo-gw agents add --id <id> --name "Name" --model "ext/cmd" \
  [--type claude-code] \
  [--permission-mode bypassPermissions|plan] \
  [--working-dir /path] [--timeout 600000]
enconvo-gw agents remove --id <id>

# Pairing
enconvo-gw pairing list [channel]
enconvo-gw pairing approve <channel> <code>

# Config
enconvo-gw config get <dot.path>
enconvo-gw config set <dot.path> <value>
```

**DM policies:** `open` (all), `allowlist` (only approved), `pairing` (code-based approval, 8-char, 60min TTL)

**CRITICAL:** OpenClaw and enconvo-gw cannot poll the same bot token simultaneously. Disable one before enabling the other:
```bash
openclaw config set channels.telegram.accounts.<id>.enabled false
openclaw gateway --force
```

---

## OPERATIONS

### 1. Add a Single Team Member (Ad-Hoc)

#### Step 1: Plan
Gather from user:
- `displayName` — Human-readable name (e.g., "Isabelle")
- `agentId` — Slug ID (e.g., "macro")
- `role` — What this agent does (e.g., "macro research")
- `emoji` — Agent emoji
- `channels` — telegram, discord, or both
- `platform` — openclaw (default) or enconvo-gw

#### Step 2: Channel Side — Create Bots

**Telegram:**
```bash
botfather.sh create "<displayName>" "<botUsername>"
botfather.sh token @<botUsername> --json              # Save this token!
botfather.sh set privacy @<botUsername> "Disable"     # Bot reads all group msgs
botfather.sh set description @<botUsername> "<role> agent"
botfather.sh set about @<botUsername> "<role> agent for the team"
```

**Discord:**
```bash
discord-dev.sh create "<displayName>" --bot          # Save bot token from output!
discord-dev.sh intents "<displayName>" --enable MESSAGE_CONTENT GUILD_MEMBERS
discord-dev.sh oauth2-url "<displayName>" --permissions 8 --scopes "bot applications.commands"
# Open the URL in browser to invite to server
```

#### Step 3: AI Platform Side — Configure Agent

**OpenClaw:**
```bash
# 1. Enable plugins (if first time)
openclaw plugins enable telegram
openclaw plugins enable discord

# 2. Add channel accounts
openclaw channels add --channel telegram --account <agentId> --token "<TG_TOKEN>"
openclaw channels add --channel discord --account <agentId> --token "<DC_TOKEN>"

# 3. Create directories
mkdir -p ~/.openclaw/workspace-<agentId>
mkdir -p ~/.openclaw/agents/<agentId>/agent

# 4. Add agent to openclaw.json agents.list[]
#    (Edit JSON directly — add the agent entry object)

# 5. Add bindings
openclaw agents bind --agentId <agentId> --channel telegram --accountId <agentId>
openclaw agents bind --agentId <agentId> --channel discord --accountId <agentId>
```

**enconvo-gw:**
```bash
enconvo-gw agents add --id <agentId> --name "<displayName>" --model "ext/cmd" \
  --type claude-code --permission-mode bypassPermissions --working-dir ~
enconvo-gw channels add --channel telegram --account <agentId> \
  --token "<TG_TOKEN>" --agent <agentId> --dm-policy pairing
enconvo-gw channels add --channel discord --account <agentId> \
  --token "<DC_TOKEN>" --agent <agentId> --dm-policy pairing
```

#### Step 4: Agent2Agent Mesh Update

```bash
# Get all agent IDs
openclaw agents list --json

# For each existing agent at index N:
openclaw config get 'agents.list[N].subagents.allowAgents'
# Add <agentId> to the array:
openclaw config set 'agents.list[N].subagents.allowAgents' '[...existing, "<agentId>"]'

# Set new agent's allowAgents (all others):
openclaw config set 'agents.list[NEW_INDEX].subagents.allowAgents' '[<all IDs except self>]'

# Update global allow list:
openclaw config get 'tools.agentToAgent.allow'
openclaw config set 'tools.agentToAgent.allow' '[...existing, "<agentId>"]'
```

#### Step 5: Restart & Pair

```bash
# Restart gateway
openclaw gateway stop && sleep 2 && openclaw gateway
# (or for enconvo-gw: enconvo-gw gateway stop && enconvo-gw gateway --force)

# User sends /start to bot on Telegram (or first message on Discord)
# Check pending pairing requests:
openclaw pairing list telegram
openclaw pairing list discord

# Approve:
openclaw pairing approve <CODE> --channel telegram --notify
openclaw pairing approve <CODE> --channel discord --notify
```

#### Step 6: Group Membership (Optional)

**Telegram group:** Use Playwright MCP to open `https://web.telegram.org`, navigate to group -> Members -> Add Members, search for bot username.

**Discord server:** Open OAuth2 invite URL from Step 2 in browser, select server, authorize.

---

### 2. Remove a Team Member (Ad-Hoc)

#### Channel Side
```bash
botfather.sh delete @<botUsername>
discord-dev.sh delete "<displayName>"
```

#### Platform Side (OpenClaw)
```bash
openclaw channels remove --channel telegram --account <agentId> --delete
openclaw channels remove --channel discord --account <agentId> --delete
openclaw agents unbind <agentId> --channel telegram --accountId <agentId>
openclaw agents unbind <agentId> --channel discord --accountId <agentId>

# Edit openclaw.json:
# - Remove from agents.list[]
# - Remove from tools.agentToAgent.allow
# - Remove from every other agent's subagents.allowAgents

# Optional (confirm with user first):
# rm -rf ~/.openclaw/workspace-<agentId>
# rm -rf ~/.openclaw/agents/<agentId>

openclaw gateway stop && sleep 2 && openclaw gateway
```

#### Platform Side (enconvo-gw)
```bash
enconvo-gw channels remove --channel telegram --account <agentId>
enconvo-gw channels remove --channel discord --account <agentId>
enconvo-gw agents remove --id <agentId>
enconvo-gw gateway stop && enconvo-gw gateway --force
```

---

### 3. Full Team Setup from Scratch

The most complex operation. Follows all phases in order.

#### Phase 1: Prerequisites

Run the full bootstrap:
```bash
bash <SKILL_DIR>/scripts/setup.sh all
```

This installs/verifies: Node.js, OpenClaw, enconvo-gw, BotFather auth, Discord Dev auth.

If BotFather or Discord Dev need first-time setup, walk the user through Phase 0D / 0E (see FROM-SCRATCH SETUP above).

#### Phase 2: Planning

Gather from user:
```
Team Name: <name>
AI Platform: openclaw | enconvo-gw | both
Channels: telegram, discord
Members:
  - displayName, agentId, role, emoji
  - displayName, agentId, role, emoji
  - ...
```

Auto-generate naming:
- Telegram bot: `<firstname_lowercase>_bot` (must end in `bot` per Telegram rules)
- Discord app: `<DisplayName>`
- Agent ID: lowercase role slug (or custom)

Compute full mesh: each agent's `allowAgents` = all other agent IDs.

#### Phase 3: Create All Channel Bots

For each member, sequentially:

```bash
# Telegram
botfather.sh create "<displayName>" "<botUsername>"    # e.g., "isabelle_bot"
botfather.sh token @<botUsername> --json
botfather.sh set privacy @<botUsername> "Disable"

# Discord
discord-dev.sh create "<displayName>" --bot
discord-dev.sh intents "<displayName>" --enable MESSAGE_CONTENT GUILD_MEMBERS
discord-dev.sh oauth2-url "<displayName>" --permissions 8 --scopes "bot applications.commands"
```

**Collect all tokens in a structured list. Discord bot tokens are shown only once!**

#### Phase 4: Configure AI Platform

**OpenClaw:**

1. Enable plugins:
```bash
openclaw plugins enable telegram
openclaw plugins enable discord
```

2. For each member:
```bash
openclaw channels add --channel telegram --account <agentId> --token "<TG_TOKEN>"
openclaw channels add --channel discord --account <agentId> --token "<DC_TOKEN>"
mkdir -p ~/.openclaw/workspace-<agentId> ~/.openclaw/agents/<agentId>/agent
```

3. Edit `~/.openclaw/openclaw.json` directly:
   - Add all agents to `agents.list[]`
   - Add all bindings to `bindings[]`
   - Set `tools.agentToAgent.enabled: true`
   - Set `tools.agentToAgent.allow` to all agent IDs
   - For each agent, set `subagents.allowAgents` to all other IDs (full mesh)

**enconvo-gw:**

For each member:
```bash
enconvo-gw agents add --id <agentId> --name "<displayName>" --model "ext/cmd" --type claude-code
enconvo-gw channels add --channel telegram --account <agentId> --token "<TG_TOKEN>" --agent <agentId>
enconvo-gw channels add --channel discord --account <agentId> --token "<DC_TOKEN>" --agent <agentId>
```

#### Phase 5: Restart & Pair

```bash
openclaw gateway stop && sleep 2 && openclaw gateway
```

For each bot: user sends /start (Telegram) or first message (Discord), then:
```bash
openclaw pairing list telegram
openclaw pairing approve <CODE> --channel telegram --notify
```

#### Phase 6: Group Setup

Add all bots to team Telegram group (via Playwright on web.telegram.org).
Invite all Discord bots to server (via OAuth2 URLs in browser).

#### Phase 7: Verification

```bash
openclaw channels status --probe
openclaw agents list --bindings --json
openclaw agents bindings
openclaw agent --agent main --message "ping" --local
```

---

### 4. Update Agent2Agent Mesh

Recalculate full mesh for all agents:

```bash
openclaw agents list --json   # Get all IDs

# For each agent at index N, set allowAgents = all other IDs
openclaw config set 'agents.list[N].subagents.allowAgents' '[...]'

# Update global allow list
openclaw config set 'tools.agentToAgent.allow' '[all IDs]'
openclaw config set 'tools.agentToAgent.enabled' true

openclaw gateway stop && sleep 2 && openclaw gateway
```

---

### 5. Manage Group Allowlists

**OpenClaw Telegram:**
```bash
openclaw config set 'channels.telegram.accounts.<id>.groupPolicy' 'open'  # or 'allowlist'
```

**OpenClaw Discord:** Configure guilds in `channels.discord.accounts.<id>.guilds.<guildId>`

**enconvo-gw:** Set `--group-policy open` during `channels add`

---

## Important Notes

1. **Gateway restart required** after any config change
2. **Bot tokens are sensitive** — save immediately, never log plaintext
3. **Discord bot tokens shown once** — `bot-add` and `bot-reset` return only once
4. **Pairing is per-user** — each user must pair separately
5. **Full mesh = O(n^2)** — for large teams consider hub-and-spoke
6. **OpenClaw and enconvo-gw cannot share the same bot token** — disable one first
7. **BotFather auth is interactive** — needs terminal for phone + 2FA
8. **Discord dev token needs Playwright** — browser login for extraction
9. **enconvo-gw is bundled** in this skill at `<SKILL_DIR>/enconvo-gw/` — deploy via `setup.sh enconvo-gw`
10. **OpenClaw is public** — installed via `npm install -g openclaw`, auto-detected/installed by `setup.sh openclaw`
