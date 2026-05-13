"""
BACKTEST: Supertrend — LONG ONLY
=================================
Supertrend indicator (ATR period=10, multiplier=3.0) — long positions only.
- BUY: Supertrend flips from bearish to bullish (price crosses above band)
- EXIT: Supertrend flips from bullish to bearish
- No shorting — sits in cash during bearish periods.

STATS:
---
Start                     2024-02-12 05:00:00+00:00
End                       2026-02-11 05:00:00+00:00
Duration                    730 days 00:00:00
Exposure Time [%]                    52.82177
Equity Final [$]                 861075.86386
Equity Peak [$]                 1738738.25155
Return [%]                          -13.89241
Buy & Hold Return [%]                35.11361
Return (Ann.) [%]                    -7.19633
Volatility (Ann.) [%]                32.97747
Sharpe Ratio                         -0.21822
Sortino Ratio                        -0.34116
Calmar Ratio                         -0.14257
Max. Drawdown [%]                   -50.47697
Avg. Drawdown [%]                    -3.04137
# Trades                                  242
Win Rate [%]                         32.64463
Best Trade [%]                       26.36857
Worst Trade [%]                      -4.60914
Avg. Trade [%]                        -0.0694
Max. Trade Duration           8 days 02:00:00
Avg. Trade Duration           1 days 14:00:00
Profit Factor                         0.98054
Expectancy [%]                       -0.02078
SQN                                  -0.23397
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


# ── Supertrend Calculation (standalone function) ─────────────
def calc_supertrend_direction(high, low, close, atr_period=10, multiplier=3.0):
    """
    Compute Supertrend direction array.
    Returns: array where 1 = bullish, -1 = bearish.
    """
    atr = talib.ATR(high, low, close, timeperiod=atr_period)
    hl2 = (high + low) / 2.0

    basic_upper = hl2 + multiplier * atr
    basic_lower = hl2 - multiplier * atr

    n = len(close)
    final_upper = np.full(n, np.nan)
    final_lower = np.full(n, np.nan)
    direction = np.full(n, np.nan)

    first_valid = atr_period
    final_upper[first_valid] = basic_upper[first_valid]
    final_lower[first_valid] = basic_lower[first_valid]
    direction[first_valid] = 1.0

    for i in range(first_valid + 1, n):
        if close[i - 1] <= final_upper[i - 1]:
            final_upper[i] = min(basic_upper[i], final_upper[i - 1])
        else:
            final_upper[i] = basic_upper[i]

        if close[i - 1] >= final_lower[i - 1]:
            final_lower[i] = max(basic_lower[i], final_lower[i - 1])
        else:
            final_lower[i] = basic_lower[i]

        if direction[i - 1] == 1.0:
            if close[i] < final_lower[i]:
                direction[i] = -1.0
            else:
                direction[i] = 1.0
        else:
            if close[i] > final_upper[i]:
                direction[i] = 1.0
            else:
                direction[i] = -1.0

    return direction


# ── Strategy ─────────────────────────────────────────────────
class SupertrendLongOnly(Strategy):
    atr_period = 10
    multiplier = 3.0

    def init(self):
        self.direction = self.I(
            calc_supertrend_direction,
            self.data.High,
            self.data.Low,
            self.data.Close,
            self.atr_period,
            self.multiplier,
        )

    def next(self):
        curr_dir = self.direction[-1]
        prev_dir = self.direction[-2]

        if np.isnan(curr_dir) or np.isnan(prev_dir):
            return

        # BUY: trend flips bullish
        if curr_dir == 1.0 and prev_dir == -1.0:
            if not self.position.is_long:
                self.buy()

        # EXIT: trend flips bearish — close long, sit in cash
        elif curr_dir == -1.0 and prev_dir == 1.0:
            if self.position.is_long:
                self.position.close()


# ── Run ──────────────────────────────────────────────────────
bt = Backtest(
    data,
    SupertrendLongOnly,
    cash=1_000_000,
    commission=0.001,
    exclusive_orders=True,
)

stats = bt.run()
print(stats)
print(f"\n_strategy_name: SupertrendLongOnly")
