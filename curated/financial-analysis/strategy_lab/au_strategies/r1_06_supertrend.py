"""
ROUND 1 — Strategy 06: SuperTrend
==================================
ATR-based trend indicator. Buy when price is above SuperTrend line,
sell when below. Great for capturing strong directional moves in AU.

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


def supertrend(high, low, close, period=10, multiplier=3.0):
    atr = talib.ATR(high, low, close, timeperiod=period)
    hl2 = (high + low) / 2
    upper = hl2 + multiplier * atr
    lower = hl2 - multiplier * atr

    st = np.full_like(close, np.nan)
    direction = np.zeros_like(close)

    for i in range(period, len(close)):
        if i == period:
            st[i] = upper[i]
            direction[i] = -1
            continue

        if direction[i-1] == 1:  # was bullish
            lower[i] = max(lower[i], lower[i-1]) if not np.isnan(lower[i-1]) else lower[i]
            if close[i] < lower[i]:
                direction[i] = -1
                st[i] = upper[i]
            else:
                direction[i] = 1
                st[i] = lower[i]
        else:  # was bearish
            upper[i] = min(upper[i], upper[i-1]) if not np.isnan(upper[i-1]) else upper[i]
            if close[i] > upper[i]:
                direction[i] = 1
                st[i] = lower[i]
            else:
                direction[i] = -1
                st[i] = upper[i]

    return direction


class SuperTrendStrategy(Strategy):
    atr_period = 10
    multiplier = 3.0

    def init(self):
        self.direction = self.I(supertrend, self.data.High, self.data.Low,
                                self.data.Close, self.atr_period, self.multiplier)

    def next(self):
        if self.direction[-1] == 1 and (len(self.direction) < 2 or self.direction[-2] == -1):
            self.buy()
        elif self.direction[-1] == -1 and self.position:
            self.position.close()


bt = Backtest(data, SuperTrendStrategy, cash=100_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r1_06_supertrend")
