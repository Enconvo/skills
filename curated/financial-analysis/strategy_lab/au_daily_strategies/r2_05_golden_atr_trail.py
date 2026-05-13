"""R2-05: Golden Cross + ATR Trailing Stop — Protect profits better than death cross exit."""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_au_data
import numpy as np, talib
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

data = load_au_data("daily")

def calc_sma(close, period):
    return talib.SMA(close, timeperiod=period)

def calc_atr(high, low, close, period):
    return talib.ATR(high, low, close, timeperiod=period)

class GoldenATRTrail(Strategy):
    fast = 50
    slow = 200
    atr_period = 14
    atr_mult = 3.0

    def init(self):
        self.sma_fast = self.I(calc_sma, self.data.Close, self.fast)
        self.sma_slow = self.I(calc_sma, self.data.Close, self.slow)
        self.atr = self.I(calc_atr, self.data.High, self.data.Low, self.data.Close, self.atr_period)
        self.highest = 0
        self.trail_stop = 0

    def next(self):
        price = self.data.Close[-1]
        atr_val = self.atr[-1]
        if np.isnan(self.sma_slow[-1]) or np.isnan(atr_val):
            return
        if not self.position:
            if crossover(self.sma_fast, self.sma_slow):
                self.buy()
                self.highest = price
                self.trail_stop = price - self.atr_mult * atr_val
        else:
            if price > self.highest:
                self.highest = price
            new_stop = self.highest - self.atr_mult * atr_val
            if new_stop > self.trail_stop:
                self.trail_stop = new_stop
            if price < self.trail_stop:
                self.position.close()
                self.highest = 0
                self.trail_stop = 0

bt = Backtest(data, GoldenATRTrail, cash=100_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(f"R2-05 Golden+ATR Trail | Return: {stats['Return [%]']:.1f}% | Sharpe: {stats['Sharpe Ratio']:.2f} | Sortino: {stats['Sortino Ratio']:.2f} | MaxDD: {stats['Max. Drawdown [%]']:.1f}% | WinRate: {stats['Win Rate [%]']:.1f}% | Trades: {stats['# Trades']} | SQN: {stats['SQN']:.2f}")
