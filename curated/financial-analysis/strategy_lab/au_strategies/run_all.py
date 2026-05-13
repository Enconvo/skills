"""
AU Strategy Evolution Engine
=============================
Runs all AU strategies, logs results to CSV, and prints a ranked summary.
"""

import subprocess
import sys
import os
import re
import pandas as pd
from datetime import datetime

STRATEGIES_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(STRATEGIES_DIR)
CSV_PATH = os.path.join(PROJECT_DIR, "au_results.csv")


def run_strategy(filepath):
    """Run a single strategy file and capture output."""
    name = os.path.basename(filepath).replace(".py", "")
    print(f"\n{'='*60}")
    print(f"  Running: {name}")
    print(f"{'='*60}")

    try:
        result = subprocess.run(
            [sys.executable, filepath],
            capture_output=True, text=True, timeout=120,
            cwd=PROJECT_DIR
        )
        output = result.stdout + result.stderr
        print(output[-2000:] if len(output) > 2000 else output)
        return name, output, result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"  TIMEOUT: {name}")
        return name, "TIMEOUT", False
    except Exception as e:
        print(f"  ERROR: {name}: {e}")
        return name, str(e), False


def parse_stats(output):
    """Parse backtesting.py stats from output."""
    stats = {}
    patterns = {
        "Return [%]": r"Return \[%\]\s+([-\d.]+)",
        "Sharpe Ratio": r"Sharpe Ratio\s+([-\d.]+)",
        "Sortino Ratio": r"Sortino Ratio\s+([-\d.]+)",
        "Max. Drawdown [%]": r"Max\. Drawdown \[%\]\s+([-\d.]+)",
        "# Trades": r"# Trades\s+(\d+)",
        "Win Rate [%]": r"Win Rate \[%\]\s+([-\d.]+)",
        "Profit Factor": r"Profit Factor\s+([-\d.]+)",
        "Expectancy [%]": r"Expectancy \[%\]\s+([-\d.]+)",
        "Equity Final [$]": r"Equity Final \[\$\]\s+([-\d.]+)",
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, output)
        if match:
            stats[key] = float(match.group(1))
    return stats


def main():
    # Find all strategy files (exclude run_all.py and __init__)
    files = sorted([
        os.path.join(STRATEGIES_DIR, f)
        for f in os.listdir(STRATEGIES_DIR)
        if f.endswith(".py") and f not in ("run_all.py", "__init__.py")
    ])

    print(f"\nFound {len(files)} strategies to run\n")

    results = []
    for filepath in files:
        name, output, success = run_strategy(filepath)
        if success:
            stats = parse_stats(output)
            if stats:
                stats["Strategy"] = name
                stats["Python File"] = os.path.basename(filepath)
                results.append(stats)

    if not results:
        print("\nNo successful backtests!")
        return

    # Save to CSV
    df = pd.DataFrame(results)
    cols = ["Strategy", "Python File", "Return [%]", "Max. Drawdown [%]",
            "Sharpe Ratio", "Sortino Ratio", "# Trades", "Win Rate [%]",
            "Profit Factor", "Expectancy [%]", "Equity Final [$]"]
    cols = [c for c in cols if c in df.columns]
    df = df[cols]
    df.to_csv(CSV_PATH, index=False)
    print(f"\nResults saved to {CSV_PATH}")

    # Print ranked summary
    print(f"\n{'='*80}")
    print(f"  AU STRATEGY RANKINGS (sorted by Return %)")
    print(f"{'='*80}")
    if "Return [%]" in df.columns:
        df_sorted = df.sort_values("Return [%]", ascending=False)
    else:
        df_sorted = df
    print(df_sorted.to_string(index=False))
    print(f"\n{'='*80}")


if __name__ == "__main__":
    main()
