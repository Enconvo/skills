"""
MACD RSI Volume Divergence Strategy
=====================================
MACD histogram reversal + RSI divergence filter + volume spike confirmation.
Catches momentum reversals with conviction — filters out weak/noisy signals.

STATS:
---
Start                     2024-02-12 05:00:00+00:00
End                       2026-02-11 05:00:00+00:00
Duration                    730 days 00:00:00
Exposure Time [%]                    18.72606
Equity Final [$]                 581289.74855
Equity Peak [$]                 1125410.30159
Return [%]                          -41.87103
Buy & Hold Return [%]                38.43745
Return (Ann.) [%]                   -23.72934
Volatility (Ann.) [%]                16.79955
Sharpe Ratio                          -1.4125
Sortino Ratio                        -1.62139
Max. Drawdown [%]                   -57.30198
Avg. Drawdown [%]                    -6.03626
# Trades                                  264
Win Rate [%]                         31.81818
Best Trade [%]                         9.1705
Worst Trade [%]                      -6.65855
Avg. Trade [%]                        -0.2232
Profit Factor                         0.73791
Expectancy [%]                       -0.20598
SQN                                    -1.841
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


# ── Helper functions for self.I() ────────────────────────────
def macd_histogram(close, fastperiod=12, slowperiod=26, signalperiod=9):
    """Return MACD histogram."""
    _, _, hist = talib.MACD(close, fastperiod=fastperiod,
                            slowperiod=slowperiod, signalperiod=signalperiod)
    return hist


def volume_sma(volume, timeperiod=20):
    """Return SMA of volume."""
    return talib.SMA(np.asarray(volume, dtype=np.float64), timeperiod=timeperiod)


# ── Strategy ─────────────────────────────────────────────────
class MACDRSIVolumeDivergence(Strategy):
    # MACD parameters
    macd_fast = 12
    macd_slow = 26
    macd_signal = 9
    # RSI parameters
    rsi_period = 14
    rsi_overbought = 70
    rsi_oversold = 30
    rsi_extreme_high = 80
    rsi_extreme_low = 20
    # Volume parameters
    vol_sma_period = 20
    vol_spike_mult = 1.5

    def init(self):
        self.macd_hist = self.I(macd_histogram, self.data.Close,
                                self.macd_fast, self.macd_slow, self.macd_signal)
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=self.rsi_period)
        self.vol_sma = self.I(volume_sma, self.data.Volume, self.vol_sma_period)

    def next(self):
        hist_curr = self.macd_hist[-1]
        hist_prev = self.macd_hist[-2]
        rsi_val = self.rsi[-1]
        vol_curr = self.data.Volume[-1]
        vol_avg = self.vol_sma[-1]

        # Skip if indicators not ready
        if np.isnan(hist_curr) or np.isnan(hist_prev) or np.isnan(rsi_val) or np.isnan(vol_avg):
            return

        # Volume spike check
        volume_spike = vol_curr > self.vol_spike_mult * vol_avg if vol_avg > 0 else False

        # MACD histogram reversal signals
        hist_turned_positive = hist_prev < 0 and hist_curr > 0
        hist_turned_negative = hist_prev > 0 and hist_curr < 0

        # Exit conditions first
        if self.position.is_long:
            # Exit long: opposite signal or RSI extreme
            if hist_turned_negative or rsi_val > self.rsi_extreme_high:
                self.position.close()
                return
        elif self.position.is_short:
            # Exit short: opposite signal or RSI extreme
            if hist_turned_positive or rsi_val < self.rsi_extreme_low:
                self.position.close()
                return

        # Entry conditions
        # LONG: histogram turns positive + RSI not overbought + volume spike
        if hist_turned_positive and rsi_val < self.rsi_overbought and volume_spike:
            if not self.position.is_long:
                self.buy()

        # SHORT: histogram turns negative + RSI not oversold + volume spike
        elif hist_turned_negative and rsi_val > self.rsi_oversold and volume_spike:
            if not self.position.is_short:
                self.sell()


# ── Run ──────────────────────────────────────────────────────
bt = Backtest(
    data,
    MACDRSIVolumeDivergence,
    cash=1_000_000,
    commission=0.001,
    exclusive_orders=True,
)

stats = bt.run()
print(stats)
print(f"\n_strategy_name: MACDRSIVolumeDivergence")
