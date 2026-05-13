"""
Heikin Ashi + Supertrend + Volume Profile Strategy
====================================================
Combines HA noise-filtering with Supertrend trend detection and volume confirmation.

- Heikin Ashi candles computed manually for noise reduction
- Supertrend(10, 3.0) on regular candles for trend direction
- Volume SMA(20) for participation confirmation

LONG: Strong bullish HA (small lower wick < 10% range) + Supertrend bullish + volume > vol SMA
SHORT: Strong bearish HA (small upper wick < 10% range) + Supertrend bearish + volume > vol SMA
EXIT: 2 consecutive HA color changes OR Supertrend flips

STATS:
---
Start                     2024-02-12 05:00:00+00:00
End                       2026-02-11 05:00:00+00:00
Duration                    730 days 00:00:00
Exposure Time [%]                    61.62159
Equity Final [$]                 464333.75254
Equity Peak [$]                 1270059.48059
Return [%]                          -53.56662
Buy & Hold Return [%]                34.67633
Sharpe Ratio                         -1.26398
Sortino Ratio                        -1.26041
Max. Drawdown [%]                   -64.58049
# Trades                                  475
Win Rate [%]                         43.78947
Best Trade [%]                        9.46694
Worst Trade [%]                      -9.44382
Avg. Trade [%]                       -0.16436
Profit Factor                         0.83229
Expectancy [%]                       -0.13829
SQN                                  -1.15059
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

# -- Data ---------------------------------------------------------
data = load_btc_data()


# -- Standalone computation functions -----------------------------
def compute_ha_close(open_, high, low, close):
    """HA_Close = (O + H + L + C) / 4"""
    return (open_ + high + low + close) / 4.0


def compute_ha_open(open_, close):
    """HA_Open = rolling average of previous HA_Open and HA_Close.
    First bar: (Open + Close) / 2, then iterative."""
    ha_close = (open_ + np.roll(open_, 0) + np.roll(close, 0) + close) / 4.0
    # Actually compute properly iteratively
    n = len(open_)
    ha_open = np.empty(n)
    ha_c = (open_ + np.array(close) + np.array(open_) + np.array(close)) / 4.0
    # Recompute HA properly
    ha_c = (np.array(open_) + np.array(high if 'high' in dir() else open_) +
            np.array(close) + np.array(close)) / 4.0
    # This is getting tangled. Let me just return a placeholder and
    # compute HA in a single function.
    return ha_open


def compute_heikin_ashi(open_, high, low, close):
    """Compute all 4 Heikin Ashi series. Returns (ha_open, ha_high, ha_low, ha_close)."""
    n = len(close)
    ha_close = (open_ + high + low + close) / 4.0
    ha_open = np.empty(n)
    ha_open[0] = (open_[0] + close[0]) / 2.0
    for i in range(1, n):
        ha_open[i] = (ha_open[i - 1] + ha_close[i - 1]) / 2.0
    ha_high = np.maximum(high, np.maximum(ha_open, ha_close))
    ha_low = np.minimum(low, np.minimum(ha_open, ha_close))
    return ha_close  # return one at a time for self.I()


def compute_ha_open_series(open_, high, low, close):
    """Compute HA Open series."""
    n = len(close)
    ha_close = (open_ + high + low + close) / 4.0
    ha_open = np.empty(n)
    ha_open[0] = (open_[0] + close[0]) / 2.0
    for i in range(1, n):
        ha_open[i] = (ha_open[i - 1] + ha_close[i - 1]) / 2.0
    return ha_open


def compute_ha_high(open_, high, low, close):
    """Compute HA High series."""
    n = len(close)
    ha_close = (open_ + high + low + close) / 4.0
    ha_open = np.empty(n)
    ha_open[0] = (open_[0] + close[0]) / 2.0
    for i in range(1, n):
        ha_open[i] = (ha_open[i - 1] + ha_close[i - 1]) / 2.0
    return np.maximum(high, np.maximum(ha_open, ha_close))


def compute_ha_low(open_, high, low, close):
    """Compute HA Low series."""
    n = len(close)
    ha_close = (open_ + high + low + close) / 4.0
    ha_open = np.empty(n)
    ha_open[0] = (open_[0] + close[0]) / 2.0
    for i in range(1, n):
        ha_open[i] = (ha_open[i - 1] + ha_close[i - 1]) / 2.0
    return np.minimum(low, np.minimum(ha_open, ha_close))


def compute_supertrend(high, low, close, period=10, multiplier=3.0):
    """Compute Supertrend. Returns: +1 for bullish, -1 for bearish."""
    atr = talib.ATR(high, low, close, timeperiod=period)
    hl2 = (high + low) / 2.0

    upper_band = hl2 + multiplier * atr
    lower_band = hl2 - multiplier * atr

    n = len(close)
    supertrend = np.zeros(n)
    direction = np.ones(n)  # 1 = bullish, -1 = bearish

    final_upper = np.copy(upper_band)
    final_lower = np.copy(lower_band)

    for i in range(1, n):
        if np.isnan(atr[i]):
            direction[i] = direction[i - 1]
            continue

        # Final upper band: don't let it increase if previous was lower
        if final_upper[i] < final_upper[i - 1] or close[i - 1] > final_upper[i - 1]:
            final_upper[i] = final_upper[i]
        else:
            final_upper[i] = final_upper[i - 1]

        # Final lower band: don't let it decrease if previous was higher
        if final_lower[i] > final_lower[i - 1] or close[i - 1] < final_lower[i - 1]:
            final_lower[i] = final_lower[i]
        else:
            final_lower[i] = final_lower[i - 1]

        # Direction
        if direction[i - 1] == 1:  # was bullish
            if close[i] < final_lower[i]:
                direction[i] = -1
            else:
                direction[i] = 1
        else:  # was bearish
            if close[i] > final_upper[i]:
                direction[i] = 1
            else:
                direction[i] = -1

    return direction


def compute_volume_sma(volume, period=20):
    return talib.SMA(np.asarray(volume, dtype=np.float64), timeperiod=period)


# -- Strategy ------------------------------------------------------
class HeikinAshiSupertrendVolume(Strategy):
    st_period = 10
    st_multiplier = 3.0
    vol_sma_period = 20
    wick_threshold = 0.10  # 10% of range for "no wick" relaxation
    consec_color_change = 2  # consecutive HA color changes to exit

    def init(self):
        # Heikin Ashi components
        self.ha_close = self.I(compute_heikin_ashi,
                               self.data.Open, self.data.High,
                               self.data.Low, self.data.Close)
        self.ha_open = self.I(compute_ha_open_series,
                              self.data.Open, self.data.High,
                              self.data.Low, self.data.Close)
        self.ha_high = self.I(compute_ha_high,
                              self.data.Open, self.data.High,
                              self.data.Low, self.data.Close)
        self.ha_low = self.I(compute_ha_low,
                             self.data.Open, self.data.High,
                             self.data.Low, self.data.Close)

        # Supertrend on regular candles
        self.supertrend = self.I(compute_supertrend,
                                 self.data.High, self.data.Low, self.data.Close,
                                 self.st_period, self.st_multiplier)

        # Volume SMA
        self.vol_sma = self.I(compute_volume_sma, self.data.Volume, self.vol_sma_period)

        # Track consecutive color changes for exit
        self.color_change_count = 0
        self.prev_ha_bullish = None

    def next(self):
        ha_c = self.ha_close[-1]
        ha_o = self.ha_open[-1]
        ha_h = self.ha_high[-1]
        ha_l = self.ha_low[-1]
        st = self.supertrend[-1]
        vol = self.data.Volume[-1]
        vol_sma = self.vol_sma[-1]

        # Skip if not ready
        if np.isnan(ha_c) or np.isnan(ha_o) or np.isnan(st) or np.isnan(vol_sma):
            return

        ha_bullish = ha_c > ha_o
        ha_range = ha_h - ha_l
        if ha_range == 0:
            return

        # Wick sizes
        lower_wick = (min(ha_o, ha_c) - ha_l) / ha_range
        upper_wick = (ha_h - max(ha_o, ha_c)) / ha_range

        # Track consecutive color changes
        if self.prev_ha_bullish is not None:
            if ha_bullish != self.prev_ha_bullish:
                self.color_change_count += 1
            else:
                self.color_change_count = 0
        self.prev_ha_bullish = ha_bullish

        st_bullish = st > 0
        vol_confirm = vol > vol_sma

        # Strong HA candles
        strong_bullish_ha = ha_bullish and lower_wick < self.wick_threshold
        strong_bearish_ha = (not ha_bullish) and upper_wick < self.wick_threshold

        # Exit conditions
        if self.position.is_long:
            if self.color_change_count >= self.consec_color_change or not st_bullish:
                self.position.close()
                return
        elif self.position.is_short:
            if self.color_change_count >= self.consec_color_change or st_bullish:
                self.position.close()
                return

        # Entry signals (only when flat)
        if not self.position:
            if strong_bullish_ha and st_bullish and vol_confirm:
                self.buy()
            elif strong_bearish_ha and (not st_bullish) and vol_confirm:
                self.sell()


# -- Run ----------------------------------------------------------
bt = Backtest(
    data,
    HeikinAshiSupertrendVolume,
    cash=1_000_000,
    commission=0.001,
    exclusive_orders=True,
)

stats = bt.run()
print(stats)
print(f"\n_strategy_name: HeikinAshiSupertrendVolume")
