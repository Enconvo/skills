"""
ROUND 2 — Strategy 08: Adaptive Mean Reversion / Trend Switch
=============================================================
EVOLUTION: Novel approach — switches between mean reversion and trend following
based on market regime (ADX).
- When ADX < 25 (choppy): Use RSI mean reversion (buy <30, sell >70)
- When ADX >= 25 (trending): Use EMA crossover (8/21)
AU alternates between gold-driven trends and choppy consolidation.
Adapting to the regime should outperform any single approach.

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

def calc_adx(high, low, close, period):
    return talib.ADX(high, low, close, timeperiod=period)

def ema(close, period):
    return talib.EMA(close, timeperiod=period)


class MeanRevTrendSwitch(Strategy):
    adx_period = 14
    adx_threshold = 25
    rsi_period = 14

    def init(self):
        self.rsi = self.I(calc_rsi, self.data.Close, self.rsi_period)
        self.adx = self.I(calc_adx, self.data.High, self.data.Low,
                          self.data.Close, self.adx_period)
        self.ema8 = self.I(ema, self.data.Close, 8)
        self.ema21 = self.I(ema, self.data.Close, 21)

    def next(self):
        if np.isnan(self.adx[-1]):
            return

        trending = self.adx[-1] >= self.adx_threshold

        if trending:
            # Trend mode: EMA crossover
            if crossover(self.ema8, self.ema21) and not self.position:
                self.buy()
            elif crossover(self.ema21, self.ema8) and self.position:
                self.position.close()
        else:
            # Mean reversion mode: RSI
            if self.rsi[-1] < 30 and not self.position:
                self.buy()
            elif self.rsi[-1] > 70 and self.position:
                self.position.close()


bt = Backtest(data, MeanRevTrendSwitch, cash=100_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r2_08_mean_rev_trend_switch")
