"""
ROUND 1 — Strategy 06: SuperTrend
==================================
ATR-based trend follower. Buy when SuperTrend flips bullish,
sell when it flips bearish. Period=10, Multiplier=3.0.
"""
import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_nvda_data

data = load_nvda_data("1h")


def calc_supertrend_dir(high, low, close, period=10, mult=3.0):
    atr = talib.ATR(high, low, close, timeperiod=period)
    hl2 = (high + low) / 2
    ub = hl2 + mult * atr
    lb = hl2 - mult * atr
    st = np.full_like(close, np.nan)
    d = np.full_like(close, 1.0)
    for i in range(1, len(close)):
        if np.isnan(atr[i]):
            continue
        if ub[i] < ub[i-1] or close[i-1] > ub[i-1]:
            pass
        else:
            ub[i] = ub[i-1]
        if lb[i] > lb[i-1] or close[i-1] < lb[i-1]:
            pass
        else:
            lb[i] = lb[i-1]
        if not np.isnan(st[i-1]):
            if st[i-1] == ub[i-1]:
                if close[i] <= ub[i]:
                    st[i] = ub[i]; d[i] = -1
                else:
                    st[i] = lb[i]; d[i] = 1
            else:
                if close[i] >= lb[i]:
                    st[i] = lb[i]; d[i] = 1
                else:
                    st[i] = ub[i]; d[i] = -1
        else:
            st[i] = lb[i]; d[i] = 1
    return d


class SuperTrendStrategy(Strategy):
    def init(self):
        self.direction = self.I(calc_supertrend_dir, self.data.High,
                                self.data.Low, self.data.Close)

    def next(self):
        if self.direction[-1] == 1 and self.direction[-2] == -1:
            self.buy()
        elif self.direction[-1] == -1 and self.direction[-2] == 1:
            if self.position:
                self.position.close()


bt = Backtest(data, SuperTrendStrategy, cash=1_000_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r1_06_supertrend")
