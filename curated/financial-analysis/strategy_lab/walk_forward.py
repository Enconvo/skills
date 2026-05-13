"""Rolling Walk-Forward Validation Framework for AU Daily Strategies.

Runs each strategy across 7 overlapping windows (7yr train, 3yr test, slide by 3yr).
A strategy is ROBUST if profitable in 5/7+ test windows.
Only measures performance on the TEST window (train provides indicator warmup).

Usage:
    python walk_forward.py
"""
import sys, os, importlib, inspect, warnings
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import load_au_data
from backtesting import Backtest, Strategy

warnings.filterwarnings("ignore")

# ── Configuration ──────────────────────────────────────────────────────
STRATEGY_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "au_daily_strategies")
CASH = 100_000
COMMISSION = 0.001

# Rolling windows: (train_start, train_end/test_start, test_end)
# 7yr train, 3yr test, slide by 3yr
WINDOWS = [
    ("1998-08-05", "2005-08-05", "2008-08-05"),  # W1: train 98-05, test 05-08 (gold bull)
    ("2001-08-05", "2008-08-05", "2011-08-05"),  # W2: train 01-08, test 08-11 (GFC + recovery)
    ("2004-08-05", "2011-08-05", "2014-08-05"),  # W3: train 04-11, test 11-14 (gold bear)
    ("2007-08-05", "2014-08-05", "2017-08-05"),  # W4: train 07-14, test 14-17 (consolidation)
    ("2010-08-05", "2017-08-05", "2020-08-05"),  # W5: train 10-17, test 17-20 (COVID crash)
    ("2013-08-05", "2020-08-05", "2023-08-05"),  # W6: train 13-20, test 20-23 (inflation)
    ("2016-08-05", "2023-08-05", "2026-08-05"),  # W7: train 16-23, test 23-26 (AU mega-rally)
]


def load_full_data():
    """Load full AU daily dataset."""
    data = load_au_data("daily")
    return data


def find_strategy_class(module):
    """Find the Strategy subclass in a module (not Strategy itself)."""
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if issubclass(obj, Strategy) and obj is not Strategy:
            return name, obj
    return None, None


def load_all_strategies():
    """Dynamically import all strategy files and extract Strategy classes."""
    strategies = {}
    strategy_files = sorted([f for f in os.listdir(STRATEGY_DIR) if f.endswith(".py") and f.startswith("r")])

    for fname in strategy_files:
        module_name = fname[:-3]  # strip .py
        filepath = os.path.join(STRATEGY_DIR, fname)

        try:
            # Load the module without executing the backtest at module level
            spec = importlib.util.spec_from_file_location(module_name, filepath)
            # We need to prevent module-level code from running (the bt.run() calls)
            # Instead, read the file and extract just the class definition
            with open(filepath, 'r') as f:
                source = f.read()

            # Create a restricted execution environment
            exec_globals = {
                '__builtins__': __builtins__,
                'sys': sys,
                'os': os,
                'np': np,
                'numpy': np,
            }

            # Import required modules into the exec environment
            import talib
            from backtesting.lib import crossover
            exec_globals['talib'] = talib
            exec_globals['Strategy'] = Strategy
            exec_globals['Backtest'] = Backtest
            exec_globals['crossover'] = crossover

            # Mock load_au_data to return None (we'll provide data later)
            exec_globals['load_au_data'] = lambda *a, **kw: pd.DataFrame()

            # Extract just the imports, function definitions, and class definition
            # Skip lines that create Backtest objects or call bt.run()
            filtered_lines = []
            for line in source.split('\n'):
                stripped = line.strip()
                # Skip module-level execution
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

            filtered_source = '\n'.join(filtered_lines)

            exec(filtered_source, exec_globals)

            # Find the Strategy subclass
            for name, obj in exec_globals.items():
                if isinstance(obj, type) and issubclass(obj, Strategy) and obj is not Strategy:
                    # Build a readable strategy name from filename
                    strategy_name = module_name.replace('_', ' ').upper()
                    # Use the CSV-style name mapping
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
    """Run a strategy on a train+test window, return test-period stats.

    We run the backtest on the FULL window (train+test) so indicators warm up,
    but we measure performance only on the test period by comparing equity at
    test_start vs test_end.
    """
    # Slice data: from train_start to test_end (or end of data)
    mask = (data.index >= pd.Timestamp(train_start)) & (data.index <= pd.Timestamp(test_end))
    window_data = data.loc[mask].copy()

    if len(window_data) < 100:
        return None  # Not enough data

    try:
        bt = Backtest(window_data, strategy_cls, cash=CASH, commission=COMMISSION, exclusive_orders=True)
        stats = bt.run()

        # Get the equity curve
        equity = stats._equity_curve
        if equity is None or len(equity) == 0:
            return None

        # Find test-period equity
        test_mask = equity.index >= pd.Timestamp(test_start)
        test_equity = equity.loc[test_mask]

        if len(test_equity) < 10:
            return None

        # Calculate test-period metrics
        test_start_equity = test_equity['Equity'].iloc[0]
        test_end_equity = test_equity['Equity'].iloc[-1]
        test_return = ((test_end_equity / test_start_equity) - 1) * 100

        # Max drawdown in test period
        test_eq = test_equity['Equity']
        running_max = test_eq.cummax()
        drawdowns = (test_eq - running_max) / running_max * 100
        test_maxdd = drawdowns.min()

        # Count trades in test period
        trades = stats._trades
        if trades is not None and len(trades) > 0:
            test_trades = trades[trades['ExitTime'] >= pd.Timestamp(test_start)]
            n_trades = len(test_trades)
            if n_trades > 0:
                win_trades = test_trades[test_trades['PnL'] > 0]
                win_rate = len(win_trades) / n_trades * 100
            else:
                win_rate = 0.0
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


def main():
    print("=" * 80)
    print("  ROLLING WALK-FORWARD VALIDATION — AU Daily Strategies")
    print("  7yr train / 3yr test / 7 sliding windows")
    print("=" * 80)
    print()

    # Load data
    data = load_full_data()
    data_start = data.index[0]
    data_end = data.index[-1]
    print(f"Data: {data_start.date()} → {data_end.date()} ({len(data)} bars)")
    print()

    # Print window map
    print("── Window Map ──────────────────────────────────────────────")
    for i, (ts, te_ts, te) in enumerate(WINDOWS, 1):
        regime = ["Gold bull", "GFC+recovery", "Gold bear", "Consolidation",
                  "COVID era", "Inflation", "AU mega-rally"][i-1]
        print(f"  W{i}: Train {ts[:4]}-{te_ts[:4]} → Test {te_ts[:4]}-{te[:4]}  ({regime})")
    print()

    # Load strategies
    print("── Loading Strategies ──────────────────────────────────────")
    strategies = load_all_strategies()
    print(f"  Loaded {len(strategies)} strategies")
    print()

    # Run walk-forward for each strategy
    results = []
    print("── Running Walk-Forward Tests ──────────────────────────────")
    print()

    for fname, strat_info in sorted(strategies.items()):
        name = strat_info['name']
        cls = strat_info['class']
        print(f"  {name}:", end=" ", flush=True)

        window_results = []
        wins = 0
        for i, (train_start, test_start, test_end) in enumerate(WINDOWS, 1):
            # Clamp test_end to actual data end
            actual_test_end = min(pd.Timestamp(test_end), data_end)
            result = run_window(cls, data, train_start, test_start, str(actual_test_end.date()))

            if result is None:
                window_results.append({'return': 0, 'maxdd': 0, 'trades': 0, 'win_rate': 0, 'profitable': False, 'error': 'no data'})
                print("·", end="", flush=True)
            elif result.get('profitable', False):
                window_results.append(result)
                wins += 1
                print("✓", end="", flush=True)
            else:
                window_results.append(result)
                print("✗", end="", flush=True)

        pass_rate = wins / len(WINDOWS) * 100
        robust = wins >= 5
        status = "ROBUST" if robust else ("MARGINAL" if wins >= 4 else "FRAGILE")
        print(f"  {wins}/7 ({status})")

        results.append({
            'name': name,
            'file': fname,
            'windows_passed': wins,
            'pass_rate': pass_rate,
            'status': status,
            'window_results': window_results,
        })

    # Sort by windows passed (descending), then by avg test return
    results.sort(key=lambda x: (-x['windows_passed'],
                                 -np.mean([w['return'] for w in x['window_results']])))

    # Print detailed results
    print()
    print("=" * 80)
    print("  WALK-FORWARD RESULTS — RANKED BY ROBUSTNESS")
    print("=" * 80)
    print()
    print(f"{'Strategy':<30} {'Pass':>5} {'Status':<9} {'W1':>7} {'W2':>7} {'W3':>7} {'W4':>7} {'W5':>7} {'W6':>7} {'W7':>7} {'Avg':>7}")
    print("─" * 120)

    for r in results:
        rets = [w['return'] for w in r['window_results']]
        avg_ret = np.mean(rets)
        ret_strs = [f"{ret:>6.1f}%" for ret in rets]
        print(f"{r['name']:<30} {r['windows_passed']}/7   {r['status']:<9} {' '.join(ret_strs)} {avg_ret:>6.1f}%")

    # Print trade counts per window
    print()
    print(f"{'Strategy':<30} {'Trades per window':>60}")
    print(f"{'':30} {'W1':>7} {'W2':>7} {'W3':>7} {'W4':>7} {'W5':>7} {'W6':>7} {'W7':>7} {'Total':>7}")
    print("─" * 100)

    for r in results:
        trades = [w['trades'] for w in r['window_results']]
        total = sum(trades)
        trade_strs = [f"{t:>6}t" for t in trades]
        print(f"{r['name']:<30} {' '.join(trade_strs)} {total:>6}t")

    # Summary
    print()
    print("=" * 80)
    print("  SUMMARY")
    print("=" * 80)
    robust = [r for r in results if r['status'] == 'ROBUST']
    marginal = [r for r in results if r['status'] == 'MARGINAL']
    fragile = [r for r in results if r['status'] == 'FRAGILE']
    print(f"  ROBUST (5-7/7):   {len(robust)} strategies")
    for r in robust:
        avg = np.mean([w['return'] for w in r['window_results']])
        print(f"    → {r['name']} ({r['windows_passed']}/7, avg test return {avg:.1f}%)")
    print(f"  MARGINAL (4/7):   {len(marginal)} strategies")
    for r in marginal:
        avg = np.mean([w['return'] for w in r['window_results']])
        print(f"    → {r['name']} ({r['windows_passed']}/7, avg test return {avg:.1f}%)")
    print(f"  FRAGILE (0-3/7):  {len(fragile)} strategies")
    for r in fragile:
        avg = np.mean([w['return'] for w in r['window_results']])
        print(f"    → {r['name']} ({r['windows_passed']}/7, avg test return {avg:.1f}%)")

    # Save results to CSV
    csv_rows = []
    for r in results:
        row = {
            'Strategy': r['name'],
            'File': r['file'],
            'Windows_Passed': r['windows_passed'],
            'Pass_Rate': r['pass_rate'],
            'Status': r['status'],
        }
        for i, w in enumerate(r['window_results'], 1):
            row[f'W{i}_Return'] = w['return']
            row[f'W{i}_MaxDD'] = w['maxdd']
            row[f'W{i}_Trades'] = w['trades']
            row[f'W{i}_WinRate'] = w['win_rate']
        row['Avg_Return'] = round(np.mean([w['return'] for w in r['window_results']]), 1)
        csv_rows.append(row)

    df = pd.DataFrame(csv_rows)
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "au_daily_walk_forward.csv")
    df.to_csv(csv_path, index=False)
    print(f"\n  Results saved to: {csv_path}")

    # Compare with full-history rankings
    print()
    print("=" * 80)
    print("  FULL-HISTORY vs WALK-FORWARD COMPARISON")
    print("=" * 80)
    print()
    print("  Strategies that rank high on full history but FAIL walk-forward")
    print("  are likely overfit to specific market regimes.")
    print()

    # Load full-history results if available
    full_csv = os.path.join(os.path.dirname(os.path.abspath(__file__)), "au_daily_results.csv")
    if os.path.exists(full_csv):
        full_df = pd.read_csv(full_csv)
        print(f"  {'Strategy':<30} {'Full Return':>12} {'WF Status':<10} {'WF Pass':>8} {'WF Avg':>8}")
        print("  " + "─" * 72)
        for _, frow in full_df.iterrows():
            fname = frow['File']
            full_ret = frow['Return']
            # Find matching walk-forward result
            wf_match = [r for r in results if r['file'] == fname]
            if wf_match:
                wf = wf_match[0]
                avg = np.mean([w['return'] for w in wf['window_results']])
                print(f"  {frow['Strategy']:<30} {full_ret:>10.1f}% {wf['status']:<10} {wf['windows_passed']}/7    {avg:>6.1f}%")
            else:
                print(f"  {frow['Strategy']:<30} {full_ret:>10.1f}% {'N/A':<10}")

    print()
    print("  KEY INSIGHT: Strategies that are both high-return AND ROBUST")
    print("  across walk-forward windows are the most trustworthy for live trading.")
    print("=" * 80)


if __name__ == "__main__":
    main()
