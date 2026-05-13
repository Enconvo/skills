#!/usr/bin/env python3
"""
Round 1 Strategy 06: Stochastic RSI
Buy when StochRSI crosses above 20, sell when crosses below 80.
"""
from backtesting import Strategy
import talib
import numpy as np
import sys
sys.path.append("..")
from utils import load_meta_data

def stochrsi_k(data, period=14):
    fastk, fastd = talib.STOCHRSI(data, timeperiod=period, fastk_period=5, fastd_period=3)
    return fastk

class StochRSIStrategy(Strategy):
    rsi_period = 14
    k_lower = 20
    k_upper = 80

    def init(self):
        self.stochrsi = self.I(stochrsi_k, self.data.Close, self.rsi_period)

    def next(self):
        if self.stochrsi[-1] > self.k_lower and self.stochrsi[-2] <= self.k_lower and not self.position:
            self.buy()
        elif self.stochrsi[-1] < self.k_upper and self.stochrsi[-2] >= self.k_upper and self.position:
            self.position.close()

if __name__ == "__main__":
    from backtesting import Backtest
    data = load_meta_data("1h")
    bt = Backtest(data, StochRSIStrategy, cash=100_000, commission=.002)
    stats = bt.run()
    print(stats)
