"""
ROUND 1 — Strategy 03: Bollinger Band Mean Reversion
=====================================================
Buy when price touches lower Bollinger Band (oversold bounce).
Sell when price touches upper Bollinger Band.
"""
import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_nvda_data

data = load_nvda_data("1h")


_bb_cache = {}

def _get_bbands(close, period, nbdev):
    key = (id(close), period, nbdev)
    if key not in _bb_cache:
        _bb_cache[key] = talib.BBANDS(close, timeperiod=period, nbdevup=nbdev, nbdevdn=nbdev)
    return _bb_cache[key]

def calc_bb_upper(close, period, nbdev):
    return _get_bbands(close, period, nbdev)[0]

def calc_bb_lower(close, period, nbdev):
    return _get_bbands(close, period, nbdev)[2]


class BollingerBounce(Strategy):
    bb_period = 20
    bb_std = 2.0

    def init(self):
        self.bb_upper = self.I(calc_bb_upper, self.data.Close, self.bb_period, self.bb_std)
        self.bb_lower = self.I(calc_bb_lower, self.data.Close, self.bb_period, self.bb_std)

    def next(self):
        price = self.data.Close[-1]
        if not self.position:
            if price <= self.bb_lower[-1]:
                self.buy()
        else:
            if price >= self.bb_upper[-1]:
                self.position.close()


bt = Backtest(data, BollingerBounce, cash=1_000_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r1_03_bollinger_bounce")
