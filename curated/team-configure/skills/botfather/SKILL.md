---
name: botfather
description: "Manage Telegram bots via @BotFather — create/delete bots, set name/description/about/commands/photo, toggle inline/groups/privacy, get/revoke tokens."
version: 1.1.0
author: zanearcher
category: tools
---

# BotFather Skill

Interact with Telegram's @BotFather programmatically via Telethon (user client API).

**Trigger on:** "botfather", "telegram bot settings", "create telegram bot", "bot name", "bot description", "bot commands", "bot token", "set bot", "delete bot"

---

## Setup — Two Options

When setup is needed, ask the user which option they prefer:

### Option 1: Browser Automation (Playwright) — Recommended

AI opens my.telegram.org in a browser, user only handles login. AI scrapes the API credentials automatically.

**Flow:**

1. Use Playwright MCP to navigate to `https://my.telegram.org/auth`
2. Take a snapshot so the user can see the login page
3. Tell the user: "Please enter your phone number in the browser and complete the login. Let me know when you're on the main page."
4. Wait for user confirmation, then take a snapshot to verify login succeeded
5. Click the **"API development tools"** link
6. Take a snapshot to check the page:
   - **If app already exists:** The page shows `api_id` and `api_hash` fields with values. Scrape them from the page.
   - **If no app exists:** Fill the "Create Application" form:
     - App title: `BotFather CLI`
     - Short name: `botfather_cli`
     - Platform: `Desktop`
     - Description: (leave empty)
     - Click "Create application"
     - Then scrape `api_id` and `api_hash` from the resulting page
7. Save credentials:
   ```bash
   ~/.claude/skills/botfather/scripts/botfather.sh save-creds --api-id <ID> --api-hash <HASH> --skip-auth
   ```
8. Run Telethon auth (interactive — needs terminal for phone + code):
   ```bash
   ~/.claude/skills/botfather/scripts/botfather.sh auth
   ```
9. Close the browser

**Key Playwright selectors for my.telegram.org:**

The site is simple HTML. Use snapshots to identify elements. Typical structure:
- Login page: phone input field, "Next" button, then code input
- Main page: links including "API development tools"
- API page: form with `api_id`, `api_hash` displayed (or create form if no app yet)

### Option 2: Manual (Step-by-Step Instructions)

User does everything themselves. Claude provides instructions.

```bash
~/.claude/skills/botfather/scripts/botfather.sh setup
```

This will:
1. Print instructions to visit https://my.telegram.org
2. Prompt for api_id and api_hash (user types them in)
3. Authenticate via Telethon (phone + code in terminal)

---

## Quick Reference

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

All commands support `--json` for machine-readable output.

**Full path:** `~/.claude/skills/botfather/scripts/botfather.sh`

---

## CLI Subcommands

```bash
botfather.sh setup                    # Interactive setup (manual option)
botfather.sh save-creds --api-id ID --api-hash HASH [--skip-auth]  # Save creds (Playwright option)
botfather.sh auth                     # Telethon auth only (after save-creds --skip-auth)
botfather.sh status                   # Check auth status
botfather.sh list                     # List all bots
botfather.sh create NAME USERNAME     # Create new bot
botfather.sh delete @bot              # Delete a bot
botfather.sh set SETTING @bot VALUE   # Change a setting
botfather.sh token @bot [--revoke]    # Get or revoke token
botfather.sh info @bot                # Get bot info
botfather.sh send "/command" [--follow-up TEXT] [--click] [--timeout N]
```

---

## How It Works

- Uses **Telethon** (Python Telegram user client) to send messages to @BotFather as the user
- Parses BotFather's text responses and inline keyboard buttons
- Clicks inline buttons to navigate BotFather's menu system
- Session persists at `~/.botfather/session.session` (no re-auth needed after first login)
- Python venv with Telethon auto-created at `~/.botfather/venv/` on first run

---

## File Layout

```
~/.claude/skills/botfather/
  SKILL.md                    # This file
  scripts/
    botfather.sh              # Shell wrapper (ensures venv + telethon)
    botfather.py              # Python CLI (Telethon + argparse)

~/.botfather/
  config.json                 # api_id, api_hash
  session.session             # Telethon session (auto-created)
  venv/                       # Python venv with telethon
```

---

## Important Notes

- **Telethon auth is always interactive** — needs terminal input for phone number + 2FA code. Cannot be automated.
- The Playwright option only automates getting API credentials from my.telegram.org — Telethon auth still needs terminal.
- BotFather responds with inline keyboards — the script clicks buttons by matching text.
- Bot usernames in commands should include the `@` prefix (e.g., `@mybot`).
- For `/setcommands`, format value as `"cmd1 - Description\ncmd2 - Description"`.
- Token output contains the bot token — treat as sensitive.
- The `send` subcommand can send any raw BotFather command for operations not covered by dedicated subcommands.
