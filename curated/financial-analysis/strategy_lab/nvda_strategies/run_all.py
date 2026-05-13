"""Run all NVDA strategies and produce ranked output."""
import subprocess
import sys
import os
import re
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)

results = []

# Find all strategy .py files (exclude run_all.py)
strategy_files = sorted([
    f for f in os.listdir(SCRIPT_DIR)
    if f.endswith('.py') and f != 'run_all.py' and f != '__init__.py'
])

print(f"Found {len(strategy_files)} strategies to run\n")
print("=" * 70)

for sf in strategy_files:
    filepath = os.path.join(SCRIPT_DIR, sf)
    print(f"\nRunning {sf}...")
    print("-" * 50)

    try:
        result = subprocess.run(
            [sys.executable, filepath],
            capture_output=True, text=True, timeout=120,
            cwd=PROJECT_DIR
        )
        output = result.stdout + result.stderr

        # Extract strategy name
        name_match = re.search(r'_strategy_name:\s*(.+)', output)
        name = name_match.group(1).strip() if name_match else sf.replace('.py', '')

        # Extract stats using regex
        def extract(pattern, text, default=0):
            m = re.search(pattern, text)
            if m:
                val = m.group(1).replace('%', '').strip()
                try:
                    return float(val)
                except:
                    return default
            return default

        ret = extract(r'Return \[%\]\s+([-\d.]+)', output)
        sharpe = extract(r'Sharpe Ratio\s+([-\d.]+)', output)
        sortino = extract(r'Sortino Ratio\s+([-\d.]+)', output)
        maxdd = extract(r'Max\. Drawdown \[%\]\s+([-\d.]+)', output)
        winrate = extract(r'Win Rate \[%\]\s+([-\d.]+)', output)
        trades = extract(r'# Trades\s+(\d+)', output)
        sqn = extract(r'SQN\s+([-\d.]+)', output)
        expectancy = extract(r'Expectancy \[%\]\s+([-\d.]+)', output)

        results.append({
            'Strategy': name,
            'File': sf,
            'Return%': ret,
            'Sharpe': sharpe,
            'Sortino': sortino,
            'MaxDD%': maxdd,
            'WinRate%': winrate,
            'Trades': int(trades),
            'SQN': sqn,
            'Expectancy%': expectancy,
            'Status': 'OK' if trades > 0 else 'NO TRADES'
        })

        if trades > 0:
            print(f"  Return: {ret:.1f}% | Sharpe: {sharpe:.2f} | "
                  f"Win: {winrate:.0f}% | Trades: {int(trades)} | DD: {maxdd:.1f}%")
        else:
            print(f"  NO TRADES — strategy conditions never triggered")

    except subprocess.TimeoutExpired:
        print(f"  TIMEOUT — skipped")
        results.append({'Strategy': sf, 'File': sf, 'Return%': 0, 'Status': 'TIMEOUT'})
    except Exception as e:
        print(f"  ERROR: {e}")
        results.append({'Strategy': sf, 'File': sf, 'Return%': 0, 'Status': f'ERROR: {e}'})

# Sort by return
df = pd.DataFrame(results)
df = df.sort_values('Return%', ascending=False).reset_index(drop=True)
df.index += 1  # 1-based ranking

# Save to CSV
csv_path = os.path.join(PROJECT_DIR, 'nvda_results.csv')
df.to_csv(csv_path, index_label='Rank')

# Print ranked summary
print("\n" + "=" * 70)
print("  NVDA STRATEGY RANKINGS")
print("=" * 70)
print(f"\n{'Rank':<5} {'Strategy':<30} {'Return%':>8} {'Sharpe':>7} {'WinRate':>8} {'Trades':>7} {'MaxDD%':>7} {'SQN':>6}")
print("-" * 82)
for idx, row in df.iterrows():
    print(f"{idx:<5} {row['Strategy']:<30} {row['Return%']:>7.1f}% {row.get('Sharpe',0):>7.2f} "
          f"{row.get('WinRate%',0):>7.0f}% {row.get('Trades',0):>7.0f} {row.get('MaxDD%',0):>7.1f}% {row.get('SQN',0):>6.2f}")

print(f"\nResults saved to {csv_path}")
