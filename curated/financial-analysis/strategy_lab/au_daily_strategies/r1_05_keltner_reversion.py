"""R1-05: Keltner Channel Mean Reversion — Buy at lower KC, sell at upper."""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_au_data
import numpy as np, talib
from backtesting import Backtest, Strategy

data = load_au_data("daily")

def calc_kc_mid(close, period):
    return talib.EMA(close, timeperiod=period)

def calc_atr(high, low, close, period):
    return talib.ATR(high, low, close, timeperiod=period)

class KeltnerReversion(Strategy):
    kc_period = 20
    kc_mult = 2.0

    def init(self):
        self.kc_mid = self.I(calc_kc_mid, self.data.Close, self.kc_period)
        self.atr = self.I(calc_atr, self.data.High, self.data.Low, self.data.Close, self.kc_period)

    def next(self):
        if np.isnan(self.atr[-1]):
            return
        kc_lower = self.kc_mid[-1] - self.kc_mult * self.atr[-1]
        kc_upper = self.kc_mid[-1] + self.kc_mult * self.atr[-1]

        if not self.position:
            if self.data.Close[-1] <= kc_lower:
                self.buy()
        else:
            if self.data.Close[-1] >= kc_upper:
                self.position.close()

bt = Backtest(data, KeltnerReversion, cash=100_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(f"R1-05 Keltner Reversion | Return: {stats['Return [%]']:.1f}% | Sharpe: {stats['Sharpe Ratio']:.2f} | Sortino: {stats['Sortino Ratio']:.2f} | MaxDD: {stats['Max. Drawdown [%]']:.1f}% | WinRate: {stats['Win Rate [%]']:.1f}% | Trades: {stats['# Trades']} | SQN: {stats['SQN']:.2f}")
