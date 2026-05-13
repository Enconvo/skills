#!/usr/bin/env python3
"""
Round 1 Strategy 07: Donchian Channel Breakout
Buy on 20-period high, sell on 20-period low.
"""
from backtesting import Strategy
import pandas as pd
import sys
sys.path.append("..")
from utils import load_meta_data

def donchian_upper(high, period=20):
    return pd.Series(high).rolling(period).max().values

def donchian_lower(low, period=20):
    return pd.Series(low).rolling(period).min().values

class DonchianBreakout(Strategy):
    donchian_period = 20

    def init(self):
        self.upper = self.I(donchian_upper, self.data.High, self.donchian_period)
        self.lower = self.I(donchian_lower, self.data.Low, self.donchian_period)

    def next(self):
        if self.data.Close[-1] >= self.upper[-2] and not self.position:
            self.buy()
        elif self.data.Close[-1] <= self.lower[-2] and self.position:
            self.position.close()

if __name__ == "__main__":
    from backtesting import Backtest
    data = load_meta_data("1h")
    bt = Backtest(data, DonchianBreakout, cash=100_000, commission=.002)
    stats = bt.run()
    print(stats)
