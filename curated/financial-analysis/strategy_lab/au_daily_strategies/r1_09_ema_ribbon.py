"""R1-09: EMA Ribbon (8/21/55) — Trend following with triple EMA."""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_au_data
import numpy as np, talib
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

data = load_au_data("daily")

def calc_ema(close, period):
    return talib.EMA(close, timeperiod=period)

class EMARibbon(Strategy):
    fast = 8
    mid = 21
    slow = 55

    def init(self):
        self.ema_fast = self.I(calc_ema, self.data.Close, self.fast)
        self.ema_mid = self.I(calc_ema, self.data.Close, self.mid)
        self.ema_slow = self.I(calc_ema, self.data.Close, self.slow)

    def next(self):
        if np.isnan(self.ema_slow[-1]):
            return
        bullish = self.ema_fast[-1] > self.ema_mid[-1] > self.ema_slow[-1]
        bearish = self.ema_fast[-1] < self.ema_mid[-1] < self.ema_slow[-1]

        if not self.position:
            if bullish and crossover(self.ema_fast, self.ema_mid):
                self.buy()
        else:
            if bearish or crossover(self.ema_mid, self.ema_fast):
                self.position.close()

bt = Backtest(data, EMARibbon, cash=100_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(f"R1-09 EMA Ribbon | Return: {stats['Return [%]']:.1f}% | Sharpe: {stats['Sharpe Ratio']:.2f} | Sortino: {stats['Sortino Ratio']:.2f} | MaxDD: {stats['Max. Drawdown [%]']:.1f}% | WinRate: {stats['Win Rate [%]']:.1f}% | Trades: {stats['# Trades']} | SQN: {stats['SQN']:.2f}")
