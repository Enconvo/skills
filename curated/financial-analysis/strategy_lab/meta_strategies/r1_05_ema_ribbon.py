#!/usr/bin/env python3
"""
Round 1 Strategy 05: EMA Ribbon (8/21/55)
Buy when EMA8 > EMA21 > EMA55, sell when order reverses.
"""
from backtesting import Strategy
import talib
import sys
sys.path.append("..")
from utils import load_meta_data

def ema(data, period):
    return talib.EMA(data, timeperiod=period)

class EMARibbon(Strategy):
    ema_fast = 8
    ema_mid = 21
    ema_slow = 55

    def init(self):
        self.ema8 = self.I(ema, self.data.Close, self.ema_fast)
        self.ema21 = self.I(ema, self.data.Close, self.ema_mid)
        self.ema55 = self.I(ema, self.data.Close, self.ema_slow)

    def next(self):
        if self.ema8[-1] > self.ema21[-1] > self.ema55[-1] and not self.position:
            self.buy()
        elif self.ema8[-1] < self.ema21[-1] and self.position:
            self.position.close()

if __name__ == "__main__":
    from backtesting import Backtest
    data = load_meta_data("1h")
    bt = Backtest(data, EMARibbon, cash=100_000, commission=.002)
    stats = bt.run()
    print(stats)
