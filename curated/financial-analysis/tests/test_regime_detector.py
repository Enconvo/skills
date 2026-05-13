"""Tests for regime_detector — regime detection, window generation, edge cases."""
import pytest
import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "strategy_lab"))


@pytest.fixture
def daily_ohlcv():
    """Generate 3 years of synthetic daily OHLCV data with a visible trend change."""
    np.random.seed(42)
    dates = pd.date_range("2023-01-01", periods=750, freq="B")  # ~3 years business days
    # Create a bull → bear → bull pattern
    n = len(dates)
    phase1 = np.cumsum(np.random.randn(250) * 0.5 + 0.1)  # bull
    phase2 = np.cumsum(np.random.randn(250) * 0.8 - 0.15)  # bear
    phase3 = np.cumsum(np.random.randn(250) * 0.5 + 0.08)  # recovery
    close = 100 + np.concatenate([phase1, phase1[-1] + phase2, phase1[-1] + phase2[-1] + phase3])
    close = np.maximum(close, 10)  # floor at $10

    return pd.DataFrame({
        "Open": close + np.random.randn(n) * 0.3,
        "High": close + abs(np.random.randn(n) * 0.8),
        "Low": close - abs(np.random.randn(n) * 0.8),
        "Close": close,
        "Volume": np.random.randint(1000, 100000, n).astype(float),
    }, index=dates)


@pytest.fixture
def short_ohlcv():
    """Generate 50 bars of data (below default return_window)."""
    np.random.seed(99)
    dates = pd.date_range("2025-01-01", periods=50, freq="B")
    close = 100 + np.cumsum(np.random.randn(50) * 0.5)
    return pd.DataFrame({
        "Open": close, "High": close + 1, "Low": close - 1,
        "Close": close, "Volume": np.full(50, 10000.0),
    }, index=dates)


class TestDetectRegimes:
    def test_returns_list_of_regimes(self, daily_ohlcv):
        from regime_detector import detect_regimes
        regimes = detect_regimes(daily_ohlcv)
        assert isinstance(regimes, list)
        assert len(regimes) >= 2  # should detect at least 2 regimes

    def test_regime_has_required_keys(self, daily_ohlcv):
        from regime_detector import detect_regimes
        regimes = detect_regimes(daily_ohlcv)
        for r in regimes:
            assert "start" in r
            assert "end" in r
            assert "label" in r
            assert "bars" in r
            assert "total_return" in r
            assert "annualized_vol" in r

    def test_regimes_cover_full_data(self, daily_ohlcv):
        from regime_detector import detect_regimes
        regimes = detect_regimes(daily_ohlcv)
        total_bars = sum(r["bars"] for r in regimes)
        # Total bars should be close to dataset length (warmup may eat some bars)
        assert total_bars > len(daily_ohlcv) * 0.5

    def test_labels_are_valid(self, daily_ohlcv):
        from regime_detector import detect_regimes
        regimes = detect_regimes(daily_ohlcv)
        valid_labels = {"bull", "bear", "consolidation", "choppy"}
        for r in regimes:
            assert r["label"] in valid_labels, f"Unknown label: {r['label']}"

    def test_small_dataset_auto_scales(self, short_ohlcv):
        """Previously would crash with 'Not enough data'. Now auto-scales return_window."""
        from regime_detector import detect_regimes
        regimes = detect_regimes(short_ohlcv)
        assert isinstance(regimes, list)
        assert len(regimes) >= 1

    def test_very_small_dataset_raises(self):
        """20 bars should still raise ValueError."""
        from regime_detector import detect_regimes
        dates = pd.date_range("2025-01-01", periods=20, freq="B")
        df = pd.DataFrame({
            "Close": np.arange(20, dtype=float) + 100,
        }, index=dates)
        with pytest.raises(ValueError):
            detect_regimes(df)

    def test_custom_percentiles(self, daily_ohlcv):
        from regime_detector import detect_regimes
        regimes = detect_regimes(daily_ohlcv, bull_percentile=80, bear_percentile=20)
        assert isinstance(regimes, list)

    def test_target_regimes_parameter(self, daily_ohlcv):
        from regime_detector import detect_regimes
        regimes_5 = detect_regimes(daily_ohlcv, target_regimes=5)
        regimes_20 = detect_regimes(daily_ohlcv, target_regimes=20)
        # More target regimes should generally produce more regimes
        assert isinstance(regimes_5, list)
        assert isinstance(regimes_20, list)


class TestRegimesToWindows:
    def test_produces_windows(self, daily_ohlcv):
        from regime_detector import detect_regimes, regimes_to_windows
        regimes = detect_regimes(daily_ohlcv)
        windows, labels = regimes_to_windows(regimes, daily_ohlcv)
        assert len(windows) > 0
        assert len(windows) == len(labels)

    def test_window_format(self, daily_ohlcv):
        from regime_detector import detect_regimes, regimes_to_windows
        regimes = detect_regimes(daily_ohlcv)
        windows, labels = regimes_to_windows(regimes, daily_ohlcv)
        for train_start, test_start, test_end in windows:
            # All should be date strings
            assert len(train_start) == 10  # YYYY-MM-DD
            assert len(test_start) == 10
            assert len(test_end) == 10
            assert train_start < test_start
            assert test_start <= test_end

    def test_labels_contain_return(self, daily_ohlcv):
        from regime_detector import detect_regimes, regimes_to_windows
        regimes = detect_regimes(daily_ohlcv)
        _, labels = regimes_to_windows(regimes, daily_ohlcv)
        for label in labels:
            assert "%" in label  # Should contain return percentage


class TestSmartMerge:
    def test_merges_short_segments(self):
        from regime_detector import _smart_merge
        segments = [
            {"start": "A", "end": "B", "label": "bull", "bars": 100},
            {"start": "C", "end": "D", "label": "bear", "bars": 5},  # too short
            {"start": "E", "end": "F", "label": "bull", "bars": 100},
        ]
        merged = _smart_merge(segments, min_bars=30)
        assert len(merged) == 2  # short segment should be merged

    def test_preserves_long_segments(self):
        from regime_detector import _smart_merge
        segments = [
            {"start": "A", "end": "B", "label": "bull", "bars": 100},
            {"start": "C", "end": "D", "label": "bear", "bars": 100},
        ]
        merged = _smart_merge(segments, min_bars=30)
        assert len(merged) == 2  # both long enough, no merge

    def test_empty_input(self):
        from regime_detector import _smart_merge
        assert _smart_merge([], min_bars=30) == []
