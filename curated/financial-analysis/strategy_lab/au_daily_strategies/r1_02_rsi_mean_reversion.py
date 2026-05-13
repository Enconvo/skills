"""R1-02: RSI Mean Reversion — Buy oversold, sell overbought."""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_au_data
import numpy as np, talib
from backtesting import Backtest, Strategy

data = load_au_data("daily")

def calc_rsi(close, period):
    return talib.RSI(close, timeperiod=period)

class RSIMeanReversion(Strategy):
    rsi_period = 14
    rsi_entry = 30
    rsi_exit = 70

    def init(self):
        self.rsi = self.I(calc_rsi, self.data.Close, self.rsi_period)

    def next(self):
        if np.isnan(self.rsi[-1]):
            return
        if not self.position:
            if self.rsi[-1] < self.rsi_entry:
                self.buy()
        else:
            if self.rsi[-1] > self.rsi_exit:
                self.position.close()

bt = Backtest(data, RSIMeanReversion, cash=100_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(f"R1-02 RSI Mean Reversion | Return: {stats['Return [%]']:.1f}% | Sharpe: {stats['Sharpe Ratio']:.2f} | Sortino: {stats['Sortino Ratio']:.2f} | MaxDD: {stats['Max. Drawdown [%]']:.1f}% | WinRate: {stats['Win Rate [%]']:.1f}% | Trades: {stats['# Trades']} | SQN: {stats['SQN']:.2f}")
