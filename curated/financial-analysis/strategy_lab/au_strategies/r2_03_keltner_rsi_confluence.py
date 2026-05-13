"""
ROUND 2 — Strategy 03: Keltner + RSI Confluence
================================================
EVOLUTION: Combines #5 (Keltner, 71% win rate, lowest DD) with #1 (RSI momentum).
Buy when price touches lower Keltner AND RSI < 40 (double oversold confirmation).
Exit at middle Keltner OR RSI > 65.
Double filter = fewer but higher quality trades.

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


def calc_rsi(close, period):
    return talib.RSI(close, timeperiod=period)

_kc_cache = {}

def _get_keltner(high, low, close, period, mult):
    key = (id(high), id(low), id(close), period, mult)
    if key not in _kc_cache:
        ema_val = talib.EMA(close, timeperiod=period)
        atr = talib.ATR(high, low, close, timeperiod=period)
        _kc_cache[key] = (ema_val, ema_val - mult * atr)
    return _kc_cache[key]

def keltner_middle(close, period):
    return talib.EMA(close, timeperiod=period)

def keltner_lower(high, low, close, period, mult):
    return _get_keltner(high, low, close, period, mult)[1]


class KeltnerRSIConfluence(Strategy):
    kc_period = 20
    kc_mult = 2.0
    rsi_period = 14
    rsi_buy = 40
    rsi_sell = 65

    def init(self):
        self.rsi = self.I(calc_rsi, self.data.Close, self.rsi_period)
        self.kc_mid = self.I(keltner_middle, self.data.Close, self.kc_period)
        self.kc_low = self.I(keltner_lower, self.data.High, self.data.Low,
                             self.data.Close, self.kc_period, self.kc_mult)

    def next(self):
        price = self.data.Close[-1]
        if (price <= self.kc_low[-1] and
            self.rsi[-1] < self.rsi_buy and
            not self.position):
            self.buy()
        elif self.position:
            if price >= self.kc_mid[-1] or self.rsi[-1] > self.rsi_sell:
                self.position.close()


bt = Backtest(data, KeltnerRSIConfluence, cash=100_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r2_03_keltner_rsi_confluence")
