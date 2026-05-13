"""
Pivot Points + RSI + VWAP Strategy
=====================================
Institutional-style trading using floor trader pivot levels with VWAP fair value.

- Classic Pivot Points from rolling 24-bar window (24h on 1h data)
  PP = (H24 + L24 + C) / 3
  R1 = 2*PP - L24, S1 = 2*PP - H24
  R2 = PP + (H24 - L24), S2 = PP - (H24 - L24)
- Rolling VWAP = sum(TP * Volume, 24) / sum(Volume, 24)
- RSI(14) for timing

LONG: Price bounces off S1/S2 support (within 0.5% in last 3 bars) + RSI < 40 + price > VWAP
SHORT: Price rejected at R1/R2 resistance (within 0.5% in last 3 bars) + RSI > 60 + price < VWAP
EXIT: Price reaches PP (from S-level entries) or opposite pivot, OR trail with 1.5x ATR in profit

STATS:
---
Start                     2024-02-12 05:00:00+00:00
End                       2026-02-11 05:00:00+00:00
Duration                    730 days 00:00:00
Exposure Time [%]                     0.46315
Equity Final [$]                 925766.39454
Equity Peak [$]                     1000000.0
Return [%]                           -7.42336
Buy & Hold Return [%]                35.13071
Sharpe Ratio                         -1.59162
Sortino Ratio                         -1.6247
Max. Drawdown [%]                    -7.42336
# Trades                                   14
Win Rate [%]                         35.71429
Best Trade [%]                        0.48229
Worst Trade [%]                      -1.86473
Avg. Trade [%]                       -0.57101
Profit Factor                         0.14349
Expectancy [%]                       -0.56837
SQN                                  -2.82355
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


# -- Standalone helper functions ----------------------------------
def compute_rolling_high24(high, period=24):
    """Rolling 24-bar high."""
    return talib.MAX(high, timeperiod=period)


def compute_rolling_low24(low, period=24):
    """Rolling 24-bar low."""
    return talib.MIN(low, timeperiod=period)


def compute_rolling_vwap(high, low, close, volume, period=24):
    """Approximate rolling VWAP: sum(TP * vol, 24) / sum(vol, 24)."""
    tp = (high + low + close) / 3.0
    n = len(close)
    vwap = np.full(n, np.nan)
    for i in range(period - 1, n):
        vol_sum = np.sum(volume[i - period + 1:i + 1])
        if vol_sum > 0:
            vwap[i] = np.sum(tp[i - period + 1:i + 1] * volume[i - period + 1:i + 1]) / vol_sum
    return vwap


# -- Strategy ------------------------------------------------------
class PivotRsiVwap(Strategy):
    pivot_period = 24
    rsi_period = 14
    atr_period = 14
    atr_trail_mult = 1.5
    proximity_pct = 0.005  # 0.5% proximity to pivot level
    lookback_bars = 3  # look back 3 bars for "bounce"
    rsi_oversold = 40
    rsi_overbought = 60

    def init(self):
        self.h24 = self.I(compute_rolling_high24, self.data.High, self.pivot_period)
        self.l24 = self.I(compute_rolling_low24, self.data.Low, self.pivot_period)
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=self.rsi_period)
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close,
                          timeperiod=self.atr_period)
        self.vwap = self.I(compute_rolling_vwap,
                           self.data.High, self.data.Low, self.data.Close,
                           self.data.Volume, self.pivot_period)

        # Track entry level and trailing stop
        self.entry_from_support = False
        self.trailing_stop = 0.0
        self.target_level = 0.0
        self.entry_price = 0.0

    def _compute_pivots(self):
        """Compute pivot levels from current rolling H24/L24 and close."""
        h24 = self.h24[-1]
        l24 = self.l24[-1]
        c = self.data.Close[-1]
        pp = (h24 + l24 + c) / 3.0
        r1 = 2 * pp - l24
        s1 = 2 * pp - h24
        r2 = pp + (h24 - l24)
        s2 = pp - (h24 - l24)
        return pp, r1, r2, s1, s2

    def _near_level(self, level):
        """Check if price was within proximity_pct of level in last lookback_bars."""
        for i in range(1, min(self.lookback_bars + 1, len(self.data.Close))):
            bar_low = self.data.Low[-i]
            bar_high = self.data.High[-i]
            threshold = level * self.proximity_pct
            if abs(bar_low - level) <= threshold or abs(bar_high - level) <= threshold:
                return True
            # Also check if price crossed through the level
            if bar_low <= level <= bar_high:
                return True
        return False

    def _bounced_off_support(self, level):
        """Price was near support level recently and is now moving above it."""
        price = self.data.Close[-1]
        return self._near_level(level) and price > level

    def _rejected_at_resistance(self, level):
        """Price was near resistance level recently and is now moving below it."""
        price = self.data.Close[-1]
        return self._near_level(level) and price < level

    def next(self):
        price = self.data.Close[-1]
        rsi = self.rsi[-1]
        atr = self.atr[-1]
        vwap = self.vwap[-1]

        # Skip if indicators not ready
        if np.isnan(self.h24[-1]) or np.isnan(self.l24[-1]) or np.isnan(rsi):
            return
        if np.isnan(atr) or np.isnan(vwap):
            return

        pp, r1, r2, s1, s2 = self._compute_pivots()

        # Manage existing positions
        if self.position.is_long:
            # Update trailing stop if in profit
            if self.entry_price > 0 and price > self.entry_price:
                new_stop = price - self.atr_trail_mult * atr
                if new_stop > self.trailing_stop:
                    self.trailing_stop = new_stop

            # Exit: hit target or trailing stop
            if self.target_level > 0 and price >= self.target_level:
                self.position.close()
                self.trailing_stop = 0.0
                self.target_level = 0.0
                self.entry_price = 0.0
                return
            if self.trailing_stop > 0 and price <= self.trailing_stop:
                self.position.close()
                self.trailing_stop = 0.0
                self.target_level = 0.0
                self.entry_price = 0.0
                return

        elif self.position.is_short:
            # Update trailing stop if in profit
            if self.entry_price > 0 and price < self.entry_price:
                new_stop = price + self.atr_trail_mult * atr
                if self.trailing_stop == 0 or new_stop < self.trailing_stop:
                    self.trailing_stop = new_stop

            # Exit: hit target or trailing stop
            if self.target_level > 0 and price <= self.target_level:
                self.position.close()
                self.trailing_stop = 0.0
                self.target_level = 0.0
                self.entry_price = 0.0
                return
            if self.trailing_stop > 0 and price >= self.trailing_stop:
                self.position.close()
                self.trailing_stop = 0.0
                self.target_level = 0.0
                self.entry_price = 0.0
                return

        # Entry signals (only when flat)
        if not self.position:
            # LONG: Bounce off S1 or S2 + RSI oversold + price > VWAP
            if rsi < self.rsi_oversold and price > vwap:
                if self._bounced_off_support(s1):
                    self.buy()
                    self.entry_price = price
                    self.trailing_stop = price - self.atr_trail_mult * atr
                    self.target_level = pp  # target pivot point
                    self.entry_from_support = True
                elif self._bounced_off_support(s2):
                    self.buy()
                    self.entry_price = price
                    self.trailing_stop = price - self.atr_trail_mult * atr
                    self.target_level = s1  # target S1 from S2 entry
                    self.entry_from_support = True

            # SHORT: Rejected at R1 or R2 + RSI overbought + price < VWAP
            elif rsi > self.rsi_overbought and price < vwap:
                if self._rejected_at_resistance(r1):
                    self.sell()
                    self.entry_price = price
                    self.trailing_stop = price + self.atr_trail_mult * atr
                    self.target_level = pp  # target pivot point
                    self.entry_from_support = False
                elif self._rejected_at_resistance(r2):
                    self.sell()
                    self.entry_price = price
                    self.trailing_stop = price + self.atr_trail_mult * atr
                    self.target_level = r1  # target R1 from R2 entry
                    self.entry_from_support = False


# -- Run ----------------------------------------------------------
bt = Backtest(
    data,
    PivotRsiVwap,
    cash=1_000_000,
    commission=0.001,
    exclusive_orders=True,
)

stats = bt.run()
print(stats)
print(f"\n_strategy_name: PivotRsiVwap")
