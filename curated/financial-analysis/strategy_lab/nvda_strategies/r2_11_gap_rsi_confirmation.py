"""
ROUND 2 — Strategy 11: Gap + RSI Confirmation
===============================================
Evolved from R1-17 (Gap Momentum Filter, 346% but -61.2% DD).
Fix: Add RSI momentum confirmation AND tighter stop. Only enter gap-ups
when RSI confirms bullish momentum (rising RSI, not yet overbought).
This should cut the massive drawdown while preserving most gains.
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


def calc_rsi(close, period):
    return talib.RSI(close, timeperiod=period)


def calc_ema(close, period):
    return talib.EMA(close, timeperiod=period)


def calc_atr(high, low, close, period):
    return talib.ATR(high, low, close, timeperiod=period)


class GapRSIConfirmation(Strategy):
    gap_min = 1.0
    rsi_low = 35
    rsi_high = 60
    ema_period = 21
    atr_period = 14
    atr_mult = 2.0

    def init(self):
        self.gap = self.I(calc_gap_pct, self.data.Open, self.data.Close)
        self.rsi = self.I(calc_rsi, self.data.Close, 14)
        self.ema = self.I(calc_ema, self.data.Close, self.ema_period)
        self.atr = self.I(calc_atr, self.data.High, self.data.Low, self.data.Close, self.atr_period)
        self.trail_stop = 0

    def next(self):
        price = self.data.Close[-1]

        if not self.position:
            # Gap up + RSI in sweet spot + above EMA
            if (self.gap[-1] > self.gap_min and
                    self.rsi_low < self.rsi[-1] < self.rsi_high and
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


bt = Backtest(data, GapRSIConfirmation, cash=1_000_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r2_11_gap_rsi_confirmation")
