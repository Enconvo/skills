"""
Williams %R + CCI Double-Oscillator Mean Reversion System
==========================================================
Dual-oscillator approach using Williams %R and CCI to identify
high-probability reversal zones. Both must agree on oversold/overbought
to filter single-indicator noise. EMA(50) provides trend context —
only buy dips in uptrends, sell rips in downtrends.

STATS:
---
Start                     2024-02-12 05:00:00+00:00
End                       2026-02-11 05:00:00+00:00
Duration                    730 days 00:00:00
Exposure Time [%]                    14.80931
Equity Final [$]                 400195.74775
Equity Peak [$]                  1044807.3475
Return [%]                          -59.98043
Buy & Hold Return [%]                35.86069
Return (Ann.) [%]                   -36.69933
Volatility (Ann.) [%]                10.52594
Sharpe Ratio                         -3.48656
Sortino Ratio                        -2.73482
Calmar Ratio                         -0.59274
Max. Drawdown [%]                    -61.9148
Avg. Drawdown [%]                    -7.35081
# Trades                                  452
Win Rate [%]                         40.04425
Best Trade [%]                        4.30442
Worst Trade [%]                      -5.37743
Avg. Trade [%]                       -0.21954
Profit Factor                         0.60745
Expectancy [%]                       -0.21305
SQN                                  -3.61751
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


# ── Helper: constant line for crossover/crossunder ───────────
def const_line(close, value=0.0):
    """Return a constant array the same length as close, for use with crossover."""
    return np.full_like(close, value, dtype=float)


# ── Strategy ─────────────────────────────────────────────────
class WilliamsRCCICombo(Strategy):
    willr_period = 14
    cci_period = 20
    ema_period = 50
    willr_oversold = -80
    willr_overbought = -20
    cci_oversold = -100
    cci_overbought = 100

    def init(self):
        self.willr = self.I(talib.WILLR, self.data.High, self.data.Low,
                            self.data.Close, timeperiod=self.willr_period)
        self.cci = self.I(talib.CCI, self.data.High, self.data.Low,
                          self.data.Close, timeperiod=self.cci_period)
        self.ema = self.I(talib.EMA, self.data.Close, timeperiod=self.ema_period)

        # Constant lines for crossover detection
        self.willr_os_line = self.I(const_line, self.data.Close,
                                     value=self.willr_oversold)
        self.willr_ob_line = self.I(const_line, self.data.Close,
                                     value=self.willr_overbought)
        self.cci_os_line = self.I(const_line, self.data.Close,
                                   value=self.cci_oversold)
        self.cci_ob_line = self.I(const_line, self.data.Close,
                                   value=self.cci_overbought)

    def next(self):
        price = self.data.Close[-1]
        willr_val = self.willr[-1]
        willr_prev = self.willr[-2] if len(self.willr) > 1 else np.nan
        cci_val = self.cci[-1]
        cci_prev = self.cci[-2] if len(self.cci) > 1 else np.nan
        ema_val = self.ema[-1]

        if np.isnan(willr_val) or np.isnan(cci_val) or np.isnan(ema_val) or np.isnan(willr_prev):
            return

        # Williams %R crosses above -80 (leaving oversold)
        willr_cross_up = willr_prev <= self.willr_oversold and willr_val > self.willr_oversold
        # Williams %R crosses below -20 (leaving overbought)
        willr_cross_down = willr_prev >= self.willr_overbought and willr_val < self.willr_overbought
        # CCI crosses above -100 (leaving oversold)
        cci_cross_up = cci_prev <= self.cci_oversold and cci_val > self.cci_oversold
        # CCI crosses below +100 (leaving overbought)
        cci_cross_down = cci_prev >= self.cci_overbought and cci_val < self.cci_overbought

        # For entries, we use a looser condition: both oscillators must be
        # recently leaving their extreme zones (within the last few bars)
        # but we require at least one to be crossing NOW
        willr_recently_oversold = willr_val > self.willr_oversold and willr_val < -50
        cci_recently_oversold = cci_val > self.cci_oversold and cci_val < 0
        willr_recently_overbought = willr_val < self.willr_overbought and willr_val > -50
        cci_recently_overbought = cci_val < self.cci_overbought and cci_val > 0

        # LONG: Both oscillators confirming oversold reversal + uptrend
        if not self.position:
            if price > ema_val:  # Uptrend — buy dips
                # At least one crossing now, other recently left oversold
                long_signal = (
                    (willr_cross_up and cci_recently_oversold) or
                    (cci_cross_up and willr_recently_oversold) or
                    (willr_cross_up and cci_cross_up)
                )
                if long_signal:
                    self.buy()

            elif price < ema_val:  # Downtrend — sell rips
                short_signal = (
                    (willr_cross_down and cci_recently_overbought) or
                    (cci_cross_down and willr_recently_overbought) or
                    (willr_cross_down and cci_cross_down)
                )
                if short_signal:
                    self.sell()

        # EXIT logic for open positions
        elif self.position.is_long:
            # Exit long: Williams %R hits overbought (-20) OR price crosses below EMA
            if willr_val >= self.willr_overbought or price < ema_val:
                self.position.close()

        elif self.position.is_short:
            # Exit short: Williams %R hits oversold (-80) OR price crosses above EMA
            if willr_val <= self.willr_oversold or price > ema_val:
                self.position.close()


# ── Run ──────────────────────────────────────────────────────
bt = Backtest(
    data,
    WilliamsRCCICombo,
    cash=1_000_000,
    commission=0.001,
    exclusive_orders=True,
)

stats = bt.run()
print(stats)
print(f"\n_strategy_name: WilliamsRCCICombo")
