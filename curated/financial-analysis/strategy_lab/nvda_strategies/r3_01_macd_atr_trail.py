"""
ROUND 3 — Strategy 01: MACD Momentum + ATR Trailing (Max Return)
================================================================
EVOLUTION: MACD crossover is #1 (98%) but -27.6% DD. Add ATR trailing
to lock in profits during big runs while keeping the momentum entries.
Wider trail (3x ATR) since NVDA is volatile.
"""
import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_nvda_data

data = load_nvda_data("1h")


_macd_cache = {}

def calc_macd(close):
    key = id(close)
    if key not in _macd_cache:
        _macd_cache[key] = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
    return _macd_cache[key][0]

def calc_macd_signal(close):
    key = id(close)
    if key not in _macd_cache:
        _macd_cache[key] = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
    return _macd_cache[key][1]

def calc_atr(high, low, close, period):
    return talib.ATR(high, low, close, timeperiod=period)


class MACDATRTrail(Strategy):
    atr_mult = 3.0

    def init(self):
        self.macd = self.I(calc_macd, self.data.Close)
        self.signal = self.I(calc_macd_signal, self.data.Close)
        self.atr = self.I(calc_atr, self.data.High, self.data.Low, self.data.Close, 14)
        self.highest = 0
        self.trail_stop = 0

    def next(self):
        price = self.data.Close[-1]
        atr_val = self.atr[-1]
        if np.isnan(atr_val):
            return
        if not self.position:
            if crossover(self.macd, self.signal):
                self.buy()
                self.highest = price
                self.trail_stop = price - self.atr_mult * atr_val
        else:
            if price > self.highest:
                self.highest = price
            new_stop = self.highest - self.atr_mult * atr_val
            if new_stop > self.trail_stop:
                self.trail_stop = new_stop
            # Exit on either MACD bearish cross OR trailing stop hit
            if crossover(self.signal, self.macd) or price < self.trail_stop:
                self.position.close()
                self.highest = 0
                self.trail_stop = 0


bt = Backtest(data, MACDATRTrail, cash=1_000_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r3_01_macd_atr_trail")
