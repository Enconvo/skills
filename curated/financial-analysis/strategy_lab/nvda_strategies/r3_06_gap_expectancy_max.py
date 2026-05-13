"""
ROUND 3 — Strategy 06: Gap Expectancy Maximizer
=================================================
Evolved from R2-12 (Expectancy 8.36% per trade — highest of all).
Optimized for highest expected value per trade:
- Stricter entry: gap up >1.5% AND open > prev high AND MACD positive
- Moderate ATR trail (2.0x) — balanced between cutting losers and riding winners
- Fewer trades, but each trade has maximum expected payoff.
Goal: Expectancy >10% per trade with SQN > 1.5.
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


def calc_sma(close, period):
    return talib.SMA(close, timeperiod=period)


def calc_macd_hist(close):
    _, _, hist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
    return hist


class GapExpectancyMax(Strategy):
    gap_min = 1.5
    atr_period = 14
    atr_mult = 2.0
    sma_period = 50

    def init(self):
        self.gap = self.I(calc_gap_pct, self.data.Open, self.data.Close)
        self.atr = self.I(calc_atr, self.data.High, self.data.Low, self.data.Close, self.atr_period)
        self.sma = self.I(calc_sma, self.data.Close, self.sma_period)
        self.macd_hist = self.I(calc_macd_hist, self.data.Close)
        self.trail_stop = 0

    def next(self):
        price = self.data.Close[-1]

        if not self.position:
            # Triple confirmation: big gap + breakout + MACD momentum
            if (len(self.data) > 1 and
                    self.gap[-1] > self.gap_min and
                    self.data.Open[-1] > self.data.High[-2] and
                    self.macd_hist[-1] > 0 and
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


bt = Backtest(data, GapExpectancyMax, cash=1_000_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r3_06_gap_expectancy_max")
