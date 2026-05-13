"""
ROUND 2 — Strategy 02: StochRSI + EMA Ribbon Filter
====================================================
EVOLUTION: Combines #3 (StochRSI, 70% win rate) with #2 (EMA Ribbon trend filter).
Buy when StochRSI K crosses above D below 20 AND EMAs are stacked bullish (8>21>55).
This filters oversold bounces to only trade in strong uptrends.
Exit when StochRSI overbought OR EMA stack breaks.

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

def ema(close, period):
    return talib.EMA(close, timeperiod=period)


class StochRSIEMAFilter(Strategy):
    rsi_period = 14
    k_period = 14
    d_period = 3

    def init(self):
        self.k = self.I(stoch_rsi_k, self.data.Close, self.rsi_period, self.k_period, self.d_period)
        self.d = self.I(stoch_rsi_d, self.data.Close, self.rsi_period, self.k_period, self.d_period)
        self.ema8 = self.I(ema, self.data.Close, 8)
        self.ema21 = self.I(ema, self.data.Close, 21)
        self.ema55 = self.I(ema, self.data.Close, 55)

    def next(self):
        bullish_stack = (self.ema8[-1] > self.ema21[-1] > self.ema55[-1])

        if (crossover(self.k, self.d) and self.k[-1] < 25 and
            bullish_stack and not self.position):
            self.buy()
        elif self.position:
            if (crossover(self.d, self.k) and self.k[-1] > 75) or self.ema8[-1] < self.ema21[-1]:
                self.position.close()


bt = Backtest(data, StochRSIEMAFilter, cash=100_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r2_02_stochrsi_ema_filter")
