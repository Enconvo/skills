"""R1-01: Golden Cross (SMA 50/200) — Classic trend following."""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_au_data
import numpy as np, talib
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

data = load_au_data("daily")

def calc_sma(close, period):
    return talib.SMA(close, timeperiod=period)

class GoldenCross(Strategy):
    fast = 50
    slow = 200

    def init(self):
        self.sma_fast = self.I(calc_sma, self.data.Close, self.fast)
        self.sma_slow = self.I(calc_sma, self.data.Close, self.slow)

    def next(self):
        if not self.position:
            if crossover(self.sma_fast, self.sma_slow):
                self.buy()
        else:
            if crossover(self.sma_slow, self.sma_fast):
                self.position.close()

bt = Backtest(data, GoldenCross, cash=100_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(f"R1-01 Golden Cross | Return: {stats['Return [%]']:.1f}% | Sharpe: {stats['Sharpe Ratio']:.2f} | Sortino: {stats['Sortino Ratio']:.2f} | MaxDD: {stats['Max. Drawdown [%]']:.1f}% | WinRate: {stats['Win Rate [%]']:.1f}% | Trades: {stats['# Trades']} | SQN: {stats['SQN']:.2f}")
