"""
ROUND 1 — Strategy 09: StochRSI Oversold Bounce
================================================
Buy when StochRSI K crosses above D below 20 (oversold zone).
Sell when K crosses below D above 80 (overbought zone).
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


_stochrsi_cache = {}

def _get_stochrsi(close, period, fk, fd):
    key = (id(close), period, fk, fd)
    if key not in _stochrsi_cache:
        _stochrsi_cache[key] = talib.STOCHRSI(close, timeperiod=period, fastk_period=fk, fastd_period=fd)
    return _stochrsi_cache[key]

def calc_stochrsi_k(close, period=14, fk=3, fd=3):
    return _get_stochrsi(close, period, fk, fd)[0]

def calc_stochrsi_d(close, period=14, fk=3, fd=3):
    return _get_stochrsi(close, period, fk, fd)[1]


class StochRSIOversold(Strategy):
    oversold = 20
    overbought = 80

    def init(self):
        self.k = self.I(calc_stochrsi_k, self.data.Close)
        self.d = self.I(calc_stochrsi_d, self.data.Close)

    def next(self):
        if not self.position:
            if crossover(self.k, self.d) and self.k[-1] < self.oversold:
                self.buy()
        else:
            if crossover(self.d, self.k) and self.k[-1] > self.overbought:
                self.position.close()


bt = Backtest(data, StochRSIOversold, cash=1_000_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r1_09_stochrsi_oversold")
