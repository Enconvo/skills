"""
BACKTEST TEMPLATE — TradingView Community Indicator Backtester
==============================================================
Copy this file and rename for each new strategy conversion.

STATS (paste after running):
---
[paste stats here]
---
"""

import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy
from backtesting.lib import crossover, crossunder
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_btc_data

# ── Data ─────────────────────────────────────────────────────
data = load_btc_data()

# ── Strategy ─────────────────────────────────────────────────
class MyStrategy(Strategy):
    # Parameters (keep unoptimized!)
    param1 = 14  # example

    def init(self):
        # Calculate indicators here using self.I()
        # Example: self.sma = self.I(talib.SMA, self.data.Close, timeperiod=self.param1)
        pass

    def next(self):
        # Trading logic here
        # if crossover(self.fast_ma, self.slow_ma):
        #     self.buy()
        # elif crossunder(self.fast_ma, self.slow_ma):
        #     self.position.close()
        pass

# ── Run ──────────────────────────────────────────────────────
bt = Backtest(
    data,
    MyStrategy,
    cash=1_000_000,
    commission=0.001,
    exclusive_orders=True,
)

stats = bt.run()
print(stats)
print(f"\n_strategy_name: MyStrategy")
