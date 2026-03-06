---
name: enconvo-gw-skill
description: "Manage the enconvo-gw gateway — start/stop/status, add/remove Telegram & Discord bots, approve pairing requests, configure agents (EnConvo + Claude Code), manage bot settings via BotFather & Discord Developer Portal, and troubleshoot the messaging bridge."
version: 2.0.0
author: zanearcher
category: tools
---

# enconvo-gw Skill

Manage the **enconvo-gw** gateway — a standalone bridge that routes Telegram and Discord messages to EnConvo or Claude Code backends. Includes built-in BotFather and Discord Developer Portal management.

**Trigger on:** "enconvo-gw", "enconvo gateway", "enconvo telegram", "enconvo discord", "enconvo bot", "enconvo pairing", "approve pairing", "enconvo-gw start", "enconvo-gw stop", "botfather", "telegram bot settings", "create telegram bot", "bot name", "bot description", "bot commands", "bot token", "set bot", "delete bot", "discord developer", "discord bot settings", "create discord bot", "discord app", "discord application", "discord token", "discord intents", "discord commands", "discord oauth"

---

## Architecture

```
Telegram Bot API ←→ enconvo-gw (Grammy, long-polling) ←→ EnConvo API (localhost:54535)
Discord Gateway  ←→ enconvo-gw (discord.js)           ←→ Claude Code CLI (claude -p)
                         ↕
                   ~/.enconvo-gw/config.json    (config)
                   ~/.enconvo-gw/pairing/       (pending codes)
                   ~/.enconvo-gw/allowlists/    (approved senders)
                   ~/.enconvo-gw/media/inbound/  (user-uploaded files)
                   ~/.enconvo-gw/media/outbound/ (deliverable files for channel upload)
```

- **Source code:** `~/enconvo-gw/` (Node.js ESM, npm-linked globally)
- **Config + data:** `~/.enconvo-gw/`
- **CLI binary:** `/opt/homebrew/bin/enconvo-gw` -> symlink to `~/enconvo-gw/bin/enconvo-gw.js`
- **Dependencies:** `grammy` + `discord.js` + `commander`
- **Logs:** `/tmp/enconvo-gw.log`
- **PID file:** `~/.enconvo-gw/gateway.pid`

---

## Quick Reference

| Want to... | Command |
|---|---|
| Check if gateway is running | `enconvo-gw gateway status` |
| Start gateway (foreground) | `enconvo-gw gateway` |
| Start gateway (background) | `cd ~/enconvo-gw && nohup node bin/enconvo-gw.js gateway > /tmp/enconvo-gw.log 2>&1 &` |
| Start + kill existing | `enconvo-gw gateway --force` |
| Stop gateway | `enconvo-gw gateway stop` |
| List configured bots | `enconvo-gw channels list` |
| Probe live connections | `enconvo-gw channels status` |
| List agents | `enconvo-gw agents list` |
| Show pending pairing | `enconvo-gw pairing list` |
| Approve a user | `enconvo-gw pairing approve telegram <CODE>` |
| Read config value | `enconvo-gw config get <dot.path>` |
| Set config value | `enconvo-gw config set <dot.path> <value>` |
| View live logs | `tail -f /tmp/enconvo-gw.log` |

---

## CLI Commands — Full Reference

### Gateway

```bash
enconvo-gw gateway [--force]       # Start gateway (foreground). --force kills existing first
enconvo-gw gateway stop            # Send SIGTERM to running gateway
enconvo-gw gateway status          # Show PID / running status
```

### Channels

```bash
enconvo-gw channels list           # List all accounts + agent mapping + dm policy
enconvo-gw channels status         # Probe each bot token against Telegram API
enconvo-gw channels add \
  --channel telegram|discord \
  --account <id> \
  --token <bot-token> \
  --agent <agentId> \
  [--dm-policy pairing|allowlist|open] \
  [--group-policy open]
enconvo-gw channels remove --channel telegram|discord --account <id>
```

### Agents

```bash
enconvo-gw agents list             # List configured agents
enconvo-gw agents add --id <id> --name <name> --model <ext/cmd> \
  [--type claude-code] \
  [--system-prompt "..."] \
  [--permission-mode bypassPermissions|plan] \
  [--allowed-tools tool1,tool2] \
  [--working-dir /path] \
  [--timeout 600000]
enconvo-gw agents remove --id <id>
```

### Pairing

```bash
enconvo-gw pairing list [channel]              # Show pending pairing requests
enconvo-gw pairing approve <channel> <code>    # Approve a sender by code
```

### Config

```bash
enconvo-gw config get <dot.path>    # e.g., enconvo.url, channels.telegram.accounts.enconvo-bot
enconvo-gw config set <dot.path> <value>
```

---

## Agent Types

### EnConvo Agent (default)

Routes messages to EnConvo's local API. Config:

```json
{
  "name": "My Agent",
  "model": "ext/cmd_id"
}
```

### Claude Code Agent

Spawns the `claude` CLI for each message. Supports multi-turn conversations via session IDs. Config:

```json
{
  "name": "Claude Code",
  "type": "claude-code",
  "model": "sonnet",
  "permissionMode": "bypassPermissions",
  "workingDir": "/Users/youruser",
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

---

## Media Handling

```
~/.enconvo-gw/media/
  inbound/     # Files downloaded from channel (user uploads)
  outbound/    # Files created by Claude Code for channel delivery
```

- **Inbound:** When users send photos/videos/documents/voice/audio, they're downloaded here and the local path is passed to the agent as `[File downloaded to: /path]`
- **Outbound:** Claude Code is instructed via system prompt to save deliverable files here. After each response, new files are auto-uploaded to the channel and cleaned up.
- Uploadable extensions: `.mp4`, `.mov`, `.avi`, `.mkv`, `.webm`, `.mp3`, `.wav`, `.ogg`, `.m4a`, `.flac`, `.aac`, `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`, `.bmp`, `.pdf`, `.docx`, `.xlsx`, `.pptx`, `.csv`, `.zip`, `.tar`, `.gz`

---

## DM Access Policies

| Policy | Behavior |
|---|---|
| `open` | Accept all DMs |
| `allowlist` | Only accept from `allowFrom` array + `~/.enconvo-gw/allowlists/<account>.json` |
| `pairing` | Unknown senders get 8-char code, owner approves via `pairing approve` |

- Pairing codes expire after 60 minutes, max 3 pending per account
- Group policy is separate: `open` = respond when @mentioned or replied to

---

## Discord-Specific Notes

- `messageContentIntent: true` in channel config enables the privileged `MessageContent` intent (must also be enabled in Discord Developer Portal)
- Without `MessageContent` intent, DMs and @mentions still work but guild message content won't be readable
- Discord bot responds to DMs, @mentions, and replies to its own messages
- `!reset` or `/reset` in Discord clears Claude Code session

---

## Config Schema (`~/.enconvo-gw/config.json`)

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

---

## Streaming

`streaming: true` (default) enables progressive message editing — response text is revealed in chunks with a typing cursor. This is cosmetic only; the backend returns the full response at once.

Set `streaming: false` per-account to send the complete message immediately instead.

---

## Telegram BotFather Management

Manage Telegram bots via @BotFather programmatically using Telethon.

### BotFather Setup

Two options:

**Option 1: Browser Automation (Playwright)**
1. Navigate to `https://my.telegram.org/auth` via Playwright
2. User logs in, AI scrapes API credentials from "API development tools" page
3. Save credentials: `~/.claude/skills/botfather/scripts/botfather.sh save-creds --api-id <ID> --api-hash <HASH> --skip-auth`
4. Run Telethon auth (interactive terminal): `~/.claude/skills/botfather/scripts/botfather.sh auth`

**Option 2: Manual**
```bash
~/.claude/skills/botfather/scripts/botfather.sh setup
```

### BotFather Quick Reference

| Want to... | Command |
|---|---|
| Check auth status | `botfather.sh status` |
| List all bots | `botfather.sh list` |
| Create a bot | `botfather.sh create "Display Name" "username_bot"` |
| Delete a bot | `botfather.sh delete @mybot` |
| Set bot name | `botfather.sh set name @mybot "New Name"` |
| Set bot description | `botfather.sh set description @mybot "New description"` |
| Set bot about | `botfather.sh set about @mybot "About text"` |
| Set bot commands | `botfather.sh set commands @mybot "cmd1 - Desc 1\ncmd2 - Desc 2"` |
| Set bot photo | `botfather.sh set userpic @mybot /path/to/photo.jpg` |
| Toggle inline mode | `botfather.sh set inline @mybot "Enable"` or `"Disable"` |
| Toggle group joining | `botfather.sh set joingroups @mybot "Enable"` or `"Disable"` |
| Toggle privacy | `botfather.sh set privacy @mybot "Enable"` or `"Disable"` |
| Get bot token | `botfather.sh token @mybot` |
| Revoke bot token | `botfather.sh token @mybot --revoke` |
| Get bot info | `botfather.sh info @mybot` |
| Send raw command | `botfather.sh send "/mybots"` |

All commands support `--json`. Full path: `~/.claude/skills/botfather/scripts/botfather.sh`

### BotFather Files

```
~/.claude/skills/botfather/scripts/
  botfather.sh    # Shell wrapper (ensures venv + telethon)
  botfather.py    # Python CLI (Telethon + argparse)
~/.botfather/
  config.json     # api_id, api_hash
  session.session # Telethon session
  venv/           # Python venv with telethon
```

### BotFather Notes
- Telethon auth is always interactive (phone + 2FA code in terminal)
- Bot usernames should include `@` prefix
- For `/setcommands`, format as `"cmd1 - Description\ncmd2 - Description"`
- The `send` subcommand handles any raw BotFather command

---

## Discord Developer Portal Management

Manage Discord applications and bots via the Discord REST API.

### Discord Dev Setup

1. Obtain your Discord user token (see discord-dev skill docs for methods)
2. Save: `~/.claude/skills/discord-dev/scripts/discord-dev.sh save-token --token "<token>"`
3. Verify: `discord-dev.sh status`

### Discord Dev Quick Reference

| Want to... | Command |
|---|---|
| Check auth | `discord-dev.sh status` |
| List all apps | `discord-dev.sh list` |
| Create app + bot | `discord-dev.sh create "My App" --bot` |
| Create app only | `discord-dev.sh create "My App"` |
| Delete app | `discord-dev.sh delete "My App"` |
| Get app info | `discord-dev.sh info "My App"` |
| Set app name | `discord-dev.sh update "My App" --name "New Name"` |
| Set description | `discord-dev.sh update "My App" --description "About this bot"` |
| Set icon | `discord-dev.sh update "My App" --icon /path/to/icon.png` |
| Set public/private | `discord-dev.sh update "My App" --public false` |
| Add bot to app | `discord-dev.sh bot-add "My App"` |
| Reset bot token | `discord-dev.sh bot-reset "My App"` |
| List slash commands | `discord-dev.sh commands-list "My App"` |
| Set slash commands | `discord-dev.sh commands-set "My App" '[{"name":"ping","description":"Pong!"}]'` |
| Generate invite URL | `discord-dev.sh oauth2-url "My App" --permissions 8 --scopes "bot applications.commands"` |
| View intents | `discord-dev.sh intents "My App"` |
| Enable intents | `discord-dev.sh intents "My App" --enable MESSAGE_CONTENT GUILD_MEMBERS` |
| Disable intents | `discord-dev.sh intents "My App" --disable PRESENCE` |

Apps referenced by name or ID. All commands support `--json`. Full path: `~/.claude/skills/discord-dev/scripts/discord-dev.sh`

### Discord Dev Files

```
~/.claude/skills/discord-dev/scripts/
  discord-dev.sh    # Shell wrapper
  discord-dev.py    # Python CLI (stdlib only, no deps)
~/.discord-dev/
  config.json       # User token
```

### Discord Dev Notes
- No external dependencies — uses Python stdlib only
- Token is a Discord **user session token** (not a bot token), expires on password change
- `bot-add` and `bot-reset` return the bot token once — save immediately
- `commands-set` uses bulk overwrite — replaces ALL commands
- Slash command option types: 1=SUB_COMMAND, 3=STRING, 4=INTEGER, 5=BOOLEAN, 6=USER, 7=CHANNEL, 8=ROLE, 10=NUMBER

---

## Adding a New Bot — End-to-End

### Telegram Bot

1. Create bot via BotFather:
   ```bash
   botfather.sh create "My Agent" "my_agent_bot"
   ```
2. Get the token:
   ```bash
   botfather.sh token @my_agent_bot
   ```
3. Add agent:
   ```bash
   enconvo-gw agents add --id my-agent --name "My Agent" --model "ext/cmd" --type claude-code
   ```
4. Add channel:
   ```bash
   enconvo-gw channels add --channel telegram --account my-agent --token "BOT_TOKEN" --agent my-agent
   ```
5. Restart gateway:
   ```bash
   enconvo-gw gateway stop && enconvo-gw gateway
   ```

### Discord Bot

1. Create app + bot:
   ```bash
   discord-dev.sh create "My Agent" --bot
   ```
2. Save the bot token from output
3. Enable intents if needed:
   ```bash
   discord-dev.sh intents "My Agent" --enable MESSAGE_CONTENT
   ```
4. Generate invite URL:
   ```bash
   discord-dev.sh oauth2-url "My Agent" --permissions 8 --scopes "bot applications.commands"
   ```
5. Add channel:
   ```bash
   enconvo-gw channels add --channel discord --account my-agent-dc --token "BOT_TOKEN" --agent my-agent --dm-policy open
   ```
6. Restart gateway

---

## OpenClaw Coexistence

enconvo-gw and OpenClaw **cannot poll the same Telegram bot tokens simultaneously**. Before starting enconvo-gw:

```bash
openclaw config set channels.telegram.accounts.enconvo-bot.enabled false
openclaw gateway --force
```

Discord accounts can potentially conflict too if both systems use the same bot token.

---

## Troubleshooting

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

---

## Key Source Files

```
~/enconvo-gw/
├── bin/enconvo-gw.js           # CLI entry (#!/usr/bin/env node)
├── src/cli.js                  # Commander CLI definitions
├── src/config.js               # Config load/save (~/.enconvo-gw/config.json)
├── src/gateway.js              # Bot lifecycle, PID file, auto-restart w/ backoff
├── src/files.js                # Media inbound/outbound, file download/upload
├── src/enconvo/client.js       # EnConvo HTTP API client (90s timeout)
├── src/claude/client.js        # Claude Code CLI spawner (session, timeout, system prompt)
├── src/claude/session.js       # UUID session tracking (started flag, reset)
├── src/telegram/bot.js         # Grammy bot + dedup middleware
├── src/telegram/handlers.js    # Message routing, file download, output upload
├── src/telegram/access.js      # DM policy enforcement
├── src/telegram/send.js        # Progressive streaming + chunked send
├── src/telegram/session.js     # Session key: tg-<accountId>-<chatId>
├── src/discord/bot.js          # Discord.js client factory
├── src/discord/handlers.js     # Discord message routing, file download, output upload
├── src/discord/access.js       # Discord DM policy enforcement
├── src/discord/send.js         # Discord streaming + chunked send
├── src/discord/session.js      # Session key: dc-<accountId>-<channelId>
└── src/pairing/pairing.js      # 8-char codes, 60min TTL, max 3 pending
```
