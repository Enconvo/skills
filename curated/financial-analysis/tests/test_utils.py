"""Tests for strategy_lab/utils.py — data loaders, crossovers, gap metrics."""
import os
import pytest
import pandas as pd
import numpy as np

from strategy_lab.utils import (
    crossover_manual,
    crossunder_manual,
    compute_gap_metrics,
    load_btc_data,
    load_au_data,
    load_data,
    append_result,
)


class TestCrossoverManual:
    def test_crossover_detected(self):
        a = pd.Series([1.0, 2.0, 3.0])
        b = pd.Series([2.0, 2.0, 2.0])
        assert crossover_manual(a, b) == True

    def test_no_crossover_when_already_above(self):
        a = pd.Series([3.0, 4.0, 5.0])
        b = pd.Series([2.0, 2.0, 2.0])
        assert crossover_manual(a, b) == False

    def test_crossunder_detected(self):
        a = pd.Series([3.0, 2.0, 1.0])
        b = pd.Series([2.0, 2.0, 2.0])
        assert crossunder_manual(a, b) == True

    def test_no_crossunder_when_already_below(self):
        a = pd.Series([1.0, 0.5, 0.2])
        b = pd.Series([2.0, 2.0, 2.0])
        assert crossunder_manual(a, b) == False


class TestComputeGapMetrics:
    def test_gap_up_detected(self, sample_ohlcv):
        df = sample_ohlcv.copy()
        # Force a clear gap-up on day 2
        df.iloc[1, df.columns.get_loc("Open")] = df.iloc[0, df.columns.get_loc("Close")] * 1.05
        result = compute_gap_metrics(df)
        assert "gap_pct" in result.columns
        assert "gap_dir" in result.columns
        assert result.iloc[1]["gap_dir"] == "up"
        assert result.iloc[1]["gap_pct"] > 0

    def test_gap_down_detected(self, sample_ohlcv):
        df = sample_ohlcv.copy()
        # Force a clear gap-down
        df.iloc[1, df.columns.get_loc("Open")] = df.iloc[0, df.columns.get_loc("Close")] * 0.95
        result = compute_gap_metrics(df)
        assert result.iloc[1]["gap_dir"] == "down"

    def test_flat_gap(self, sample_ohlcv):
        df = sample_ohlcv.copy()
        # Set open equal to previous close
        df.iloc[1, df.columns.get_loc("Open")] = df.iloc[0, df.columns.get_loc("Close")]
        result = compute_gap_metrics(df)
        assert result.iloc[1]["gap_dir"] == "flat"

    def test_gap_fill_detection(self, sample_ohlcv):
        df = sample_ohlcv.copy()
        prev_close = df.iloc[0, df.columns.get_loc("Close")]
        # Gap up but low comes back down
        df.iloc[1, df.columns.get_loc("Open")] = prev_close * 1.05
        df.iloc[1, df.columns.get_loc("Low")] = prev_close * 0.99
        result = compute_gap_metrics(df)
        assert result.iloc[1]["gap_filled"] == True

    def test_output_columns(self, sample_ohlcv):
        result = compute_gap_metrics(sample_ohlcv)
        expected_cols = {"gap_pct", "gap_size", "gap_dir", "gap_filled"}
        assert expected_cols.issubset(set(result.columns))


class TestLoadBtcData:
    def test_load_from_csv(self, sample_ohlcv_csv):
        df = load_btc_data(csv_path=sample_ohlcv_csv)
        assert len(df) == 100
        assert list(df.columns) == ["Open", "High", "Low", "Close", "Volume"]
        assert isinstance(df.index, pd.DatetimeIndex)

    def test_file_not_found(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_btc_data(csv_path=str(tmp_path / "nonexistent.csv"))

    def test_missing_columns(self, tmp_path):
        csv_path = tmp_path / "bad_data.csv"
        pd.DataFrame({"Date": ["2024-01-01"], "Foo": [1]}).to_csv(csv_path, index=False)
        with pytest.raises(ValueError, match="Missing columns"):
            load_btc_data(csv_path=str(csv_path))


class TestLoadAuData:
    def test_loads_real_data(self, project_root):
        """Integration test — loads actual CSV from repo."""
        csv_path = os.path.join(project_root, "strategy_lab", "au_daily.csv")
        if not os.path.exists(csv_path):
            pytest.skip("au_daily.csv not present")
        df = load_au_data(timeframe="daily")
        assert len(df) > 0
        assert "Close" in df.columns


class TestAppendResult:
    def test_creates_csv(self, tmp_path, monkeypatch):
        monkeypatch.setattr("strategy_lab.utils.PROJECT_DIR", str(tmp_path))
        stats = {
            "Expectancy [%]": 1.5,
            "Sortino Ratio": 2.0,
            "# Trades": 50,
            "Win Rate [%]": 55.5,
            "Profit Factor": 1.8,
            "Max. Drawdown [%]": -15.3,
            "Sharpe Ratio": 1.2,
            "Return [%]": 120.5,
            "Equity Final [$]": 2_200_000,
        }
        append_result("TestStrategy", stats, notes="test run")
        csv_path = tmp_path / "master_results.csv"
        assert csv_path.exists()
        df = pd.read_csv(csv_path)
        assert len(df) == 1
        assert df.iloc[0]["Strategy Name"] == "TestStrategy"

    def test_appends_to_existing(self, tmp_path, monkeypatch):
        monkeypatch.setattr("strategy_lab.utils.PROJECT_DIR", str(tmp_path))
        stats = {"# Trades": 10, "Win Rate [%]": 60}
        append_result("Strat1", stats)
        append_result("Strat2", stats)
        df = pd.read_csv(tmp_path / "master_results.csv")
        assert len(df) == 2
