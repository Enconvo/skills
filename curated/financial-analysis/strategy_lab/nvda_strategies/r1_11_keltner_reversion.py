"""
ROUND 1 — Strategy 11: Keltner Channel Mean Reversion
======================================================
Buy when price touches lower Keltner Channel (oversold bounce).
Sell when price touches upper Keltner Channel.
"""
import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_nvda_data

data = load_nvda_data("1h")


def calc_kc_upper(high, low, close, period=20, mult=2.0):
    mid = talib.EMA(close, timeperiod=period)
    atr = talib.ATR(high, low, close, timeperiod=period)
    return mid + mult * atr

def calc_kc_lower(high, low, close, period=20, mult=2.0):
    mid = talib.EMA(close, timeperiod=period)
    atr = talib.ATR(high, low, close, timeperiod=period)
    return mid - mult * atr


class KeltnerReversion(Strategy):
    def init(self):
        self.kc_upper = self.I(calc_kc_upper, self.data.High, self.data.Low, self.data.Close)
        self.kc_lower = self.I(calc_kc_lower, self.data.High, self.data.Low, self.data.Close)

    def next(self):
        price = self.data.Close[-1]
        if not self.position:
            if price <= self.kc_lower[-1]:
                self.buy()
        else:
            if price >= self.kc_upper[-1]:
                self.position.close()


bt = Backtest(data, KeltnerReversion, cash=1_000_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r1_11_keltner_reversion")
