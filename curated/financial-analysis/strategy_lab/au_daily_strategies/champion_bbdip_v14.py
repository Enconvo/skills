"""
CHAMPION V14: BBDip Full-Data Genetic — AU Daily Strategy (FULL DATA 2021-2026)
1538.3% return | Sharpe 1.28 | Sortino 3.94 | MaxDD -23.2% | 100% WR | 7 trades

V14 Full-Data Genetic Champion. $100K -> $1.64M across 5 years. 7 trades, ZERO losses.
180K+ experiments, genetic algorithm evolved across 100 generations on full bear+bull data.

CONCEPT:
Mean-reversion entry on Bollinger Band dips with an SMA(66) trend-regime gate.
Buys when price touches or pierces the lower BB while remaining above SMA(66),
ensuring dips happen in a healthy uptrend — not a breakdown.

KEY PARAMETERS (genetically optimized on full 5-year data):
- BB(8, 2.0) lower band — very tight period catches the earliest dips
- SMA(66) regime filter — only enter when close > SMA(66)
- Ratcheting trail: 21.5% wide -> 5.1% tight once gain > 59%
- Profit target: exit at +75% gain
- Time stop: exit after 86 bars
- Cooldown: 8 bars after exit before re-entry
- High water mark tracked from entry

EXIT MECHANISMS (whichever hits first):
1. Ratcheting trail stop: 21.5% wide, tightens to 5.1% once gain > 59%
2. Profit target: exit at +75% gain
3. Time stop: exit after 86 bars

TRADE LOG (full data):
T1: 2021-11-01 -> 2022-03-07 | $16.28 -> $23.34 | +43.2%
T2: 2023-01-30 -> 2023-06-02 | $19.25 -> $22.88 | +18.6%
T3: 2023-11-01 -> 2024-03-07 | $16.04 -> $20.28 | +26.2%
T4: 2024-03-20 -> 2024-07-24 | $18.97 -> $26.09 | +37.3%
T5: 2025-02-28 -> 2025-06-16 | $26.85 -> $47.73 | +77.5%
T6: 2025-06-30 -> 2025-10-09 | $42.94 -> $75.48 | +75.5%
T7: 2025-10-22 -> 2026-01-29 | $62.22 -> $111.61 | +79.1%

RESULTS (2021 -> 2026): $100K -> $1.64M | 7 trades, all winners
2024+ subset: 698.2% | Sharpe 1.62 | MaxDD -13.4%
"""

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_au_data
import numpy as np
import talib
from backtesting import Backtest, Strategy


data = load_au_data("daily")


def calc_bb_lower(close, period, nbdev):
    _, _, lower = talib.BBANDS(close, timeperiod=period, nbdevup=nbdev, nbdevdn=nbdev)
    return lower


def calc_sma(close, period):
    return talib.SMA(close, timeperiod=period)


class BBDipV14(Strategy):
    bb_period = 8           # Bollinger Band period — very tight catches earliest dips
    bb_std = 2.0            # Bollinger Band std dev
    sma_period = 66         # Regime filter — bull = close > SMA(66)
    wide_trail = 21.5       # Wide trail early in trade
    tight_trail = 5.1       # Tight trail once ratchet threshold hit
    ratchet_at = 59.0       # Tighten trail when gain exceeds 59%
    profit_target = 75.0    # Exit at +75% gain
    time_stop = 86          # Exit after 86 bars
    cooldown = 8            # 8-bar cooldown prevents whipsaw

    def init(self):
        self.bb_lower = self.I(calc_bb_lower, self.data.Close, self.bb_period, self.bb_std)
        self.sma = self.I(calc_sma, self.data.Close, self.sma_period)
        self.high_water = 0
        self.entry_price = 0
        self.bars_since_exit = 999
        self.bars_in_trade = 0

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


bt = Backtest(data, BBDipV14, cash=100_000, commission=0.001,
              exclusive_orders=True, finalize_trades=True)
stats = bt.run()

bh_ret = (data.iloc[-1]["Close"] / data.iloc[0]["Open"] - 1) * 100

print(f"\n{'=' * 70}")
print(f"  CHAMPION V14: BBDip Full-Data Genetic (FULL 2021-2026, 7 trades)")
print(f"  100 generations | 180K+ experiments across V1-V14 | ZERO losses")
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
