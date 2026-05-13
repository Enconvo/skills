"""Generate full NVDA chart: regimes + trades from top 3 strategies + equity curves."""
import sys, os, warnings
import pandas as pd
import numpy as np
import talib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
warnings.filterwarnings("ignore")

from utils import load_nvda_data
from regime_detector import detect_regimes, print_regime_report
from regime_chart import generate_chart
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

STRATEGY_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nvda_strategies")
CASH = 1_000_000

# Top 3 from walk-forward results
TOP_STRATEGIES = [
    ('r1_07_ema_ribbon.py', 'EMA Ribbon'),
    ('r2_10_gap_keltner_hybrid.py', 'Gap+Keltner Hybrid'),
    ('r1_03_bollinger_bounce.py', 'Bollinger Bounce'),
]


def load_strategy_class(fname):
    """Load a strategy class from file."""
    filepath = os.path.join(STRATEGY_DIR, fname)
    with open(filepath, 'r') as f:
        source = f.read()

    exec_globals = {
        '__builtins__': __builtins__,
        'sys': sys, 'os': os, 'np': np, 'numpy': np, 'pd': pd,
        'talib': talib,
        'Strategy': Strategy, 'Backtest': Backtest, 'crossover': crossover,
        'load_nvda_data': lambda *a, **kw: pd.DataFrame(),
    }

    filtered = []
    for line in source.split('\n'):
        s = line.strip()
        if any(s.startswith(skip) for skip in [
            'data = load_nvda_data', 'bt = Backtest', 'stats = bt.run',
            'print(', 'sys.path.append', 'from utils import'
        ]):
            continue
        filtered.append(line)

    exec('\n'.join(filtered), exec_globals)

    for name, obj in exec_globals.items():
        if isinstance(obj, type) and issubclass(obj, Strategy) and obj is not Strategy:
            return obj
    return None


def main():
    print("Loading NVDA data...")
    data = load_nvda_data("daily")

    print("Detecting regimes...")
    regimes = detect_regimes(data)
    print_regime_report(regimes, ticker="NVDA")

    trades_dict = {}
    equity_dict = {}
    wf_results = {}

    # Walk-forward scores from the last run
    wf_scores = {
        'EMA Ribbon': {'windows_passed': 7, 'n_windows': 9, 'status': 'ROBUST'},
        'Gap+Keltner Hybrid': {'windows_passed': 7, 'n_windows': 9, 'status': 'ROBUST'},
        'Bollinger Bounce': {'windows_passed': 7, 'n_windows': 9, 'status': 'ROBUST'},
    }

    for fname, display_name in TOP_STRATEGIES:
        print(f"  Running {display_name}...", end=" ", flush=True)
        cls = load_strategy_class(fname)
        if cls is None:
            print("SKIP (could not load)")
            continue

        bt = Backtest(data, cls, cash=CASH, commission=0.001, exclusive_orders=True)
        stats = bt.run()

        trades = stats['_trades']
        if trades is not None and len(trades) > 0:
            trades_dict[display_name] = trades
            print(f"{len(trades)} trades")
        else:
            print("0 trades")

        equity = stats._equity_curve
        if equity is not None:
            equity_dict[display_name] = equity['Equity']

        if display_name in wf_scores:
            wf_results[display_name] = wf_scores[display_name]

    print("\nGenerating chart...")
    path = generate_chart(
        data, regimes,
        trades_by_strategy=trades_dict,
        equity_by_strategy=equity_dict,
        walk_forward_results=wf_results,
        ticker="NVDA",
    )

    print(f"\nDone! Open: file://{os.path.abspath(path)}")

    try:
        import webbrowser
        webbrowser.open(f"file://{os.path.abspath(path)}")
    except Exception:
        pass


if __name__ == "__main__":
    main()
