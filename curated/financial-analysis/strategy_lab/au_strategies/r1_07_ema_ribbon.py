"""
ROUND 1 — Strategy 07: EMA Ribbon Trend
========================================
Uses 3 EMAs (8, 21, 55). Buy when all three are stacked bullish
(8 > 21 > 55). Exit when 8 EMA crosses below 21 EMA.
Multi-timeframe trend confirmation.

STATS:
---
[pending]
---
"""
import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_au_data

data = load_au_data("1h")


def ema(close, period):
    return talib.EMA(close, timeperiod=period)


class EMARibbon(Strategy):
    fast = 8
    mid = 21
    slow = 55

    def init(self):
        self.ema_fast = self.I(ema, self.data.Close, self.fast)
        self.ema_mid = self.I(ema, self.data.Close, self.mid)
        self.ema_slow = self.I(ema, self.data.Close, self.slow)

    def next(self):
        bullish_stack = (self.ema_fast[-1] > self.ema_mid[-1] > self.ema_slow[-1])
        if bullish_stack and not self.position:
            self.buy()
        elif self.position and self.ema_fast[-1] < self.ema_mid[-1]:
            self.position.close()


bt = Backtest(data, EMARibbon, cash=100_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r1_07_ema_ribbon")
