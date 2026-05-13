"""
ROUND 2 — Strategy 08: Keltner Mean Reversion + ATR Trailing
==============================================================
EVOLUTION: Keltner reversion (#2, 91.7%) with ATR trailing stop
instead of fixed upper Keltner exit. Should capture bigger moves.
"""
import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_nvda_data

data = load_nvda_data("1h")


def calc_kc_lower(high, low, close, period=20, mult=2.0):
    mid = talib.EMA(close, timeperiod=period)
    atr = talib.ATR(high, low, close, timeperiod=period)
    return mid - mult * atr

def calc_atr(high, low, close, period):
    return talib.ATR(high, low, close, timeperiod=period)


class KeltnerATRTrailing(Strategy):
    atr_mult = 2.0

    def init(self):
        self.kc_lower = self.I(calc_kc_lower, self.data.High, self.data.Low, self.data.Close)
        self.atr = self.I(calc_atr, self.data.High, self.data.Low, self.data.Close, 14)
        self.highest = 0
        self.trail_stop = 0

    def next(self):
        price = self.data.Close[-1]
        atr_val = self.atr[-1]
        if np.isnan(atr_val):
            return
        if not self.position:
            if price <= self.kc_lower[-1]:
                self.buy()
                self.highest = price
                self.trail_stop = price - self.atr_mult * atr_val
        else:
            if price > self.highest:
                self.highest = price
            new_stop = self.highest - self.atr_mult * atr_val
            if new_stop > self.trail_stop:
                self.trail_stop = new_stop
            if price < self.trail_stop:
                self.position.close()
                self.highest = 0
                self.trail_stop = 0


bt = Backtest(data, KeltnerATRTrailing, cash=1_000_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r2_08_keltner_atr_trailing")
