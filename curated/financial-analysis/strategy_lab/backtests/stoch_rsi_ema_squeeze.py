"""
Stochastic RSI + EMA Squeeze Strategy
=======================================
StochRSI crossover from extremes + EMA200 trend filter + Bollinger Band
squeeze detection. Catches explosive breakouts after consolidation.

STATS:
---
Start                     2024-02-12 05:00:00+00:00
End                       2026-02-11 05:00:00+00:00
Duration                    730 days 00:00:00
Exposure Time [%]                    35.98262
Equity Final [$]                 599088.13009
Equity Peak [$]                 1037018.31086
Return [%]                          -40.09119
Buy & Hold Return [%]                29.28591
Return (Ann.) [%]                   -22.57209
Volatility (Ann.) [%]                18.08281
Sharpe Ratio                         -1.24826
Sortino Ratio                        -1.34546
Max. Drawdown [%]                   -45.24963
Avg. Drawdown [%]                    -7.68894
# Trades                                  500
Win Rate [%]                             47.0
Best Trade [%]                        6.18539
Worst Trade [%]                      -4.83908
Avg. Trade [%]                       -0.11012
Profit Factor                         0.83328
Expectancy [%]                       -0.09875
SQN                                  -1.48345
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
_stochrsi_cache = {}

def _get_stoch_rsi_k(close, rsi_period, stoch_period, k_smooth):
    """Compute and cache StochRSI %K to avoid redundant RSI calculation."""
    key = (id(close), rsi_period, stoch_period, k_smooth)
    if key not in _stochrsi_cache:
        rsi = talib.RSI(close, timeperiod=rsi_period)
        rsi_series = pd.Series(rsi)
        rsi_min = rsi_series.rolling(window=stoch_period).min().values
        rsi_max = rsi_series.rolling(window=stoch_period).max().values
        denom = rsi_max - rsi_min
        denom[denom == 0] = 1.0
        stoch_rsi = (rsi - rsi_min) / denom * 100
        _stochrsi_cache[key] = talib.SMA(stoch_rsi, timeperiod=k_smooth)
    return _stochrsi_cache[key]

def stoch_rsi_k(close, rsi_period=14, stoch_period=14, k_smooth=3):
    """Calculate Stochastic RSI %K line."""
    return _get_stoch_rsi_k(close, rsi_period, stoch_period, k_smooth)

def stoch_rsi_d(close, rsi_period=14, stoch_period=14, k_smooth=3, d_smooth=3):
    """Calculate Stochastic RSI %D line (SMA of %K)."""
    k = _get_stoch_rsi_k(close, rsi_period, stoch_period, k_smooth)
    d = talib.SMA(k, timeperiod=d_smooth)
    return d


def bb_bandwidth(close, timeperiod=20, nbdevup=2, nbdevdn=2):
    """Calculate Bollinger Band bandwidth: (upper - lower) / middle."""
    upper, middle, lower = talib.BBANDS(close, timeperiod=timeperiod,
                                         nbdevup=nbdevup, nbdevdn=nbdevdn)
    bw = np.where(middle != 0, (upper - lower) / middle, 0.0)
    return bw


def ema_200(close):
    """EMA 200."""
    return talib.EMA(close, timeperiod=200)


# ── Strategy ─────────────────────────────────────────────────
class StochRSIEmaSqueeze(Strategy):
    # StochRSI parameters
    rsi_period = 14
    stoch_period = 14
    k_smooth = 3
    d_smooth = 3
    stoch_oversold = 20
    stoch_overbought = 80
    # EMA trend filter
    ema_period = 200
    # Bollinger squeeze
    bb_period = 20
    squeeze_threshold = 0.04
    squeeze_lookback = 5

    def init(self):
        self.stoch_k = self.I(stoch_rsi_k, self.data.Close,
                              self.rsi_period, self.stoch_period, self.k_smooth)
        self.stoch_d = self.I(stoch_rsi_d, self.data.Close,
                              self.rsi_period, self.stoch_period,
                              self.k_smooth, self.d_smooth)
        self.ema = self.I(ema_200, self.data.Close)
        self.bbw = self.I(bb_bandwidth, self.data.Close, self.bb_period)

    def next(self):
        k_val = self.stoch_k[-1]
        d_val = self.stoch_d[-1]
        price = self.data.Close[-1]
        ema_val = self.ema[-1]

        # Skip if indicators not ready
        if np.isnan(k_val) or np.isnan(d_val) or np.isnan(ema_val):
            return

        # Check for recent BB squeeze (within last squeeze_lookback bars)
        recent_squeeze = False
        lookback = min(self.squeeze_lookback, len(self.bbw) - 1)
        for i in range(1, lookback + 1):
            if not np.isnan(self.bbw[-i]) and self.bbw[-i] < self.squeeze_threshold:
                recent_squeeze = True
                break

        # K crosses above D (bullish)
        k_cross_up = (self.stoch_k[-1] > self.stoch_d[-1] and
                      self.stoch_k[-2] <= self.stoch_d[-2])
        # K crosses below D (bearish)
        k_cross_down = (self.stoch_k[-1] < self.stoch_d[-1] and
                        self.stoch_k[-2] >= self.stoch_d[-2])

        # Was recently oversold/overbought (within last 3 bars)
        was_oversold = any(
            not np.isnan(self.stoch_k[-i]) and self.stoch_k[-i] < self.stoch_oversold
            for i in range(1, 4)
        )
        was_overbought = any(
            not np.isnan(self.stoch_k[-i]) and self.stoch_k[-i] > self.stoch_overbought
            for i in range(1, 4)
        )

        # Exit conditions
        if self.position.is_long:
            # Exit: StochRSI overbought extreme or price crosses below EMA
            if k_val > self.stoch_overbought or price < ema_val:
                self.position.close()
                return
        elif self.position.is_short:
            # Exit: StochRSI oversold extreme or price crosses above EMA
            if k_val < self.stoch_oversold or price > ema_val:
                self.position.close()
                return

        # Entry conditions
        # LONG: K crosses above D from oversold + price > EMA200 + recent squeeze
        if k_cross_up and was_oversold and price > ema_val and recent_squeeze:
            if not self.position.is_long:
                self.buy()

        # SHORT: K crosses below D from overbought + price < EMA200 + recent squeeze
        elif k_cross_down and was_overbought and price < ema_val and recent_squeeze:
            if not self.position.is_short:
                self.sell()


# ── Run ──────────────────────────────────────────────────────
bt = Backtest(
    data,
    StochRSIEmaSqueeze,
    cash=1_000_000,
    commission=0.001,
    exclusive_orders=True,
)

stats = bt.run()
print(stats)
print(f"\n_strategy_name: StochRSIEmaSqueeze")
