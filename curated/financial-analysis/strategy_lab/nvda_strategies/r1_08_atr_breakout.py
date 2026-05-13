"""
ROUND 1 — Strategy 08: ATR Volatility Breakout
===============================================
Buy when price moves more than 2x ATR above the 20-period SMA.
This signals a volatility expansion / breakout.
Exit when price drops back to SMA.
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


class ATRBreakout(Strategy):
    sma_period = 20
    atr_period = 14
    atr_mult = 2.0

    def init(self):
        self.sma = self.I(calc_sma, self.data.Close, self.sma_period)
        self.atr = self.I(calc_atr, self.data.High, self.data.Low,
                          self.data.Close, self.atr_period)

    def next(self):
        price = self.data.Close[-1]
        if np.isnan(self.atr[-1]):
            return
        breakout_level = self.sma[-1] + self.atr_mult * self.atr[-1]
        if not self.position:
            if price > breakout_level:
                self.buy()
        else:
            if price < self.sma[-1]:
                self.position.close()


bt = Backtest(data, ATRBreakout, cash=1_000_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r1_08_atr_breakout")
