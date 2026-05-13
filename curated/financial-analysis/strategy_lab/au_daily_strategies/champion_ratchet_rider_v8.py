"""
CHAMPION V8: RatchetRider — AU Daily Strategy (Full Data Optimized)
76,000+ experiments across 7 archetypes | 918.7% return | Sharpe 0.88 | Sortino 2.28

Karpathy-loop: V1 (268%) → V2 (200%) → V3 (330%) → V5 (389%) → V7 (783%) → V8 (919%)

KEY PARAMETERS:
- SMA(75) regime filter — tighter than V7's SMA(100), enters bull regime sooner
- EMA(2) entry — ultra-fast, within 1-2 days
- 20% wide trail → 11% tight trail at +40% gain — tighter ratchet locks profits faster
- Cooldown 2 bars — prevents whipsaw re-entries

FULL DATA (2021-03 to 2026-03): $100K → $1.02M → peak $1.35M
"""

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_au_data
import numpy as np
import talib
from backtesting import Backtest, Strategy


data = load_au_data("daily")


def calc_ema(close, period):
    return talib.EMA(close, timeperiod=period)

def calc_sma(close, period):
    return talib.SMA(close, timeperiod=period)


class RatchetRiderV8(Strategy):
    ema_entry = 2         # Ultra-fast entry
    sma_period = 75       # Regime filter — enters bull sooner than SMA(100)
    wide_trail = 20.0     # Wide trail early in trade
    tight_trail = 11.0    # Tight trail once profitable — locks gains faster
    ratchet_at = 40.0     # Ratchet earlier than V7 (40% vs 60%)
    cooldown = 2          # 2-bar cooldown prevents whipsaw

    def init(self):
        self.ema = self.I(calc_ema, self.data.Close, self.ema_entry)
        self.sma = self.I(calc_sma, self.data.Close, self.sma_period)
        self.high_water = 0
        self.entry_price = 0
        self.bars_since_exit = 999

    def next(self):
        if np.isnan(self.ema[-1]) or np.isnan(self.sma[-1]):
            return

        if not self.position:
            self.bars_since_exit += 1
            above_ema = self.data.Close[-1] > self.ema[-1]
            above_sma = self.data.Close[-1] > self.sma[-1]
            cooled = self.bars_since_exit > self.cooldown

            if above_ema and above_sma and cooled:
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


bt = Backtest(data, RatchetRiderV8, cash=100_000, commission=0.001,
              exclusive_orders=True, finalize_trades=True)
stats = bt.run()

bh_ret = (data.iloc[-1]["Close"] / data.iloc[0]["Open"] - 1) * 100

print(f"\n{'═' * 70}")
print(f"  CHAMPION V8: RatchetRider (Full Data, 76K+ experiments)")
print(f"{'═' * 70}")
print(f"  Data:       {data.index[0].date()} → {data.index[-1].date()} ({len(data)} bars)")
print(f"  Return:     {stats['Return [%]']:.1f}% (B&H: {bh_ret:.1f}%)")
print(f"  Alpha:      {stats['Return [%]'] - bh_ret:+.1f}%")
print(f"  Sharpe:     {stats['Sharpe Ratio']:.2f}")
print(f"  Sortino:    {stats['Sortino Ratio']:.2f}")
print(f"  MaxDD:      {stats['Max. Drawdown [%]']:.1f}%")
print(f"  Win Rate:   {stats['Win Rate [%]']:.1f}%")
print(f"  Trades:     {stats['# Trades']}")
print(f"  Equity:     ${stats['Equity Final [$]']:,.0f}")
print(f"  Peak Equity: ${stats._equity_curve['Equity'].max():,.0f}")
print(f"{'═' * 70}")

trades = stats['_trades']
print(f"\n  TRADES:")
for i, t in trades.iterrows():
    dur = t['Duration'].days
    ret = t['ReturnPct'] * 100
    win = "✓" if ret > 0 else "✗"
    print(f"  {win} {i+1}. {t['EntryTime'].date()} → {t['ExitTime'].date()} ({dur}d)")
    print(f"      ${t['EntryPrice']:.2f} → ${t['ExitPrice']:.2f} | {ret:+.1f}% | ${t['PnL']:+,.0f}")
print()
