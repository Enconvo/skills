"""
ROUND 1 — Strategy 16: Pre-Market Breakout Proxy (Daily)
=========================================================
Approximates pre-market breakout using daily data: if today's open breaks
above yesterday's high (strong overnight buying), enter long.
This proxies the effect of pre-market momentum pushing above resistance.
Uses ATR trailing stop for exits.

Note: For true pre-market data, use fetch_extended_hours() with Polygon.
This daily version captures the same signal less precisely but with 5yr history.
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


def calc_volume_sma(volume, period):
    return talib.SMA(volume.astype(float), timeperiod=period)


class PremarketBreakout(Strategy):
    atr_period = 14
    atr_mult = 2.0
    sma_period = 50     # trend filter
    vol_mult = 1.5      # require above-average volume

    def init(self):
        self.atr = self.I(calc_atr, self.data.High, self.data.Low, self.data.Close, self.atr_period)
        self.sma = self.I(calc_sma, self.data.Close, self.sma_period)
        self.vol_sma = self.I(calc_volume_sma, self.data.Volume, 20)
        self.trail_stop = 0

    def next(self):
        price = self.data.Close[-1]

        if not self.position:
            # Open breaks above yesterday's high = pre-market breakout signal
            if (len(self.data) > 1 and
                    self.data.Open[-1] > self.data.High[-2] and
                    price > self.sma[-1] and
                    self.data.Volume[-1] > self.vol_sma[-1] * self.vol_mult and
                    not np.isnan(self.atr[-1])):
                self.buy()
                self.trail_stop = price - self.atr[-1] * self.atr_mult
        else:
            new_trail = price - self.atr[-1] * self.atr_mult
            if new_trail > self.trail_stop:
                self.trail_stop = new_trail
            if price < self.trail_stop:
                self.position.close()


bt = Backtest(data, PremarketBreakout, cash=1_000_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r1_16_premarket_breakout")
