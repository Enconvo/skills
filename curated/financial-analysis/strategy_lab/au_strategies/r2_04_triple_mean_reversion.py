"""
ROUND 2 — Strategy 04: Triple Mean Reversion (RSI + StochRSI + Keltner)
=======================================================================
EVOLUTION: All 3 best mean reversion strategies combined.
Buy ONLY when ALL three say oversold simultaneously:
  - RSI < 35
  - StochRSI K < 20
  - Price at or below lower Keltner Channel
Exit when ANY two say overbought/recovered.
Maximum conviction entries only.

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

def stoch_rsi_k(close, rsi_period, k_period):
    rsi = talib.RSI(close, timeperiod=rsi_period)
    k, d = talib.STOCH(rsi, rsi, rsi, fastk_period=k_period, slowk_period=3, slowd_period=3)
    return k

def keltner_lower(high, low, close, period, mult):
    ema_val = talib.EMA(close, timeperiod=period)
    atr = talib.ATR(high, low, close, timeperiod=period)
    return ema_val - mult * atr

def keltner_middle(close, period):
    return talib.EMA(close, timeperiod=period)


class TripleMeanReversion(Strategy):
    rsi_period = 14
    rsi_oversold = 35
    stoch_k_period = 14
    stoch_oversold = 20
    kc_period = 20
    kc_mult = 1.5

    def init(self):
        self.rsi = self.I(calc_rsi, self.data.Close, self.rsi_period)
        self.stoch_k = self.I(stoch_rsi_k, self.data.Close, self.rsi_period, self.stoch_k_period)
        self.kc_low = self.I(keltner_lower, self.data.High, self.data.Low,
                             self.data.Close, self.kc_period, self.kc_mult)
        self.kc_mid = self.I(keltner_middle, self.data.Close, self.kc_period)

    def next(self):
        price = self.data.Close[-1]

        # Triple oversold confirmation
        rsi_oversold = self.rsi[-1] < self.rsi_oversold
        stoch_oversold = self.stoch_k[-1] < self.stoch_oversold
        kc_oversold = price <= self.kc_low[-1]

        if rsi_oversold and stoch_oversold and kc_oversold and not self.position:
            self.buy()
        elif self.position:
            # Exit when 2 of 3 say recovered
            rsi_ok = self.rsi[-1] > 55
            stoch_ok = self.stoch_k[-1] > 60
            kc_ok = price >= self.kc_mid[-1]
            if sum([rsi_ok, stoch_ok, kc_ok]) >= 2:
                self.position.close()


bt = Backtest(data, TripleMeanReversion, cash=100_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r2_04_triple_mean_reversion")
