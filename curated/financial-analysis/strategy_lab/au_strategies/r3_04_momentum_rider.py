"""
ROUND 3 — Strategy 04: Momentum Rider (Max Returns)
====================================================
FINAL EVOLUTION: Optimized for MAXIMUM RETURNS.
Combines RSI entry timing with SuperTrend direction + EMA confirmation
+ wide ATR trailing stop to ride momentum as long as possible.

Entry: RSI < 35 + SuperTrend bullish + Close > EMA55 (long-term uptrend)
Exit: ATR trail (3x) — only exit when momentum truly dies
No RSI exit — let the trail do the work.

STATS:
---
[pending]
---
"""
import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_au_data

data = load_au_data("1h")


def calc_rsi(close, period):
    return talib.RSI(close, timeperiod=period)

def ema55(close):
    return talib.EMA(close, timeperiod=55)

def calc_atr(high, low, close, period):
    return talib.ATR(high, low, close, timeperiod=period)

def supertrend_dir(high, low, close, period=10, multiplier=3.0):
    atr = talib.ATR(high, low, close, timeperiod=period)
    hl2 = (high + low) / 2
    upper = hl2 + multiplier * atr
    lower = hl2 - multiplier * atr
    direction = np.zeros_like(close)
    for i in range(period, len(close)):
        if i == period:
            direction[i] = -1
            continue
        if direction[i-1] == 1:
            lower[i] = max(lower[i], lower[i-1]) if not np.isnan(lower[i-1]) else lower[i]
            direction[i] = -1 if close[i] < lower[i] else 1
        else:
            upper[i] = min(upper[i], upper[i-1]) if not np.isnan(upper[i-1]) else upper[i]
            direction[i] = 1 if close[i] > upper[i] else -1
    return direction


class MomentumRider(Strategy):
    rsi_period = 14
    rsi_entry = 35
    atr_period = 14
    atr_trail = 3.0

    def init(self):
        self.rsi = self.I(calc_rsi, self.data.Close, self.rsi_period)
        self.ema = self.I(ema55, self.data.Close)
        self.atr = self.I(calc_atr, self.data.High, self.data.Low,
                          self.data.Close, self.atr_period)
        self.st_dir = self.I(supertrend_dir, self.data.High, self.data.Low,
                             self.data.Close)
        self.highest = 0
        self.trail_stop = 0

    def next(self):
        price = self.data.Close[-1]
        atr_val = self.atr[-1]

        if np.isnan(atr_val) or np.isnan(self.ema[-1]):
            return

        if not self.position:
            uptrend = price > self.ema[-1]
            st_bull = self.st_dir[-1] == 1
            oversold = self.rsi[-1] < self.rsi_entry

            if uptrend and st_bull and oversold:
                self.buy()
                self.highest = price
                self.trail_stop = price - self.atr_trail * atr_val
        else:
            if price > self.highest:
                self.highest = price
            new_stop = self.highest - self.atr_trail * atr_val
            if new_stop > self.trail_stop:
                self.trail_stop = new_stop
            if price < self.trail_stop:
                self.position.close()
                self.highest = 0
                self.trail_stop = 0


bt = Backtest(data, MomentumRider, cash=100_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r3_04_momentum_rider")
