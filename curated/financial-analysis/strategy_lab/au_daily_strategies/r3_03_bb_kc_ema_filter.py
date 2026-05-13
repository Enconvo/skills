"""R3-03: BB+KC Squeeze + EMA Trend Filter — Best entry + trend confirmation.
Only takes BB+KC squeeze entries when EMA 21 > EMA 55 (uptrend)."""
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

def calc_bb_middle(close, period, nbdev):
    return _get_bbands(close, period, nbdev)[1]

def calc_atr(high, low, close, period):
    return talib.ATR(high, low, close, timeperiod=period)

class BBKCEMAFilter(Strategy):
    bb_period = 20
    bb_std = 2.0
    kc_period = 20
    kc_mult = 2.0
    ema_mid = 21
    ema_slow = 55

    def init(self):
        self.bb_upper = self.I(calc_bb_upper, self.data.Close, self.bb_period, self.bb_std)
        self.bb_lower = self.I(calc_bb_lower, self.data.Close, self.bb_period, self.bb_std)
        self.bb_middle = self.I(calc_bb_middle, self.data.Close, self.bb_period, self.bb_std)
        self.kc_mid = self.I(calc_ema, self.data.Close, self.kc_period)
        self.atr = self.I(calc_atr, self.data.High, self.data.Low, self.data.Close, self.kc_period)
        self.ema21 = self.I(calc_ema, self.data.Close, self.ema_mid)
        self.ema55 = self.I(calc_ema, self.data.Close, self.ema_slow)

    def next(self):
        price = self.data.Close[-1]
        if np.isnan(self.atr[-1]) or np.isnan(self.ema55[-1]):
            return
        kc_lower = self.kc_mid[-1] - self.kc_mult * self.atr[-1]
        uptrend = self.ema21[-1] > self.ema55[-1]

        if not self.position:
            if uptrend and price <= self.bb_lower[-1] and price <= kc_lower:
                self.buy()
        else:
            if price >= self.bb_middle[-1]:
                self.position.close()

bt = Backtest(data, BBKCEMAFilter, cash=100_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(f"R3-03 BB+KC+EMA Filt | Return: {stats['Return [%]']:.1f}% | Sharpe: {stats['Sharpe Ratio']:.2f} | Sortino: {stats['Sortino Ratio']:.2f} | MaxDD: {stats['Max. Drawdown [%]']:.1f}% | WinRate: {stats['Win Rate [%]']:.1f}% | Trades: {stats['# Trades']} | SQN: {stats['SQN']:.2f}")
