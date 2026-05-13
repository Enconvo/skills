"""
ROUND 1 — Strategy 09: Stochastic RSI Oversold Bounce
======================================================
Buy when StochRSI K line crosses above D line while both are below 20
(oversold momentum shift). Sell when K crosses below D above 80.
Combines RSI sensitivity with stochastic timing.

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


_stochrsi_cache = {}

def _get_stoch_rsi(close, rsi_period, k_period, d_period):
    key = (id(close), rsi_period, k_period, d_period)
    if key not in _stochrsi_cache:
        rsi = talib.RSI(close, timeperiod=rsi_period)
        _stochrsi_cache[key] = talib.STOCH(rsi, rsi, rsi, fastk_period=k_period, slowk_period=3, slowd_period=d_period)
    return _stochrsi_cache[key]

def stoch_rsi_k(close, rsi_period, k_period, d_period):
    return _get_stoch_rsi(close, rsi_period, k_period, d_period)[0]

def stoch_rsi_d(close, rsi_period, k_period, d_period):
    return _get_stoch_rsi(close, rsi_period, k_period, d_period)[1]


class StochRSIOversold(Strategy):
    rsi_period = 14
    k_period = 14
    d_period = 3

    def init(self):
        self.k = self.I(stoch_rsi_k, self.data.Close, self.rsi_period, self.k_period, self.d_period)
        self.d = self.I(stoch_rsi_d, self.data.Close, self.rsi_period, self.k_period, self.d_period)

    def next(self):
        if crossover(self.k, self.d) and self.k[-1] < 20 and not self.position:
            self.buy()
        elif crossover(self.d, self.k) and self.k[-1] > 80 and self.position:
            self.position.close()


bt = Backtest(data, StochRSIOversold, cash=100_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r1_09_stoch_rsi_oversold")
