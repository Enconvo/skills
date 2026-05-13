"""
BACKTEST: Chandelier Exit + Parabolic SAR Dual Trailing-Stop System
====================================================================
Double trailing-stop system combining:
- Chandelier Exit: highest_high(22) - 3*ATR(22) for longs, lowest_low(22) + 3*ATR(22) for shorts
- Parabolic SAR(0.02, 0.2)
- EMA(50) trend filter
- Enter when both systems agree, exit when either triggers

STATS:
---
Start                     2024-02-12 05:00:00+00:00
End                       2026-02-11 05:00:00+00:00
Duration                    730 days 00:00:00
Exposure Time [%]                     15.6384
Equity Final [$]                 648252.19775
Equity Peak [$]                 1135296.20856
Return [%]                          -35.17478
Buy & Hold Return [%]                35.86069
Return (Ann.) [%]                   -19.46201
Volatility (Ann.) [%]                16.32386
Sharpe Ratio                         -1.19224
Sortino Ratio                        -1.47576
Calmar Ratio                         -0.45254
Max. Drawdown [%]                   -43.00641
Avg. Drawdown [%]                    -3.95185
# Trades                                  261
Win Rate [%]                         29.88506
Best Trade [%]                        9.69402
Worst Trade [%]                      -5.68259
Avg. Trade [%]                       -0.18013
Max. Trade Duration           1 days 10:00:00
Avg. Trade Duration           0 days 10:00:00
Profit Factor                         0.76568
Expectancy [%]                       -0.16379
SQN                                  -1.37837
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


# ── Helper functions ─────────────────────────────────────────
def chandelier_long_stop(high, low, close, period=22, mult=3.0):
    """Chandelier long stop: highest_high(period) - mult * ATR(period)."""
    highest = talib.MAX(high, timeperiod=period)
    atr = talib.ATR(high, low, close, timeperiod=period)
    return highest - mult * atr

def chandelier_short_stop(high, low, close, period=22, mult=3.0):
    """Chandelier short stop: lowest_low(period) + mult * ATR(period)."""
    lowest = talib.MIN(low, timeperiod=period)
    atr = talib.ATR(high, low, close, timeperiod=period)
    return lowest + mult * atr


# ── Strategy ─────────────────────────────────────────────────
class ChandelierPSARSystem(Strategy):
    chand_period = 22
    chand_mult = 3.0
    sar_accel = 0.02
    sar_max = 0.2
    ema_period = 50

    def init(self):
        # Chandelier stops
        self.chand_long = self.I(chandelier_long_stop,
                                  self.data.High, self.data.Low, self.data.Close,
                                  self.chand_period, self.chand_mult, name='Chand_Long')
        self.chand_short = self.I(chandelier_short_stop,
                                   self.data.High, self.data.Low, self.data.Close,
                                   self.chand_period, self.chand_mult, name='Chand_Short')

        # Parabolic SAR
        self.sar = self.I(talib.SAR, self.data.High, self.data.Low,
                          acceleration=self.sar_accel, maximum=self.sar_max)

        # EMA trend filter
        self.ema = self.I(talib.EMA, self.data.Close, timeperiod=self.ema_period)

    def next(self):
        if len(self.data) < 55:
            return

        price = self.data.Close[-1]
        prev_price = self.data.Close[-2]
        sar_now = self.sar[-1]
        ema_now = self.ema[-1]
        chand_long_now = self.chand_long[-1]
        chand_long_prev = self.chand_long[-2]
        chand_short_now = self.chand_short[-1]
        chand_short_prev = self.chand_short[-2]

        if np.isnan(chand_long_now) or np.isnan(sar_now) or np.isnan(ema_now):
            return

        sar_below = sar_now < price
        sar_above = sar_now > price

        # Cross above chandelier long stop
        price_crossed_above_chand_long = (prev_price <= chand_long_prev) and (price > chand_long_now)
        # Cross below chandelier short stop
        price_crossed_below_chand_short = (prev_price >= chand_short_prev) and (price < chand_short_now)

        # Exit conditions (conservative — either stop triggers)
        if self.position.is_long:
            if price < chand_long_now or sar_above:
                self.position.close()
                return
        elif self.position.is_short:
            if price > chand_short_now or sar_below:
                self.position.close()
                return

        # Entry conditions
        if price > ema_now and price_crossed_above_chand_long and sar_below:
            if not self.position.is_long:
                self.buy()
        elif price < ema_now and price_crossed_below_chand_short and sar_above:
            if not self.position.is_short:
                self.sell()


# ── Run ──────────────────────────────────────────────────────
bt = Backtest(
    data,
    ChandelierPSARSystem,
    cash=1_000_000,
    commission=0.001,
    exclusive_orders=True,
)

stats = bt.run()
print(stats)
print(f"\n_strategy_name: ChandelierPSARSystem")
