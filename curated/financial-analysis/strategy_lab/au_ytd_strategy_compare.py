"""
AU YTD strategy comparison using a Pine-compatible execution model.

Purpose:
- Use full daily history for indicator warmup.
- Allow new trades only from 2026-01-01 onward.
- Use TradingView-like defaults: 100% equity, 0.1% commission,
  and next-bar-open fills for market orders.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import json
import math

import numpy as np
import pandas as pd
import yfinance as yf


TICKER = "AU"
START = pd.Timestamp("2026-01-01")
INITIAL_CAPITAL = 100_000.0
COMMISSION_RATE = 0.001


def fetch_daily(ticker: str) -> pd.DataFrame:
    df = yf.download(
        ticker,
        period="5y",
        interval="1d",
        auto_adjust=False,
        progress=False,
        threads=False,
    )
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] for c in df.columns]
    df = df[["Open", "High", "Low", "Close", "Volume"]].dropna().copy()
    df.index = pd.to_datetime(df.index).tz_localize(None)
    return df


def sma(series: pd.Series, length: int) -> pd.Series:
    return series.rolling(length, min_periods=length).mean()


def ema(series: pd.Series, length: int) -> pd.Series:
    return series.ewm(span=length, adjust=False).mean()


def stdev(series: pd.Series, length: int) -> pd.Series:
    return series.rolling(length, min_periods=length).std(ddof=0)


def bb_lower(close: pd.Series, length: int, mult: float) -> pd.Series:
    mid = sma(close, length)
    return mid - mult * stdev(close, length)


def true_range(df: pd.DataFrame) -> pd.Series:
    prev_close = df["Close"].shift(1)
    tr = pd.concat(
        [
            df["High"] - df["Low"],
            (df["High"] - prev_close).abs(),
            (df["Low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    tr.iloc[0] = df["High"].iloc[0] - df["Low"].iloc[0]
    return tr


def rma(series: pd.Series, length: int) -> pd.Series:
    values = series.to_numpy(dtype=float)
    out = np.full(len(values), np.nan)
    if len(values) < length:
        return pd.Series(out, index=series.index)
    out[length - 1] = np.nanmean(values[:length])
    for i in range(length, len(values)):
        out[i] = (out[i - 1] * (length - 1) + values[i]) / length
    return pd.Series(out, index=series.index)


def atr(df: pd.DataFrame, length: int) -> pd.Series:
    return rma(true_range(df), length)


@dataclass(frozen=True)
class StrategySpec:
    name: str
    family: str
    params: dict


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    close = out["Close"]
    for n in sorted({2, 6, 8, 11, 20, 30, 54, 66, 75}):
        out[f"SMA{n}"] = sma(close, n)
        out[f"EMA{n}"] = ema(close, n)
    for n, mult in [(8, 2.0), (11, 1.7), (11, 2.0)]:
        out[f"BBL{n}_{str(mult).replace('.', '_')}"] = bb_lower(close, n, mult)
    out["ATR14"] = atr(out, 14)
    return out


def crossed_over(fast: pd.Series, slow: pd.Series, i: int) -> bool:
    if i == 0:
        return False
    vals = (fast.iloc[i], slow.iloc[i], fast.iloc[i - 1], slow.iloc[i - 1])
    if any(pd.isna(v) for v in vals):
        return False
    return vals[0] > vals[1] and vals[2] <= vals[3]


def entry_signal(spec: StrategySpec, data: pd.DataFrame, i: int) -> bool:
    row = data.iloc[i]
    p = spec.params
    if spec.family == "bb_sma":
        lower = row[f"BBL{p['bb_len']}_{str(p['bb_std']).replace('.', '_')}"]
        regime = row["Close"] > row[f"SMA{p['regime_len']}"]
        return not pd.isna(lower) and row["Close"] <= lower and regime
    if spec.family == "bb_ema":
        lower = row[f"BBL{p['bb_len']}_{str(p['bb_std']).replace('.', '_')}"]
        regime = row["Close"] > row[f"EMA{p['regime_len']}"]
        return not pd.isna(lower) and row["Close"] <= lower and regime
    if spec.family == "ema_cross_sma":
        fast = data[f"EMA{p['ema_fast']}"]
        slow = data[f"EMA{p['ema_slow']}"]
        regime = row["Close"] > row[f"SMA{p['regime_len']}"]
        return crossed_over(fast, slow, i) and regime
    if spec.family == "ratchet_rider":
        regime = row["Close"] > row[f"SMA{p['regime_len']}"]
        return row["Close"] > row[f"EMA{p['ema_len']}"] and regime
    raise ValueError(f"Unknown strategy family: {spec.family}")


def simulate(spec: StrategySpec, data: pd.DataFrame) -> dict:
    cash = INITIAL_CAPITAL
    shares = 0.0
    in_position = False
    pending_entry: dict | None = None
    pending_exit: dict | None = None
    current_trade: dict | None = None
    trades: list[dict] = []

    high_water = math.nan
    signal_entry_price = math.nan
    bars_since_exit = 999
    bars_in_trade = 0

    p = spec.params

    for i, (ts, row) in enumerate(data.iterrows()):
        open_price = float(row["Open"])
        close_price = float(row["Close"])

        if pending_exit and in_position:
            exit_value = shares * open_price
            exit_commission = exit_value * COMMISSION_RATE
            cash += exit_value - exit_commission
            net_pnl = cash - current_trade["EntryEquity"]
            ret_pct = net_pnl / current_trade["EntryEquity"] * 100
            trades.append(
                {
                    **current_trade,
                    "ExitSignalTime": pending_exit["signal_time"],
                    "ExitSignalPrice": pending_exit["signal_price"],
                    "ExitTime": ts,
                    "ExitPrice": open_price,
                    "ExitReason": pending_exit["reason"],
                    "ExitCommission": exit_commission,
                    "NetPnL": net_pnl,
                    "ReturnPct": ret_pct,
                    "BarsHeld": current_trade["BarsHeldSignal"],
                }
            )
            shares = 0.0
            in_position = False
            pending_exit = None
            current_trade = None

        if pending_entry and not in_position:
            entry_equity = cash
            shares = pending_entry["shares"]
            entry_value = shares * open_price
            entry_commission = entry_value * COMMISSION_RATE
            cash -= entry_value + entry_commission
            in_position = True
            current_trade = {
                "Strategy": spec.name,
                "EntrySignalTime": pending_entry["signal_time"],
                "EntrySignalPrice": pending_entry["signal_price"],
                "EntryTime": ts,
                "EntryPrice": open_price,
                "EntryEquity": entry_equity,
                "EntryCommission": entry_commission,
                "BarsHeldSignal": 0,
            }
            pending_entry = None

        if not in_position:
            bars_since_exit += 1
            if ts >= START and entry_signal(spec, data, i) and bars_since_exit > p["cooldown"]:
                # TradingView computes percent-of-equity market order quantity from
                # the signal bar, reserves commission, rounds stocks to whole shares,
                # then fills that fixed quantity on the next bar's open.
                order_shares = math.floor(cash / (close_price * (1.0 + COMMISSION_RATE)))
                pending_entry = {
                    "signal_time": ts,
                    "signal_price": close_price,
                    "shares": float(order_shares),
                }
                high_water = close_price
                signal_entry_price = close_price
                bars_in_trade = 0
                bars_since_exit = 0
        else:
            bars_in_trade += 1
            current_trade["BarsHeldSignal"] = bars_in_trade
            high_water = max(high_water, close_price)
            gain_pct = (close_price / signal_entry_price - 1.0) * 100.0

            if p.get("use_atr_trail", False) and not pd.isna(row["ATR14"]) and row["ATR14"] > 0:
                atr_pct = p["atr_mult"] * float(row["ATR14"]) / close_price * 100.0
                if gain_pct <= p["ratchet_at"]:
                    trail = min(atr_pct, p["wide_trail"])
                else:
                    trail = min(atr_pct * 0.5, p["tight_trail"])
                trail = max(trail, 3.0)
            else:
                trail = p["tight_trail"] if gain_pct > p["ratchet_at"] else p["wide_trail"]

            trail_level = high_water * (1.0 - trail / 100.0)
            reason = None
            if close_price < trail_level:
                reason = f"Trail {trail:.1f}%"
            elif p.get("profit_target", 0) > 0 and gain_pct >= p["profit_target"]:
                reason = f"Target {p['profit_target']:.0f}%"
            elif p.get("time_stop", 0) > 0 and bars_in_trade >= p["time_stop"]:
                reason = f"Time {p['time_stop']} bars"

            if reason:
                pending_exit = {
                    "signal_time": ts,
                    "signal_price": close_price,
                    "reason": reason,
                }
                bars_since_exit = 0

    last_close = float(data["Close"].iloc[-1])
    final_equity = cash + shares * last_close
    open_trade = None
    if in_position and current_trade:
        open_trade = {
            **current_trade,
            "MarkPrice": last_close,
            "OpenNetPnL": final_equity - current_trade["EntryEquity"],
            "OpenReturnPct": (final_equity / current_trade["EntryEquity"] - 1.0) * 100.0,
        }

    closed_net = sum(t["NetPnL"] for t in trades)
    wins = [t for t in trades if t["NetPnL"] > 0]
    return {
        "name": spec.name,
        "net_profit_including_open": final_equity - INITIAL_CAPITAL,
        "return_pct_including_open": (final_equity / INITIAL_CAPITAL - 1.0) * 100.0,
        "closed_net_profit": closed_net,
        "closed_return_pct": closed_net / INITIAL_CAPITAL * 100.0,
        "final_equity": final_equity,
        "closed_trades": len(trades),
        "open_trade": open_trade,
        "win_rate_pct": (len(wins) / len(trades) * 100.0) if trades else 0.0,
        "trades": trades,
    }


def buy_hold_ytd(data: pd.DataFrame) -> dict:
    ytd = data[data.index >= START]
    entry = float(ytd["Open"].iloc[0])
    last = float(ytd["Close"].iloc[-1])
    shares = INITIAL_CAPITAL / entry
    final = shares * last
    return {
        "entry_time": str(ytd.index[0].date()),
        "entry_price": entry,
        "last_time": str(ytd.index[-1].date()),
        "last_close": last,
        "return_pct": (final / INITIAL_CAPITAL - 1.0) * 100.0,
        "final_equity": final,
    }


def main() -> None:
    data = add_indicators(fetch_daily(TICKER))
    specs = [
        StrategySpec(
            "BBDip Compounder V16",
            "bb_sma",
            {
                "bb_len": 11,
                "bb_std": 1.7,
                "regime_len": 54,
                "wide_trail": 34.5,
                "tight_trail": 11.9,
                "ratchet_at": 62.0,
                "profit_target": 32.0,
                "time_stop": 0,
                "cooldown": 3,
                "use_atr_trail": True,
                "atr_mult": 3.8,
            },
        ),
        StrategySpec(
            "BBDip V14 Full-Data Genetic",
            "bb_sma",
            {
                "bb_len": 8,
                "bb_std": 2.0,
                "regime_len": 66,
                "wide_trail": 21.5,
                "tight_trail": 5.1,
                "ratchet_at": 59.0,
                "profit_target": 75.0,
                "time_stop": 86,
                "cooldown": 8,
            },
        ),
        StrategySpec(
            "BBDip Genetic V13",
            "bb_ema",
            {
                "bb_len": 11,
                "bb_std": 2.0,
                "regime_len": 66,
                "wide_trail": 34.2,
                "tight_trail": 3.7,
                "ratchet_at": 60.0,
                "profit_target": 74.0,
                "time_stop": 82,
                "cooldown": 4,
            },
        ),
        StrategySpec(
            "EMACross 722 V11",
            "ema_cross_sma",
            {
                "ema_fast": 6,
                "ema_slow": 20,
                "regime_len": 30,
                "wide_trail": 34.0,
                "tight_trail": 20.0,
                "ratchet_at": 100.0,
                "profit_target": 70.0,
                "time_stop": 0,
                "cooldown": 2,
            },
        ),
        StrategySpec(
            "RatchetRider V8",
            "ratchet_rider",
            {
                "ema_len": 2,
                "regime_len": 75,
                "wide_trail": 20.0,
                "tight_trail": 11.0,
                "ratchet_at": 40.0,
                "profit_target": 0.0,
                "time_stop": 0,
                "cooldown": 2,
            },
        ),
    ]

    results = [simulate(spec, data) for spec in specs]
    results.sort(key=lambda x: x["return_pct_including_open"], reverse=True)
    bh = buy_hold_ytd(data)

    output = {
        "ticker": TICKER,
        "source": "yfinance",
        "start": str(START.date()),
        "last_bar": str(data.index[-1].date()),
        "last_close": float(data["Close"].iloc[-1]),
        "initial_capital": INITIAL_CAPITAL,
        "commission_rate": COMMISSION_RATE,
        "buy_hold_ytd": bh,
        "ranked_results": results,
    }

    out_path = Path(__file__).with_name("au_ytd_strategy_compare_results.json")
    out_path.write_text(json.dumps(output, indent=2, default=str))

    print("=" * 78)
    print(f"AU YTD STRATEGY COMPARISON | {START.date()} -> {data.index[-1].date()}")
    print("=" * 78)
    print(
        f"Buy & hold: {bh['return_pct']:+.2f}% | "
        f"${INITIAL_CAPITAL:,.0f} -> ${bh['final_equity']:,.0f}"
    )
    print()
    for rank, result in enumerate(results, 1):
        open_flag = " + OPEN" if result["open_trade"] else ""
        print(
            f"{rank}. {result['name']:<28} "
            f"{result['return_pct_including_open']:+8.2f}% "
            f"${result['final_equity']:>11,.0f} "
            f"closed={result['closed_trades']} wr={result['win_rate_pct']:.0f}%{open_flag}"
        )
    print()
    best = results[0]
    print("BEST:", best["name"])
    print("Trades:")
    for t in best["trades"]:
        print(
            f"  {t['EntryTime'].date()} @ {t['EntryPrice']:.2f} -> "
            f"{t['ExitTime'].date()} @ {t['ExitPrice']:.2f} | "
            f"{t['ReturnPct']:+.2f}% | ${t['NetPnL']:+,.0f} | {t['ExitReason']}"
        )
    if best["open_trade"]:
        ot = best["open_trade"]
        print(
            f"  OPEN {ot['EntryTime'].date()} @ {ot['EntryPrice']:.2f} -> "
            f"mark {data.index[-1].date()} @ {ot['MarkPrice']:.2f} | "
            f"{ot['OpenReturnPct']:+.2f}% | ${ot['OpenNetPnL']:+,.0f}"
        )
    print()
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
