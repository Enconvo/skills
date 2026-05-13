"""
ROUND 2 — Strategy 10: Gap + Keltner Channel Hybrid
=====================================================
Combines R1-13 Gap-and-Go (451%) with R1-11 Keltner Reversion (89.6%, SQN 2.21).
Entry: Gap up >1% AND price near lower Keltner band (buying gap momentum
at a technically oversold level). This filters out gaps into resistance.
Exit: ATR trailing stop.
"""
import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_nvda_data

data = load_nvda_data("1h")


def calc_gap_pct(open_price, close_price):
    gap = np.full_like(open_price, np.nan)
    gap[1:] = (open_price[1:] - close_price[:-1]) / close_price[:-1] * 100
    return gap


def calc_ema(close, period):
    return talib.EMA(close, timeperiod=period)


def calc_atr(high, low, close, period):
    return talib.ATR(high, low, close, timeperiod=period)


def calc_keltner_lower(close, high, low, ema_period, atr_period, atr_mult):
    ema = talib.EMA(close, timeperiod=ema_period)
    atr = talib.ATR(high, low, close, timeperiod=atr_period)
    return ema - atr * atr_mult


class GapKeltnerHybrid(Strategy):
    gap_min = 0.5
    ema_period = 20
    atr_period = 14
    keltner_mult = 1.5
    trail_mult = 2.0

    def init(self):
        self.gap = self.I(calc_gap_pct, self.data.Open, self.data.Close)
        self.ema = self.I(calc_ema, self.data.Close, self.ema_period)
        self.atr = self.I(calc_atr, self.data.High, self.data.Low, self.data.Close, self.atr_period)
        self.keltner_low = self.I(calc_keltner_lower, self.data.Close, self.data.High,
                                   self.data.Low, self.ema_period, self.atr_period, self.keltner_mult)
        self.trail_stop = 0

    def next(self):
        price = self.data.Close[-1]

        if not self.position:
            # Gap up + price near or below Keltner lower band = buying dip with momentum
            if (self.gap[-1] > self.gap_min and
                    price <= self.keltner_low[-1] * 1.02 and  # within 2% of lower band
                    not np.isnan(self.atr[-1])):
                self.buy()
                self.trail_stop = price - self.atr[-1] * self.trail_mult
        else:
            new_trail = price - self.atr[-1] * self.trail_mult
            if new_trail > self.trail_stop:
                self.trail_stop = new_trail
            if price < self.trail_stop:
                self.position.close()


bt = Backtest(data, GapKeltnerHybrid, cash=1_000_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r2_10_gap_keltner_hybrid")
