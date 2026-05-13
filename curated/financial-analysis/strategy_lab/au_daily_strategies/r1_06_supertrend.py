"""R1-06: SuperTrend — Trend following with ATR-based dynamic support/resistance."""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_au_data
import numpy as np, talib
from backtesting import Backtest, Strategy

data = load_au_data("daily")

def calc_atr(high, low, close, period):
    return talib.ATR(high, low, close, timeperiod=period)

class SuperTrend(Strategy):
    atr_period = 10
    atr_mult = 3.0

    def init(self):
        self.atr = self.I(calc_atr, self.data.High, self.data.Low, self.data.Close, self.atr_period)
        self.direction = 1  # 1=bullish, -1=bearish
        self.upper_band = 0
        self.lower_band = 0

    def next(self):
        if np.isnan(self.atr[-1]):
            return
        hl2 = (self.data.High[-1] + self.data.Low[-1]) / 2
        new_upper = hl2 + self.atr_mult * self.atr[-1]
        new_lower = hl2 - self.atr_mult * self.atr[-1]

        if self.lower_band > 0:
            new_lower = max(new_lower, self.lower_band) if self.data.Close[-2] > self.lower_band else new_lower
        if self.upper_band > 0:
            new_upper = min(new_upper, self.upper_band) if self.data.Close[-2] < self.upper_band else new_upper

        self.upper_band = new_upper
        self.lower_band = new_lower

        prev_dir = self.direction
        if self.data.Close[-1] > self.upper_band:
            self.direction = 1
        elif self.data.Close[-1] < self.lower_band:
            self.direction = -1

        if not self.position:
            if self.direction == 1 and prev_dir == -1:
                self.buy()
        else:
            if self.direction == -1 and prev_dir == 1:
                self.position.close()

bt = Backtest(data, SuperTrend, cash=100_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(f"R1-06 SuperTrend | Return: {stats['Return [%]']:.1f}% | Sharpe: {stats['Sharpe Ratio']:.2f} | Sortino: {stats['Sortino Ratio']:.2f} | MaxDD: {stats['Max. Drawdown [%]']:.1f}% | WinRate: {stats['Win Rate [%]']:.1f}% | Trades: {stats['# Trades']} | SQN: {stats['SQN']:.2f}")
