"""
ROUND 1 — Strategy 02: RSI Mean Reversion
==========================================
Buy when RSI drops below 30 (oversold). Sell when RSI rises above 70 (overbought).
Simple but effective on many tickers.
"""
import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_nvda_data

data = load_nvda_data("1h")


def calc_rsi(close, period):
    return talib.RSI(close, timeperiod=period)


class RSIMeanReversion(Strategy):
    rsi_period = 14
    rsi_oversold = 30
    rsi_overbought = 70

    def init(self):
        self.rsi = self.I(calc_rsi, self.data.Close, self.rsi_period)

    def next(self):
        if not self.position:
            if self.rsi[-1] < self.rsi_oversold:
                self.buy()
        else:
            if self.rsi[-1] > self.rsi_overbought:
                self.position.close()


bt = Backtest(data, RSIMeanReversion, cash=1_000_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r1_02_rsi_mean_reversion")
