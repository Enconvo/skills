"""
Ichimoku Cloud Strategy
=======================
Full Ichimoku Kinko Hyo system (9/26/52 periods).

Tenkan-sen = (highest_high(9) + lowest_low(9)) / 2
Kijun-sen = (highest_high(26) + lowest_low(26)) / 2
Senkou Span A = (Tenkan + Kijun) / 2
Senkou Span B = (highest_high(52) + lowest_low(52)) / 2

LONG: Tenkan crosses above Kijun AND price above cloud
SHORT: Tenkan crosses below Kijun AND price below cloud
EXIT: TK cross reversal OR price enters cloud

STATS:
---
Start                     2024-02-12 05:00:00+00:00
End                       2026-02-11 05:00:00+00:00
Duration                    730 days 00:00:00
Exposure Time [%]                     27.7889
Equity Final [$]                 668397.54464
Equity Peak [$]                 1006490.58429
Return [%]                          -33.16025
Buy & Hold Return [%]                33.12595
Return (Ann.) [%]                   -18.22188
Volatility (Ann.) [%]                19.55368
Sharpe Ratio                         -0.93189
Sortino Ratio                        -1.21568
Calmar Ratio                         -0.43587
Max. Drawdown [%]                   -41.80618
Avg. Drawdown [%]                   -14.38813
# Trades                                  331
Win Rate [%]                         28.70091
Best Trade [%]                       11.49435
Worst Trade [%]                     -17.80383
Avg. Trade [%]                       -0.13439
Profit Factor                         0.81501
Expectancy [%]                       -0.11596
SQN                                  -1.26905
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


# ── Ichimoku Calculation Functions (standalone) ──────────────
def calc_tenkan(high, low, period=9):
    """Tenkan-sen: (highest_high + lowest_low) / 2 over period."""
    hh = talib.MAX(high, timeperiod=period)
    ll = talib.MIN(low, timeperiod=period)
    return (hh + ll) / 2.0


def calc_kijun(high, low, period=26):
    """Kijun-sen: (highest_high + lowest_low) / 2 over period."""
    hh = talib.MAX(high, timeperiod=period)
    ll = talib.MIN(low, timeperiod=period)
    return (hh + ll) / 2.0


def calc_senkou_a(high, low, tenkan_period=9, kijun_period=26):
    """Senkou Span A: (Tenkan + Kijun) / 2."""
    tenkan = calc_tenkan(high, low, tenkan_period)
    kijun = calc_kijun(high, low, kijun_period)
    return (tenkan + kijun) / 2.0


def calc_senkou_b(high, low, period=52):
    """Senkou Span B: (highest_high(52) + lowest_low(52)) / 2."""
    hh = talib.MAX(high, timeperiod=period)
    ll = talib.MIN(low, timeperiod=period)
    return (hh + ll) / 2.0


# ── Strategy ─────────────────────────────────────────────────
class IchimokuCloud(Strategy):
    tenkan_period = 9
    kijun_period = 26
    senkou_b_period = 52

    def init(self):
        self.tenkan = self.I(calc_tenkan, self.data.High, self.data.Low, self.tenkan_period)
        self.kijun = self.I(calc_kijun, self.data.High, self.data.Low, self.kijun_period)
        self.span_a = self.I(calc_senkou_a, self.data.High, self.data.Low, self.tenkan_period, self.kijun_period)
        self.span_b = self.I(calc_senkou_b, self.data.High, self.data.Low, self.senkou_b_period)

    def next(self):
        price = self.data.Close[-1]
        tenkan = self.tenkan[-1]
        kijun = self.kijun[-1]
        span_a = self.span_a[-1]
        span_b = self.span_b[-1]

        # Skip if indicators not ready
        if np.isnan(tenkan) or np.isnan(kijun) or np.isnan(span_a) or np.isnan(span_b):
            return

        cloud_top = max(span_a, span_b)
        cloud_bottom = min(span_a, span_b)

        above_cloud = price > cloud_top
        below_cloud = price < cloud_bottom
        in_cloud = cloud_bottom <= price <= cloud_top

        tk_cross_up = crossover(self.tenkan, self.kijun)
        tk_cross_down = crossover(self.kijun, self.tenkan)

        # Exit conditions
        if self.position.is_long:
            if tk_cross_down or in_cloud:
                self.position.close()
                return

        elif self.position.is_short:
            if tk_cross_up or in_cloud:
                self.position.close()
                return

        # Entry signals (only when flat)
        if not self.position:
            if tk_cross_up and above_cloud:
                self.buy()
            elif tk_cross_down and below_cloud:
                self.sell()


# ── Run ──────────────────────────────────────────────────────
bt = Backtest(
    data,
    IchimokuCloud,
    cash=1_000_000,
    commission=0.001,
    exclusive_orders=True,
)

stats = bt.run()
print(stats)
print(f"\n_strategy_name: IchimokuCloud")
