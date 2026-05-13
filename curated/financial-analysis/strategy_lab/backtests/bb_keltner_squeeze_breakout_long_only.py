"""
BACKTEST: BB-Keltner Squeeze Breakout — LONG ONLY
===================================================
John Carter's TTM Squeeze — long entries only (no shorting into bull runs).
- Squeeze ON when BB inside KC (volatility compressed)
- Squeeze OFF when BB expands outside KC (breakout)
- LONG: squeeze fires + momentum positive and rising
- EXIT: momentum turns negative
- Stop loss: 2x ATR

STATS:
---
Start                     2024-02-12 05:00:00+00:00
End                       2026-02-11 05:00:00+00:00
Duration                    730 days 00:00:00
Exposure Time [%]                    12.80233
Equity Final [$]                 889533.69322
Equity Peak [$]                 1143547.31739
Return [%]                          -11.04663
Buy & Hold Return [%]                34.67633
Return (Ann.) [%]                    -5.67735
Volatility (Ann.) [%]                14.53352
Sharpe Ratio                         -0.39064
Sortino Ratio                        -0.71935
Calmar Ratio                         -0.23043
Max. Drawdown [%]                   -24.63792
Avg. Drawdown [%]                    -5.51565
# Trades                                  130
Win Rate [%]                         26.92308
Best Trade [%]                        12.2978
Worst Trade [%]                      -2.76339
Avg. Trade [%]                       -0.09481
Max. Trade Duration           3 days 04:00:00
Avg. Trade Duration           0 days 17:00:00
Profit Factor                         0.87654
Expectancy [%]                       -0.07759
SQN                                  -0.55636
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
    diff = np.where(np.isnan(diff), 0.0, diff)
    mom = talib.LINEARREG(diff, timeperiod=20)
    return mom


# ── Strategy ─────────────────────────────────────────────────
class BBKeltnerSqueezeLongOnly(Strategy):
    atr_sl_mult = 2.0

    def init(self):
        self.squeeze_on = self.I(calc_squeeze_on, self.data.Close, self.data.High, self.data.Low, name='Squeeze')
        self.momentum = self.I(calc_momentum, self.data.Close, name='Momentum')
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=14)

    def next(self):
        if len(self.data) < 25:
            return

        squeeze_now = self.squeeze_on[-1]
        squeeze_prev = self.squeeze_on[-2]
        mom_now = self.momentum[-1]
        mom_prev = self.momentum[-2]
        atr_now = self.atr[-1]

        if np.isnan(mom_now) or np.isnan(mom_prev) or np.isnan(atr_now):
            return

        squeeze_fired = (squeeze_prev == 1.0) and (squeeze_now == 0.0)
        mom_rising = mom_now > mom_prev
        mom_positive = mom_now > 0
        mom_negative = mom_now < 0
        price = self.data.Close[-1]

        # LONG entry: squeeze fires + momentum positive and rising
        if squeeze_fired and mom_positive and mom_rising:
            if not self.position.is_long:
                sl = price - self.atr_sl_mult * atr_now
                self.buy(sl=sl)

        # EXIT: momentum turns negative
        if self.position.is_long and mom_negative:
            self.position.close()


# ── Run ──────────────────────────────────────────────────────
bt = Backtest(
    data,
    BBKeltnerSqueezeLongOnly,
    cash=1_000_000,
    commission=0.001,
    exclusive_orders=True,
)

stats = bt.run()
print(stats)
print(f"\n_strategy_name: BBKeltnerSqueezeLongOnly")
