"""
ROUND 3 — Strategy 05: Gap Regime Safe (RISK-ADJUSTED)
========================================================
Evolved from R2-12 (445%, DD -42%). Optimized for risk-adjusted returns:
- 200 SMA regime filter: only trade when price > 200 SMA (long-term uptrend)
- Tighter ATR trail (1.5x) to cut losses faster
- Volume confirmation: require above-average volume on breakout day
Goal: cut drawdown below -25% while maintaining Sharpe > 1.0.
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


class GapRegimeSafe(Strategy):
    atr_period = 14
    atr_mult = 1.5
    sma_trend = 200       # regime filter
    sma_short = 50

    def init(self):
        self.atr = self.I(calc_atr, self.data.High, self.data.Low, self.data.Close, self.atr_period)
        self.sma200 = self.I(calc_sma, self.data.Close, self.sma_trend)
        self.sma50 = self.I(calc_sma, self.data.Close, self.sma_short)
        self.macd_hist = self.I(calc_macd_hist, self.data.Close)
        self.vol_sma = self.I(calc_volume_sma, self.data.Volume, 20)
        self.trail_stop = 0

    def next(self):
        price = self.data.Close[-1]

        if not self.position:
            if (len(self.data) > 1 and
                    self.data.Open[-1] > self.data.High[-2] and   # breakout
                    self.macd_hist[-1] > 0 and                     # momentum
                    price > self.sma200[-1] and                    # regime: uptrend
                    price > self.sma50[-1] and                     # short-term uptrend
                    self.data.Volume[-1] > self.vol_sma[-1] and   # volume confirmation
                    not np.isnan(self.atr[-1])):
                self.buy()
                self.trail_stop = price - self.atr[-1] * self.atr_mult
        else:
            new_trail = price - self.atr[-1] * self.atr_mult
            if new_trail > self.trail_stop:
                self.trail_stop = new_trail
            if price < self.trail_stop:
                self.position.close()


bt = Backtest(data, GapRegimeSafe, cash=1_000_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r3_05_gap_regime_safe")
