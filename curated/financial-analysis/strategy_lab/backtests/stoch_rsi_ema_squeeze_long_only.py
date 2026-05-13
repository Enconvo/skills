"""
BACKTEST: StochRSI + EMA + BB Squeeze — LONG ONLY
===================================================
StochRSI crossover from oversold + EMA200 trend filter + BB squeeze detection.
Only takes long positions — catches bullish breakouts after consolidation.

STATS:
---
Start                     2024-02-12 05:00:00+00:00
End                       2026-02-11 05:00:00+00:00
Duration                    730 days 00:00:00
Exposure Time [%]                    19.88679
Equity Final [$]                 735446.09538
Equity Peak [$]                 1101272.87078
Return [%]                          -26.45539
Buy & Hold Return [%]                29.28591
Return (Ann.) [%]                   -14.22382
Volatility (Ann.) [%]                  14.193
Sharpe Ratio                         -1.00217
Sortino Ratio                        -1.16903
Calmar Ratio                         -0.41455
Max. Drawdown [%]                   -34.31165
Avg. Drawdown [%]                    -5.00681
# Trades                                  257
Win Rate [%]                         48.63813
Best Trade [%]                        6.18539
Worst Trade [%]                      -4.58289
Avg. Trade [%]                       -0.12614
Max. Trade Duration           2 days 11:00:00
Avg. Trade Duration           0 days 13:00:00
Profit Factor                         0.80175
Expectancy [%]                       -0.11508
SQN                                  -1.20008
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
    return talib.EMA(close, timeperiod=200)


# ── Strategy ─────────────────────────────────────────────────
class StochRSIEmaSqueezelLongOnly(Strategy):
    rsi_period = 14
    stoch_period = 14
    k_smooth = 3
    d_smooth = 3
    stoch_oversold = 20
    stoch_overbought = 80
    ema_period = 200
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

        if np.isnan(k_val) or np.isnan(d_val) or np.isnan(ema_val):
            return

        # Check for recent BB squeeze
        recent_squeeze = False
        lookback = min(self.squeeze_lookback, len(self.bbw) - 1)
        for i in range(1, lookback + 1):
            if not np.isnan(self.bbw[-i]) and self.bbw[-i] < self.squeeze_threshold:
                recent_squeeze = True
                break

        # K crosses above D (bullish)
        k_cross_up = (self.stoch_k[-1] > self.stoch_d[-1] and
                      self.stoch_k[-2] <= self.stoch_d[-2])

        # Was recently oversold
        was_oversold = any(
            not np.isnan(self.stoch_k[-i]) and self.stoch_k[-i] < self.stoch_oversold
            for i in range(1, 4)
        )

        # EXIT: StochRSI overbought or price drops below EMA
        if self.position.is_long:
            if k_val > self.stoch_overbought or price < ema_val:
                self.position.close()
                return

        # LONG ENTRY: K crosses above D from oversold + price > EMA200 + recent squeeze
        if k_cross_up and was_oversold and price > ema_val and recent_squeeze:
            if not self.position.is_long:
                self.buy()


# ── Run ──────────────────────────────────────────────────────
bt = Backtest(
    data,
    StochRSIEmaSqueezelLongOnly,
    cash=1_000_000,
    commission=0.001,
    exclusive_orders=True,
)

stats = bt.run()
print(stats)
print(f"\n_strategy_name: StochRSIEmaSqueezelLongOnly")
