"""R1-11: StochRSI Momentum — Buy oversold StochRSI cross, sell overbought."""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_au_data
import numpy as np, talib
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

data = load_au_data("daily")

_stochrsi_cache = {}

def _get_stochrsi(close, period, k_period):
    key = (id(close), period, k_period)
    if key not in _stochrsi_cache:
        _stochrsi_cache[key] = talib.STOCHRSI(close, timeperiod=period, fastk_period=k_period, fastd_period=3)
    return _stochrsi_cache[key]

def calc_stochrsi_k(close, period, k_period):
    return _get_stochrsi(close, period, k_period)[0]

def calc_stochrsi_d(close, period, k_period):
    return _get_stochrsi(close, period, k_period)[1]

class StochRSIMomentum(Strategy):
    period = 14
    k_period = 5
    oversold = 20
    overbought = 80

    def init(self):
        self.k = self.I(calc_stochrsi_k, self.data.Close, self.period, self.k_period)
        self.d = self.I(calc_stochrsi_d, self.data.Close, self.period, self.k_period)

    def next(self):
        if np.isnan(self.k[-1]) or np.isnan(self.d[-1]):
            return
        if not self.position:
            if self.k[-1] < self.oversold and crossover(self.k, self.d):
                self.buy()
        else:
            if self.k[-1] > self.overbought and crossover(self.d, self.k):
                self.position.close()

bt = Backtest(data, StochRSIMomentum, cash=100_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(f"R1-11 StochRSI Momentum | Return: {stats['Return [%]']:.1f}% | Sharpe: {stats['Sharpe Ratio']:.2f} | Sortino: {stats['Sortino Ratio']:.2f} | MaxDD: {stats['Max. Drawdown [%]']:.1f}% | WinRate: {stats['Win Rate [%]']:.1f}% | Trades: {stats['# Trades']} | SQN: {stats['SQN']:.2f}")
