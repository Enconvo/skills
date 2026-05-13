"""
CHAMPION V10: EMACross Attacker — AU Daily Strategy (2024-01 onward)
523.1% return | Sharpe 1.25 | Sortino 4.68 | MaxDD -24.8% | 100% WR | 4 trades

ENTRY: EMA(5) crosses above EMA(13) AND Close > SMA(30) regime filter.
       Cooldown=0 — instant re-entry after exit.

EXIT:  Ratcheting trailing stop —
       20% wide trail initially, tightens to 7% once unrealized gain > 60%.
       High water mark tracked from entry.

This is an "attacker" archetype: fast EMA crossover for entries,
aggressive trail tightening to lock in large gains.
"""

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_au_data
import numpy as np
import talib
from backtesting import Backtest, Strategy
from backtesting.lib import crossover


data = load_au_data("daily")
data = data.loc["2024-01-01":]


def calc_ema(close, period):
    return talib.EMA(close, timeperiod=period)

def calc_sma(close, period):
    return talib.SMA(close, timeperiod=period)


class EMACrossAttackerV10(Strategy):
    ema_fast = 5          # Fast EMA for crossover
    ema_slow = 13         # Slow EMA for crossover
    sma_period = 30       # Regime filter — bull when Close > SMA(30)
    wide_trail = 20.0     # Wide trail early in trade
    tight_trail = 7.0     # Tight trail once gain > ratchet threshold
    ratchet_at = 60.0     # Tighten trail when gain exceeds 60%
    cooldown = 0          # Instant re-entry

    def init(self):
        self.ema_f = self.I(calc_ema, self.data.Close, self.ema_fast)
        self.ema_s = self.I(calc_ema, self.data.Close, self.ema_slow)
        self.sma = self.I(calc_sma, self.data.Close, self.sma_period)
        self.high_water = 0
        self.entry_price = 0
        self.bars_since_exit = 999

    def next(self):
        if np.isnan(self.ema_f[-1]) or np.isnan(self.ema_s[-1]) or np.isnan(self.sma[-1]):
            return

        if not self.position:
            self.bars_since_exit += 1
            ema_cross = crossover(self.ema_f, self.ema_s)
            above_sma = self.data.Close[-1] > self.sma[-1]
            cooled = self.bars_since_exit > self.cooldown

            if ema_cross and above_sma and cooled:
                self.buy()
                self.high_water = self.data.Close[-1]
                self.entry_price = self.data.Close[-1]
        else:
            self.high_water = max(self.high_water, self.data.Close[-1])
            gain_pct = (self.data.Close[-1] / self.entry_price - 1) * 100
            trail = self.tight_trail if gain_pct > self.ratchet_at else self.wide_trail
            trail_level = self.high_water * (1 - trail / 100)

            if self.data.Close[-1] < trail_level:
                self.position.close()
                self.bars_since_exit = 0


bt = Backtest(data, EMACrossAttackerV10, cash=100_000, commission=0.001,
              exclusive_orders=True, finalize_trades=True)
stats = bt.run()

bh_ret = (data.iloc[-1]["Close"] / data.iloc[0]["Open"] - 1) * 100

print(f"\n{'=' * 70}")
print(f"  CHAMPION V10: EMACross Attacker (2024-01 onward)")
print(f"{'=' * 70}")
print(f"  Data:       {data.index[0].date()} -> {data.index[-1].date()} ({len(data)} bars)")
print(f"  Return:     {stats['Return [%]']:.1f}% (B&H: {bh_ret:.1f}%)")
print(f"  Alpha:      {stats['Return [%]'] - bh_ret:+.1f}%")
print(f"  Sharpe:     {stats['Sharpe Ratio']:.2f}")
print(f"  Sortino:    {stats['Sortino Ratio']:.2f}")
print(f"  MaxDD:      {stats['Max. Drawdown [%]']:.1f}%")
print(f"  Win Rate:   {stats['Win Rate [%]']:.1f}%")
print(f"  Trades:     {stats['# Trades']}")
print(f"  Equity:     ${stats['Equity Final [$]']:,.0f}")
print(f"  Peak Equity: ${stats._equity_curve['Equity'].max():,.0f}")
print(f"{'=' * 70}")

trades = stats['_trades']
print(f"\n  TRADES:")
for i, t in trades.iterrows():
    dur = t['Duration'].days
    ret = t['ReturnPct'] * 100
    win = "W" if ret > 0 else "L"
    print(f"  {win} {i+1}. {t['EntryTime'].date()} -> {t['ExitTime'].date()} ({dur}d)")
    print(f"      ${t['EntryPrice']:.2f} -> ${t['ExitPrice']:.2f} | {ret:+.1f}% | ${t['PnL']:+,.0f}")
print()
