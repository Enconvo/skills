#!/usr/bin/env python3
"""
Round 1 Strategy 02: RSI Mean Reversion
Buy when RSI < 30 (oversold), sell when RSI > 70 (overbought).
"""
from backtesting import Strategy
import talib
import sys
sys.path.append("..")
from utils import load_meta_data

def rsi_ind(data, period=14):
    return talib.RSI(data, timeperiod=period)

class RSIMeanReversion(Strategy):
    rsi_period = 14
    rsi_lower = 30
    rsi_upper = 70

    def init(self):
        self.rsi = self.I(rsi_ind, self.data.Close, self.rsi_period)

    def next(self):
        if self.rsi[-1] < self.rsi_lower and not self.position:
            self.buy()
        elif self.rsi[-1] > self.rsi_upper and self.position:
            self.position.close()

if __name__ == "__main__":
    from backtesting import Backtest
    data = load_meta_data("1h")
    bt = Backtest(data, RSIMeanReversion, cash=100_000, commission=.002)
    stats = bt.run()
    print(stats)
