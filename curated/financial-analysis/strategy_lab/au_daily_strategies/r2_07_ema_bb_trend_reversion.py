"""R2-07: EMA Ribbon Trend + Bollinger Dip Entry — Only buy BB dips in uptrends."""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_au_data
import numpy as np, talib
from backtesting import Backtest, Strategy

data = load_au_data("daily")

def calc_ema(close, period):
    return talib.EMA(close, timeperiod=period)

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

class EMABBTrendReversion(Strategy):
    ema_fast = 8
    ema_mid = 21
    ema_slow = 55
    bb_period = 20
    bb_std = 2.0

    def init(self):
        self.ema8 = self.I(calc_ema, self.data.Close, self.ema_fast)
        self.ema21 = self.I(calc_ema, self.data.Close, self.ema_mid)
        self.ema55 = self.I(calc_ema, self.data.Close, self.ema_slow)
        self.bb_upper = self.I(calc_bb_upper, self.data.Close, self.bb_period, self.bb_std)
        self.bb_lower = self.I(calc_bb_lower, self.data.Close, self.bb_period, self.bb_std)

    def next(self):
        if np.isnan(self.ema55[-1]) or np.isnan(self.bb_lower[-1]):
            return
        bullish_trend = self.ema8[-1] > self.ema21[-1] > self.ema55[-1]

        if not self.position:
            if bullish_trend and self.data.Close[-1] <= self.bb_lower[-1]:
                self.buy()
        else:
            if self.data.Close[-1] >= self.bb_upper[-1]:
                self.position.close()

bt = Backtest(data, EMABBTrendReversion, cash=100_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(f"R2-07 EMA+BB Trend Rev | Return: {stats['Return [%]']:.1f}% | Sharpe: {stats['Sharpe Ratio']:.2f} | Sortino: {stats['Sortino Ratio']:.2f} | MaxDD: {stats['Max. Drawdown [%]']:.1f}% | WinRate: {stats['Win Rate [%]']:.1f}% | Trades: {stats['# Trades']} | SQN: {stats['SQN']:.2f}")
