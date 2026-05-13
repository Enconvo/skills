"""
BACKTEST: Donchian Channel Breakout with ATR Filter
====================================================
Turtle Trading inspired system adapted for crypto.
- 20-period Donchian Channel for entries
- 10-period Donchian Channel for exits (tighter)
- ATR(14) must be above its 50-period SMA (volatility expanding)
- Entry/exit channel asymmetry is key to the system

STATS:
---
Start                     2024-02-12 05:00:00+00:00
End                       2026-02-11 05:00:00+00:00
Duration                    730 days 00:00:00
Exposure Time [%]                    47.73858
Equity Final [$]                 326387.72571
Equity Peak [$]                 1154805.65951
Return [%]                          -67.36123
Buy & Hold Return [%]                30.31041
Return (Ann.) [%]                   -42.82588
Volatility (Ann.) [%]                20.21802
Sharpe Ratio                          -2.1182
Sortino Ratio                        -1.86818
Calmar Ratio                         -0.56571
Max. Drawdown [%]                   -75.70231
Avg. Drawdown [%]                    -6.70987
# Trades                                  505
Win Rate [%]                         32.67327
Best Trade [%]                       17.46067
Worst Trade [%]                      -5.45772
Avg. Trade [%]                       -0.24414
Max. Trade Duration           3 days 01:00:00
Avg. Trade Duration           0 days 16:00:00
Profit Factor                         0.73882
Expectancy [%]                       -0.22177
SQN                                  -2.10899
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
def donchian_upper(high, period=20):
    """Highest high over period (shifted by 1 to not include current bar)."""
    return talib.MAX(high, timeperiod=period)

def donchian_lower(low, period=20):
    """Lowest low over period (shifted by 1 to not include current bar)."""
    return talib.MIN(low, timeperiod=period)

def atr_sma(high, low, close, atr_period=14, sma_period=50):
    """SMA of ATR — used as volatility expansion filter."""
    atr = talib.ATR(high, low, close, timeperiod=atr_period)
    return talib.SMA(atr, timeperiod=sma_period)


# ── Strategy ─────────────────────────────────────────────────
class DonchianBreakoutATR(Strategy):
    entry_period = 20
    exit_period = 10
    atr_period = 14
    atr_sma_period = 50

    def init(self):
        # Entry channels (20-period)
        self.dc_upper = self.I(donchian_upper, self.data.High, self.entry_period, name='DC_Upper_20')
        self.dc_lower = self.I(donchian_lower, self.data.Low, self.entry_period, name='DC_Lower_20')

        # Exit channels (10-period)
        self.exit_lower = self.I(donchian_lower, self.data.Low, self.exit_period, name='DC_Lower_10')
        self.exit_upper = self.I(donchian_upper, self.data.High, self.exit_period, name='DC_Upper_10')

        # ATR and its SMA
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close,
                          timeperiod=self.atr_period)
        self.atr_avg = self.I(atr_sma, self.data.High, self.data.Low, self.data.Close,
                              self.atr_period, self.atr_sma_period, name='ATR_SMA')

    def next(self):
        if len(self.data) < 55:
            return

        price = self.data.Close[-1]
        high = self.data.High[-1]
        low = self.data.Low[-1]

        # Previous bar's channels (so current bar can "break" them)
        dc_up = self.dc_upper[-2]
        dc_dn = self.dc_lower[-2]
        exit_dn = self.exit_lower[-1]
        exit_up = self.exit_upper[-1]
        atr_val = self.atr[-1]
        atr_avg_val = self.atr_avg[-1]

        if np.isnan(dc_up) or np.isnan(dc_dn) or np.isnan(atr_val) or np.isnan(atr_avg_val):
            return

        vol_expanding = atr_val > atr_avg_val

        # Exit conditions (check before entries)
        if self.position.is_long:
            if low <= exit_dn:
                self.position.close()
                return
        elif self.position.is_short:
            if high >= exit_up:
                self.position.close()
                return

        # Entry conditions: breakout + volatility expanding
        if vol_expanding:
            if high > dc_up and not self.position.is_long:
                if self.position.is_short:
                    self.position.close()
                self.buy()
            elif low < dc_dn and not self.position.is_short:
                if self.position.is_long:
                    self.position.close()
                self.sell()


# ── Run ──────────────────────────────────────────────────────
bt = Backtest(
    data,
    DonchianBreakoutATR,
    cash=1_000_000,
    commission=0.001,
    exclusive_orders=True,
)

stats = bt.run()
print(stats)
print(f"\n_strategy_name: DonchianBreakoutATR")
