# hermes-configure

Configure any aspect of [Hermes Agent](https://github.com/NousResearch/hermes-agent) (by Nous Research) via CLI. The Hermes counterpart to `openclaw-configure` — same structure, parallel concepts, but real Hermes commands and config paths.

## What it does

Battle-tested guidance for managing a Hermes Agent install:

- **Channels** — Telegram / Discord / WhatsApp / Slack messaging gateway
- **Models** — full provider table (20 providers: Nous, Anthropic, OpenAI Codex, Gemini, OpenRouter, z.ai, Kimi, MiniMax, NVIDIA, Ollama, LM Studio, …) and how to switch the default
- **Skills** — 89 bundled skills, structure conventions, where user skills live
- **Plugins** — Hermes' Python plugin system at `~/.hermes/hermes-agent/plugins/`
- **Gateway** — service vs foreground, restart, install/uninstall
- **Cron / Hooks / Memory / MCP / ACP / Sessions / Insights**
- **Status / Diagnostics** — `hermes status`, `hermes doctor`, `hermes logs`
- **Backup / Import / Update / Uninstall**

Plus battle-tested **troubleshooting tables** for known gotchas (silent-deny on Telegram allowlists, polling conflicts, the `hermes login` command-removed footgun, auth.json schema mismatch with `~/.codex/auth.json`, etc.).

## What's verified end-to-end

The skill marks recipes that have been **tested against the live CLI** (not inferred from docs). Originally verified on Hermes v0.12.0 (2026-05-06) and carried forward through the v0.20.5 refresh (2026-08-24):

- ✅ Codex OAuth jumpstart — `openai-codex/gpt-5.5` mirroring an OpenClaw `main` agent
- ✅ Telegram bot setup non-interactive (env-var driven, with allowlist + home channel)
- ✅ Running OpenClaw + Hermes side-by-side on one host (different bots, shared Codex OAuth account)

## Hermes vs OpenClaw quick map

| Concept | OpenClaw | Hermes |
|---|---|---|
| Main config | `~/.openclaw/openclaw.json` (JSON) | `~/.hermes/config.yaml` (YAML) |
| API keys | inline in JSON / auth-profiles | `~/.hermes/.env` (env-style) |
| Personality | `~/.openclaw/workspace/SOUL.md` | `~/.hermes/SOUL.md` |
| Multi-agent | `agents add`, bindings | **single-agent design** |
| Importer | `openclaw migrate` (imports Hermes) | `hermes import` (imports Claude Code, etc.) |

Full map and "key differences" callout in `SKILL.md`.

## Self-evolution

The skill includes a **Version Check & Auto-Update Protocol** — when Hermes is upgraded, Claude regenerates `cli-reference.md` from the live binary, updates `commands.md`, and bumps `SKILL.md`. Each session that exercises a new corner of the CLI adds to the troubleshooting table.

## Files

- `SKILL.md` — main skill (Hermes/OpenClaw map, all subcommand domains, troubleshooting, jumpstart recipes, self-evolution protocol, version check protocol)
- `commands.md` — condensed CLI reference, one line per command
- `cli-reference.md` — full `--help` output for every top-level subcommand and nested subcommands (auto-generated from the live binary)
