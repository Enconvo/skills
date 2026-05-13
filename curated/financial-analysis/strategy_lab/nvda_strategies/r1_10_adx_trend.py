"""
ROUND 1 — Strategy 10: ADX Trend Strength + DI Crossover
=========================================================
Buy when ADX > 25 (strong trend) and +DI crosses above -DI (bullish).
Sell when -DI crosses above +DI or ADX drops below 20 (trend weakening).
"""
import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_nvda_data

data = load_nvda_data("1h")


def calc_adx(high, low, close, period):
    return talib.ADX(high, low, close, timeperiod=period)

def calc_plus_di(high, low, close, period):
    return talib.PLUS_DI(high, low, close, timeperiod=period)

def calc_minus_di(high, low, close, period):
    return talib.MINUS_DI(high, low, close, timeperiod=period)


class ADXTrend(Strategy):
    adx_period = 14
    adx_threshold = 25

    def init(self):
        self.adx = self.I(calc_adx, self.data.High, self.data.Low,
                          self.data.Close, self.adx_period)
        self.plus_di = self.I(calc_plus_di, self.data.High, self.data.Low,
                              self.data.Close, self.adx_period)
        self.minus_di = self.I(calc_minus_di, self.data.High, self.data.Low,
                               self.data.Close, self.adx_period)

    def next(self):
        if not self.position:
            if self.adx[-1] > self.adx_threshold and crossover(self.plus_di, self.minus_di):
                self.buy()
        else:
            if crossover(self.minus_di, self.plus_di) or self.adx[-1] < 20:
                self.position.close()


bt = Backtest(data, ADXTrend, cash=1_000_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r1_10_adx_trend")
