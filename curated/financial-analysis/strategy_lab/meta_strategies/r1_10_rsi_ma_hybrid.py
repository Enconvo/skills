#!/usr/bin/env python3
"""
Round 1 Strategy 10: RSI + MA Hybrid
Buy when RSI < 40 AND price > MA50 (dip in uptrend).
"""
from backtesting import Strategy
import talib
import sys
sys.path.append("..")
from utils import load_meta_data

def rsi_ind(data, period=14):
    return talib.RSI(data, timeperiod=period)

def sma(data, period):
    return talib.SMA(data, timeperiod=period)

class RSIMAHybrid(Strategy):
    rsi_period = 14
    rsi_buy = 40
    rsi_sell = 70
    ma_period = 50

    def init(self):
        self.rsi = self.I(rsi_ind, self.data.Close, self.rsi_period)
        self.ma = self.I(sma, self.data.Close, self.ma_period)

    def next(self):
        if self.rsi[-1] < self.rsi_buy and self.data.Close[-1] > self.ma[-1] and not self.position:
            self.buy()
        elif self.rsi[-1] > self.rsi_sell and self.position:
            self.position.close()

if __name__ == "__main__":
    from backtesting import Backtest
    data = load_meta_data("1h")
    bt = Backtest(data, RSIMAHybrid, cash=100_000, commission=.002)
    stats = bt.run()
    print(stats)
