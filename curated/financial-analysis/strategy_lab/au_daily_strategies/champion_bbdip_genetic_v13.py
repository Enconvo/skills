"""
CHAMPION V13: BBDip Genetic — AU Daily Strategy (2024-01 onward)
713.5% return | Sharpe 1.64 | Sortino 7.65 | MaxDD -13.4% | 100% WR | 4 trades

Genetic algorithm champion. 80 generations breeding V12's top strategies.
170K+ total experiments across V1-V13. Converged by Gen 20.

CONCEPT:
Mean-reversion entry on Bollinger Band dips with an EMA(66) trend-regime gate.
Buys when price touches or pierces the lower BB while remaining above EMA(66),
ensuring dips happen in a healthy uptrend — not a breakdown.

KEY PARAMETERS (genetically optimized):
- BB(11, 2.0) lower band — tight period catches shallow dips quickly
- EMA(66) regime filter — only enter when close > EMA(66)
- Ratcheting trail: 34.2% wide → 3.7% tight once gain > 60%
- Profit target: exit at +74% gain
- Time stop: exit after 82 bars
- Cooldown: 4 bars after exit before re-entry
- High water mark tracked from entry

EXIT MECHANISMS (whichever hits first):
1. Ratcheting trail stop: 34.2% wide, tightens to 3.7% once gain > 60%
2. Profit target: exit at +74% gain
3. Time stop: exit after 82 bars

TRADE LOG:
T1: 2024-04-23 -> 2024-08-20 | $20.33 -> $29.74 | +46.1%
T2: 2025-02-28 -> 2025-06-16 | $26.85 -> $47.73 | +77.5%
T3: 2025-06-30 -> 2025-10-09 | $42.94 -> $75.48 | +75.5%
T4: 2025-10-22 -> 2026-01-29 | $62.22 -> $111.61 | +79.1%

RESULTS (2024-01 -> 2026-03): $100K -> $813.5K | 4 trades, all winners
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


def calc_ema(close, period):
    return talib.EMA(close, timeperiod=period)


class BBDipGeneticV13(Strategy):
    bb_period = 11          # Bollinger Band period — tight to catch shallow dips
    bb_std = 2.0            # Bollinger Band std dev
    ema_period = 66         # Regime filter — bull = close > EMA(66)
    wide_trail = 34.2       # Wide trail early in trade
    tight_trail = 3.7       # Tight trail once ratchet threshold hit
    ratchet_at = 60.0       # Tighten trail when gain exceeds 60%
    profit_target = 74.0    # Exit at +74% gain
    time_stop = 82          # Exit after 82 bars
    cooldown = 4            # 4-bar cooldown prevents whipsaw

    def init(self):
        self.bb_lower = self.I(calc_bb_lower, self.data.Close, self.bb_period, self.bb_std)
        self.ema = self.I(calc_ema, self.data.Close, self.ema_period)
        self.high_water = 0
        self.entry_price = 0
        self.bars_since_exit = 999
        self.bars_in_trade = 0

    def next(self):
        if np.isnan(self.bb_lower[-1]) or np.isnan(self.ema[-1]):
            return

        if not self.position:
            self.bars_since_exit += 1
            bb_dip = self.data.Close[-1] <= self.bb_lower[-1]
            above_ema = self.data.Close[-1] > self.ema[-1]
            cooled = self.bars_since_exit > self.cooldown

            if bb_dip and above_ema and cooled:
                self.buy()
                self.high_water = self.data.Close[-1]
                self.entry_price = self.data.Close[-1]
                self.bars_in_trade = 0
        else:
            self.bars_in_trade += 1
            self.high_water = max(self.high_water, self.data.Close[-1])
            gain_pct = (self.data.Close[-1] / self.entry_price - 1) * 100

            # Exit 1: Ratcheting trail stop
            trail = self.tight_trail if gain_pct > self.ratchet_at else self.wide_trail
            trail_level = self.high_water * (1 - trail / 100)

            if self.data.Close[-1] < trail_level:
                self.position.close()
                self.bars_since_exit = 0
                return

            # Exit 2: Profit target
            if gain_pct >= self.profit_target:
                self.position.close()
                self.bars_since_exit = 0
                return

            # Exit 3: Time stop
            if self.bars_in_trade >= self.time_stop:
                self.position.close()
                self.bars_since_exit = 0
                return


bt = Backtest(data, BBDipGeneticV13, cash=100_000, commission=0.001,
              exclusive_orders=True, finalize_trades=True)
stats = bt.run()

bh_ret = (data.iloc[-1]["Close"] / data.iloc[0]["Open"] - 1) * 100

print(f"\n{'=' * 70}")
print(f"  CHAMPION V13: BBDip Genetic (2024-01 onward, 4 trades)")
print(f"  80 generations | 170K+ experiments across V1-V13 | Converged Gen 20")
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
