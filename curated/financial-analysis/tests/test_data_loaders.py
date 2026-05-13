"""Tests for strategy_lab/utils.py — generic data loader and premarket metrics."""
import os
import pytest
import pandas as pd
import numpy as np

from strategy_lab.utils import load_data, compute_premarket_metrics


class TestLoadData:
    def test_loads_from_csv(self, tmp_path, sample_ohlcv, monkeypatch):
        """load_data should read a ticker CSV and return OHLCV DataFrame."""
        monkeypatch.setattr("strategy_lab.utils.PROJECT_DIR", str(tmp_path))
        csv_path = tmp_path / "aapl_1h.csv"
        df = sample_ohlcv.copy()
        df.index.name = "Date"
        df.to_csv(csv_path)

        result = load_data("AAPL", timeframe="1h")
        assert len(result) == 100
        assert list(result.columns) == ["Open", "High", "Low", "Close", "Volume"]
        assert isinstance(result.index, pd.DatetimeIndex)

    def test_daily_timeframe(self, tmp_path, sample_ohlcv, monkeypatch):
        monkeypatch.setattr("strategy_lab.utils.PROJECT_DIR", str(tmp_path))
        csv_path = tmp_path / "aapl_daily.csv"
        df = sample_ohlcv.copy()
        df.index.name = "Date"
        df.to_csv(csv_path)

        result = load_data("AAPL", timeframe="daily")
        assert len(result) == 100

    def test_file_not_found(self, tmp_path, monkeypatch):
        monkeypatch.setattr("strategy_lab.utils.PROJECT_DIR", str(tmp_path))
        with pytest.raises(FileNotFoundError):
            load_data("NONEXISTENT", timeframe="1h")

    def test_missing_columns(self, tmp_path, monkeypatch):
        monkeypatch.setattr("strategy_lab.utils.PROJECT_DIR", str(tmp_path))
        csv_path = tmp_path / "bad_1h.csv"
        pd.DataFrame({"Date": ["2024-01-01"], "Foo": [1]}).to_csv(csv_path, index=False)
        with pytest.raises(ValueError, match="Missing columns"):
            load_data("BAD", timeframe="1h")

    def test_ticker_cleaning(self, tmp_path, sample_ohlcv, monkeypatch):
        """Tickers with special chars should be cleaned for filename."""
        monkeypatch.setattr("strategy_lab.utils.PROJECT_DIR", str(tmp_path))
        csv_path = tmp_path / "x_btcusd_1h.csv"
        df = sample_ohlcv.copy()
        df.index.name = "Date"
        df.to_csv(csv_path)

        result = load_data("X:BTCUSD", timeframe="1h")
        assert len(result) == 100


class TestComputePremarketMetrics:
    def test_basic_premarket(self):
        """Should aggregate pre-market bars per day."""
        dates = pd.date_range("2024-01-02 04:00", periods=6, freq="h")
        df = pd.DataFrame(
            {
                "Open": [100, 101, 102, 103, 104, 105],
                "High": [101, 102, 103, 104, 105, 106],
                "Low": [99, 100, 101, 102, 103, 104],
                "Close": [100.5, 101.5, 102.5, 103.5, 104.5, 105.5],
                "Volume": [1000, 1100, 1200, 1300, 1400, 1500],
                "session": ["pre_market"] * 6,
            },
            index=dates,
        )
        result = compute_premarket_metrics(df)
        assert len(result) == 1
        assert "pm_high" in result.columns
        assert "pm_volume" in result.columns
        assert result.iloc[0]["pm_high"] == 106
        assert result.iloc[0]["pm_volume"] == 7500

    def test_empty_premarket(self):
        """Should return empty DataFrame if no pre-market bars."""
        dates = pd.date_range("2024-01-02 10:00", periods=3, freq="h")
        df = pd.DataFrame(
            {
                "Open": [100, 101, 102],
                "High": [101, 102, 103],
                "Low": [99, 100, 101],
                "Close": [100.5, 101.5, 102.5],
                "Volume": [1000, 1100, 1200],
                "session": ["regular"] * 3,
            },
            index=dates,
        )
        result = compute_premarket_metrics(df)
        assert result.empty

    def test_multi_day_premarket(self):
        """Should group metrics by date."""
        dates = pd.to_datetime([
            "2024-01-02 05:00", "2024-01-02 06:00",
            "2024-01-03 05:00", "2024-01-03 06:00",
        ])
        df = pd.DataFrame(
            {
                "Open": [100, 101, 200, 201],
                "High": [102, 103, 202, 203],
                "Low": [99, 100, 199, 200],
                "Close": [101, 102, 201, 202],
                "Volume": [500, 600, 700, 800],
                "session": ["pre_market"] * 4,
            },
            index=dates,
        )
        result = compute_premarket_metrics(df)
        assert len(result) == 2
