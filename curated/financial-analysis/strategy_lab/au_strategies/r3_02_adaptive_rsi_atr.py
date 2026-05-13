"""
ROUND 3 — Strategy 02: Adaptive RSI + ATR (Regime Switching)
============================================================
FINAL EVOLUTION: Takes the adaptive regime idea (R2-08, 190%) and adds
ATR trailing stop (R2-05, 210%). Best of both worlds.
- Low ADX (choppy): RSI mean reversion with tight ATR trail (1.5x)
- High ADX (trending): RSI entry with wide ATR trail (3.0x) to ride trends
Adapts position management to market conditions.

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


def calc_rsi(close, period):
    return talib.RSI(close, timeperiod=period)

def calc_adx(high, low, close, period):
    return talib.ADX(high, low, close, timeperiod=period)

def calc_atr(high, low, close, period):
    return talib.ATR(high, low, close, timeperiod=period)


class AdaptiveRSIATR(Strategy):
    rsi_period = 14
    adx_period = 14
    adx_threshold = 25
    atr_period = 14
    # Choppy regime
    rsi_entry_choppy = 30
    rsi_exit_choppy = 70
    atr_trail_choppy = 1.5
    # Trending regime
    rsi_entry_trend = 35
    atr_trail_trend = 3.0

    def init(self):
        self.rsi = self.I(calc_rsi, self.data.Close, self.rsi_period)
        self.adx = self.I(calc_adx, self.data.High, self.data.Low,
                          self.data.Close, self.adx_period)
        self.atr = self.I(calc_atr, self.data.High, self.data.Low,
                          self.data.Close, self.atr_period)
        self.highest = 0
        self.trail_stop = 0
        self.entry_regime = None  # track which regime we entered in

    def next(self):
        price = self.data.Close[-1]
        atr_val = self.atr[-1]

        if np.isnan(atr_val) or np.isnan(self.adx[-1]):
            return

        trending = self.adx[-1] >= self.adx_threshold

        if not self.position:
            if trending and self.rsi[-1] < self.rsi_entry_trend:
                self.buy()
                self.highest = price
                self.trail_stop = price - self.atr_trail_trend * atr_val
                self.entry_regime = "trend"
            elif not trending and self.rsi[-1] < self.rsi_entry_choppy:
                self.buy()
                self.highest = price
                self.trail_stop = price - self.atr_trail_choppy * atr_val
                self.entry_regime = "choppy"
        else:
            # Adaptive trail based on entry regime
            if price > self.highest:
                self.highest = price

            mult = self.atr_trail_trend if self.entry_regime == "trend" else self.atr_trail_choppy
            new_stop = self.highest - mult * atr_val
            if new_stop > self.trail_stop:
                self.trail_stop = new_stop

            # Exit conditions
            exit_signal = False
            if price < self.trail_stop:
                exit_signal = True
            if self.entry_regime == "choppy" and self.rsi[-1] > self.rsi_exit_choppy:
                exit_signal = True

            if exit_signal:
                self.position.close()
                self.highest = 0
                self.trail_stop = 0
                self.entry_regime = None


bt = Backtest(data, AdaptiveRSIATR, cash=100_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r3_02_adaptive_rsi_atr")
