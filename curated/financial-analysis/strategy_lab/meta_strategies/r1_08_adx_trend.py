#!/usr/bin/env python3
"""
Round 1 Strategy 08: ADX + DI Crossover
Buy when +DI crosses above -DI and ADX > 25 (strong trend).
"""
from backtesting import Strategy
from backtesting.lib import crossover
import talib
import sys
sys.path.append("..")
from utils import load_meta_data

def adx_ind(high, low, close, period=14):
    return talib.ADX(high, low, close, timeperiod=period)

def plus_di(high, low, close, period=14):
    return talib.PLUS_DI(high, low, close, timeperiod=period)

def minus_di(high, low, close, period=14):
    return talib.MINUS_DI(high, low, close, timeperiod=period)

class ADXTrend(Strategy):
    adx_period = 14
    adx_threshold = 25

    def init(self):
        self.adx = self.I(adx_ind, self.data.High, self.data.Low, self.data.Close, self.adx_period)
        self.plus_di = self.I(plus_di, self.data.High, self.data.Low, self.data.Close, self.adx_period)
        self.minus_di = self.I(minus_di, self.data.High, self.data.Low, self.data.Close, self.adx_period)

    def next(self):
        if crossover(self.plus_di, self.minus_di) and self.adx[-1] > self.adx_threshold:
            if not self.position:
                self.buy()
        elif crossover(self.minus_di, self.plus_di):
            if self.position:
                self.position.close()

if __name__ == "__main__":
    from backtesting import Backtest
    data = load_meta_data("1h")
    bt = Backtest(data, ADXTrend, cash=100_000, commission=.002)
    stats = bt.run()
    print(stats)
