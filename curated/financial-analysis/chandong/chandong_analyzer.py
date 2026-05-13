"""禅動 (Chandong) Local Signal Analyzer.

Ported from: chandong/禅动Pro_Strategy_v1.0.pine
Computes Jurik RSX, Laguerre RSI, MACD, Fibonacci, Order Blocks,
confluence scoring, and the b1/b2/b3/s?/s1/s2 signal state machine.

Usage:
    python3 chandong_analyzer.py NVDA                    # Daily, terminal output
    python3 chandong_analyzer.py NVDA --interval 30      # 30-min
    python3 chandong_analyzer.py NVDA --json             # JSON output
    python3 chandong_analyzer.py NVDA --interval W --json
"""

import argparse
import json
import sys
import os
from datetime import datetime

import numpy as np
import pandas as pd

# Add parent dir so we can import strategy_lab/utils.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "strategy_lab"))

try:
    import talib
except ImportError:
    talib = None


# ═══════════════════════════════════════════════════════════
#  OSCILLATORS — ported from Pine Script
# ═══════════════════════════════════════════════════════════

def jurik_rsx(src: np.ndarray, length: int = 14) -> np.ndarray:
    """Jurik RSX — smoother than RSI, less noise.

    Ported from Pine Script lines 56-97 of 禅动Pro_Strategy_v1.0.pine.
    Uses triple-smoothed momentum with absolute deviation normalization.
    """
    n = len(src)
    result = np.full(n, 50.0)

    f18 = 3.0 / (length + 2.0)
    f20 = 1.0 - f18

    # Smoothing state variables
    f8_prev = 0.0
    f28, f30 = 0.0, 0.0
    f38, f40 = 0.0, 0.0
    f48, f50 = 0.0, 0.0
    f58, f60 = 0.0, 0.0
    f68, f70 = 0.0, 0.0
    f78, f80 = 0.0, 0.0

    # Warmup period: need ~length bars for smoothing filters to stabilize
    warmup = length + 2

    for i in range(n):
        f8 = 100.0 * src[i]

        if i == 0:
            f8_prev = f8
            continue

        v8 = f8 - f8_prev
        f8_prev = f8

        # Triple-smoothed momentum (numerator path)
        f28 = f20 * f28 + f18 * v8
        f30 = f18 * f28 + f20 * f30
        vC = f28 * 1.5 - f30 * 0.5

        f38 = f20 * f38 + f18 * vC
        f40 = f18 * f38 + f20 * f40
        v10 = f38 * 1.5 - f40 * 0.5

        f48 = f20 * f48 + f18 * v10
        f50 = f18 * f48 + f20 * f50
        v14 = f48 * 1.5 - f50 * 0.5

        # Triple-smoothed absolute deviation (denominator path)
        v18 = abs(v8)
        f58 = f20 * f58 + f18 * v18
        f60 = f18 * f58 + f20 * f60
        v1C = f58 * 1.5 - f60 * 0.5

        f68 = f20 * f68 + f18 * v1C
        f70 = f18 * f68 + f20 * f70
        v1E = f68 * 1.5 - f70 * 0.5

        f78 = f20 * f78 + f18 * v1E
        f80 = f18 * f78 + f20 * f80
        v20 = f78 * 1.5 - f80 * 0.5

        # Output: ratio of smoothed momentum to smoothed deviation, scaled to 0-100
        if i >= warmup and v20 > 1e-10:
            v4 = (v14 / v20 + 1.0) * 50.0
        else:
            v4 = 50.0

        result[i] = min(max(v4, 0.0), 100.0)

    return result


def laguerre_rsi(src: np.ndarray, alpha: float = 0.7) -> np.ndarray:
    """Laguerre RSI — faster response to reversals.

    Ported from Pine Script lines 99-110.
    """
    n = len(src)
    result = np.zeros(n)

    L0, L1, L2, L3 = 0.0, 0.0, 0.0, 0.0

    for i in range(n):
        L0_prev, L1_prev, L2_prev = L0, L1, L2

        L0 = alpha * src[i] + (1 - alpha) * L0
        L1 = -(1 - alpha) * L0 + L0_prev + (1 - alpha) * L1
        L2 = -(1 - alpha) * L1 + L1_prev + (1 - alpha) * L2
        L3 = -(1 - alpha) * L2 + L2_prev + (1 - alpha) * L3

        CU = 0.0
        CD = 0.0
        CU += (L0 - L1) if L0 >= L1 else 0
        CU += (L1 - L2) if L1 >= L2 else 0
        CU += (L2 - L3) if L2 >= L3 else 0
        CD += (L1 - L0) if L0 < L1 else 0
        CD += (L2 - L1) if L1 < L2 else 0
        CD += (L3 - L2) if L2 < L3 else 0

        result[i] = CU / (CU + CD) if (CU + CD) != 0 else 0.0

    return result


# ═══════════════════════════════════════════════════════════
#  FIBONACCI & CONFLUENCE
# ═══════════════════════════════════════════════════════════

def detect_swings(high: np.ndarray, low: np.ndarray, length: int = 10):
    """Detect swing highs and lows using pivot detection."""
    n = len(high)
    swing_highs = []
    swing_lows = []

    for i in range(length, n - length):
        # Swing high: highest in window
        if high[i] == max(high[i - length:i + length + 1]):
            swing_highs.append((i, high[i]))
        # Swing low: lowest in window
        if low[i] == min(low[i - length:i + length + 1]):
            swing_lows.append((i, low[i]))

    return swing_highs, swing_lows


def compute_fib_levels(swing_high: float, swing_low: float):
    """Compute Fibonacci retracement levels."""
    fib_range = swing_high - swing_low
    return {
        "0.0": swing_high,
        "0.236": swing_high - fib_range * 0.236,
        "0.382": swing_high - fib_range * 0.382,
        "0.5": swing_high - fib_range * 0.5,
        "0.618": swing_high - fib_range * 0.618,
        "0.786": swing_high - fib_range * 0.786,
        "1.0": swing_low,
    }


def detect_order_blocks(open_arr: np.ndarray, close_arr: np.ndarray,
                        high_arr: np.ndarray, low_arr: np.ndarray):
    """Detect bullish order blocks (bearish candle followed by bullish engulfing)."""
    n = len(close_arr)
    ob_top = np.nan
    ob_bottom = np.nan

    for i in range(1, n):
        # Bullish OB: previous candle bearish, current bullish engulfing
        if close_arr[i - 1] < open_arr[i - 1] and close_arr[i] > open_arr[i] and close_arr[i] > high_arr[i - 1]:
            ob_top = high_arr[i - 1]
            ob_bottom = low_arr[i - 1]

    return ob_top, ob_bottom


def detect_fvg(high_arr: np.ndarray, low_arr: np.ndarray):
    """Detect Fair Value Gaps (bullish: gap between candle 1 high and candle 3 low)."""
    n = len(high_arr)
    fvg_top = np.nan
    fvg_bottom = np.nan

    for i in range(2, n):
        # Bullish FVG: candle[i] low > candle[i-2] high
        if low_arr[i] > high_arr[i - 2]:
            fvg_top = low_arr[i]
            fvg_bottom = high_arr[i - 2]

    return fvg_top, fvg_bottom


def compute_confluence(close: float, fib_levels: dict, ob_top: float, ob_bottom: float,
                       fvg_top: float, fvg_bottom: float, ema200: float,
                       above_ema20: bool, above_ema50: bool, above_ema200: bool,
                       tolerance_pct: float = 2.0):
    """Compute confluence score 0-8."""
    tolerance = close * (tolerance_pct / 100.0)
    score = 0
    details = []

    # Fib 61.8% (+2)
    if not np.isnan(fib_levels.get("0.618", np.nan)):
        if abs(close - fib_levels["0.618"]) <= tolerance:
            score += 2
            details.append("At Fib 61.8% (Golden Pocket) [+2]")

    # Fib 50% (+1)
    if not np.isnan(fib_levels.get("0.5", np.nan)):
        if abs(close - fib_levels["0.5"]) <= tolerance:
            score += 1
            details.append("At Fib 50% [+1]")

    # Inside Order Block (+2)
    if not np.isnan(ob_top) and not np.isnan(ob_bottom):
        if ob_bottom <= close <= ob_top:
            score += 2
            details.append("Inside Order Block [+2]")

    # Inside FVG (+1)
    if not np.isnan(fvg_top) and not np.isnan(fvg_bottom):
        if fvg_bottom <= close <= fvg_top:
            score += 1
            details.append("Inside FVG [+1]")

    # Near EMA 200 (+1)
    if not np.isnan(ema200):
        if abs(close - ema200) <= tolerance:
            score += 1
            details.append("Near EMA 200 [+1]")

    # Multi-TF alignment: all EMAs aligned (+1)
    if above_ema20 and above_ema50 and above_ema200:
        score += 1
        details.append("EMA alignment (20 > 50 > 200) [+1]")

    score = min(score, 8)
    return score, details


# ═══════════════════════════════════════════════════════════
#  SIGNAL STATE MACHINE
# ═══════════════════════════════════════════════════════════

def run_signal_state_machine(close: np.ndarray, high: np.ndarray, low: np.ndarray,
                             rsx: np.ndarray, lrsi_arr: np.ndarray, macd_hist: np.ndarray,
                             ema20: np.ndarray, confluence_scores: np.ndarray,
                             oversold_rsx: int = 30, overbought_rsx: int = 70,
                             oversold_lrsi: float = 0.2, overbought_lrsi: float = 0.8,
                             min_confluence: int = 2):
    """Run the b1/b2/b3/s?/s1/s2 state machine across all bars.

    Returns list of signal events and final state info.
    """
    n = len(close)
    signal_state = 0
    bars_since = 0
    signals = []  # list of (bar_index, signal_name, price, rsx_val, lrsi_val)

    SIGNAL_NAMES = {1: "b1", 2: "b2", 3: "b3", -1: "s?", -2: "s1", -3: "s2", 0: "neutral"}

    for i in range(2, n):
        bars_since += 1

        # Higher low / Lower high detection
        lookback = min(5, i)
        higher_low = low[i] > np.min(low[max(0, i - lookback):i])
        lower_high = high[i] < np.max(high[max(0, i - lookback):i])

        # RSX turning down
        rsx_turning_down = (rsx[i] < rsx[i - 1]) and (rsx[i - 1] > rsx[i - 2]) if i >= 2 else False

        # Buy conditions
        b1_cond = (rsx[i] < oversold_rsx and lrsi_arr[i] < oversold_lrsi
                   and confluence_scores[i] >= min_confluence and signal_state >= 0)

        b2_cond = (signal_state == 1 and bars_since <= 10
                   and rsx[i] > oversold_rsx and rsx[i - 1] <= oversold_rsx  # crossover
                   and (macd_hist[i] > macd_hist[i - 1] or macd_hist[i] > 0))

        b3_cond = (signal_state == 2 and bars_since <= 10
                   and rsx[i] > 50 and close[i] > ema20[i] and higher_low)

        # Sell conditions
        s_warn_cond = (rsx[i] > overbought_rsx and lrsi_arr[i] > overbought_lrsi
                       and signal_state <= 0)

        s1_cond = ((signal_state == -1 or s_warn_cond)
                   and rsx[i] > 75 and rsx_turning_down)

        s2_cond = (signal_state == -2 and bars_since <= 10
                   and rsx[i] < overbought_rsx and rsx[i - 1] >= overbought_rsx  # crossunder
                   and macd_hist[i] < 0 and lower_high)

        # State transitions (priority: higher signals first)
        prev_state = signal_state

        if b3_cond:
            signal_state = 3
            bars_since = 0
        elif b2_cond:
            signal_state = 2
            bars_since = 0
        elif b1_cond and signal_state != 1:
            signal_state = 1
            bars_since = 0

        if s2_cond:
            signal_state = -3
            bars_since = 0
        elif s1_cond and signal_state != -2:
            signal_state = -2
            bars_since = 0
        elif s_warn_cond and signal_state != -1 and signal_state >= 0:
            signal_state = -1
            bars_since = 0

        # Decay: reset after 30 bars of no new signal at terminal states
        if bars_since > 30 and signal_state in (3, -3):
            signal_state = 0

        # Record signal transitions
        if signal_state != prev_state and signal_state != 0:
            signals.append({
                "bar": i,
                "signal": SIGNAL_NAMES.get(signal_state, "?"),
                "price": round(float(close[i]), 2),
                "rsx": round(float(rsx[i]), 2),
                "lrsi": round(float(lrsi_arr[i]), 4),
            })

    return signals, signal_state, bars_since


# ═══════════════════════════════════════════════════════════
#  MAIN ANALYSIS
# ═══════════════════════════════════════════════════════════

def fetch_ohlcv(ticker: str, interval: str = "D"):
    """Fetch OHLCV data using yfinance."""
    try:
        import yfinance as yf
    except ImportError:
        print("ERROR: yfinance not installed. Run: pip install yfinance", file=sys.stderr)
        sys.exit(1)

    interval_map = {
        "1": "1m", "5": "5m", "15": "15m", "30": "30m", "60": "1h",
        "D": "1d", "W": "1wk", "M": "1mo",
    }
    period_map = {
        "1": "7d", "5": "60d", "15": "60d", "30": "60d", "60": "2y",
        "D": "2y", "W": "5y", "M": "10y",
    }

    yf_interval = interval_map.get(interval, "1d")
    yf_period = period_map.get(interval, "2y")

    t = yf.Ticker(ticker)
    df = t.history(period=yf_period, interval=yf_interval)

    if df.empty:
        print(f"ERROR: No data returned for {ticker} interval={interval}", file=sys.stderr)
        sys.exit(1)

    df = df[["Open", "High", "Low", "Close", "Volume"]]
    try:
        df.index = pd.to_datetime(df.index, utc=True).tz_localize(None)
    except Exception:
        df.index = pd.to_datetime(df.index)
    df = df.sort_index().dropna()

    return df


def analyze(ticker: str, interval: str = "D"):
    """Run full 禅動 analysis and return results dict."""
    df = fetch_ohlcv(ticker, interval)

    close = df["Close"].values
    high = df["High"].values
    low = df["Low"].values
    open_arr = df["Open"].values
    n = len(close)

    # Oscillators
    rsx = jurik_rsx(close, length=14)
    lrsi_arr = laguerre_rsi(close, alpha=0.7)

    if talib is not None:
        macd_line, signal_line, macd_hist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
        ema20 = talib.EMA(close, timeperiod=20)
        ema50 = talib.EMA(close, timeperiod=50)
        ema200 = talib.EMA(close, timeperiod=200)
    else:
        # Fallback: pandas EWM — MACD values may differ slightly from talib
        import logging as _log
        _log.getLogger(__name__).warning("talib not installed — using pandas EWM fallback (MACD values may differ)")
        s = pd.Series(close)
        ema20 = s.ewm(span=20, adjust=False).mean().values
        ema50 = s.ewm(span=50, adjust=False).mean().values
        ema200 = s.ewm(span=200, adjust=False).mean().values
        ema12 = s.ewm(span=12, adjust=False).mean().values
        ema26 = s.ewm(span=26, adjust=False).mean().values
        macd_line = ema12 - ema26
        signal_line = pd.Series(macd_line).ewm(span=9, adjust=False).mean().values
        macd_hist = macd_line - signal_line

    # Replace NaN with 0 for safety
    macd_hist = np.nan_to_num(macd_hist, nan=0.0)
    ema20 = np.nan_to_num(ema20, nan=close[0])
    ema50 = np.nan_to_num(ema50, nan=close[0])
    ema200 = np.nan_to_num(ema200, nan=close[0])

    # Fibonacci
    swing_highs, swing_lows = detect_swings(high, low, length=10)
    if swing_highs and swing_lows:
        last_sh = swing_highs[-1][1]
        last_sl = swing_lows[-1][1]
        fib_levels = compute_fib_levels(last_sh, last_sl)
    else:
        last_sh, last_sl = np.nan, np.nan
        fib_levels = {"0.0": np.nan, "0.236": np.nan, "0.382": np.nan,
                      "0.5": np.nan, "0.618": np.nan, "0.786": np.nan, "1.0": np.nan}

    # Order Blocks & FVG
    ob_top, ob_bottom = detect_order_blocks(open_arr, close, high, low)
    fvg_top, fvg_bottom = detect_fvg(high, low)

    # Per-bar confluence scores (simplified: use last bar's static context)
    confluence_scores = np.zeros(n, dtype=int)
    for i in range(n):
        tol = close[i] * 0.02
        score = 0
        if not np.isnan(fib_levels.get("0.618", np.nan)):
            if abs(close[i] - fib_levels["0.618"]) <= tol:
                score += 2
        if not np.isnan(fib_levels.get("0.5", np.nan)):
            if abs(close[i] - fib_levels["0.5"]) <= tol:
                score += 1
        if not np.isnan(ob_top) and ob_bottom <= close[i] <= ob_top:
            score += 2
        if not np.isnan(fvg_top) and fvg_bottom <= close[i] <= fvg_top:
            score += 1
        if not np.isnan(ema200[i]) and abs(close[i] - ema200[i]) <= tol:
            score += 1
        if close[i] > ema20[i] and close[i] > ema50[i] and close[i] > ema200[i]:
            score += 1
        confluence_scores[i] = min(score, 8)

    # Signal state machine
    signals, final_state, bars_since = run_signal_state_machine(
        close, high, low, rsx, lrsi_arr, macd_hist, ema20, confluence_scores
    )

    # Final confluence for current bar
    current_price = float(close[-1])
    final_confluence, confluence_details = compute_confluence(
        current_price, fib_levels, ob_top, ob_bottom, fvg_top, fvg_bottom,
        float(ema200[-1]),
        current_price > ema20[-1], current_price > ema50[-1], current_price > ema200[-1]
    )

    SIGNAL_NAMES = {1: "b1", 2: "b2", 3: "b3", -1: "s?", -2: "s1", -3: "s2", 0: "neutral"}

    # Position sizing
    if final_confluence <= 2:
        position_size = "25%"
        confidence = "LOW"
    elif final_confluence <= 4:
        position_size = "50%"
        confidence = "MEDIUM"
    elif final_confluence <= 6:
        position_size = "75%"
        confidence = "HIGH"
    else:
        position_size = "100%"
        confidence = "VERY HIGH"

    # Signal progression description
    sig_name = SIGNAL_NAMES.get(final_state, "neutral")
    if final_state == 1:
        progression = "b1 triggered, watching for b2 confirmation (RSX cross above 30)"
    elif final_state == 2:
        progression = "b2 confirmed, watching for b3 (RSX > 50 + above EMA 20 + higher low)"
    elif final_state == 3:
        progression = "b3 full conviction — entry signal active"
    elif final_state == -1:
        progression = "s? warning — overbought, watching for s1"
    elif final_state == -2:
        progression = "s1 triggered — RSX turning down, consider reducing"
    elif final_state == -3:
        progression = "s2 confirmed — exit signal active"
    else:
        progression = "Neutral — no active signal progression"

    # RSX zone
    rsx_val = float(rsx[-1])
    if rsx_val < 30:
        rsx_zone = "oversold"
    elif rsx_val > 70:
        rsx_zone = "overbought"
    else:
        rsx_zone = "neutral"

    # LRSI zone
    lrsi_val = float(lrsi_arr[-1])
    if lrsi_val < 0.2:
        lrsi_zone = "oversold"
    elif lrsi_val > 0.8:
        lrsi_zone = "overbought"
    else:
        lrsi_zone = "neutral"

    # MACD description
    hist_val = float(macd_hist[-1])
    if len(macd_hist) > 1:
        hist_prev = float(macd_hist[-2])
        if hist_val > 0 and hist_val > hist_prev:
            macd_desc = "positive, strengthening"
        elif hist_val > 0:
            macd_desc = "positive, weakening"
        elif hist_val < 0 and hist_val < hist_prev:
            macd_desc = "negative, deepening"
        elif hist_val < 0:
            macd_desc = "negative, recovering"
        else:
            macd_desc = "flat"
    else:
        macd_desc = "N/A"

    # Signal price
    signal_price = signals[-1]["price"] if signals else current_price

    # Last 5 signals
    recent = signals[-5:] if signals else []
    recent_with_dates = []
    for s in recent:
        bar_idx = s["bar"]
        if bar_idx < len(df):
            date_str = df.index[bar_idx].strftime("%Y-%m-%d")
        else:
            date_str = "?"
        recent_with_dates.append({
            "date": date_str,
            "signal": s["signal"],
            "price": s["price"],
            "rsx": s["rsx"],
            "lrsi": s["lrsi"],
        })

    # Clean NaN for JSON serialization
    def clean(v):
        if isinstance(v, float) and np.isnan(v):
            return None
        return v

    result = {
        "ticker": ticker,
        "interval": interval,
        "current_price": round(current_price, 2),
        "data_points": n,
        "date_range": f"{df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')}",
        "signal_state": sig_name,
        "signal_price": signal_price,
        "bars_since_signal": bars_since,
        "progression": progression,
        "rsx": round(rsx_val, 2),
        "rsx_zone": rsx_zone,
        "lrsi": round(lrsi_val, 4),
        "lrsi_zone": lrsi_zone,
        "macd_hist": round(hist_val, 4),
        "macd_desc": macd_desc,
        "ema20": round(float(ema20[-1]), 2),
        "ema50": round(float(ema50[-1]), 2),
        "ema200": round(float(ema200[-1]), 2),
        "fib_levels": {k: clean(round(v, 2)) if not np.isnan(v) else None for k, v in fib_levels.items()},
        "confluence_score": final_confluence,
        "confluence_details": confluence_details,
        "confidence": confidence,
        "position_size": position_size,
        "recent_signals": recent_with_dates,
        "total_signals": len(signals),
    }

    return result


def format_dashboard(result: dict) -> str:
    """Format analysis result as terminal dashboard."""
    r = result
    lines = []

    lines.append("")
    lines.append("=" * 58)
    lines.append(f"  禅動 ANALYSIS: {r['ticker']} ({r['interval']}) — ${r['current_price']}")
    lines.append(f"  Source: Local Analysis")
    lines.append(f"  Data: {r['data_points']} bars ({r['date_range']})")
    lines.append("=" * 58)
    lines.append("")
    lines.append(f"  LATEST SIGNAL: {r['signal_state'].upper()} at ~${r['signal_price']}")
    lines.append(f"  SIGNAL AGE: {r['bars_since_signal']} bars")
    lines.append(f"  PROGRESSION: {r['progression']}")
    lines.append("")
    lines.append("  OSCILLATORS:")
    lines.append(f"    RSX(14):      {r['rsx']} ({r['rsx_zone']})")
    lines.append(f"    Laguerre RSI: {r['lrsi']} ({r['lrsi_zone']})")
    lines.append(f"    MACD Hist:    {r['macd_hist']} ({r['macd_desc']})")
    lines.append("")
    lines.append(f"  CONFLUENCE: {r['confluence_score']}/8 ({r['confidence']})")
    if r['confluence_details']:
        for d in r['confluence_details']:
            lines.append(f"    + {d}")
    else:
        lines.append("    (no confluence conditions met)")
    lines.append("")
    lines.append(f"  POSITION SIZING: {r['position_size']} based on confluence")
    lines.append("")
    lines.append(f"  EMAs:")
    lines.append(f"    EMA 20:  ${r['ema20']}")
    lines.append(f"    EMA 50:  ${r['ema50']}")
    lines.append(f"    EMA 200: ${r['ema200']}")
    lines.append("")

    if r.get("fib_levels"):
        fib = r["fib_levels"]
        lines.append("  FIBONACCI LEVELS:")
        for level in ["0.236", "0.382", "0.5", "0.618", "0.786"]:
            val = fib.get(level)
            marker = " <-- price" if val and abs(r["current_price"] - val) <= r["current_price"] * 0.02 else ""
            lines.append(f"    {level}: ${val}{marker}" if val else f"    {level}: N/A")
        lines.append("")

    lines.append("-- Last 5 Signals " + "-" * 39)
    if r['recent_signals']:
        for s in r['recent_signals']:
            lines.append(f"  {s['date']}  {s['signal'].upper():>3}  ${s['price']:<10}  RSX: {s['rsx']}  LRSI: {s['lrsi']}")
    else:
        lines.append("  (no signals detected in data range)")
    lines.append("=" * 58)
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="禅動 (Chandong) Local Signal Analyzer")
    parser.add_argument("ticker", help="Stock ticker (e.g., NVDA, AAPL, AU)")
    parser.add_argument("--interval", "-i", default="D",
                        help="Chart interval: 1,5,15,30,60,D,W,M (default: D)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    ticker = args.ticker.upper()
    interval = args.interval

    result = analyze(ticker, interval)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(format_dashboard(result))


if __name__ == "__main__":
    main()
