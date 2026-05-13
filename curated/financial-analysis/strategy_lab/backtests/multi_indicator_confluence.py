"""
Multi-Indicator Confluence Scoring System
==========================================
"Kitchen sink" done RIGHT -- only trade when overwhelming evidence agrees.

Confluence score (-5 to +5) from:
  1. EMA alignment: EMA(8) > EMA(21) > EMA(55) = +1, reverse = -1
  2. RSI(14): +1 if healthy bullish momentum, -1 if bearish
  3. MACD(12,26,9): +1 if MACD > signal AND histogram positive, -1 opposite
  4. ADX(14): +1 if ADX > 25 (amplifies direction), 0 if below
  5. Volume: +1 if volume > 1.2x SMA(20) volume (amplifies direction)

LONG: Score >= 4   SHORT: Score <= -4
EXIT: Score drops to 0 or flips sign
Stop loss: 2x ATR(14)

STATS:
---
Start                     2024-02-12 05:00:00+00:00
End                       2026-02-11 05:00:00+00:00
Duration                    730 days 00:00:00
Exposure Time [%]                     40.7113
Equity Final [$]                 289340.00616
Equity Peak [$]                   1120608.508
Return [%]                            -71.066
Buy & Hold Return [%]                30.80311
Sharpe Ratio                         -2.86048
Sortino Ratio                        -2.34987
Max. Drawdown [%]                   -76.52181
# Trades                                  720
Win Rate [%]                            28.75
Best Trade [%]                       13.10277
Worst Trade [%]                      -4.45033
Avg. Trade [%]                       -0.18987
Profit Factor                         0.72387
Expectancy [%]                       -0.17757
SQN                                  -2.81176
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

# -- Data ---------------------------------------------------------
data = load_btc_data()


# -- Helper functions outside class --------------------------------
def compute_volume_sma(volume, period=20):
    return talib.SMA(np.asarray(volume, dtype=np.float64), timeperiod=period)


# -- Strategy ------------------------------------------------------
class MultiIndicatorConfluence(Strategy):
    ema_fast = 8
    ema_mid = 21
    ema_slow = 55
    rsi_period = 14
    macd_fast = 12
    macd_slow = 26
    macd_signal = 9
    adx_period = 14
    adx_threshold = 25
    atr_period = 14
    atr_sl_mult = 2.0
    vol_sma_period = 20
    vol_mult = 1.2
    entry_threshold = 4

    def init(self):
        self.ema8 = self.I(talib.EMA, self.data.Close, timeperiod=self.ema_fast)
        self.ema21 = self.I(talib.EMA, self.data.Close, timeperiod=self.ema_mid)
        self.ema55 = self.I(talib.EMA, self.data.Close, timeperiod=self.ema_slow)
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=self.rsi_period)
        self.macd_line, self.macd_signal_line, self.macd_hist = self.I(
            talib.MACD, self.data.Close,
            fastperiod=self.macd_fast,
            slowperiod=self.macd_slow,
            signalperiod=self.macd_signal,
        )
        self.adx = self.I(talib.ADX, self.data.High, self.data.Low, self.data.Close,
                          timeperiod=self.adx_period)
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close,
                          timeperiod=self.atr_period)
        self.vol_sma = self.I(compute_volume_sma, self.data.Volume, self.vol_sma_period)

    def _confluence_score(self):
        """Calculate confluence score from -5 to +5."""
        ema8 = self.ema8[-1]
        ema21 = self.ema21[-1]
        ema55 = self.ema55[-1]
        rsi = self.rsi[-1]
        rsi_prev = self.rsi[-2]
        macd = self.macd_line[-1]
        signal = self.macd_signal_line[-1]
        hist = self.macd_hist[-1]
        adx = self.adx[-1]
        vol = self.data.Volume[-1]
        vol_sma = self.vol_sma[-1]

        # Directional components (each contributes +1 or -1)
        # 1. EMA Alignment
        ema_score = 0
        if ema8 > ema21 > ema55:
            ema_score = 1
        elif ema8 < ema21 < ema55:
            ema_score = -1

        # 2. RSI momentum direction
        rsi_score = 0
        if rsi > rsi_prev and rsi > 40:
            rsi_score = 1   # rising with bullish room
        elif rsi < rsi_prev and rsi < 60:
            rsi_score = -1  # falling with bearish room

        # 3. MACD
        macd_score = 0
        if macd > signal and hist > 0:
            macd_score = 1
        elif macd < signal and hist < 0:
            macd_score = -1

        # Compute directional bias from the 3 directional indicators
        directional_sum = ema_score + rsi_score + macd_score
        direction = 1 if directional_sum > 0 else (-1 if directional_sum < 0 else 0)

        # 4. ADX amplifier -- adds in the direction of existing bias
        adx_score = 0
        if adx > self.adx_threshold and direction != 0:
            adx_score = direction  # amplifies existing direction

        # 5. Volume amplifier -- adds in the direction of existing bias
        vol_score = 0
        if not np.isnan(vol_sma) and vol_sma > 0 and vol > self.vol_mult * vol_sma and direction != 0:
            vol_score = direction  # amplifies existing direction

        return ema_score + rsi_score + macd_score + adx_score + vol_score

    def next(self):
        price = self.data.Close[-1]
        atr = self.atr[-1]

        # Skip if indicators not ready
        if np.isnan(self.ema55[-1]) or np.isnan(self.adx[-1]) or np.isnan(self.atr[-1]):
            return
        if np.isnan(self.rsi[-2]) or np.isnan(self.macd_hist[-1]):
            return
        if np.isnan(self.vol_sma[-1]):
            return

        score = self._confluence_score()

        # Manage existing positions
        if self.position.is_long:
            if score <= 0:
                self.position.close()
                return

        elif self.position.is_short:
            if score >= 0:
                self.position.close()
                return

        # Entry signals (only when flat)
        if not self.position:
            sl_distance = self.atr_sl_mult * atr
            if score >= self.entry_threshold:
                self.buy(sl=price - sl_distance)
            elif score <= -self.entry_threshold:
                self.sell(sl=price + sl_distance)


# -- Run ----------------------------------------------------------
bt = Backtest(
    data,
    MultiIndicatorConfluence,
    cash=1_000_000,
    commission=0.001,
    exclusive_orders=True,
)

stats = bt.run()
print(stats)
print(f"\n_strategy_name: MultiIndicatorConfluence")
