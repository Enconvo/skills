"""
ROUND 1 — Strategy 03: Bollinger Band Breakout
===============================================
Buy when price closes above upper Bollinger Band (momentum breakout).
Close when price falls back below middle band (SMA).
AU tends to have strong breakout moves when gold spikes.

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


_bb_cache = {}

def _get_bbands(close, period, nbdev):
    key = (id(close), period, nbdev)
    if key not in _bb_cache:
        _bb_cache[key] = talib.BBANDS(close, timeperiod=period, nbdevup=nbdev, nbdevdn=nbdev)
    return _bb_cache[key]

def calc_bb_upper(close, period, nbdev):
    return _get_bbands(close, period, nbdev)[0]

def calc_bb_middle(close, period, nbdev):
    return _get_bbands(close, period, nbdev)[1]

def calc_bb_lower(close, period, nbdev):
    return _get_bbands(close, period, nbdev)[2]


class BollingerBreakout(Strategy):
    bb_period = 20
    bb_std = 2.0

    def init(self):
        self.upper = self.I(calc_bb_upper, self.data.Close, self.bb_period, self.bb_std)
        self.middle = self.I(calc_bb_middle, self.data.Close, self.bb_period, self.bb_std)
        self.lower = self.I(calc_bb_lower, self.data.Close, self.bb_period, self.bb_std)

    def next(self):
        price = self.data.Close[-1]
        if price > self.upper[-1] and not self.position:
            self.buy()
        elif price < self.middle[-1] and self.position:
            self.position.close()


bt = Backtest(data, BollingerBreakout, cash=100_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r1_03_bollinger_breakout")
