#!/usr/bin/env python3
"""
Round 1 Strategy 09: Keltner Channel Mean Reversion
Buy when price touches lower Keltner, sell when touches upper.
"""
from backtesting import Strategy
import talib
import pandas as pd
import sys
sys.path.append("..")
from utils import load_meta_data

_kc_cache = {}

def _get_keltner(high, low, close, period, mult):
    key = (id(high), id(low), id(close), period, mult)
    if key not in _kc_cache:
        ema = talib.EMA(close, timeperiod=period)
        atr = talib.ATR(high, low, close, timeperiod=period)
        _kc_cache[key] = (ema + atr * mult, ema - atr * mult)
    return _kc_cache[key]

def keltner_upper(high, low, close, period=20, mult=2):
    return _get_keltner(high, low, close, period, mult)[0]

def keltner_lower(high, low, close, period=20, mult=2):
    return _get_keltner(high, low, close, period, mult)[1]

class KeltnerMeanReversion(Strategy):
    kc_period = 20
    kc_mult = 2

    def init(self):
        self.kc_upper = self.I(keltner_upper, self.data.High, self.data.Low, self.data.Close,
                               self.kc_period, self.kc_mult)
        self.kc_lower = self.I(keltner_lower, self.data.High, self.data.Low, self.data.Close,
                               self.kc_period, self.kc_mult)

    def next(self):
        if self.data.Close[-1] <= self.kc_lower[-1] and not self.position:
            self.buy()
        elif self.data.Close[-1] >= self.kc_upper[-1] and self.position:
            self.position.close()

if __name__ == "__main__":
    from backtesting import Backtest
    data = load_meta_data("1h")
    bt = Backtest(data, KeltnerMeanReversion, cash=100_000, commission=.002)
    stats = bt.run()
    print(stats)
