#!/usr/bin/env python3
"""
Round 1 Strategy 04: Bollinger Band Bounce
Buy when price touches lower band, sell when touches upper band.
"""
from backtesting import Strategy
import talib
import sys
sys.path.append("..")
from utils import load_meta_data

_bb_cache = {}

def _get_bbands(data, period, std):
    key = (id(data), period, std)
    if key not in _bb_cache:
        _bb_cache[key] = talib.BBANDS(data, timeperiod=period, nbdevup=std, nbdevdn=std)
    return _bb_cache[key]

def bb_upper(data, period=20, std=2):
    return _get_bbands(data, period, std)[0]

def bb_lower(data, period=20, std=2):
    return _get_bbands(data, period, std)[2]

class BollingerBounce(Strategy):
    bb_period = 20
    bb_std = 2

    def init(self):
        self.bb_upper = self.I(bb_upper, self.data.Close, self.bb_period, self.bb_std)
        self.bb_lower = self.I(bb_lower, self.data.Close, self.bb_period, self.bb_std)

    def next(self):
        if self.data.Close[-1] <= self.bb_lower[-1] and not self.position:
            self.buy()
        elif self.data.Close[-1] >= self.bb_upper[-1] and self.position:
            self.position.close()

if __name__ == "__main__":
    from backtesting import Backtest
    data = load_meta_data("1h")
    bt = Backtest(data, BollingerBounce, cash=100_000, commission=.002)
    stats = bt.run()
    print(stats)
