"""
ROUND 1 — Strategy 07: EMA Ribbon (8/21/55)
============================================
Buy when EMAs stack bullish (8 > 21 > 55). Sell when bearish stack (8 < 21 < 55).
Captures strong trends early.
"""
import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_nvda_data

data = load_nvda_data("1h")


def calc_ema(close, period):
    return talib.EMA(close, timeperiod=period)


class EMARibbon(Strategy):
    fast = 8
    mid = 21
    slow = 55

    def init(self):
        self.ema_fast = self.I(calc_ema, self.data.Close, self.fast)
        self.ema_mid = self.I(calc_ema, self.data.Close, self.mid)
        self.ema_slow = self.I(calc_ema, self.data.Close, self.slow)

    def next(self):
        bullish = self.ema_fast[-1] > self.ema_mid[-1] > self.ema_slow[-1]
        bearish = self.ema_fast[-1] < self.ema_mid[-1] < self.ema_slow[-1]

        if bullish and not self.position:
            self.buy()
        elif bearish and self.position:
            self.position.close()


bt = Backtest(data, EMARibbon, cash=1_000_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r1_07_ema_ribbon")
