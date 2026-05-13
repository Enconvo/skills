"""
NVDA — Last Bar State Checker
Runs the #1 strategy (R1-13 Gap-and-Go) on latest data and reports
the current state: in position or flat, with key indicator values.
Also checks R2-12 (PreMarket MACD Hybrid) as the best risk-adjusted pick.
"""
import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_nvda_data

data = load_nvda_data("daily")

# ── Strategy 1: R1-13 Gap-and-Go (#1 by return) ──

state_gap = {}

def calc_gap_pct(open_price, close_price):
    gap = np.full_like(open_price, np.nan)
    gap[1:] = (open_price[1:] - close_price[:-1]) / close_price[:-1] * 100
    return gap

def calc_atr(high, low, close, period):
    return talib.ATR(high, low, close, timeperiod=period)

def calc_sma(close, period):
    return talib.SMA(close, timeperiod=period)

def calc_macd_hist(close):
    _, _, hist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
    return hist


class GapAndGoState(Strategy):
    gap_threshold = 1.5
    atr_period = 14
    atr_mult = 2.5
    sma_period = 50

    def init(self):
        self.gap = self.I(calc_gap_pct, self.data.Open, self.data.Close)
        self.atr = self.I(calc_atr, self.data.High, self.data.Low, self.data.Close, self.atr_period)
        self.sma = self.I(calc_sma, self.data.Close, self.sma_period)
        self.trail_stop = 0

    def next(self):
        price = self.data.Close[-1]
        if not self.position:
            if (self.gap[-1] > self.gap_threshold and
                    price > self.sma[-1] and
                    not np.isnan(self.atr[-1])):
                self.buy()
                self.trail_stop = price - self.atr[-1] * self.atr_mult
        else:
            new_trail = price - self.atr[-1] * self.atr_mult
            if new_trail > self.trail_stop:
                self.trail_stop = new_trail
            if price < self.trail_stop:
                self.position.close()

        state_gap['in_position'] = bool(self.position)
        state_gap['price'] = price
        state_gap['gap_pct'] = self.gap[-1] if not np.isnan(self.gap[-1]) else 0
        state_gap['atr'] = self.atr[-1] if not np.isnan(self.atr[-1]) else 0
        state_gap['sma50'] = self.sma[-1] if not np.isnan(self.sma[-1]) else 0
        state_gap['trail_stop'] = self.trail_stop
        state_gap['date'] = str(self.data.index[-1])


# ── Strategy 2: R2-12 PreMarket MACD Hybrid (#2 best balance) ──

state_macd = {}

class PremarketMACDState(Strategy):
    atr_period = 14
    atr_mult = 2.0
    sma_period = 50

    def init(self):
        self.atr = self.I(calc_atr, self.data.High, self.data.Low, self.data.Close, self.atr_period)
        self.sma = self.I(calc_sma, self.data.Close, self.sma_period)
        self.macd_hist = self.I(calc_macd_hist, self.data.Close)
        self.trail_stop = 0

    def next(self):
        price = self.data.Close[-1]
        if not self.position:
            if (len(self.data) > 1 and
                    self.data.Open[-1] > self.data.High[-2] and
                    self.macd_hist[-1] > 0 and
                    price > self.sma[-1] and
                    not np.isnan(self.atr[-1])):
                self.buy()
                self.trail_stop = price - self.atr[-1] * self.atr_mult
        else:
            new_trail = price - self.atr[-1] * self.atr_mult
            if new_trail > self.trail_stop:
                self.trail_stop = new_trail
            if price < self.trail_stop:
                self.position.close()

        state_macd['in_position'] = bool(self.position)
        state_macd['price'] = price
        state_macd['macd_hist'] = self.macd_hist[-1] if not np.isnan(self.macd_hist[-1]) else 0
        state_macd['atr'] = self.atr[-1] if not np.isnan(self.atr[-1]) else 0
        state_macd['sma50'] = self.sma[-1] if not np.isnan(self.sma[-1]) else 0
        state_macd['trail_stop'] = self.trail_stop
        state_macd['date'] = str(self.data.index[-1])
        state_macd['prev_high'] = self.data.High[-2] if len(self.data) > 1 else 0


# Run both
bt1 = Backtest(data, GapAndGoState, cash=1_000_000, commission=0.001, exclusive_orders=True)
bt1.run()

bt2 = Backtest(data, PremarketMACDState, cash=1_000_000, commission=0.001, exclusive_orders=True)
bt2.run()


# ── Print Current State ──
print("=" * 60)
print(f"  CURRENT STATE: NVDA Strategies")
print(f"  Last candle: {state_gap.get('date', 'N/A')}")
print("=" * 60)

print(f"\n{'─' * 60}")
print(f"  #1: R1-13 Gap-and-Go (451.4% return)")
print(f"{'─' * 60}")
if state_gap.get('in_position'):
    print(f"  STATUS:       IN POSITION (LONG)")
    print(f"  Current:      ${state_gap['price']:.2f}")
    print(f"  Trail stop:   ${state_gap['trail_stop']:.2f}")
    pnl = (state_gap['price'] - state_gap['trail_stop']) / state_gap['trail_stop'] * 100
    print(f"  Cushion:      {pnl:.1f}% above trail stop")
    print(f"  ATR(14):      ${state_gap['atr']:.2f}")
    print(f"  ACTION:       HOLD. Let trailing stop manage exit.")
else:
    print(f"  STATUS:       FLAT (no position)")
    print(f"  Price:        ${state_gap['price']:.2f}")
    print(f"  SMA(50):      ${state_gap['sma50']:.2f}")
    trend = "ABOVE" if state_gap['price'] > state_gap['sma50'] else "BELOW"
    print(f"  Trend:        Price {trend} SMA(50)")
    print(f"  Last gap:     {state_gap['gap_pct']:.2f}%")
    print(f"  Entry needs:  Gap up > 1.5% + price > SMA(50)")
    print(f"  ACTION:       WAIT. No entry signal.")

print(f"\n{'─' * 60}")
print(f"  #2: R2-12 PreMarket MACD Hybrid (445.8% | Sharpe 0.90)")
print(f"{'─' * 60}")
if state_macd.get('in_position'):
    print(f"  STATUS:       IN POSITION (LONG)")
    print(f"  Current:      ${state_macd['price']:.2f}")
    print(f"  Trail stop:   ${state_macd['trail_stop']:.2f}")
    pnl = (state_macd['price'] - state_macd['trail_stop']) / state_macd['trail_stop'] * 100
    print(f"  Cushion:      {pnl:.1f}% above trail stop")
    print(f"  MACD hist:    {state_macd['macd_hist']:.4f}")
    print(f"  ACTION:       HOLD. Trail stop active.")
else:
    print(f"  STATUS:       FLAT (no position)")
    print(f"  Price:        ${state_macd['price']:.2f}")
    print(f"  SMA(50):      ${state_macd['sma50']:.2f}")
    trend = "ABOVE" if state_macd['price'] > state_macd['sma50'] else "BELOW"
    print(f"  Trend:        Price {trend} SMA(50)")
    print(f"  MACD hist:    {state_macd['macd_hist']:.4f} ({'positive' if state_macd['macd_hist'] > 0 else 'negative'})")
    print(f"  Prev high:    ${state_macd['prev_high']:.2f}")
    need_breakout = "YES" if state_macd['price'] > state_macd['prev_high'] else "NO"
    print(f"  Breakout:     {need_breakout} (open > prev high?)")
    print(f"  ACTION:       WAIT. Need open > prev high + MACD > 0 + uptrend.")

print(f"\n{'=' * 60}")
print(f"\n_strategy_name: last_bar_state")
