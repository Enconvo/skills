"""
ROUND 1 — Strategy 04: MACD Trend Following
============================================
Buy when MACD line crosses above signal line (bullish momentum).
Sell when MACD crosses below signal (momentum fading).
Classic momentum indicator, works well on trending gold stocks.

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


_macd_cache = {}

def calc_macd(close):
    key = id(close)
    if key not in _macd_cache:
        _macd_cache[key] = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
    return _macd_cache[key][0]

def calc_macd_signal(close):
    key = id(close)
    if key not in _macd_cache:
        _macd_cache[key] = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
    return _macd_cache[key][1]


class MACDTrend(Strategy):
    def init(self):
        self.macd = self.I(calc_macd, self.data.Close)
        self.signal = self.I(calc_macd_signal, self.data.Close)

    def next(self):
        if crossover(self.macd, self.signal):
            self.buy()
        elif crossover(self.signal, self.macd):
            self.position.close()


bt = Backtest(data, MACDTrend, cash=100_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r1_04_macd_trend")
