"""
ROUND 3 — Strategy 02: RSI Oversold + MACD Momentum Hybrid (Risk-Adjusted)
===========================================================================
EVOLUTION: Buy when RSI < 35 (mean reversion zone) AND MACD histogram
is turning positive (momentum confirming the bounce). Two signals agree.
ATR trailing exit. Optimized for high win rate + decent returns.
"""
import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_nvda_data

data = load_nvda_data("1h")


def calc_rsi(close, period):
    return talib.RSI(close, timeperiod=period)

def calc_macd_hist(close):
    m, s, h = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
    return h

def calc_atr(high, low, close, period):
    return talib.ATR(high, low, close, timeperiod=period)


class RSIMACDHybrid(Strategy):
    rsi_entry = 35
    atr_mult = 2.5

    def init(self):
        self.rsi = self.I(calc_rsi, self.data.Close, 14)
        self.hist = self.I(calc_macd_hist, self.data.Close)
        self.atr = self.I(calc_atr, self.data.High, self.data.Low, self.data.Close, 14)
        self.highest = 0
        self.trail_stop = 0

    def next(self):
        price = self.data.Close[-1]
        atr_val = self.atr[-1]
        if np.isnan(atr_val):
            return
        if not self.position:
            # RSI oversold + MACD histogram turning up
            if self.rsi[-1] < self.rsi_entry and self.hist[-1] > self.hist[-2]:
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


bt = Backtest(data, RSIMACDHybrid, cash=1_000_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r3_02_rsi_macd_hybrid")
