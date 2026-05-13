"""R2-02: Bollinger Entry + ATR Trailing Exit — Capture bigger runs than fixed BB exit."""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_au_data
import numpy as np, talib
from backtesting import Backtest, Strategy

data = load_au_data("daily")

def calc_bb_lower(close, period, nbdev):
    u, m, l = talib.BBANDS(close, timeperiod=period, nbdevup=nbdev, nbdevdn=nbdev)
    return l

def calc_atr(high, low, close, period):
    return talib.ATR(high, low, close, timeperiod=period)

class BBATRTrailing(Strategy):
    bb_period = 20
    bb_std = 2.0
    atr_period = 14
    atr_mult = 2.5

    def init(self):
        self.bb_lower = self.I(calc_bb_lower, self.data.Close, self.bb_period, self.bb_std)
        self.atr = self.I(calc_atr, self.data.High, self.data.Low, self.data.Close, self.atr_period)
        self.highest = 0
        self.trail_stop = 0

    def next(self):
        price = self.data.Close[-1]
        atr_val = self.atr[-1]
        if np.isnan(self.bb_lower[-1]) or np.isnan(atr_val):
            return
        if not self.position:
            if price <= self.bb_lower[-1]:
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

bt = Backtest(data, BBATRTrailing, cash=100_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(f"R2-02 BB+ATR Trail | Return: {stats['Return [%]']:.1f}% | Sharpe: {stats['Sharpe Ratio']:.2f} | Sortino: {stats['Sortino Ratio']:.2f} | MaxDD: {stats['Max. Drawdown [%]']:.1f}% | WinRate: {stats['Win Rate [%]']:.1f}% | Trades: {stats['# Trades']} | SQN: {stats['SQN']:.2f}")
