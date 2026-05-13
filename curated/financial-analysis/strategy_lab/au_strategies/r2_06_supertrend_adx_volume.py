"""
ROUND 2 — Strategy 06: SuperTrend + ADX Strength + Volume Confirmation
======================================================================
EVOLUTION: SuperTrend (#4) was strong but had -22% DD. Adding ADX filter
(only trade when ADX > 20 = trending) and volume confirmation (volume > 20SMA).
Should filter false breakouts and reduce drawdown.

STATS:
---
[pending]
---
"""
import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_au_data

data = load_au_data("1h")


def supertrend_dir(high, low, close, period=10, multiplier=3.0):
    atr = talib.ATR(high, low, close, timeperiod=period)
    hl2 = (high + low) / 2
    upper = hl2 + multiplier * atr
    lower = hl2 - multiplier * atr
    direction = np.zeros_like(close)
    for i in range(period, len(close)):
        if i == period:
            direction[i] = -1
            continue
        if direction[i-1] == 1:
            lower[i] = max(lower[i], lower[i-1]) if not np.isnan(lower[i-1]) else lower[i]
            direction[i] = -1 if close[i] < lower[i] else 1
        else:
            upper[i] = min(upper[i], upper[i-1]) if not np.isnan(upper[i-1]) else upper[i]
            direction[i] = 1 if close[i] > upper[i] else -1
    return direction

def calc_adx(high, low, close, period):
    return talib.ADX(high, low, close, timeperiod=period)

def calc_vol_sma(volume, period):
    return talib.SMA(volume, timeperiod=period)


class SuperTrendADXVolume(Strategy):
    st_period = 10
    st_mult = 3.0
    adx_period = 14
    adx_threshold = 20
    vol_period = 20

    def init(self):
        self.st_dir = self.I(supertrend_dir, self.data.High, self.data.Low,
                             self.data.Close, self.st_period, self.st_mult)
        self.adx = self.I(calc_adx, self.data.High, self.data.Low,
                          self.data.Close, self.adx_period)
        self.vol_sma = self.I(calc_vol_sma, self.data.Volume.astype(float), self.vol_period)

    def next(self):
        if np.isnan(self.adx[-1]) or np.isnan(self.vol_sma[-1]):
            return

        st_flip_bull = self.st_dir[-1] == 1 and (len(self.st_dir) < 2 or self.st_dir[-2] == -1)
        strong_trend = self.adx[-1] > self.adx_threshold
        high_volume = self.data.Volume[-1] > self.vol_sma[-1]

        if st_flip_bull and strong_trend and high_volume and not self.position:
            self.buy()
        elif self.st_dir[-1] == -1 and self.position:
            self.position.close()


bt = Backtest(data, SuperTrendADXVolume, cash=100_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r2_06_supertrend_adx_volume")
