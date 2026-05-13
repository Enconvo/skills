"""
ROUND 2 — Strategy 06: Mean Reversion + Trend Regime Switch
============================================================
EVOLUTION: ADX-based regime detection.
- Choppy (ADX < 25): RSI mean reversion (buy < 35, sell > 65)
- Trending (ADX > 25): MACD crossover with EMA filter
Adapts to NVDA's shifting between momentum runs and consolidation.
"""
import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_nvda_data

data = load_nvda_data("1h")


def calc_rsi(close, period):
    return talib.RSI(close, timeperiod=period)

def calc_adx(high, low, close, period):
    return talib.ADX(high, low, close, timeperiod=period)

_macd_cache = {}

def calc_macd(close):
    key = id(close)
    if key not in _macd_cache:
        _macd_cache[key] = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
    return _macd_cache[key][0]

def calc_macd_signal(close):
    key = id(close)
    if key not in _macd_cache:
        _macd_cache[key] = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
    return _macd_cache[key][1]

def calc_ema(close, period):
    return talib.EMA(close, timeperiod=period)

def calc_atr(high, low, close, period):
    return talib.ATR(high, low, close, timeperiod=period)


class RegimeSwitch(Strategy):
    adx_threshold = 25

    def init(self):
        self.rsi = self.I(calc_rsi, self.data.Close, 14)
        self.adx = self.I(calc_adx, self.data.High, self.data.Low, self.data.Close, 14)
        self.macd = self.I(calc_macd, self.data.Close)
        self.macd_sig = self.I(calc_macd_signal, self.data.Close)
        self.ema55 = self.I(calc_ema, self.data.Close, 55)
        self.atr = self.I(calc_atr, self.data.High, self.data.Low, self.data.Close, 14)
        self.highest = 0
        self.trail_stop = 0

    def next(self):
        price = self.data.Close[-1]
        atr_val = self.atr[-1]
        if np.isnan(atr_val) or np.isnan(self.adx[-1]):
            return

        trending = self.adx[-1] > self.adx_threshold

        if not self.position:
            if trending:
                # Trend mode: MACD cross + price above EMA 55
                if crossover(self.macd, self.macd_sig) and price > self.ema55[-1]:
                    self.buy()
                    self.highest = price
                    self.trail_stop = price - 2.0 * atr_val
            else:
                # Mean reversion mode: RSI oversold
                if self.rsi[-1] < 35:
                    self.buy()
                    self.highest = price
                    self.trail_stop = price - 2.0 * atr_val
        else:
            # Universal ATR trailing stop
            if price > self.highest:
                self.highest = price
            new_stop = self.highest - 2.0 * atr_val
            if new_stop > self.trail_stop:
                self.trail_stop = new_stop
            if price < self.trail_stop:
                self.position.close()
                self.highest = 0
                self.trail_stop = 0


bt = Backtest(data, RegimeSwitch, cash=1_000_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r2_06_mean_rev_regime_switch")
