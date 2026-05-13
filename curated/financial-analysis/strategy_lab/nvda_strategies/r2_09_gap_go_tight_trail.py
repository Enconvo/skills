"""
ROUND 2 — Strategy 09: Gap-and-Go with Tight Trailing Stop
============================================================
Evolved from R1-13 (Gap-and-Go, 451% but -48.5% drawdown).
Fix: Tighter ATR trailing stop (1.5x vs 2.5x) + EMA filter to reduce drawdown.
Sacrifice some return for much better risk control.
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


def calc_atr(high, low, close, period):
    return talib.ATR(high, low, close, timeperiod=period)


def calc_ema(close, period):
    return talib.EMA(close, timeperiod=period)


def calc_sma(close, period):
    return talib.SMA(close, timeperiod=period)


class GapGoTightTrail(Strategy):
    gap_threshold = 1.5
    atr_period = 14
    atr_mult = 1.5        # tighter than R1 (was 2.5)
    ema_short = 21
    sma_long = 50

    def init(self):
        self.gap = self.I(calc_gap_pct, self.data.Open, self.data.Close)
        self.atr = self.I(calc_atr, self.data.High, self.data.Low, self.data.Close, self.atr_period)
        self.ema = self.I(calc_ema, self.data.Close, self.ema_short)
        self.sma = self.I(calc_sma, self.data.Close, self.sma_long)
        self.trail_stop = 0

    def next(self):
        price = self.data.Close[-1]

        if not self.position:
            if (self.gap[-1] > self.gap_threshold and
                    price > self.ema[-1] and
                    price > self.sma[-1] and
                    not np.isnan(self.atr[-1])):
                self.buy()
                self.trail_stop = price - self.atr[-1] * self.atr_mult
        else:
            new_trail = price - self.atr[-1] * self.atr_mult
            if new_trail > self.trail_stop:
                self.trail_stop = new_trail
            if price < self.trail_stop:
                self.position.close()


bt = Backtest(data, GapGoTightTrail, cash=1_000_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r2_09_gap_go_tight_trail")
