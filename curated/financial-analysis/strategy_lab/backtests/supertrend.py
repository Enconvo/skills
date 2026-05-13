"""
Supertrend Strategy
===================
Supertrend indicator (ATR period=10, multiplier=3.0).

Supertrend uses ATR bands with sticky logic to determine trend direction.
LONG: price crosses above supertrend (trend flips bullish)
SHORT: price crosses below supertrend (trend flips bearish)

STATS:
---
Start                     2024-02-12 05:00:00+00:00
End                       2026-02-11 05:00:00+00:00
Duration                    730 days 00:00:00
Exposure Time [%]                    99.70839
Equity Final [$]                 450613.84611
Equity Peak [$]                 1502912.52102
Return [%]                          -54.93862
Buy & Hold Return [%]                35.11361
Return (Ann.) [%]                   -32.83561
Volatility (Ann.) [%]                32.38897
Sharpe Ratio                         -1.01379
Sortino Ratio                        -1.01121
Calmar Ratio                         -0.45528
Max. Drawdown [%]                   -72.12166
Avg. Drawdown [%]                    -4.26706
# Trades                                  484
Win Rate [%]                         31.61157
Best Trade [%]                       26.36857
Worst Trade [%]                      -5.99985
Avg. Trade [%]                       -0.18029
Profit Factor                         0.87762
Expectancy [%]                       -0.13638
SQN                                  -0.92341
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

    # Initialize first valid index
    first_valid = atr_period  # ATR needs atr_period bars
    final_upper[first_valid] = basic_upper[first_valid]
    final_lower[first_valid] = basic_lower[first_valid]
    direction[first_valid] = 1.0  # start bullish

    for i in range(first_valid + 1, n):
        # Final upper band (sticky logic)
        if close[i - 1] <= final_upper[i - 1]:
            final_upper[i] = min(basic_upper[i], final_upper[i - 1])
        else:
            final_upper[i] = basic_upper[i]

        # Final lower band (sticky logic)
        if close[i - 1] >= final_lower[i - 1]:
            final_lower[i] = max(basic_lower[i], final_lower[i - 1])
        else:
            final_lower[i] = basic_lower[i]

        # Direction logic
        if direction[i - 1] == 1.0:  # was bullish
            if close[i] < final_lower[i]:
                direction[i] = -1.0  # flip bearish
            else:
                direction[i] = 1.0
        else:  # was bearish
            if close[i] > final_upper[i]:
                direction[i] = 1.0  # flip bullish
            else:
                direction[i] = -1.0

    return direction


# ── Strategy ─────────────────────────────────────────────────
class Supertrend(Strategy):
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

        # Trend flip from bearish to bullish
        if curr_dir == 1.0 and prev_dir == -1.0:
            if self.position.is_short:
                self.position.close()
            self.buy()

        # Trend flip from bullish to bearish
        elif curr_dir == -1.0 and prev_dir == 1.0:
            if self.position.is_long:
                self.position.close()
            self.sell()


# ── Run ──────────────────────────────────────────────────────
bt = Backtest(
    data,
    Supertrend,
    cash=1_000_000,
    commission=0.001,
    exclusive_orders=True,
)

stats = bt.run()
print(stats)
print(f"\n_strategy_name: Supertrend")
