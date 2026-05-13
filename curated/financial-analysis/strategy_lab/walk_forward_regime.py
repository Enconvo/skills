"""Regime-Aware Walk-Forward Validation for AU Daily Strategies.

Adds a 200 SMA regime filter to each strategy:
- Only enter trades when price > 200 SMA (bullish regime)
- Close positions when price drops below 200 SMA
- Sit out during bear markets entirely

Compares ORIGINAL vs REGIME-AWARE results side by side.

Usage:
    python walk_forward_regime.py
"""
import sys, os, importlib, inspect, warnings
import pandas as pd
import numpy as np
import talib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import load_au_data
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

warnings.filterwarnings("ignore")

# ── Configuration ──────────────────────────────────────────────────────
STRATEGY_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "au_daily_strategies")
CASH = 100_000
COMMISSION = 0.001
REGIME_SMA_PERIOD = 200

WINDOWS = [
    ("1998-08-05", "2005-08-05", "2008-08-05"),  # W1: Gold bull
    ("2001-08-05", "2008-08-05", "2011-08-05"),  # W2: GFC + recovery
    ("2004-08-05", "2011-08-05", "2014-08-05"),  # W3: Gold bear
    ("2007-08-05", "2014-08-05", "2017-08-05"),  # W4: Consolidation
    ("2010-08-05", "2017-08-05", "2020-08-05"),  # W5: COVID era
    ("2013-08-05", "2020-08-05", "2023-08-05"),  # W6: Inflation
    ("2016-08-05", "2023-08-05", "2026-08-05"),  # W7: AU mega-rally
]

WINDOW_LABELS = ["Gold bull", "GFC+recov", "Gold bear", "Consolid.", "COVID era", "Inflation", "AU rally"]


def calc_sma_regime(close, period):
    return talib.SMA(close, timeperiod=period)


def make_regime_aware(StrategyClass):
    """Factory: wrap any Strategy with a 200 SMA regime filter."""

    class RegimeAwareStrategy(StrategyClass):
        regime_period = REGIME_SMA_PERIOD

        def init(self):
            super().init()
            self.regime_sma = self.I(calc_sma_regime, self.data.Close, self.regime_period)

        def next(self):
            sma = self.regime_sma[-1]
            if np.isnan(sma):
                return

            bullish = self.data.Close[-1] > sma

            # Bear regime: close any open position and don't enter
            if not bullish:
                if self.position:
                    self.position.close()
                    # Reset trailing stop state if it exists
                    if hasattr(self, 'highest'):
                        self.highest = 0
                    if hasattr(self, 'trail_stop'):
                        self.trail_stop = 0
                return

            # Bull regime: run original strategy logic
            super().next()

    RegimeAwareStrategy.__name__ = f"{StrategyClass.__name__}_Regime"
    RegimeAwareStrategy.__qualname__ = f"{StrategyClass.__qualname__}_Regime"
    return RegimeAwareStrategy


def load_all_strategies():
    """Dynamically import all strategy files and extract Strategy classes."""
    strategies = {}
    strategy_files = sorted([f for f in os.listdir(STRATEGY_DIR) if f.endswith(".py") and f.startswith("r")])

    for fname in strategy_files:
        module_name = fname[:-3]
        filepath = os.path.join(STRATEGY_DIR, fname)

        try:
            with open(filepath, 'r') as f:
                source = f.read()

            exec_globals = {
                '__builtins__': __builtins__,
                'sys': sys, 'os': os, 'np': np, 'numpy': np,
                'talib': talib,
                'Strategy': Strategy, 'Backtest': Backtest, 'crossover': crossover,
                'load_au_data': lambda *a, **kw: pd.DataFrame(),
            }

            filtered_lines = []
            for line in source.split('\n'):
                stripped = line.strip()
                if stripped.startswith('data = load_au_data'):
                    continue
                if stripped.startswith('bt = Backtest'):
                    continue
                if stripped.startswith('stats = bt.run'):
                    continue
                if stripped.startswith('print(f"R'):
                    continue
                if stripped.startswith('sys.path.append'):
                    continue
                if stripped.startswith('from utils import'):
                    continue
                filtered_lines.append(line)

            exec('\n'.join(filtered_lines), exec_globals)

            for name, obj in exec_globals.items():
                if isinstance(obj, type) and issubclass(obj, Strategy) and obj is not Strategy:
                    strategies[fname] = {
                        'name': module_name,
                        'class': obj,
                        'file': fname,
                    }
                    break

        except Exception as e:
            print(f"  SKIP {fname}: {e}")

    return strategies


def run_window(strategy_cls, data, train_start, test_start, test_end):
    """Run strategy on train+test window, return test-period stats."""
    mask = (data.index >= pd.Timestamp(train_start)) & (data.index <= pd.Timestamp(test_end))
    window_data = data.loc[mask].copy()

    if len(window_data) < 100:
        return None

    try:
        bt = Backtest(window_data, strategy_cls, cash=CASH, commission=COMMISSION, exclusive_orders=True)
        stats = bt.run()

        equity = stats._equity_curve
        if equity is None or len(equity) == 0:
            return None

        test_mask = equity.index >= pd.Timestamp(test_start)
        test_equity = equity.loc[test_mask]

        if len(test_equity) < 10:
            return None

        test_start_eq = test_equity['Equity'].iloc[0]
        test_end_eq = test_equity['Equity'].iloc[-1]
        test_return = ((test_end_eq / test_start_eq) - 1) * 100

        test_eq = test_equity['Equity']
        running_max = test_eq.cummax()
        drawdowns = (test_eq - running_max) / running_max * 100
        test_maxdd = drawdowns.min()

        trades = stats._trades
        if trades is not None and len(trades) > 0:
            test_trades = trades[trades['ExitTime'] >= pd.Timestamp(test_start)]
            n_trades = len(test_trades)
            win_rate = len(test_trades[test_trades['PnL'] > 0]) / n_trades * 100 if n_trades > 0 else 0.0
        else:
            n_trades = 0
            win_rate = 0.0

        return {
            'return': round(test_return, 1),
            'maxdd': round(test_maxdd, 1),
            'trades': n_trades,
            'win_rate': round(win_rate, 1),
            'profitable': test_return > 0,
        }

    except Exception as e:
        return {'error': str(e), 'return': 0, 'maxdd': 0, 'trades': 0, 'win_rate': 0, 'profitable': False}


def run_walk_forward(strategies, data, regime_aware=False):
    """Run walk-forward for all strategies, return results list."""
    results = []

    for fname, strat_info in sorted(strategies.items()):
        name = strat_info['name']
        cls = strat_info['class']

        if regime_aware:
            cls = make_regime_aware(cls)

        tag = "RA" if regime_aware else "OG"
        print(f"  [{tag}] {name}:", end=" ", flush=True)

        window_results = []
        wins = 0
        for i, (train_start, test_start, test_end) in enumerate(WINDOWS, 1):
            actual_test_end = min(pd.Timestamp(test_end), data.index[-1])
            result = run_window(cls, data, train_start, test_start, str(actual_test_end.date()))

            if result is None:
                window_results.append({'return': 0, 'maxdd': 0, 'trades': 0, 'win_rate': 0, 'profitable': False})
                print("·", end="", flush=True)
            elif result.get('profitable', False):
                window_results.append(result)
                wins += 1
                print("✓", end="", flush=True)
            else:
                window_results.append(result)
                print("✗", end="", flush=True)

        status = "ROBUST" if wins >= 5 else ("MARGINAL" if wins >= 4 else "FRAGILE")
        print(f"  {wins}/7 ({status})")

        results.append({
            'name': name,
            'file': fname,
            'windows_passed': wins,
            'status': status,
            'window_results': window_results,
            'avg_return': round(np.mean([w['return'] for w in window_results]), 1),
            'avg_maxdd': round(np.mean([w['maxdd'] for w in window_results]), 1),
            'total_trades': sum(w['trades'] for w in window_results),
        })

    results.sort(key=lambda x: (-x['windows_passed'], -x['avg_return']))
    return results


def print_results_table(results, label):
    """Print formatted results table."""
    print(f"\n{'─' * 120}")
    print(f"  {label}")
    print(f"{'─' * 120}")
    print(f"  {'Strategy':<30} {'Pass':>5} {'Status':<9} ", end="")
    for i, lbl in enumerate(WINDOW_LABELS, 1):
        print(f"{'W'+str(i):>8}", end="")
    print(f"  {'Avg':>7}  {'AvgDD':>7}  {'Trades':>6}")
    print(f"  {'':30} {'':5} {'':9} ", end="")
    for lbl in WINDOW_LABELS:
        print(f"{lbl:>8}", end="")
    print()
    print(f"  {'─' * 116}")

    for r in results:
        rets = [w['return'] for w in r['window_results']]
        print(f"  {r['name']:<30} {r['windows_passed']}/7   {r['status']:<9} ", end="")
        for ret in rets:
            if ret > 0:
                print(f"{ret:>7.1f}%", end="")
            else:
                print(f"{ret:>7.1f}%", end="")
        print(f"  {r['avg_return']:>6.1f}%  {r['avg_maxdd']:>6.1f}%  {r['total_trades']:>5}t")


def main():
    print("=" * 100)
    print("  REGIME-AWARE WALK-FORWARD VALIDATION — AU Daily Strategies")
    print("  Regime filter: 200 SMA (trade only when price > 200 SMA)")
    print("=" * 100)
    print()

    data = load_full_data()
    print(f"  Data: {data.index[0].date()} → {data.index[-1].date()} ({len(data)} bars)")
    print()

    # Print window map
    print("  ── Window Map ──────────────────────────────────────────")
    for i, ((ts, te_ts, te), lbl) in enumerate(zip(WINDOWS, WINDOW_LABELS), 1):
        print(f"    W{i}: Train {ts[:4]}-{te_ts[:4]} → Test {te_ts[:4]}-{te[:4]}  ({lbl})")
    print()

    # Load strategies
    print("  ── Loading Strategies ──────────────────────────────────")
    strategies = load_all_strategies()
    print(f"    Loaded {len(strategies)} strategies")
    print()

    # Run ORIGINAL walk-forward
    print("  ══ PHASE 1: ORIGINAL STRATEGIES (no regime filter) ═════")
    og_results = run_walk_forward(strategies, data, regime_aware=False)

    # Run REGIME-AWARE walk-forward
    print()
    print("  ══ PHASE 2: REGIME-AWARE STRATEGIES (200 SMA filter) ══")
    ra_results = run_walk_forward(strategies, data, regime_aware=True)

    # Print side-by-side results
    print()
    print("=" * 100)
    print("  RESULTS COMPARISON")
    print("=" * 100)

    print_results_table(og_results, "ORIGINAL (no filter)")
    print_results_table(ra_results, "REGIME-AWARE (200 SMA filter)")

    # Print improvement analysis
    print()
    print("=" * 100)
    print("  IMPROVEMENT ANALYSIS: Original → Regime-Aware")
    print("=" * 100)
    print()
    print(f"  {'Strategy':<30} {'OG Pass':>8} {'RA Pass':>8} {'Change':>8} {'OG Avg':>8} {'RA Avg':>8} {'Δ Avg':>8} {'OG DD':>8} {'RA DD':>8}")
    print(f"  {'─' * 100}")

    improved = 0
    same = 0
    worse = 0

    for og, ra in zip(sorted(og_results, key=lambda x: x['file']),
                      sorted(ra_results, key=lambda x: x['file'])):
        pass_change = ra['windows_passed'] - og['windows_passed']
        avg_change = ra['avg_return'] - og['avg_return']
        sign = "+" if pass_change > 0 else ("" if pass_change == 0 else "")
        avg_sign = "+" if avg_change > 0 else ""

        if pass_change > 0:
            improved += 1
            marker = " ⬆"
        elif pass_change < 0:
            worse += 1
            marker = " ⬇"
        else:
            same += 1
            marker = "  ="

        print(f"  {og['name']:<30} {og['windows_passed']}/7    {ra['windows_passed']}/7    {sign}{pass_change:>+d}{marker}   {og['avg_return']:>6.1f}%  {ra['avg_return']:>6.1f}%  {avg_sign}{avg_change:.1f}%  {og['avg_maxdd']:>6.1f}%  {ra['avg_maxdd']:>6.1f}%")

    print()
    print(f"  SUMMARY: {improved} improved, {same} unchanged, {worse} worse")

    # Final rankings — regime-aware
    print()
    print("=" * 100)
    print("  FINAL REGIME-AWARE RANKINGS")
    print("=" * 100)
    print()

    robust_ra = [r for r in ra_results if r['status'] == 'ROBUST']
    marginal_ra = [r for r in ra_results if r['status'] == 'MARGINAL']
    fragile_ra = [r for r in ra_results if r['status'] == 'FRAGILE']

    print(f"  ROBUST (5-7/7): {len(robust_ra)} strategies")
    for r in robust_ra:
        print(f"    ★ {r['name']} — {r['windows_passed']}/7, avg {r['avg_return']:.1f}%, {r['total_trades']} trades")
    print(f"  MARGINAL (4/7): {len(marginal_ra)} strategies")
    for r in marginal_ra:
        print(f"    ○ {r['name']} — {r['windows_passed']}/7, avg {r['avg_return']:.1f}%")
    print(f"  FRAGILE (0-3/7): {len(fragile_ra)} strategies")
    for r in fragile_ra:
        print(f"    ✗ {r['name']} — {r['windows_passed']}/7, avg {r['avg_return']:.1f}%")

    # Save combined results to CSV
    csv_rows = []
    for og, ra in zip(sorted(og_results, key=lambda x: x['file']),
                      sorted(ra_results, key=lambda x: x['file'])):
        row = {
            'Strategy': og['name'],
            'File': og['file'],
            'OG_Windows_Passed': og['windows_passed'],
            'OG_Status': og['status'],
            'OG_Avg_Return': og['avg_return'],
            'OG_Avg_MaxDD': og['avg_maxdd'],
            'RA_Windows_Passed': ra['windows_passed'],
            'RA_Status': ra['status'],
            'RA_Avg_Return': ra['avg_return'],
            'RA_Avg_MaxDD': ra['avg_maxdd'],
            'Pass_Change': ra['windows_passed'] - og['windows_passed'],
            'Return_Change': round(ra['avg_return'] - og['avg_return'], 1),
        }
        for i, w in enumerate(og['window_results'], 1):
            row[f'OG_W{i}_Return'] = w['return']
        for i, w in enumerate(ra['window_results'], 1):
            row[f'RA_W{i}_Return'] = w['return']
        csv_rows.append(row)

    df = pd.DataFrame(csv_rows)
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "au_daily_walk_forward_regime.csv")
    df.to_csv(csv_path, index=False)
    print(f"\n  Results saved to: {csv_path}")
    print("=" * 100)


def load_full_data():
    return load_au_data("daily")


if __name__ == "__main__":
    main()
