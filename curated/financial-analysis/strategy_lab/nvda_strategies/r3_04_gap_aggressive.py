"""
ROUND 3 — Strategy 04: Aggressive Gap Momentum (MAX RETURNS)
==============================================================
Evolved from R2-12 (445%, Sharpe 0.90). Optimized for maximum returns:
- Wider ATR trail (3.0x) to let winners run longer
- Lower gap threshold (open > prev high by any amount)
- MACD histogram confirmation retained
Goal: push returns higher, accept more drawdown.
"""
import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_nvda_data

data = load_nvda_data("daily")


def calc_atr(high, low, close, period):
    return talib.ATR(high, low, close, timeperiod=period)


def calc_ema(close, period):
    return talib.EMA(close, timeperiod=period)


def calc_macd_hist(close):
    _, _, hist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
    return hist


class GapAggressive(Strategy):
    atr_period = 14
    atr_mult = 3.0       # wider trail to let winners run
    ema_period = 21

    def init(self):
        self.atr = self.I(calc_atr, self.data.High, self.data.Low, self.data.Close, self.atr_period)
        self.ema = self.I(calc_ema, self.data.Close, self.ema_period)
        self.macd_hist = self.I(calc_macd_hist, self.data.Close)
        self.trail_stop = 0

    def next(self):
        price = self.data.Close[-1]

        if not self.position:
            if (len(self.data) > 1 and
                    self.data.Open[-1] > self.data.High[-2] and
                    self.macd_hist[-1] > 0 and
                    price > self.ema[-1] and
                    not np.isnan(self.atr[-1])):
                self.buy()
                self.trail_stop = price - self.atr[-1] * self.atr_mult
        else:
            new_trail = price - self.atr[-1] * self.atr_mult
            if new_trail > self.trail_stop:
                self.trail_stop = new_trail
            if price < self.trail_stop:
                self.position.close()


bt = Backtest(data, GapAggressive, cash=1_000_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r3_04_gap_aggressive")
