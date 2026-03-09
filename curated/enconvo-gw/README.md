# enconvo-gw

A lightweight gateway that bridges **Telegram** and **Discord** messaging channels to **EnConvo** and **Claude Code** backends.

Users can interact with Claude Code running on your macOS from anywhere via Telegram or Discord — just like sitting at the terminal.

## Features

- **Dual backend**: Route messages to EnConvo API or Claude Code CLI
- **Multi-channel**: Telegram (Grammy, long-polling) + Discord (discord.js)
- **Multi-turn sessions**: Persistent conversation context via session IDs
- **File handling**: Inbound (user uploads) and outbound (deliverable files) with auto-upload to channel
- **Access control**: Open, allowlist, or pairing-code DM policies
- **Streaming**: Progressive message editing with typing cursor
- **BotFather management**: Create/configure Telegram bots programmatically via Telethon
- **Discord Developer Portal**: Manage Discord apps/bots, intents, slash commands via REST API

## Quick Start

```bash
# Install
cd enconvo-gw && npm install && npm link

# Add an agent
enconvo-gw agents add --id my-agent --name "My Agent" --type claude-code --model sonnet

# Add a Telegram channel
enconvo-gw channels add --channel telegram --account my-bot \
  --token "BOT_TOKEN" --agent my-agent --dm-policy open

# Add a Discord channel
enconvo-gw channels add --channel discord --account my-dc-bot \
  --token "BOT_TOKEN" --agent my-agent --dm-policy open

# Start
enconvo-gw gateway
```

## Architecture

```
Telegram Bot API  ←→  enconvo-gw  ←→  EnConvo API (localhost:54535)
Discord Gateway   ←→  (Node.js)   ←→  Claude Code CLI (claude -p)
                         ↕
                   ~/.enconvo-gw/
                     config.json
                     media/inbound/    (user uploads)
                     media/outbound/   (deliverable files)
```

## Directory Structure

```
enconvo-gw/
├── bin/enconvo-gw.js              # CLI entry point
├── src/
│   ├── cli.js                     # Commander CLI
│   ├── config.js                  # Config management (~/.enconvo-gw/)
│   ├── files.js                   # Media inbound/outbound handling
│   ├── gateway.js                 # Bot lifecycle, PID, auto-restart
│   ├── utils.js
│   ├── claude/
│   │   ├── client.js              # Claude Code CLI spawner
│   │   └── session.js             # Session UUID tracking
│   ├── discord/
│   │   ├── bot.js, handlers.js    # Discord bot + message routing
│   │   ├── access.js, send.js     # Access control + streaming
│   │   └── session.js
│   ├── enconvo/
│   │   └── client.js              # EnConvo HTTP API client
│   ├── telegram/
│   │   ├── bot.js, handlers.js    # Telegram bot + message routing
│   │   ├── access.js, send.js     # Access control + streaming
│   │   └── session.js
│   └── pairing/
│       └── pairing.js             # Pairing code system
├── skills/
│   ├── botfather/                 # Telegram BotFather management
│   └── discord-dev/               # Discord Developer Portal management
├── SKILL.md                       # Full skill documentation
└── package.json
```

## Dependencies

- [grammy](https://grammy.dev/) — Telegram bot framework
- [discord.js](https://discord.js.org/) — Discord bot framework
- [commander](https://github.com/tj/commander.js) — CLI framework

## Requirements

- Node.js 18+
- For Claude Code backend: `claude` CLI installed and authenticated
- For EnConvo backend: EnConvo running locally on port 54535

## Documentation

See [SKILL.md](SKILL.md) for full reference including CLI commands, config schema, agent types, media handling, BotFather/Discord setup, troubleshooting, and more.
