"""
ROUND 2 — Strategy 05: RSI Entry + ATR Trailing Stop
=====================================================
EVOLUTION: Takes #1 (RSI, best returns) and adds smart ATR trailing stop
instead of fixed RSI exit. Lets winners run further.
Buy when RSI < 30. Trail stop at 2x ATR below highest close since entry.
This should capture more of AU's big moves.

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

def calc_atr(high, low, close, period):
    return talib.ATR(high, low, close, timeperiod=period)


class RSIATRTrailing(Strategy):
    rsi_period = 14
    rsi_entry = 30
    atr_period = 14
    atr_mult = 2.0

    def init(self):
        self.rsi = self.I(calc_rsi, self.data.Close, self.rsi_period)
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
            if self.rsi[-1] < self.rsi_entry:
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


bt = Backtest(data, RSIATRTrailing, cash=100_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r2_05_rsi_atr_trailing")
