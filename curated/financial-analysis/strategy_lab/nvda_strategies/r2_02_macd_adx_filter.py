"""
ROUND 2 — Strategy 02: MACD + ADX Filter
==========================================
EVOLUTION: MACD had best return (98%) but 39% win rate. Add ADX > 20
to only trade when a real trend exists, reducing whipsaw trades.
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

def calc_adx(high, low, close, period):
    return talib.ADX(high, low, close, timeperiod=period)


class MACDADXFilter(Strategy):
    adx_threshold = 20

    def init(self):
        self.macd = self.I(calc_macd, self.data.Close)
        self.signal = self.I(calc_macd_signal, self.data.Close)
        self.adx = self.I(calc_adx, self.data.High, self.data.Low,
                          self.data.Close, 14)

    def next(self):
        if not self.position:
            if crossover(self.macd, self.signal) and self.adx[-1] > self.adx_threshold:
                self.buy()
        else:
            if crossover(self.signal, self.macd):
                self.position.close()


bt = Backtest(data, MACDADXFilter, cash=1_000_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r2_02_macd_adx_filter")
