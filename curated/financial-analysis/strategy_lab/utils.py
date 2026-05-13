"""Utility functions for the TradingView backtester project."""

import pandas as pd
import numpy as np
import os

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))


def load_au_data(timeframe="1h"):
    """Load AU (Barrick Gold) data formatted for backtesting.py."""
    if timeframe == "1h":
        csv_path = os.path.join(PROJECT_DIR, "au_1h.csv")
    else:
        csv_path = os.path.join(PROJECT_DIR, "au_daily.csv")

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"AU data not found at {csv_path}. Run fetch_au_data.py first.")

    data = pd.read_csv(csv_path, index_col=0, parse_dates=True)
    data.index.name = "Date"
    try:
        data.index = pd.to_datetime(data.index, utc=True).tz_localize(None)
    except Exception:
        data.index = pd.to_datetime(data.index)
    data = data.sort_index()

    required = ["Open", "High", "Low", "Close", "Volume"]
    missing = [c for c in required if c not in data.columns]
    if missing:
        raise ValueError(f"Missing columns in CSV: {missing}")
    data = data[required]
    data = data.dropna()

    if len(data) == 0:
        raise ValueError(f"CSV has no valid rows after dropping NaN: {csv_path}")

    print(f"Loaded {len(data)} AU {timeframe} candles from {data.index[0]} to {data.index[-1]}")
    return data


def load_nvda_data(timeframe="1h"):
    """Load NVDA data formatted for backtesting.py."""
    if timeframe == "1h":
        csv_path = os.path.join(PROJECT_DIR, "nvda_1h.csv")
    else:
        csv_path = os.path.join(PROJECT_DIR, "nvda_daily.csv")

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"NVDA data not found at {csv_path}. Download via yfinance first.")

    data = pd.read_csv(csv_path, index_col=0, parse_dates=True)
    try:
        data.index = pd.to_datetime(data.index, utc=True).tz_localize(None)
    except Exception:
        data.index = pd.to_datetime(data.index)
    data = data.sort_index()

    required = ["Open", "High", "Low", "Close", "Volume"]
    missing = [c for c in required if c not in data.columns]
    if missing:
        raise ValueError(f"Missing columns in CSV: {missing}")
    data = data[required]
    data = data.dropna()

    if len(data) == 0:
        raise ValueError(f"CSV has no valid rows after dropping NaN: {csv_path}")

    print(f"Loaded {len(data)} NVDA {timeframe} candles from {data.index[0]} to {data.index[-1]}")
    return data


def load_btc_data(csv_path=None):
    """Load BTC 1h data formatted for backtesting.py.

    backtesting.py expects a DataFrame with DatetimeIndex and columns:
    Open, High, Low, Close, Volume
    """
    if csv_path is None:
        csv_path = os.path.join(PROJECT_DIR, "btc_1h.csv")

    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"BTC data not found at {csv_path}. "
            "Run fetch_btc_data.py first to download it."
        )

    data = pd.read_csv(csv_path, index_col=0, parse_dates=True)
    data.index.name = "Date"
    data = data.sort_index()

    # Ensure required columns exist
    required = ["Open", "High", "Low", "Close", "Volume"]
    missing = [c for c in required if c not in data.columns]
    if missing:
        raise ValueError(f"Missing columns in CSV: {missing}")

    # Keep only required columns in correct order
    data = data[required]

    # Drop any NaN rows
    data = data.dropna()

    if len(data) == 0:
        raise ValueError(f"CSV has no valid rows after dropping NaN: {csv_path}")

    print(f"Loaded {len(data)} candles from {data.index[0]} to {data.index[-1]}")
    return data


def append_result(strategy_name, stats, notes=""):
    """Append a backtest result row to master_results.csv."""
    csv_path = os.path.join(PROJECT_DIR, "master_results.csv")

    row = {
        "Strategy Name": strategy_name,
        "Python File Link": "",
        "Expectancy [%]": round(stats.get("Expectancy [%]", 0), 4),
        "Sortino Ratio": round(stats.get("Sortino Ratio", 0), 4),
        "# Trades": int(stats.get("# Trades", 0)),
        "Win Rate [%]": round(stats.get("Win Rate [%]", 0), 2),
        "Profit Factor": round(stats.get("Profit Factor", 0), 4),
        "Max. Drawdown [%]": round(stats.get("Max. Drawdown [%]", 0), 2),
        "Sharpe Ratio": round(stats.get("Sharpe Ratio", 0), 4),
        "Return [%]": round(stats.get("Return [%]", 0), 2),
        "Net Profit [$]": round(stats.get("Equity Final [$]", 1_000_000) - 1_000_000, 2),
        "Notes/Skipped Reason": notes,
    }

    df = pd.DataFrame([row])

    # Append to CSV (write header only if file doesn't exist or is empty)
    write_header = not os.path.exists(csv_path) or os.path.getsize(csv_path) == 0
    df.to_csv(csv_path, mode="a", header=write_header, index=False)
    print(f"Result appended to {csv_path}")


def crossover_manual(series_a, series_b):
    """Manual crossover: series_a crosses above series_b."""
    return (series_a.iloc[-1] > series_b.iloc[-1]) and (series_a.iloc[-2] <= series_b.iloc[-2])


def crossunder_manual(series_a, series_b):
    """Manual crossunder: series_a crosses below series_b."""
    return (series_a.iloc[-1] < series_b.iloc[-1]) and (series_a.iloc[-2] >= series_b.iloc[-2])

def load_meta_data(timeframe="1h"):
    """Load META (Meta Platforms) price data."""
    if timeframe == "1h":
        csv_path = os.path.join(PROJECT_DIR, "meta_1h.csv")
    elif timeframe == "daily":
        csv_path = os.path.join(PROJECT_DIR, "meta_daily.csv")
    else:
        raise ValueError(f"Unknown timeframe: {timeframe}")

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"META data not found at {csv_path}.")

    data = pd.read_csv(csv_path, index_col=0, parse_dates=True)

    # Ensure timezone-naive
    try:
        data.index = pd.to_datetime(data.index, utc=True).tz_localize(None)
    except Exception:
        data.index = pd.to_datetime(data.index)
    data = data.sort_index()

    required = ["Open", "High", "Low", "Close", "Volume"]
    missing = [c for c in required if c not in data.columns]
    if missing:
        raise ValueError(f"Missing columns in CSV: {missing}")
    data = data[required]
    data = data.dropna()

    if len(data) == 0:
        raise ValueError(f"CSV has no valid rows after dropping NaN: {csv_path}")

    print(f"Loaded {len(data)} META {timeframe} candles from {data.index[0]} to {data.index[-1]}")
    return data


# ═══════════════════════════════════════════════════════════
#  Polygon.io Integration + Data Cross-Verification
# ═══════════════════════════════════════════════════════════

def load_env():
    """Load .env file from project directory (falls back to parent dir)."""
    try:
        from dotenv import load_dotenv
        env_path = os.path.join(PROJECT_DIR, ".env")
        if not os.path.exists(env_path):
            env_path = os.path.join(os.path.dirname(PROJECT_DIR), ".env")
        if os.path.exists(env_path):
            load_dotenv(env_path)
            return True
    except ImportError:
        # Fallback: manual .env parsing
        env_path = os.path.join(PROJECT_DIR, ".env")
        if not os.path.exists(env_path):
            env_path = os.path.join(os.path.dirname(PROJECT_DIR), ".env")
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, val = line.split("=", 1)
                        os.environ[key.strip()] = val.strip()
            return True
    return False


def get_polygon_client():
    """Get Polygon REST client. Returns None if no API key available."""
    load_env()
    api_key = os.environ.get("POLYGON_API_KEY")
    if not api_key:
        return None
    try:
        from polygon import RESTClient
        return RESTClient(api_key)
    except ImportError:
        print("polygon-api-client not installed. Run: pip install polygon-api-client")
        return None


def fetch_polygon_ohlcv(ticker, timeframe="1h", years_back=5):
    """Fetch OHLCV from Polygon.io REST API.

    Args:
        ticker: Symbol (e.g., "AAPL", "AU", "X:BTCUSD")
        timeframe: "1h" or "daily"
        years_back: Years of history (Starter plan supports up to 5)

    Returns:
        DataFrame with DatetimeIndex [Open,High,Low,Close,Volume] or None.
    """
    client = get_polygon_client()
    if client is None:
        return None

    from datetime import datetime, timedelta

    end = datetime.now()
    start = end - timedelta(days=int(365.25 * years_back))

    timespan = "hour" if timeframe == "1h" else "day"

    print(f"  Polygon: {ticker} {timeframe} | {start.date()} -> {end.date()} ...")

    try:
        aggs = client.list_aggs(
            ticker=ticker,
            multiplier=1,
            timespan=timespan,
            from_=start.strftime("%Y-%m-%d"),
            to=end.strftime("%Y-%m-%d"),
            limit=50000,
        )

        bars = []
        for bar in aggs:
            bars.append({
                "Date": pd.to_datetime(bar.timestamp, unit="ms", utc=True).tz_localize(None),
                "Open": bar.open,
                "High": bar.high,
                "Low": bar.low,
                "Close": bar.close,
                "Volume": float(bar.volume) if bar.volume else 0.0,
            })

        if not bars:
            print("  Polygon: no data returned")
            return None

        df = pd.DataFrame(bars).set_index("Date").sort_index()
        df = df[~df.index.duplicated(keep="first")]
        print(f"  Polygon: {len(df)} candles received")
        return df

    except Exception as e:
        print(f"  Polygon failed: {e}")
        return None


def fetch_yfinance_ohlcv(ticker, timeframe="1h"):
    """Fetch OHLCV from yfinance (fallback).

    Limitations: 1h data ~2 years, daily ~5 years.
    """
    try:
        import yfinance as yf
    except ImportError:
        print("  yfinance not installed")
        return None

    interval = "1h" if timeframe == "1h" else "1d"
    period = "2y" if timeframe == "1h" else "5y"

    print(f"  yfinance: {ticker} {timeframe} (period={period}) ...")

    try:
        t = yf.Ticker(ticker)
        df = t.history(period=period, interval=interval)

        if df.empty:
            print("  yfinance: no data returned")
            return None

        df = df[["Open", "High", "Low", "Close", "Volume"]]
        df.index.name = "Date"
        try:
            df.index = pd.to_datetime(df.index, utc=True).tz_localize(None)
        except Exception:
            df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        df = df[~df.index.duplicated(keep="first")]
        df["Volume"] = df["Volume"].astype(float)
        print(f"  yfinance: {len(df)} candles received")
        return df

    except Exception as e:
        print(f"  yfinance failed: {e}")
        return None


def fetch_data(ticker, timeframe="1h", years_back=5, save=True):
    """Unified data fetcher: Polygon.io (primary) -> yfinance (fallback).

    Args:
        ticker: Stock ticker (e.g., "AAPL", "AU", "NVDA")
        timeframe: "1h" or "daily"
        years_back: Years of history for Polygon (yfinance has fixed limits)
        save: Save to CSV in project directory

    Returns:
        Tuple of (DataFrame, source_name) where source is "polygon" or "yfinance".
    """
    source = None
    df = None

    # Try Polygon first
    df = fetch_polygon_ohlcv(ticker, timeframe, years_back)
    if df is not None:
        source = "polygon"
    else:
        # Fallback to yfinance
        print("  -> Falling back to yfinance ...")
        yf_ticker = ticker
        if ticker.startswith("X:"):
            yf_ticker = ticker.replace("X:", "").replace("USD", "-USD")
        df = fetch_yfinance_ohlcv(yf_ticker, timeframe)
        if df is not None:
            source = "yfinance"

    if df is None:
        raise RuntimeError(f"All sources failed for {ticker} {timeframe}")

    # Clean
    df = df.dropna()
    df["Volume"] = df["Volume"].astype(float)

    # Save to CSV
    if save:
        suffix = "1h" if timeframe == "1h" else "daily"
        ticker_clean = ticker.replace(":", "_").replace("-", "").lower()
        csv_path = os.path.join(PROJECT_DIR, f"{ticker_clean}_{suffix}.csv")
        df.to_csv(csv_path)
        print(f"  Saved -> {csv_path} ({len(df)} candles, source: {source})")

    return df, source


def cross_verify_indicators(data, ticker, timeframe="daily", tolerance=0.5):
    """Cross-verify local talib indicators against Polygon.io API values.

    Tests SMA(50), EMA(21), RSI(14), MACD(12,26,9) — computes locally and
    fetches from Polygon, then compares overlapping values.

    Args:
        data: DataFrame with OHLCV and DatetimeIndex
        ticker: Polygon ticker symbol
        timeframe: "1h" or "daily"
        tolerance: Max allowed absolute difference (default 0.5)

    Returns:
        dict with per-indicator results, or None if Polygon unavailable.
    """
    client = get_polygon_client()
    if client is None:
        print("  Cross-verification skipped: no Polygon API key")
        return None

    try:
        import talib
    except ImportError:
        print("  Cross-verification skipped: talib not installed")
        return None

    import time

    close = data["Close"].values
    timespan = "hour" if timeframe == "1h" else "day"
    results = {}

    def _compare(name, local_series, api_response, tol):
        """Compare local vs API indicator values."""
        try:
            api_vals = {
                pd.to_datetime(v.timestamp, unit="ms").tz_localize(None): v.value
                for v in api_response.values
            }
            api_series = pd.Series(api_vals).sort_index()
            common = local_series.index.intersection(api_series.index)
            if len(common) > 0:
                delta = (local_series[common] - api_series[common]).abs()
                return {
                    "pass": float(delta.max()) < tol,
                    "max_delta": round(float(delta.max()), 4),
                    "mean_delta": round(float(delta.mean()), 4),
                    "compared": len(common),
                }
            else:
                return {"pass": None, "compared": 0, "note": "no overlapping timestamps"}
        except Exception as e:
            return {"pass": None, "error": str(e)}

    # Per-indicator tolerances (accounts for initialization/rounding differences)
    tols = {"SMA(50)": tolerance, "EMA(21)": tolerance, "RSI(14)": 1.0, "MACD(12,26,9)": tolerance}

    # SMA(50)
    try:
        local = pd.Series(talib.SMA(close, timeperiod=50), index=data.index).dropna()
        api = client.get_sma(ticker, timespan=timespan, window=50, limit=200, order="desc")
        results["SMA(50)"] = _compare("SMA(50)", local, api, tols["SMA(50)"])
    except Exception as e:
        results["SMA(50)"] = {"pass": None, "error": str(e)}

    time.sleep(0.5)  # Avoid 429 rate limiting

    # EMA(21)
    try:
        local = pd.Series(talib.EMA(close, timeperiod=21), index=data.index).dropna()
        api = client.get_ema(ticker, timespan=timespan, window=21, limit=200, order="desc")
        results["EMA(21)"] = _compare("EMA(21)", local, api, tols["EMA(21)"])
    except Exception as e:
        results["EMA(21)"] = {"pass": None, "error": str(e)}

    time.sleep(0.5)

    # RSI(14) — higher tolerance: talib vs Polygon differ on RSI seed values
    try:
        local = pd.Series(talib.RSI(close, timeperiod=14), index=data.index).dropna()
        api = client.get_rsi(ticker, timespan=timespan, window=14, limit=200, order="desc")
        results["RSI(14)"] = _compare("RSI(14)", local, api, tols["RSI(14)"])
    except Exception as e:
        results["RSI(14)"] = {"pass": None, "error": str(e)}

    time.sleep(0.5)

    # MACD(12,26,9)
    try:
        macd_line, _, _ = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
        local = pd.Series(macd_line, index=data.index).dropna()
        api = client.get_macd(
            ticker, timespan=timespan,
            short_window=12, long_window=26, signal_window=9,
            limit=200, order="desc",
        )
        results["MACD(12,26,9)"] = _compare("MACD(12,26,9)", local, api, tols["MACD(12,26,9)"])
    except Exception as e:
        results["MACD(12,26,9)"] = {"pass": None, "error": str(e)}

    return results


def print_verification_report(results, ticker):
    """Pretty-print the cross-verification results."""
    if results is None:
        return

    print(f"\n{'=' * 54}")
    print(f"  DATA CROSS-VERIFICATION: {ticker}")
    print(f"{'=' * 54}")
    print(f"  Comparing local talib vs Polygon API indicators\n")

    all_pass = True
    for name, res in results.items():
        if "error" in res:
            status = "! ERROR"
            detail = res["error"]
            all_pass = False
        elif res.get("compared", 0) == 0:
            status = "~ SKIP"
            detail = res.get("note", "no data to compare")
            all_pass = False
        elif res["pass"]:
            status = "MATCH"
            detail = f"max d: {res['max_delta']}  mean d: {res['mean_delta']}  ({res['compared']} bars)"
        else:
            status = "X MISMATCH"
            detail = f"max d: {res['max_delta']}  mean d: {res['mean_delta']}  ({res['compared']} bars)"
            all_pass = False

        print(f"  {name:<16} {status:<12} {detail}")

    print()
    if all_pass:
        print(f"  VERDICT: Data foundation VERIFIED")
        print(f"  All strategies built on this data can be trusted.")
    else:
        print(f"  VERDICT: Verification incomplete or has mismatches")
        print(f"  Review above. Minor deltas (<0.5) are normal rounding.")
    print(f"{'=' * 54}\n")


def save_verification_report(results, ticker):
    """Save verification results to JSON for caching."""
    import json
    from datetime import datetime

    report = {
        "ticker": ticker,
        "verified_at": datetime.now().isoformat(),
        "indicators": results,
    }

    path = os.path.join(PROJECT_DIR, f"{ticker.lower()}_data_verified.json")
    with open(path, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"  Verification saved -> {path}")


def is_verified(ticker):
    """Check if ticker data has been previously verified."""
    import json
    path = os.path.join(PROJECT_DIR, f"{ticker.lower()}_data_verified.json")
    if not os.path.exists(path):
        return False
    try:
        with open(path) as f:
            report = json.load(f)
        for ind, res in report.get("indicators", {}).items():
            if not res.get("pass"):
                return False
        return True
    except Exception:
        return False


def fetch_extended_hours(ticker, years_back=2, save=True):
    """Fetch 1h OHLCV including pre-market (4AM-9:30AM) and post-market (4PM-8PM) bars.

    Polygon includes extended hours by default. This function fetches the full
    4AM-8PM range and labels each bar with a session tag.

    Returns:
        DataFrame with OHLCV + 'session' column ('pre_market', 'regular', 'post_market').
    """
    df, source = fetch_data(ticker, timeframe="1h", years_back=years_back, save=False)

    if source != "polygon":
        print("  WARNING: Extended hours data requires Polygon. yfinance data may have gaps.")

    # Convert to Eastern time for session labeling, then back to naive
    df_et = df.copy()
    df_et.index = df_et.index.tz_localize("UTC").tz_convert("US/Eastern")

    def _label_session(ts):
        h, m = ts.hour, ts.minute
        if h < 9 or (h == 9 and m < 30):
            return "pre_market"
        elif h < 16:
            return "regular"
        else:
            return "post_market"

    df["session"] = [_label_session(ts) for ts in df_et.index]

    if save:
        ticker_clean = ticker.replace(":", "_").replace("-", "").lower()
        csv_path = os.path.join(PROJECT_DIR, f"{ticker_clean}_extended_1h.csv")
        df.to_csv(csv_path)
        print(f"  Saved -> {csv_path} ({len(df)} candles, source: {source})")

    sessions = df["session"].value_counts()
    print(f"  Sessions: {sessions.to_dict()}")

    return df, source


def compute_gap_metrics(daily_data):
    """Compute overnight gap metrics from daily OHLCV.

    Adds columns to daily data:
        gap_pct:  (Today Open - Yesterday Close) / Yesterday Close * 100
        gap_size: Absolute dollar gap
        gap_dir:  'up', 'down', or 'flat'
        gap_filled: True if today's low <= yesterday's close (for gap-ups)
                    or today's high >= yesterday's close (for gap-downs)

    Args:
        daily_data: DataFrame with OHLCV columns and DatetimeIndex.

    Returns:
        DataFrame with gap metric columns added.
    """
    df = daily_data.copy()
    prev_close = df["Close"].shift(1)

    df["gap_pct"] = (df["Open"] - prev_close) / prev_close * 100
    df["gap_size"] = df["Open"] - prev_close
    df["gap_dir"] = "flat"
    df.loc[df["gap_pct"] > 0.1, "gap_dir"] = "up"
    df.loc[df["gap_pct"] < -0.1, "gap_dir"] = "down"

    # Gap fill detection
    df["gap_filled"] = False
    # Gap-up filled if price comes back down to previous close
    gap_up = df["gap_dir"] == "up"
    df.loc[gap_up, "gap_filled"] = df.loc[gap_up, "Low"] <= prev_close[gap_up]
    # Gap-down filled if price comes back up to previous close
    gap_dn = df["gap_dir"] == "down"
    df.loc[gap_dn, "gap_filled"] = df.loc[gap_dn, "High"] >= prev_close[gap_dn]

    return df


def compute_premarket_metrics(extended_data):
    """Compute pre-market session metrics from extended hours 1h data.

    Groups pre-market bars (4AM-9:30AM ET) per trading day and computes:
        pm_high, pm_low, pm_volume, pm_range_pct, pm_vwap_approx

    Args:
        extended_data: DataFrame from fetch_extended_hours() with 'session' column.

    Returns:
        DataFrame indexed by date with pre-market metrics.
    """
    pre = extended_data[extended_data["session"] == "pre_market"].copy()

    if pre.empty:
        print("  No pre-market bars found")
        return pd.DataFrame()

    pre["date"] = pre.index.date

    metrics = pre.groupby("date").agg(
        pm_open=("Open", "first"),
        pm_high=("High", "max"),
        pm_low=("Low", "min"),
        pm_close=("Close", "last"),
        pm_volume=("Volume", "sum"),
    )

    metrics["pm_range_pct"] = (metrics["pm_high"] - metrics["pm_low"]) / metrics["pm_low"] * 100

    metrics.index = pd.to_datetime(metrics.index)
    return metrics


def load_data(ticker, timeframe="1h"):
    """Generic data loader — reads from CSV (assumes fetch_data was already run).

    Replaces per-ticker loaders (load_au_data, load_nvda_data, etc.).

    Args:
        ticker: Stock ticker (e.g., "AAPL", "AU")
        timeframe: "1h" or "daily"

    Returns:
        DataFrame with DatetimeIndex and OHLCV columns.
    """
    suffix = "1h" if timeframe == "1h" else "daily"
    ticker_clean = ticker.replace(":", "_").replace("-", "").lower()
    csv_path = os.path.join(PROJECT_DIR, f"{ticker_clean}_{suffix}.csv")

    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"Data not found at {csv_path}. "
            f"Run fetch_data('{ticker}', '{timeframe}') first."
        )

    data = pd.read_csv(csv_path, index_col=0, parse_dates=True)
    try:
        data.index = pd.to_datetime(data.index, utc=True).tz_localize(None)
    except Exception:
        data.index = pd.to_datetime(data.index)
    data = data.sort_index()

    required = ["Open", "High", "Low", "Close", "Volume"]
    missing = [c for c in required if c not in data.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    data = data[required]
    data = data.dropna()

    print(f"Loaded {len(data)} {ticker} {timeframe} candles: {data.index[0]} -> {data.index[-1]}")
    return data

