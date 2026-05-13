"""Auto-detect market regimes from price data.

Replaces hardcoded walk-forward windows with data-driven regime detection.
Uses smoothed rolling returns with percentile-based thresholds that
auto-adapt to any ticker's volatility profile.

Usage:
    from regime_detector import detect_regimes, regimes_to_windows, print_regime_report

    regimes = detect_regimes(df)
    print_regime_report(regimes, ticker="NVDA")
    windows, labels = regimes_to_windows(regimes, df)
"""
import pandas as pd
import numpy as np


def detect_regimes(df, return_window=120, smooth_window=None, vol_window=60,
                   min_segment_bars=None, target_regimes=10,
                   bull_percentile=75, bear_percentile=25):
    """Auto-detect market regimes from OHLCV data.

    Two-stage smoothing: rolling return over return_window, then an additional
    moving average of smooth_window to eliminate noise. Percentile-based
    thresholds auto-adapt to any stock's volatility profile.

    Parameters auto-scale with data length to produce ~target_regimes regimes
    regardless of whether the dataset is 2 years or 28 years.

    After segmentation and merging, segments are re-labeled by their actual
    total return (not bar-level classification) to avoid misleading labels.

    Args:
        df: DataFrame with DatetimeIndex and 'Close' column
        return_window: Rolling return lookback in trading days (default 120 ~ 6 months)
        smooth_window: Secondary MA to smooth rolling returns (auto-scaled if None)
        vol_window: Rolling volatility lookback (default 60 ~ 3 months)
        min_segment_bars: Minimum bars per regime; auto-scaled if None
        target_regimes: Approximate number of regimes to detect (default 10)
        bull_percentile: Percentile above which smoothed return = bull (default 75)
        bear_percentile: Percentile below which smoothed return = bear (default 25)

    Returns:
        List of dicts: [{start, end, label, bars, total_return, annualized_vol}, ...]
        Labels: 'bull', 'bear', 'consolidation', 'choppy'
    """
    n_bars = len(df)
    if n_bars < 30:
        raise ValueError(f"Need at least 30 bars of data, got {n_bars}")

    # Auto-scale return_window to available data (cap at 40% of dataset)
    max_return_window = max(20, n_bars * 2 // 5)
    if return_window > max_return_window:
        return_window = max_return_window

    # Auto-scale vol_window similarly
    if vol_window > max_return_window:
        vol_window = max(20, max_return_window // 2)

    # Auto-scale smoothing and segment size to data length
    if smooth_window is None:
        smooth_window = max(10, n_bars // 50)
    if min_segment_bars is None:
        min_segment_bars = max(20, n_bars // (target_regimes * 2))

    if isinstance(df, pd.Series):
        close = df
    else:
        close = df['Close']

    # Step 1: Rolling return (lookback scaled to data)
    rolling_return = close.pct_change(return_window) * 100

    # Step 2: Smooth with additional MA to kill oscillations
    smooth_return = rolling_return.rolling(smooth_window, min_periods=1).mean()

    # Step 3: Rolling annualized volatility
    daily_returns = close.pct_change()
    rolling_vol = daily_returns.rolling(vol_window).std() * np.sqrt(252) * 100

    # Step 4: Percentile thresholds from full history
    valid_returns = smooth_return.dropna()
    if len(valid_returns) < 10:
        raise ValueError(f"Not enough valid data ({len(valid_returns)} bars after warmup) for regime detection")

    bull_thresh = np.percentile(valid_returns, bull_percentile)
    bear_thresh = np.percentile(valid_returns, bear_percentile)
    vol_median = rolling_vol.dropna().median()

    # Step 5: Classify each bar
    bar_labels = []
    for i in range(len(df)):
        ret = smooth_return.iloc[i]
        vol = rolling_vol.iloc[i]

        if pd.isna(ret) or pd.isna(vol):
            bar_labels.append('warmup')
        elif ret > bull_thresh:
            bar_labels.append('bull')
        elif ret < bear_thresh:
            bar_labels.append('bear')
        elif vol < vol_median * 0.8:
            bar_labels.append('consolidation')
        else:
            bar_labels.append('choppy')

    # Step 6: Group consecutive same-label bars into raw segments
    segments = []
    current = bar_labels[0]
    seg_start = 0

    for i in range(1, len(bar_labels)):
        if bar_labels[i] != current:
            if current != 'warmup':
                segments.append({
                    'start': df.index[seg_start],
                    'end': df.index[i - 1],
                    'label': current,
                    'bars': i - seg_start,
                })
            seg_start = i
            current = bar_labels[i]

    if current != 'warmup':
        segments.append({
            'start': df.index[seg_start],
            'end': df.index[-1],
            'label': current,
            'bars': len(df) - seg_start,
        })

    # Step 7: Merge short segments (smart: prefer merging into similar neighbor)
    merged = _smart_merge(segments, min_segment_bars)

    # Step 8: Re-label by actual segment return (eliminates misleading labels)
    for seg in merged:
        mask = (close.index >= seg['start']) & (close.index <= seg['end'])
        seg_close = close.loc[mask]
        if len(seg_close) > 1:
            seg['total_return'] = round(((seg_close.iloc[-1] / seg_close.iloc[0]) - 1) * 100, 1)
            daily_ret = seg_close.pct_change().dropna()
            seg['annualized_vol'] = round(daily_ret.std() * np.sqrt(252) * 100, 1) if len(daily_ret) > 0 else 0
        else:
            seg['total_return'] = 0
            seg['annualized_vol'] = 0

    # Re-label based on actual returns + volatility (percentile-adaptive)
    all_returns = [s['total_return'] for s in merged]
    all_vols = [s['annualized_vol'] for s in merged]
    if len(all_returns) >= 4:
        ret_p75 = np.percentile(all_returns, 75)
        ret_p25 = np.percentile(all_returns, 25)
        vol_med = np.median(all_vols)
    else:
        ret_p75 = 15
        ret_p25 = -15
        vol_med = 40

    for seg in merged:
        ret = seg['total_return']
        vol = seg['annualized_vol']
        if ret > max(ret_p75, 10):
            seg['label'] = 'bull'
        elif ret < min(ret_p25, -10):
            seg['label'] = 'bear'
        elif abs(ret) < max(abs(ret_p25) * 0.5, 8) and vol < vol_med:
            seg['label'] = 'consolidation'
        else:
            seg['label'] = 'choppy'

    # Store thresholds for transparency
    for seg in merged:
        seg['_thresholds'] = {
            'bull_return': round(bull_thresh, 1),
            'bear_return': round(bear_thresh, 1),
            'vol_median': round(vol_median, 1),
            'segment_bull': round(max(ret_p75, 10), 1),
            'segment_bear': round(min(ret_p25, -10), 1),
        }

    return merged


def _smart_merge(segments, min_bars):
    """Merge short segments into the most similar neighbor.

    Unlike naive forward-merge, this finds the shortest segment and merges it
    into whichever neighbor shares the same label (or is longer). Repeats until
    all segments meet the minimum bar requirement.
    """
    if not segments:
        return segments

    merged = [s.copy() for s in segments]

    while True:
        # Find shortest segment below minimum
        shortest_idx = None
        shortest_bars = float('inf')
        for i, seg in enumerate(merged):
            if seg['bars'] < min_bars and seg['bars'] < shortest_bars:
                shortest_bars = seg['bars']
                shortest_idx = i

        if shortest_idx is None:
            break  # All segments meet minimum

        if len(merged) <= 2:
            # Can't merge further without going below 2 segments
            break

        seg = merged[shortest_idx]
        prev_seg = merged[shortest_idx - 1] if shortest_idx > 0 else None
        next_seg = merged[shortest_idx + 1] if shortest_idx < len(merged) - 1 else None

        # Decide which neighbor to merge into
        merge_into = None
        if prev_seg and next_seg:
            # Prefer neighbor with same label
            if prev_seg['label'] == seg['label']:
                merge_into = 'prev'
            elif next_seg['label'] == seg['label']:
                merge_into = 'next'
            # Otherwise merge into the longer neighbor
            elif prev_seg['bars'] >= next_seg['bars']:
                merge_into = 'prev'
            else:
                merge_into = 'next'
        elif prev_seg:
            merge_into = 'prev'
        elif next_seg:
            merge_into = 'next'
        else:
            break

        if merge_into == 'prev':
            prev_seg['end'] = seg['end']
            prev_seg['bars'] += seg['bars']
            merged.pop(shortest_idx)
        else:
            next_seg['start'] = seg['start']
            next_seg['bars'] += seg['bars']
            merged.pop(shortest_idx)

    return merged


def regimes_to_windows(regimes, df, train_lookback_bars=252):
    """Convert detected regimes into walk-forward (train_start, test_start, test_end) windows.

    Each regime becomes a TEST window. Training period = prior data up to train_lookback_bars.

    Args:
        regimes: Output from detect_regimes()
        df: Full DataFrame (for index lookups)
        train_lookback_bars: Bars before test_start used for training (default 252 ~ 1 year)

    Returns:
        Tuple of (windows, labels):
            windows = [(train_start, test_start, test_end), ...]
            labels = ["Bull (+45.2%)", "Bear (-31.0%)", ...]
    """
    windows = []
    labels = []

    # Accept DataFrame, Series, or DatetimeIndex
    if isinstance(df, pd.DatetimeIndex):
        idx = df
    else:
        idx = df.index

    for regime in regimes:
        test_start = regime['start']
        test_end = regime['end']

        # Find index position of test_start
        idx_pos = idx.get_indexer([test_start], method='nearest')[0]

        # Training starts train_lookback_bars before test
        train_start_pos = max(0, idx_pos - train_lookback_bars)
        train_start = idx[train_start_pos]

        # Skip if training period would be too short (< 50 bars)
        if idx_pos - train_start_pos < 50:
            continue

        windows.append((
            str(train_start.date()),
            str(test_start.date()),
            str(test_end.date()),
        ))

        ret = regime.get('total_return', 0)
        sign = "+" if ret >= 0 else ""
        labels.append(f"{regime['label'].title()} ({sign}{ret:.0f}%)")

    return windows, labels


def print_regime_report(regimes, ticker=""):
    """Pretty-print detected regimes with stats."""
    print()
    thresholds = regimes[0].get('_thresholds', {}) if regimes else {}

    print(f"  AUTO-DETECTED REGIMES{' — ' + ticker if ticker else ''}")
    if thresholds:
        print(f"  Bar thresholds (smoothed 120d return): "
              f"bull > {thresholds.get('bull_return', '?')}%, "
              f"bear < {thresholds.get('bear_return', '?')}%")
        print(f"  Segment re-label: "
              f"bull > {thresholds.get('segment_bull', '?')}% total return, "
              f"bear < {thresholds.get('segment_bear', '?')}%")
    print(f"  {'─' * 70}")
    print(f"  {'#':<4} {'Start':<12} {'End':<12} {'Label':<16} {'Bars':>5} {'Return':>8} {'Vol':>6}")
    print(f"  {'─' * 70}")

    for i, r in enumerate(regimes, 1):
        ret_str = f"{r.get('total_return', 0):+.1f}%"
        vol_str = f"{r.get('annualized_vol', 0):.0f}%"
        print(f"  {i:<4} {str(r['start'].date()):<12} {str(r['end'].date()):<12} "
              f"{r['label'].upper():<16} {r['bars']:>5} {ret_str:>8} {vol_str:>6}")

    print(f"  {'─' * 70}")
    print(f"  Total: {len(regimes)} regimes detected from data")

    # Summary counts
    label_counts = {}
    for r in regimes:
        label_counts[r['label']] = label_counts.get(r['label'], 0) + 1
    summary = ", ".join(f"{v} {k}" for k, v in sorted(label_counts.items()))
    print(f"  Breakdown: {summary}")
    print()


if __name__ == "__main__":
    """Quick test: detect regimes on any available daily CSV."""
    import sys
    sys.path.insert(0, '.')

    ticker = sys.argv[1] if len(sys.argv) > 1 else "NVDA"

    from utils import load_data
    df = load_data(ticker, "daily")

    regimes = detect_regimes(df)
    print_regime_report(regimes, ticker=ticker)

    windows, labels = regimes_to_windows(regimes, df)
    print(f"  Walk-forward windows ({len(windows)}):")
    for i, ((ts, te_s, te_e), lbl) in enumerate(zip(windows, labels), 1):
        print(f"    W{i}: train {ts} | test {te_s} → {te_e} | {lbl}")
    print()
