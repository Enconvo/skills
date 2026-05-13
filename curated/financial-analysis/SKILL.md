---
name: financial-analysis
description: "Unified financial analysis & portfolio management toolkit. Routes to the right sub-system based on intent. Covers: daily market briefings, macro risk monitoring, sentiment scanning, strategy evolution & signals, options analysis, 禅動 chart analysis, COT smart-money reports, and full portfolio checking (structured notes, sell puts, FX options, accumulators) with XLSX report generation. Use when user says /financial-analysis, 'daily briefing', 'morning briefing', 'macro risk', 'liquidity check', 'sentiment scan', 'market sentiment', 'evolve strategy', 'create strategy', 'strategy signal', 'what does the strategy say', 'quick look', 'scan ticker', 'ride the rally', 'catch dips', 'play safe', '禅動', 'chandong', 'analyze ticker', 'fcn check', 'fcn status', 'check fcn', 'portfolio check', 'portfolio report', 'structured products', 'are my fcns safe', 'sell puts', 'accumulators', 'options analysis', 'cot report', 'smart money'."
---

# Financial Analysis & Portfolio Management — Unified Toolkit

## Overview

Single skill with 10 sub-commands covering market intelligence, strategy evolution, signal generation, options analysis, 禅動 chart analysis, COT (smart-money) reporting, and portfolio management (structured notes, sell puts, FX options, accumulators) with XLSX report generation.

All Python code is shipped inside the skill directory itself — referred to below as `$SKILL_DIR`. After installation that's typically `~/.claude/skills/financial-analysis/` (or wherever your harness places skills).

## Sub-Command Routing

| User Says | Routes To | Directory |
|-----------|-----------|-----------|
| `/financial-analysis` or "daily briefing" / "morning briefing" / "market update" | Daily Briefing | `market_intel/` |
| "macro risk" / "liquidity check" / "risk check" / "is the market safe" | Macro Monitor | `market_intel/` |
| "sentiment scan" / "market sentiment" / "how is sentiment" / "retail sentiment" | Sentiment Scanner | `market_intel/` |
| "evolve strategy for TICKER" / "create strategy" / "backtest" | Evolve Strategy | `strategy_lab/` |
| "strategy signal TICKER" / "what does the strategy say" / "ride the rally" / "catch dips" | Strategy Signal | `strategy_lab/` + `market_intel/` |
| "quick look TICKER" / "scan ticker" / "what do indicators say" | Quick Look | `strategy_lab/` |
| "options analysis TICKER" / "GEX" / "max pain" / "put call ratio" / "IV skew" / "options flow" / "dealer positioning" | Options Analysis | `market_intel/` |
| "fcn check" / "fcn status" / "check fcn" / "portfolio check" / "portfolio report" / "structured products" / "are my fcns safe" / "sell puts" / "accumulators" | Portfolio Check + XLSX Report | `market_intel/` |
| "禅動 TICKER" / "chandong TICKER" / "analyze TICKER" | 禅動 Analysis (automated) | `chandong/` + Playwright MCP |
| "cot" / "cot update" / "cot report" / "weekly cot" / "smart money" / "smart money scan" / "hedge fund positioning" / "cftc" | COT Report | `market_intel/` |

If the user just says `/financial-analysis` with no qualifier, run the **Daily Briefing** (most common use case).

## Project Structure

```
$SKILL_DIR/
├── .env                          ← POLYGON_API_KEY, FRED_API_KEY, optional paths
├── .env.example
├── .gitignore
├── SKILL.md
├── README.md
├── requirements.txt
├── pyproject.toml
├── market_intel/                 ← Macro / sentiment / briefing / options / portfolio
│   ├── config.py                 ← Central config, .env loader, OUTPUT_DIR
│   ├── data_sources.py           ← Data fetchers (FRED, Polygon, Yahoo, CNN, Treasury, TradingView TA)
│   ├── macro_monitor.py          ← 4-indicator risk engine (GREEN/YELLOW/RED)
│   ├── sentiment_scanner.py      ← Composite sentiment (0-100) with contrarian signals
│   ├── briefing.py               ← Full daily briefing: macro + TA watchlist + actions
│   ├── options_analyzer.py       ← 9-dimension options analysis (GEX, max pain, IV skew)
│   ├── portfolio_checker.py      ← Portfolio check (structured notes, sell puts, FX, accumulators)
│   ├── generate_portfolio_xlsx.py ← XLSX report generator (template-based)
│   ├── cot_tracker.py            ← CFTC smart-money JSON tracker
│   ├── generate_cot_html_report.py ← Self-contained HTML COT report
│   ├── generate_cot_report.py    ← DOCX COT report
│   ├── portfolio_data.template.json ← Copy to `portfolio_data.json` and fill in
│   └── templates/
│       └── Portfolio_Report_Template.xlsx
├── strategy_lab/                 ← Strategy evolution & signals
│   ├── utils.py                  ← Data loading, Polygon fetching, cross-verification
│   ├── analyze.py, regime_detector.py, regime_chart.py
│   ├── walk_forward*.py, fetch_*.py
│   ├── strategy_registry.json    ← Intent→strategy mapping per ticker
│   ├── au_strategies/, au_daily_strategies/, nvda_strategies/, meta_strategies/
│   ├── backtests/                ← Generic backtest templates
│   └── pine_scripts/             ← Generated Pine Script strategies
├── chandong/                     ← 禅動 signal analysis
│   ├── chandong_analyzer.py
│   └── Phase4_禅动Pro_Development_Plan.md
└── tests/
```

## Configuration

All paths are configurable via environment variables (see `.env.example`). Defaults are sensible — most installs only need to set `POLYGON_API_KEY` and `FRED_API_KEY`.

| Env Var | Purpose | Default |
|---------|---------|---------|
| `POLYGON_API_KEY` | Stock + options data | required for full features |
| `FRED_API_KEY` | Macro indicators | required for full features |
| `FINANCIAL_ANALYSIS_OUTPUT_DIR` | Where reports land | `$SKILL_DIR/reports/` |
| `OBSIDIAN_VAULT_PATH` | Optional Obsidian markdown sync | unset → skip |
| `CHANDONG_DISCORD_URL` | Optional Discord bot URL for `chandong` | unset → local fallback |
| `WATCHLIST` | Override default tickers | `NVDA,AAPL,MSFT,GOOGL,META,TSLA,AMZN,SPY,QQQ,BTCUSD` |

## Obsidian Integration (optional)

If `OBSIDIAN_VAULT_PATH` is set, briefings, sentiment scans, macro reports, options analyses, and chandong reports auto-save as markdown notes under `<vault>/Daily Briefings/`. File naming: `Daily Briefings/YYYY-MM-DD — {Report Type}.md`. Each note carries YAML frontmatter (`date`, `type`, `risk_level`, `sentiment_score`, `key_signals`, tags). If the vault path is unset, this step is silently skipped.

---

# ═══════════════════════════════════════════════════════════
#  SUB-COMMAND 1: DAILY BRIEFING
# ═══════════════════════════════════════════════════════════

## Trigger
`/financial-analysis`, "daily briefing", "morning briefing", "market briefing", "daily brief", "what happened overnight", "market update"

## Workflow

### Step 1: Run the Briefing Generator
```bash
cd "$SKILL_DIR/market_intel" && python3 briefing.py
```

This automatically:
1. Fetches macro data (FRED: net liquidity, SOFR, yields | Polygon: USDJPY, S&P 500 | CNN: Fear & Greed)
2. Runs the macro liquidity risk assessment (GREEN/YELLOW/RED)
3. Fetches TradingView TA for the configured watchlist
4. Generates action items based on risk level

### Step 1.5: Run CFTC Smart-Money Scan
```bash
cd "$SKILL_DIR/market_intel" && python3 cot_tracker.py --json
```

Include in daily brief highlights:
- Bitcoin, S&P 500, Nasdaq 100, Gold, Crude Oil, Euro FX, 10Y Treasury
- Hedge-fund net position + week-over-week delta
- 2-3 biggest directional changes as "Smart Money Alerts"

### Step 2: Get Structured Data
```bash
cd "$SKILL_DIR/market_intel" && python3 briefing.py --json
```

### Step 3: Save to Obsidian (only if `OBSIDIAN_VAULT_PATH` is set)
Write the file at `$OBSIDIAN_VAULT_PATH/Daily Briefings/$DATE — Daily Briefing.md` with:
- **Frontmatter**: `date`, `type: Daily Briefing`, `risk_level`, `sentiment_score`, `key_signals`, `tags: [market-intel, daily-briefing]`
- **Content**: The full text report output (formatted as markdown)

### Step 4: TTS Output (if audio mode on)
If audio mode is enabled, generate a spoken summary of the key findings.

## Data Sources
| Source | Data | Auth |
|--------|------|------|
| FRED API | Net liquidity (WALCL, WTREGEN, RRPONTSYD), SOFR, yields | `FRED_API_KEY` |
| Polygon.io | USDJPY, S&P 500 | `POLYGON_API_KEY` |
| TradingView TA | RSI, MACD, ADX, buy/sell signals | No auth (tradingview-ta) |
| CNN | Fear & Greed Index | Public |
| Yahoo Finance | MOVE Index | Public |
| Treasury Fiscal Data | TGA balance | Public |

## Risk Level Interpretation
- **GREEN** (score 0-2): Normal conditions. Proceed with strategy.
- **YELLOW** (score 3-4): Caution. Tighten stops, avoid new large positions.
- **RED** (score 5+): Elevated risk. Reduce positions, consider hedges.

---

# ═══════════════════════════════════════════════════════════
#  SUB-COMMAND 2: MACRO MONITOR
# ═══════════════════════════════════════════════════════════

## Trigger
"macro risk", "liquidity check", "check liquidity", "risk check", "is the market safe", "market risk level"

## Workflow

```bash
cd "$SKILL_DIR/market_intel" && python3 macro_monitor.py            # text
cd "$SKILL_DIR/market_intel" && python3 macro_monitor.py --json     # structured
```

Optionally save to `$OBSIDIAN_VAULT_PATH/Daily Briefings/$DATE — Macro Monitor.md` with frontmatter: `date`, `type: Macro Monitor`, `risk_level`, `key_signals`, `tags: [market-intel, macro-monitor]`.

## Key Indicators
| Indicator | Source | Trigger |
|-----------|--------|---------|
| Net Liquidity | FRED (WALCL - WTREGEN - RRPONTSYD) | >5% weekly drop → RED |
| SOFR | FRED (SOFR) | >5.5% → reduce positions |
| MOVE | Yahoo Finance (^MOVE) | >130 → stop loss |
| USDJPY | Polygon (C:USDJPY) | >2% weekly drop → carry unwind risk |
| Fear & Greed | CNN API | >80 extreme greed, <20 extreme fear |

---

# ═══════════════════════════════════════════════════════════
#  SUB-COMMAND 3: SENTIMENT SCANNER
# ═══════════════════════════════════════════════════════════

## Trigger
"sentiment scan", "market sentiment", "what is the mood", "how is sentiment", "are people bullish", "retail sentiment"

## Workflow

```bash
cd "$SKILL_DIR/market_intel" && python3 sentiment_scanner.py
cd "$SKILL_DIR/market_intel" && python3 sentiment_scanner.py --json
```

Optionally save to `$OBSIDIAN_VAULT_PATH/Daily Briefings/$DATE — Sentiment Scan.md`.

## Data Sources & Weights
| Source | Weight | What it measures |
|--------|--------|-----------------|
| NAAIM Exposure Index | 25% | Institutional positioning (0-200 scale) |
| CNN Fear & Greed | 25% | Market-wide composite (0-100) |
| VIX (inverted) | 20% | Equity volatility / fear gauge |
| Reddit (WSB, stocks, investing) | 15% | Retail sentiment keyword analysis |
| TradingView TA consensus | 15% | Technical buy/sell signals across watchlist |

## Composite Score Interpretation
- **75-100**: EXTREME GREED — contrarian sell zone
- **60-74**: GREED — caution, potential topping
- **40-59**: NEUTRAL
- **25-39**: FEAR — contrarian lean
- **0-24**: EXTREME FEAR — contrarian buy zone

---

# ═══════════════════════════════════════════════════════════
#  SUB-COMMAND 4: EVOLVE STRATEGY
# ═══════════════════════════════════════════════════════════

## Trigger
"evolve strategy for TICKER", "create strategy for", "build trading strategy", "backtest ticker", `/evolve-strategy TICKER`, `--refresh` flag to re-evaluate existing strategies

## Invocation

```
/financial-analysis evolve TICKER
/financial-analysis evolve TICKER --refresh
```

If the user mentions a ticker that already has a `{ticker}_strategies/` folder, suggest refresh mode.

## Project Location

All work happens in: `$SKILL_DIR/strategy_lab/`

Key files:
- `utils.py` — Data loading, Polygon fetching, cross-verification utilities
- `strategy_registry.json` — Intent→strategy mapping per ticker
- `regime_detector.py` — Auto-detect market regimes from OHLCV data
- `regime_chart.py` — Interactive HTML chart generator (Plotly)
- `au_strategies/`, `au_daily_strategies/`, `nvda_strategies/`, `meta_strategies/` — Example evolved strategies (shipped as reference)
- `pine_scripts/` — Generated Pine Script strategies for TradingView
- `backtests/` — Generic backtest templates
- `*_results.csv` — Master results per ticker
- `*_data_verified.json` — Cross-verification reports per ticker

## Configuration — Polygon.io (Primary) + yfinance (Fallback)

API key comes from `POLYGON_API_KEY` in `.env`. Loaded via `config.py`'s parent-dir fallback so scripts work whether run from the skill root or from a subdir.

**Data source priority:**
1. **Polygon.io** (Stocks Starter plan) — SIP-licensed, clean data, up to 5 years 1h candles
2. **yfinance** (fallback) — Free, 2 years 1h / 5 years daily

### Key `utils.py` Functions

| Function | Purpose |
|----------|---------|
| `fetch_data(ticker, timeframe, years_back)` | Polygon → yfinance fallback, saves CSV |
| `load_data(ticker, timeframe)` | Generic CSV loader |
| `cross_verify_indicators(data, ticker, timeframe)` | Local talib vs Polygon API |
| `is_verified(ticker)` | Checks if ticker has passing verification |

## Workflow

### Step 1: Download Data
```python
from utils import fetch_data
df_1h, source_1h = fetch_data(ticker, timeframe="1h", years_back=5)
df_daily, source_daily = fetch_data(ticker, timeframe="daily", years_back=5)
```

### Step 1.5: Data Profile & Integrity Check
Print provider, dataset sizes, date ranges, price range, NaN/zero-volume/OHLC checks.

### Step 1.6: Cross-Verification (one-time per ticker)
```python
from utils import cross_verify_indicators, print_verification_report, save_verification_report, is_verified

if not is_verified(ticker):
    results = cross_verify_indicators(data_daily, ticker, timeframe="daily")
    print_verification_report(results, ticker)
    save_verification_report(results, ticker)
```

Tests SMA(50), EMA(21), RSI(14), MACD(12,26,9) — local talib vs Polygon API.

### Step 2: Set Cash Amount
- Stock price > $100: `cash=1_000_000`
- Stock price $10-$100: `cash=100_000`
- Stock price < $10: `cash=10_000`

### Step 3: Round 1 — Generate 10+ Diverse Strategies
Create directory `{ticker_lower}_strategies/`. Categories: Trend Following, Mean Reversion, Momentum, Breakout, Multi-Indicator, Gap, Pre-Market.

Each strategy file must be standalone Python, use `self.I()` to wrap all indicator calculations, define indicator functions OUTSIDE the Strategy class, use `from backtesting.lib import crossover` (NOT crossunder), print full stats.

### Steps 4-6: Analyze → Round 2 (6-8) → Round 3 (3-4)
Analyze patterns, combine winners, fix losers, add ATR trailing stops, build regime-switching strategies. Max 3 entry conditions.

### Step 7: Generate Pine Scripts
Convert top 3 to Pine Script v5. Save to `pine_scripts/{ticker}_{name}.pine`.

### Step 8: Final Report + Current State of #1 Strategy
Print ranked summary. Run #1 strategy on full dataset and report its state on the last bar.

### Step 9: Smart Walk-Forward Validation
Auto-detect regimes (bull/bear/consolidation/choppy), test each strategy across all regimes, with/without 200 SMA filter.
- ROBUST: profitable in >= 75% of windows
- MARGINAL: 50-74%
- FRAGILE: < 50%

### Step 10: Interactive HTML Dashboard
Generate a self-contained HTML chart using `regime_chart.generate_chart(...)`. Outputs `{ticker_lower}_chart.html` in `strategy_lab/`. Self-contained, dark theme, candlestick + regime bands + trade markers + equity curves + volume.

## Refresh Mode (`--refresh`)
1. Re-download fresh data
2. Load previous `{ticker}_results.csv`
3. Re-run ALL existing strategies on new data
4. Compare old vs new (IMPROVING/STABLE/DECAYING/FAILING)
5. Update Pine Scripts if top 3 changed
6. Regenerate HTML dashboard
7. Save refresh history to `{ticker}_refresh_log.csv`

## Key Technical Notes
- `crossunder` NOT in backtesting.lib — use `crossover(b, a)` instead
- Define indicator functions OUTSIDE the Strategy class
- Use `self.I()` to wrap all indicator functions in `init()`
- 200 SMA regime filter helps TREND FOLLOWING but HURTS MEAN REVERSION
- Polygon data is timezone-naive after `fetch_data()`
- yfinance fallback data still needs `tz_localize(None)` — handled in `fetch_yfinance_ohlcv()`

---

# ═══════════════════════════════════════════════════════════
#  SUB-COMMAND 5: STRATEGY SIGNAL
# ═══════════════════════════════════════════════════════════

## Trigger
"strategy signal TICKER", "what does the strategy say", "strategy state", "is the strategy in a trade", "ride the rally", "catch dips", "play safe"

## Invocation

```
/financial-analysis signal TICKER [INTENT]
```

### Intent Keywords

| Intent | Keywords | Strategy Type |
|--------|----------|--------------|
| ride_rally | `ride`, `rally`, `trend`, `momentum`, `bull` | Trend-following |
| catch_dips | `dips`, `dip`, `oversold`, `bounce`, `mean reversion` | Mean-reversion |
| play_safe | `safe`, `conservative`, `careful`, `protect`, `defensive` | Regime-filtered mean-reversion |
| balanced | `balanced`, `hybrid`, `moderate`, `mix` | Hybrid trend+reversion |

If no intent keyword is detected, run regime detection and recommend accordingly.

## Workflow

### Step 1: Load Strategy Registry
Read `$SKILL_DIR/strategy_lab/strategy_registry.json`. If ticker isn't in registry, fall back to `{ticker_lower}_daily_strategies/` or `{ticker_lower}_strategies/`.

### Step 2: Download Fresh Data
yfinance: `period='max', interval='1d'`. Update CSV so strategy scripts can load it.

### Step 3: Pre-Signal Gates (Macro + Sentiment + Options)

**Run ALL THREE BEFORE any strategy signals.**

```bash
cd "$SKILL_DIR/market_intel" && python3 macro_monitor.py --json
cd "$SKILL_DIR/market_intel" && python3 sentiment_scanner.py --json
cd "$SKILL_DIR/market_intel" && python3 options_analyzer.py TICKER --json
```

Parse all three JSON outputs. Key fields:
- Macro: `risk_level` (GREEN/YELLOW/RED)
- Sentiment: `sentiment_score` (0-100), `sentiment_label`
- Options: `key_levels.support`, `key_levels.resistance`, `key_levels.max_pain`, `key_levels.gex_flip`, `gex.total_gex`, `dex.total_dex`, `options_sentiment.score`, `options_sentiment.label`

### Options Quick Reference

| Metric | Meaning | How to use |
|--------|--------|------------|
| GEX positive | Dealers long gamma → buy dips, sell rips → range-bound | Favor mean-reversion, tighter targets |
| GEX negative | Dealers short gamma → momentum amplified | Favor trend-following, wider stops |
| GEX flip strike | Above = pinned, below = runs | Watch for regime change near flip |
| Max pain | Magnet near expiry | 1-3 day directional bias |
| Put OI walls | Support (dealers buy to hedge puts) | Stop-loss reference |
| Call OI walls | Resistance (dealers sell to hedge calls) | Profit target |
| DEX positive | Dealers net long shares → supportive | Confirms bullish setups |
| DEX negative | Dealers net short shares → pressure | Confirms bearish setups |

### Combined Gating Logic

| Macro | Sentiment | Strategy says BUY | Strategy says FLAT |
|-------|-----------|-------------------|-------------------|
| GREEN | NEUTRAL | Full send | Wait for entry |
| GREEN | EXTREME GREED | Reduce size 50% — contrarian top risk | No urgency |
| GREEN | EXTREME FEAR | Conviction entry — contrarian tailwind | Watch closely — buy zone |
| GREEN | GREED | Normal size | No urgency |
| GREEN | FEAR | Extra conviction | Getting interesting |
| YELLOW | any | Half position | No urgency |
| RED | any | Skip entry | Stay out |

### Options Overlay on Gate Decision

| Options Context | Modifier |
|-----------------|----------|
| Price near put OI wall + GEX positive | Strengthens BUY |
| Price near call OI wall + GEX positive | Weakens BUY |
| Price below GEX flip + GEX negative | Risk amplified |
| Above max pain near expiry (< 3 days) | Bearish gravity |
| Below max pain near expiry (< 3 days) | Bullish gravity |
| Options sentiment diverges from market sentiment | Flag it — options flow is smarter money |

**If any gate check fails**: Skip gracefully, print "Macro/Sentiment/Options check unavailable — proceeding with strategy signals only."

### Step 4: Market Regime Detection
Compute from downloaded data using talib (EMA 8/21/55, ADX 14, SMA 200, 60-bar momentum).

| Regime | Conditions | Default Intent |
|--------|-----------|----------------|
| STRONG UPTREND | ema_bullish AND adx > 25 AND above_sma200 | ride_rally |
| MILD UPTREND | above_sma200 AND (not ema_bullish OR adx <= 25) | balanced |
| SIDEWAYS | adx < 20 AND price within 5% of SMA 200 | catch_dips |
| DOWNTREND | ema_bearish AND NOT above_sma200 | play_safe |

### Steps 5-8: Match → Run → Output → Detail
Match intent → strategy. Run all 4 intent strategies on full dataset using backtesting.py. Capture final state. Print formatted dashboard (header, intent, matched strategy, position state, options key levels, recent trades, other strategies, Pine Script, stats).

---

# ═══════════════════════════════════════════════════════════
#  SUB-COMMAND 6: QUICK LOOK
# ═══════════════════════════════════════════════════════════

## Trigger
"quick look TICKER", "scan ticker", "what do indicators say", fast overview before committing to full evolution

## Invocation
```
/financial-analysis look TICKER [TIMEFRAME]
```
Timeframes: `1h` (default), `daily`/`1d`, `weekly`/`1wk`

## Workflow

1. Download fresh yfinance data in-memory (don't save CSV)
2. Run all key indicators: EMA Ribbon (8/21/55), SuperTrend (10, 3.0), SMA 50/200, RSI (14), MACD, StochRSI, BB (20, 2), KC (20, 2), ATR (14), ADX (14), +DI / -DI
3. Score each indicator +1 / 0 / -1. Total score -10 to +10
4. Output: snapshot label, score, indicator breakdown, strategy cross-reference (if evolved), triage summary ("worth evolving?")

## Key Technical Notes
- Use talib for all indicators
- yfinance interval="1h" for intraday, "1d" for daily
- Handle timezone: `pd.to_datetime(data.index, utc=True).tz_localize(None)`
- SuperTrend must be calculated manually (not in talib)
- Keep ephemeral and fast — no CSV writes

---

# ═══════════════════════════════════════════════════════════
#  SUB-COMMAND 7: 禅動 ANALYSIS (AUTOMATED)
# ═══════════════════════════════════════════════════════════

## Trigger
"禅動 TICKER", "chandong TICKER", "chandong TICKER INTERVAL", "analyze TICKER"

## Overview

Automated 禅動 (Chandong) signal analysis. **Primary path** uses a Discord bot via Playwright — requires `CHANDONG_DISCORD_URL` env var pointing at a channel where a `/chart` slash command is available. **Fallback** runs local Python analysis via `chandong_analyzer.py`. If `CHANDONG_DISCORD_URL` is unset or the bot times out, the skill silently falls back to local analysis.

## Invocation

```
chandong NVDA            # Daily chart (default), Discord bot if configured
chandong NVDA 30         # 30-minute chart
chandong NVDA --local    # Skip Discord, run local analysis
```

## Workflow

### Step 0: Parse Input
Extract TICKER, INTERVAL (default `D`), MODE (`--local` / `--offline` → skip Discord).

### Step 1: Macro + Sentiment Gate
```bash
cd "$SKILL_DIR/market_intel" && python3 macro_monitor.py --json
cd "$SKILL_DIR/market_intel" && python3 sentiment_scanner.py --json
```

### Step 2: Route — Discord or Local
- `--local` / `--offline` flag → skip to Step 8
- `CHANDONG_DISCORD_URL` unset → skip to Step 8
- Otherwise → Discord bot workflow (Steps 3-7)

### Step 3: Open Discord in Browser
Use Playwright MCP: `browser_navigate → $CHANDONG_DISCORD_URL`

### Step 4: Handle Auth
Snapshot to check page state:
- Login page → tell user "Discord login required. Please log in manually. Say 'ready' when done."
- Logged in → proceed
- CAPTCHA / 2FA → ask user to complete it manually

### Step 5: Send /chart Command
Discord's message input is a contenteditable `<div>`:
1. Click message input
2. Type `/chart` and wait 1-2s for autocomplete
3. Snapshot to verify popup
4. Click the bot's `/chart` option
5. Fill `symbol` and `interval` fields (Tab between them)
6. Press Enter to submit

### Step 6: Wait for Bot Response
Poll for new message with an image. Wait 5s, snapshot. Repeat up to 6 times (30s timeout). If timeout, fall back to local.

### Step 7: Screenshot and Interpret
Click chart to enlarge (lightbox), `browser_take_screenshot`, read signal labels (b1/b2/b3/s?/s1/s2), oscillator values, EMA positions, Fib levels, trend structure. Close lightbox.

Set `source = "Discord Bot"`. Skip to Step 9.

### Step 8: Local Analysis (Fallback)

```bash
cd "$SKILL_DIR" && python3 chandong/chandong_analyzer.py TICKER --interval INTERVAL --json
```

Parse JSON: `signal_state`, `signal_price`, `bars_since_signal`, `rsx`, `lrsi`, `macd_hist`, `confluence_score`, `confluence_details`, `ema20`, `ema50`, `ema200`, `fib_levels`, `recent_signals`, `current_price`. Set `source = "Local Analysis"`.

### Step 9: Score Confluence and Build Dashboard

**Confluence (0-8 points):**
| Condition | Points |
|-----------|--------|
| At Fib 61.8% (Golden Pocket) | +2 |
| At Fib 50% | +1 |
| Inside Order Block | +2 |
| Inside FVG | +1 |
| Near EMA 200 | +1 |
| Multi-TF alignment | +1 |

**Confidence → Position Sizing:** 1-2: LOW (25%), 3-4: MEDIUM (50%), 5-6: HIGH (75%), 7-8: VERY HIGH (100%).

**Signal Reference:**
| Signal | Conditions | Action |
|--------|------------|--------|
| **b1** | RSX < 30 + LRSI < 0.2 + Near Fib support | Watch |
| **b2** | b1 confirmed + RSX crossing above 30 + MACD improving | Consider entry |
| **b3** | b2 confirmed + RSX > 50 + Above EMA 20 + Higher low | Full conviction |
| **s?** | RSX > 70 + LRSI > 0.8 | Tighten stops |
| **s1** | RSX > 75 turning down + Near Fib resistance | Reduce position |
| **s2** | s1 confirmed + RSX below 70 + MACD negative | Exit |

Apply combined macro+sentiment gating as in Sub-Command 5.

### Step 10: Output Dashboard
Print a formatted report: header (ticker, interval, price, macro, sentiment, source), latest signal & age, progression, oscillators, confluence with checkmarks, position sizing, gate-check decision, last 5 signals.

### Step 11: Save to Obsidian (optional)
If `OBSIDIAN_VAULT_PATH` is set, save to `$OBSIDIAN_VAULT_PATH/Daily Briefings/$DATE — 禅動 {TICKER}.md`.

## Error Handling

| Failure | Response |
|---------|----------|
| Playwright won't connect | "Browser unavailable. Running local analysis." → Step 8 |
| `CHANDONG_DISCORD_URL` unset | Silent fallback to local analysis |
| Discord login required | "Please log in to Discord. Say 'ready' when done." |
| Bot timeout (30s) | "Bot timed out. Running local analysis." → Step 8 |
| `chandong_analyzer.py` fails | "Local analysis failed: {error}. Check that talib and yfinance are installed." |
| Macro/sentiment scripts fail | Skip the gate, note "Gates unavailable" in output |

## Files
- **Discord automation**: This SKILL.md workflow (Playwright MCP)
- **Local fallback**: `$SKILL_DIR/chandong/chandong_analyzer.py`
- **Development plan**: `$SKILL_DIR/chandong/Phase4_禅动Pro_Development_Plan.md`

---

# ═══════════════════════════════════════════════════════════
#  SUB-COMMAND 8: OPTIONS ANALYSIS
# ═══════════════════════════════════════════════════════════

## Trigger
"options analysis TICKER", "options flow", "GEX", "gamma exposure", "max pain", "put call ratio", "IV skew", "dealer positioning", "options sentiment", "OI walls"

## Workflow

```bash
cd "$SKILL_DIR/market_intel" && python3 options_analyzer.py TICKER
cd "$SKILL_DIR/market_intel" && python3 options_analyzer.py            # batch — top watchlist tickers
cd "$SKILL_DIR/market_intel" && python3 options_analyzer.py TICKER --json
```

Optionally save to `$OBSIDIAN_VAULT_PATH/Daily Briefings/$DATE — Options {TICKER}.md`.

## Data Sources
| Source | Data | Auth |
|--------|------|------|
| Yahoo Finance (yfinance) | Option chains, IV, OI, volume, spot | No auth |
| FRED API | 2Y Treasury yield (B-S risk-free rate) | `FRED_API_KEY` |
| Polygon.io | Contract-level prev close (cross-verification) | `POLYGON_API_KEY` |
| scipy | Black-Scholes greeks | Local |

## 9 Analysis Dimensions
1. Put/Call Ratio — Volume & OI
2. IV Skew — OI-weighted put vs call IV
3. Max Pain — Strike where option holders lose most
4. GEX — Net dealer gamma exposure
5. DEX — Net dealer delta exposure
6. OI Walls — Highest OI strikes
7. Options Sentiment — Composite 0-100
8. Key Levels — Support/resistance/flip
9. Cross-Verification — Polygon vs Yahoo

## Sentiment Score (0-100)
- **75-100**: STRONG BULLISH
- **60-74**: LEANING BULLISH
- **40-59**: NEUTRAL
- **25-39**: LEANING BEARISH
- **0-24**: STRONG BEARISH

## Chart Output
Saved to `strategy_lab/{ticker}_options_chart.html` — interactive Plotly with GEX by strike, OI distribution, IV smile.

---

# ═══════════════════════════════════════════════════════════
#  SUB-COMMAND 9: PORTFOLIO CHECK + XLSX REPORT
# ═══════════════════════════════════════════════════════════

## Trigger
"fcn check", "fcn status", "portfolio check", "portfolio report", "structured products", "are my fcns safe", "sell puts", "accumulators"

## Setup (first time only)

The portfolio sub-command reads from `market_intel/portfolio_data.json`. **This file is gitignored** — you create it yourself by copying the template:

```bash
cp "$SKILL_DIR/market_intel/portfolio_data.template.json" "$SKILL_DIR/market_intel/portfolio_data.json"
# then edit portfolio_data.json with your real positions
```

Schema keys: `FCN_PORTFOLIO`, `FX_OPTIONS`, `SELL_PUTS`, `ACCUMULATORS`. Each entry follows the JSON schema documented below.

## Workflow

### Step 1: Run the Portfolio Checker
```bash
cd "$SKILL_DIR/market_intel" && python3 portfolio_checker.py
```

Covers: structured notes (active + autocalled), FX options, sell puts, accumulators, autocall (KO) proximity, ticker impact / blockers, portfolio summary.

### Step 2: Generate XLSX Report

```bash
cd "$SKILL_DIR/market_intel" && python3 generate_portfolio_xlsx.py
```

Options:
- `--output path.xlsx` — custom path (default: `$FINANCIAL_ANALYSIS_OUTPUT_DIR/Portfolio_Report_YYYY-MM-DD.xlsx`)
- `--json-file data.json` — use a pre-existing JSON instead of live data

### Step 3: Deliver
Send the .xlsx to the user.

### Template Management
- **Template**: `market_intel/templates/Portfolio_Report_Template.xlsx`
- **Style**: Executive Editorial (Rockwell headings, Georgia body, red accent)
- **Do NOT regenerate the template** — load and populate it
- **If template changes**: open in Excel, tweak, save back to the same path

### JSON Schema
- `structured_notes[]` — account, isin, product, amount, coupon, expiry, status, worst_performer, underlyings[]
- `sell_puts[]` — account, ticker, strike, current, buffer_pct, expiry, status
- `fx_options[]` — id, description, notional, spot_strike, buffer, expiry
- `accumulators[]` — account, description, strike_call, current, buffer_pct, expiry, status
- `blockers[]` — ticker, blocks, exposure, avg_gap

---

# ═══════════════════════════════════════════════════════════
#  SUB-COMMAND 10: COT (CFTC SMART-MONEY) REPORT
# ═══════════════════════════════════════════════════════════

## Trigger
"cot", "cot update", "cot report", "weekly cot", "smart money", "smart money scan", "hedge fund positioning", "cftc", "cftc data", "get cot data"

## Overview
Weekly workflow: pull fresh CFTC Commitments of Traders data, generate the interactive HTML report. Cadence: CFTC publishes Tuesday snapshot on Friday ~3:30pm ET.

## Data Source
`cot_tracker.py` and `generate_cot_html_report.py` pull directly from the CFTC public archive — no API key:

| Report | URL |
|--------|-----|
| Traders in Financial Futures (BTC, S&P, NDX, EUR, 10Y) | `https://www.cftc.gov/files/dea/history/fut_fin_txt_{year}.zip` |
| Disaggregated (Gold, Crude Oil) | `https://www.cftc.gov/files/dea/history/fut_disagg_txt_{year}.zip` |

Hedge-fund (Managed Money) net positioning + week-over-week delta for: Bitcoin, S&P 500, Nasdaq 100, Gold, Crude Oil, Euro FX, 10Y Treasury.

## Workflow

### Step 1: Generate HTML report
```bash
cd "$SKILL_DIR/market_intel" && python3 generate_cot_html_report.py
```
Writes to `$FINANCIAL_ANALYSIS_OUTPUT_DIR/COT_Smart_Money_Report.html`. Self-contained Chart.js page.

### Step 2 (optional): Publish to your own host
The HTML is fully self-contained — drop it on any static host (Vercel, Netlify, GitHub Pages, S3, plain nginx). Configure your own deploy path; this skill no longer ships any specific deployment wiring.

### Step 3 (optional): Text-only scan for daily-briefing reuse
If invoked as part of the Daily Briefing (Sub-Command 1, Step 1.5):
```bash
cd "$SKILL_DIR/market_intel" && python3 cot_tracker.py --json
```

## Template Management
- **Template**: `market_intel/generate_cot_html_report.py` builds the HTML inline (no external template). Styling, Chart.js config, and commentary all live in that script.
- **Never edit the generated `.html` by hand** — re-run the generator after editing the script.

## Failure Modes
| Failure | Response |
|---------|----------|
| CFTC archive 404 (release not out yet) | "CFTC hasn't published this week's snapshot yet, try after Friday 3:30pm ET" |
| Network error | Retry once, then surface error |

---

# ═══════════════════════════════════════════════════════════
#  SHARED: KEY TECHNICAL NOTES
# ═══════════════════════════════════════════════════════════

## Python Dependencies
- tradingview-ta, tradingview-screener, beautifulsoup4
- backtesting (backtesting.py)
- talib (TA-Lib)
- yfinance
- pandas, numpy, scipy
- plotly (for interactive HTML charts)
- polygon-api-client (optional, for Polygon.io)
- openpyxl (for XLSX reports)
- python-docx (optional, for DOCX COT report)

See `requirements.txt` for pinned versions.

## backtesting.py Notes
- `crossunder` NOT in backtesting.lib — use `crossover(b, a)` instead
- Always use `self.I()` to wrap indicator functions
- Define indicator functions OUTSIDE the Strategy class
- Use `exclusive_orders=True` to prevent conflicting orders
- Cash sizing: >$100 stock = $1M, $10-100 = $100K, <$10 = $10K

## Known Pitfalls
- Too many entry filters = 0 trades (keep max 3 conditions)
- VWAP with integer volume can cause NaN errors — cast to float first
- Polygon data is timezone-naive after `fetch_data()`
- yfinance fallback data needs `tz_localize(None)` — handled in `utils.py`
- Cross-verification tolerance of 0.5 for rounding between talib and Polygon
- If Polygon API key missing, all functions silently fall back to yfinance
