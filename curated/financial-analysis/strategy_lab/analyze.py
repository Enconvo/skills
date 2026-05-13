#!/usr/bin/env python3
"""
Stock Technical Analysis Engine
================================
Usage: python analyze.py TICKER [timeframe]
Example: python analyze.py AU 1h
         python analyze.py AAPL 1d

Runs full indicator suite and prints a structured analysis report.
"""

import sys
import numpy as np
import pandas as pd
import talib
import yfinance as yf
from datetime import datetime, timedelta


def fetch_data(ticker, interval="1h"):
    """Fetch OHLCV data from yfinance."""
    t = yf.Ticker(ticker)
    if interval in ("1h", "30m", "15m", "5m"):
        df = t.history(period="730d", interval=interval)
    else:
        df = t.history(period="5y", interval=interval)
    if df.empty:
        raise ValueError(f"No data returned for {ticker}")
    df = df.reset_index()
    date_col = "Datetime" if "Datetime" in df.columns else "Date"
    df = df.rename(columns={date_col: "Date"})
    df = df[["Date", "Open", "High", "Low", "Close", "Volume"]].dropna()
    df = df.sort_values("Date").reset_index(drop=True)
    return df


def supertrend(high, low, close, atr_period=10, mult=3.0):
    """Compute Supertrend direction and line."""
    atr = talib.ATR(high, low, close, timeperiod=atr_period)
    hl2 = (high + low) / 2.0
    bu = hl2 + mult * atr
    bl = hl2 - mult * atr
    n = len(close)
    fu = np.full(n, np.nan)
    fl = np.full(n, np.nan)
    d = np.full(n, np.nan)
    st_line = np.full(n, np.nan)
    fv = atr_period
    fu[fv] = bu[fv]; fl[fv] = bl[fv]; d[fv] = 1.0; st_line[fv] = fl[fv]
    for i in range(fv + 1, n):
        fu[i] = min(bu[i], fu[i-1]) if close[i-1] <= fu[i-1] else bu[i]
        fl[i] = max(bl[i], fl[i-1]) if close[i-1] >= fl[i-1] else bl[i]
        if d[i-1] == 1.0:
            d[i] = -1.0 if close[i] < fl[i] else 1.0
        else:
            d[i] = 1.0 if close[i] > fu[i] else -1.0
        st_line[i] = fl[i] if d[i] == 1.0 else fu[i]
    return d, st_line


def ichimoku(high, low, close):
    """Compute Ichimoku components."""
    def donchian_mid(h, l, period):
        hh = pd.Series(h).rolling(period).max().values
        ll = pd.Series(l).rolling(period).min().values
        return (hh + ll) / 2.0
    tenkan = donchian_mid(high, low, 9)
    kijun = donchian_mid(high, low, 26)
    span_a = (tenkan + kijun) / 2.0
    span_b = donchian_mid(high, low, 52)
    return tenkan, kijun, span_a, span_b


def bb_squeeze(close, high, low):
    """Check if BB is inside Keltner (squeeze ON)."""
    bbu, bbm, bbl = talib.BBANDS(close, timeperiod=20, nbdevup=2.0, nbdevdn=2.0)
    ema = talib.EMA(close, timeperiod=20)
    atr = talib.ATR(high, low, close, timeperiod=10)
    kcu = ema + 1.5 * atr
    kcl = ema - 1.5 * atr
    squeeze_on = (bbl > kcl) & (bbu < kcu)
    return squeeze_on, bbu, bbm, bbl, kcu, kcl


def find_support_resistance(high, low, close, lookback=100):
    """Find key S/R levels using pivot points and rolling extremes."""
    levels = []
    h = high[-lookback:]
    l = low[-lookback:]
    c = close[-lookback:]

    # Daily pivot points (using last bar)
    pp = (h[-1] + l[-1] + c[-1]) / 3
    r1 = 2 * pp - l[-1]
    s1 = 2 * pp - h[-1]
    r2 = pp + (h[-1] - l[-1])
    s2 = pp - (h[-1] - l[-1])

    # Rolling levels
    r_20h = np.max(h[-20:])
    s_20l = np.min(l[-20:])
    r_50h = np.max(h[-50:]) if len(h) >= 50 else np.max(h)
    s_50l = np.min(l[-50:]) if len(l) >= 50 else np.min(l)

    return {
        "Pivot Point": round(pp, 2),
        "R1 (Pivot)": round(r1, 2),
        "R2 (Pivot)": round(r2, 2),
        "S1 (Pivot)": round(s1, 2),
        "S2 (Pivot)": round(s2, 2),
        "20-bar High": round(r_20h, 2),
        "20-bar Low": round(s_20l, 2),
        "50-bar High": round(r_50h, 2),
        "50-bar Low": round(s_50l, 2),
    }


def confluence_score(close, high, low, volume):
    """Score from -5 to +5 based on multiple indicators."""
    score = 0
    reasons = []
    i = -1  # latest bar

    # 1. EMA alignment
    ema8 = talib.EMA(close, timeperiod=8)
    ema21 = talib.EMA(close, timeperiod=21)
    ema55 = talib.EMA(close, timeperiod=55)
    if ema8[i] > ema21[i] > ema55[i]:
        score += 1; reasons.append("EMA 8>21>55 bullish alignment (+1)")
    elif ema8[i] < ema21[i] < ema55[i]:
        score -= 1; reasons.append("EMA 8<21<55 bearish alignment (-1)")
    else:
        reasons.append("EMA mixed (0)")

    # 2. RSI
    rsi = talib.RSI(close, timeperiod=14)
    rsi_val = rsi[i]
    rsi_rising = rsi[i] > rsi[i-1]
    if 40 <= rsi_val <= 60 and rsi_rising:
        score += 1; reasons.append(f"RSI {rsi_val:.1f} healthy & rising (+1)")
    elif rsi_val > 70:
        score -= 1; reasons.append(f"RSI {rsi_val:.1f} overbought (-1)")
    elif rsi_val < 30:
        score += 1; reasons.append(f"RSI {rsi_val:.1f} oversold — potential bounce (+1)")
    else:
        reasons.append(f"RSI {rsi_val:.1f} neutral (0)")

    # 3. MACD
    macd, signal, hist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
    if macd[i] > signal[i] and hist[i] > 0:
        score += 1; reasons.append(f"MACD bullish (line > signal, histogram +) (+1)")
    elif macd[i] < signal[i] and hist[i] < 0:
        score -= 1; reasons.append(f"MACD bearish (line < signal, histogram -) (-1)")
    else:
        reasons.append("MACD mixed (0)")

    # 4. ADX trend strength
    adx = talib.ADX(high, low, close, timeperiod=14)
    plus_di = talib.PLUS_DI(high, low, close, timeperiod=14)
    minus_di = talib.MINUS_DI(high, low, close, timeperiod=14)
    if adx[i] > 25:
        if plus_di[i] > minus_di[i]:
            score += 1; reasons.append(f"ADX {adx[i]:.1f} strong trend, +DI leading (+1)")
        else:
            score -= 1; reasons.append(f"ADX {adx[i]:.1f} strong trend, -DI leading (-1)")
    else:
        reasons.append(f"ADX {adx[i]:.1f} weak/no trend (0)")

    # 5. Volume
    vol_sma = talib.SMA(volume.astype(float), timeperiod=20)
    if volume[i] > 1.2 * vol_sma[i]:
        score += 1 if score > 0 else -1
        direction = "confirming" if score > 0 else "confirming selling"
        reasons.append(f"Volume {volume[i]/vol_sma[i]:.1f}x avg — {direction} ({'+1' if score > 0 else '-1'})")
    else:
        reasons.append(f"Volume {volume[i]/vol_sma[i]:.1f}x avg — below threshold (0)")

    return score, reasons


def analyze(ticker, interval="1h"):
    """Run full analysis on a ticker."""
    print(f"\n{'='*70}")
    print(f"  TECHNICAL ANALYSIS: {ticker.upper()}")
    print(f"  Timeframe: {interval} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*70}\n")

    # Fetch data
    df = fetch_data(ticker, interval)
    close = df["Close"].values
    high = df["High"].values
    low = df["Low"].values
    volume = df["Volume"].values
    opens = df["Open"].values
    price = close[-1]
    prev_close = close[-2]
    change_pct = (price - prev_close) / prev_close * 100 if prev_close != 0 else 0

    print(f"  Price: ${price:.2f}  ({'+' if change_pct > 0 else ''}{change_pct:.2f}%)")
    print(f"  Data: {len(df)} candles from {df['Date'].iloc[0]} to {df['Date'].iloc[-1]}")

    # ─── TREND ────────────────────────────────────────────────
    print(f"\n{'─'*70}")
    print("  TREND ANALYSIS")
    print(f"{'─'*70}")

    ema8 = talib.EMA(close, timeperiod=8)
    ema21 = talib.EMA(close, timeperiod=21)
    ema55 = talib.EMA(close, timeperiod=55)
    ema200 = talib.EMA(close, timeperiod=200)

    print(f"  EMA 8:    ${ema8[-1]:.2f}  {'▲ price above' if price > ema8[-1] else '▼ price below'}")
    print(f"  EMA 21:   ${ema21[-1]:.2f}  {'▲ price above' if price > ema21[-1] else '▼ price below'}")
    print(f"  EMA 55:   ${ema55[-1]:.2f}  {'▲ price above' if price > ema55[-1] else '▼ price below'}")
    if not np.isnan(ema200[-1]):
        print(f"  EMA 200:  ${ema200[-1]:.2f}  {'▲ price above' if price > ema200[-1] else '▼ price below'}")

    if ema8[-1] > ema21[-1] > ema55[-1]:
        ema_verdict = "BULLISH — all EMAs stacked up"
    elif ema8[-1] < ema21[-1] < ema55[-1]:
        ema_verdict = "BEARISH — all EMAs stacked down"
    else:
        ema_verdict = "MIXED — EMAs not aligned"
    print(f"  EMA Verdict: {ema_verdict}")

    # Supertrend
    st_dir, st_line = supertrend(high, low, close)
    st_label = "BULLISH" if st_dir[-1] == 1.0 else "BEARISH"
    st_flip = "just flipped!" if st_dir[-1] != st_dir[-2] else "continuation"
    print(f"\n  Supertrend: {st_label} (line @ ${st_line[-1]:.2f}) — {st_flip}")

    # Ichimoku
    tenkan, kijun, span_a, span_b = ichimoku(high, low, close)
    cloud_top = max(span_a[-1], span_b[-1])
    cloud_bottom = min(span_a[-1], span_b[-1])
    if price > cloud_top:
        ichi_pos = "ABOVE cloud — bullish"
    elif price < cloud_bottom:
        ichi_pos = "BELOW cloud — bearish"
    else:
        ichi_pos = "INSIDE cloud — indecisive"
    tk_cross = "Tenkan > Kijun (bullish)" if tenkan[-1] > kijun[-1] else "Tenkan < Kijun (bearish)"
    print(f"  Ichimoku: {ichi_pos}")
    print(f"  Ichimoku T/K: {tk_cross}")
    print(f"  Cloud range: ${cloud_bottom:.2f} — ${cloud_top:.2f}")

    # ─── MOMENTUM ─────────────────────────────────────────────
    print(f"\n{'─'*70}")
    print("  MOMENTUM")
    print(f"{'─'*70}")

    rsi = talib.RSI(close, timeperiod=14)
    rsi_val = rsi[-1]
    rsi_label = "OVERBOUGHT" if rsi_val > 70 else "OVERSOLD" if rsi_val < 30 else "NEUTRAL"
    rsi_trend = "rising" if rsi[-1] > rsi[-2] else "falling"
    print(f"  RSI(14): {rsi_val:.1f} — {rsi_label} ({rsi_trend})")

    macd, signal, hist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
    macd_cross = ""
    if macd[-1] > signal[-1] and macd[-2] <= signal[-2]:
        macd_cross = " ** BULLISH CROSS just happened **"
    elif macd[-1] < signal[-1] and macd[-2] >= signal[-2]:
        macd_cross = " ** BEARISH CROSS just happened **"
    hist_dir = "growing" if abs(hist[-1]) > abs(hist[-2]) else "shrinking"
    print(f"  MACD: {'above' if macd[-1] > signal[-1] else 'below'} signal | Histogram {hist_dir}{macd_cross}")

    adx = talib.ADX(high, low, close, timeperiod=14)
    plus_di = talib.PLUS_DI(high, low, close, timeperiod=14)
    minus_di = talib.MINUS_DI(high, low, close, timeperiod=14)
    adx_label = "STRONG TREND" if adx[-1] > 25 else "WEAK/NO TREND"
    di_label = "+DI leading (bullish pressure)" if plus_di[-1] > minus_di[-1] else "-DI leading (bearish pressure)"
    print(f"  ADX(14): {adx[-1]:.1f} — {adx_label} | {di_label}")

    stoch_k, stoch_d = talib.STOCH(high, low, close, fastk_period=14, slowk_period=3, slowd_period=3)
    stoch_label = "OVERBOUGHT" if stoch_k[-1] > 80 else "OVERSOLD" if stoch_k[-1] < 20 else "NEUTRAL"
    print(f"  Stochastic(14,3,3): %K={stoch_k[-1]:.1f} %D={stoch_d[-1]:.1f} — {stoch_label}")

    willr = talib.WILLR(high, low, close, timeperiod=14)
    cci = talib.CCI(high, low, close, timeperiod=20)
    print(f"  Williams %R(14): {willr[-1]:.1f} | CCI(20): {cci[-1]:.1f}")

    # ─── VOLATILITY ───────────────────────────────────────────
    print(f"\n{'─'*70}")
    print("  VOLATILITY & SQUEEZE")
    print(f"{'─'*70}")

    atr = talib.ATR(high, low, close, timeperiod=14)
    atr_pct = atr[-1] / price * 100 if price != 0 else 0
    print(f"  ATR(14): ${atr[-1]:.2f} ({atr_pct:.2f}% of price)")

    bbu, bbm, bbl = talib.BBANDS(close, timeperiod=20, nbdevup=2.0, nbdevdn=2.0)
    bb_width = (bbu[-1] - bbl[-1]) / bbm[-1] if bbm[-1] != 0 else 0
    print(f"  Bollinger Bands(20,2): ${bbl[-1]:.2f} — ${bbm[-1]:.2f} — ${bbu[-1]:.2f}")
    print(f"  BB Width: {bb_width:.4f} {'(TIGHT — squeeze possible)' if bb_width < 0.04 else '(normal)' if bb_width < 0.08 else '(WIDE — expanded volatility)'}")

    squeeze_on, _, _, _, kcu, kcl = bb_squeeze(close, high, low)
    squeeze_now = squeeze_on[-1]
    squeeze_bars = 0
    for j in range(len(squeeze_on)-1, -1, -1):
        if squeeze_on[j] == squeeze_now:
            squeeze_bars += 1
        else:
            break
    if squeeze_now:
        print(f"  TTM Squeeze: ON for {squeeze_bars} bars — COILING, breakout imminent")
    else:
        if squeeze_bars < 5:
            print(f"  TTM Squeeze: OFF (just fired {squeeze_bars} bars ago!) — BREAKOUT IN PROGRESS")
        else:
            print(f"  TTM Squeeze: OFF for {squeeze_bars} bars — normal volatility")

    # ─── SUPPORT & RESISTANCE ─────────────────────────────────
    print(f"\n{'─'*70}")
    print("  SUPPORT & RESISTANCE LEVELS")
    print(f"{'─'*70}")

    levels = find_support_resistance(high, low, close)
    # Sort by price
    sorted_levels = sorted(levels.items(), key=lambda x: x[1], reverse=True)
    for name, val in sorted_levels:
        marker = "  ◄── PRICE HERE" if (price != 0 and abs(val - price) / price < 0.005) else ""
        above_below = "resistance" if val > price else "support" if val < price else "AT"
        print(f"  ${val:<10.2f} {name:<20s} ({above_below}){marker}")
    print(f"  ${price:<10.2f} {'CURRENT PRICE':<20s}")

    # Donchian levels
    don_20h = np.max(high[-20:])
    don_20l = np.min(low[-20:])
    don_50h = np.max(high[-50:]) if len(high) >= 50 else np.max(high)
    don_50l = np.min(low[-50:]) if len(low) >= 50 else np.min(low)
    print(f"\n  Donchian 20: ${don_20l:.2f} — ${don_20h:.2f}  (breakout levels)")
    print(f"  Donchian 50: ${don_50l:.2f} — ${don_50h:.2f}  (major breakout levels)")

    # ─── CONFLUENCE SCORE ─────────────────────────────────────
    print(f"\n{'─'*70}")
    print("  CONFLUENCE SCORE")
    print(f"{'─'*70}")

    score, reasons = confluence_score(close, high, low, volume)
    for r in reasons:
        print(f"  {r}")
    bar = "█" * abs(score) + "░" * (5 - abs(score))
    direction = "BULLISH" if score > 0 else "BEARISH" if score < 0 else "NEUTRAL"
    print(f"\n  Score: {score:+d}/5 [{bar}] → {direction}")

    # ─── VERDICT & SCENARIOS ──────────────────────────────────
    print(f"\n{'─'*70}")
    print("  VERDICT & SCENARIOS")
    print(f"{'─'*70}")

    # Overall verdict
    bullish_signals = 0
    bearish_signals = 0
    total_signals = 7

    if ema8[-1] > ema21[-1] > ema55[-1]: bullish_signals += 1
    elif ema8[-1] < ema21[-1] < ema55[-1]: bearish_signals += 1
    if st_dir[-1] == 1.0: bullish_signals += 1
    else: bearish_signals += 1
    if price > cloud_top: bullish_signals += 1
    elif price < cloud_bottom: bearish_signals += 1
    if rsi_val < 30: bullish_signals += 1  # oversold = potential buy
    elif rsi_val > 70: bearish_signals += 1
    if macd[-1] > signal[-1]: bullish_signals += 1
    else: bearish_signals += 1
    if plus_di[-1] > minus_di[-1]: bullish_signals += 1
    else: bearish_signals += 1
    if score > 0: bullish_signals += 1
    elif score < 0: bearish_signals += 1

    print(f"\n  Bullish signals: {bullish_signals}/{total_signals}")
    print(f"  Bearish signals: {bearish_signals}/{total_signals}")

    if bullish_signals >= 5:
        verdict = "STRONG BUY BIAS"
    elif bullish_signals >= 4:
        verdict = "MODERATE BUY BIAS"
    elif bearish_signals >= 5:
        verdict = "STRONG SELL BIAS"
    elif bearish_signals >= 4:
        verdict = "MODERATE SELL BIAS"
    else:
        verdict = "NEUTRAL / WAIT"

    print(f"\n  >>> VERDICT: {verdict} <<<")

    # Scenarios
    nearest_resistance = min([v for _, v in sorted_levels if v > price], default=price * 1.05)
    nearest_support = max([v for _, v in sorted_levels if v < price], default=price * 0.95)

    print(f"\n  IF price breaks above ${nearest_resistance:.2f} (nearest resistance):")
    print(f"    → Bullish confirmation. Next target: ${don_50h:.2f} (50-bar high)")
    print(f"    → Consider entry with stop at ${nearest_support:.2f}")

    print(f"\n  IF price breaks below ${nearest_support:.2f} (nearest support):")
    print(f"    → Bearish breakdown. Next support: ${don_50l:.2f} (50-bar low)")
    print(f"    → Avoid longs. Watch for bounce at ${don_50l:.2f}")

    if squeeze_now:
        print(f"\n  IF squeeze fires (BB expands outside Keltner):")
        print(f"    → High-probability breakout. Direction determined by momentum at fire.")
        print(f"    → Watch for volume spike to confirm. Set stop at ${price - 2*atr[-1]:.2f} (2x ATR)")

    if rsi_val > 65:
        print(f"\n  IF RSI crosses above 70:")
        print(f"    → Overbought territory. Consider tightening stops or taking partial profits.")
    elif rsi_val < 35:
        print(f"\n  IF RSI crosses below 30:")
        print(f"    → Oversold territory. Watch for reversal candles for potential long entry.")

    print(f"\n  RISK LEVELS:")
    print(f"    Stop loss (tight):  ${price - 1.5 * atr[-1]:.2f} (1.5x ATR)")
    print(f"    Stop loss (wide):   ${price - 2.5 * atr[-1]:.2f} (2.5x ATR)")
    print(f"    Take profit (1:2):  ${price + 3.0 * atr[-1]:.2f} (3x ATR)")
    print(f"    Take profit (1:3):  ${price + 4.5 * atr[-1]:.2f} (4.5x ATR)")

    # ─── DISCLAIMER ───────────────────────────────────────────
    print(f"\n{'─'*70}")
    print("  DISCLAIMER: This is technical analysis only — not financial advice.")
    print("  Always do your own research and manage risk appropriately.")
    print(f"{'─'*70}\n")


if __name__ == "__main__":
    ticker = sys.argv[1] if len(sys.argv) > 1 else "AU"
    interval = sys.argv[2] if len(sys.argv) > 2 else "1h"
    analyze(ticker, interval)
