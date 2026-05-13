"""
ROUND 2 — Strategy 03: Keltner + RSI Confluence
=================================================
EVOLUTION: Combine two mean reversion winners. Buy only when BOTH
price hits lower Keltner AND RSI < 40 (not as strict as 30).
Sell at upper Keltner or RSI > 70.
"""
import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_nvda_data

data = load_nvda_data("1h")


def calc_rsi(close, period):
    return talib.RSI(close, timeperiod=period)

_kc_cache = {}

def _get_kc(high, low, close, period, mult):
    key = (id(high), id(low), id(close), period, mult)
    if key not in _kc_cache:
        mid = talib.EMA(close, timeperiod=period)
        atr = talib.ATR(high, low, close, timeperiod=period)
        _kc_cache[key] = (mid + mult * atr, mid - mult * atr)
    return _kc_cache[key]

def calc_kc_upper(high, low, close, period=20, mult=2.0):
    return _get_kc(high, low, close, period, mult)[0]

def calc_kc_lower(high, low, close, period=20, mult=2.0):
    return _get_kc(high, low, close, period, mult)[1]


class KeltnerRSIConfluence(Strategy):
    rsi_entry = 40
    rsi_exit = 70

    def init(self):
        self.rsi = self.I(calc_rsi, self.data.Close, 14)
        self.kc_upper = self.I(calc_kc_upper, self.data.High, self.data.Low, self.data.Close)
        self.kc_lower = self.I(calc_kc_lower, self.data.High, self.data.Low, self.data.Close)

    def next(self):
        price = self.data.Close[-1]
        if not self.position:
            if price <= self.kc_lower[-1] and self.rsi[-1] < self.rsi_entry:
                self.buy()
        else:
            if price >= self.kc_upper[-1] or self.rsi[-1] > self.rsi_exit:
                self.position.close()


bt = Backtest(data, KeltnerRSIConfluence, cash=1_000_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r2_03_keltner_rsi_confluence")
