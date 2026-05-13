"""
ROUND 2 — Strategy 07: EMA Trend + RSI Pullback Entry
=====================================================
EVOLUTION: EMA Ribbon (#2, 174% return) had only 43% win rate.
Problem: entering on stack formation catches late entries.
Fix: Wait for EMA bullish stack, then buy pullbacks when RSI dips < 40.
Better entries = higher win rate + same trend exposure.

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


def ema(close, period):
    return talib.EMA(close, timeperiod=period)

def calc_rsi(close, period):
    return talib.RSI(close, timeperiod=period)


class EMAPullbackRSI(Strategy):
    rsi_period = 14
    rsi_pullback = 40
    rsi_exit = 70

    def init(self):
        self.ema8 = self.I(ema, self.data.Close, 8)
        self.ema21 = self.I(ema, self.data.Close, 21)
        self.ema55 = self.I(ema, self.data.Close, 55)
        self.rsi = self.I(calc_rsi, self.data.Close, self.rsi_period)

    def next(self):
        bullish_stack = (self.ema8[-1] > self.ema21[-1] > self.ema55[-1])

        if (bullish_stack and
            self.rsi[-1] < self.rsi_pullback and
            not self.position):
            self.buy()
        elif self.position:
            if self.rsi[-1] > self.rsi_exit or self.ema8[-1] < self.ema55[-1]:
                self.position.close()


bt = Backtest(data, EMAPullbackRSI, cash=100_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r2_07_ema_pullback_rsi")
