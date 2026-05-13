"""
ROUND 1 — Strategy 12: Williams %R + Volume Weighted Price
==========================================================
Buy when Williams %R < -80 (oversold) AND price is below VWAP (undervalued).
Sell when Williams %R > -20 (overbought).
Combines momentum oscillator with volume-price relationship.

STATS:
---
[pending]
---
"""
import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_au_data

data = load_au_data("1h")


def calc_willr(high, low, close, period):
    return talib.WILLR(high, low, close, timeperiod=period)

def calc_vwap_proxy(high, low, close, volume):
    """Rolling VWAP approximation using cumulative typical price * volume."""
    tp = (high + low + close) / 3
    cum_tp_vol = np.nancumsum(tp * volume)
    cum_vol = np.nancumsum(volume)
    cum_vol[cum_vol == 0] = np.nan
    return cum_tp_vol / cum_vol


class WilliamsVWAP(Strategy):
    willr_period = 14

    def init(self):
        self.willr = self.I(calc_willr, self.data.High, self.data.Low,
                            self.data.Close, self.willr_period)
        self.vwap = self.I(calc_vwap_proxy, self.data.High, self.data.Low,
                           self.data.Close, self.data.Volume)

    def next(self):
        if (self.willr[-1] < -80 and
            self.data.Close[-1] < self.vwap[-1] and
            not self.position):
            self.buy()
        elif self.willr[-1] > -20 and self.position:
            self.position.close()


bt = Backtest(data, WilliamsVWAP, cash=100_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r1_12_williams_vwap")
