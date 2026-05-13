"""
ROUND 3 — Strategy 03: Safe Momentum Compounder (Best Expectancy)
==================================================================
EVOLUTION: ATR breakout (best risk, -15.5% DD) + squeeze filter (best Sharpe).
Only enter breakout when coming out of a low-volatility squeeze.
Tight 2x ATR trailing. Optimized for highest expectancy per trade.
"""
import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_nvda_data

data = load_nvda_data("1h")


def calc_sma(close, period):
    return talib.SMA(close, timeperiod=period)

def calc_atr(high, low, close, period):
    return talib.ATR(high, low, close, timeperiod=period)

def calc_bb_squeeze(high, low, close):
    """1 = squeeze is on, 0 = no squeeze"""
    bb_upper, bb_mid, bb_lower = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2)
    kc_mid = talib.EMA(close, timeperiod=20)
    kc_atr = talib.ATR(high, low, close, timeperiod=20)
    kc_upper = kc_mid + 1.5 * kc_atr
    kc_lower = kc_mid - 1.5 * kc_atr
    return ((bb_lower > kc_lower) & (bb_upper < kc_upper)).astype(float)


class SafeMomentum(Strategy):
    sma_period = 20
    atr_period = 14
    entry_mult = 1.5
    trail_mult = 2.0

    def init(self):
        self.sma = self.I(calc_sma, self.data.Close, self.sma_period)
        self.atr = self.I(calc_atr, self.data.High, self.data.Low, self.data.Close, self.atr_period)
        self.squeeze = self.I(calc_bb_squeeze, self.data.High, self.data.Low, self.data.Close)
        self.highest = 0
        self.trail_stop = 0
        self.was_squeezed = False

    def next(self):
        price = self.data.Close[-1]
        atr_val = self.atr[-1]
        if np.isnan(atr_val):
            return

        # Track if we were recently in a squeeze
        if self.squeeze[-1] == 1:
            self.was_squeezed = True

        if not self.position:
            # Enter: breakout from a squeeze
            breakout = price > self.sma[-1] + self.entry_mult * atr_val
            if breakout and self.was_squeezed:
                self.buy()
                self.highest = price
                self.trail_stop = price - self.trail_mult * atr_val
                self.was_squeezed = False
        else:
            if price > self.highest:
                self.highest = price
            new_stop = self.highest - self.trail_mult * atr_val
            if new_stop > self.trail_stop:
                self.trail_stop = new_stop
            if price < self.trail_stop:
                self.position.close()
                self.highest = 0
                self.trail_stop = 0


bt = Backtest(data, SafeMomentum, cash=1_000_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r3_03_safe_momentum")
