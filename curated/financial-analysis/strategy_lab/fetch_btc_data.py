#!/usr/bin/env python3
"""
Fetch BTC/USD 1-hour OHLCV data.

Primary: Polygon.io REST API (requires POLYGON_API_KEY env var)
Fallback: yfinance (limited to ~730 days of 1h data)

Output: btc_1h.csv with columns Date, Open, High, Low, Close, Volume
"""

import os
import sys
from datetime import datetime, timedelta

import pandas as pd


def fetch_polygon(api_key: str) -> pd.DataFrame:
    """Fetch BTC 1h data from Polygon.io with pagination."""
    from polygon import RESTClient

    client = RESTClient(api_key)

    # Go back as far as possible — Polygon free tier has limits,
    # paid plans can go back to 2014+
    end = datetime.now()
    start = end - timedelta(days=365 * 3)  # 3 years back

    print(f"Polygon: fetching X:BTCUSD 1h from {start.date()} to {end.date()} ...")

    all_bars = []
    # Polygon's list_aggs handles pagination internally
    aggs = client.list_aggs(
        ticker="X:BTCUSD",
        multiplier=1,
        timespan="hour",
        from_=start.strftime("%Y-%m-%d"),
        to=end.strftime("%Y-%m-%d"),
        limit=50000,
    )

    for bar in aggs:
        all_bars.append({
            "Date": pd.to_datetime(bar.timestamp, unit="ms", utc=True),
            "Open": bar.open,
            "High": bar.high,
            "Low": bar.low,
            "Close": bar.close,
            "Volume": bar.volume,
        })

    if not all_bars:
        raise ValueError("Polygon returned no data")

    df = pd.DataFrame(all_bars)
    df.sort_values("Date", inplace=True)
    df.reset_index(drop=True, inplace=True)
    print(f"Polygon: received {len(df)} candles")
    return df


def fetch_yfinance() -> pd.DataFrame:
    """Fetch BTC 1h data from yfinance (~730 days max)."""
    import yfinance as yf

    print("yfinance: fetching BTC-USD 1h data (max ~730 days) ...")
    ticker = yf.Ticker("BTC-USD")
    df = ticker.history(period="max", interval="1h")

    if df.empty:
        raise ValueError("yfinance returned no data")

    df = df.reset_index()
    # yfinance returns 'Datetime' for intraday
    date_col = "Datetime" if "Datetime" in df.columns else "Date"
    df = df.rename(columns={date_col: "Date"})
    df = df[["Date", "Open", "High", "Low", "Close", "Volume"]]
    df.sort_values("Date", inplace=True)
    df.reset_index(drop=True, inplace=True)
    print(f"yfinance: received {len(df)} candles")
    return df


def main():
    df = None
    api_key = os.environ.get("POLYGON_API_KEY")

    # Try Polygon first
    if api_key:
        try:
            df = fetch_polygon(api_key)
        except Exception as e:
            print(f"Polygon failed: {e}")
            print("Falling back to yfinance ...")
    else:
        print("No POLYGON_API_KEY found, using yfinance fallback.")

    # Fallback to yfinance
    if df is None:
        try:
            df = fetch_yfinance()
        except Exception as e:
            print(f"yfinance also failed: {e}")
            sys.exit(1)

    # Save to CSV
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "btc_1h.csv")
    df.to_csv(out_path, index=False)
    print(f"\nSaved {len(df)} rows to {out_path}")

    # Summary
    print(f"\nDate range: {df['Date'].iloc[0]}  to  {df['Date'].iloc[-1]}")
    print(f"Total candles: {len(df)}")
    print(f"\nFirst 3 rows:\n{df.head(3).to_string(index=False)}")
    print(f"\nLast 3 rows:\n{df.tail(3).to_string(index=False)}")


if __name__ == "__main__":
    main()
