"""Central configuration for the finance agent system."""
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

PROJECT_DIR = Path(__file__).parent
ENV_FILE = PROJECT_DIR / ".env"
if not ENV_FILE.exists():
    ENV_FILE = PROJECT_DIR.parent / ".env"

def load_env():
    """Load .env file into os.environ.

    Handles comments, quoted values, and inline comments.
    Logs a warning if no .env file is found.
    """
    if not ENV_FILE.exists():
        logger.warning("No .env file found at %s — API keys may be missing", ENV_FILE)
        return
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip()
        # Strip surrounding quotes
        if len(val) >= 2 and val[0] == val[-1] and val[0] in ('"', "'"):
            val = val[1:-1]
        # Strip inline comments (only for unquoted values)
        if " #" in val:
            val = val[:val.index(" #")].rstrip()
        os.environ.setdefault(key, val)

load_env()

POLYGON_API_KEY = os.environ.get("POLYGON_API_KEY", "")
FRED_API_KEY = os.environ.get("FRED_API_KEY", "")

def validate_api_keys():
    """Check that required API keys are set and non-empty. Returns list of missing keys."""
    missing = []
    if not POLYGON_API_KEY:
        missing.append("POLYGON_API_KEY")
    if not FRED_API_KEY:
        missing.append("FRED_API_KEY")
    if missing:
        logger.warning("Missing API keys: %s — some features will be unavailable", ", ".join(missing))
    return missing

# ── Output / Vault Paths ─────────────────────────────────────────────────
# All generated reports (XLSX, HTML, DOCX) land in OUTPUT_DIR.
# Override via env: FINANCIAL_ANALYSIS_OUTPUT_DIR=/path/to/reports
# Default: <repo>/reports/
REPO_ROOT = PROJECT_DIR.parent
OUTPUT_DIR = Path(
    os.environ.get(
        "FINANCIAL_ANALYSIS_OUTPUT_DIR",
        str(REPO_ROOT / "reports"),
    )
).expanduser()

def get_output_dir() -> Path:
    """Return OUTPUT_DIR, creating it on first call."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR

# Optional Obsidian vault for auto-saving briefings as markdown notes.
# Override via env: OBSIDIAN_VAULT_PATH=/path/to/Obsidian Vault
# If unset, Obsidian save steps are silently skipped.
_vault_env = os.environ.get("OBSIDIAN_VAULT_PATH", "").strip()
OBSIDIAN_VAULT_PATH = Path(_vault_env).expanduser() if _vault_env else None

# Optional Discord channel URL for the 禅動 (chandong) sub-command.
# Override via env: CHANDONG_DISCORD_URL=https://discord.com/channels/SERVER_ID/CHANNEL_ID
# If unset, chandong falls back to local analysis automatically.
CHANDONG_DISCORD_URL = os.environ.get("CHANDONG_DISCORD_URL", "").strip() or None

# FRED series IDs for macro liquidity
FRED_SERIES = {
    "fed_assets": "WALCL",       # Fed total assets (weekly)
    "tga_balance": "WTREGEN",    # Treasury General Account (weekly)
    "rrp": "RRPONTSYD",         # Overnight Reverse Repo (daily)
    "sofr": "SOFR",             # Secured Overnight Financing Rate (daily)
    "cpi": "CPIAUCSL",          # CPI (monthly)
    "nfp": "PAYEMS",            # Non-farm payrolls (monthly)
    "us2y": "DGS2",             # 2-year Treasury yield (daily)
    "us10y": "DGS10",           # 10-year Treasury yield (daily)
    "fed_funds": "DFF",         # Fed funds rate (daily)
    "vix": "VIXCLS",            # VIX (daily)
}

# Treasury Fiscal Data API (no auth needed)
TREASURY_API_BASE = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service"

# Macro liquidity trigger thresholds (from article)
TRIGGERS = {
    "net_liquidity_weekly_drop_pct": 5.0,   # >5% weekly drop → warning
    "sofr_reduce_threshold": 5.5,           # SOFR > 5.5% → reduce positions
    "move_stop_loss": 130,                  # MOVE > 130 → stop loss
    "move_warning": 100,                    # MOVE > 100 → warning
}

# Sentiment thresholds
SENTIMENT = {
    "naaim_overbought": 80,        # NAAIM > 80 → institutions maxed out
    "aaii_bull_extreme": 60,        # AAII bulls > 60% → euphoria
    "aaii_bear_extreme": 50,        # AAII bears > 50% → capitulation
    "fear_greed_extreme_greed": 80, # CNN Fear & Greed > 80
    "fear_greed_extreme_fear": 20,  # CNN Fear & Greed < 20
}

# Options analysis thresholds
OPTIONS = {
    "pc_ratio_bearish": 1.5,       # P/C ratio > 1.5 → bearish
    "pc_ratio_bullish": 0.5,       # P/C ratio < 0.5 → bullish
    "iv_skew_bearish": 0.05,       # Put IV premium > 5% → bearish
    "iv_skew_bullish": -0.05,      # Call IV premium > 5% → bullish
    "chain_fetch_delay": 0.3,      # Delay between chain fetches (seconds)
    "max_dte": 45,                 # Max days to expiration
    "max_expirations": 4,          # Max expirations to analyze
}
