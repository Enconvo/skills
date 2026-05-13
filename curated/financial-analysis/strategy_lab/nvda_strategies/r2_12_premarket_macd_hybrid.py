"""
ROUND 2 — Strategy 12: Pre-Market Breakout + MACD Confirmation
================================================================
Combines R1-16 Pre-Market Breakout (211%, Sharpe 0.83) with MACD momentum.
Entry: Open > yesterday's high (breakout) AND MACD histogram positive (momentum).
This adds momentum confirmation to reduce false breakouts.
Exit: ATR trailing stop.
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


def calc_sma(close, period):
    return talib.SMA(close, timeperiod=period)


def calc_macd_hist(close):
    _, _, hist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
    return hist


def calc_volume_sma(volume, period):
    return talib.SMA(volume.astype(float), timeperiod=period)


class PremarketMACDHybrid(Strategy):
    atr_period = 14
    atr_mult = 2.0
    sma_period = 50

    def init(self):
        self.atr = self.I(calc_atr, self.data.High, self.data.Low, self.data.Close, self.atr_period)
        self.sma = self.I(calc_sma, self.data.Close, self.sma_period)
        self.macd_hist = self.I(calc_macd_hist, self.data.Close)
        self.vol_sma = self.I(calc_volume_sma, self.data.Volume, 20)
        self.trail_stop = 0

    def next(self):
        price = self.data.Close[-1]

        if not self.position:
            if (len(self.data) > 1 and
                    self.data.Open[-1] > self.data.High[-2] and  # breakout
                    self.macd_hist[-1] > 0 and                    # MACD positive
                    price > self.sma[-1] and                      # uptrend
                    not np.isnan(self.atr[-1])):
                self.buy()
                self.trail_stop = price - self.atr[-1] * self.atr_mult
        else:
            new_trail = price - self.atr[-1] * self.atr_mult
            if new_trail > self.trail_stop:
                self.trail_stop = new_trail
            if price < self.trail_stop:
                self.position.close()


bt = Backtest(data, PremarketMACDHybrid, cash=1_000_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r2_12_premarket_macd_hybrid")
