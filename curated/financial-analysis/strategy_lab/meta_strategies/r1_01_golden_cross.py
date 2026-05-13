#!/usr/bin/env python3
"""
Round 1 Strategy 01: Golden Cross (SMA 50/200)
Classic trend-following strategy. Buy when SMA50 crosses above SMA200, sell when crosses below.
"""
from backtesting import Strategy
from backtesting.lib import crossover
import talib
import sys
sys.path.append("..")
from utils import load_meta_data

def sma(data, period):
    return talib.SMA(data, timeperiod=period)

class GoldenCross(Strategy):
    sma_fast = 50
    sma_slow = 200

    def init(self):
        self.sma50 = self.I(sma, self.data.Close, self.sma_fast)
        self.sma200 = self.I(sma, self.data.Close, self.sma_slow)

    def next(self):
        if crossover(self.sma50, self.sma200):
            self.buy()
        elif crossover(self.sma200, self.sma50):
            self.position.close()

if __name__ == "__main__":
    from backtesting import Backtest
    data = load_meta_data("1h")
    bt = Backtest(data, GoldenCross, cash=100_000, commission=.002)
    stats = bt.run()
    print(stats)
