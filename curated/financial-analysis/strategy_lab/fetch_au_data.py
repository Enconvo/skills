"""Download AU (Barrick Gold) historical data for backtesting."""

import yfinance as yf
import pandas as pd
import os

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

# Download max available 1h data (yfinance gives ~2 years for 1h)
print("Downloading AU 1h data from Yahoo Finance...")
ticker = yf.Ticker("AU")
data = ticker.history(period="2y", interval="1h")

print(f"Downloaded {len(data)} candles")
print(f"Date range: {data.index[0]} to {data.index[-1]}")

# Clean up columns for backtesting.py format
data = data[["Open", "High", "Low", "Close", "Volume"]]
data.index.name = "Date"
data = data.dropna()

# Save
csv_path = os.path.join(PROJECT_DIR, "au_1h.csv")
data.to_csv(csv_path)
print(f"Saved to {csv_path}")
print(f"Final: {len(data)} candles")

# Also download daily for swing trading strategies
print("\nDownloading AU daily data (5 years)...")
data_daily = ticker.history(period="5y", interval="1d")
data_daily = data_daily[["Open", "High", "Low", "Close", "Volume"]]
data_daily.index.name = "Date"
data_daily = data_daily.dropna()

csv_daily = os.path.join(PROJECT_DIR, "au_daily.csv")
data_daily.to_csv(csv_daily)
print(f"Saved to {csv_daily}")
print(f"Final: {len(data_daily)} daily candles")
