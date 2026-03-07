#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ENCONVO_GW_DEPLOY="$HOME/enconvo-gw"
ENCONVO_GW_DATA="$HOME/.enconvo-gw"
ENCONVO_GW_BUNDLED="$SKILL_DIR/enconvo-gw"

usage() {
  cat <<EOF
team-configure setup — Bootstrap all dependencies for team management.

Usage: $(basename "$0") <command>

Commands:
  all               Run full setup (openclaw + enconvo-gw + botfather + discord-dev)
  openclaw          Install/update OpenClaw (npm global)
  enconvo-gw        Deploy/update enconvo-gw from bundled source
  botfather         Check/setup BotFather Telethon auth
  discord-dev       Check/setup Discord Developer Portal auth
  status            Show status of all dependencies
  help              Show this help

Examples:
  $(basename "$0") status        # Check what's installed
  $(basename "$0") all           # Full bootstrap
  $(basename "$0") enconvo-gw    # Deploy/update enconvo-gw only
EOF
}

log() { echo "▸ $*"; }
ok()  { echo "✓ $*"; }
err() { echo "✗ $*" >&2; }
warn(){ echo "⚠ $*"; }

# --- OpenClaw ---
setup_openclaw() {
  log "Checking OpenClaw..."
  if command -v openclaw &>/dev/null; then
    local ver
    ver=$(openclaw --version 2>/dev/null || echo "unknown")
    ok "OpenClaw installed: v$ver"
    log "Checking for updates..."
    npm update -g openclaw 2>/dev/null && ok "OpenClaw up to date" || warn "Update check failed (may need sudo)"
  else
    log "OpenClaw not found. Installing via npm..."
    if command -v npm &>/dev/null; then
      npm install -g openclaw
      ok "OpenClaw installed: $(openclaw --version 2>/dev/null)"
    else
      err "npm not found. Install Node.js first: https://nodejs.org/"
      return 1
    fi
  fi

  # Check if initial setup needed
  if [ ! -f "$HOME/.openclaw/openclaw.json" ]; then
    warn "OpenClaw not configured yet."
    echo "  Run: openclaw setup"
    echo "  Or:  openclaw onboard --flow quickstart"
  else
    ok "OpenClaw config exists at ~/.openclaw/openclaw.json"
  fi
}

# --- enconvo-gw ---
setup_enconvo_gw() {
  log "Deploying enconvo-gw from bundled source..."

  if [ ! -d "$ENCONVO_GW_BUNDLED/src" ]; then
    err "Bundled enconvo-gw not found at $ENCONVO_GW_BUNDLED"
    err "Reinstall the team-configure skill."
    return 1
  fi

  # Create deploy directory
  mkdir -p "$ENCONVO_GW_DEPLOY"

  # Check rsync availability
  if ! command -v rsync &>/dev/null; then
    err "rsync not found. Install it first (brew install rsync / apt install rsync)"
    return 1
  fi

  # Compare versions — always deploy latest from bundle
  local bundled_ver deployed_ver
  bundled_ver=$(node -e "console.log(require('$ENCONVO_GW_BUNDLED/package.json').version)" 2>/dev/null || echo "0.0.0")
  deployed_ver=$(node -e "console.log(require('$ENCONVO_GW_DEPLOY/package.json').version)" 2>/dev/null || echo "0.0.0")

  if [ "$bundled_ver" = "$deployed_ver" ] && [ -d "$ENCONVO_GW_DEPLOY/node_modules" ]; then
    # Even if same version, sync source files (skill may have been updated)
    log "Same version ($bundled_ver), syncing source files..."
    rsync -a --delete "$ENCONVO_GW_BUNDLED/src/" "$ENCONVO_GW_DEPLOY/src/"
    rsync -a --delete "$ENCONVO_GW_BUNDLED/bin/" "$ENCONVO_GW_DEPLOY/bin/"
    cp "$ENCONVO_GW_BUNDLED/package.json" "$ENCONVO_GW_DEPLOY/package.json"
    cp "$ENCONVO_GW_BUNDLED/package-lock.json" "$ENCONVO_GW_DEPLOY/package-lock.json"
    ok "enconvo-gw source synced (v$bundled_ver)"
  else
    log "Deploying enconvo-gw v$bundled_ver (was: $deployed_ver)..."
    rsync -a --delete --exclude node_modules "$ENCONVO_GW_BUNDLED/" "$ENCONVO_GW_DEPLOY/"
    cd "$ENCONVO_GW_DEPLOY"
    npm install --production || { err "npm install failed"; return 1; }
    ok "enconvo-gw deployed v$bundled_ver"
  fi

  # npm link for global CLI
  cd "$ENCONVO_GW_DEPLOY"
  if ! command -v enconvo-gw &>/dev/null; then
    log "Linking enconvo-gw globally..."
    npm link 2>/dev/null || sudo npm link 2>/dev/null
  fi

  if command -v enconvo-gw &>/dev/null; then
    ok "enconvo-gw CLI available: $(which enconvo-gw)"
  else
    warn "enconvo-gw not on PATH. Add to PATH or run directly: node $ENCONVO_GW_DEPLOY/bin/enconvo-gw.js"
  fi

  # Create data directory
  mkdir -p "$ENCONVO_GW_DATA"/{pairing,allowlists,media/{inbound,outbound}}
  ok "enconvo-gw data directory ready at $ENCONVO_GW_DATA"
}

# --- BotFather ---
setup_botfather() {
  local bf="$HOME/.claude/skills/botfather/scripts/botfather.sh"
  log "Checking BotFather skill..."

  if [ ! -f "$bf" ]; then
    err "BotFather skill not installed."
    echo "  Install it from ClawHub or copy to ~/.claude/skills/botfather/"
    return 1
  fi

  ok "BotFather script found: $bf"

  # Check auth status
  local status
  status=$("$bf" status 2>&1) || true
  if echo "$status" | grep -qi "authenticated\|ready\|logged in\|connected"; then
    ok "BotFather: authenticated"
  else
    warn "BotFather: not authenticated yet."
    echo "  Option 1 (Playwright): AI navigates my.telegram.org, extracts API creds"
    echo "  Option 2 (Manual):     $bf setup"
    echo ""
    echo "  After creds are saved, run: $bf auth"
    echo "  (Interactive — needs phone number + 2FA code in terminal)"
  fi
}

# --- Discord Dev ---
setup_discord_dev() {
  local dd="$HOME/.claude/skills/discord-dev/scripts/discord-dev.sh"
  log "Checking Discord Dev skill..."

  if [ ! -f "$dd" ]; then
    err "Discord Dev skill not installed."
    echo "  Install it from ClawHub or copy to ~/.claude/skills/discord-dev/"
    return 1
  fi

  ok "Discord Dev script found: $dd"

  # Check auth status
  local status
  status=$("$dd" status 2>&1) || true
  if echo "$status" | grep -qi "authenticated\|ready\|valid\|token ok"; then
    ok "Discord Dev: authenticated"
  else
    warn "Discord Dev: not authenticated yet."
    echo "  Setup requires Playwright browser automation:"
    echo "  1. Navigate to https://discord.com/login"
    echo "  2. User logs in"
    echo "  3. AI extracts user session token via browser_evaluate"
    echo "  4. Save: $dd save-token --token <TOKEN>"
  fi
}

# --- Status ---
show_status() {
  echo "=== team-configure dependency status ==="
  echo ""

  # OpenClaw
  if command -v openclaw &>/dev/null; then
    ok "OpenClaw: $(openclaw --version 2>/dev/null)"
    if [ -f "$HOME/.openclaw/openclaw.json" ]; then
      ok "  Config: ~/.openclaw/openclaw.json exists"
    else
      warn "  Config: not initialized (run: openclaw setup)"
    fi
  else
    err "OpenClaw: not installed"
  fi
  echo ""

  # enconvo-gw
  if command -v enconvo-gw &>/dev/null; then
    local ver
    ver=$(node -e "console.log(require('$ENCONVO_GW_DEPLOY/package.json').version)" 2>/dev/null || echo "?")
    ok "enconvo-gw: v$ver ($(which enconvo-gw))"
    local gw_status
    gw_status=$(enconvo-gw gateway status 2>&1) || true
    if echo "$gw_status" | grep -qi "running"; then
      ok "  Gateway: running"
    else
      warn "  Gateway: not running"
    fi
  elif [ -d "$ENCONVO_GW_DEPLOY/src" ]; then
    warn "enconvo-gw: deployed but not linked (run: setup.sh enconvo-gw)"
  else
    err "enconvo-gw: not deployed (run: setup.sh enconvo-gw)"
  fi
  echo ""

  # BotFather
  local bf="$HOME/.claude/skills/botfather/scripts/botfather.sh"
  if [ -f "$bf" ]; then
    ok "BotFather: skill installed"
    local bf_status
    bf_status=$("$bf" status 2>&1) || true
    if echo "$bf_status" | grep -qi "authenticated\|ready\|logged in\|connected"; then
      ok "  Auth: ready"
    else
      warn "  Auth: not configured (run: setup.sh botfather)"
    fi
  else
    err "BotFather: skill not installed"
  fi
  echo ""

  # Discord Dev
  local dd="$HOME/.claude/skills/discord-dev/scripts/discord-dev.sh"
  if [ -f "$dd" ]; then
    ok "Discord Dev: skill installed"
    local dd_status
    dd_status=$("$dd" status 2>&1) || true
    if echo "$dd_status" | grep -qi "authenticated\|ready\|valid\|token ok"; then
      ok "  Auth: ready"
    else
      warn "  Auth: not configured (run: setup.sh discord-dev)"
    fi
  else
    err "Discord Dev: skill not installed"
  fi
  echo ""
  echo "=== end ==="
}

# --- Main ---
case "${1:-help}" in
  all)
    setup_openclaw
    echo ""
    setup_enconvo_gw
    echo ""
    setup_botfather
    echo ""
    setup_discord_dev
    echo ""
    echo "=== Setup complete. Run 'setup.sh status' to verify. ==="
    ;;
  openclaw)     setup_openclaw ;;
  enconvo-gw)   setup_enconvo_gw ;;
  botfather)    setup_botfather ;;
  discord-dev)  setup_discord_dev ;;
  status)       show_status ;;
  help|--help|-h) usage ;;
  *)
    err "Unknown command: $1"
    usage
    exit 1
    ;;
esac
