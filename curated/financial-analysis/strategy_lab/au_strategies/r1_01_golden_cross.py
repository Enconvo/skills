"""
ROUND 1 — Strategy 01: Golden Cross / Death Cross
===================================================
Classic trend-following: 50 SMA crosses above 200 SMA = buy, below = sell.
Simple, proven on gold-related stocks. AU is a gold miner so this should
capture big macro trends.

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


def sma_fast(close, period):
    return talib.SMA(close, timeperiod=period)

def sma_slow(close, period):
    return talib.SMA(close, timeperiod=period)


class GoldenCross(Strategy):
    fast_period = 50
    slow_period = 200

    def init(self):
        self.fast_ma = self.I(sma_fast, self.data.Close, self.fast_period)
        self.slow_ma = self.I(sma_slow, self.data.Close, self.slow_period)

    def next(self):
        if crossover(self.fast_ma, self.slow_ma):
            self.buy()
        elif crossover(self.slow_ma, self.fast_ma):
            self.position.close()


bt = Backtest(data, GoldenCross, cash=100_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r1_01_golden_cross")
