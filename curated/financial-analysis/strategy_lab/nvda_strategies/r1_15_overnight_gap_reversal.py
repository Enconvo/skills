"""
ROUND 1 — Strategy 15: Overnight Gap Reversal
===============================================
Buy gap-downs >2% at open, sell when the gap fills (intraday mean reversion).
Works on the principle that overnight panic selling often overshoots — smart
money buys the open dip and price reverts toward yesterday's close.
Uses daily bars — entry at open, exit on gap fill or time stop.
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
    gap = np.full_like(open_price, np.nan)
    gap[1:] = (open_price[1:] - close_price[:-1]) / close_price[:-1] * 100
    return gap


def calc_sma(close, period):
    return talib.SMA(close, timeperiod=period)


def calc_atr(high, low, close, period):
    return talib.ATR(high, low, close, timeperiod=period)


class OvernightGapReversal(Strategy):
    gap_threshold = -2.0   # gap-down % threshold
    sma_period = 200       # only buy in long-term uptrend
    hold_max = 3           # max hold days
    atr_period = 14

    def init(self):
        self.gap = self.I(calc_gap_pct, self.data.Open, self.data.Close)
        self.sma = self.I(calc_sma, self.data.Close, self.sma_period)
        self.atr = self.I(calc_atr, self.data.High, self.data.Low, self.data.Close, self.atr_period)
        self.entry_bar = 0
        self.target = 0

    def next(self):
        bar = len(self.data) - 1
        price = self.data.Close[-1]

        if not self.position:
            # Buy gap-downs in uptrend
            if (self.gap[-1] < self.gap_threshold and
                    price > self.sma[-1] and
                    not np.isnan(self.atr[-1])):
                self.buy()
                self.entry_bar = bar
                self.target = self.data.Close[-2]  # target = previous close (gap fill)
        else:
            # Exit: gap filled, time stop, or hard stop
            if self.data.High[-1] >= self.target:
                self.position.close()
            elif (bar - self.entry_bar) >= self.hold_max:
                self.position.close()
            elif price < self.data.Open[self.entry_bar] - self.atr[-1] * 2:
                self.position.close()


bt = Backtest(data, OvernightGapReversal, cash=1_000_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r1_15_overnight_gap_reversal")
