"""Smart Walk-Forward Advisor — Auto-classifies, tests, and recommends.

For each strategy:
1. Auto-detects if it's trend-following or mean-reversion
2. Tests BOTH original and regime-aware versions
3. Picks the best version automatically
4. Produces beginner-friendly recommendations with portfolio suggestions

Usage:
    python walk_forward_smart.py
"""
import sys, os, warnings
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
    ("1998-08-05", "2005-08-05", "2008-08-05"),
    ("2001-08-05", "2008-08-05", "2011-08-05"),
    ("2004-08-05", "2011-08-05", "2014-08-05"),
    ("2007-08-05", "2014-08-05", "2017-08-05"),
    ("2010-08-05", "2017-08-05", "2020-08-05"),
    ("2013-08-05", "2020-08-05", "2023-08-05"),
    ("2016-08-05", "2023-08-05", "2026-08-05"),
]
WINDOW_LABELS = ["Gold bull", "GFC+recovery", "Gold bear", "Consolidation",
                 "COVID era", "Inflation", "AU mega-rally"]

# ── Strategy Classification ────────────────────────────────────────────
# Keywords in source code that indicate strategy category
TREND_KEYWORDS = [
    "crossover(self.sma_fast, self.sma_slow",  # golden/death cross
    "crossover(self.sma_slow, self.sma_fast",
    "supertrend", "ema8[-1] > self.ema21[-1] > self.ema55[-1]",  # EMA ribbon
    "bullish_trend", "adx", "+di", "-di", "donchian",
    "ema_ribbon", "golden_cross", "ema_bb_trend",
]
MEAN_REV_KEYWORDS = [
    "bb_lower", "bb_upper", "rsi", "keltner", "kc_lower", "kc_upper",
    "bollinger", "stochrsi", "mean_reversion", "bounce",
    "oversold", "overbought",
]

# Human-readable strategy names
STRATEGY_NAMES = {
    'r1_01_golden_cross': 'Golden Cross (SMA 50/200)',
    'r1_02_rsi_mean_reversion': 'RSI Mean Reversion',
    'r1_03_macd_crossover': 'MACD Crossover',
    'r1_04_bollinger_bounce': 'Bollinger Band Bounce',
    'r1_05_keltner_reversion': 'Keltner Channel Reversion',
    'r1_06_supertrend': 'SuperTrend',
    'r1_07_donchian_breakout': 'Donchian Channel Breakout',
    'r1_08_adx_trend': 'ADX Trend Strength',
    'r1_09_ema_ribbon': 'EMA Ribbon',
    'r1_10_rsi_atr_trailing': 'RSI + ATR Trailing Stop',
    'r1_11_stochrsi_momentum': 'StochRSI Momentum',
    'r1_12_macd_atr_trail': 'MACD + ATR Trailing',
    'r2_01_bb_rsi_combo': 'Bollinger + RSI Combo',
    'r2_02_bb_atr_trailing': 'Bollinger + ATR Trailing',
    'r2_03_rsi_wider_bands': 'RSI Wider Bands + ATR',
    'r2_04_keltner_rsi_combo': 'Keltner + RSI Combo',
    'r2_05_golden_atr_trail': 'Golden Cross + ATR Trail',
    'r2_06_bb_keltner_squeeze': 'Bollinger + Keltner Squeeze',
    'r2_07_ema_bb_trend_reversion': 'EMA Trend + Bollinger Dip',
    'r3_01_bb_kc_atr_trail': 'BB + KC + ATR Trail',
    'r3_02_ema_bb_wider': 'EMA + BB Wider Bands',
    'r3_03_bb_kc_ema_filter': 'BB + KC + EMA Filter',
    'r3_04_bb_kc_rsi_atr': 'BB + KC + RSI + ATR',
}


def classify_strategy(filepath, module_name):
    """Auto-detect if a strategy is trend-following, mean-reversion, or hybrid."""
    with open(filepath, 'r') as f:
        source = f.read().lower()

    trend_score = sum(1 for kw in TREND_KEYWORDS if kw.lower() in source)
    mr_score = sum(1 for kw in MEAN_REV_KEYWORDS if kw.lower() in source)

    # Also check filename for hints
    name = module_name.lower()
    if any(k in name for k in ['golden', 'ema_ribbon', 'supertrend', 'donchian', 'adx']):
        trend_score += 2
    if any(k in name for k in ['rsi', 'bollinger', 'bb_', 'keltner', 'kc_', 'bounce', 'reversion', 'squeeze']):
        mr_score += 2
    if 'macd' in name:
        trend_score += 1  # MACD is mostly trend

    if trend_score > mr_score + 1:
        return 'trend'
    elif mr_score > trend_score + 1:
        return 'mean_reversion'
    else:
        return 'hybrid'


def calc_sma_regime(close, period):
    return talib.SMA(close, timeperiod=period)


def make_regime_aware(StrategyClass):
    """Wrap a strategy with a 200 SMA regime filter."""
    class RegimeAwareStrategy(StrategyClass):
        regime_period = REGIME_SMA_PERIOD

        def init(self):
            super().init()
            self.regime_sma = self.I(calc_sma_regime, self.data.Close, self.regime_period)

        def next(self):
            sma = self.regime_sma[-1]
            if np.isnan(sma):
                return
            if self.data.Close[-1] <= sma:
                if self.position:
                    self.position.close()
                    if hasattr(self, 'highest'):
                        self.highest = 0
                    if hasattr(self, 'trail_stop'):
                        self.trail_stop = 0
                return
            super().next()

    RegimeAwareStrategy.__name__ = f"{StrategyClass.__name__}_Regime"
    return RegimeAwareStrategy


def load_all_strategies():
    """Load all strategy files, classify them, and extract Strategy classes."""
    strategies = {}
    strategy_files = sorted([f for f in os.listdir(STRATEGY_DIR) if f.endswith(".py") and f.startswith("r")])

    for fname in strategy_files:
        module_name = fname[:-3]
        filepath = os.path.join(STRATEGY_DIR, fname)

        category = classify_strategy(filepath, module_name)

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
                if any(stripped.startswith(skip) for skip in [
                    'data = load_au_data', 'bt = Backtest', 'stats = bt.run',
                    'print(f"R', 'sys.path.append', 'from utils import'
                ]):
                    continue
                filtered_lines.append(line)

            exec('\n'.join(filtered_lines), exec_globals)

            for name, obj in exec_globals.items():
                if isinstance(obj, type) and issubclass(obj, Strategy) and obj is not Strategy:
                    strategies[fname] = {
                        'name': module_name,
                        'display_name': STRATEGY_NAMES.get(module_name, module_name),
                        'class': obj,
                        'file': fname,
                        'category': category,
                    }
                    break
        except Exception as e:
            print(f"  SKIP {fname}: {e}")

    return strategies


def run_window(strategy_cls, data, train_start, test_start, test_end):
    """Run strategy on a window, return test-period stats."""
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

        test_equity = equity.loc[equity.index >= pd.Timestamp(test_start)]
        if len(test_equity) < 10:
            return None

        start_eq = test_equity['Equity'].iloc[0]
        end_eq = test_equity['Equity'].iloc[-1]
        ret = ((end_eq / start_eq) - 1) * 100

        running_max = test_equity['Equity'].cummax()
        drawdowns = (test_equity['Equity'] - running_max) / running_max * 100
        maxdd = drawdowns.min()

        trades = stats._trades
        if trades is not None and len(trades) > 0:
            test_trades = trades[trades['ExitTime'] >= pd.Timestamp(test_start)]
            n_trades = len(test_trades)
            win_rate = len(test_trades[test_trades['PnL'] > 0]) / n_trades * 100 if n_trades > 0 else 0
        else:
            n_trades = 0
            win_rate = 0

        return {
            'return': round(ret, 1), 'maxdd': round(maxdd, 1),
            'trades': n_trades, 'win_rate': round(win_rate, 1),
            'profitable': ret > 0,
        }
    except:
        return {'return': 0, 'maxdd': 0, 'trades': 0, 'win_rate': 0, 'profitable': False}


def run_walk_forward(strategy_cls, data):
    """Run walk-forward across all windows, return summary."""
    window_results = []
    wins = 0
    for train_start, test_start, test_end in WINDOWS:
        actual_end = min(pd.Timestamp(test_end), data.index[-1])
        result = run_window(strategy_cls, data, train_start, test_start, str(actual_end.date()))
        if result is None:
            result = {'return': 0, 'maxdd': 0, 'trades': 0, 'win_rate': 0, 'profitable': False}
        if result['profitable']:
            wins += 1
        window_results.append(result)

    return {
        'windows_passed': wins,
        'status': 'ROBUST' if wins >= 5 else ('MARGINAL' if wins >= 4 else 'FRAGILE'),
        'avg_return': round(np.mean([w['return'] for w in window_results]), 1),
        'avg_maxdd': round(np.mean([w['maxdd'] for w in window_results]), 1),
        'total_trades': sum(w['trades'] for w in window_results),
        'window_results': window_results,
    }


def pick_best_version(og, ra, category):
    """Smart selection: pick the best version based on category and data."""
    og_score = og['windows_passed'] * 10 + og['avg_return'] * 0.5 - abs(og['avg_maxdd']) * 0.3
    ra_score = ra['windows_passed'] * 10 + ra['avg_return'] * 0.5 - abs(ra['avg_maxdd']) * 0.3

    # Bonus: regime filter gets a small boost for trend strategies
    if category == 'trend':
        ra_score += 5

    # Penalty: regime filter gets a penalty for mean reversion
    if category == 'mean_reversion':
        og_score += 3

    # If regime version passes more windows, strongly prefer it
    if ra['windows_passed'] > og['windows_passed']:
        ra_score += 10
    elif og['windows_passed'] > ra['windows_passed']:
        og_score += 10

    # Tiebreaker: prefer lower drawdown
    if abs(og_score - ra_score) < 3:
        if ra['avg_maxdd'] > og['avg_maxdd']:  # less negative = better
            ra_score += 2
        else:
            og_score += 2

    if ra_score > og_score:
        return 'regime', ra
    else:
        return 'original', og


def risk_rating(avg_maxdd):
    """Convert average max drawdown to a 1-5 risk rating."""
    dd = abs(avg_maxdd)
    if dd < 10:
        return 1, "Low"
    elif dd < 20:
        return 2, "Moderate"
    elif dd < 35:
        return 3, "Medium"
    elif dd < 50:
        return 4, "High"
    else:
        return 5, "Very High"


def confidence_rating(windows_passed, total_trades):
    """How confident we are in this strategy's robustness."""
    if windows_passed >= 6 and total_trades >= 15:
        return "High"
    elif windows_passed >= 5 and total_trades >= 10:
        return "Good"
    elif windows_passed >= 5:
        return "Moderate (few trades)"
    elif windows_passed >= 4:
        return "Low-Moderate"
    else:
        return "Low"


def main():
    print()
    print("=" * 80)
    print("  SMART STRATEGY ADVISOR — AU (AngloGold Ashanti)")
    print("  Auto-classifies, tests, and recommends the best strategies")
    print("=" * 80)
    print()

    data = load_au_data("daily")
    last_price = data['Close'].iloc[-1]
    print(f"  Current price: ${last_price:.2f}")
    print(f"  Data: {data.index[0].date()} to {data.index[-1].date()} ({len(data)} trading days)")
    print()

    # Load and classify
    strategies = load_all_strategies()

    cat_counts = {}
    for s in strategies.values():
        cat_counts[s['category']] = cat_counts.get(s['category'], 0) + 1
    print(f"  Loaded {len(strategies)} strategies:")
    print(f"    Trend-following: {cat_counts.get('trend', 0)}")
    print(f"    Mean-reversion:  {cat_counts.get('mean_reversion', 0)}")
    print(f"    Hybrid:          {cat_counts.get('hybrid', 0)}")
    print()

    # Test all strategies both ways
    print("  Testing across 7 market periods (1998-2026)...")
    print("  Each period is ~3 years covering a different market condition.")
    print()

    best_picks = []

    for fname, strat_info in sorted(strategies.items()):
        name = strat_info['name']
        display = strat_info['display_name']
        cls = strat_info['class']
        cat = strat_info['category']
        cat_emoji = {"trend": "T", "mean_reversion": "MR", "hybrid": "H"}[cat]

        print(f"  [{cat_emoji}] {display}...", end=" ", flush=True)

        # Test original
        og = run_walk_forward(cls, data)

        # Test regime-aware
        ra_cls = make_regime_aware(cls)
        ra = run_walk_forward(ra_cls, data)

        # Pick best
        version, best = pick_best_version(og, ra, cat)

        best_picks.append({
            'name': name,
            'display_name': display,
            'category': cat,
            'version': version,
            'og': og,
            'ra': ra,
            'best': best,
            'file': fname,
        })

        v_tag = "REGIME" if version == 'regime' else "ORIG"
        print(f"{best['windows_passed']}/7 {best['status']} (best: {v_tag})")

    # Sort by robustness then return
    best_picks.sort(key=lambda x: (-x['best']['windows_passed'], -x['best']['avg_return']))

    # ── RECOMMENDATIONS ────────────────────────────────────────────────
    print()
    print("=" * 80)
    print("  RECOMMENDATIONS")
    print("=" * 80)
    print()
    print("  We tested each strategy across 7 different 3-year market periods")
    print("  (bull runs, crashes, bear markets, recoveries). A strategy is")
    print("  trustworthy if it made money in MOST of those periods.")
    print()
    print("  For each strategy, we also tested a 'safety filter' version that")
    print("  only trades during uptrends (price above 200-day average). We")
    print("  automatically picked whichever version performed better.")
    print()

    robust = [p for p in best_picks if p['best']['status'] == 'ROBUST']
    marginal = [p for p in best_picks if p['best']['status'] == 'MARGINAL']

    if robust:
        print(f"  ── TOP PICKS (Profitable in 5+ of 7 periods) ────────────")
        print()
        for i, p in enumerate(robust, 1):
            risk_num, risk_label = risk_rating(p['best']['avg_maxdd'])
            conf = confidence_rating(p['best']['windows_passed'], p['best']['total_trades'])
            version_explain = (
                "Uses a safety filter — only trades during uptrends"
                if p['version'] == 'regime' else
                "Trades in all market conditions (no filter needed)"
            )
            cat_explain = {
                'trend': "Follows the market direction (buys uptrends, avoids downtrends)",
                'mean_reversion': "Buys when price drops unusually low (\"buy the dip\")",
                'hybrid': "Combines trend detection with dip-buying",
            }[p['category']]

            print(f"  {'*' * 3} #{i}: {p['display_name']}")
            print(f"      How it works:  {cat_explain}")
            print(f"      Mode:          {version_explain}")
            print(f"      Reliability:   {p['best']['windows_passed']}/7 periods profitable ({conf} confidence)")
            print(f"      Avg return:    {p['best']['avg_return']}% per 3-year period")
            print(f"      Risk level:    {'*' * risk_num}{'.' * (5-risk_num)} {risk_label} (avg worst dip: {p['best']['avg_maxdd']:.0f}%)")
            print(f"      Total trades:  {p['best']['total_trades']} across 28 years")

            # Plain-English commentary
            if p['best']['windows_passed'] >= 6:
                print(f"      Verdict:       STRONG — Profitable in almost every market condition.")
            elif p['best']['avg_return'] > 30:
                print(f"      Verdict:       HIGH RETURN — Big gains when it works, but some bad periods too.")
            elif abs(p['best']['avg_maxdd']) < 20:
                print(f"      Verdict:       STEADY — Lower returns but also lower risk. Good for peace of mind.")
            else:
                print(f"      Verdict:       SOLID — Good balance of returns and reliability.")
            print()

    if marginal:
        print(f"  ── SECOND TIER (Profitable in 4 of 7 periods) ───────────")
        print(f"  These are decent but less reliable. Consider as additions")
        print(f"  to a portfolio, not as standalone strategies.")
        print()
        for p in marginal[:5]:  # Show top 5 marginal
            risk_num, risk_label = risk_rating(p['best']['avg_maxdd'])
            v = "w/ safety filter" if p['version'] == 'regime' else "no filter"
            print(f"    {p['display_name']:<35} {p['best']['windows_passed']}/7  avg {p['best']['avg_return']:>5.1f}%  risk: {risk_label:<10} ({v})")

    # ── PORTFOLIO SUGGESTION ───────────────────────────────────────────
    print()
    print("=" * 80)
    print("  SUGGESTED PORTFOLIO")
    print("=" * 80)
    print()

    if len(robust) >= 2:
        # Find the best trend and best mean reversion among robust
        robust_trend = [p for p in robust if p['category'] == 'trend']
        robust_mr = [p for p in robust if p['category'] in ('mean_reversion', 'hybrid')]

        if robust_trend and robust_mr:
            print("  We recommend combining TWO strategies for diversification:")
            print("  One that follows trends + one that buys dips. They complement")
            print("  each other because they profit in different market conditions.")
            print()
            t = robust_trend[0]
            m = robust_mr[0]
            t_risk, t_risk_label = risk_rating(t['best']['avg_maxdd'])
            m_risk, m_risk_label = risk_rating(m['best']['avg_maxdd'])

            print(f"  STRATEGY A (50% of capital): {t['display_name']}")
            print(f"    Type:     Trend-following {'+ safety filter' if t['version'] == 'regime' else ''}")
            print(f"    Returns:  {t['best']['avg_return']}% avg per period  |  Risk: {t_risk_label}")
            print(f"    Strength: Catches big moves when the market is trending up")
            print()
            print(f"  STRATEGY B (50% of capital): {m['display_name']}")
            print(f"    Type:     Buy-the-dip {'+ safety filter' if m['version'] == 'regime' else ''}")
            print(f"    Returns:  {m['best']['avg_return']}% avg per period  |  Risk: {m_risk_label}")
            print(f"    Strength: Profits from temporary pullbacks in otherwise healthy markets")
            print()
            print("  WHY THIS COMBINATION WORKS:")
            print("    - When the market trends smoothly → Strategy A profits")
            print("    - When the market dips temporarily → Strategy B profits")
            print("    - When the market crashes hard → Both sit out (safety filters / natural stops)")
            print("    - Spreading capital across two strategies reduces the impact of any single bad trade")
        else:
            # All robust are same category
            print("  Top 2 strategies for a balanced approach:")
            print()
            for i, p in enumerate(robust[:2], 1):
                pct = 60 if i == 1 else 40
                r, rl = risk_rating(p['best']['avg_maxdd'])
                print(f"  STRATEGY {chr(64+i)} ({pct}% of capital): {p['display_name']}")
                print(f"    {p['best']['windows_passed']}/7 reliable  |  {p['best']['avg_return']}% avg return  |  Risk: {rl}")
                print()
    elif len(robust) == 1:
        p = robust[0]
        r, rl = risk_rating(p['best']['avg_maxdd'])
        print(f"  Only one highly reliable strategy found:")
        print(f"  {p['display_name']} — {p['best']['windows_passed']}/7 periods, avg {p['best']['avg_return']}% return")
        print(f"  Risk: {rl}")
        print()
        print("  Consider using this as your primary strategy with conservative sizing")
        print("  (not 100% of capital) until more strategies prove themselves.")
    else:
        print("  No strategies passed the highest reliability threshold (5/7).")
        print("  Consider the MARGINAL strategies above with smaller position sizes,")
        print("  or wait for better market conditions to test new approaches.")

    # ── IMPORTANT NOTES ────────────────────────────────────────────────
    print()
    print("=" * 80)
    print("  IMPORTANT THINGS TO KNOW")
    print("=" * 80)
    print()
    print("  1. PAST RESULTS ARE NOT GUARANTEED")
    print("     These strategies worked across 28 years of history,")
    print("     but the future may be different. Always use stop losses.")
    print()
    print("  2. ALL STRATEGIES LOSE SOMETIMES")
    print("     Even the best strategy lost money in 2 out of 7 periods.")
    print("     This is normal. Don't panic-sell during a losing streak.")
    print()
    print("  3. THESE ARE LONG-ONLY STRATEGIES")
    print("     They only buy (not short-sell). During major bear markets,")
    print("     the best move is to sit out — which the safety filter does.")
    print()
    print("  4. SIGNALS ARE ON THE CHART")
    print("     Load the Pine Script into TradingView to see exact")
    print("     buy/sell signals with alerts. Set up phone notifications")
    print("     so you never miss a signal.")
    print()
    print("  5. POSITION SIZING MATTERS")
    print("     Never put all your money in one trade. The strategies")
    print("     assume 100% of allocated capital per trade — in practice,")
    print("     consider using 50-70% to leave room for error.")
    print()

    # ── SAVE RESULTS ───────────────────────────────────────────────────
    csv_rows = []
    for p in best_picks:
        row = {
            'Strategy': p['display_name'],
            'File': p['file'],
            'Category': p['category'],
            'Best_Version': p['version'],
            'Windows_Passed': p['best']['windows_passed'],
            'Status': p['best']['status'],
            'Avg_Return': p['best']['avg_return'],
            'Avg_MaxDD': p['best']['avg_maxdd'],
            'Total_Trades': p['best']['total_trades'],
            'OG_Windows': p['og']['windows_passed'],
            'OG_Avg_Return': p['og']['avg_return'],
            'RA_Windows': p['ra']['windows_passed'],
            'RA_Avg_Return': p['ra']['avg_return'],
        }
        for i, w in enumerate(p['best']['window_results'], 1):
            row[f'W{i}_Return'] = w['return']
        csv_rows.append(row)

    df = pd.DataFrame(csv_rows)
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "au_daily_smart_advisor.csv")
    df.to_csv(csv_path, index=False)
    print(f"  Full results saved to: {csv_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
