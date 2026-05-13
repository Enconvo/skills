"""
Strategy Signal: AU — Run #1 strategy (RSI + ATR Trailing) on fresh data.
"""
import yfinance as yf
import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ── Step 1: Download fresh data ──────────────────────────────────
print("Downloading fresh AU data...")
ticker = yf.Ticker("AU")
df = ticker.history(period="2y", interval="1h")
df.index = pd.to_datetime(df.index, utc=True).tz_localize(None)
df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
df = df.dropna()

# Save to CSV so load_au_data works
import os
_output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "tradingview")
if os.path.isdir(_output_dir):
    df.to_csv(os.path.join(_output_dir, "au_1h.csv"))

last_ts = df.index[-1]
last_price = df['Close'].iloc[-1]
now = datetime.now()
# Check if market is likely open (rough: Mon-Fri 9:30-16:00 ET)
is_weekday = now.weekday() < 5
market_status = "Market hours" if is_weekday else "Weekend (market closed)"

print(f"Got {len(df)} candles: {df.index[0]} → {last_ts}")
print(f"Last price: ${last_price:.2f} | {market_status}")
print()

# ── Step 2: Run strategy with state tracking ─────────────────────
state = {}

def calc_rsi(close, period):
    return talib.RSI(close, timeperiod=period)

def calc_atr(high, low, close, period):
    return talib.ATR(high, low, close, timeperiod=period)


class RSIATRTrailingState(Strategy):
    rsi_period = 14
    rsi_entry = 30
    atr_period = 14
    atr_mult = 2.0

    def init(self):
        self.rsi = self.I(calc_rsi, self.data.Close, self.rsi_period)
        self.atr = self.I(calc_atr, self.data.High, self.data.Low,
                          self.data.Close, self.atr_period)
        self.highest = 0
        self.trail_stop = 0
        self.entry_price = 0
        self.entry_date = None

    def next(self):
        price = self.data.Close[-1]
        atr_val = self.atr[-1]

        if np.isnan(atr_val):
            return

        if not self.position:
            if self.rsi[-1] < self.rsi_entry:
                self.buy()
                self.highest = price
                self.trail_stop = price - self.atr_mult * atr_val
                self.entry_price = price
                self.entry_date = str(self.data.index[-1])
        else:
            if price > self.highest:
                self.highest = price
            new_stop = self.highest - self.atr_mult * atr_val
            if new_stop > self.trail_stop:
                self.trail_stop = new_stop
            if price < self.trail_stop:
                self.position.close()
                self.highest = 0
                self.trail_stop = 0
                self.entry_price = 0
                self.entry_date = None

        # Capture state every bar
        state['in_position'] = bool(self.position)
        state['price'] = price
        state['rsi'] = float(self.rsi[-1]) if not np.isnan(self.rsi[-1]) else 0
        state['atr'] = float(atr_val)
        state['highest'] = self.highest
        state['trail_stop'] = self.trail_stop
        state['entry_price'] = self.entry_price
        state['entry_date'] = self.entry_date
        state['timestamp'] = str(self.data.index[-1])


bt = Backtest(df, RSIATRTrailingState, cash=100_000, commission=0.001, exclusive_orders=True)
stats = bt.run()

# ── Step 3: Extract track record ────────────────────────────────
ret = stats['Return [%]']
sharpe = stats['Sharpe Ratio']
sortino = stats['Sortino Ratio']
maxdd = stats['Max. Drawdown [%]']
winrate = stats['Win Rate [%]']
trades = stats['# Trades']

# ── Step 4: Print report ────────────────────────────────────────
print("=" * 60)
print(f"  STRATEGY STATE: AU — RSI + ATR Trailing (#1)")
print(f"  Last candle: {state['timestamp']} ({market_status})")
print("=" * 60)

if state['in_position']:
    pnl = (state['price'] - state['entry_price']) / state['entry_price'] * 100
    dist_to_stop = state['price'] - state['trail_stop']
    dist_pct = dist_to_stop / state['price'] * 100
    atr_away = dist_to_stop / state['atr'] if state['atr'] > 0 else 0

    print(f"\n  STATUS: IN POSITION (LONG)")
    print(f"  Entry:              ${state['entry_price']:.2f} on {state['entry_date']}")
    print(f"  Current:            ${state['price']:.2f} ({pnl:+.2f}%)")
    print(f"  Highest since entry:${state['highest']:.2f}")
    print(f"  Trailing Stop:      ${state['trail_stop']:.2f}")
    print(f"  Distance to stop:   ${dist_to_stop:.2f} ({dist_pct:.1f}%)")
    print(f"  ATR:                ${state['atr']:.2f} ({atr_away:.1f}x ATR from stop)")

    if atr_away < 1.0:
        print(f"\n  WARNING: Price within 1 ATR of trailing stop. Exit may be imminent.")
    else:
        print(f"\n  Position healthy — {atr_away:.1f}x ATR buffer above stop.")

    print(f"\n  ACTION: Hold. Let the trailing stop manage the exit.")
    print(f"  Exit triggers: Price drops below ${state['trail_stop']:.2f}")

else:
    rsi_val = state['rsi']
    distance = rsi_val - 30
    print(f"\n  STATUS: FLAT (no position)")
    print(f"  Current Price:  ${state['price']:.2f}")
    print(f"  RSI (14):       {rsi_val:.1f} (entry trigger: < 30)")
    print(f"  Distance:       RSI needs to drop {distance:.1f} points")
    print(f"  ATR (14):       ${state['atr']:.2f}")

    if rsi_val < 35:
        print(f"\n  APPROACHING — RSI at {rsi_val:.1f}, close to 30 entry trigger.")
    elif rsi_val > 60:
        print(f"\n  WAITING — RSI at {rsi_val:.1f}, far from oversold. Be patient.")
    else:
        print(f"\n  NEUTRAL — RSI at {rsi_val:.1f}, not near entry zone yet.")

    print(f"\n  ACTION: No trade. Wait for RSI < 30 (oversold dip).")
    print(f"  The strategy's edge comes from buying oversold dips — don't front-run.")

print(f"\n── Strategy Track Record (on fresh data) ──────────────────")
print(f"  Return: {ret:.1f}%  |  Win Rate: {winrate:.1f}%  |  Sharpe: {sharpe:.2f}")
print(f"  Trades: {trades}  |  Sortino: {sortino:.2f}  |  Max DD: {maxdd:.1f}%")
print("=" * 60)
