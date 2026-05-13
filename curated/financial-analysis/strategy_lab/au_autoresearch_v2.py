"""
AU Autoresearch V2 — Karpathy Loop Iteration 2.

HYPOTHESIS: V1 strategies exit too early. The 285% B&H works because it NEVER exits.
This iteration focuses on:
1. Percent-based trailing stops (not ATR — ATR tightens in low vol, shaking you out)
2. NO RSI/oscillator exits (these cut winners during parabolic moves)
3. Pyramiding — add to winners on pullbacks
4. Trend-riding — stay in as long as price > moving average
5. Chandelier exits — high-water mark based stops
"""

import sys, os, json, time, itertools, hashlib
from datetime import datetime
from copy import deepcopy

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
PEAK_DATE = DATA["Close"].idxmax()
CASH = 100_000

print(f"═══════════════════════════════════════════════════════════")
print(f"  AU AUTORESEARCH V2 — 'STAY IN THE TRADE'")
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

def calc_plus_di(high, low, close, period):
    return talib.PLUS_DI(high, low, close, timeperiod=period)

def calc_minus_di(high, low, close, period):
    return talib.MINUS_DI(high, low, close, timeperiod=period)

def calc_macd_line(close, fast, slow, signal):
    m, s, h = talib.MACD(close, fastperiod=fast, slowperiod=slow, signalperiod=signal)
    return m

def calc_macd_signal(close, fast, slow, signal):
    m, s, h = talib.MACD(close, fastperiod=fast, slowperiod=slow, signalperiod=signal)
    return s

def calc_bb_lower(close, period, nbdev):
    u, m, l = talib.BBANDS(close, timeperiod=period, nbdevup=nbdev, nbdevdn=nbdev)
    return l

def calc_bb_middle(close, period, nbdev):
    u, m, l = talib.BBANDS(close, timeperiod=period, nbdevup=nbdev, nbdevdn=nbdev)
    return m


# ═══════════════════════════════════════════════════════════
#  NEW STRATEGY ARCHETYPES — "RIDE THE WAVE"
# ═══════════════════════════════════════════════════════════

class PercentTrailRider(Strategy):
    """Enter on EMA cross, exit ONLY on percent-based trailing stop.
    No oscillator exit. The trail is a % from highest close since entry."""
    ema_fast = 8
    ema_slow = 21
    trail_pct = 15.0  # Exit if price drops X% from peak
    adx_period = 14
    adx_thresh = 18

    def init(self):
        self.ema_f = self.I(calc_ema, self.data.Close, self.ema_fast)
        self.ema_s = self.I(calc_ema, self.data.Close, self.ema_slow)
        self.adx = self.I(calc_adx, self.data.High, self.data.Low, self.data.Close, self.adx_period)
        self.high_water = 0

    def next(self):
        if np.isnan(self.ema_f[-1]) or np.isnan(self.adx[-1]):
            return

        if not self.position:
            if crossover(self.ema_f, self.ema_s) and self.adx[-1] > self.adx_thresh:
                self.buy()
                self.high_water = self.data.Close[-1]
        else:
            self.high_water = max(self.high_water, self.data.Close[-1])
            trail_level = self.high_water * (1 - self.trail_pct / 100)
            if self.data.Close[-1] < trail_level:
                self.position.close()


class EMAFloorRider(Strategy):
    """Stay long as long as price is above a slow EMA. Simple and powerful.
    Enter: fast EMA > slow EMA. Exit: close below floor EMA."""
    ema_fast = 8
    ema_floor = 50  # The floor — exit when price breaks below
    reentry_buffer = 1.02  # Must be X% above floor to re-enter

    def init(self):
        self.ema_f = self.I(calc_ema, self.data.Close, self.ema_fast)
        self.ema_fl = self.I(calc_ema, self.data.Close, self.ema_floor)

    def next(self):
        if np.isnan(self.ema_f[-1]) or np.isnan(self.ema_fl[-1]):
            return

        if not self.position:
            above_floor = self.data.Close[-1] > self.ema_fl[-1] * self.reentry_buffer
            ema_bullish = self.ema_f[-1] > self.ema_fl[-1]
            if above_floor and ema_bullish:
                self.buy()
        else:
            if self.data.Close[-1] < self.ema_fl[-1]:
                self.position.close()


class ChandelierRider(Strategy):
    """Chandelier exit: trail from highest high by N * ATR.
    But with a WIDE multiplier so it doesn't shake out during consolidation."""
    ema_fast = 10
    ema_slow = 30
    atr_period = 14
    chandelier_mult = 4.0  # Wide! Standard is 3.0
    lookback = 22  # Highest high over N bars

    def init(self):
        self.ema_f = self.I(calc_ema, self.data.Close, self.ema_fast)
        self.ema_s = self.I(calc_ema, self.data.Close, self.ema_slow)
        self.atr = self.I(calc_atr, self.data.High, self.data.Low, self.data.Close, self.atr_period)

    def next(self):
        if np.isnan(self.ema_f[-1]) or np.isnan(self.atr[-1]):
            return
        if len(self.data.Close) < self.lookback + 1:
            return

        if not self.position:
            if crossover(self.ema_f, self.ema_s):
                self.buy()
        else:
            highest = max(self.data.High[-self.lookback:])
            chandelier_stop = highest - self.chandelier_mult * self.atr[-1]
            if self.data.Close[-1] < chandelier_stop:
                self.position.close()


class PyramidTrendRider(Strategy):
    """Enter initial position on trend signal, ADD on pullbacks.
    Uses size parameter to control position scaling.
    Exit only on percent trail from portfolio high-water mark."""
    ema_fast = 8
    ema_slow = 30
    rsi_period = 14
    rsi_pullback = 40  # Add when RSI dips to this level in uptrend
    trail_pct = 12.0
    max_units = 3  # Max position units

    def init(self):
        self.ema_f = self.I(calc_ema, self.data.Close, self.ema_fast)
        self.ema_s = self.I(calc_ema, self.data.Close, self.ema_slow)
        self.rsi = self.I(calc_rsi, self.data.Close, self.rsi_period)
        self.high_water = 0
        self.units = 0

    def next(self):
        if np.isnan(self.ema_f[-1]) or np.isnan(self.rsi[-1]):
            return

        uptrend = self.ema_f[-1] > self.ema_s[-1]

        if not self.position:
            if uptrend and crossover(self.ema_f, self.ema_s):
                size = 1.0 / self.max_units
                self.buy(size=size)
                self.high_water = self.data.Close[-1]
                self.units = 1
        else:
            self.high_water = max(self.high_water, self.data.Close[-1])

            # Pyramid: add on RSI pullback while still in uptrend
            if uptrend and self.units < self.max_units and self.rsi[-1] < self.rsi_pullback:
                size = 1.0 / self.max_units
                self.buy(size=size)
                self.units += 1

            # Exit: percent trail from high water
            trail_level = self.high_water * (1 - self.trail_pct / 100)
            if self.data.Close[-1] < trail_level:
                self.position.close()
                self.units = 0


class MACDTrendStayer(Strategy):
    """MACD entry, but exit ONLY on percent trail, not MACD cross down.
    V1 showed MACD entries are good but MACD exits kill winners."""
    macd_fast = 8
    macd_slow = 21
    macd_signal = 9
    ema_filter = 30
    trail_pct = 15.0

    def init(self):
        self.macd = self.I(calc_macd_line, self.data.Close, self.macd_fast, self.macd_slow, self.macd_signal)
        self.macd_sig = self.I(calc_macd_signal, self.data.Close, self.macd_fast, self.macd_slow, self.macd_signal)
        self.ema = self.I(calc_ema, self.data.Close, self.ema_filter)
        self.high_water = 0

    def next(self):
        if np.isnan(self.macd[-1]) or np.isnan(self.ema[-1]):
            return

        if not self.position:
            if crossover(self.macd, self.macd_sig) and self.data.Close[-1] > self.ema[-1]:
                self.buy()
                self.high_water = self.data.Close[-1]
        else:
            self.high_water = max(self.high_water, self.data.Close[-1])
            trail_level = self.high_water * (1 - self.trail_pct / 100)
            if self.data.Close[-1] < trail_level:
                self.position.close()


class BBDipTrendStayer(Strategy):
    """Buy Bollinger Band dips in uptrend. Never sell on oscillator.
    Exit only on percent trail or EMA breakdown."""
    bb_period = 20
    bb_std = 2.0
    ema_trend = 50
    trail_pct = 15.0

    def init(self):
        self.bb_lower = self.I(calc_bb_lower, self.data.Close, self.bb_period, self.bb_std)
        self.ema = self.I(calc_ema, self.data.Close, self.ema_trend)
        self.high_water = 0

    def next(self):
        if np.isnan(self.bb_lower[-1]) or np.isnan(self.ema[-1]):
            return

        if not self.position:
            uptrend = self.data.Close[-1] > self.ema[-1]
            at_band = self.data.Close[-1] <= self.bb_lower[-1]
            if uptrend and at_band:
                self.buy()
                self.high_water = self.data.Close[-1]
        else:
            self.high_water = max(self.high_water, self.data.Close[-1])
            trail_level = self.high_water * (1 - self.trail_pct / 100)
            if self.data.Close[-1] < trail_level:
                self.position.close()


class ADXPowerTrend(Strategy):
    """Only enter when ADX shows STRONG trend (>25), ride with wide trail.
    +DI > -DI confirms direction. Exit on trail or ADX collapse."""
    adx_period = 14
    adx_entry = 25
    adx_exit = 15  # Exit if trend weakens below this
    ema_period = 21
    trail_pct = 18.0

    def init(self):
        self.adx = self.I(calc_adx, self.data.High, self.data.Low, self.data.Close, self.adx_period)
        self.plus_di = self.I(calc_plus_di, self.data.High, self.data.Low, self.data.Close, self.adx_period)
        self.minus_di = self.I(calc_minus_di, self.data.High, self.data.Low, self.data.Close, self.adx_period)
        self.ema = self.I(calc_ema, self.data.Close, self.ema_period)
        self.high_water = 0

    def next(self):
        if np.isnan(self.adx[-1]) or np.isnan(self.ema[-1]):
            return

        if not self.position:
            strong_trend = self.adx[-1] > self.adx_entry
            bullish = self.plus_di[-1] > self.minus_di[-1]
            above_ema = self.data.Close[-1] > self.ema[-1]
            if strong_trend and bullish and above_ema:
                self.buy()
                self.high_water = self.data.Close[-1]
        else:
            self.high_water = max(self.high_water, self.data.Close[-1])
            trail_level = self.high_water * (1 - self.trail_pct / 100)
            trend_dead = self.adx[-1] < self.adx_exit
            if self.data.Close[-1] < trail_level or trend_dead:
                self.position.close()


class HybridStayer(Strategy):
    """Best of V1 MomentumRider entry + V2 percent trail exit.
    RSI entry but NO RSI exit. MACD confirmation. Wide percent trail."""
    rsi_period = 14
    rsi_entry = 50
    macd_fast = 12
    macd_slow = 26
    macd_signal = 9
    trail_pct = 15.0
    ema_filter = 30

    def init(self):
        self.rsi = self.I(calc_rsi, self.data.Close, self.rsi_period)
        self.macd = self.I(calc_macd_line, self.data.Close, self.macd_fast, self.macd_slow, self.macd_signal)
        self.macd_sig = self.I(calc_macd_signal, self.data.Close, self.macd_fast, self.macd_slow, self.macd_signal)
        self.ema = self.I(calc_ema, self.data.Close, self.ema_filter)
        self.high_water = 0

    def next(self):
        if np.isnan(self.rsi[-1]) or np.isnan(self.macd[-1]) or np.isnan(self.ema[-1]):
            return

        if not self.position:
            rsi_ok = self.rsi[-1] > self.rsi_entry
            macd_bull = self.macd[-1] > self.macd_sig[-1]
            above_ema = self.data.Close[-1] > self.ema[-1]
            if rsi_ok and macd_bull and above_ema:
                self.buy()
                self.high_water = self.data.Close[-1]
        else:
            self.high_water = max(self.high_water, self.data.Close[-1])
            trail_level = self.high_water * (1 - self.trail_pct / 100)
            if self.data.Close[-1] < trail_level:
                self.position.close()


# ═══════════════════════════════════════════════════════════
#  PARAMETER SPACE
# ═══════════════════════════════════════════════════════════

PARAM_SPACE = {
    "PercentTrailRider": {
        "ema_fast": [5, 8, 10, 13],
        "ema_slow": [15, 21, 30],
        "trail_pct": [8, 10, 12, 15, 18, 20, 25],
        "adx_thresh": [12, 15, 18, 20, 25],
    },
    "EMAFloorRider": {
        "ema_fast": [5, 8, 10, 13, 15],
        "ema_floor": [20, 30, 40, 50, 60],
        "reentry_buffer": [1.0, 1.01, 1.02, 1.03, 1.05],
    },
    "ChandelierRider": {
        "ema_fast": [5, 8, 10],
        "ema_slow": [20, 30, 40],
        "chandelier_mult": [3.0, 3.5, 4.0, 4.5, 5.0, 6.0],
        "lookback": [14, 22, 30, 44],
    },
    "PyramidTrendRider": {
        "ema_fast": [5, 8, 10],
        "ema_slow": [20, 30, 40],
        "rsi_pullback": [30, 35, 40, 45],
        "trail_pct": [10, 12, 15, 18, 20],
        "max_units": [2, 3, 4],
    },
    "MACDTrendStayer": {
        "macd_fast": [6, 8, 10, 12],
        "macd_slow": [17, 21, 26],
        "macd_signal": [7, 9],
        "ema_filter": [15, 21, 30, 40],
        "trail_pct": [10, 12, 15, 18, 20, 25],
    },
    "BBDipTrendStayer": {
        "bb_period": [15, 20, 25],
        "bb_std": [1.5, 2.0, 2.5],
        "ema_trend": [20, 30, 40, 50],
        "trail_pct": [10, 12, 15, 18, 20, 25],
    },
    "ADXPowerTrend": {
        "adx_entry": [20, 25, 30],
        "adx_exit": [10, 12, 15, 18],
        "ema_period": [15, 21, 30],
        "trail_pct": [12, 15, 18, 20, 25],
    },
    "HybridStayer": {
        "rsi_entry": [40, 45, 50, 55],
        "macd_fast": [8, 12],
        "macd_slow": [21, 26],
        "ema_filter": [15, 21, 30],
        "trail_pct": [10, 12, 15, 18, 20, 25],
    },
}

STRATEGY_CLASSES = {
    "PercentTrailRider": PercentTrailRider,
    "EMAFloorRider": EMAFloorRider,
    "ChandelierRider": ChandelierRider,
    "PyramidTrendRider": PyramidTrendRider,
    "MACDTrendStayer": MACDTrendStayer,
    "BBDipTrendStayer": BBDipTrendStayer,
    "ADXPowerTrend": ADXPowerTrend,
    "HybridStayer": HybridStayer,
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
        fitness *= 3.0  # Big bonus for beating B&H

    return round(fitness, 2)


# ═══════════════════════════════════════════════════════════
#  EXPERIMENT RUNNER
# ═══════════════════════════════════════════════════════════

def run_experiment(strategy_class, params):
    try:
        bt = Backtest(DATA, strategy_class, cash=CASH, commission=0.001,
                      exclusive_orders=True, finalize_trades=True)
        stats = bt.run(**params)
        fitness = compute_fitness(stats)

        return {
            "return": round(stats["Return [%]"], 1),
            "sharpe": round(stats["Sharpe Ratio"] or 0, 2),
            "max_dd": round(stats["Max. Drawdown [%]"], 1),
            "win_rate": round(stats["Win Rate [%]"] or 0, 1),
            "trades": stats["# Trades"],
            "equity_final": round(stats["Equity Final [$]"], 0),
            "fitness": fitness,
            "sortino": round(stats["Sortino Ratio"] or 0, 2),
        }
    except Exception as e:
        return {"error": str(e), "fitness": -9999}


def generate_param_combos(archetype_name, max_combos=200):
    import random
    space = PARAM_SPACE[archetype_name]
    keys = sorted(space.keys())
    values = [space[k] for k in keys]

    total = 1
    for v in values:
        total *= len(v)

    if total <= max_combos:
        combos = []
        for vals in itertools.product(*values):
            combos.append(dict(zip(keys, vals)))
        return combos
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

    print(f"TARGET: Beat B&H ({BH_RETURN:.1f}%) with good Sharpe & controlled DD\n")

    # Phase 1: Broad sweep
    print("═══ PHASE 1: BROAD SWEEP — 'STAY IN THE TRADE' ARCHETYPES ═══")
    for arch_name, strat_class in STRATEGY_CLASSES.items():
        combos = generate_param_combos(arch_name, max_combos=200)
        print(f"\n  {arch_name}: {len(combos)} variants...")

        arch_results = []
        for params in combos:
            result = run_experiment(strat_class, params)
            result["archetype"] = arch_name
            result["params"] = params
            arch_results.append(result)
            experiment_count += 1

        arch_results.sort(key=lambda x: x["fitness"], reverse=True)

        for i, r in enumerate(arch_results[:3]):
            if "error" not in r:
                beat = "✓ BEATS B&H" if r["return"] > BH_RETURN else ""
                print(f"    #{i+1} Ret:{r['return']:>7.1f}% Sharpe:{r['sharpe']:>5.2f} DD:{r['max_dd']:>6.1f}% WR:{r['win_rate']:>5.1f}% Trades:{r['trades']:>3} Fit:{r['fitness']:>8.1f} {beat}")

        results.extend(arch_results)

    # Phase 2: Deep optimization on top 4
    print(f"\n═══ PHASE 2: DEEP OPTIMIZATION ═══")
    results.sort(key=lambda x: x["fitness"], reverse=True)

    top_archetypes = []
    seen = set()
    for r in results:
        if "error" not in r and r["archetype"] not in seen:
            top_archetypes.append((r["archetype"], r["params"]))
            seen.add(r["archetype"])
            if len(top_archetypes) == 4:
                break

    for arch_name, best_params in top_archetypes:
        strat_class = STRATEGY_CLASSES[arch_name]
        print(f"\n  Fine-tuning {arch_name}...")

        fine_combos = []
        for key, val in best_params.items():
            if isinstance(val, (int, float)) and not isinstance(val, bool):
                for delta in [-0.4, -0.3, -0.2, -0.15, -0.1, -0.05, 0, 0.05, 0.1, 0.15, 0.2, 0.3, 0.4]:
                    new_params = best_params.copy()
                    new_val = val * (1 + delta)
                    if isinstance(val, int):
                        new_val = max(2, int(round(new_val)))
                    else:
                        new_val = round(max(0.5, new_val), 2)
                    new_params[key] = new_val
                    fine_combos.append(new_params)

        seen_hashes = set()
        unique_combos = []
        for c in fine_combos:
            h = hashlib.md5(json.dumps(c, sort_keys=True).encode()).hexdigest()
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

    # ═══ PHASE 3: Cross-breed top strategies ═══
    print(f"\n═══ PHASE 3: CROSS-BREEDING ═══")
    # Take the best trail_pct from each winner and try them across archetypes
    results.sort(key=lambda x: x["fitness"], reverse=True)
    valid = [r for r in results if "error" not in r and r["fitness"] > 0]

    best_trail_pcts = set()
    for r in valid[:20]:
        if "trail_pct" in r["params"]:
            best_trail_pcts.add(r["params"]["trail_pct"])

    if best_trail_pcts:
        print(f"  Best trail_pct values: {sorted(best_trail_pcts)}")
        for arch_name in ["PercentTrailRider", "HybridStayer", "MACDTrendStayer"]:
            strat_class = STRATEGY_CLASSES[arch_name]
            # Get current best for this arch
            arch_best = [r for r in valid if r["archetype"] == arch_name]
            if arch_best:
                base = arch_best[0]["params"].copy()
                for tp in best_trail_pcts:
                    new_p = base.copy()
                    new_p["trail_pct"] = tp
                    result = run_experiment(strat_class, new_p)
                    result["archetype"] = arch_name
                    result["params"] = new_p
                    results.append(result)
                    experiment_count += 1

    # ═══ FINAL RANKING ═══
    results.sort(key=lambda x: x["fitness"], reverse=True)
    valid = [r for r in results if "error" not in r and r["fitness"] > 0]

    elapsed = time.time() - start_time

    print(f"\n{'═' * 78}")
    print(f"  AUTORESEARCH V2 COMPLETE")
    print(f"  Experiments: {experiment_count} | Time: {elapsed:.1f}s | Rate: {experiment_count/elapsed:.1f}/s")
    print(f"  Buy & Hold: {BH_RETURN:.1f}%")
    print(f"{'═' * 78}\n")

    print(f"  TOP 25 STRATEGIES:\n")
    print(f"  {'#':>3} {'Archetype':<22} {'Return':>8} {'Sharpe':>7} {'MaxDD':>7} {'WR':>6} {'Trades':>6} {'Fitness':>9} {'B&H':>5}")
    print(f"  {'─' * 82}")

    for i, r in enumerate(valid[:25]):
        beat = "✓" if r["return"] > BH_RETURN else " "
        print(f"  {i+1:>3} {r['archetype']:<22} {r['return']:>7.1f}% {r['sharpe']:>6.2f} {r['max_dd']:>6.1f}% {r['win_rate']:>5.1f}% {r['trades']:>5} {r['fitness']:>9.1f} {beat:>3}")

    # Save
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "au_autoresearch_v2_results.json")
    with open(output_path, "w") as f:
        json.dump({
            "meta": {
                "version": 2,
                "experiments": experiment_count,
                "elapsed_s": round(elapsed, 1),
                "bh_return": round(BH_RETURN, 1),
                "data_range": f"{DATA.index[0].date()} to {DATA.index[-1].date()}",
                "timestamp": datetime.now().isoformat(),
            },
            "top_strategies": valid[:50],
        }, f, indent=2, default=str)
    print(f"\n  Results → {output_path}")

    # Champion details
    if valid:
        best = valid[0]
        print(f"\n{'═' * 78}")
        print(f"  CHAMPION: {best['archetype']}")
        print(f"  Return: {best['return']}% | Sharpe: {best['sharpe']} | MaxDD: {best['max_dd']}%")
        print(f"  WR: {best['win_rate']}% | Trades: {best['trades']} | Fitness: {best['fitness']}")
        print(f"  Params: {json.dumps(best['params'], indent=4)}")
        vs_bh = best['return'] - BH_RETURN
        print(f"  vs B&H: {'+' if vs_bh > 0 else ''}{vs_bh:.1f}%")
        print(f"{'═' * 78}")

    return valid


if __name__ == "__main__":
    run_autoresearch()
