#!/usr/bin/env python3
"""
Round 1 Strategy 03: MACD Crossover
Buy when MACD crosses above signal, sell when crosses below.
"""
from backtesting import Strategy
from backtesting.lib import crossover
import talib
import sys
sys.path.append("..")
from utils import load_meta_data

def macd_line(data):
    macd, signal, hist = talib.MACD(data, fastperiod=12, slowperiod=26, signalperiod=9)
    return macd

def macd_signal(data):
    macd, signal, hist = talib.MACD(data, fastperiod=12, slowperiod=26, signalperiod=9)
    return signal

class MACDCrossover(Strategy):
    def init(self):
        self.macd = self.I(macd_line, self.data.Close)
        self.signal = self.I(macd_signal, self.data.Close)

    def next(self):
        if crossover(self.macd, self.signal):
            self.buy()
        elif crossover(self.signal, self.macd):
            self.position.close()

if __name__ == "__main__":
    from backtesting import Backtest
    data = load_meta_data("1h")
    bt = Backtest(data, MACDCrossover, cash=100_000, commission=.002)
    stats = bt.run()
    print(stats)
