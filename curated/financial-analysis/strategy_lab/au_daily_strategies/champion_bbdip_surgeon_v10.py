"""
CHAMPION V10: BBDip Surgeon — AU Daily Strategy (2024-01 onward)
404.7% return | Sharpe 1.55 | Sortino 5.87 | MaxDD -13.4% | 100% WR | 4 trades

CONCEPT:
Mean-reversion entry on Bollinger Band dips with a trend-regime gate.
Buys when price touches or pierces the lower BB while remaining above SMA(60),
ensuring dips happen in a healthy uptrend — not a breakdown.

KEY PARAMETERS:
- BB(11, 2.0) lower band — tight period catches shallow dips quickly
- SMA(60) regime filter — only enter when close > SMA(60)
- 20% wide trail → 5% tight trail at +35% gain — surgical profit lock
- Cooldown 3 bars — prevents whipsaw re-entries after trail stop

RESULTS (2024-01 → 2026-03): $100K → $504.7K | 4 trades, all winners
"""

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_au_data
import numpy as np
import talib
from backtesting import Backtest, Strategy


data = load_au_data("daily")
data = data["2024-01-01":]


def calc_bb_lower(close, period, nbdev):
    _, _, lower = talib.BBANDS(close, timeperiod=period, nbdevup=nbdev, nbdevdn=nbdev)
    return lower


def calc_sma(close, period):
    return talib.SMA(close, timeperiod=period)


class BBDipSurgeonV10(Strategy):
    bb_period = 11        # Bollinger Band period — tight to catch shallow dips
    bb_std = 2.0          # Bollinger Band std dev
    sma_period = 60       # Regime filter — bull = close > SMA(60)
    wide_trail = 20.0     # Wide trail early in trade
    tight_trail = 5.0     # Tight trail once profitable — surgical lock
    ratchet_at = 35.0     # Tighten trail when gain exceeds 35%
    cooldown = 3          # 3-bar cooldown prevents whipsaw

    def init(self):
        self.bb_lower = self.I(calc_bb_lower, self.data.Close, self.bb_period, self.bb_std)
        self.sma = self.I(calc_sma, self.data.Close, self.sma_period)
        self.high_water = 0
        self.entry_price = 0
        self.bars_since_exit = 999

    def next(self):
        if np.isnan(self.bb_lower[-1]) or np.isnan(self.sma[-1]):
            return

        if not self.position:
            self.bars_since_exit += 1
            bb_dip = self.data.Close[-1] <= self.bb_lower[-1]
            above_sma = self.data.Close[-1] > self.sma[-1]
            cooled = self.bars_since_exit > self.cooldown

            if bb_dip and above_sma and cooled:
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


bt = Backtest(data, BBDipSurgeonV10, cash=100_000, commission=0.001,
              exclusive_orders=True, finalize_trades=True)
stats = bt.run()

bh_ret = (data.iloc[-1]["Close"] / data.iloc[0]["Open"] - 1) * 100

print(f"\n{'═' * 70}")
print(f"  CHAMPION V10: BBDip Surgeon (2024-01 onward, 4 trades)")
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
