"""Tests for config.py — env loading, validation, thresholds."""
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "market_intel"))


class TestConfigConstants:
    def test_fred_series_all_strings(self):
        from config import FRED_SERIES
        for key, value in FRED_SERIES.items():
            assert isinstance(key, str)
            assert isinstance(value, str)

    def test_triggers_all_numeric(self):
        from config import TRIGGERS
        for key, value in TRIGGERS.items():
            assert isinstance(value, (int, float)), f"TRIGGERS[{key}] = {value} is not numeric"

    def test_sentiment_all_numeric(self):
        from config import SENTIMENT
        for key, value in SENTIMENT.items():
            assert isinstance(value, (int, float)), f"SENTIMENT[{key}] = {value} is not numeric"

    def test_options_config_valid(self):
        from config import OPTIONS
        assert OPTIONS["max_dte"] > 0
        assert OPTIONS["max_expirations"] > 0
        assert OPTIONS["pc_ratio_bearish"] > OPTIONS["pc_ratio_bullish"]
        assert OPTIONS["chain_fetch_delay"] >= 0


class TestValidateApiKeys:
    def test_returns_list(self):
        from config import validate_api_keys
        missing = validate_api_keys()
        assert isinstance(missing, list)

    def test_detects_empty_keys(self):
        from config import validate_api_keys
        old_poly = os.environ.get("POLYGON_API_KEY", "")
        old_fred = os.environ.get("FRED_API_KEY", "")
        os.environ["POLYGON_API_KEY"] = ""
        os.environ["FRED_API_KEY"] = ""
        try:
            # Reload config module to pick up new env
            import config
            config.POLYGON_API_KEY = ""
            config.FRED_API_KEY = ""
            missing = config.validate_api_keys()
            assert "POLYGON_API_KEY" in missing
            assert "FRED_API_KEY" in missing
        finally:
            os.environ["POLYGON_API_KEY"] = old_poly
            os.environ["FRED_API_KEY"] = old_fred


class TestRetryDecorator:
    def test_retry_succeeds_on_second_attempt(self):
        from data_sources import retry_on_failure
        call_count = 0

        @retry_on_failure(max_retries=2, delay=0.01, exceptions=(ValueError,))
        def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("transient error")
            return "success"

        result = flaky_func()
        assert result == "success"
        assert call_count == 2

    def test_retry_exhausts_attempts(self):
        from data_sources import retry_on_failure

        @retry_on_failure(max_retries=1, delay=0.01, exceptions=(ValueError,))
        def always_fails():
            raise ValueError("permanent error")

        with pytest.raises(ValueError, match="permanent error"):
            always_fails()

    def test_retry_does_not_catch_wrong_exception(self):
        from data_sources import retry_on_failure

        @retry_on_failure(max_retries=2, delay=0.01, exceptions=(ValueError,))
        def raises_type_error():
            raise TypeError("wrong type")

        with pytest.raises(TypeError):
            raises_type_error()

    def test_retry_no_retry_on_success(self):
        from data_sources import retry_on_failure
        call_count = 0

        @retry_on_failure(max_retries=3, delay=0.01, exceptions=(ValueError,))
        def works_first_time():
            nonlocal call_count
            call_count += 1
            return 42

        result = works_first_time()
        assert result == 42
        assert call_count == 1


class TestDataSourcesWatchlistConfig:
    def test_watchlist_has_entries(self):
        from data_sources import WATCHLIST_CONFIG
        assert len(WATCHLIST_CONFIG) > 5
        assert "NVDA" in WATCHLIST_CONFIG
        assert "AU" in WATCHLIST_CONFIG

    def test_watchlist_format(self):
        from data_sources import WATCHLIST_CONFIG
        for symbol, (exchange, screener) in WATCHLIST_CONFIG.items():
            assert isinstance(symbol, str)
            assert isinstance(exchange, str)
            assert isinstance(screener, str)

    def test_polygon_ticker_map_valid(self):
        from data_sources import POLYGON_TICKER_MAP
        for display, polygon in POLYGON_TICKER_MAP.items():
            assert isinstance(display, str)
            assert isinstance(polygon, str)
