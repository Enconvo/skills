"""
ROUND 1 — Strategy 08: ATR Volatility Breakout
===============================================
Buy when price moves more than 2x ATR above 20-period SMA in a single bar
(volatility expansion = momentum). Exit with ATR trailing stop (1.5x ATR).
Catches explosive moves in AU.

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


def calc_atr(high, low, close, period):
    return talib.ATR(high, low, close, timeperiod=period)

def calc_sma(close, period):
    return talib.SMA(close, timeperiod=period)


class ATRVolatilityBreakout(Strategy):
    atr_period = 14
    sma_period = 20
    entry_mult = 2.0
    trail_mult = 1.5

    def init(self):
        self.atr = self.I(calc_atr, self.data.High, self.data.Low,
                          self.data.Close, self.atr_period)
        self.sma = self.I(calc_sma, self.data.Close, self.sma_period)
        self.trailing_stop = 0

    def next(self):
        price = self.data.Close[-1]
        atr_val = self.atr[-1]

        if np.isnan(atr_val) or np.isnan(self.sma[-1]):
            return

        if not self.position:
            if price > self.sma[-1] + self.entry_mult * atr_val:
                self.buy()
                self.trailing_stop = price - self.trail_mult * atr_val
        else:
            new_stop = price - self.trail_mult * atr_val
            if new_stop > self.trailing_stop:
                self.trailing_stop = new_stop
            if price < self.trailing_stop:
                self.position.close()


bt = Backtest(data, ATRVolatilityBreakout, cash=100_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r1_08_atr_volatility_breakout")
