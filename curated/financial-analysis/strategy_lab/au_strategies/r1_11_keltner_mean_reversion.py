"""
ROUND 1 — Strategy 11: Keltner Channel Mean Reversion
=====================================================
Buy when price touches lower Keltner Channel (oversold dip).
Sell when price reaches middle band (EMA).
Gold miners often snap back after touching lower channels.

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


_kc_cache = {}

def _get_keltner(high, low, close, period, mult):
    key = (id(high), id(low), id(close), period, mult)
    if key not in _kc_cache:
        ema_val = talib.EMA(close, timeperiod=period)
        atr = talib.ATR(high, low, close, timeperiod=period)
        _kc_cache[key] = (ema_val + mult * atr, ema_val, ema_val - mult * atr)
    return _kc_cache[key]

def keltner_upper(high, low, close, period, mult):
    return _get_keltner(high, low, close, period, mult)[0]

def keltner_middle(close, period):
    return talib.EMA(close, timeperiod=period)

def keltner_lower(high, low, close, period, mult):
    return _get_keltner(high, low, close, period, mult)[2]


class KeltnerMeanReversion(Strategy):
    kc_period = 20
    kc_mult = 2.0

    def init(self):
        self.upper = self.I(keltner_upper, self.data.High, self.data.Low,
                            self.data.Close, self.kc_period, self.kc_mult)
        self.middle = self.I(keltner_middle, self.data.Close, self.kc_period)
        self.lower = self.I(keltner_lower, self.data.High, self.data.Low,
                            self.data.Close, self.kc_period, self.kc_mult)

    def next(self):
        price = self.data.Close[-1]
        if price <= self.lower[-1] and not self.position:
            self.buy()
        elif price >= self.middle[-1] and self.position:
            self.position.close()


bt = Backtest(data, KeltnerMeanReversion, cash=100_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r1_11_keltner_mean_reversion")
