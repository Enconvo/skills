#!/usr/bin/env python3
"""
Run all META strategies and rank by performance
"""
import os
import sys
import pandas as pd
from backtesting import Backtest

sys.path.append("..")
from utils import load_meta_data

# Import all strategy modules
strategy_files = [f for f in os.listdir('.') if f.startswith('r') and f.endswith('.py') and f != 'run_all.py']

results = []
data = load_meta_data("1h")

print("="*80)
print(f"  运行 {len(strategy_files)} 个 META 策略")
print("="*80)
print()

for i, strategy_file in enumerate(sorted(strategy_files), 1):
    module_name = strategy_file[:-3]

    try:
        # Import the strategy module
        spec = __import__(module_name)

        # Find the Strategy class (look for class that inherits from Strategy)
        strategy_class = None
        for attr_name in dir(spec):
            attr = getattr(spec, attr_name)
            if isinstance(attr, type) and attr_name not in ['Strategy', 'Backtest']:
                try:
                    if issubclass(attr, __import__('backtesting').Strategy) and attr is not __import__('backtesting').Strategy:
                        strategy_class = attr
                        break
                except TypeError:
                    continue

        if strategy_class is None:
            print(f"❌ [{i}/{len(strategy_files)}] {strategy_file}: 找不到策略类")
            continue

        print(f"🔄 [{i}/{len(strategy_files)}] {strategy_file}...")

        # Run backtest
        bt = Backtest(data, strategy_class, cash=100_000, commission=.002)
        stats = bt.run()

        results.append({
            'Strategy': module_name,
            'Return [%]': stats['Return [%]'],
            'Sharpe Ratio': stats['Sharpe Ratio'],
            'Sortino Ratio': stats['Sortino Ratio'],
            'Max. Drawdown [%]': stats['Max. Drawdown [%]'],
            'Win Rate [%]': stats['Win Rate [%]'],
            'SQN': stats['SQN'],
            '# Trades': stats['# Trades'],
            'Avg. Trade [%]': stats['Avg. Trade [%]'],
        })

        print(f"   ✅ Return: {stats['Return [%]']:.1f}% | Sharpe: {stats['Sharpe Ratio']:.2f} | Trades: {stats['# Trades']}")

    except Exception as e:
        print(f"   ❌ 错误: {str(e)[:100]}")
        continue

print()
print("="*80)
print("  回测完成 - 按收益率排序")
print("="*80)
print()

# Create results DataFrame
df = pd.DataFrame(results)
df = df.sort_values('Return [%]', ascending=False)

# Print formatted results
print(df.to_string(index=False))
print()

# Save to CSV
df.to_csv("../meta_results_r1.csv", index=False)
print(f"✅ 结果已保存到 meta_results_r1.csv")
print()

# Analysis summary
print("="*80)
print("  第一轮分析")
print("="*80)
print()

top_3 = df.head(3)
print("🏆 前3名策略:")
for i, row in top_3.iterrows():
    print(f"   {row['Strategy']}: {row['Return [%]']:.1f}% (Sharpe: {row['Sharpe Ratio']:.2f}, Trades: {int(row['# Trades'])})")

print()

# Identify patterns
mean_reversion = df[df['Strategy'].str.contains('rsi|bollinger|keltner|williams|cci')]
trend_following = df[df['Strategy'].str.contains('golden|ema|macd|adx')]

print(f"📊 均值回归策略平均收益: {mean_reversion['Return [%]'].mean():.1f}%")
print(f"📊 趋势跟踪策略平均收益: {trend_following['Return [%]'].mean():.1f}%")
print()

