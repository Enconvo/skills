"""
AU Autoresearch Loop — Karpathy-style autonomous strategy optimization.

Philosophy: Fixed compute budget per experiment. Form hypothesis → modify → run → evaluate → repeat.
Focus: 2025-01-01 to present only. Beat buy-and-hold (285%+), capture the rally, avoid the crash.

Fitness = Return * min(Sharpe, 3.0) / max(abs(MaxDD), 10) * (1 + WinRate/100)
Bonus: +50% if strategy exits before peak drawdown period
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

# ═══════════════════════════════════════════════════════════
#  DATA
# ═══════════════════════════════════════════════════════════

def load_au_2025():
    """Load AU daily data, 2025-01-01 onward only."""
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "au_daily.csv")
    df = pd.read_csv(csv_path, index_col=0, parse_dates=True)
    try:
        df.index = pd.to_datetime(df.index, utc=True).tz_localize(None)
    except Exception:
        df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()
    # 2025+ only
    df = df.loc["2025-01-01":]
    return df

DATA = load_au_2025()
BH_RETURN = (DATA.iloc[-1]["Close"] / DATA.iloc[0]["Open"] - 1) * 100
PEAK_PRICE = DATA["Close"].max()
PEAK_DATE = DATA["Close"].idxmax()
CASH = 100_000

print(f"═══════════════════════════════════════════════════════════")
print(f"  AU AUTORESEARCH LOOP")
print(f"  Data: {DATA.index[0].date()} → {DATA.index[-1].date()} ({len(DATA)} bars)")
print(f"  Price: ${DATA.iloc[0]['Open']:.2f} → ${DATA.iloc[-1]['Close']:.2f}")
print(f"  Peak: ${PEAK_PRICE:.2f} on {PEAK_DATE.date()}")
print(f"  Buy & Hold: {BH_RETURN:.1f}%")
print(f"═══════════════════════════════════════════════════════════\n")


# ═══════════════════════════════════════════════════════════
#  INDICATOR FUNCTIONS (must be outside Strategy class)
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

def calc_macd_hist(close, fast, slow, signal):
    m, s, h = talib.MACD(close, fastperiod=fast, slowperiod=slow, signalperiod=signal)
    return h

def calc_bb_upper(close, period, nbdev):
    u, m, l = talib.BBANDS(close, timeperiod=period, nbdevup=nbdev, nbdevdn=nbdev)
    return u

def calc_bb_middle(close, period, nbdev):
    u, m, l = talib.BBANDS(close, timeperiod=period, nbdevup=nbdev, nbdevdn=nbdev)
    return m

def calc_bb_lower(close, period, nbdev):
    u, m, l = talib.BBANDS(close, timeperiod=period, nbdevup=nbdev, nbdevdn=nbdev)
    return l

def calc_stoch_k(high, low, close, k_period, d_period):
    k, d = talib.STOCH(high, low, close, fastk_period=k_period, slowk_period=d_period, slowd_period=d_period)
    return k

def calc_stoch_d(high, low, close, k_period, d_period):
    k, d = talib.STOCH(high, low, close, fastk_period=k_period, slowk_period=d_period, slowd_period=d_period)
    return d

def calc_supertrend(high, low, close, period, multiplier):
    """Manual SuperTrend calculation."""
    atr = talib.ATR(high, low, close, timeperiod=period)
    hl2 = (high + low) / 2
    upper_band = hl2 + multiplier * atr
    lower_band = hl2 - multiplier * atr

    supertrend = np.full_like(close, np.nan)
    direction = np.zeros_like(close)

    for i in range(period, len(close)):
        if np.isnan(atr[i]):
            continue
        if i == period:
            supertrend[i] = upper_band[i]
            direction[i] = -1
            continue

        if close[i] > supertrend[i-1]:
            direction[i] = 1
        elif close[i] < supertrend[i-1]:
            direction[i] = -1
        else:
            direction[i] = direction[i-1]

        if direction[i] == 1:
            supertrend[i] = max(lower_band[i], supertrend[i-1]) if direction[i-1] == 1 else lower_band[i]
        else:
            supertrend[i] = min(upper_band[i], supertrend[i-1]) if direction[i-1] == -1 else upper_band[i]

    return supertrend


# ═══════════════════════════════════════════════════════════
#  STRATEGY ARCHETYPES (the "genes")
# ═══════════════════════════════════════════════════════════

class TrendFollower(Strategy):
    """EMA crossover with ADX filter and ATR trailing stop."""
    ema_fast = 8
    ema_slow = 21
    adx_period = 14
    adx_thresh = 20
    atr_period = 14
    atr_mult = 2.0
    use_sma_filter = True
    sma_period = 50

    def init(self):
        self.ema_f = self.I(calc_ema, self.data.Close, self.ema_fast)
        self.ema_s = self.I(calc_ema, self.data.Close, self.ema_slow)
        self.adx = self.I(calc_adx, self.data.High, self.data.Low, self.data.Close, self.adx_period)
        self.atr = self.I(calc_atr, self.data.High, self.data.Low, self.data.Close, self.atr_period)
        self.sma = self.I(calc_sma, self.data.Close, self.sma_period)
        self.trail_stop = 0

    def next(self):
        if np.isnan(self.ema_f[-1]) or np.isnan(self.adx[-1]) or np.isnan(self.atr[-1]):
            return

        if not self.position:
            trend_ok = self.adx[-1] > self.adx_thresh
            cross_up = crossover(self.ema_f, self.ema_s)
            sma_ok = (not self.use_sma_filter) or (self.data.Close[-1] > self.sma[-1])

            if cross_up and trend_ok and sma_ok:
                self.buy()
                self.trail_stop = self.data.Close[-1] - self.atr_mult * self.atr[-1]
        else:
            new_stop = self.data.Close[-1] - self.atr_mult * self.atr[-1]
            self.trail_stop = max(self.trail_stop, new_stop)
            if self.data.Close[-1] < self.trail_stop:
                self.position.close()


class MomentumRider(Strategy):
    """RSI + MACD momentum with volatility filter."""
    rsi_period = 14
    rsi_entry = 55
    rsi_exit = 75
    macd_fast = 12
    macd_slow = 26
    macd_signal = 9
    atr_period = 14
    atr_trail = 2.5

    def init(self):
        self.rsi = self.I(calc_rsi, self.data.Close, self.rsi_period)
        self.macd = self.I(calc_macd_line, self.data.Close, self.macd_fast, self.macd_slow, self.macd_signal)
        self.macd_sig = self.I(calc_macd_signal, self.data.Close, self.macd_fast, self.macd_slow, self.macd_signal)
        self.macd_hist = self.I(calc_macd_hist, self.data.Close, self.macd_fast, self.macd_slow, self.macd_signal)
        self.atr = self.I(calc_atr, self.data.High, self.data.Low, self.data.Close, self.atr_period)
        self.trail_stop = 0

    def next(self):
        if np.isnan(self.rsi[-1]) or np.isnan(self.macd[-1]) or np.isnan(self.atr[-1]):
            return

        if not self.position:
            rsi_ok = self.rsi[-1] > self.rsi_entry
            macd_cross = crossover(self.macd, self.macd_sig)
            macd_pos = self.macd_hist[-1] > 0

            if rsi_ok and (macd_cross or macd_pos):
                self.buy()
                self.trail_stop = self.data.Close[-1] - self.atr_trail * self.atr[-1]
        else:
            new_stop = self.data.Close[-1] - self.atr_trail * self.atr[-1]
            self.trail_stop = max(self.trail_stop, new_stop)
            if self.data.Close[-1] < self.trail_stop or self.rsi[-1] > self.rsi_exit:
                self.position.close()


class SuperTrendFollower(Strategy):
    """SuperTrend + EMA alignment for strong trend capture."""
    st_period = 10
    st_mult = 3.0
    ema_period = 21
    atr_period = 14
    atr_trail = 2.0

    def init(self):
        self.st = self.I(calc_supertrend, self.data.High, self.data.Low, self.data.Close, self.st_period, self.st_mult)
        self.ema = self.I(calc_ema, self.data.Close, self.ema_period)
        self.atr = self.I(calc_atr, self.data.High, self.data.Low, self.data.Close, self.atr_period)
        self.trail_stop = 0

    def next(self):
        if np.isnan(self.st[-1]) or np.isnan(self.ema[-1]) or np.isnan(self.atr[-1]):
            return

        if not self.position:
            above_st = self.data.Close[-1] > self.st[-1]
            above_ema = self.data.Close[-1] > self.ema[-1]
            if above_st and above_ema:
                self.buy()
                self.trail_stop = self.st[-1]
        else:
            # Use max of SuperTrend and ATR trail
            atr_stop = self.data.Close[-1] - self.atr_trail * self.atr[-1]
            new_stop = max(self.st[-1], atr_stop)
            self.trail_stop = max(self.trail_stop, new_stop)
            if self.data.Close[-1] < self.trail_stop:
                self.position.close()


class BreakoutMomentum(Strategy):
    """Donchian channel breakout with momentum confirmation."""
    dc_period = 20
    atr_period = 14
    atr_trail = 2.0
    adx_period = 14
    adx_thresh = 20

    def init(self):
        self.adx = self.I(calc_adx, self.data.High, self.data.Low, self.data.Close, self.adx_period)
        self.atr = self.I(calc_atr, self.data.High, self.data.Low, self.data.Close, self.atr_period)
        self.plus_di = self.I(calc_plus_di, self.data.High, self.data.Low, self.data.Close, self.adx_period)
        self.minus_di = self.I(calc_minus_di, self.data.High, self.data.Low, self.data.Close, self.adx_period)
        self.trail_stop = 0

    def next(self):
        if np.isnan(self.atr[-1]) or np.isnan(self.adx[-1]):
            return

        if len(self.data.Close) < self.dc_period + 1:
            return

        if not self.position:
            dc_high = max(self.data.High[-self.dc_period:-1])
            breakout = self.data.Close[-1] > dc_high
            trend_ok = self.adx[-1] > self.adx_thresh and self.plus_di[-1] > self.minus_di[-1]

            if breakout and trend_ok:
                self.buy()
                self.trail_stop = self.data.Close[-1] - self.atr_trail * self.atr[-1]
        else:
            new_stop = self.data.Close[-1] - self.atr_trail * self.atr[-1]
            self.trail_stop = max(self.trail_stop, new_stop)
            if self.data.Close[-1] < self.trail_stop:
                self.position.close()


class MACDTrendSurfer(Strategy):
    """MACD histogram slope riding with fast exit on divergence."""
    macd_fast = 8
    macd_slow = 17
    macd_signal = 9
    ema_period = 21
    atr_period = 14
    atr_trail = 1.5

    def init(self):
        self.macd = self.I(calc_macd_line, self.data.Close, self.macd_fast, self.macd_slow, self.macd_signal)
        self.macd_sig = self.I(calc_macd_signal, self.data.Close, self.macd_fast, self.macd_slow, self.macd_signal)
        self.macd_hist = self.I(calc_macd_hist, self.data.Close, self.macd_fast, self.macd_slow, self.macd_signal)
        self.ema = self.I(calc_ema, self.data.Close, self.ema_period)
        self.atr = self.I(calc_atr, self.data.High, self.data.Low, self.data.Close, self.atr_period)
        self.trail_stop = 0

    def next(self):
        if np.isnan(self.macd[-1]) or np.isnan(self.ema[-1]) or np.isnan(self.atr[-1]):
            return

        if not self.position:
            macd_cross = crossover(self.macd, self.macd_sig)
            above_ema = self.data.Close[-1] > self.ema[-1]
            hist_rising = len(self.macd_hist) > 2 and self.macd_hist[-1] > self.macd_hist[-2]

            if macd_cross and above_ema:
                self.buy()
                self.trail_stop = self.data.Close[-1] - self.atr_trail * self.atr[-1]
        else:
            new_stop = self.data.Close[-1] - self.atr_trail * self.atr[-1]
            self.trail_stop = max(self.trail_stop, new_stop)
            # Exit on MACD cross down OR trail stop
            macd_cross_down = crossover(self.macd_sig, self.macd)
            if self.data.Close[-1] < self.trail_stop or macd_cross_down:
                self.position.close()


class PullbackBuyer(Strategy):
    """Buy dips in uptrend: EMA trend + RSI pullback."""
    ema_fast = 8
    ema_slow = 50
    rsi_period = 14
    rsi_buy = 40
    rsi_sell = 70
    atr_period = 14
    atr_trail = 2.0

    def init(self):
        self.ema_f = self.I(calc_ema, self.data.Close, self.ema_fast)
        self.ema_s = self.I(calc_ema, self.data.Close, self.ema_slow)
        self.rsi = self.I(calc_rsi, self.data.Close, self.rsi_period)
        self.atr = self.I(calc_atr, self.data.High, self.data.Low, self.data.Close, self.atr_period)
        self.trail_stop = 0

    def next(self):
        if np.isnan(self.ema_s[-1]) or np.isnan(self.rsi[-1]) or np.isnan(self.atr[-1]):
            return

        uptrend = self.ema_f[-1] > self.ema_s[-1]

        if not self.position:
            pullback = self.rsi[-1] < self.rsi_buy
            if uptrend and pullback:
                self.buy()
                self.trail_stop = self.data.Close[-1] - self.atr_trail * self.atr[-1]
        else:
            new_stop = self.data.Close[-1] - self.atr_trail * self.atr[-1]
            self.trail_stop = max(self.trail_stop, new_stop)
            if self.data.Close[-1] < self.trail_stop or self.rsi[-1] > self.rsi_sell:
                self.position.close()


class GoldenCrossATR(Strategy):
    """Classic golden cross (fast/slow SMA) with ATR dynamic exit."""
    sma_fast = 20
    sma_slow = 50
    atr_period = 14
    atr_trail = 2.5

    def init(self):
        self.sma_f = self.I(calc_sma, self.data.Close, self.sma_fast)
        self.sma_s = self.I(calc_sma, self.data.Close, self.sma_slow)
        self.atr = self.I(calc_atr, self.data.High, self.data.Low, self.data.Close, self.atr_period)
        self.trail_stop = 0

    def next(self):
        if np.isnan(self.sma_f[-1]) or np.isnan(self.sma_s[-1]) or np.isnan(self.atr[-1]):
            return

        if not self.position:
            if crossover(self.sma_f, self.sma_s):
                self.buy()
                self.trail_stop = self.data.Close[-1] - self.atr_trail * self.atr[-1]
        else:
            new_stop = self.data.Close[-1] - self.atr_trail * self.atr[-1]
            self.trail_stop = max(self.trail_stop, new_stop)
            cross_down = crossover(self.sma_s, self.sma_f)
            if self.data.Close[-1] < self.trail_stop or cross_down:
                self.position.close()


# ═══════════════════════════════════════════════════════════
#  PARAMETER SPACE (per archetype)
# ═══════════════════════════════════════════════════════════

PARAM_SPACE = {
    "TrendFollower": {
        "ema_fast": [5, 8, 10, 13],
        "ema_slow": [15, 21, 30, 40],
        "adx_thresh": [15, 20, 25],
        "atr_mult": [1.5, 2.0, 2.5, 3.0],
        "use_sma_filter": [True, False],
        "sma_period": [30, 50],
    },
    "MomentumRider": {
        "rsi_period": [10, 14],
        "rsi_entry": [45, 50, 55, 60],
        "rsi_exit": [70, 75, 80, 85],
        "macd_fast": [8, 12],
        "macd_slow": [21, 26],
        "atr_trail": [1.5, 2.0, 2.5, 3.0],
    },
    "SuperTrendFollower": {
        "st_period": [7, 10, 14],
        "st_mult": [2.0, 2.5, 3.0, 3.5],
        "ema_period": [15, 21, 30],
        "atr_trail": [1.5, 2.0, 2.5, 3.0],
    },
    "BreakoutMomentum": {
        "dc_period": [10, 15, 20, 30],
        "atr_trail": [1.5, 2.0, 2.5, 3.0],
        "adx_thresh": [15, 20, 25],
    },
    "MACDTrendSurfer": {
        "macd_fast": [6, 8, 10, 12],
        "macd_slow": [15, 17, 21, 26],
        "macd_signal": [7, 9],
        "ema_period": [15, 21, 30],
        "atr_trail": [1.0, 1.5, 2.0, 2.5],
    },
    "PullbackBuyer": {
        "ema_fast": [5, 8, 13],
        "ema_slow": [30, 50],
        "rsi_buy": [30, 35, 40, 45],
        "rsi_sell": [65, 70, 75, 80],
        "atr_trail": [1.5, 2.0, 2.5, 3.0],
    },
    "GoldenCrossATR": {
        "sma_fast": [10, 15, 20, 30],
        "sma_slow": [40, 50, 60],
        "atr_trail": [1.5, 2.0, 2.5, 3.0],
    },
}

STRATEGY_CLASSES = {
    "TrendFollower": TrendFollower,
    "MomentumRider": MomentumRider,
    "SuperTrendFollower": SuperTrendFollower,
    "BreakoutMomentum": BreakoutMomentum,
    "MACDTrendSurfer": MACDTrendSurfer,
    "PullbackBuyer": PullbackBuyer,
    "GoldenCrossATR": GoldenCrossATR,
}


# ═══════════════════════════════════════════════════════════
#  FITNESS FUNCTION
# ═══════════════════════════════════════════════════════════

def compute_fitness(stats):
    """Score a backtest. Higher = better.

    Rewards: High return, high Sharpe, high win rate
    Penalizes: Deep drawdowns, too few trades
    Bonus: Beating buy-and-hold
    """
    ret = stats.get("Return [%]", 0)
    sharpe = stats.get("Sharpe Ratio", 0) or 0
    max_dd = abs(stats.get("Max. Drawdown [%]", -100))
    win_rate = stats.get("Win Rate [%]", 0) or 0
    n_trades = stats.get("# Trades", 0)

    if n_trades < 3:
        return -9999  # Too few trades = unreliable

    # Core fitness: return-weighted risk-adjusted score
    sharpe_cap = min(max(sharpe, 0), 4.0)  # Cap Sharpe to avoid overfitting on 1 trade
    dd_penalty = max(max_dd, 10)  # Floor at 10% to avoid div by tiny DD

    fitness = ret * (1 + sharpe_cap) * (1 + win_rate / 100) / dd_penalty

    # B&H bonus: strategies that beat B&H get 2x multiplier
    if ret > BH_RETURN:
        fitness *= 2.0

    return round(fitness, 2)


# ═══════════════════════════════════════════════════════════
#  EXPERIMENT RUNNER
# ═══════════════════════════════════════════════════════════

def run_experiment(strategy_class, params):
    """Run one backtest experiment. Returns stats dict + fitness."""
    try:
        bt = Backtest(DATA, strategy_class, cash=CASH, commission=0.001, exclusive_orders=True)
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
            "profit_factor": round(stats.get("Profit Factor", 0) or 0, 2),
        }
    except Exception as e:
        return {"error": str(e), "fitness": -9999}


def generate_param_combos(archetype_name, max_combos=200):
    """Generate parameter combinations for an archetype. Smart sampling if space is huge."""
    space = PARAM_SPACE[archetype_name]
    keys = sorted(space.keys())
    values = [space[k] for k in keys]

    # Calculate total combinations
    total = 1
    for v in values:
        total *= len(v)

    if total <= max_combos:
        # Exhaustive
        combos = []
        for vals in itertools.product(*values):
            combos.append(dict(zip(keys, vals)))
        return combos
    else:
        # Random sampling
        import random
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

def run_autoresearch(max_experiments=2000, target_return=500):
    """Karpathy loop: iterate until target or budget exhausted."""

    results = []
    experiment_count = 0
    start_time = time.time()

    print(f"TARGET: {target_return}%+ return (B&H = {BH_RETURN:.1f}%)")
    print(f"BUDGET: {max_experiments} experiments max\n")

    # Phase 1: Broad sweep across all archetypes
    print("═══ PHASE 1: BROAD SWEEP ═══")
    for arch_name, strat_class in STRATEGY_CLASSES.items():
        combos = generate_param_combos(arch_name, max_combos=150)
        print(f"\n  {arch_name}: testing {len(combos)} variants...")

        arch_results = []
        for params in combos:
            result = run_experiment(strat_class, params)
            result["archetype"] = arch_name
            result["params"] = params
            arch_results.append(result)
            experiment_count += 1

        # Sort by fitness
        arch_results.sort(key=lambda x: x["fitness"], reverse=True)

        # Show top 3
        for i, r in enumerate(arch_results[:3]):
            if "error" not in r:
                beat = "✓ BEATS B&H" if r["return"] > BH_RETURN else ""
                print(f"    #{i+1} Return:{r['return']:>7.1f}% | Sharpe:{r['sharpe']:>5.2f} | DD:{r['max_dd']:>6.1f}% | WR:{r['win_rate']:>5.1f}% | Trades:{r['trades']:>3} | Fitness:{r['fitness']:>8.1f} {beat}")

        results.extend(arch_results)

    # Phase 2: Deep optimization on top performers
    print(f"\n═══ PHASE 2: DEEP OPTIMIZATION (top archetypes) ═══")

    # Find the top 3 archetypes
    results.sort(key=lambda x: x["fitness"], reverse=True)
    top_archetypes = []
    seen = set()
    for r in results:
        if "error" not in r and r["archetype"] not in seen:
            top_archetypes.append(r["archetype"])
            seen.add(r["archetype"])
            if len(top_archetypes) == 3:
                break

    print(f"  Top archetypes: {top_archetypes}")

    for arch_name in top_archetypes:
        strat_class = STRATEGY_CLASSES[arch_name]
        space = PARAM_SPACE[arch_name]

        # Get the best params from phase 1
        best_phase1 = [r for r in results if r["archetype"] == arch_name and "error" not in r]
        best_phase1.sort(key=lambda x: x["fitness"], reverse=True)
        best_params = best_phase1[0]["params"]

        # Fine-grained search around the best params
        print(f"\n  Deep optimizing {arch_name} around {best_params}...")

        fine_combos = []
        for key, val in best_params.items():
            if isinstance(val, (int, float)) and not isinstance(val, bool):
                # Generate ±20% neighborhood
                for delta in [-0.3, -0.2, -0.1, 0, 0.1, 0.2, 0.3]:
                    new_params = best_params.copy()
                    new_val = val * (1 + delta)
                    if isinstance(val, int):
                        new_val = max(2, int(round(new_val)))
                    else:
                        new_val = round(new_val, 2)
                    new_params[key] = new_val
                    fine_combos.append(new_params)

        # Deduplicate
        seen_hashes = set()
        unique_combos = []
        for c in fine_combos:
            h = hashlib.md5(json.dumps(c, sort_keys=True).encode()).hexdigest()
            if h not in seen_hashes:
                seen_hashes.add(h)
                unique_combos.append(c)

        print(f"  Testing {len(unique_combos)} fine-grained variants...")

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

    print(f"\n{'═' * 70}")
    print(f"  AUTORESEARCH COMPLETE")
    print(f"  Experiments: {experiment_count} | Time: {elapsed:.1f}s | Rate: {experiment_count/elapsed:.1f}/s")
    print(f"  Buy & Hold: {BH_RETURN:.1f}%")
    print(f"{'═' * 70}\n")

    print(f"  TOP 20 STRATEGIES:\n")
    print(f"  {'#':>3} {'Archetype':<22} {'Return':>8} {'Sharpe':>7} {'MaxDD':>7} {'WR':>6} {'Trades':>6} {'Fitness':>8} {'B&H':>6}")
    print(f"  {'─' * 80}")

    for i, r in enumerate(valid[:20]):
        beat = "✓" if r["return"] > BH_RETURN else " "
        print(f"  {i+1:>3} {r['archetype']:<22} {r['return']:>7.1f}% {r['sharpe']:>6.2f} {r['max_dd']:>6.1f}% {r['win_rate']:>5.1f}% {r['trades']:>5} {r['fitness']:>8.1f} {beat:>4}")

    # Save results
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "au_autoresearch_results.json")
    top50 = valid[:50]
    with open(output_path, "w") as f:
        json.dump({
            "meta": {
                "experiments": experiment_count,
                "elapsed_s": round(elapsed, 1),
                "bh_return": round(BH_RETURN, 1),
                "data_range": f"{DATA.index[0].date()} to {DATA.index[-1].date()}",
                "bars": len(DATA),
                "timestamp": datetime.now().isoformat(),
            },
            "top_strategies": top50,
        }, f, indent=2, default=str)
    print(f"\n  Results saved → {output_path}")

    # Print #1 strategy details
    if valid:
        best = valid[0]
        print(f"\n{'═' * 70}")
        print(f"  🏆 CHAMPION: {best['archetype']}")
        print(f"  Return: {best['return']}% | Sharpe: {best['sharpe']} | MaxDD: {best['max_dd']}%")
        print(f"  Win Rate: {best['win_rate']}% | Trades: {best['trades']} | Fitness: {best['fitness']}")
        print(f"  Params: {json.dumps(best['params'], indent=4)}")
        print(f"{'═' * 70}")

    return valid


if __name__ == "__main__":
    results = run_autoresearch(max_experiments=2000, target_return=500)
