"""
ROUND 1 — Strategy 13: Gap-and-Go
===================================
Buy when NVDA gaps up >1.5% at the open (strong momentum signal).
Use ATR trailing stop to ride the move. Exit when momentum fades.
Works best on high-momentum stocks like NVDA where gaps signal institutional buying.
"""
import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_nvda_data

data = load_nvda_data("daily")


def calc_gap_pct(open_price, close_price):
    """Gap % = (today's open - yesterday's close) / yesterday's close * 100."""
    gap = np.full_like(open_price, np.nan)
    gap[1:] = (open_price[1:] - close_price[:-1]) / close_price[:-1] * 100
    return gap


def calc_atr(high, low, close, period):
    return talib.ATR(high, low, close, timeperiod=period)


def calc_sma(close, period):
    return talib.SMA(close, timeperiod=period)


class GapAndGo(Strategy):
    gap_threshold = 1.5   # min gap % to trigger entry
    atr_period = 14
    atr_mult = 2.5        # trailing stop multiplier
    sma_period = 50       # trend filter

    def init(self):
        self.gap = self.I(calc_gap_pct, self.data.Open, self.data.Close)
        self.atr = self.I(calc_atr, self.data.High, self.data.Low, self.data.Close, self.atr_period)
        self.sma = self.I(calc_sma, self.data.Close, self.sma_period)
        self.trail_stop = 0

    def next(self):
        price = self.data.Close[-1]

        if not self.position:
            # Buy on gap-up above threshold, only in uptrend
            if (self.gap[-1] > self.gap_threshold and
                    price > self.sma[-1] and
                    not np.isnan(self.atr[-1])):
                self.buy()
                self.trail_stop = price - self.atr[-1] * self.atr_mult
        else:
            # Update trailing stop
            new_trail = price - self.atr[-1] * self.atr_mult
            if new_trail > self.trail_stop:
                self.trail_stop = new_trail
            # Exit if price drops below trailing stop
            if price < self.trail_stop:
                self.position.close()


bt = Backtest(data, GapAndGo, cash=1_000_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r1_13_gap_and_go")
