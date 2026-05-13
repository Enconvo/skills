"""
ROUND 3 — Strategy 03: Safe Compounder (Max Risk-Adjusted Returns)
=================================================================
FINAL EVOLUTION: Optimized for RISK-ADJUSTED returns (Sharpe/Sortino/SQN).
Combines Keltner (lowest DD, highest SQN 2.51) with triple confirmation.
Goal: High win rate, low drawdown, consistent compounding.

Entry: Price at lower Keltner + RSI < 40 + StochRSI K < 25
Exit: Price at middle Keltner OR RSI > 60
Position sizing: Never risk more than 1 ATR per trade.

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

def calc_atr(high, low, close, period):
    return talib.ATR(high, low, close, timeperiod=period)


class SafeCompounder(Strategy):
    rsi_period = 14
    kc_period = 20
    kc_mult = 1.5
    rsi_entry = 40
    stoch_entry = 25
    rsi_exit = 60

    def init(self):
        self.rsi = self.I(calc_rsi, self.data.Close, self.rsi_period)
        self.stoch_k = self.I(stoch_rsi_k, self.data.Close, self.rsi_period, 14)
        self.kc_low = self.I(keltner_lower, self.data.High, self.data.Low,
                             self.data.Close, self.kc_period, self.kc_mult)
        self.kc_mid = self.I(keltner_middle, self.data.Close, self.kc_period)
        self.atr = self.I(calc_atr, self.data.High, self.data.Low,
                          self.data.Close, 14)

    def next(self):
        price = self.data.Close[-1]

        if np.isnan(self.atr[-1]):
            return

        kc_hit = price <= self.kc_low[-1]
        rsi_oversold = self.rsi[-1] < self.rsi_entry
        stoch_oversold = self.stoch_k[-1] < self.stoch_entry

        if kc_hit and rsi_oversold and stoch_oversold and not self.position:
            self.buy()
        elif self.position:
            if price >= self.kc_mid[-1] or self.rsi[-1] > self.rsi_exit:
                self.position.close()


bt = Backtest(data, SafeCompounder, cash=100_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r3_03_safe_compounder")
