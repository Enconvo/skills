"""R1-08: ADX + DI Crossover — Trade strong trends only."""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_au_data
import numpy as np, talib
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

data = load_au_data("daily")

def calc_adx(high, low, close, period):
    return talib.ADX(high, low, close, timeperiod=period)

def calc_plus_di(high, low, close, period):
    return talib.PLUS_DI(high, low, close, timeperiod=period)

def calc_minus_di(high, low, close, period):
    return talib.MINUS_DI(high, low, close, timeperiod=period)

class ADXTrend(Strategy):
    adx_period = 14
    adx_threshold = 25

    def init(self):
        self.adx = self.I(calc_adx, self.data.High, self.data.Low, self.data.Close, self.adx_period)
        self.plus_di = self.I(calc_plus_di, self.data.High, self.data.Low, self.data.Close, self.adx_period)
        self.minus_di = self.I(calc_minus_di, self.data.High, self.data.Low, self.data.Close, self.adx_period)

    def next(self):
        if np.isnan(self.adx[-1]):
            return
        if not self.position:
            if self.adx[-1] > self.adx_threshold and crossover(self.plus_di, self.minus_di):
                self.buy()
        else:
            if crossover(self.minus_di, self.plus_di):
                self.position.close()

bt = Backtest(data, ADXTrend, cash=100_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(f"R1-08 ADX Trend | Return: {stats['Return [%]']:.1f}% | Sharpe: {stats['Sharpe Ratio']:.2f} | Sortino: {stats['Sortino Ratio']:.2f} | MaxDD: {stats['Max. Drawdown [%]']:.1f}% | WinRate: {stats['Win Rate [%]']:.1f}% | Trades: {stats['# Trades']} | SQN: {stats['SQN']:.2f}")
