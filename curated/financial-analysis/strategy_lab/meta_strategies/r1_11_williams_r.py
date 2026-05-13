#!/usr/bin/env python3
"""
Round 1 Strategy 11: Williams %R
Buy when %R crosses above -80 (oversold), sell when crosses below -20 (overbought).
"""
from backtesting import Strategy
import talib
import sys
sys.path.append("..")
from utils import load_meta_data

def willr(high, low, close, period=14):
    return talib.WILLR(high, low, close, timeperiod=period)

class WilliamsR(Strategy):
    willr_period = 14
    willr_lower = -80
    willr_upper = -20

    def init(self):
        self.willr = self.I(willr, self.data.High, self.data.Low, self.data.Close, self.willr_period)

    def next(self):
        if self.willr[-1] > self.willr_lower and self.willr[-2] <= self.willr_lower and not self.position:
            self.buy()
        elif self.willr[-1] < self.willr_upper and self.willr[-2] >= self.willr_upper and self.position:
            self.position.close()

if __name__ == "__main__":
    from backtesting import Backtest
    data = load_meta_data("1h")
    bt = Backtest(data, WilliamsR, cash=100_000, commission=.002)
    stats = bt.run()
    print(stats)
