"""
ROUND 2 — Strategy 07: BB/Keltner Squeeze + ATR Trailing
==========================================================
EVOLUTION: Squeeze had best Sharpe (1.11) and lowest DD (-9.2%).
Add ATR trailing stop to let winners run instead of exiting on MACD flip.
"""
import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_nvda_data

data = load_nvda_data("1h")


def calc_squeeze_signal(high, low, close):
    bb_upper, bb_mid, bb_lower = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2)
    kc_mid = talib.EMA(close, timeperiod=20)
    kc_atr = talib.ATR(high, low, close, timeperiod=20)
    kc_upper = kc_mid + 1.5 * kc_atr
    kc_lower = kc_mid - 1.5 * kc_atr
    squeeze_on = (bb_lower > kc_lower) & (bb_upper < kc_upper)
    macd, signal, hist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
    result = np.zeros_like(close)
    for i in range(1, len(close)):
        if squeeze_on[i-1] and not squeeze_on[i]:
            if hist[i] > 0:
                result[i] = 1
    return result

def calc_atr(high, low, close, period):
    return talib.ATR(high, low, close, timeperiod=period)


class SqueezeATRTrail(Strategy):
    atr_mult = 2.5

    def init(self):
        self.squeeze = self.I(calc_squeeze_signal, self.data.High, self.data.Low, self.data.Close)
        self.atr = self.I(calc_atr, self.data.High, self.data.Low, self.data.Close, 14)
        self.highest = 0
        self.trail_stop = 0

    def next(self):
        price = self.data.Close[-1]
        atr_val = self.atr[-1]
        if np.isnan(atr_val):
            return
        if not self.position:
            if self.squeeze[-1] == 1:
                self.buy()
                self.highest = price
                self.trail_stop = price - self.atr_mult * atr_val
        else:
            if price > self.highest:
                self.highest = price
            new_stop = self.highest - self.atr_mult * atr_val
            if new_stop > self.trail_stop:
                self.trail_stop = new_stop
            if price < self.trail_stop:
                self.position.close()
                self.highest = 0
                self.trail_stop = 0


bt = Backtest(data, SqueezeATRTrail, cash=1_000_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r2_07_squeeze_atr_trail")
