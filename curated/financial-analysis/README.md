# Financial Analysis Skill

A unified financial analysis & portfolio management toolkit for [Claude Code](https://claude.com/claude-code) (and compatible agent harnesses). Ten sub-commands covering market intelligence, strategy evolution, signal generation, options analysis, 禅動 chart analysis, CFTC smart-money tracking, and structured-note / options portfolio management with XLSX reporting.

## What this skill does

| Sub-command | What it does |
|-------------|--------------|
| **Daily Briefing** | Macro + sentiment + watchlist TA, with action items |
| **Macro Monitor** | 4-indicator liquidity risk engine (GREEN/YELLOW/RED) |
| **Sentiment Scanner** | Composite sentiment score (0–100) from NAAIM, F&G, VIX, Reddit, TA |
| **Evolve Strategy** | Generate, backtest, and walk-forward-validate 10+ trading strategies per ticker |
| **Strategy Signal** | "What does my strategy say right now?" — gated by macro, sentiment, options |
| **Quick Look** | Fast 10-indicator scoring for any ticker |
| **Options Analysis** | GEX, max pain, IV skew, OI walls, options sentiment |
| **禅動 (chandong)** | Buy/sell signal analysis via Discord bot (Playwright) + local fallback |
| **Portfolio Check** | Structured notes, sell puts, FX options, accumulators + dated XLSX report |
| **COT Report** | Weekly CFTC smart-money positioning HTML report |

## Install

### 1. Clone into your Claude Code skills directory

```bash
git clone https://github.com/EnConvo/curated.git
ln -s "$(pwd)/curated/financial-analysis" ~/.claude/skills/financial-analysis
```

Or, if you only want this single skill:

```bash
git clone https://github.com/EnConvo/curated.git /tmp/curated
cp -R /tmp/curated/financial-analysis ~/.claude/skills/
```

### 2. Install system dependencies

```bash
# TA-Lib C library (required for the talib Python wheel)
brew install ta-lib              # macOS
# or: apt-get install libta-lib0-dev   # Debian/Ubuntu
```

### 3. Install Python dependencies

```bash
cd ~/.claude/skills/financial-analysis
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cd ~/.claude/skills/financial-analysis
cp .env.example .env
# edit .env and set POLYGON_API_KEY and FRED_API_KEY
```

Both API keys have generous free tiers:
- **Polygon.io** — https://polygon.io/ (Stocks Starter recommended for full feature set)
- **FRED** — https://fred.stlouisfed.org/docs/api/api_key.html (instant, free)

Yahoo Finance data works without any keys, so most sub-commands degrade gracefully if Polygon is missing.

### 5. (Optional) Portfolio sub-command setup

If you want the portfolio checker:

```bash
cp market_intel/portfolio_data.template.json market_intel/portfolio_data.json
# edit portfolio_data.json with your real positions
```

`portfolio_data.json` is gitignored — never commit it.

## Usage

Inside Claude Code (or any compatible harness), just say:

```
/financial-analysis                 → Daily briefing
sentiment scan                      → Composite sentiment
evolve strategy for NVDA            → Build strategies for NVDA
strategy signal AAPL ride the rally → Trend-following signal for AAPL
quick look TSLA                     → 10-indicator snapshot
options analysis META               → GEX, max pain, OI walls
chandong NVDA                       → 禅動 buy/sell signal
fcn check                           → Portfolio risk report
weekly cot                          → CFTC smart-money report
```

See `SKILL.md` for the full sub-command reference.

## Optional configuration

All optional via `.env` — see `.env.example` for the full list:

| Env var | Effect |
|---------|--------|
| `FINANCIAL_ANALYSIS_OUTPUT_DIR` | Where generated reports land (default: `./reports/`) |
| `OBSIDIAN_VAULT_PATH` | Auto-save markdown briefings to your Obsidian vault |
| `CHANDONG_DISCORD_URL` | Discord channel URL for `/chart` bot automation |
| `WATCHLIST` | Override the default watchlist tickers |

## Project layout

```
financial-analysis/
├── SKILL.md                       # Sub-command routing, workflows, schemas
├── README.md
├── .env.example
├── requirements.txt
├── pyproject.toml
├── market_intel/                  # Macro / sentiment / options / portfolio
├── strategy_lab/                  # Backtesting, walk-forward, Pine Scripts
├── chandong/                      # 禅動 signal analyzer
└── tests/
```

## License

MIT — see `LICENSE` (you may add one when forking).

## Security & privacy notes

- `.env` (API keys) is gitignored
- `market_intel/portfolio_data.json` (your actual positions) is gitignored
- Generated XLSX/HTML/DOCX reports go to `$FINANCIAL_ANALYSIS_OUTPUT_DIR` (default `./reports/`), which is also gitignored
- If you fork and publish, double-check no `.env`, no `portfolio_data.json`, and no `reports/` files leaked into commits
