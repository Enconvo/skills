"""
RSI + Bollinger Band Mean Reversion with ATR Risk Management
=============================================================
Catches overextensions beyond Bollinger Bands confirmed by RSI extremes,
then rides the reversion back to the mean (middle BB). ATR-based stops
prevent blowups on legitimate breakouts.

STATS:
---
Start                     2024-02-12 05:00:00+00:00
End                       2026-02-11 05:00:00+00:00
Duration                    730 days 00:00:00
Exposure Time [%]                    36.15987
Equity Final [$]                 415131.07138
Equity Peak [$]                   1023474.351
Return [%]                          -58.48689
Buy & Hold Return [%]                34.67633
Return (Ann.) [%]                   -35.53058
Volatility (Ann.) [%]                18.38673
Sharpe Ratio                          -1.9324
Sortino Ratio                        -1.59865
Calmar Ratio                         -0.59777
Max. Drawdown [%]                   -59.43904
Avg. Drawdown [%]                    -12.0562
# Trades                                  447
Win Rate [%]                         27.06935
Best Trade [%]                        8.45249
Worst Trade [%]                      -3.65225
Avg. Trade [%]                       -0.21197
Profit Factor                         0.78479
Expectancy [%]                       -0.19425
SQN                                  -2.16349
---
"""

import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_btc_data

# ── Data ─────────────────────────────────────────────────────
data = load_btc_data()


# ── Helper functions for self.I() ────────────────────────────
_bb_cache = {}


def _get_bbands(close, timeperiod, nbdevup):
    key = (id(close), timeperiod, nbdevup)
    if key not in _bb_cache:
        _bb_cache[key] = talib.BBANDS(close, timeperiod=timeperiod,
                                       nbdevup=nbdevup, nbdevdn=nbdevup,
                                       matype=0)
    return _bb_cache[key]


def bb_upper(close, timeperiod=20, nbdevup=2.0):
    return _get_bbands(close, timeperiod, nbdevup)[0]


def bb_middle(close, timeperiod=20, nbdevup=2.0):
    return _get_bbands(close, timeperiod, nbdevup)[1]


def bb_lower(close, timeperiod=20, nbdevup=2.0):
    return _get_bbands(close, timeperiod, nbdevup)[2]


def bb_bandwidth(close, timeperiod=20, nbdevup=2.0):
    upper, middle, lower = _get_bbands(close, timeperiod, nbdevup)
    return (upper - lower) / middle


# ── Strategy ─────────────────────────────────────────────────
class RSIBollingerMeanReversion(Strategy):
    bb_period = 20
    bb_std = 2.0
    rsi_period = 14
    atr_period = 14
    atr_sl_mult = 1.5
    rsi_oversold = 30
    rsi_overbought = 70
    min_bandwidth = 0.02

    def init(self):
        self.bb_up = self.I(bb_upper, self.data.Close,
                            timeperiod=self.bb_period, nbdevup=self.bb_std)
        self.bb_mid = self.I(bb_middle, self.data.Close,
                             timeperiod=self.bb_period, nbdevup=self.bb_std)
        self.bb_low = self.I(bb_lower, self.data.Close,
                             timeperiod=self.bb_period, nbdevup=self.bb_std)
        self.bandwidth = self.I(bb_bandwidth, self.data.Close,
                                timeperiod=self.bb_period, nbdevup=self.bb_std)
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=self.rsi_period)
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low,
                          self.data.Close, timeperiod=self.atr_period)

    def next(self):
        price = self.data.Close[-1]
        atr_val = self.atr[-1]
        rsi_val = self.rsi[-1]
        upper = self.bb_up[-1]
        middle = self.bb_mid[-1]
        lower = self.bb_low[-1]
        bw = self.bandwidth[-1]

        # Skip if any indicator is NaN
        if np.isnan(atr_val) or np.isnan(rsi_val) or np.isnan(bw):
            return

        # Don't trade during BB squeeze — no mean to revert to
        if bw < self.min_bandwidth:
            return

        # LONG: Price at/below lower BB AND RSI oversold
        if not self.position and price <= lower and rsi_val < self.rsi_oversold:
            sl = price - self.atr_sl_mult * atr_val
            tp = middle  # Mean reversion target
            if tp > price and sl < price:
                self.buy(sl=sl, tp=tp)

        # SHORT: Price at/above upper BB AND RSI overbought
        elif not self.position and price >= upper and rsi_val > self.rsi_overbought:
            sl = price + self.atr_sl_mult * atr_val
            tp = middle  # Mean reversion target
            if tp < price and sl > price:
                self.sell(sl=sl, tp=tp)


# ── Run ──────────────────────────────────────────────────────
bt = Backtest(
    data,
    RSIBollingerMeanReversion,
    cash=1_000_000,
    commission=0.001,
    exclusive_orders=True,
)

stats = bt.run()
print(stats)
print(f"\n_strategy_name: RSIBollingerMeanReversion")
