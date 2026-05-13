#!/usr/bin/env python3
"""
Round 1 Strategy 12: CCI (Commodity Channel Index) Momentum
Buy when CCI crosses above -100, sell when crosses below +100.
"""
from backtesting import Strategy
import talib
import sys
sys.path.append("..")
from utils import load_meta_data

def cci_ind(high, low, close, period=20):
    return talib.CCI(high, low, close, timeperiod=period)

class CCIMomentum(Strategy):
    cci_period = 20
    cci_lower = -100
    cci_upper = 100

    def init(self):
        self.cci = self.I(cci_ind, self.data.High, self.data.Low, self.data.Close, self.cci_period)

    def next(self):
        if self.cci[-1] > self.cci_lower and self.cci[-2] <= self.cci_lower and not self.position:
            self.buy()
        elif self.cci[-1] < self.cci_upper and self.cci[-2] >= self.cci_upper and self.position:
            self.position.close()

if __name__ == "__main__":
    from backtesting import Backtest
    data = load_meta_data("1h")
    bt = Backtest(data, CCIMomentum, cash=100_000, commission=.002)
    stats = bt.run()
    print(stats)
