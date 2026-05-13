"""
Keltner Channel Mean Reversion with RSI and Volume Filter
==========================================================
Uses Keltner Channels (EMA + ATR bands) for mean reversion entries.
More robust than Bollinger Bands for crypto — ATR adapts better to
volatile markets than standard deviation. Volume filter ensures we
only trade into panic selling or euphoric buying, not low-conviction moves.

STATS:
---
Start                     2024-02-12 05:00:00+00:00
End                       2026-02-11 05:00:00+00:00
Duration                    730 days 00:00:00
Exposure Time [%]                    42.77546
Equity Final [$]                 145648.78877
Equity Peak [$]                 1011126.85082
Return [%]                          -85.43512
Buy & Hold Return [%]                34.67633
Return (Ann.) [%]                   -61.78572
Volatility (Ann.) [%]                10.50812
Sharpe Ratio                         -5.87981
Sortino Ratio                        -2.62051
Calmar Ratio                         -0.71599
Max. Drawdown [%]                   -86.29399
Avg. Drawdown [%]                   -28.97149
# Trades                                  959
Win Rate [%]                         24.71324
Best Trade [%]                        8.81045
Worst Trade [%]                      -3.53707
Avg. Trade [%]                       -0.23533
Profit Factor                         0.65268
Expectancy [%]                       -0.22671
SQN                                  -4.42347
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
_kc_cache = {}


def _get_keltner(high, low, close, ema_period, atr_period, atr_mult):
    key = (id(high), id(low), id(close), ema_period, atr_period, atr_mult)
    if key not in _kc_cache:
        ema = talib.EMA(close, timeperiod=ema_period)
        atr = talib.ATR(high, low, close, timeperiod=atr_period)
        _kc_cache[key] = (ema + atr_mult * atr, ema, ema - atr_mult * atr)
    return _kc_cache[key]


def keltner_upper(close, high, low, ema_period=20, atr_period=10, atr_mult=2.0):
    return _get_keltner(high, low, close, ema_period, atr_period, atr_mult)[0]


def keltner_lower(close, high, low, ema_period=20, atr_period=10, atr_mult=2.0):
    return _get_keltner(high, low, close, ema_period, atr_period, atr_mult)[2]


def volume_sma(volume, timeperiod=20):
    return talib.SMA(volume.astype(float), timeperiod=timeperiod)


# ── Strategy ─────────────────────────────────────────────────
class KeltnerChannelMeanReversion(Strategy):
    ema_period = 20
    atr_period = 10
    atr_mult = 2.0
    rsi_period = 14
    vol_period = 20
    rsi_oversold = 35
    rsi_overbought = 65
    sl_atr_mult = 2.0

    def init(self):
        self.kc_upper = self.I(keltner_upper, self.data.Close,
                               self.data.High, self.data.Low,
                               ema_period=self.ema_period,
                               atr_period=self.atr_period,
                               atr_mult=self.atr_mult)
        self.kc_center = self.I(talib.EMA, self.data.Close,
                                timeperiod=self.ema_period)
        self.kc_lower = self.I(keltner_lower, self.data.Close,
                               self.data.High, self.data.Low,
                               ema_period=self.ema_period,
                               atr_period=self.atr_period,
                               atr_mult=self.atr_mult)
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low,
                          self.data.Close, timeperiod=self.atr_period)
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=self.rsi_period)
        self.vol_sma = self.I(volume_sma, self.data.Volume,
                              timeperiod=self.vol_period)

    def next(self):
        price = self.data.Close[-1]
        upper = self.kc_upper[-1]
        center = self.kc_center[-1]
        lower = self.kc_lower[-1]
        atr_val = self.atr[-1]
        rsi_val = self.rsi[-1]
        vol = self.data.Volume[-1]
        vol_avg = self.vol_sma[-1]

        # Skip if any indicator is NaN
        if np.isnan(atr_val) or np.isnan(rsi_val) or np.isnan(vol_avg) or np.isnan(upper):
            return

        # Volume must be above average (panic/euphoria filter)
        high_volume = vol > vol_avg

        # LONG: Price below lower Keltner + RSI oversold + high volume (panic selling)
        if not self.position and price < lower and rsi_val < self.rsi_oversold and high_volume:
            sl = lower - self.sl_atr_mult * atr_val
            tp = center  # Mean reversion target
            if tp > price and sl < price:
                self.buy(sl=sl, tp=tp)

        # SHORT: Price above upper Keltner + RSI overbought + high volume (euphoric buying)
        elif not self.position and price > upper and rsi_val > self.rsi_overbought and high_volume:
            sl = upper + self.sl_atr_mult * atr_val
            tp = center  # Mean reversion target
            if tp < price and sl > price:
                self.sell(sl=sl, tp=tp)


# ── Run ──────────────────────────────────────────────────────
bt = Backtest(
    data,
    KeltnerChannelMeanReversion,
    cash=1_000_000,
    commission=0.001,
    exclusive_orders=True,
)

stats = bt.run()
print(stats)
print(f"\n_strategy_name: KeltnerChannelMeanReversion")
