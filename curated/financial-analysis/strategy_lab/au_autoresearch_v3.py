"""
AU Autoresearch V3 — Karpathy Loop Iteration 3.

INSIGHT FROM V2: 20% trail from peak gives 316% if entered on day 1.
V2 failed because EMA crossover enters TOO LATE (weeks after the move starts).

V3 HYPOTHESIS:
1. Ultra-fast entry — buy within 1-3 days (minimal confirmation)
2. 20% trailing stop from high-water mark
3. Instant re-entry after stop-out (no waiting for slow EMA cross)
4. Test trail widths 18-25% systematically
"""

import sys, os, json, time, itertools, hashlib
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
import talib
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import warnings
warnings.filterwarnings("ignore")

# ═══════════════════════════════════════════════════════════
#  DATA
# ═══════════════════════════════════════════════════════════

def load_au_2025():
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "au_daily.csv")
    df = pd.read_csv(csv_path, index_col=0, parse_dates=True)
    try:
        df.index = pd.to_datetime(df.index, utc=True).tz_localize(None)
    except Exception:
        df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()
    df = df.loc["2025-01-01":]
    return df

DATA = load_au_2025()
BH_RETURN = (DATA.iloc[-1]["Close"] / DATA.iloc[0]["Open"] - 1) * 100
PEAK_PRICE = DATA["Close"].max()
CASH = 100_000

print(f"═══════════════════════════════════════════════════════════")
print(f"  AU AUTORESEARCH V3 — 'FAST IN, WIDE TRAIL'")
print(f"  Data: {DATA.index[0].date()} → {DATA.index[-1].date()} ({len(DATA)} bars)")
print(f"  B&H: {BH_RETURN:.1f}% | Peak: ${PEAK_PRICE:.2f}")
print(f"═══════════════════════════════════════════════════════════\n")

# ═══════════════════════════════════════════════════════════
#  INDICATOR FUNCTIONS
# ═══════════════════════════════════════════════════════════

def calc_ema(close, period):
    return talib.EMA(close, timeperiod=period)

def calc_sma(close, period):
    return talib.SMA(close, timeperiod=period)

def calc_rsi(close, period):
    return talib.RSI(close, timeperiod=period)

def calc_atr(high, low, close, period):
    return talib.ATR(high, low, close, timeperiod=period)

def calc_adx(high, low, close, period):
    return talib.ADX(high, low, close, timeperiod=period)

def calc_macd_line(close, fast, slow, signal):
    m, s, h = talib.MACD(close, fastperiod=fast, slowperiod=slow, signalperiod=signal)
    return m

def calc_macd_signal(close, fast, slow, signal):
    m, s, h = talib.MACD(close, fastperiod=fast, slowperiod=slow, signalperiod=signal)
    return s


# ═══════════════════════════════════════════════════════════
#  V3 STRATEGIES — FAST ENTRY + WIDE TRAIL
# ═══════════════════════════════════════════════════════════

class InstantRider(Strategy):
    """The simplest possible: buy when price > EMA(N), sell on % trail.
    Ultra-fast EMA (3-7) means entry within 1-2 days of any move."""
    ema_entry = 5       # Very fast EMA — triggers almost immediately
    trail_pct = 20.0    # Wide trail to survive all pullbacks
    cooldown = 0        # Bars to wait after stop-out before re-entering

    def init(self):
        self.ema = self.I(calc_ema, self.data.Close, self.ema_entry)
        self.high_water = 0
        self.bars_since_exit = 999

    def next(self):
        if np.isnan(self.ema[-1]):
            return

        if not self.position:
            self.bars_since_exit += 1
            if self.data.Close[-1] > self.ema[-1] and self.bars_since_exit > self.cooldown:
                self.buy()
                self.high_water = self.data.Close[-1]
        else:
            self.high_water = max(self.high_water, self.data.Close[-1])
            trail_level = self.high_water * (1 - self.trail_pct / 100)
            if self.data.Close[-1] < trail_level:
                self.position.close()
                self.bars_since_exit = 0


class RSIInstantRider(Strategy):
    """Buy when RSI > threshold (very low bar), sell on % trail.
    RSI(5) > 40 would trigger almost immediately in any bullish environment."""
    rsi_period = 5
    rsi_entry = 40      # Low bar — just needs to not be deeply oversold
    trail_pct = 20.0
    cooldown = 2

    def init(self):
        self.rsi = self.I(calc_rsi, self.data.Close, self.rsi_period)
        self.high_water = 0
        self.bars_since_exit = 999

    def next(self):
        if np.isnan(self.rsi[-1]):
            return

        if not self.position:
            self.bars_since_exit += 1
            if self.rsi[-1] > self.rsi_entry and self.bars_since_exit > self.cooldown:
                self.buy()
                self.high_water = self.data.Close[-1]
        else:
            self.high_water = max(self.high_water, self.data.Close[-1])
            trail_level = self.high_water * (1 - self.trail_pct / 100)
            if self.data.Close[-1] < trail_level:
                self.position.close()
                self.bars_since_exit = 0


class GreenBarRider(Strategy):
    """Buy on N consecutive green (up) bars, sell on % trail.
    2 green bars = enter. Fastest possible confirmation."""
    green_bars = 2      # Just 2 up days to confirm
    trail_pct = 20.0
    cooldown = 2
    ema_sanity = 10     # Must be above this EMA (sanity check)

    def init(self):
        self.ema = self.I(calc_ema, self.data.Close, self.ema_sanity)
        self.high_water = 0
        self.bars_since_exit = 999

    def next(self):
        if np.isnan(self.ema[-1]):
            return
        if len(self.data.Close) < self.green_bars + 1:
            return

        if not self.position:
            self.bars_since_exit += 1
            # Count consecutive green bars
            green_count = 0
            for i in range(1, self.green_bars + 1):
                if self.data.Close[-i] > self.data.Open[-i]:
                    green_count += 1
                else:
                    break

            above_ema = self.data.Close[-1] > self.ema[-1]
            if green_count >= self.green_bars and above_ema and self.bars_since_exit > self.cooldown:
                self.buy()
                self.high_water = self.data.Close[-1]
        else:
            self.high_water = max(self.high_water, self.data.Close[-1])
            trail_level = self.high_water * (1 - self.trail_pct / 100)
            if self.data.Close[-1] < trail_level:
                self.position.close()
                self.bars_since_exit = 0


class MACDFastRider(Strategy):
    """MACD with FAST settings (5/13/4) for quick signal + wide trail.
    Standard MACD(12/26/9) is too slow. This fires within days."""
    macd_fast = 5
    macd_slow = 13
    macd_signal = 4
    trail_pct = 20.0
    cooldown = 1

    def init(self):
        self.macd = self.I(calc_macd_line, self.data.Close, self.macd_fast, self.macd_slow, self.macd_signal)
        self.macd_sig = self.I(calc_macd_signal, self.data.Close, self.macd_fast, self.macd_slow, self.macd_signal)
        self.high_water = 0
        self.bars_since_exit = 999

    def next(self):
        if np.isnan(self.macd[-1]):
            return

        if not self.position:
            self.bars_since_exit += 1
            if crossover(self.macd, self.macd_sig) and self.bars_since_exit > self.cooldown:
                self.buy()
                self.high_water = self.data.Close[-1]
        else:
            self.high_water = max(self.high_water, self.data.Close[-1])
            trail_level = self.high_water * (1 - self.trail_pct / 100)
            if self.data.Close[-1] < trail_level:
                self.position.close()
                self.bars_since_exit = 0


class AdaptiveTrailRider(Strategy):
    """Fast entry + ADAPTIVE trail: trail tightens as price extends.
    Start with 25% trail, tighten to 15% when price > 3x entry.
    This captures the explosive move but tightens profit protection."""
    ema_entry = 5
    initial_trail = 25.0
    tight_trail = 15.0
    tighten_mult = 3.0   # Tighten when price > N * entry_price
    cooldown = 2

    def init(self):
        self.ema = self.I(calc_ema, self.data.Close, self.ema_entry)
        self.high_water = 0
        self.entry_price = 0
        self.bars_since_exit = 999

    def next(self):
        if np.isnan(self.ema[-1]):
            return

        if not self.position:
            self.bars_since_exit += 1
            if self.data.Close[-1] > self.ema[-1] and self.bars_since_exit > self.cooldown:
                self.buy()
                self.high_water = self.data.Close[-1]
                self.entry_price = self.data.Close[-1]
        else:
            self.high_water = max(self.high_water, self.data.Close[-1])

            # Adaptive trail: tighten when price has moved a lot
            if self.entry_price > 0 and self.data.Close[-1] > self.tighten_mult * self.entry_price:
                trail = self.tight_trail
            else:
                trail = self.initial_trail

            trail_level = self.high_water * (1 - trail / 100)
            if self.data.Close[-1] < trail_level:
                self.position.close()
                self.bars_since_exit = 0


class DualEMAFastRider(Strategy):
    """Fast EMA cross (3/8) for entry + percent trail exit.
    The fastest EMA cross that still has some signal quality."""
    ema_fast = 3
    ema_slow = 8
    trail_pct = 20.0
    cooldown = 1

    def init(self):
        self.ema_f = self.I(calc_ema, self.data.Close, self.ema_fast)
        self.ema_s = self.I(calc_ema, self.data.Close, self.ema_slow)
        self.high_water = 0
        self.bars_since_exit = 999

    def next(self):
        if np.isnan(self.ema_f[-1]) or np.isnan(self.ema_s[-1]):
            return

        if not self.position:
            self.bars_since_exit += 1
            # Enter on cross OR when already above (instant re-entry)
            cross = crossover(self.ema_f, self.ema_s)
            above = self.ema_f[-1] > self.ema_s[-1]
            if (cross or (above and self.bars_since_exit > self.cooldown)):
                self.buy()
                self.high_water = self.data.Close[-1]
        else:
            self.high_water = max(self.high_water, self.data.Close[-1])
            trail_level = self.high_water * (1 - self.trail_pct / 100)
            if self.data.Close[-1] < trail_level:
                self.position.close()
                self.bars_since_exit = 0


class VolatilityAdaptiveRider(Strategy):
    """Entry: fast EMA. Trail: ATR-scaled percentage.
    During high vol (big ATR), trail widens automatically.
    During low vol, trail tightens. Best of both worlds."""
    ema_entry = 5
    atr_period = 14
    trail_atr_mult = 3.5  # trail = N * ATR as % of price
    min_trail_pct = 12.0
    max_trail_pct = 30.0
    cooldown = 2

    def init(self):
        self.ema = self.I(calc_ema, self.data.Close, self.ema_entry)
        self.atr = self.I(calc_atr, self.data.High, self.data.Low, self.data.Close, self.atr_period)
        self.high_water = 0
        self.bars_since_exit = 999

    def next(self):
        if np.isnan(self.ema[-1]) or np.isnan(self.atr[-1]):
            return

        if not self.position:
            self.bars_since_exit += 1
            if self.data.Close[-1] > self.ema[-1] and self.bars_since_exit > self.cooldown:
                self.buy()
                self.high_water = self.data.Close[-1]
        else:
            self.high_water = max(self.high_water, self.data.Close[-1])

            # ATR-scaled trail %
            atr_pct = (self.trail_atr_mult * self.atr[-1]) / self.data.Close[-1] * 100
            trail = max(self.min_trail_pct, min(self.max_trail_pct, atr_pct))

            trail_level = self.high_water * (1 - trail / 100)
            if self.data.Close[-1] < trail_level:
                self.position.close()
                self.bars_since_exit = 0


# ═══════════════════════════════════════════════════════════
#  PARAMETER SPACE
# ═══════════════════════════════════════════════════════════

PARAM_SPACE = {
    "InstantRider": {
        "ema_entry": [3, 5, 7, 8, 10],
        "trail_pct": [16, 18, 19, 20, 21, 22, 23, 25],
        "cooldown": [0, 1, 2, 3, 5],
    },
    "RSIInstantRider": {
        "rsi_period": [3, 5, 7, 10],
        "rsi_entry": [30, 35, 40, 45, 50],
        "trail_pct": [18, 19, 20, 21, 22, 25],
        "cooldown": [0, 1, 2, 3],
    },
    "GreenBarRider": {
        "green_bars": [1, 2, 3],
        "trail_pct": [18, 19, 20, 21, 22, 25],
        "cooldown": [0, 1, 2, 3],
        "ema_sanity": [5, 8, 10, 15],
    },
    "MACDFastRider": {
        "macd_fast": [3, 5, 6, 8],
        "macd_slow": [10, 13, 15, 17],
        "macd_signal": [3, 4, 5],
        "trail_pct": [18, 19, 20, 21, 22, 25],
        "cooldown": [0, 1, 2, 3],
    },
    "AdaptiveTrailRider": {
        "ema_entry": [3, 5, 7],
        "initial_trail": [20, 22, 25, 28],
        "tight_trail": [12, 14, 15, 17],
        "tighten_mult": [2.0, 2.5, 3.0, 3.5, 4.0],
        "cooldown": [0, 1, 2, 3],
    },
    "DualEMAFastRider": {
        "ema_fast": [2, 3, 4, 5],
        "ema_slow": [6, 8, 10, 12],
        "trail_pct": [18, 19, 20, 21, 22, 25],
        "cooldown": [0, 1, 2, 3],
    },
    "VolatilityAdaptiveRider": {
        "ema_entry": [3, 5, 7],
        "trail_atr_mult": [2.5, 3.0, 3.5, 4.0, 4.5, 5.0],
        "min_trail_pct": [10, 12, 15],
        "max_trail_pct": [25, 28, 30],
        "cooldown": [0, 1, 2, 3],
    },
}

STRATEGY_CLASSES = {
    "InstantRider": InstantRider,
    "RSIInstantRider": RSIInstantRider,
    "GreenBarRider": GreenBarRider,
    "MACDFastRider": MACDFastRider,
    "AdaptiveTrailRider": AdaptiveTrailRider,
    "DualEMAFastRider": DualEMAFastRider,
    "VolatilityAdaptiveRider": VolatilityAdaptiveRider,
}


# ═══════════════════════════════════════════════════════════
#  FITNESS
# ═══════════════════════════════════════════════════════════

def compute_fitness(stats):
    ret = stats.get("Return [%]", 0)
    sharpe = stats.get("Sharpe Ratio", 0) or 0
    max_dd = abs(stats.get("Max. Drawdown [%]", -100))
    win_rate = stats.get("Win Rate [%]", 0) or 0
    n_trades = stats.get("# Trades", 0)

    if n_trades < 2:
        return -9999

    sharpe_cap = min(max(sharpe, 0), 4.0)
    dd_penalty = max(max_dd, 5)

    fitness = ret * (1 + sharpe_cap) * (1 + win_rate / 100) / dd_penalty

    if ret > BH_RETURN:
        fitness *= 3.0

    return round(fitness, 2)


def run_experiment(strategy_class, params):
    try:
        bt = Backtest(DATA, strategy_class, cash=CASH, commission=0.001,
                      exclusive_orders=True, finalize_trades=True)
        stats = bt.run(**params)
        fitness = compute_fitness(stats)

        # Also capture equity curve peaks for analysis
        eq = stats._equity_curve
        eq_peak = eq["Equity"].max()
        eq_final = stats["Equity Final [$]"]

        return {
            "return": round(stats["Return [%]"], 1),
            "sharpe": round(stats["Sharpe Ratio"] or 0, 2),
            "max_dd": round(stats["Max. Drawdown [%]"], 1),
            "win_rate": round(stats["Win Rate [%]"] or 0, 1),
            "trades": stats["# Trades"],
            "equity_final": round(eq_final, 0),
            "equity_peak": round(eq_peak, 0),
            "fitness": fitness,
            "sortino": round(stats["Sortino Ratio"] or 0, 2),
        }
    except Exception as e:
        return {"error": str(e), "fitness": -9999}


def generate_param_combos(archetype_name, max_combos=250):
    import random
    space = PARAM_SPACE[archetype_name]
    keys = sorted(space.keys())
    values = [space[k] for k in keys]

    total = 1
    for v in values:
        total *= len(v)

    if total <= max_combos:
        return [dict(zip(keys, vals)) for vals in itertools.product(*values)]
    else:
        combos = set()
        attempts = 0
        while len(combos) < max_combos and attempts < max_combos * 10:
            vals = tuple(random.choice(v) for v in values)
            combos.add(vals)
            attempts += 1
        return [dict(zip(keys, vals)) for vals in combos]


# ═══════════════════════════════════════════════════════════
#  MAIN LOOP
# ═══════════════════════════════════════════════════════════

def run_autoresearch():
    results = []
    experiment_count = 0
    start_time = time.time()

    print(f"TARGET: Beat B&H ({BH_RETURN:.1f}%) — enter fast, trail at 20%\n")

    # Phase 1: Broad sweep
    print("═══ PHASE 1: BROAD SWEEP — FAST ENTRY ARCHETYPES ═══")
    for arch_name, strat_class in STRATEGY_CLASSES.items():
        combos = generate_param_combos(arch_name, max_combos=250)
        print(f"\n  {arch_name}: {len(combos)} variants...")

        arch_results = []
        for params in combos:
            result = run_experiment(strat_class, params)
            result["archetype"] = arch_name
            result["params"] = params
            arch_results.append(result)
            experiment_count += 1

        arch_results.sort(key=lambda x: x["fitness"], reverse=True)

        for i, r in enumerate(arch_results[:5]):
            if "error" not in r:
                beat = "✓ B&H" if r["return"] > BH_RETURN else ""
                peak_str = f"Peak:${r.get('equity_peak', 0):,.0f}" if r.get("equity_peak") else ""
                print(f"    #{i+1} Ret:{r['return']:>7.1f}% Sharpe:{r['sharpe']:>5.2f} DD:{r['max_dd']:>6.1f}% WR:{r['win_rate']:>5.1f}% T:{r['trades']:>2} {peak_str} {beat}")

        results.extend(arch_results)

    # Phase 2: Deep optimization on top 5 archetypes
    print(f"\n═══ PHASE 2: DEEP OPTIMIZATION ═══")
    results.sort(key=lambda x: x["fitness"], reverse=True)

    top_archetypes = []
    seen = set()
    for r in results:
        if "error" not in r and r["archetype"] not in seen and r["fitness"] > 0:
            top_archetypes.append((r["archetype"], r["params"]))
            seen.add(r["archetype"])
            if len(top_archetypes) == 5:
                break

    for arch_name, best_params in top_archetypes:
        strat_class = STRATEGY_CLASSES[arch_name]
        print(f"\n  Fine-tuning {arch_name}...")

        fine_combos = []
        for key, val in best_params.items():
            if isinstance(val, (int, float)) and not isinstance(val, bool):
                for delta_pct in np.arange(-0.3, 0.31, 0.05):
                    new_params = best_params.copy()
                    new_val = val * (1 + delta_pct)
                    if isinstance(val, int):
                        new_val = max(1, int(round(new_val)))
                    else:
                        new_val = round(max(0.5, new_val), 1)
                    new_params[key] = new_val
                    fine_combos.append(new_params)

        # Also: cross key trails at 19, 19.5, 20, 20.5, 21
        if "trail_pct" in best_params:
            for tp in [18.5, 19.0, 19.5, 20.0, 20.5, 21.0, 21.5, 22.0]:
                new_params = best_params.copy()
                new_params["trail_pct"] = tp
                fine_combos.append(new_params)

        seen_hashes = set()
        unique_combos = []
        for c in fine_combos:
            h = hashlib.md5(json.dumps(c, sort_keys=True, default=str).encode()).hexdigest()
            if h not in seen_hashes:
                seen_hashes.add(h)
                unique_combos.append(c)

        print(f"  {len(unique_combos)} fine variants...")
        for params in unique_combos:
            result = run_experiment(strat_class, params)
            result["archetype"] = arch_name
            result["params"] = params
            results.append(result)
            experiment_count += 1

    # ═══ FINAL RANKING ═══
    results.sort(key=lambda x: x["fitness"], reverse=True)
    valid = [r for r in results if "error" not in r and r["fitness"] > 0]

    elapsed = time.time() - start_time

    # Deduplicate by return+sharpe+trades (many combos converge to same result)
    deduped = []
    seen_sigs = set()
    for r in valid:
        sig = (r["return"], r["sharpe"], r["trades"], r["max_dd"])
        if sig not in seen_sigs:
            seen_sigs.add(sig)
            deduped.append(r)

    print(f"\n{'═' * 85}")
    print(f"  AUTORESEARCH V3 COMPLETE")
    print(f"  Experiments: {experiment_count} | Time: {elapsed:.1f}s | Rate: {experiment_count/elapsed:.1f}/s")
    print(f"  Buy & Hold: {BH_RETURN:.1f}%")
    print(f"{'═' * 85}\n")

    print(f"  TOP 30 (deduplicated):\n")
    print(f"  {'#':>3} {'Archetype':<24} {'Return':>8} {'Sharpe':>7} {'MaxDD':>7} {'WR':>6} {'T':>3} {'EqPeak':>10} {'Fitness':>9} {'B&H':>4}")
    print(f"  {'─' * 90}")

    for i, r in enumerate(deduped[:30]):
        beat = "✓" if r["return"] > BH_RETURN else " "
        peak = f"${r.get('equity_peak', 0):>8,.0f}"
        print(f"  {i+1:>3} {r['archetype']:<24} {r['return']:>7.1f}% {r['sharpe']:>6.2f} {r['max_dd']:>6.1f}% {r['win_rate']:>5.1f}% {r['trades']:>3} {peak} {r['fitness']:>9.1f} {beat:>3}")

    # Count B&H beaters
    beaters = [r for r in deduped if r["return"] > BH_RETURN]
    print(f"\n  B&H Beaters: {len(beaters)} / {len(deduped)} strategies")

    # Save
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "au_autoresearch_v3_results.json")
    with open(output_path, "w") as f:
        json.dump({
            "meta": {
                "version": 3,
                "experiments": experiment_count,
                "elapsed_s": round(elapsed, 1),
                "bh_return": round(BH_RETURN, 1),
                "data_range": f"{DATA.index[0].date()} to {DATA.index[-1].date()}",
                "timestamp": datetime.now().isoformat(),
            },
            "top_strategies": deduped[:50],
        }, f, indent=2, default=str)
    print(f"\n  Results → {output_path}")

    # Champion
    if deduped:
        best = deduped[0]
        print(f"\n{'═' * 85}")
        print(f"  CHAMPION: {best['archetype']}")
        print(f"  Return: {best['return']}% | Sharpe: {best['sharpe']} | MaxDD: {best['max_dd']}%")
        print(f"  WR: {best['win_rate']}% | Trades: {best['trades']} | Equity Peak: ${best.get('equity_peak', 0):,.0f}")
        print(f"  Params: {json.dumps(best['params'], indent=4)}")
        vs_bh = best['return'] - BH_RETURN
        print(f"  vs B&H: {'+' if vs_bh > 0 else ''}{vs_bh:.1f}%")
        print(f"{'═' * 85}")

    return deduped


if __name__ == "__main__":
    run_autoresearch()
