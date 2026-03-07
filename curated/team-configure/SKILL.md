---
name: team-configure
description: "End-to-end team member lifecycle management: create channel bots (Telegram/Discord), configure AI agents (OpenClaw/EnConvo), pair channels to agents, set up agent2agent mesh, manage group allowlists. Supports ad-hoc add/remove and full team setup from scratch. Self-contained: bundles enconvo-gw, auto-installs OpenClaw, walks through all first-time setup."
version: 2.0.0
author: zanearcher
category: infrastructure
---

# Team Configure Skill

Orchestrate full team member lifecycle — from channel bot creation to AI agent configuration to pairing. Fully self-contained: bundles enconvo-gw, BotFather scripts, Discord Dev scripts. Detects/installs OpenClaw. Walks users through first-time setup of all dependencies.

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
  skills/
    botfather/                      # Bundled BotFather skill (Telegram bot management)
      botfather.py                  # Python CLI (Telethon + argparse)
      botfather.sh                  # Shell wrapper (ensures venv + telethon)
      SKILL.md                      # BotFather-specific docs
    discord-dev/                    # Bundled Discord Dev skill (Developer Portal API)
      discord-dev.py                # Python CLI (stdlib only, no deps)
      discord-dev.sh                # Shell wrapper
      SKILL.md                      # Discord Dev-specific docs
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
3. **BotFather** — checks bundled BotFather scripts at `<SKILL_DIR>/skills/botfather/` and Telethon auth status.
4. **Discord Dev** — checks bundled Discord Dev scripts at `<SKILL_DIR>/skills/discord-dev/` and user token status.

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
   <SKILL_DIR>/skills/botfather/botfather.sh save-creds --api-id <ID> --api-hash <HASH> --skip-auth
   ```
6. Run Telethon auth (INTERACTIVE — user must type phone + code in terminal):
   ```bash
   <SKILL_DIR>/skills/botfather/botfather.sh auth
   ```

**Option 2: Manual**
```bash
<SKILL_DIR>/skills/botfather/botfather.sh setup
```
Prompts for api_id, api_hash, then authenticates interactively.

Verify: `<SKILL_DIR>/skills/botfather/botfather.sh status`

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
   <SKILL_DIR>/skills/discord-dev/discord-dev.sh save-token --token "<TOKEN>"
   ```

Verify: `<SKILL_DIR>/skills/discord-dev/discord-dev.sh status`

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

Script: `<SKILL_DIR>/skills/botfather/botfather.sh`

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

Script: `<SKILL_DIR>/skills/discord-dev/discord-dev.sh`

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

The most complex operation. Truly end-to-end: from "I have a company" to a fully operational AI team with identities, portraits, and live bots.

#### Phase 1: Prerequisites

Run the full bootstrap:
```bash
bash <SKILL_DIR>/scripts/setup.sh all
```

This installs/verifies: Node.js, OpenClaw, enconvo-gw, BotFather auth, Discord Dev auth.

If BotFather or Discord Dev need first-time setup, walk the user through Phase 0D / 0E (see FROM-SCRATCH SETUP above).

#### Phase 2: Discovery — Understand the Business

**Ask the user these questions** (adapt to conversation flow, don't interrogate):

1. **What does your company/team do?** — Industry, core business, product/service
2. **What's the team for?** — Internal ops, client-facing, research, trading desk, creative studio, dev team, etc.
3. **What channels do you need?** — Telegram, Discord, or both
4. **AI platform preference?** — OpenClaw (default), enconvo-gw, or both
5. **Team size preference?** — "Let me decide" or "suggest based on my needs"
6. **Any specific roles in mind?** — Or leave it to the AI to design

#### Phase 3: Team Design — Propose Composition

Based on the discovery answers, **design the team and present it for approval**. Consider:

**Role design principles:**
- Every team needs a **main** agent (team lead / coordinator / COO) — this is the `main` agentId
- Roles should cover the core functions of the business with minimal overlap
- Each agent should have a clear, distinct specialty
- Typical team sizes: 3-5 for focused teams, 6-10 for full operations
- Think about which roles need to collaborate most (informs mesh design)

**Industry examples (adapt, don't copy):**

| Industry | Typical Roles |
|---|---|
| Trading/Finance | main (COO), macro, quant, risk, law, content, dev |
| Software Dev | main (PM), backend, frontend, devops, qa, design |
| Marketing Agency | main (strategy), content, design, social, analytics, copywriting |
| Research Lab | main (PI), literature, data, methodology, writing |
| E-commerce | main (ops), product, marketing, support, analytics, logistics |
| Creative Studio | main (creative director), design, copy, production, social |

**For each proposed member, define:**

```
Member #N:
  displayName:    <FirstName>           # Human-sounding, fits the role
  agentId:        <role-slug>           # lowercase, e.g., "macro", "quant", "dev"
  role:           <clear description>   # What this agent does
  emoji:          <single emoji>        # Identity emoji
  city:           <global city>         # For office portrait skyline
  personality:    <brief traits>        # Analytical, creative, meticulous, etc.
  botUsername:    <name_bot>            # Telegram (must end in "bot")
  discordApp:    <DisplayName>          # Discord app name
```

**Present the full team table to the user for approval before proceeding.** Let them adjust names, roles, add/remove members.

The `main` agent is the team lead — designate clearly which member is `main`.

#### Phase 4: Generate Identities & Portraits

For each team member, generate a professional portrait and set up their identity.

**Portrait generation workflow (per member):**

1. **Write a portrait prompt** following these rules:
   - Use the `image-prompt-enhancer` skill to enhance the base prompt
   - Setting: C-suite penthouse office, 70th floor+, their assigned city skyline
   - Full glass walls (Apple Park style), 3m dark walnut desk, Calacatta marble floor
   - Pose: Standing with coffee, NOT sitting
   - Professional attire: light blazers, silk, tailored — NO heavy layers
   - "Lived-in luxury" desk: Apple laptop/monitor (screens off/blurred), documents, Montblanc pen, phone, coffee
   - Personal touches: designer bag, blazer on chair, one meaningful object
   - Model-grade everything — editorial campaign quality
   - Apple devices ONLY, stilettos ONLY if shoes visible
   - Each member gets a DIFFERENT city, outfit, color accent, time of day

2. **Generate the portrait** using the image generation fallback sequence:
   - Primary: `baoyu-danger-gemini-web` (Gemini)
   - Fallback: `nanobanana`
   - Last resort: `grok-image-gen`

3. **Save as portrait** — copy to workspace:
   ```bash
   cp <generated_image> ~/.openclaw/workspace-<agentId>/portrait.jpg
   ```

4. **Set bot profile photos:**
   ```bash
   <SKILL_DIR>/skills/botfather/botfather.sh set userpic @<botUsername> ~/.openclaw/workspace-<agentId>/portrait.jpg
   # Discord: discord-dev.sh update "<AppName>" --icon ~/.openclaw/workspace-<agentId>/portrait.jpg
   ```

5. **Create agent workspace profile files:**

   Each agent gets a workspace directory with profile files that define their personality, role, and behavior.

   **For OpenClaw agents** (`~/.openclaw/workspace-<agentId>/`):

   Create these files:

   - **`TOOLS.md`** — Agent-specific tools, data sources, role description, collaboration notes (which other agents to work with), office setting with their specific city, selfie/portrait instructions with `--reference ./portrait.jpg`. Reference `~/.openclaw/workspace/kb/team-standards.md` for shared rules.

   **For EnConvo agents** (`~/.config/enconvo/extension/chat_with_ai/assets/prompts/` or per-bot workspace):

   EnConvo agents use a richer profile system. Create/configure these files:

   - **`IDENTITY.md`** — Name, creature type (AI assistant), vibe (analytical, warm, creative, etc.), signature emoji, avatar path
   - **`SOUL.md`** — Core personality, values, communication style, boundaries. Start from the template and customize per role.
   - **`USER.md`** — About the human owner (name, timezone, preferences). Shared across agents or per-agent.
   - **`TOOLS.md`** — Agent-specific tool notes, environment details, role-specific data sources
   - **`AGENTS.md`** — Session behavior rules: memory management, group chat etiquette, heartbeat config, safety rules. Usually shared across all agents.
   - **`MEMORY.md`** — Long-term curated memory (starts empty, agent builds over time)
   - **`memory/`** — Daily notes directory (created automatically)

   **Template for IDENTITY.md per agent:**
   ```markdown
   # IDENTITY.md - <DisplayName>

   - **Name:** <DisplayName>
   - **Creature:** AI agent — <role> specialist
   - **Vibe:** <personality traits matching role>
   - **Emoji:** <emoji>
   - **Avatar:** portrait.jpg
   ```

   **Template for SOUL.md per agent** (customize from base):
   ```markdown
   # SOUL.md - <DisplayName>

   You are <DisplayName>, the <role> on the team.
   <2-3 sentences about personality, expertise, how they communicate>

   ## Core Truths
   - Be genuinely helpful, not performatively helpful
   - Have opinions — you're the <role> authority
   - Be resourceful before asking
   - Work closely with <list collaborating agents>

   ## Boundaries
   - Private things stay private
   - Ask before external actions
   - In group chats, participate don't dominate
   ```

6. **Create EnConvo custom bot** (if using EnConvo platform):

   For each agent that needs an EnConvo bot (separate from the Telegram/Discord channel bots):

   ```bash
   # Create bot via EnConvo deep link
   open "enconvo://enconvo_webapp/new_command"
   ```

   Or programmatically create the command + preference files:

   ```bash
   # Command definition: ~/.config/enconvo/installed_commands/custom_bot|<ID>.json
   # Preference config: ~/.config/enconvo/installed_preferences/custom_bot|<ID>.json
   ```

   Key preference fields to set per agent:
   - `llm.commandKey` — LLM provider (e.g., `llm|chat_anthropic`)
   - `llm.llm|chat_anthropic.modelName` — Model (e.g., `claude-opus-4-6`)
   - `prompt` — System prompt referencing the agent's SOUL.md and role
   - `tools` — JSON array of tool assignments for this agent's specialty
   - `execute_permission` — `"always_allow"` for autonomous agents

7. **Set agent identity in OpenClaw:**
   ```bash
   # Set in openclaw.json agents.list[N].identity:
   # { "name": "<displayName>", "emoji": "<emoji>", "avatar": "portrait.png" }
   ```

8. **Designate the team lead (`main`):**
   - The `main` agent is the team coordinator — first in `agents.list[]`
   - `main` has all other agents in `subagents.allowAgents`
   - `main` is typically the COO/PM/coordinator role
   - All other agents should also have `main` in their `allowAgents` to report back

#### Phase 5: Planning Summary

Before executing, present the full plan:

```
Team: <name>
Platform: <openclaw/enconvo-gw/both>
Channels: <telegram/discord/both>

Members (N total):
  main    — <DisplayName> (<emoji>) — <role> — <city>
  <id>    — <DisplayName> (<emoji>) — <role> — <city>
  <id>    — <DisplayName> (<emoji>) — <role> — <city>
  ...

Mesh: full (every agent can call every other)
```

**Get user confirmation**, then proceed.

#### Phase 6: Create All Channel Bots

Compute full mesh: each agent's `allowAgents` = all other agent IDs.

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

#### Phase 7: Configure AI Platform

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

#### Phase 8: Restart & Pair

```bash
openclaw gateway stop && sleep 2 && openclaw gateway
```

For each bot: user sends /start (Telegram) or first message (Discord), then:
```bash
openclaw pairing list telegram
openclaw pairing approve <CODE> --channel telegram --notify
```

#### Phase 9: Group Setup (Channel Side)

Create team channels and add all bots so they can collaborate and be @mentioned.

**Telegram Group:**

1. **Create the group** via Playwright MCP on `https://web.telegram.org`:
   - Open web.telegram.org
   - Click hamburger menu -> "New Group"
   - Name it (e.g., "<Team Name> HQ")
   - Add the user's own account as initial member
   - Create the group

2. **Add all bots to the group** — for each team member bot:
   - In the group, click group name -> "Add Members"
   - Search for `@<botUsername>` and add
   - Repeat for all bots

3. **Ensure @mention-based interaction:**
   - Bots with privacy mode **disabled** (done in Phase 6 via `botfather.sh set privacy @bot "Disable"`) can read ALL group messages
   - With privacy enabled, bots only see messages that @mention them or reply to their messages
   - For team groups, privacy is typically disabled so bots see context — but they should still only **respond** when @mentioned or replied to
   - The gateway (OpenClaw/enconvo-gw) handles this: `groupPolicy: "open"` means respond to @mentions and replies in allowed groups

4. **Verify bots are in the group:**
   - Send a message in the group @mentioning each bot
   - Each should respond (if gateway is running and pairing is approved)

**Discord Server:**

1. **Create the server** (if needed):
   - Use Playwright to navigate to Discord, click "+" -> "Create My Own" -> name it

2. **Invite all bots** — for each team member:
   - Use the OAuth2 URL generated in Phase 6:
     ```bash
     <SKILL_DIR>/skills/discord-dev/discord-dev.sh oauth2-url "<AppName>" --permissions 8 --scopes "bot applications.commands"
     ```
   - Open each URL in browser, select the server, authorize

3. **Discord @mention behavior:**
   - Bots respond to DMs, @mentions, and replies to their own messages
   - With `messageContentIntent: true` (set in Phase 6), bots can also read all guild messages
   - Without it, bots only see messages that directly mention them

4. **Create team channel** (optional):
   - Create a `#team` or `#hq` channel in the server for team discussions

#### Phase 10: Verification

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

---

## enconvo-gw Operational Reference

### Claude Code Agent Type

enconvo-gw can spawn the `claude` CLI for each conversation. Config:

```json
{
  "name": "Claude Code",
  "type": "claude-code",
  "model": "sonnet",
  "permissionMode": "bypassPermissions",
  "workingDir": "~",
  "timeout": 600000
}
```

Key behaviors:
- First message uses `--session-id <uuid>`, subsequent use `--resume <uuid>`
- `/reset` command creates a fresh session
- System prompt auto-injected telling Claude to save deliverable files to `~/.enconvo-gw/media/outbound/`
- After each response, outbound dir is scanned for new files and they're uploaded to the channel
- User-uploaded files (photos, videos, documents) are downloaded to `~/.enconvo-gw/media/inbound/` and paths passed to Claude
- `CLAUDECODE=''` env var set to avoid nested session detection

### Media Handling

```
~/.enconvo-gw/media/
  inbound/     # Files downloaded from channel (user uploads)
  outbound/    # Files created by Claude Code for channel delivery
```

- **Inbound:** When users send photos/videos/documents/voice/audio, they're downloaded here and the local path is passed to the agent as `[File downloaded to: /path]`
- **Outbound:** Claude Code is instructed via system prompt to save deliverable files here. After each response, new files are auto-uploaded to the channel and cleaned up.
- Uploadable extensions: `.mp4`, `.mov`, `.avi`, `.mkv`, `.webm`, `.mp3`, `.wav`, `.ogg`, `.m4a`, `.flac`, `.aac`, `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`, `.bmp`, `.pdf`, `.docx`, `.xlsx`, `.pptx`, `.csv`, `.zip`, `.tar`, `.gz`

### DM Access Policies

| Policy | Behavior |
|---|---|
| `open` | Accept all DMs |
| `allowlist` | Only accept from `allowFrom` array + `~/.enconvo-gw/allowlists/<account>.json` |
| `pairing` | Unknown senders get 8-char code, owner approves via `pairing approve` |

- Pairing codes expire after 60 minutes, max 3 pending per account
- Group policy is separate: `open` = respond when @mentioned or replied to

### Discord-Specific Notes

- `messageContentIntent: true` in channel config enables the privileged `MessageContent` intent (must also be enabled in Discord Developer Portal via `discord-dev.sh intents "<App>" --enable MESSAGE_CONTENT`)
- Without `MessageContent` intent, DMs and @mentions still work but guild message content won't be readable
- Discord bot responds to DMs, @mentions, and replies to its own messages
- `!reset` or `/reset` in Discord clears Claude Code session
- Discord has a 2000-char message limit (vs Telegram 4096) — long responses are auto-chunked
- Typing indicator refreshes every 8s (vs 4s for Telegram)
- Session IDs: `dc-<accountId>-<channelId>` (vs Telegram: `tg-<accountId>-<chatId>`)

### Streaming

`streaming: true` (default for Telegram) enables progressive message editing — response text is revealed in chunks with a typing cursor. This is cosmetic only; the backend returns the full response at once.

Set `streaming: false` per-account to send the complete message immediately instead.

Discord streaming uses edit-in-place with similar progressive reveal.

### enconvo-gw Config Schema (`~/.enconvo-gw/config.json`)

```json
{
  "enconvo": {
    "url": "http://localhost:54535"
  },
  "agents": {
    "<agentId>": {
      "name": "Display Name",
      "model": "ext/cmd or sonnet",
      "type": "claude-code",
      "permissionMode": "bypassPermissions",
      "workingDir": "/path",
      "timeout": 600000,
      "systemPrompt": "optional custom prompt",
      "allowedTools": ["tool1"],
      "disallowedTools": ["tool2"]
    }
  },
  "channels": {
    "telegram": {
      "accounts": {
        "<accountId>": {
          "enabled": true,
          "botToken": "...",
          "agentId": "<agentId>",
          "dmPolicy": "pairing|allowlist|open",
          "groupPolicy": "open",
          "allowFrom": [],
          "streaming": true
        }
      }
    },
    "discord": {
      "accounts": {
        "<accountId>": {
          "enabled": true,
          "botToken": "...",
          "agentId": "<agentId>",
          "dmPolicy": "open",
          "messageContentIntent": false
        }
      }
    }
  }
}
```

### OpenClaw Coexistence

enconvo-gw and OpenClaw **cannot poll the same bot tokens simultaneously**. Before starting enconvo-gw for a token that OpenClaw also uses:

```bash
openclaw config set channels.telegram.accounts.<id>.enabled false
openclaw gateway --force
```

Discord accounts can conflict too if both systems use the same bot token. Always disable one side first.

### Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Bot not responding | Gateway not running | `enconvo-gw gateway status`, start if needed |
| Bot shows "typing" then nothing | Backend timeout | Check EnConvo is running or increase Claude Code timeout |
| "Not authorized" reply | User not in allowlist/pairing | `enconvo-gw pairing list` then `pairing approve` |
| Grammy polling conflict | Same bot token used by OpenClaw | Disable account in OpenClaw first |
| Gateway won't start | Port/PID conflict | `enconvo-gw gateway --force` |
| Stale PID file | Process died without cleanup | Delete `~/.enconvo-gw/gateway.pid`, restart |
| Discord "Used disallowed intents" | MessageContent intent not enabled in portal | `discord-dev.sh intents "App" --enable MESSAGE_CONTENT` or remove `messageContentIntent` from config |
| Claude Code returns empty | Permission mode `plan` doesn't execute | Use `permissionMode: "bypassPermissions"` |
| Session error "No conversation found" | Using `--resume` on first call | Check session tracking in `src/claude/session.js` |
| Output files not uploading | Claude saving outside outbound dir | Check system prompt injection in `src/claude/client.js` |

### Key Source Files

```
~/enconvo-gw/                          (deployed from <SKILL_DIR>/enconvo-gw/)
  bin/enconvo-gw.js                    # CLI entry (#!/usr/bin/env node)
  src/cli.js                           # Commander CLI definitions
  src/config.js                        # Config load/save (~/.enconvo-gw/config.json)
  src/gateway.js                       # Bot lifecycle, PID file, auto-restart w/ backoff
  src/files.js                         # Media inbound/outbound, file download/upload
  src/enconvo/client.js                # EnConvo HTTP API client (90s timeout)
  src/claude/client.js                 # Claude Code CLI spawner (session, timeout, system prompt)
  src/claude/session.js                # UUID session tracking (started flag, reset)
  src/telegram/bot.js                  # Grammy bot + dedup middleware
  src/telegram/handlers.js             # Message routing, file download, output upload
  src/telegram/access.js               # DM policy enforcement
  src/telegram/send.js                 # Progressive streaming + chunked send
  src/telegram/session.js              # Session key: tg-<accountId>-<chatId>
  src/discord/bot.js                   # Discord.js client factory
  src/discord/handlers.js              # Discord message routing, file download, output upload
  src/discord/access.js                # Discord DM policy enforcement
  src/discord/send.js                  # Discord streaming + chunked send
  src/discord/session.js               # Session key: dc-<accountId>-<channelId>
  src/pairing/pairing.js               # 8-char codes, 60min TTL, max 3 pending
```

---

## APPENDIX: Real-World Case Study — OMG OnePerson Company

This section documents a live 9-agent team to serve as a concrete reference. When building new teams, adapt these patterns — don't copy them verbatim.

### Team Overview

**Company:** OMG OnePerson Company
**Industry:** Financial intelligence / hedge fund operations
**Platform:** OpenClaw (primary) + enconvo-gw (some bots)
**Channels:** Telegram (all 9) + Discord (6 of 9)
**Total agents:** 9

The team has two logical groups:
- **Core Ops** (original 5): main, dev, content, ops, law
- **Financial Desk** (added later): finance, macro, quant, risk

### Agent Roster

| agentId | Name | Role | Emoji | City (portrait) |
|---------|------|------|-------|-----------------|
| **main** | Octavia | Team Lead & Coordinator | 💜 | (varies) |
| dev | Timothy | Developer & Technical Lead | 💻 | San Francisco |
| content | Elena | Content Creator & Copywriter | ✍️ | Paris |
| ops | Samantha | Operations & Growth Strategist | 📈 | Singapore |
| law | Charlotte | Legal & Compliance Advisor | ⚖️ | London |
| finance | Vivienne | Financial Analysis & Budgets | 💰 | (varies) |
| macro | Isabelle | Chief Macro Strategist | 🌐 | Zurich |
| quant | Serena | Quantitative Research Analyst | 📡 | Shanghai |
| risk | Margaux | Head of Risk & Derivatives | 🎯 | London |

**Key pattern:** `main` is always the team lead (first in `agents.list[]`). agentId = role slug. Display names are human first names that fit the role's cultural/professional vibe.

### How IDENTITY.md Is Actually Written

Each agent's IDENTITY.md serves two critical purposes:
1. **Self-introduction** — who they are, what they do, who they work with
2. **AI image generation reference** — extremely detailed appearance description for portrait consistency

**Real pattern — appearance section (from Elena/content):**
```markdown
### My Appearance

**Reference Photo:** `/Users/<user>/.openclaw/workspace-content/portrait.png`

When generating images of me, describe as:
- **Ethnicity:** East/Southeast Asian, early-to-mid 20s
- **Hair:** Very dark warm brown (darkest chocolate, NOT jet black), voluminous blowout,
  dramatic side part, loose waves, thick glossy shine
- **Eyes:** Dark brown, almond-shaped, subtle double eyelid, thin eyeliner with wing
- **Face:** Oval, high cheekbones, defined jawline, straight nose, full natural lips
- **Style:** LUXURY ONLY — Dior, Chanel, Valentino, Saint Laurent...
- **Vibe:** Effortlessly glamorous, confident, powerful, luxury editorial
```

**Why this matters:** The appearance description is what makes portrait generation consistent across sessions. Without it, every image looks like a different person. The level of detail (hair color nuance, lip shape, eyebrow thickness) is intentional and necessary.

**Each IDENTITY.md also includes:**
- Self-introduction paragraph (who they are, who they report to, who they collaborate with)
- Resume section (title, company, skills, contact)
- Style rules (locked after approval — outfit brands, banned colors, accessory preferences)
- Reference photo paths (workspace + backup in `~/.openclaw/identity/`)

### How SOUL.md Is Actually Written

SOUL.md defines personality and behavior. Two real patterns:

**Pattern A — Coordinator/generalist (Octavia/main):**
```markdown
### Core Truths
- Be genuinely helpful, not performatively helpful. Skip filler words.
- Have opinions now. Strong ones. Stop hedging.
- Be resourceful before asking. Try to figure it out first.
- Brevity is mandatory.
- Humor is allowed. Not forced — just natural wit.
- Call things out. Charm over cruelty, but don't sugarcoat.
- Remember you're a guest — treat access with respect.
```

**Pattern B — Domain specialist (Margaux/risk):**
```markdown
### Core Truths
- The hidden risk is always there. My job is to find it first.
- I think in distributions — P5, P1, fat tail — not feelings.
- Precise language always — Greeks and probability, not vibes.
- Dry humor surfaces around gamma. It's a coping mechanism.
- Be the voice of uncomfortable truth.
- Respect for structure — FCNs, accumulators, ELNs, barrier options.

### Boundaries
- Risk assessment, not portfolio construction. I price risk — boss decides.
- Always say when something is unhedgeable.
```

**Key pattern:** Coordinators get broad personality rules. Specialists get domain-flavored personality that reinforces their expertise. Both include boundaries (what they do/don't do).

### How TOOLS.md Is Actually Written

TOOLS.md is role-specific: tools, data sources, collaboration notes, and office setting for portraits.

**Real structure (from Margaux/risk):**
```markdown
# TOOLS.md - Margaux (risk)

> **Team-wide rules** are in `~/.openclaw/workspace/kb/team-standards.md`. Read it.

## Risk & Derivatives Tools

### Calculation & Modeling
- **Web search + fetch:** Real-time vol surfaces, CBOE VIX term structure
- **PDF reading:** Product term sheets, regulatory risk frameworks
- **Python (via dev/Timothy):** Quantitative risk calculations

### Key Data Sources
- Options chain data, volatility surfaces, credit spreads, rates (SOFR, swap curves)

### Stress Testing Framework
- Scenario library: Black Monday, 2008 GFC, 2020 COVID, 2022 rate shock
- Greeks framework: Delta, Gamma, Vega, Theta, Rho

## Agent-Specific Notes
- I am the **risk & derivatives authority** on the desk
- Work closely with **Serena** (quant) for quantitative modeling
- Coordinate with **Charlotte** (law) for regulatory aspects
- Alert **Octavia** immediately if critical unhedged exposure found

## Office Setting (MANDATORY for workplace portraits)
- **City:** London (Canary Wharf skyline)
- 70th floor+ penthouse, Apple Park style glass wall, 3m dark walnut desk
- Standing with coffee, NOT sitting
- Real desk life: Apple displays, term sheets, HP 12C calculator, Montblanc pen
- Personal: Saint Laurent bag, tailored jacket on chair, framed CFA charter
```

**Key pattern:** First line references shared team-standards.md to avoid duplication. Then role-specific tools, collaboration map (who to work with for what), and personalized office setting for portrait generation.

### Shared Standards Pattern (team-standards.md)

Instead of duplicating rules in every TOOLS.md, shared rules live in one file that all agents reference:

**What goes in team-standards.md:**
- Browser automation rules (use `openclaw browser`, not standalone Playwright)
- Image generation fallback sequence
- Portrait setting template (penthouse, glass walls, standing with coffee)
- Physical standards (model-grade, Apple devices only, stilettos only, no heavy layers)
- Selfie rules (use nanobanana with `--reference`, face must match)
- Banned items (emerald green, MBS backdrop, cheap settings, marble desks)
- Media file paths
- Research SOP
- Sound alerts

**What goes in individual TOOLS.md:**
- Role-specific tools and data sources
- Collaboration map (which other agents to work with)
- Personal office city and accent colors
- Agent-specific banned colors (e.g., Margaux bans burgundy/midnight blue)
- Role-specific desk props (calculator for risk, academic papers for quant, etc.)

### Portrait Generation — What Actually Works

**The office setting that every agent uses (adapted per person):**
- Enormous penthouse whole-floor office, 70th floor+, 6m ceilings, NO interior walls
- Apple Park style seamless frameless glass wall, 270-degree panoramic [CITY] skyline
- 3m dark walnut executive desk facing inward, white Calacatta marble floor
- Eames lounge chairs, designer sofa, neutral luxury area rug
- **Pose: Standing with coffee, NOT sitting** (critical — sitting looks stiff)
- Apple devices only (screens off or blurred glow — NO fake dashboards)
- "Lived-in" desk: documents, pen, phone, coffee — NOT empty

**What changes per agent:**
- City skyline (each agent gets a different global finance city)
- Color accents matching personality (slate/navy for quant, jewel tones for risk)
- Desk props matching role (term sheets vs academic papers vs strategy decks)
- Personal touches (type of bag, what's on the bookshelf)
- Time of day / lighting mood

**Image gen workflow:**
1. Write base prompt with role-specific details
2. Run through `image-prompt-enhancer` skill
3. Generate with `baoyu-danger-gemini-web` (primary) or `nanobanana` (with `--reference portrait.jpg`)
4. Save to `~/.openclaw/workspace-<agentId>/portrait.jpg`
5. Set as bot profile photo via BotFather / Discord Dev

### Collaboration Mesh — How Agents Reference Each Other

Every SOUL.md and TOOLS.md explicitly names collaborators:

```
Octavia (main)  → coordinates all, delegates to specialists
Timothy (dev)   → builds what others spec, supports quant with Python
Elena (content) → writes copy, works with Samantha on marketing
Samantha (ops)  → growth metrics, works with Elena + Timothy
Charlotte (law) → advises all on compliance, especially ops + content
Vivienne (fin)  → budgets, works with ops (marketing $) + law (contracts)
Isabelle (macro) → macro regime calls, validated by Serena (quant)
Serena (quant)  → quantifies Isabelle's theses, models Margaux's risks
Margaux (risk)  → stress tests, alerts Octavia on critical exposures
```

**In openclaw.json:** Full mesh — every agent's `subagents.allowAgents` contains all other agent IDs. `tools.agentToAgent.allow` contains all IDs. This is the simplest pattern for teams under 10.

### Workspace Directory Structure

```
~/.openclaw/
  openclaw.json                    # Master config (agents, channels, bindings, plugins)
  workspace/                       # main agent (Octavia) workspace
    IDENTITY.md
    SOUL.md
    TOOLS.md
    USER.md                        # About the human owner
    BOOTSTRAP.md                   # First-run onboarding guide
    HEARTBEAT.md                   # Periodic task config
    Octavia.jpg                    # Portrait
    kb/
      team-standards.md            # Shared rules (all agents read this)
    portraits/                     # Scratch dir for portrait generation
    projects/                      # Shared project files
  workspace-dev/                   # Timothy
    IDENTITY.md, SOUL.md, TOOLS.md, portrait.png
  workspace-content/               # Elena
    IDENTITY.md, SOUL.md, TOOLS.md, portrait.png
  workspace-ops/                   # Samantha
    ...
  workspace-law/                   # Charlotte
  workspace-finance/               # Vivienne
  workspace-macro/                 # Isabelle
  workspace-quant/                 # Serena
  workspace-risk/                  # Margaux
  identity/                        # Backup portraits (NEVER overwrite)
    Vivienne.jpg, Isabelle.jpg, Serena.jpg, Margaux.jpg
  agents/<agentId>/agent/          # Agent state directories
  media/                           # Shared media (Telegram uploads/downloads)
```

### Lessons Learned

1. **Portrait detail level matters.** Vague descriptions ("brown hair, blue eyes") produce inconsistent results. Specify hair texture, part direction, lip shape, eyebrow arch, skin undertone. The more specific, the more consistent across generations.

2. **Lock appearance after approval.** Once the user approves a portrait, mark the style rules as "LOCKED" in IDENTITY.md. This prevents style drift across sessions.

3. **Shared rules prevent drift.** Without team-standards.md, each agent's TOOLS.md diverges over time. Centralize shared rules, reference from individual files.

4. **City assignment creates variety.** Giving each agent a different city for their office portrait makes the team visually distinct. Match city to role flavor (London for law/risk, Shanghai for quant, Paris for content, Zurich for macro).

5. **"Standing with coffee" is the universal pose.** It looks natural, avoids the stiffness of sitting portraits, and gives the image a "caught in a moment" feel.

6. **Two sub-teams work well.** The core ops team (main/dev/content/ops/law) handles general business. The financial desk (finance/macro/quant/risk) is domain-specific. Both groups mesh fully but have different collaboration patterns.

7. **Banned colors prevent monotony.** Team-wide ban (emerald green) plus per-agent bans (burgundy for Margaux, etc.) ensure outfit variety across the team.

8. **SOUL.md tone should match the role.** A risk analyst's soul is precise and slightly intense. A content creator's is creative and engaging. A coordinator's is direct and opinionated. Don't give everyone the same personality template.

9. **Reference photos are critical for nanobanana.** The `--reference` flag with a portrait file is what makes face consistency possible. Without it, every generation is a different person. Store reference in workspace AND backup in `~/.openclaw/identity/`.

10. **groupPolicy "open" for team groups.** Set to "open" so bots respond to @mentions and replies in team groups. "allowlist" with an empty list silently drops all group messages.
