"""
YTD backtest of CHAMPION V16 (BBDip 2025 'The Compounder') on AU.
Refreshes data first, then filters to 2026-01-01 -> today.
"""
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils import fetch_data, load_data
import numpy as np
import talib
from backtesting import Backtest, Strategy

# Refresh data
print("Refreshing AU daily data...")
df, src = fetch_data("AU", timeframe="daily", years_back=2)
print(f"  Source: {src} | {len(df)} bars | {df.index[0].date()} -> {df.index[-1].date()}")

# Filter to YTD 2026
data = df[df.index >= "2026-01-01"].copy()
print(f"  YTD slice: {data.index[0].date()} -> {data.index[-1].date()} ({len(data)} bars)\n")


def calc_bb_lower(close, period, nbdev):
    _, _, lower = talib.BBANDS(close, timeperiod=period, nbdevup=nbdev, nbdevdn=nbdev)
    return lower

def calc_sma(close, period):
    return talib.SMA(close, timeperiod=period)

def calc_atr(high, low, close, period=14):
    return talib.ATR(high, low, close, timeperiod=period)


class BBDip2025V16(Strategy):
    bb_period = 11
    bb_std = 1.7
    sma_period = 54
    wide_trail = 34.5
    tight_trail = 11.9
    ratchet_at = 62.0
    profit_target = 32.0
    time_stop = 0
    cooldown = 3
    use_atr_trail = True
    atr_mult = 3.8

    def init(self):
        self.bb_lower = self.I(calc_bb_lower, self.data.Close, self.bb_period, self.bb_std)
        self.sma = self.I(calc_sma, self.data.Close, self.sma_period)
        self.atr = self.I(calc_atr, self.data.High, self.data.Low, self.data.Close, 14)
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
            price = self.data.Close[-1]
            gain_pct = (price / self.entry_price - 1) * 100
            if self.use_atr_trail and not np.isnan(self.atr[-1]) and self.atr[-1] > 0:
                atr_pct = (self.atr_mult * self.atr[-1] / price) * 100
                if gain_pct <= self.ratchet_at:
                    trail = min(atr_pct, self.wide_trail)
                else:
                    trail = min(atr_pct * 0.5, self.tight_trail)
                trail = max(trail, 3.0)
            else:
                trail = self.tight_trail if gain_pct > self.ratchet_at else self.wide_trail
            trail_level = self.high_water * (1 - trail / 100)
            if price < trail_level:
                self.position.close(); self.bars_since_exit = 0; return
            if gain_pct >= self.profit_target:
                self.position.close(); self.bars_since_exit = 0; return
            if self.time_stop > 0 and self.bars_in_trade >= self.time_stop:
                self.position.close(); self.bars_since_exit = 0; return


# IMPORTANT: BB(11) and SMA(54) need lookback. Use the full df for indicator warmup,
# then evaluate only the YTD window. Easier: pass enough history.
# We'll re-slice with a 60-bar buffer before 2026-01-01 so indicators are warm by Jan 2.
buffer_start = (df.index >= "2025-10-15")
data_with_warmup = df[buffer_start].copy()
print(f"Running with warmup: {data_with_warmup.index[0].date()} -> {data_with_warmup.index[-1].date()}\n")

bt = Backtest(data_with_warmup, BBDip2025V16, cash=100_000, commission=0.001,
              exclusive_orders=True, finalize_trades=True)
stats = bt.run()

# Compute YTD-only B&H from Jan 2 open
ytd = df[df.index >= "2026-01-01"]
bh_ret = (ytd.iloc[-1]["Close"] / ytd.iloc[0]["Open"] - 1) * 100

# Filter trades to 2026 entries only
trades_all = stats["_trades"]
ytd_trades = trades_all[trades_all["EntryTime"] >= "2026-01-01"].copy()

# Recompute strategy YTD return from those trades only (compounded)
equity = 100_000.0
for _, t in ytd_trades.iterrows():
    equity *= (1 + t["ReturnPct"])
ytd_strategy_return = (equity / 100_000 - 1) * 100

print("=" * 70)
print(f"  AU CHAMPION V16 — YTD BACKTEST (2026-01-01 -> {ytd.index[-1].date()})")
print("=" * 70)
print(f"  YTD bars:           {len(ytd)}")
print(f"  YTD trades taken:   {len(ytd_trades)}")
print(f"  Strategy YTD return: {ytd_strategy_return:+.1f}%   (compounded from YTD trades)")
print(f"  Buy & Hold YTD:      {bh_ret:+.1f}%")
print(f"  Alpha:               {ytd_strategy_return - bh_ret:+.1f}%")
print(f"  Final equity:        ${equity:,.0f}  (from $100K)")
print()
print(f"  (Full-window stats incl. warmup trades from late 2025:)")
print(f"  Sharpe:     {stats['Sharpe Ratio']:.2f}")
print(f"  Sortino:    {stats['Sortino Ratio']:.2f}")
print(f"  MaxDD:      {stats['Max. Drawdown [%]']:.1f}%")
print(f"  Win Rate:   {stats['Win Rate [%]']:.1f}%")
print(f"  Total trades (incl warmup): {stats['# Trades']}")
print("=" * 70)

print(f"\n  YTD TRADES (entries on/after 2026-01-01):")
if len(ytd_trades) == 0:
    print("    (none — strategy did not signal entry within YTD window)")
else:
    for i, t in ytd_trades.iterrows():
        dur = t["Duration"].days
        ret = t["ReturnPct"] * 100
        win = "W" if ret > 0 else "L"
        exit_status = "CLOSED" if not isinstance(t["ExitTime"], type(None)) else "OPEN"
        print(f"  {win} {t['EntryTime'].date()} -> {t['ExitTime'].date()} ({dur}d)")
        print(f"      ${t['EntryPrice']:.2f} -> ${t['ExitPrice']:.2f} | {ret:+.1f}% | ${t['PnL']:+,.0f}")
print()

# Current state
last_close = df.iloc[-1]["Close"]
last_date = df.index[-1].date()
in_pos = False
# Check if last trade is open (has no exit beyond data end)
if len(trades_all) > 0:
    last_trade = trades_all.iloc[-1]
    if last_trade["ExitTime"] >= df.index[-1]:
        in_pos = True
print(f"  Current: AU = ${last_close:.2f} on {last_date}")
print(f"  Strategy state at last bar: {'IN POSITION' if in_pos else 'FLAT'}")
