"""
ROUND 1 — Strategy 05: Donchian Channel Breakout (Turtle Trading)
=================================================================
Buy when price breaks above 20-period high. Sell when price breaks below 10-period low.
Classic trend-following breakout system.
"""
import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_nvda_data

data = load_nvda_data("1h")


def calc_highest(high, period):
    return talib.MAX(high, timeperiod=period)

def calc_lowest(low, period):
    return talib.MIN(low, timeperiod=period)


class DonchianBreakout(Strategy):
    entry_period = 20
    exit_period = 10

    def init(self):
        self.entry_high = self.I(calc_highest, self.data.High, self.entry_period)
        self.exit_low = self.I(calc_lowest, self.data.Low, self.exit_period)

    def next(self):
        price = self.data.Close[-1]
        if not self.position:
            if price > self.entry_high[-2]:  # Break above previous bar's high channel
                self.buy()
        else:
            if price < self.exit_low[-2]:  # Break below previous bar's low channel
                self.position.close()


bt = Backtest(data, DonchianBreakout, cash=1_000_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(stats)
print(f"\n_strategy_name: r1_05_donchian_breakout")
