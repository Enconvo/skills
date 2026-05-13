"""R2-01: Bollinger Bounce + RSI Confirmation — Double mean reversion signal."""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_au_data
import numpy as np, talib
from backtesting import Backtest, Strategy

data = load_au_data("daily")

_bb_cache = {}

def _get_bbands(close, period, nbdev):
    key = (id(close), period, nbdev)
    if key not in _bb_cache:
        _bb_cache[key] = talib.BBANDS(close, timeperiod=period, nbdevup=nbdev, nbdevdn=nbdev)
    return _bb_cache[key]

def calc_bb_upper(close, period, nbdev):
    return _get_bbands(close, period, nbdev)[0]

def calc_bb_lower(close, period, nbdev):
    return _get_bbands(close, period, nbdev)[2]

def calc_rsi(close, period):
    return talib.RSI(close, timeperiod=period)

class BBRSICombo(Strategy):
    bb_period = 20
    bb_std = 2.0
    rsi_period = 14
    rsi_entry = 35
    rsi_exit = 70

    def init(self):
        self.bb_upper = self.I(calc_bb_upper, self.data.Close, self.bb_period, self.bb_std)
        self.bb_lower = self.I(calc_bb_lower, self.data.Close, self.bb_period, self.bb_std)
        self.rsi = self.I(calc_rsi, self.data.Close, self.rsi_period)

    def next(self):
        if np.isnan(self.bb_lower[-1]) or np.isnan(self.rsi[-1]):
            return
        if not self.position:
            if self.data.Close[-1] <= self.bb_lower[-1] and self.rsi[-1] < self.rsi_entry:
                self.buy()
        else:
            if self.data.Close[-1] >= self.bb_upper[-1] or self.rsi[-1] > self.rsi_exit:
                self.position.close()

bt = Backtest(data, BBRSICombo, cash=100_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(f"R2-01 BB+RSI Combo | Return: {stats['Return [%]']:.1f}% | Sharpe: {stats['Sharpe Ratio']:.2f} | Sortino: {stats['Sortino Ratio']:.2f} | MaxDD: {stats['Max. Drawdown [%]']:.1f}% | WinRate: {stats['Win Rate [%]']:.1f}% | Trades: {stats['# Trades']} | SQN: {stats['SQN']:.2f}")
