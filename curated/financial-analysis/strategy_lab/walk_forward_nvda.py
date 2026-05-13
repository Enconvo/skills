"""Smart Walk-Forward Advisor — NVDA
Auto-classifies, dual-tests, and recommends the best NVDA strategies.

Uses auto-detected market regimes from regime_detector.py instead of
hardcoded windows. Regimes are identified from rolling returns + volatility
with percentile-based thresholds that adapt to NVDA's volatility profile.
"""
import sys, os, warnings
import pandas as pd
import numpy as np
import talib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import load_nvda_data
from regime_detector import detect_regimes, regimes_to_windows, print_regime_report
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

warnings.filterwarnings("ignore")

# ── Configuration ──────────────────────────────────────────────────────
STRATEGY_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nvda_strategies")
CASH = 1_000_000
COMMISSION = 0.001
REGIME_SMA_PERIOD = 200

# Windows and labels are auto-detected at runtime (see main())
WINDOWS = None
WINDOW_LABELS = None

# ── Strategy Classification ────────────────────────────────────────────
TREND_KEYWORDS = [
    "crossover(self.sma_fast, self.sma_slow", "supertrend",
    "ema8[-1] > self.ema21[-1]", "adx", "donchian",
    "ema_ribbon", "golden_cross", "macd_crossover",
]
MEAN_REV_KEYWORDS = [
    "bb_lower", "bb_upper", "rsi", "keltner", "kc_lower", "kc_upper",
    "bollinger", "stochrsi", "mean_reversion", "bounce", "oversold",
]
GAP_KEYWORDS = [
    "gap", "gap_pct", "gap_threshold", "gap_min", "breakout",
    "open[-1] > self.data.high[-2]", "premarket",
]

STRATEGY_NAMES = {
    'r1_01_golden_cross': 'Golden Cross (SMA 50/200)',
    'r1_02_rsi_mean_reversion': 'RSI Mean Reversion',
    'r1_03_bollinger_bounce': 'Bollinger Band Bounce',
    'r1_04_macd_crossover': 'MACD Crossover',
    'r1_05_donchian_breakout': 'Donchian Channel Breakout',
    'r1_06_supertrend': 'SuperTrend',
    'r1_07_ema_ribbon': 'EMA Ribbon',
    'r1_08_atr_breakout': 'ATR Volatility Breakout',
    'r1_09_stochrsi_oversold': 'StochRSI Oversold',
    'r1_10_adx_trend': 'ADX Trend Strength',
    'r1_11_keltner_reversion': 'Keltner Channel Reversion',
    'r1_12_bb_keltner_squeeze': 'BB + Keltner Squeeze',
    'r1_13_gap_and_go': 'Gap-and-Go',
    'r1_14_gap_fade': 'Gap Fade',
    'r1_15_overnight_gap_reversal': 'Overnight Gap Reversal',
    'r1_16_premarket_breakout': 'Pre-Market Breakout',
    'r1_17_gap_momentum_filter': 'Gap Momentum Filter',
    'r2_01_rsi_atr_trailing': 'RSI + ATR Trailing',
    'r2_02_macd_adx_filter': 'MACD + ADX Filter',
    'r2_03_keltner_rsi_confluence': 'Keltner + RSI Confluence',
    'r2_04_atr_breakout_trailing': 'ATR Breakout + Trailing',
    'r2_05_bb_ema_filter': 'Bollinger + EMA Filter',
    'r2_06_mean_rev_regime_switch': 'Mean Rev Regime Switch',
    'r2_07_squeeze_atr_trail': 'Squeeze + ATR Trail',
    'r2_08_keltner_atr_trailing': 'Keltner + ATR Trailing',
    'r2_09_gap_go_tight_trail': 'Gap-Go Tight Trail',
    'r2_10_gap_keltner_hybrid': 'Gap + Keltner Hybrid',
    'r2_11_gap_rsi_confirmation': 'Gap RSI Confirmation',
    'r2_12_premarket_macd_hybrid': 'PreMarket MACD Hybrid',
    'r3_01_macd_atr_trail': 'MACD + ATR Trail (R3)',
    'r3_02_rsi_macd_hybrid': 'RSI + MACD Hybrid (R3)',
    'r3_03_safe_momentum': 'Safe Momentum (R3)',
    'r3_04_gap_aggressive': 'Gap Aggressive (R3)',
    'r3_05_gap_regime_safe': 'Gap Regime Safe (R3)',
    'r3_06_gap_expectancy_max': 'Gap Expectancy Max (R3)',
}


def classify_strategy(filepath, module_name):
    """Auto-detect strategy category."""
    with open(filepath, 'r') as f:
        source = f.read().lower()

    trend_score = sum(1 for kw in TREND_KEYWORDS if kw.lower() in source)
    mr_score = sum(1 for kw in MEAN_REV_KEYWORDS if kw.lower() in source)
    gap_score = sum(1 for kw in GAP_KEYWORDS if kw.lower() in source)

    name = module_name.lower()
    if any(k in name for k in ['gap', 'premarket']):
        gap_score += 3
    if any(k in name for k in ['golden', 'ema_ribbon', 'supertrend', 'donchian', 'adx']):
        trend_score += 2
    if any(k in name for k in ['rsi', 'bollinger', 'bb_', 'keltner', 'kc_', 'bounce', 'reversion', 'squeeze']):
        mr_score += 2
    if 'macd' in name:
        trend_score += 1

    if gap_score > trend_score and gap_score > mr_score:
        return 'gap_momentum'
    elif trend_score > mr_score + 1:
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
    """Load all strategy files, classify them, extract Strategy classes."""
    strategies = {}
    skip_files = ['run_all.py', 'last_bar_state.py', '__init__.py']
    strategy_files = sorted([
        f for f in os.listdir(STRATEGY_DIR)
        if f.endswith(".py") and f.startswith("r") and f not in skip_files
    ])

    for fname in strategy_files:
        module_name = fname[:-3]
        filepath = os.path.join(STRATEGY_DIR, fname)
        category = classify_strategy(filepath, module_name)

        try:
            with open(filepath, 'r') as f:
                source = f.read()

            exec_globals = {
                '__builtins__': __builtins__,
                'sys': sys, 'os': os, 'np': np, 'numpy': np, 'pd': pd,
                'talib': talib,
                'Strategy': Strategy, 'Backtest': Backtest, 'crossover': crossover,
                'load_nvda_data': lambda *a, **kw: pd.DataFrame(),
            }

            filtered_lines = []
            for line in source.split('\n'):
                stripped = line.strip()
                if any(stripped.startswith(skip) for skip in [
                    'data = load_nvda_data', 'bt = Backtest', 'stats = bt.run',
                    'print(', 'sys.path.append', 'from utils import'
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

    if len(window_data) < 50:
        return None

    try:
        bt = Backtest(window_data, strategy_cls, cash=CASH, commission=COMMISSION, exclusive_orders=True)
        stats = bt.run()

        equity = stats._equity_curve
        if equity is None or len(equity) == 0:
            return None

        test_equity = equity.loc[equity.index >= pd.Timestamp(test_start)]
        if len(test_equity) < 5:
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
    except Exception:
        return {'return': 0, 'maxdd': 0, 'trades': 0, 'win_rate': 0, 'profitable': False}


def run_walk_forward(strategy_cls, data, windows=None):
    """Run walk-forward across all windows, return summary."""
    if windows is None:
        windows = WINDOWS
    n_windows = len(windows)
    window_results = []
    wins = 0
    for train_start, test_start, test_end in windows:
        actual_end = min(pd.Timestamp(test_end), data.index[-1])
        result = run_window(strategy_cls, data, train_start, test_start, str(actual_end.date()))
        if result is None:
            result = {'return': 0, 'maxdd': 0, 'trades': 0, 'win_rate': 0, 'profitable': False}
        if result['profitable']:
            wins += 1
        window_results.append(result)

    # Dynamic thresholds: ROBUST >= 75%, MARGINAL >= 50%
    robust_threshold = max(1, int(np.ceil(n_windows * 0.75)))
    marginal_threshold = max(1, int(np.ceil(n_windows * 0.50)))

    if wins >= robust_threshold:
        status = 'ROBUST'
    elif wins >= marginal_threshold:
        status = 'MARGINAL'
    else:
        status = 'FRAGILE'

    return {
        'windows_passed': wins,
        'n_windows': n_windows,
        'status': status,
        'avg_return': round(np.mean([w['return'] for w in window_results]), 1),
        'avg_maxdd': round(np.mean([w['maxdd'] for w in window_results]), 1),
        'total_trades': sum(w['trades'] for w in window_results),
        'window_results': window_results,
    }


def pick_best_version(og, ra, category):
    """Smart selection: pick best version based on category."""
    og_score = og['windows_passed'] * 10 + og['avg_return'] * 0.5 - abs(og['avg_maxdd']) * 0.3
    ra_score = ra['windows_passed'] * 10 + ra['avg_return'] * 0.5 - abs(ra['avg_maxdd']) * 0.3

    if category == 'trend':
        ra_score += 5
    if category == 'mean_reversion':
        og_score += 3
    # Gap strategies are momentum — regime filter can help
    if category == 'gap_momentum':
        ra_score += 3

    if ra['windows_passed'] > og['windows_passed']:
        ra_score += 10
    elif og['windows_passed'] > ra['windows_passed']:
        og_score += 10

    if abs(og_score - ra_score) < 3:
        if ra['avg_maxdd'] > og['avg_maxdd']:
            ra_score += 2
        else:
            og_score += 2

    if ra_score > og_score:
        return 'regime', ra
    else:
        return 'original', og


def risk_rating(avg_maxdd):
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


def confidence_rating(windows_passed, total_trades, n_windows=9):
    pct = windows_passed / n_windows if n_windows > 0 else 0
    if pct >= 0.85 and total_trades >= 15:
        return "High"
    elif pct >= 0.75 and total_trades >= 10:
        return "Good"
    elif pct >= 0.75:
        return "Moderate (few trades)"
    elif pct >= 0.50:
        return "Low-Moderate"
    else:
        return "Low"


def main():
    global WINDOWS, WINDOW_LABELS

    print()
    print("=" * 80)
    print("  SMART STRATEGY ADVISOR — NVDA (NVIDIA)")
    print("  Auto-classifies, tests, and recommends the best strategies")
    print("  Regimes: auto-detected from data (not hardcoded)")
    print("=" * 80)
    print()

    data = load_nvda_data("daily")
    last_price = data['Close'].iloc[-1]
    print(f"  Current price: ${last_price:.2f}")
    print(f"  Data: {data.index[0].date()} to {data.index[-1].date()} ({len(data)} trading days)")

    # Auto-detect market regimes
    regimes = detect_regimes(data)
    print_regime_report(regimes, ticker="NVDA")
    WINDOWS, WINDOW_LABELS = regimes_to_windows(regimes, data)
    n_windows = len(WINDOWS)

    strategies = load_all_strategies()

    cat_counts = {}
    for s in strategies.values():
        cat_counts[s['category']] = cat_counts.get(s['category'], 0) + 1
    print(f"  Loaded {len(strategies)} strategies:")
    print(f"    Gap/Momentum:    {cat_counts.get('gap_momentum', 0)}")
    print(f"    Trend-following: {cat_counts.get('trend', 0)}")
    print(f"    Mean-reversion:  {cat_counts.get('mean_reversion', 0)}")
    print(f"    Hybrid:          {cat_counts.get('hybrid', 0)}")
    print()

    print(f"  Testing across {n_windows} auto-detected market regimes...")
    print(f"  ROBUST >= {max(1, int(np.ceil(n_windows * 0.75)))}/{n_windows} | "
          f"MARGINAL >= {max(1, int(np.ceil(n_windows * 0.50)))}/{n_windows} | "
          f"FRAGILE < {max(1, int(np.ceil(n_windows * 0.50)))}/{n_windows}")
    print()

    best_picks = []

    for fname, strat_info in sorted(strategies.items()):
        name = strat_info['name']
        display = strat_info['display_name']
        cls = strat_info['class']
        cat = strat_info['category']
        cat_tag = {"trend": "T", "mean_reversion": "MR", "hybrid": "H", "gap_momentum": "G"}[cat]

        print(f"  [{cat_tag}] {display}...", end=" ", flush=True)

        og = run_walk_forward(cls, data, WINDOWS)
        ra_cls = make_regime_aware(cls)
        ra = run_walk_forward(ra_cls, data, WINDOWS)
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
        print(f"{best['windows_passed']}/{best['n_windows']} {best['status']} (best: {v_tag})")

    best_picks.sort(key=lambda x: (-x['best']['windows_passed'], -x['best']['avg_return']))

    # ── RECOMMENDATIONS ──
    print()
    print("=" * 80)
    print("  RECOMMENDATIONS")
    print("=" * 80)
    print()
    print(f"  We tested each strategy across {n_windows} auto-detected market regimes.")
    print("  Regimes were identified from rolling returns and volatility — no manual")
    print("  labeling. A strategy is trustworthy if it made money in MOST regimes.")
    print()
    print("  For each strategy, we also tested a 'safety filter' version that")
    print("  only trades during uptrends (price above 200-day average). We")
    print("  automatically picked whichever version performed better.")
    print()

    robust_threshold = max(1, int(np.ceil(n_windows * 0.75)))
    marginal_threshold = max(1, int(np.ceil(n_windows * 0.50)))
    robust = [p for p in best_picks if p['best']['status'] == 'ROBUST']
    marginal = [p for p in best_picks if p['best']['status'] == 'MARGINAL']

    if robust:
        print(f"  -- TOP PICKS (Profitable in {robust_threshold}+ of {n_windows} regimes) ----")
        print()
        for i, p in enumerate(robust, 1):
            risk_num, risk_label = risk_rating(p['best']['avg_maxdd'])
            conf = confidence_rating(p['best']['windows_passed'], p['best']['total_trades'], n_windows)
            version_explain = (
                "Uses a safety filter -- only trades during uptrends"
                if p['version'] == 'regime' else
                "Trades in all market conditions (no filter needed)"
            )
            cat_explain = {
                'trend': "Follows the market direction (buys uptrends, avoids downtrends)",
                'mean_reversion': "Buys when price drops unusually low (\"buy the dip\")",
                'hybrid': "Combines trend detection with dip-buying",
                'gap_momentum': "Buys after strong overnight gaps up (momentum continuation)",
            }[p['category']]

            print(f"  *** #{i}: {p['display_name']}")
            print(f"      How it works:  {cat_explain}")
            print(f"      Mode:          {version_explain}")
            print(f"      Reliability:   {p['best']['windows_passed']}/{n_windows} periods profitable ({conf} confidence)")
            print(f"      Avg return:    {p['best']['avg_return']}% per ~1yr period")
            print(f"      Risk level:    {'*' * risk_num}{'.' * (5-risk_num)} {risk_label} (avg worst dip: {p['best']['avg_maxdd']:.0f}%)")
            n_years = round((data.index[-1] - data.index[0]).days / 365.25, 1)
            print(f"      Total trades:  {p['best']['total_trades']} across {n_years} years")

            if p['best']['windows_passed'] >= int(np.ceil(n_windows * 0.85)):
                print(f"      Verdict:       STRONG -- Profitable in almost every regime tested.")
            elif p['best']['avg_return'] > 50:
                print(f"      Verdict:       HIGH RETURN -- Big gains when it works.")
            elif abs(p['best']['avg_maxdd']) < 20:
                print(f"      Verdict:       STEADY -- Lower returns but also lower risk.")
            else:
                print(f"      Verdict:       SOLID -- Good balance of returns and reliability.")
            print()

    if marginal:
        print(f"  -- SECOND TIER (Profitable in {marginal_threshold}-{robust_threshold-1} of {n_windows} regimes) ----")
        print(f"  Decent but less reliable. Consider as additions, not standalone.")
        print()
        for p in marginal[:8]:
            risk_num, risk_label = risk_rating(p['best']['avg_maxdd'])
            v = "w/ safety filter" if p['version'] == 'regime' else "no filter"
            print(f"    {p['display_name']:<35} {p['best']['windows_passed']}/{n_windows}  avg {p['best']['avg_return']:>6.1f}%  risk: {risk_label:<10} ({v})")

    fragile = [p for p in best_picks if p['best']['status'] == 'FRAGILE']
    if fragile:
        print()
        print(f"  -- FRAGILE (Profitable in <{marginal_threshold} of {n_windows} regimes) -- NOT RECOMMENDED")
        for p in fragile:
            print(f"    {p['display_name']:<35} {p['best']['windows_passed']}/{n_windows}  avg {p['best']['avg_return']:>6.1f}%")

    # ── PORTFOLIO SUGGESTION ──
    print()
    print("=" * 80)
    print("  SUGGESTED PORTFOLIO")
    print("=" * 80)
    print()

    if len(robust) >= 2:
        robust_gap = [p for p in robust if p['category'] == 'gap_momentum']
        robust_other = [p for p in robust if p['category'] != 'gap_momentum']

        if robust_gap and robust_other:
            print("  We recommend combining TWO strategies for diversification:")
            print("  One gap/momentum strategy + one non-gap strategy.")
            print()
            g = robust_gap[0]
            o = robust_other[0]
            g_risk, g_rl = risk_rating(g['best']['avg_maxdd'])
            o_risk, o_rl = risk_rating(o['best']['avg_maxdd'])

            print(f"  STRATEGY A (50% of capital): {g['display_name']}")
            print(f"    Type:     Gap momentum {'+ safety filter' if g['version'] == 'regime' else ''}")
            print(f"    Returns:  {g['best']['avg_return']}% avg per period  |  Risk: {g_rl}")
            print(f"    Strength: Catches strong overnight gaps -- institutional buying signals")
            print()
            print(f"  STRATEGY B (50% of capital): {o['display_name']}")
            print(f"    Type:     {o['category'].replace('_', ' ').title()} {'+ safety filter' if o['version'] == 'regime' else ''}")
            print(f"    Returns:  {o['best']['avg_return']}% avg per period  |  Risk: {o_rl}")
            print(f"    Strength: Trades different signals for diversified entries")
            print()
        else:
            print("  Top 2 robust strategies:")
            print()
            for i, p in enumerate(robust[:2], 1):
                pct = 60 if i == 1 else 40
                r, rl = risk_rating(p['best']['avg_maxdd'])
                print(f"  STRATEGY {chr(64+i)} ({pct}% of capital): {p['display_name']}")
                print(f"    {p['best']['windows_passed']}/{n_windows} reliable  |  {p['best']['avg_return']}% avg return  |  Risk: {rl}")
                print()
    elif len(robust) == 1:
        p = robust[0]
        r, rl = risk_rating(p['best']['avg_maxdd'])
        print(f"  Only one highly reliable strategy found:")
        print(f"  {p['display_name']} -- {p['best']['windows_passed']}/{n_windows} periods, avg {p['best']['avg_return']}% return")
        print(f"  Risk: {rl}")
        print()
        print("  Use conservative sizing (50-70% of capital) until more strategies prove out.")
    else:
        print(f"  No strategies passed the highest reliability threshold ({robust_threshold}/{n_windows}).")
        print("  Consider MARGINAL strategies with smaller position sizes.")

    # ── IMPORTANT NOTES ──
    print()
    print("=" * 80)
    print("  IMPORTANT THINGS TO KNOW")
    print("=" * 80)
    print()
    print("  1. PAST RESULTS ARE NOT GUARANTEED")
    print("     NVDA is an exceptional growth stock. These strategies are optimized")
    print("     for momentum -- they may not work if NVDA's growth story changes.")
    print()
    print("  2. ALL STRATEGIES LOSE SOMETIMES")
    print("     Bear regimes tested all strategies. Some survived, some didn't.")
    print("     Don't panic-sell during a losing streak -- follow the signals.")
    print()
    print("  3. NVDA IS VOLATILE")
    print("     20-50% drawdowns are NORMAL for NVDA. These strategies have trailing")
    print("     stops to limit losses, but expect larger swings than with stable stocks.")
    print()
    print("  4. SIGNALS ARE ON THE CHART")
    print("     Load the Pine Script into TradingView to see exact buy/sell signals")
    print("     with alerts. Set up phone notifications.")
    print()
    print("  5. POSITION SIZING MATTERS")
    print("     Never put all your money in one trade. Consider 50-70% of allocated")
    print("     capital per trade to leave room for error.")
    print()

    # ── SAVE RESULTS ──
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
            label = WINDOW_LABELS[i-1] if i-1 < len(WINDOW_LABELS) else f"W{i}"
            row[f'W{i}_{label}_Return'] = w['return']
        csv_rows.append(row)

    df = pd.DataFrame(csv_rows)
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nvda_smart_advisor.csv")
    df.to_csv(csv_path, index=False)
    print(f"  Full results saved to: {csv_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
