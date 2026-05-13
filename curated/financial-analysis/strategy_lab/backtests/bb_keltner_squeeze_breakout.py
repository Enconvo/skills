"""
BACKTEST: BB-Keltner Squeeze Breakout (TTM Squeeze)
====================================================
John Carter's famous TTM Squeeze setup.
- Bollinger Bands(20, 2.0) vs Keltner Channel(EMA20, 1.5*ATR10)
- Squeeze ON when BB inside KC (volatility compressed)
- Squeeze OFF when BB expands outside KC (breakout)
- Momentum = linear regression of (close - sma20)
- Enter on squeeze fire + momentum direction, exit on momentum reversal

STATS:
---
Start                     2024-02-12 05:00:00+00:00
End                       2026-02-11 05:00:00+00:00
Duration                    730 days 00:00:00
Exposure Time [%]                    26.50237
Equity Final [$]                 827461.68146
Equity Peak [$]                 1074404.08139
Return [%]                          -17.25383
Buy & Hold Return [%]                34.67633
Return (Ann.) [%]                    -9.02329
Volatility (Ann.) [%]                20.21573
Sharpe Ratio                         -0.44635
Sortino Ratio                        -0.74764
Calmar Ratio                         -0.30682
Max. Drawdown [%]                     -29.409
Avg. Drawdown [%]                    -5.85133
# Trades                                  261
Win Rate [%]                         29.50192
Best Trade [%]                        12.2978
Worst Trade [%]                      -2.81648
Avg. Trade [%]                        -0.0757
Max. Trade Duration           3 days 04:00:00
Avg. Trade Duration           0 days 17:00:00
Profit Factor                         0.90968
Expectancy [%]                       -0.05889
SQN                                  -0.67859
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


# ── Helper functions (must be outside class for self.I()) ────
_bb_cache = {}
_kc_cache = {}


def _get_bbands(close, timeperiod, nbdev):
    key = (id(close), timeperiod, nbdev)
    if key not in _bb_cache:
        _bb_cache[key] = talib.BBANDS(close, timeperiod=timeperiod,
                                       nbdevup=nbdev, nbdevdn=nbdev, matype=0)
    return _bb_cache[key]


def _get_keltner(high, low, close, ema_period, atr_period, atr_mult):
    key = (id(high), id(low), id(close), ema_period, atr_period, atr_mult)
    if key not in _kc_cache:
        ema = talib.EMA(close, timeperiod=ema_period)
        atr = talib.ATR(high, low, close, timeperiod=atr_period)
        _kc_cache[key] = (ema + atr_mult * atr, ema, ema - atr_mult * atr)
    return _kc_cache[key]


def calc_bb_upper(close, timeperiod=20, nbdevup=2.0):
    return _get_bbands(close, timeperiod, nbdevup)[0]

def calc_bb_lower(close, timeperiod=20, nbdevdn=2.0):
    return _get_bbands(close, timeperiod, nbdevdn)[2]

def calc_kc_upper(close, high, low, ema_period=20, atr_period=10, atr_mult=1.5):
    return _get_keltner(high, low, close, ema_period, atr_period, atr_mult)[0]

def calc_kc_lower(close, high, low, ema_period=20, atr_period=10, atr_mult=1.5):
    return _get_keltner(high, low, close, ema_period, atr_period, atr_mult)[2]

def calc_squeeze_on(close, high, low):
    """Returns 1.0 where squeeze is ON (BB inside KC), 0.0 otherwise."""
    bb_upper, _, bb_lower = _get_bbands(close, 20, 2.0)
    kc_upper, _, kc_lower = _get_keltner(high, low, close, 20, 10, 1.5)
    squeeze = np.where((bb_lower > kc_lower) & (bb_upper < kc_upper), 1.0, 0.0)
    return squeeze

def calc_momentum(close):
    """Momentum: linear regression of (close - SMA20) over 20 bars."""
    sma = talib.SMA(close, timeperiod=20)
    diff = close - sma
    # Replace NaN with 0 for LINEARREG
    diff = np.where(np.isnan(diff), 0.0, diff)
    mom = talib.LINEARREG(diff, timeperiod=20)
    return mom


# ── Strategy ─────────────────────────────────────────────────
class BBKeltnerSqueezeBreakout(Strategy):
    atr_sl_mult = 2.0

    def init(self):
        self.squeeze_on = self.I(calc_squeeze_on, self.data.Close, self.data.High, self.data.Low, name='Squeeze')
        self.momentum = self.I(calc_momentum, self.data.Close, name='Momentum')
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=14)

    def next(self):
        # Need at least 2 bars of valid data
        if len(self.data) < 25:
            return

        squeeze_now = self.squeeze_on[-1]
        squeeze_prev = self.squeeze_on[-2]
        mom_now = self.momentum[-1]
        mom_prev = self.momentum[-2]
        atr_now = self.atr[-1]

        if np.isnan(mom_now) or np.isnan(mom_prev) or np.isnan(atr_now):
            return

        # Squeeze fires: was ON (1.0), now OFF (0.0)
        squeeze_fired = (squeeze_prev == 1.0) and (squeeze_now == 0.0)

        # Momentum direction
        mom_rising = mom_now > mom_prev
        mom_falling = mom_now < mom_prev
        mom_positive = mom_now > 0
        mom_negative = mom_now < 0

        price = self.data.Close[-1]

        # Entry signals
        if squeeze_fired:
            if mom_positive and mom_rising:
                if self.position.is_short:
                    self.position.close()
                if not self.position.is_long:
                    sl = price - self.atr_sl_mult * atr_now
                    self.buy(sl=sl)
            elif mom_negative and mom_falling:
                if self.position.is_long:
                    self.position.close()
                if not self.position.is_short:
                    sl = price + self.atr_sl_mult * atr_now
                    self.sell(sl=sl)

        # Exit signals: momentum crosses zero (reversal complete)
        if self.position.is_long and mom_negative:
            self.position.close()
        elif self.position.is_short and mom_positive:
            self.position.close()


# ── Run ──────────────────────────────────────────────────────
bt = Backtest(
    data,
    BBKeltnerSqueezeBreakout,
    cash=1_000_000,
    commission=0.001,
    exclusive_orders=True,
)

stats = bt.run()
print(stats)
print(f"\n_strategy_name: BBKeltnerSqueezeBreakout")
