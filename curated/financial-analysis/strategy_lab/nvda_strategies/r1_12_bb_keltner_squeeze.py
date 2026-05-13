"""
ROUND 1 — Strategy 12: Bollinger + Keltner Squeeze Breakout
============================================================
When Bollinger Bands squeeze inside Keltner Channels, volatility is compressed.
Buy when squeeze releases and momentum is positive (MACD histogram > 0).
Sell when momentum flips negative.
"""
import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_nvda_data

data = load_nvda_data("1h")


def calc_squeeze(high, low, close):
    """Returns 1 when squeeze fires bullish, -1 bearish, 0 no squeeze."""
    bb_upper, bb_mid, bb_lower = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2)
    kc_mid = talib.EMA(close, timeperiod=20)
    kc_atr = talib.ATR(high, low, close, timeperiod=20)
    kc_upper = kc_mid + 1.5 * kc_atr
    kc_lower = kc_mid - 1.5 * kc_atr

    # Squeeze = BB inside KC
    squeeze_on = (bb_lower > kc_lower) & (bb_upper < kc_upper)

    # Momentum = linear regression of (close - avg(highest high, lowest low, close)) over 20 bars
    # Simplified: use MACD histogram as momentum proxy
    macd, signal, hist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)

    result = np.zeros_like(close)
    for i in range(1, len(close)):
        if squeeze_on[i-1] and not squeeze_on[i]:  # Squeeze just released
            if hist[i] > 0:
                result[i] = 1
            elif hist[i] < 0:
                result[i] = -1
    return result

def calc_macd_hist(close):
    macd, signal, hist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
    return hist


class SqueezeBreakout(Strategy):
    def init(self):
        self.squeeze = self.I(calc_squeeze, self.data.High, self.data.Low, self.data.Close)
        self.hist = self.I(calc_macd_hist, self.data.Close)

    def next(self):
        if not self.position:
            if self.squeeze[-1] == 1:
                self.buy()
        else:
            if self.hist[-1] < 0:
                self.position.close()


bt = Backtest(data, SqueezeBreakout, cash=1_000_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r1_12_bb_keltner_squeeze")
