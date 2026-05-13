"""
ROUND 2 — Strategy 01: RSI + SuperTrend Hybrid
===============================================
EVOLUTION: Combines #1 (RSI Mean Reversion, 208% return) with #4 (SuperTrend, 168%).
Buy when RSI < 35 (oversold) AND SuperTrend is bullish (trend filter).
This ensures we only buy dips in an UPTREND — avoiding catching falling knives.
Exit when RSI > 75 OR SuperTrend flips bearish.

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


class RSISuperTrendHybrid(Strategy):
    rsi_period = 14
    rsi_buy = 35
    rsi_sell = 75
    st_period = 10
    st_mult = 3.0

    def init(self):
        self.rsi = self.I(calc_rsi, self.data.Close, self.rsi_period)
        self.st_dir = self.I(supertrend_dir, self.data.High, self.data.Low,
                             self.data.Close, self.st_period, self.st_mult)

    def next(self):
        if (self.rsi[-1] < self.rsi_buy and
            self.st_dir[-1] == 1 and
            not self.position):
            self.buy()
        elif self.position:
            if self.rsi[-1] > self.rsi_sell or self.st_dir[-1] == -1:
                self.position.close()


bt = Backtest(data, RSISuperTrendHybrid, cash=100_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r2_01_rsi_supertrend_hybrid")
