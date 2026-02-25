# OpenClaw OAuth2 Model Setup Guide

> Source: [@robbinfan on X](https://x.com/robbinfan/status/2022952496189313404) — "别再为 Token 焦虑了" (Feb 15, 2026)
> 319K+ views, 790 likes, 1957 bookmarks

## Overview

You do NOT need to buy API tokens separately. Your existing $20/month subscriptions
(Claude Pro, GPT Plus, Gemini Pro) can be connected directly into OpenClaw via OAuth.
This gives you access to top-tier models at zero additional cost.

## The "Model Arsenal" Setup

After completing all three steps, you'll have:

| Provider | Models Available | Auth Method |
|----------|-----------------|-------------|
| Claude (Anthropic) | Opus 4.6, Opus 4.5, Sonnet 4.5 | Claude Code CLI token |
| GPT (OpenAI) | GPT 5.2, GPT 5.2 Codex, GPT 5.3 Codex | OpenAI Codex OAuth |
| Gemini (Google) | Gemini 3 Pro, Gemini 3 Flash | Gemini CLI Auth |

You can run multiple sessions simultaneously — one per model — and switch freely.

---

## Prerequisites

- OpenClaw installed and running (`openclaw gateway`)
- npm available (for installing CLI tools)
- Active subscriptions: Claude Pro ($20), GPT Plus ($20), Gemini Pro ($20)

---

## Step 1: Connect Claude Pro Subscription

### 1a. Install Claude Code CLI

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

### 1b. Generate Claude Token

```bash
claude setup-token
```

This opens a browser for OAuth authorization. After authorizing, you get a token string.
Save it.

### 1c. Configure in OpenClaw

```bash
openclaw configure
```

In the wizard:
- **Provider**: select `Anthropic`
- **Paste** the token from step 1b
- **Profile**: select `default`
- **Models**: check the ones you want (e.g. Opus 4.6, Sonnet 4.5)

### 1d. Verify

```bash
openclaw models list
```

You should see Claude models in the list.

### Risk Note

- The auth method itself is legitimate
- Anthropic may trigger risk controls for some regions/accounts
- This is an Anthropic platform policy issue, not an OpenClaw issue
- **Recommendation**: Use Claude as enhancement, GPT/Gemini as stable base

---

## Step 2: Connect GPT Plus Subscription

### 2a. Install OpenAI Codex CLI

```bash
npm i -g @openai/codex
```

### 2b. Configure in OpenClaw

```bash
openclaw configure
```

**IMPORTANT**: Choose **"OpenAI Codex"** (OAuth flow via browser), NOT "paste API Key".

The browser opens for OAuth. After authorization, return to terminal.

### 2c. Select Models

Recommended:
- GPT 5.2
- GPT 5.2 Codex
- GPT 5.3 Codex

### 2d. Verify

```bash
openclaw models list
```

---

## Step 3: Connect Gemini Pro Subscription

### 3a. Install Gemini CLI

```bash
npm install -g @google/gemini-cli
```

### 3b. Configure in OpenClaw

```bash
openclaw configure
```

- **Provider**: select `Google`
- **Auth method**: select `Google Gemini CLI Auth`
- Complete browser login

### 3c. Select Models

Recommended:
- Gemini 3 Pro
- Gemini 3 Flash

### 3d. Verify

**Terminal verification:**
```bash
openclaw models list
```

**Telegram verification:**
Send `/models` to your OpenClaw bot in Telegram. Switch to Gemini Pro and ask a question.

---

## Post-Setup: Using Multiple Models

You can open separate sessions per model:
- **Gemini 3 Pro session**: OAuth login, uses your Gemini $20 subscription. ~1M context window.
- **Claude Opus 4.6 session**: Uses Claude Pro subscription token. ~400K context window.
- **GPT session**: OAuth login. ~400K context window.

### Switching Default Model

```bash
openclaw models set <provider/model-id>
```

Examples:
```bash
openclaw models set anthropic/claude-opus-4-6
openclaw models set openai-codex/codex-5.3
openclaw models set google-gemini-cli/gemini-3-pro
```

### Checking Model Status

```bash
openclaw models status
```

Shows: default model, fallbacks, aliases, auth status, OAuth token expiry, usage quotas.

---

## OpenClaw Plugin Requirements for OAuth Providers

Some providers require enabling plugins first:

| Provider | Plugin Required | Enable Command |
|----------|----------------|----------------|
| Anthropic | None (built-in) | N/A |
| OpenAI Codex | `openai-codex` (if not auto) | Check `openclaw plugins list` |
| Google Gemini CLI | `google-gemini-cli-auth` | `openclaw plugins enable google-gemini-cli-auth` |
| MiniMax Portal | `minimax-portal-auth` | `openclaw plugins enable minimax-portal-auth` |

---

## Quick Reference: Auth Commands

```bash
# List all auth profiles
openclaw models auth

# Add new auth interactively
openclaw models auth add

# Run OAuth flow for a specific provider
openclaw models auth login

# Paste a token manually
openclaw models auth paste-token --provider <name>

# Check auth/token status
openclaw models status
```

---

## Lessons Learned (from real setup experience)

1. **Ollama (local models)** requires a provider block in config with `"api": "ollama"`,
   `"baseUrl": "http://127.0.0.1:11434"`, and `"apiKey": "ollama-local"` (dummy value)
2. **Gateway restart** is needed after config changes: `openclaw gateway stop` then `openclaw gateway`
3. **Plugin must be enabled** before a channel/provider can be used: `openclaw plugins enable <id>`
4. The `openclaw configure` interactive wizard is the easiest path for OAuth providers
5. Use `openclaw models set <model>` to switch defaults — takes effect immediately for new sessions
