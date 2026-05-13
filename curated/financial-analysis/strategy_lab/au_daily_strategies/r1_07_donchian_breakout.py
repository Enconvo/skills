"""R1-07: Donchian Channel Breakout — Buy on 20-day high, sell on 10-day low."""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_au_data
import numpy as np, talib
from backtesting import Backtest, Strategy

data = load_au_data("daily")

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
        if np.isnan(self.entry_high[-2]) or np.isnan(self.exit_low[-2]):
            return
        if not self.position:
            if self.data.Close[-1] > self.entry_high[-2]:
                self.buy()
        else:
            if self.data.Close[-1] < self.exit_low[-2]:
                self.position.close()

bt = Backtest(data, DonchianBreakout, cash=100_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(f"R1-07 Donchian Breakout | Return: {stats['Return [%]']:.1f}% | Sharpe: {stats['Sharpe Ratio']:.2f} | Sortino: {stats['Sortino Ratio']:.2f} | MaxDD: {stats['Max. Drawdown [%]']:.1f}% | WinRate: {stats['Win Rate [%]']:.1f}% | Trades: {stats['# Trades']} | SQN: {stats['SQN']:.2f}")
