"""
ROUND 1 — Strategy 01: Golden Cross (SMA 50/200)
==================================================
Classic trend-following. Buy when SMA 50 crosses above SMA 200.
Sell when SMA 50 crosses below SMA 200.
"""
import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_nvda_data

data = load_nvda_data("1h")


def calc_sma(close, period):
    return talib.SMA(close, timeperiod=period)


class GoldenCross(Strategy):
    fast_period = 50
    slow_period = 200

    def init(self):
        self.sma_fast = self.I(calc_sma, self.data.Close, self.fast_period)
        self.sma_slow = self.I(calc_sma, self.data.Close, self.slow_period)

    def next(self):
        if crossover(self.sma_fast, self.sma_slow):
            self.buy()
        elif crossover(self.sma_slow, self.sma_fast):
            if self.position:
                self.position.close()


bt = Backtest(data, GoldenCross, cash=1_000_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r1_01_golden_cross")
