"""R2-04: Keltner Channel + RSI Confirmation — Two mean reversion signals combined."""
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

def calc_rsi(close, period):
    return talib.RSI(close, timeperiod=period)

class KeltnerRSICombo(Strategy):
    kc_period = 20
    kc_mult = 2.0
    rsi_period = 14
    rsi_entry = 40

    def init(self):
        self.kc_mid = self.I(calc_kc_mid, self.data.Close, self.kc_period)
        self.atr = self.I(calc_atr, self.data.High, self.data.Low, self.data.Close, self.kc_period)
        self.rsi = self.I(calc_rsi, self.data.Close, self.rsi_period)

    def next(self):
        if np.isnan(self.atr[-1]) or np.isnan(self.rsi[-1]):
            return
        kc_lower = self.kc_mid[-1] - self.kc_mult * self.atr[-1]
        kc_upper = self.kc_mid[-1] + self.kc_mult * self.atr[-1]

        if not self.position:
            if self.data.Close[-1] <= kc_lower and self.rsi[-1] < self.rsi_entry:
                self.buy()
        else:
            if self.data.Close[-1] >= kc_upper:
                self.position.close()

bt = Backtest(data, KeltnerRSICombo, cash=100_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(f"R2-04 Keltner+RSI | Return: {stats['Return [%]']:.1f}% | Sharpe: {stats['Sharpe Ratio']:.2f} | Sortino: {stats['Sortino Ratio']:.2f} | MaxDD: {stats['Max. Drawdown [%]']:.1f}% | WinRate: {stats['Win Rate [%]']:.1f}% | Trades: {stats['# Trades']} | SQN: {stats['SQN']:.2f}")
