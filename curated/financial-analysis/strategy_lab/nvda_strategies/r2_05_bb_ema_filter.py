"""
ROUND 2 — Strategy 05: Bollinger Bounce + EMA Uptrend Filter
==============================================================
EVOLUTION: Bollinger bounce (72% win) only when EMA 21 > EMA 55
(uptrend confirmed). Avoids buying dips in a downtrend.
ATR trailing stop for exits.
"""
import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_nvda_data

data = load_nvda_data("1h")


def calc_bb_lower(close, period, nbdev):
    u, m, l = talib.BBANDS(close, timeperiod=period, nbdevup=nbdev, nbdevdn=nbdev)
    return l

def calc_ema(close, period):
    return talib.EMA(close, timeperiod=period)

def calc_atr(high, low, close, period):
    return talib.ATR(high, low, close, timeperiod=period)


class BBEMAFilter(Strategy):
    atr_mult = 2.0

    def init(self):
        self.bb_lower = self.I(calc_bb_lower, self.data.Close, 20, 2.0)
        self.ema21 = self.I(calc_ema, self.data.Close, 21)
        self.ema55 = self.I(calc_ema, self.data.Close, 55)
        self.atr = self.I(calc_atr, self.data.High, self.data.Low,
                          self.data.Close, 14)
        self.highest = 0
        self.trail_stop = 0

    def next(self):
        price = self.data.Close[-1]
        atr_val = self.atr[-1]
        if np.isnan(atr_val):
            return
        if not self.position:
            uptrend = self.ema21[-1] > self.ema55[-1]
            if price <= self.bb_lower[-1] and uptrend:
                self.buy()
                self.highest = price
                self.trail_stop = price - self.atr_mult * atr_val
        else:
            if price > self.highest:
                self.highest = price
            new_stop = self.highest - self.atr_mult * atr_val
            if new_stop > self.trail_stop:
                self.trail_stop = new_stop
            if price < self.trail_stop:
                self.position.close()
                self.highest = 0
                self.trail_stop = 0


bt = Backtest(data, BBEMAFilter, cash=1_000_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r2_05_bb_ema_filter")
