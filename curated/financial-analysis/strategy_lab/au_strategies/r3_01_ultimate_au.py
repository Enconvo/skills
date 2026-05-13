"""
ROUND 3 — Strategy 01: Ultimate AU Strategy
============================================
FINAL EVOLUTION: Combines the 3 best elements discovered:
1. RSI oversold entry (from R1-02, R2-05) — best signal for AU
2. ATR trailing stop (from R2-05) — lets winners run, Sortino 4.82
3. ADX trend filter (from R2-08) — only trade in trending markets

Logic:
- ADX > 20: Market is trending (from adaptive switch learning)
- RSI < 30: Price is oversold in a trend (high probability bounce)
- ATR trailing stop at 2.5x ATR below highest close
- Emergency exit if ADX drops below 15 (trend dying)

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


def calc_rsi(close, period):
    return talib.RSI(close, timeperiod=period)

def calc_adx(high, low, close, period):
    return talib.ADX(high, low, close, timeperiod=period)

def calc_atr(high, low, close, period):
    return talib.ATR(high, low, close, timeperiod=period)

def calc_plus_di(high, low, close, period):
    return talib.PLUS_DI(high, low, close, timeperiod=period)

def calc_minus_di(high, low, close, period):
    return talib.MINUS_DI(high, low, close, timeperiod=period)


class UltimateAU(Strategy):
    rsi_period = 14
    rsi_entry = 30
    adx_period = 14
    adx_min = 20
    adx_exit = 15
    atr_period = 14
    atr_trail_mult = 2.5

    def init(self):
        self.rsi = self.I(calc_rsi, self.data.Close, self.rsi_period)
        self.adx = self.I(calc_adx, self.data.High, self.data.Low,
                          self.data.Close, self.adx_period)
        self.atr = self.I(calc_atr, self.data.High, self.data.Low,
                          self.data.Close, self.atr_period)
        self.plus_di = self.I(calc_plus_di, self.data.High, self.data.Low,
                              self.data.Close, self.adx_period)
        self.minus_di = self.I(calc_minus_di, self.data.High, self.data.Low,
                               self.data.Close, self.adx_period)
        self.highest = 0
        self.trail_stop = 0

    def next(self):
        price = self.data.Close[-1]
        atr_val = self.atr[-1]

        if np.isnan(atr_val) or np.isnan(self.adx[-1]):
            return

        if not self.position:
            # Entry: RSI oversold + trending market + bullish DI
            trending = self.adx[-1] > self.adx_min
            bullish = self.plus_di[-1] > self.minus_di[-1]
            oversold = self.rsi[-1] < self.rsi_entry

            if trending and bullish and oversold:
                self.buy()
                self.highest = price
                self.trail_stop = price - self.atr_trail_mult * atr_val
        else:
            # Update trailing stop
            if price > self.highest:
                self.highest = price
            new_stop = self.highest - self.atr_trail_mult * atr_val
            if new_stop > self.trail_stop:
                self.trail_stop = new_stop

            # Exit: trail stop hit OR trend completely dead
            if price < self.trail_stop or self.adx[-1] < self.adx_exit:
                self.position.close()
                self.highest = 0
                self.trail_stop = 0


bt = Backtest(data, UltimateAU, cash=100_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r3_01_ultimate_au")
