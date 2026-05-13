"""Tests for TTLCache and compute_indicators input sanitization."""
import time
import pytest
import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "market_intel"))


class TestTTLCache:
    def test_set_and_get(self):
        from data_sources import TTLCache
        cache = TTLCache(default_ttl=60)
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_expired_returns_none(self):
        from data_sources import TTLCache
        cache = TTLCache(default_ttl=0.01)  # 10ms TTL
        cache.set("key1", "value1")
        time.sleep(0.02)
        assert cache.get("key1") is None

    def test_custom_ttl(self):
        from data_sources import TTLCache
        cache = TTLCache(default_ttl=0.01)
        cache.set("key1", "value1", ttl=60)  # Override with 60s
        time.sleep(0.02)
        assert cache.get("key1") == "value1"  # Still valid

    def test_missing_key_returns_none(self):
        from data_sources import TTLCache
        cache = TTLCache()
        assert cache.get("nonexistent") is None

    def test_clear(self):
        from data_sources import TTLCache
        cache = TTLCache()
        cache.set("k1", "v1")
        cache.set("k2", "v2")
        cache.clear()
        assert cache.get("k1") is None
        assert cache.get("k2") is None

    def test_overwrite(self):
        from data_sources import TTLCache
        cache = TTLCache()
        cache.set("key", "old")
        cache.set("key", "new")
        assert cache.get("key") == "new"


class TestComputeIndicatorsSanitization:
    def test_returns_none_for_empty_df(self):
        from data_sources import compute_indicators
        result = compute_indicators(pd.DataFrame())
        assert result is None

    def test_returns_none_for_short_df(self):
        from data_sources import compute_indicators
        df = pd.DataFrame({
            "Open": [1.0] * 10, "High": [2.0] * 10,
            "Low": [0.5] * 10, "Close": [1.5] * 10,
            "Volume": [100.0] * 10
        })
        result = compute_indicators(df)
        assert result is None

    def test_returns_none_for_missing_columns(self):
        from data_sources import compute_indicators
        df = pd.DataFrame({"Close": [1.0] * 50})  # missing High, Low
        result = compute_indicators(df)
        assert result is None

    def test_handles_nan_heavy_data(self):
        from data_sources import compute_indicators
        dates = pd.date_range("2024-01-01", periods=50, freq="B")
        df = pd.DataFrame({
            "Open": [float("nan")] * 50,
            "High": [float("nan")] * 50,
            "Low": [float("nan")] * 50,
            "Close": [float("nan")] * 50,
            "Volume": [100.0] * 50,
        }, index=dates)
        result = compute_indicators(df)
        assert result is None  # All NaN rows dropped, < 30 remaining
