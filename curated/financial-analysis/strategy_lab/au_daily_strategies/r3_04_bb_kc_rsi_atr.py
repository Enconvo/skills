"""R3-04: BB+KC Squeeze + RSI < 40 + ATR Trail — Max-return variant.
Triple oversold confirmation with adaptive exit for biggest runs."""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_au_data
import numpy as np, talib
from backtesting import Backtest, Strategy

data = load_au_data("daily")

def calc_rsi(close, period):
    return talib.RSI(close, timeperiod=period)

def calc_bb_lower(close, period, nbdev):
    u, m, l = talib.BBANDS(close, timeperiod=period, nbdevup=nbdev, nbdevdn=nbdev)
    return l

def calc_ema(close, period):
    return talib.EMA(close, timeperiod=period)

def calc_atr(high, low, close, period):
    return talib.ATR(high, low, close, timeperiod=period)

class BBKCRSIATRTrail(Strategy):
    bb_period = 20
    bb_std = 2.0
    kc_period = 20
    kc_mult = 2.0
    rsi_period = 14
    rsi_entry = 40
    atr_period = 14
    atr_mult = 3.0

    def init(self):
        self.bb_lower = self.I(calc_bb_lower, self.data.Close, self.bb_period, self.bb_std)
        self.kc_mid = self.I(calc_ema, self.data.Close, self.kc_period)
        self.atr = self.I(calc_atr, self.data.High, self.data.Low, self.data.Close, self.atr_period)
        self.rsi = self.I(calc_rsi, self.data.Close, self.rsi_period)
        self.highest = 0
        self.trail_stop = 0

    def next(self):
        price = self.data.Close[-1]
        atr_val = self.atr[-1]
        if np.isnan(atr_val) or np.isnan(self.rsi[-1]) or np.isnan(self.bb_lower[-1]):
            return
        kc_lower = self.kc_mid[-1] - self.kc_mult * self.atr[-1]

        if not self.position:
            if price <= self.bb_lower[-1] and price <= kc_lower and self.rsi[-1] < self.rsi_entry:
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

bt = Backtest(data, BBKCRSIATRTrail, cash=100_000, commission=0.001, exclusive_orders=True)
stats = bt.run()
print(f"R3-04 BB+KC+RSI+ATR | Return: {stats['Return [%]']:.1f}% | Sharpe: {stats['Sharpe Ratio']:.2f} | Sortino: {stats['Sortino Ratio']:.2f} | MaxDD: {stats['Max. Drawdown [%]']:.1f}% | WinRate: {stats['Win Rate [%]']:.1f}% | Trades: {stats['# Trades']} | SQN: {stats['SQN']:.2f}")
