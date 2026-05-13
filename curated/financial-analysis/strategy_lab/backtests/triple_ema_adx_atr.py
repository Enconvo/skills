"""
Triple EMA + ADX + ATR Trailing Stop Strategy
==============================================
Triple EMA (8/21/55) trend system with ADX strength filter and ATR trailing stop.

LONG: EMA8 > EMA21 > EMA55 (bullish alignment) AND ADX > 25
SHORT: EMA8 < EMA21 < EMA55 (bearish alignment) AND ADX > 25
EXIT: ATR-based trailing stop (3x ATR) OR ADX drops below 20

STATS:
---
Start                     2024-02-12 05:00:00+00:00
End                       2026-02-11 05:00:00+00:00
Duration                    730 days 00:00:00
Exposure Time [%]                    54.28555
Equity Final [$]                 445516.25332
Equity Peak [$]                 1179941.80392
Return [%]                          -55.44837
Buy & Hold Return [%]                30.80311
Return (Ann.) [%]                   -33.21607
Volatility (Ann.) [%]                24.55222
Sharpe Ratio                         -1.35287
Sortino Ratio                        -1.35722
Calmar Ratio                         -0.48336
Max. Drawdown [%]                   -68.71961
Avg. Drawdown [%]                    -5.90312
# Trades                                  382
Win Rate [%]                         34.81675
Best Trade [%]                       16.44894
Worst Trade [%]                      -6.55909
Avg. Trade [%]                       -0.23562
Profit Factor                         0.79084
Expectancy [%]                       -0.20362
SQN                                  -1.63996
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
class TripleEmaAdxAtr(Strategy):
    # Parameters
    ema_fast = 8
    ema_mid = 21
    ema_slow = 55
    adx_period = 14
    adx_entry = 25
    adx_exit = 20
    atr_period = 14
    atr_mult = 3.0

    def init(self):
        self.ema8 = self.I(talib.EMA, self.data.Close, timeperiod=self.ema_fast)
        self.ema21 = self.I(talib.EMA, self.data.Close, timeperiod=self.ema_mid)
        self.ema55 = self.I(talib.EMA, self.data.Close, timeperiod=self.ema_slow)
        self.adx = self.I(talib.ADX, self.data.High, self.data.Low, self.data.Close, timeperiod=self.adx_period)
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=self.atr_period)
        self.trailing_stop = 0.0

    def next(self):
        price = self.data.Close[-1]
        ema8 = self.ema8[-1]
        ema21 = self.ema21[-1]
        ema55 = self.ema55[-1]
        adx = self.adx[-1]
        atr = self.atr[-1]

        # Skip if indicators not ready
        if np.isnan(adx) or np.isnan(atr) or np.isnan(ema55):
            return

        bullish_aligned = ema8 > ema21 > ema55
        bearish_aligned = ema8 < ema21 < ema55
        strong_trend = adx > self.adx_entry
        weak_trend = adx < self.adx_exit

        # Manage existing position
        if self.position.is_long:
            # Update trailing stop: move up only
            new_stop = price - self.atr_mult * atr
            if new_stop > self.trailing_stop:
                self.trailing_stop = new_stop
            # Exit conditions
            if price <= self.trailing_stop or weak_trend:
                self.position.close()
                self.trailing_stop = 0.0
                return

        elif self.position.is_short:
            # Update trailing stop: move down only
            new_stop = price + self.atr_mult * atr
            if self.trailing_stop == 0.0 or new_stop < self.trailing_stop:
                self.trailing_stop = new_stop
            # Exit conditions
            if price >= self.trailing_stop or weak_trend:
                self.position.close()
                self.trailing_stop = 0.0
                return

        # Entry signals (only when flat)
        if not self.position:
            if bullish_aligned and strong_trend:
                self.buy()
                self.trailing_stop = price - self.atr_mult * atr
            elif bearish_aligned and strong_trend:
                self.sell()
                self.trailing_stop = price + self.atr_mult * atr


# ── Run ──────────────────────────────────────────────────────
bt = Backtest(
    data,
    TripleEmaAdxAtr,
    cash=1_000_000,
    commission=0.001,
    exclusive_orders=True,
)

stats = bt.run()
print(stats)
print(f"\n_strategy_name: TripleEmaAdxAtr")
