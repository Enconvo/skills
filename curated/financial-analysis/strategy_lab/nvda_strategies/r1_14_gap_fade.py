"""
ROUND 1 — Strategy 14: Gap Fade (Mean Reversion)
==================================================
Fade large gaps expecting mean reversion. When NVDA gaps up >2.5%, the move is
often over-extended — buy the gap-DOWN reversals, fade the gap-UPs.
Target: gap fill (price returns to previous close).
NVDA gap fill rate: ~59%, so this has statistical edge on gap-downs.
"""
import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_nvda_data

data = load_nvda_data("daily")


def calc_gap_pct(open_price, close_price):
    gap = np.full_like(open_price, np.nan)
    gap[1:] = (open_price[1:] - close_price[:-1]) / close_price[:-1] * 100
    return gap


def calc_rsi(close, period):
    return talib.RSI(close, timeperiod=period)


def calc_atr(high, low, close, period):
    return talib.ATR(high, low, close, timeperiod=period)


class GapFade(Strategy):
    gap_down_threshold = -2.0   # buy gap-downs bigger than this
    rsi_max = 45                # only buy if not already overbought
    atr_period = 14
    hold_days_max = 5           # max hold period (gap fill or bail)

    def init(self):
        self.gap = self.I(calc_gap_pct, self.data.Open, self.data.Close)
        self.rsi = self.I(calc_rsi, self.data.Close, 14)
        self.atr = self.I(calc_atr, self.data.High, self.data.Low, self.data.Close, self.atr_period)
        self.entry_bar = 0
        self.prev_close = 0

    def next(self):
        bar = len(self.data) - 1

        if not self.position:
            # Buy large gap-downs (expect mean reversion / gap fill)
            if (self.gap[-1] < self.gap_down_threshold and
                    self.rsi[-1] < self.rsi_max and
                    not np.isnan(self.atr[-1])):
                self.buy()
                self.entry_bar = bar
                self.prev_close = self.data.Close[-2] if len(self.data) > 1 else self.data.Close[-1]
        else:
            # Exit conditions:
            # 1. Gap filled: price reached previous close
            if self.data.High[-1] >= self.prev_close:
                self.position.close()
            # 2. Time stop: held too long
            elif (bar - self.entry_bar) >= self.hold_days_max:
                self.position.close()
            # 3. Emergency stop: dropped another ATR below entry
            elif self.data.Close[-1] < self.data.Close[self.entry_bar] - self.atr[-1] * 2:
                self.position.close()


bt = Backtest(data, GapFade, cash=1_000_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r1_14_gap_fade")
