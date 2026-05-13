"""
ROUND 2 — Strategy 04: ATR Breakout + Trailing Stop
=====================================================
EVOLUTION: ATR breakout had best risk (DD -15.5%). Replace fixed SMA exit
with ATR trailing stop to let winners run further.
"""
import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_nvda_data

data = load_nvda_data("1h")


def calc_sma(close, period):
    return talib.SMA(close, timeperiod=period)

def calc_atr(high, low, close, period):
    return talib.ATR(high, low, close, timeperiod=period)


class ATRBreakoutTrailing(Strategy):
    sma_period = 20
    atr_period = 14
    entry_mult = 2.0
    trail_mult = 2.5

    def init(self):
        self.sma = self.I(calc_sma, self.data.Close, self.sma_period)
        self.atr = self.I(calc_atr, self.data.High, self.data.Low,
                          self.data.Close, self.atr_period)
        self.highest = 0
        self.trail_stop = 0

    def next(self):
        price = self.data.Close[-1]
        atr_val = self.atr[-1]
        if np.isnan(atr_val):
            return
        if not self.position:
            breakout_level = self.sma[-1] + self.entry_mult * atr_val
            if price > breakout_level:
                self.buy()
                self.highest = price
                self.trail_stop = price - self.trail_mult * atr_val
        else:
            if price > self.highest:
                self.highest = price
            new_stop = self.highest - self.trail_mult * atr_val
            if new_stop > self.trail_stop:
                self.trail_stop = new_stop
            if price < self.trail_stop:
                self.position.close()
                self.highest = 0
                self.trail_stop = 0


bt = Backtest(data, ATRBreakoutTrailing, cash=1_000_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r2_04_atr_breakout_trailing")
