"""
ROUND 1 — Strategy 05: Donchian Channel Breakout (Turtle Trading)
=================================================================
Buy when price breaks above 20-period high (breakout).
Exit when price breaks below 10-period low (trailing exit).
The original Turtle Trading system. Works great on trending assets.

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


def donchian_high(high, period):
    out = np.full_like(high, np.nan)
    for i in range(period, len(high)):
        out[i] = np.max(high[i-period:i])
    return out

def donchian_low(low, period):
    out = np.full_like(low, np.nan)
    for i in range(period, len(low)):
        out[i] = np.min(low[i-period:i])
    return out


class DonchianBreakout(Strategy):
    entry_period = 20
    exit_period = 10

    def init(self):
        self.entry_high = self.I(donchian_high, self.data.High, self.entry_period)
        self.exit_low = self.I(donchian_low, self.data.Low, self.exit_period)

    def next(self):
        price = self.data.Close[-1]
        if price > self.entry_high[-1] and not self.position:
            self.buy()
        elif price < self.exit_low[-1] and self.position:
            self.position.close()


bt = Backtest(data, DonchianBreakout, cash=100_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r1_05_donchian_breakout")
