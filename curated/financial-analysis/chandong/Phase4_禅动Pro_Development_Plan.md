# Phase 4: 禅动 Pro Indicator Development Plan
## Custom Buy/Sell Signal System for TradingView

**Version:** 1.1
**Created:** 2026-02-03
**Status:** Parameters Finalized - Ready for Development

---

## FINALIZED DECISIONS (Senior Analyst - 2026-02-03)

| Parameter | Decision | Rationale |
|-----------|----------|-----------|
| RSX Oversold | **30** | Standard threshold; 25 too restrictive |
| Laguerre Alpha | **0.7** | Proven; 0.6 too noisy |
| Min Confluence for b1 | **≥ 2 points** | Filters low-quality signals |
| Order Blocks/FVG | **Show (toggle ON)** | Valuable context; user can disable |
| Info Table | **Top-right corner** | Essential quick reference |
| Divergence Lookback | **10 bars** | Conservative; fewer false signals |
| Alerts | **b2+, s1+ only** | Exception: High-confluence b1 (≥4) |

---

## PROJECT OVERVIEW

### Objective
Build a proprietary buy/sell signal indicator that:
- Mimics 禅动's visual style (b1/b2/b3 buy, s1/s2/s? sell labels)
- Combines mathematically superior oscillators (Jurik RSX, Laguerre RSI)
- Adds Fibonacci confluence detection
- Integrates Smart Money Concepts (Order Blocks, FVG)
- Generates Daily chart alerts for stocks (primary) and crypto (secondary)

### Design Philosophy
1. **Mimic 禅动 Visual Style** - Same label format, similar colors
2. **Mathematical Rigor** - Use Ehlers/Jurik algorithms, not folklore
3. **Multi-Confirmation** - Signal only when multiple conditions align
4. **Daily Timeframe Focus** - Optimized for swing trading

---

## PART 1: AGENT SKILLS MASTERY INTEGRATION

### Skills to Master from Zkalish/agent-skills

#### 1. pinescript-v6-uzmani (Pine Script V6 Expert)
**Key Concepts to Integrate:**
- `//@version=6` declaration
- `series` type for time-based data (CRITICAL)
- `ta.` namespace functions (RSI, MACD, ATR, crossover)
- `plotshape()` for signal labels
- `alertcondition()` for notifications
- Custom `type` structures for signal data
- `request.security()` for multi-timeframe confirmation

#### 2. chart-patterns-uzmani (Chart Patterns Expert)
**Key Patterns to Detect:**
- Double Top/Bottom (reversal signals)
- Flags and Pennants (continuation)
- Triangles (breakout)
- Head & Shoulders (major reversal)

#### 3. price-action-uzmani (Price Action Expert)
**Smart Money Concepts to Integrate:**
- Order Block detection (institutional zones)
- FVG (Fair Value Gap) identification
- BOS (Break of Structure)
- CHoCH (Change of Character)
- Liquidity sweep detection

#### 4. hisse-analiz-uzmani (Stock Analysis Expert)
**Analysis Framework:**
- 8-dimension weighted scoring
- Momentum analysis (RSI, volume)
- Risk assessment protocols

---

## PART 2: 禅动 PRO SIGNAL LOGIC

### Signal Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    禅动 PRO SIGNAL ENGINE                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  INPUT LAYER (Oscillators)                                   │
│  ├── Jurik RSX (14) ──────────────────┐                     │
│  ├── Laguerre RSI (0.7) ──────────────┼──► SIGNAL           │
│  ├── Ehlers Stochastic ───────────────┤    PROCESSOR        │
│  └── MACD Histogram ──────────────────┘                     │
│                                                              │
│  CONFLUENCE LAYER                                            │
│  ├── Fibonacci Level Detection ───────┐                     │
│  ├── Order Block Proximity ───────────┼──► CONFLUENCE       │
│  ├── FVG (Fair Value Gap) ────────────┤    SCORE (0-5)      │
│  └── EMA 20/50/200 Position ──────────┘                     │
│                                                              │
│  OUTPUT LAYER                                                │
│  ├── b1/b2/b3 Buy Signals ────────────┐                     │
│  ├── s?/s1/s2 Sell Signals ───────────┼──► CHART LABELS    │
│  ├── Divergence Warnings ─────────────┤    + ALERTS         │
│  └── Confidence Score ────────────────┘                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Buy Signal Logic (b1 → b2 → b3 Progression)

#### b1 (Initial Buy Signal)
**Conditions (ALL must be true):**
```
1. Jurik RSX < 30 (oversold)
2. Laguerre RSI < 0.2 (oversold)
3. Price near support (Fib 50%, 61.8%, or Order Block)
4. No active s1/s2 signal in last 5 bars
```
**Confluence Boost:**
- At Fib 61.8% (Golden Ratio): +1 confidence
- Inside FVG: +1 confidence
- Near Order Block: +1 confidence

#### b2 (Confirmation Buy Signal)
**Conditions (following b1):**
```
1. b1 fired within last 10 bars
2. Jurik RSX crosses above 30 (leaving oversold)
3. Laguerre RSI crosses above 0.2
4. MACD histogram turning positive OR less negative
5. Price holding above b1 level
```

#### b3 (Strong Buy Signal)
**Conditions (following b2):**
```
1. b2 fired within last 10 bars
2. Jurik RSX > 50 (momentum confirmed)
3. Laguerre RSI > 0.5
4. MACD histogram positive and increasing
5. Price above EMA 20
6. Higher low confirmed (structure bullish)
```

### Sell Signal Logic (s? → s1 → s2 Progression)

#### s? (预警 - Warning Signal)
**Conditions:**
```
1. Jurik RSX > 70 (overbought territory)
2. Laguerre RSI > 0.8
3. Price extended from EMA 20 by > 5%
4. NOT YET a confirmed sell
```
**Purpose:** Alert user to watch for reversal, not actionable alone

#### s1 (Initial Sell Signal)
**Conditions (ALL must be true):**
```
1. Jurik RSX > 75 AND turning down
2. Laguerre RSI > 0.8 AND turning down
3. Price near resistance (Fib 23.6%, 38.2%, or Order Block)
4. Bearish divergence detected (price higher, RSX lower)
```
**Divergence Detection:**
- Compare current high vs high 5-10 bars ago
- If price higher but RSX lower → "Bear Div" label

#### s2 (Confirmed Sell Signal)
**Conditions (following s1):**
```
1. s1 fired within last 10 bars
2. Jurik RSX crosses below 70 (leaving overbought)
3. MACD histogram turning negative
4. Price breaks below recent swing low
5. Lower high confirmed (structure bearish)
```

---

## PART 3: FIBONACCI CONFLUENCE MODULE

### Auto-Detection Logic

```pine
// Detect swing points for Fib calculation
swingHigh = ta.pivothigh(high, 10, 10)
swingLow = ta.pivotlow(low, 10, 10)

// Calculate Fib levels from most recent swing
fibRange = swingHigh - swingLow
fib236 = swingHigh - (fibRange * 0.236)
fib382 = swingHigh - (fibRange * 0.382)
fib500 = swingHigh - (fibRange * 0.500)
fib618 = swingHigh - (fibRange * 0.618)
fib786 = swingHigh - (fibRange * 0.786)

// Check if price is near key Fib level
nearFib618 = math.abs(close - fib618) / close < 0.02  // within 2%
nearFib500 = math.abs(close - fib500) / close < 0.02
```

### Confluence Scoring

| Condition | Points |
|-----------|--------|
| At Fib 61.8% (Golden) | +2 |
| At Fib 50% | +1 |
| At Fib 38.2% | +1 |
| Inside Order Block | +2 |
| Inside FVG | +1 |
| EMA 200 support | +1 |
| **Total Possible** | **8** |

**Signal Strength:**
- 1-2 points: Low confidence (small position)
- 3-4 points: Medium confidence (normal position)
- 5+ points: High confidence (full position)

---

## PART 4: SMART MONEY CONCEPTS MODULE

### Order Block Detection

```pine
// Bullish Order Block (last down candle before up move)
bullishOB = close[1] < open[1] and  // Previous candle bearish
            close > open and         // Current candle bullish
            close > high[1]          // Broke above previous high

// Store Order Block zone
var float obHigh = na
var float obLow = na
if bullishOB
    obHigh := high[1]
    obLow := low[1]
```

### Fair Value Gap (FVG) Detection

```pine
// Bullish FVG: Gap between candle 1 high and candle 3 low
bullishFVG = low > high[2]  // Current low above 2-bars-ago high
fvgTop = low
fvgBottom = high[2]

// Price inside FVG
insideFVG = close <= fvgTop and close >= fvgBottom
```

### Break of Structure (BOS)

```pine
// Bullish BOS: Price breaks above recent swing high
recentSwingHigh = ta.highest(high, 20)[1]  // Exclude current bar
bullishBOS = close > recentSwingHigh and close[1] <= recentSwingHigh
```

---

## PART 5: VISUAL DESIGN (Mimicking 禅动)

### Color Scheme

| Element | Color | Hex Code |
|---------|-------|----------|
| Buy Signals (b1/b2/b3) | Green | #00E676 |
| Sell Warning (s?) | Yellow | #FFEB3B |
| Sell Signals (s1/s2) | Red | #FF5252 |
| Bear Divergence | Pink | #FF80AB |
| Order Block (Bull) | Blue (transparent) | #2196F380 |
| Order Block (Bear) | Orange (transparent) | #FF980080 |
| FVG Zone | Purple (transparent) | #9C27B040 |

### Label Style

```pine
// Buy signal label (mimicking 禅动 style)
if b1Signal
    label.new(bar_index, low, "b1",
              style=label.style_label_up,
              color=color.new(#00E676, 0),
              textcolor=color.white,
              size=size.small)

// Sell signal with divergence
if s1Signal and bearishDivergence
    label.new(bar_index, high, "s1\nBear Div",
              style=label.style_label_down,
              color=color.new(#FF5252, 0),
              textcolor=color.white,
              size=size.small)
```

### Info Table (Top Right)

```
┌──────────────────────────────┐
│ 禅动 PRO v1.0                 │
├──────────────────────────────┤
│ RSX: 45.2 ■                  │
│ LRSI: 0.52 ■                 │
│ Confluence: 4/8 ★★★★☆       │
│ Last Signal: b2 @ $85.50    │
│ Trend: BULLISH ▲            │
└──────────────────────────────┘
```

---

## PART 6: ALERT SYSTEM

### Alert Conditions

```pine
// Buy Alerts
alertcondition(b1Signal, title="禅动 Pro: b1 Buy",
    message="{{ticker}} - b1 Buy Signal at {{close}}\nConfluence: {{plot_0}}/8")

alertcondition(b2Signal, title="禅动 Pro: b2 Buy Confirm",
    message="{{ticker}} - b2 Buy Confirmed at {{close}}")

alertcondition(b3Signal, title="禅动 Pro: b3 Strong Buy",
    message="{{ticker}} - b3 STRONG BUY at {{close}}")

// Sell Alerts
alertcondition(sWarning, title="禅动 Pro: s? Warning",
    message="{{ticker}} - ⚠️ Sell Warning at {{close}}")

alertcondition(s1Signal, title="禅动 Pro: s1 Sell",
    message="{{ticker}} - s1 Sell Signal at {{close}}")

alertcondition(s2Signal, title="禅动 Pro: s2 Confirmed Sell",
    message="{{ticker}} - s2 CONFIRMED SELL at {{close}}")

// Special Alerts
alertcondition(bearishDivergence, title="禅动 Pro: Bearish Divergence",
    message="{{ticker}} - ⚠️ BEARISH DIVERGENCE detected")

alertcondition(highConfluence, title="禅动 Pro: High Confluence",
    message="{{ticker}} - 🎯 HIGH CONFLUENCE (5+/8) at {{close}}")
```

---

## PART 7: DEVELOPMENT TASKS CHECKLIST

### Task 1: Core Oscillator Implementation
```
[ ] 1.1 Implement Jurik RSX (from everget repo)
[ ] 1.2 Implement Laguerre RSI (from everget repo)
[ ] 1.3 Implement Ehlers Stochastic (from everget repo)
[ ] 1.4 Add standard MACD
[ ] 1.5 Create unified oscillator panel display
```

### Task 2: Signal Engine
```
[ ] 2.1 Implement b1 buy signal logic
[ ] 2.2 Implement b2 buy confirmation logic
[ ] 2.3 Implement b3 strong buy logic
[ ] 2.4 Implement s? warning logic
[ ] 2.5 Implement s1 sell signal logic
[ ] 2.6 Implement s2 confirmed sell logic
[ ] 2.7 Implement divergence detection (bullish/bearish)
[ ] 2.8 Add signal state tracking (prevent duplicate signals)
```

### Task 3: Fibonacci Module
```
[ ] 3.1 Implement swing high/low detection
[ ] 3.2 Calculate Fib retracement levels
[ ] 3.3 Detect price proximity to Fib levels
[ ] 3.4 Draw optional Fib lines on chart
[ ] 3.5 Add Fib level to confluence scoring
```

### Task 4: Smart Money Concepts
```
[ ] 4.1 Implement Order Block detection (bullish/bearish)
[ ] 4.2 Implement FVG detection (bullish/bearish)
[ ] 4.3 Implement BOS detection
[ ] 4.4 Implement CHoCH detection
[ ] 4.5 Draw SMC zones on chart
[ ] 4.6 Add SMC to confluence scoring
```

### Task 5: Visual Design
```
[ ] 5.1 Create signal labels (禅动 style)
[ ] 5.2 Create info table (top right)
[ ] 5.3 Add oscillator panel with color coding
[ ] 5.4 Draw support/resistance zones
[ ] 5.5 Add confluence score display
[ ] 5.6 Test visual clarity on multiple symbols
```

### Task 6: Alert System
```
[ ] 6.1 Create alertcondition() for all signals
[ ] 6.2 Format alert messages with key data
[ ] 6.3 Test alerts on TradingView
[ ] 6.4 Document alert setup instructions
```

### Task 7: Testing & Optimization (COMPREHENSIVE BACKTESTING)

#### 7.1 Backtesting Methodology

**Approach:** Walk-Forward Analysis (not curve-fitting)
- Split data: 70% training / 30% validation
- Optimize on training, verify on validation
- If validation fails, reject optimization

**Test Periods:**
| Period | Market Condition | Purpose |
|--------|------------------|---------|
| 2023 Q1-Q2 | Recovery rally | Test buy signals in uptrend |
| 2023 Q3-Q4 | Consolidation | Test range-bound behavior |
| 2024 Q1-Q2 | Bull market | Test sell warnings at tops |
| 2024 Q3-Q4 | Volatility spike | Test divergence detection |
| 2025 Full Year | Mixed conditions | Final validation |
| 2026 Jan-Feb | Current (out-of-sample) | Real-time verification |

#### 7.2 Test Assets

**Stocks (Primary):**
```
[ ] HOOD - High beta growth stock (our main use case)
[ ] AU - Gold miner, commodity-linked
[ ] AAPL - Large cap, liquid, benchmark
[ ] TSLA - High volatility, tests extreme conditions
[ ] NVDA - Momentum stock, tests trend following
```

**Crypto (Secondary):**
```
[ ] BTC - Primary crypto benchmark
[ ] ETH - Secondary crypto
[ ] SOL - Higher volatility alt
```

#### 7.3 Performance Metrics to Track

**Signal Quality Metrics:**
| Metric | Target | Failure Threshold |
|--------|--------|-------------------|
| Win Rate (b2/b3 signals) | ≥ 55% | < 45% |
| Win Rate (s1/s2 signals) | ≥ 55% | < 45% |
| Avg Winner / Avg Loser | ≥ 1.5:1 | < 1:1 |
| Profit Factor | ≥ 1.3 | < 1.0 |
| Max Consecutive Losses | ≤ 5 | > 8 |

**Confluence Validation:**
| Confluence Score | Expected Win Rate |
|------------------|-------------------|
| 1-2 (Low) | 45-50% |
| 3-4 (Medium) | 55-60% |
| 5-6 (High) | 65-70% |
| 7-8 (Very High) | 70-75% |

*If high confluence doesn't outperform low confluence, scoring system needs recalibration.*

**Signal Timing:**
| Metric | Target |
|--------|--------|
| Avg bars from b1 to bottom | < 5 bars |
| Avg bars from s1 to top | < 5 bars |
| False signal rate | < 30% |

#### 7.4 Backtesting Checklist

```
[ ] 7.4.1 Build Pine Script strategy version (for TradingView backtester)
[ ] 7.4.2 Run on HOOD 2023-2025 Daily
[ ] 7.4.3 Run on AU 2023-2025 Daily
[ ] 7.4.4 Run on AAPL 2023-2025 Daily
[ ] 7.4.5 Run on BTC 2023-2025 Daily
[ ] 7.4.6 Collect performance metrics for each
[ ] 7.4.7 Compare confluence score vs actual outcomes
[ ] 7.4.8 Identify parameter adjustments needed
[ ] 7.4.9 Re-test with adjusted parameters
[ ] 7.4.10 Validate on 2026 out-of-sample data
[ ] 7.4.11 Document final optimized settings
```

#### 7.5 Validation Criteria (Go/No-Go)

**PASS Criteria (ALL must be met):**
```
✓ Win rate ≥ 50% across all test assets
✓ Profit factor ≥ 1.2 on average
✓ High confluence (5+) outperforms low confluence (1-2) by ≥ 10%
✓ Works on BOTH stocks and crypto (no asset-specific failure)
✓ 2026 out-of-sample results within 10% of backtest
```

**FAIL Actions:**
```
If win rate < 45%:
  → Tighten signal conditions (raise RSX threshold)
  → Add more confluence requirements

If profit factor < 1.0:
  → Extend signal confirmation (b2 requires more conditions)
  → Review divergence detection logic

If confluence scoring ineffective:
  → Recalibrate point weights
  → Add/remove confluence factors

If stock/crypto divergence:
  → Create asset-specific parameter presets
  → Document differences in SKILL.md
```

#### 7.6 Deliverables After Backtesting

```
[ ] Performance summary table (all assets, all periods)
[ ] Optimal parameter settings (documented)
[ ] Confluence score validation report
[ ] Known limitations and edge cases
[ ] Recommended use cases (when indicator works best)
[ ] Warning scenarios (when to be cautious)
```

### Task 8: Integration with Existing Workflow
```
[ ] 8.1 Update Financial Analysis SOP with 禅动 Pro steps
[ ] 8.2 Update SKILL.md with 禅动 Pro section
[ ] 8.3 Update HTML report template for 禅动 Pro data
[ ] 8.4 Create screenshot/extraction protocol
[ ] 8.5 Document confluence with existing 禅动 signals
```

---

## PART 8: SKILL.md INTEGRATION PLAN

### New Capabilities to Add

```markdown
## 禅动 Pro Integration (Custom Indicator)

### Features
- Jurik RSX + Laguerre RSI (superior oscillators)
- b1/b2/b3 buy signal progression
- s?/s1/s2 sell signal progression
- Fibonacci confluence detection
- Smart Money Concepts (Order Blocks, FVG, BOS)
- 8-point confluence scoring system

### Signal Interpretation
| Signal | Meaning | Action |
|--------|---------|--------|
| b1 | Initial oversold bounce | Watch for confirmation |
| b2 | Confirmed momentum shift | Consider entry |
| b3 | Strong bullish momentum | Full conviction entry |
| s? | Overbought warning | Tighten stops |
| s1 | Initial reversal signal | Reduce position |
| s2 | Confirmed distribution | Exit position |

### Confluence Score
- 1-2: Low confidence (25% position)
- 3-4: Medium confidence (50% position)
- 5-6: High confidence (75% position)
- 7-8: Very high confidence (100% position)
```

---

## APPENDIX A: PINE SCRIPT V6 CODE SKELETON

```pine
//@version=6
indicator("禅动 Pro v1.0", overlay=true, max_labels_count=500)

// ============================================================================
// INPUTS
// ============================================================================

// ============================================================================
// FINALIZED PARAMETERS (Senior Analyst Decisions - 2026-02-03)
// ============================================================================

// Oscillator Settings
i_rsxLength = input.int(14, "RSX Length", minval=1)
i_lrsiAlpha = input.float(0.7, "Laguerre RSI Alpha", minval=0.1, maxval=0.99)  // Standard, not 0.6 (too noisy)
i_stochLength = input.int(14, "Ehlers Stochastic Length", minval=1)

// Signal Settings (DECISION: Standard thresholds, proven reliability)
i_oversoldRSX = input.int(30, "RSX Oversold Level", minval=1, maxval=50)   // 30 not 25 (catches more valid reversals)
i_overboughtRSX = input.int(70, "RSX Overbought Level", minval=50, maxval=99)

// Confluence Settings (DECISION: Require minimum 2 points for b1)
i_minConfluence = input.int(2, "Minimum Confluence for b1", minval=0, maxval=5)
i_highConfluence = input.int(4, "High Confluence Threshold", minval=3, maxval=8)  // For special alerts
i_fibTolerance = input.float(2.0, "Fib Level Tolerance %", minval=0.5, maxval=5.0)

// Visual Settings (DECISION: Show with toggle, default ON)
i_showOB = input.bool(true, "Show Order Blocks")
i_showFVG = input.bool(true, "Show Fair Value Gaps")
i_showTable = input.bool(true, "Show Info Table")

// Divergence Settings (DECISION: 10 bars conservative lookback)
i_divLookback = input.int(10, "Divergence Lookback Bars", minval=5, maxval=20)

// Alert Settings (DECISION: b2+, s1+ only, exception for high-confluence b1)
i_alertB1HighConf = input.bool(true, "Alert on High-Confluence b1 (≥4)")
i_alertB2 = input.bool(true, "Alert on b2")
i_alertB3 = input.bool(true, "Alert on b3")
i_alertS1 = input.bool(true, "Alert on s1")
i_alertS2 = input.bool(true, "Alert on s2")

// ============================================================================
// OSCILLATORS (from everget repo - will import actual code)
// ============================================================================

// Jurik RSX
rsx = 0.0  // TODO: Implement

// Laguerre RSI
lrsi = 0.0  // TODO: Implement

// Ehlers Stochastic
estoch = 0.0  // TODO: Implement

// MACD
[macdLine, signalLine, histLine] = ta.macd(close, 12, 26, 9)

// ============================================================================
// FIBONACCI MODULE
// ============================================================================

// Swing detection
swingHigh = ta.pivothigh(high, 10, 10)
swingLow = ta.pivotlow(low, 10, 10)

// TODO: Fib level calculations

// ============================================================================
// SMART MONEY CONCEPTS
// ============================================================================

// TODO: Order Block detection
// TODO: FVG detection
// TODO: BOS detection

// ============================================================================
// SIGNAL ENGINE
// ============================================================================

// State tracking
var int lastBuySignal = 0  // 0=none, 1=b1, 2=b2, 3=b3
var int lastSellSignal = 0  // 0=none, 1=s?, 2=s1, 3=s2
var int barsSinceLastBuy = 0
var int barsSinceLastSell = 0

// TODO: Signal logic

// ============================================================================
// VISUAL OUTPUT
// ============================================================================

// TODO: Labels, table, zones

// ============================================================================
// ALERTS
// ============================================================================

// TODO: alertcondition() calls
```

---

## REVISION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-03 | Initial Phase 4 development plan |

---

*This document defines the complete development plan for 禅动 Pro indicator.*
