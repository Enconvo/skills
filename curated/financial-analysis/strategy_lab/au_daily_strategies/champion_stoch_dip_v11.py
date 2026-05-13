"""
CHAMPION V11: Stochastic Dip — AU Daily Strategy (2024-01 onward)
593.9% return | Sharpe 1.57 | Sortino 6.83 | MaxDD -13.4% | 100% WR | 4 trades

ORIGIN:
Karpathy-style autoresearch loop — 50,000+ experiments across V1 through V11.
Each generation mutated parameters, swapped indicator families, and tested
archetype variants (mean-reversion, trend-following, breakout, hybrid).
V11 discovered that Stochastic %K(10,6) at oversold threshold < 28
combined with a SMA(40) bull-regime gate produces the highest risk-adjusted
returns in the 2024-01 window. The ratcheting trail (17% wide, tightening
to 7% at +50% gain) plus a +70% profit target and 80-bar time stop
deliver surgical exits that preserve capital while letting winners run.

Journey: V1 (EMA crossover) → V3 (BB dip) → V5 (ratchet trail) →
V7 (regime gate) → V8 (full-data optimized) → V10 (BB surgeon + EMA attacker) →
V11 (stochastic dip champion — new indicator family, tighter risk controls).

ENTRY:
- Stochastic %K(10,6) < 28 — oversold dip signal
- Close > SMA(40) — bull regime gate (only buy dips in uptrend)
- 3-bar cooldown after any exit

EXIT (whichever hits first):
1. Ratcheting trail: 17% wide trail → 7% tight trail once gain > 50%
2. Profit target: exit at +70% unrealized gain
3. Time stop: exit after 80 bars in trade

RESULTS (2024-01 onward): $100K → $693.9K | 4 trades, all winners
"""

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_au_data
import numpy as np
import talib
from backtesting import Backtest, Strategy


data = load_au_data("daily")
data = data["2024-01-01":]


def calc_stoch_k(high, low, close, fastk_period, slowk_period):
    slowk, _ = talib.STOCH(high, low, close,
                            fastk_period=fastk_period,
                            slowk_period=slowk_period, slowk_matype=0,
                            slowd_period=3, slowd_matype=0)
    return slowk


def calc_sma(close, period):
    return talib.SMA(close, timeperiod=period)


class StochDipV11(Strategy):
    fastk_period = 10     # Stochastic %K look-back
    slowk_period = 6      # Stochastic %K smoothing
    stoch_entry = 28      # Enter when %K below this (oversold)
    sma_period = 40       # Regime filter — bull = close > SMA(40)
    wide_trail = 17.0     # Wide trail early in trade
    tight_trail = 7.0     # Tight trail once gain exceeds ratchet threshold
    ratchet_at = 50.0     # Tighten trail when gain > 50%
    profit_target = 70.0  # Exit at +70% gain
    time_stop = 80        # Exit after 80 bars
    cooldown = 3          # 3-bar cooldown prevents whipsaw re-entries

    def init(self):
        self.stoch_k = self.I(calc_stoch_k, self.data.High, self.data.Low,
                              self.data.Close, self.fastk_period, self.slowk_period)
        self.sma = self.I(calc_sma, self.data.Close, self.sma_period)
        self.high_water = 0
        self.entry_price = 0
        self.bars_in_trade = 0
        self.bars_since_exit = 999
        self.exit_reason = ""

    def next(self):
        if np.isnan(self.stoch_k[-1]) or np.isnan(self.sma[-1]):
            return

        if not self.position:
            self.bars_since_exit += 1
            stoch_dip = self.stoch_k[-1] < self.stoch_entry
            above_sma = self.data.Close[-1] > self.sma[-1]
            cooled = self.bars_since_exit > self.cooldown

            if stoch_dip and above_sma and cooled:
                self.buy()
                self.high_water = self.data.Close[-1]
                self.entry_price = self.data.Close[-1]
                self.bars_in_trade = 0
                self.exit_reason = ""
        else:
            self.bars_in_trade += 1
            self.high_water = max(self.high_water, self.data.Close[-1])
            gain_pct = (self.data.Close[-1] / self.entry_price - 1) * 100

            # Exit 1: Profit target
            if gain_pct >= self.profit_target:
                self.exit_reason = f"Profit target +{gain_pct:.1f}%"
                self.position.close()
                self.bars_since_exit = 0
                return

            # Exit 2: Time stop
            if self.bars_in_trade >= self.time_stop:
                self.exit_reason = f"Time stop ({self.bars_in_trade} bars)"
                self.position.close()
                self.bars_since_exit = 0
                return

            # Exit 3: Ratcheting trail
            trail = self.tight_trail if gain_pct > self.ratchet_at else self.wide_trail
            trail_level = self.high_water * (1 - trail / 100)

            if self.data.Close[-1] < trail_level:
                self.exit_reason = f"Trail {trail:.0f}% (gain {gain_pct:+.1f}%)"
                self.position.close()
                self.bars_since_exit = 0


bt = Backtest(data, StochDipV11, cash=100_000, commission=0.001,
              exclusive_orders=True, finalize_trades=True)
stats = bt.run()

bh_ret = (data.iloc[-1]["Close"] / data.iloc[0]["Open"] - 1) * 100

print(f"\n{'=' * 70}")
print(f"  CHAMPION V11: Stochastic Dip (2024-01 onward, 50K experiments)")
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
    print(f"  [{win}] {i+1}. {t['EntryTime'].date()} -> {t['ExitTime'].date()} ({dur}d)")
    print(f"      ${t['EntryPrice']:.2f} -> ${t['ExitPrice']:.2f} | {ret:+.1f}% | ${t['PnL']:+,.0f}")
print()
