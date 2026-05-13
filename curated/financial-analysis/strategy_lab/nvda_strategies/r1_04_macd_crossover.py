"""
ROUND 1 — Strategy 04: MACD Crossover
======================================
Buy when MACD crosses above signal line. Sell when MACD crosses below signal.
Classic momentum strategy.
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


class MACDCrossover(Strategy):
    def init(self):
        self.macd = self.I(calc_macd, self.data.Close)
        self.signal = self.I(calc_macd_signal, self.data.Close)

    def next(self):
        if crossover(self.macd, self.signal):
            if not self.position:
                self.buy()
        elif crossover(self.signal, self.macd):
            if self.position:
                self.position.close()


bt = Backtest(data, MACDCrossover, cash=1_000_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r1_04_macd_crossover")
