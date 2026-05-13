"""
ROUND 1 — Strategy 02: RSI Mean Reversion
==========================================
Buy when RSI drops below 30 (oversold), sell when RSI goes above 70 (overbought).
Gold miners can get irrationally oversold on fear — this catches the bounce.

STATS:
---
[pending]
---
"""
import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_au_data

data = load_au_data("1h")


def calc_rsi(close, period):
    return talib.RSI(close, timeperiod=period)


class RSIMeanReversion(Strategy):
    rsi_period = 14
    oversold = 30
    overbought = 70

    def init(self):
        self.rsi = self.I(calc_rsi, self.data.Close, self.rsi_period)

    def next(self):
        if self.rsi[-1] < self.oversold and not self.position:
            self.buy()
        elif self.rsi[-1] > self.overbought and self.position:
            self.position.close()


bt = Backtest(data, RSIMeanReversion, cash=100_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r1_02_rsi_mean_reversion")
