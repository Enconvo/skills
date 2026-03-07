---
name: discord-dev
description: "Manage Discord applications/bots via Developer Portal API — create/delete apps, set name/description/icon, manage bot tokens, configure OAuth2, intents, slash commands."
version: 1.0.0
author: zanearcher
category: tools
---

# Discord Developer Portal Skill

Manage Discord applications and bots via the Discord REST API, with Playwright-assisted setup for token extraction.

**Trigger on:** "discord developer", "discord bot settings", "create discord bot", "discord app", "discord application", "discord token", "discord intents", "discord commands", "discord oauth"

---

## Setup — Playwright Token Extraction

The Discord API requires a user session token.

**Flow:**

1. Obtain your Discord user token from the Developer Portal or browser dev tools
2. Save the token:
   ```bash
   ~/.claude/skills/discord-dev/scripts/discord-dev.sh save-token --token "<your_token>"
   ```
3. Verify:
   ```bash
   ~/.claude/skills/discord-dev/scripts/discord-dev.sh status
   ```

**IMPORTANT:** The token is sensitive. It grants full access to the user's Discord account. Store securely.

---

## Quick Reference

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
| Set from file | `discord-dev.sh commands-set "My App" @commands.json` |
| Generate invite URL | `discord-dev.sh oauth2-url "My App" --permissions 8 --scopes "bot applications.commands"` |
| View intents | `discord-dev.sh intents "My App"` |
| Enable intents | `discord-dev.sh intents "My App" --enable MESSAGE_CONTENT GUILD_MEMBERS` |
| Disable intents | `discord-dev.sh intents "My App" --disable PRESENCE` |

Apps can be referenced by **name** or **ID**. All commands support `--json`.

**Full path:** `~/.claude/skills/discord-dev/scripts/discord-dev.sh`

---

## API-Powered Operations (no browser needed after setup)

All operations below use Discord REST API v10 with the saved user token:

### Application Management
- **List** — `GET /applications`
- **Create** — `POST /applications`
- **Update** — `PATCH /applications/{id}` (name, description, icon, public, code_grant)
- **Delete** — `DELETE /applications/{id}`
- **Info** — `GET /applications/{id}`

### Bot Management
- **Add bot user** — `POST /applications/{id}/bot`
- **Reset token** — `POST /applications/{id}/bot/reset`

### Slash Commands
- **List** — `GET /applications/{id}/commands`
- **Bulk set** — `PUT /applications/{id}/commands`

### Intents & Permissions
- View/toggle PRESENCE, GUILD_MEMBERS, MESSAGE_CONTENT via application flags
- Generate OAuth2 invite URLs with custom permissions and scopes

---

## Slash Commands JSON Format

```json
[
  {
    "name": "ping",
    "description": "Check bot latency",
    "type": 1
  },
  {
    "name": "echo",
    "description": "Echo a message",
    "type": 1,
    "options": [
      {
        "name": "text",
        "description": "Text to echo",
        "type": 3,
        "required": true
      }
    ]
  }
]
```

Option types: 1=SUB_COMMAND, 2=SUB_COMMAND_GROUP, 3=STRING, 4=INTEGER, 5=BOOLEAN, 6=USER, 7=CHANNEL, 8=ROLE, 10=NUMBER

---

## File Layout

```
~/.claude/skills/discord-dev/
  SKILL.md                      # This file
  scripts/
    discord-dev.sh              # Shell wrapper
    discord-dev.py              # Python CLI (stdlib only, no deps)

~/.discord-dev/
  config.json                   # User token
```

---

## Important Notes

- **No external dependencies** — uses only Python stdlib (urllib, json, base64). No venv needed.
- Token is a Discord **user session token**, not a bot token. It expires if the user changes password or Discord invalidates sessions.
- If token expires, re-run the Playwright setup flow to extract a fresh one.
- `bot-add` and `bot-reset` return the bot token once — save it immediately.
- App references work by name (case-insensitive) or by Discord snowflake ID.
- Slash command changes via `commands-set` use bulk overwrite — it replaces ALL commands.
- For guild-specific commands (testing), the API path would be `/applications/{id}/guilds/{guild_id}/commands` — use the raw API path if needed.
