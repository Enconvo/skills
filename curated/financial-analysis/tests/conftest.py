"""Shared test fixtures."""
import sys
import os
import pytest
import pandas as pd
import numpy as np

# Ensure market_intel is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "market_intel"))


@pytest.fixture
def sample_ohlcv():
    """Generate a small synthetic OHLCV DataFrame for testing."""
    dates = pd.date_range("2024-01-01", periods=100, freq="h")
    np.random.seed(42)
    close = 100 + np.cumsum(np.random.randn(100) * 0.5)
    return pd.DataFrame(
        {
            "Open": close + np.random.randn(100) * 0.1,
            "High": close + abs(np.random.randn(100) * 0.5),
            "Low": close - abs(np.random.randn(100) * 0.5),
            "Close": close,
            "Volume": np.random.randint(1000, 100000, 100).astype(float),
        },
        index=dates,
    )


@pytest.fixture
def sample_ohlcv_csv(tmp_path, sample_ohlcv):
    """Write sample OHLCV data to a CSV file and return the path."""
    csv_path = tmp_path / "test_data.csv"
    df = sample_ohlcv.copy()
    df.index.name = "Date"
    df.to_csv(csv_path)
    return str(csv_path)


@pytest.fixture
def project_root():
    """Return the project root directory."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def sample_option_chain():
    """Small options chain DataFrames (calls, puts) for testing analytics."""
    calls = pd.DataFrame({
        "strike": [90.0, 95.0, 100.0, 105.0, 110.0],
        "volume": [500, 800, 1200, 600, 300],
        "openInterest": [1000, 2000, 5000, 3000, 1500],
        "impliedVolatility": [0.35, 0.32, 0.30, 0.28, 0.27],
    })
    puts = pd.DataFrame({
        "strike": [90.0, 95.0, 100.0, 105.0, 110.0],
        "volume": [300, 600, 900, 1100, 700],
        "openInterest": [1500, 2500, 4000, 3500, 2000],
        "impliedVolatility": [0.28, 0.30, 0.32, 0.35, 0.38],
    })
    return calls, puts
