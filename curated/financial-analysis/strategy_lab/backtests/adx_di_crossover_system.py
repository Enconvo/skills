"""
ADX DI Crossover System — Wilder's Directional Movement
=========================================================
Welles Wilder's original Directional Movement System.
+DI/-DI crossovers with ADX trend strength confirmation.
Battle-tested trend-following system with ATR-based stops.

STATS:
---
Start                     2024-02-12 05:00:00+00:00
End                       2026-02-11 05:00:00+00:00
Duration                    730 days 00:00:00
Exposure Time [%]                     0.50889
Equity Final [$]                 948416.41772
Equity Peak [$]                 1021222.53438
Return [%]                           -5.15836
Buy & Hold Return [%]                34.55834
Return (Ann.) [%]                     -2.6098
Volatility (Ann.) [%]                 2.47313
Sharpe Ratio                         -1.05526
Sortino Ratio                        -1.12943
Max. Drawdown [%]                    -7.12931
Avg. Drawdown [%]                    -2.06308
# Trades                                    6
Win Rate [%]                         16.66667
Best Trade [%]                        0.65438
Worst Trade [%]                      -2.25607
Avg. Trade [%]                       -0.92083
Profit Factor                         0.10641
Expectancy [%]                       -0.91584
SQN                                  -2.02638
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


# ── Strategy ─────────────────────────────────────────────────
class ADXDICrossoverSystem(Strategy):
    # ADX/DI parameters
    adx_period = 14
    adx_threshold = 25
    adx_exit_threshold = 20
    # ATR stop loss
    atr_period = 14
    atr_mult = 2.0

    def init(self):
        self.adx = self.I(talib.ADX, self.data.High, self.data.Low,
                          self.data.Close, timeperiod=self.adx_period)
        self.plus_di = self.I(talib.PLUS_DI, self.data.High, self.data.Low,
                              self.data.Close, timeperiod=self.adx_period)
        self.minus_di = self.I(talib.MINUS_DI, self.data.High, self.data.Low,
                               self.data.Close, timeperiod=self.adx_period)
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low,
                          self.data.Close, timeperiod=self.atr_period)

    def next(self):
        adx_val = self.adx[-1]
        adx_prev = self.adx[-2]
        plus_di = self.plus_di[-1]
        plus_di_prev = self.plus_di[-2]
        minus_di = self.minus_di[-1]
        minus_di_prev = self.minus_di[-2]
        atr_val = self.atr[-1]
        price = self.data.Close[-1]

        # Skip if indicators not ready
        if any(np.isnan(v) for v in [adx_val, adx_prev, plus_di, plus_di_prev,
                                      minus_di, minus_di_prev, atr_val]):
            return

        # DI crossover detection
        plus_di_cross_above = plus_di > minus_di and plus_di_prev <= minus_di_prev
        minus_di_cross_above = minus_di > plus_di and minus_di_prev <= plus_di_prev

        # ADX rising filter — trend is strengthening
        adx_rising = adx_val > adx_prev

        # Exit conditions
        if self.position.is_long:
            # Exit: ADX drops below exit threshold or -DI crosses above +DI
            if adx_val < self.adx_exit_threshold or minus_di_cross_above:
                self.position.close()
                return
        elif self.position.is_short:
            # Exit: ADX drops below exit threshold or +DI crosses above -DI
            if adx_val < self.adx_exit_threshold or plus_di_cross_above:
                self.position.close()
                return

        # Entry conditions
        # LONG: +DI crosses above -DI, ADX > 25 and rising
        if plus_di_cross_above and adx_val > self.adx_threshold and adx_rising:
            if not self.position.is_long:
                sl_price = price - self.atr_mult * atr_val
                self.buy(sl=sl_price)

        # SHORT: -DI crosses above +DI, ADX > 25 and rising
        elif minus_di_cross_above and adx_val > self.adx_threshold and adx_rising:
            if not self.position.is_short:
                sl_price = price + self.atr_mult * atr_val
                self.sell(sl=sl_price)


# ── Run ──────────────────────────────────────────────────────
bt = Backtest(
    data,
    ADXDICrossoverSystem,
    cash=1_000_000,
    commission=0.001,
    exclusive_orders=True,
)

stats = bt.run()
print(stats)
print(f"\n_strategy_name: ADXDICrossoverSystem")
