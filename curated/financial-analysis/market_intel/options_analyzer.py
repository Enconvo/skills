"""Options Analysis Module — GEX, DEX, IV Skew, Max Pain, P/C Ratio, OI Walls.

Data source: Yahoo Finance (primary), Polygon (cross-verification).
Greeks computed via Black-Scholes (scipy).
"""
import sys
import json
import time
import math
import os
from datetime import datetime, date
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

from config import OPTIONS, POLYGON_API_KEY
from data_sources import (
    fetch_spot_price,
    fetch_option_expirations,
    fetch_option_chain,
    polygon_option_prev_close,
    fred_latest,
    WATCHLIST_CONFIG,
)


# ── Black-Scholes Greeks ───────────────────────────────────────────────

def black_scholes_greeks(S: float, K: float, T: float, r: float,
                         sigma: float, option_type: str = "call") -> dict:
    """Compute Black-Scholes greeks for a single option.

    Args:
        S: Spot price
        K: Strike price
        T: Time to expiration in years
        r: Risk-free rate (annualized, e.g. 0.045 for 4.5%)
        sigma: Implied volatility (annualized, e.g. 0.30 for 30%)
        option_type: "call" or "put"

    Returns:
        Dict with delta, gamma, theta, vega.
    """
    if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
        return {"delta": 0, "gamma": 0, "theta": 0, "vega": 0}

    sqrt_T = math.sqrt(T)
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * sqrt_T)
    d2 = d1 - sigma * sqrt_T

    gamma = norm.pdf(d1) / (S * sigma * sqrt_T)
    vega = S * norm.pdf(d1) * sqrt_T / 100  # per 1% move in IV

    if option_type == "call":
        delta = norm.cdf(d1)
        theta = (-(S * norm.pdf(d1) * sigma) / (2 * sqrt_T)
                 - r * K * math.exp(-r * T) * norm.cdf(d2)) / 365
    else:
        delta = norm.cdf(d1) - 1
        theta = (-(S * norm.pdf(d1) * sigma) / (2 * sqrt_T)
                 + r * K * math.exp(-r * T) * norm.cdf(-d2)) / 365

    return {
        "delta": round(delta, 4),
        "gamma": round(gamma, 6),
        "theta": round(theta, 4),
        "vega": round(vega, 4),
    }


def compute_greeks_for_chain(chain_df: pd.DataFrame, spot: float, r: float,
                             dte_years: float, option_type: str) -> pd.DataFrame:
    """Add delta, gamma, theta, vega columns to an options chain DataFrame."""
    if chain_df.empty:
        return chain_df

    greeks = []
    for _, row in chain_df.iterrows():
        iv = row.get("impliedVolatility", 0)
        strike = row.get("strike", 0)
        if pd.isna(iv) or iv <= 0 or pd.isna(strike) or strike <= 0:
            greeks.append({"delta": 0, "gamma": 0, "theta": 0, "vega": 0})
            continue
        g = black_scholes_greeks(spot, strike, dte_years, r, iv, option_type)
        greeks.append(g)

    greeks_df = pd.DataFrame(greeks)
    for col in greeks_df.columns:
        chain_df[col] = greeks_df[col].values
    return chain_df


# ── Options Analytics ──────────────────────────────────────────────────

def compute_put_call_ratio(calls: pd.DataFrame, puts: pd.DataFrame) -> dict:
    """Compute put/call ratio by volume and open interest."""
    call_vol = calls["volume"].sum()
    put_vol = puts["volume"].sum()
    call_oi = calls["openInterest"].sum()
    put_oi = puts["openInterest"].sum()

    vol_ratio = round(put_vol / call_vol, 3) if call_vol > 0 else None
    oi_ratio = round(put_oi / call_oi, 3) if call_oi > 0 else None

    if vol_ratio is not None:
        if vol_ratio > OPTIONS["pc_ratio_bearish"]:
            interpretation = "BEARISH — heavy put buying"
        elif vol_ratio < OPTIONS["pc_ratio_bullish"]:
            interpretation = "BULLISH — heavy call buying"
        else:
            interpretation = "NEUTRAL"
    else:
        interpretation = "INSUFFICIENT DATA"

    return {
        "volume_ratio": vol_ratio,
        "oi_ratio": oi_ratio,
        "call_volume": int(call_vol),
        "put_volume": int(put_vol),
        "call_oi": int(call_oi),
        "put_oi": int(put_oi),
        "interpretation": interpretation,
    }


def compute_iv_skew(calls: pd.DataFrame, puts: pd.DataFrame, spot: float) -> dict:
    """Compute IV skew — OI-weighted average IV for puts vs calls.

    Positive skew = puts more expensive (bearish hedging demand).
    Negative skew = calls more expensive (bullish speculation).
    """
    def oi_weighted_iv(df):
        mask = (df["impliedVolatility"] > 0) & (df["openInterest"] > 0)
        filtered = df[mask]
        if filtered.empty:
            return 0
        weights = filtered["openInterest"]
        return float(np.average(filtered["impliedVolatility"], weights=weights))

    put_iv = oi_weighted_iv(puts)
    call_iv = oi_weighted_iv(calls)
    skew = round(put_iv - call_iv, 4)

    if skew > OPTIONS["iv_skew_bearish"]:
        interpretation = "BEARISH — puts command premium (hedging demand)"
    elif skew < OPTIONS["iv_skew_bullish"]:
        interpretation = "BULLISH — calls command premium (speculative demand)"
    else:
        interpretation = "NEUTRAL — balanced IV"

    return {
        "skew": skew,
        "put_iv_avg": round(put_iv, 4),
        "call_iv_avg": round(call_iv, 4),
        "interpretation": interpretation,
    }


def compute_max_pain(calls: pd.DataFrame, puts: pd.DataFrame) -> dict:
    """Compute max pain strike — the price at which total option holder losses are maximized.

    Max pain theory: market makers drive price toward max pain at expiration.
    """
    all_strikes = sorted(set(calls["strike"].tolist() + puts["strike"].tolist()))
    if not all_strikes:
        return {"max_pain": None}

    min_pain = float("inf")
    max_pain_strike = all_strikes[0]

    for test_price in all_strikes:
        total_pain = 0
        # Call holder pain: max(0, strike - test_price) * OI (calls expire worthless below strike)
        # Actually: call holder loses when price < strike. Pain = max(0, strike_paid - intrinsic)
        # Simplified: total value lost by all option holders at test_price
        for _, row in calls.iterrows():
            intrinsic = max(0, test_price - row["strike"])
            # Calls: holders paid premium, get intrinsic. Pain is when intrinsic is low.
            # But max pain counts total ITM value that must be paid out
            total_pain += intrinsic * row["openInterest"]
        for _, row in puts.iterrows():
            intrinsic = max(0, row["strike"] - test_price)
            total_pain += intrinsic * row["openInterest"]

        if total_pain < min_pain:
            min_pain = total_pain
            max_pain_strike = test_price

    return {
        "max_pain": round(max_pain_strike, 2),
        "total_payout_at_max_pain": round(min_pain, 0),
    }


def compute_gex(calls: pd.DataFrame, puts: pd.DataFrame, spot: float) -> dict:
    """Compute Gamma Exposure (GEX) — net dealer gamma by strike.

    Positive GEX = dealers are long gamma → mean-reversion (supportive).
    Negative GEX = dealers are short gamma → momentum/volatility amplifier.
    GEX flip strike = where dealer gamma changes sign.
    """
    gex_by_strike = {}

    # Dealers are SHORT calls (sold to buyers) → positive gamma
    for _, row in calls.iterrows():
        strike = row["strike"]
        gamma = row.get("gamma", 0)
        oi = row["openInterest"]
        # Dealer gamma from calls: +gamma * OI * 100 * spot (notional)
        dealer_gex = gamma * oi * 100 * spot
        gex_by_strike[strike] = gex_by_strike.get(strike, 0) + dealer_gex

    # Dealers are SHORT puts (sold to buyers) → negative gamma
    for _, row in puts.iterrows():
        strike = row["strike"]
        gamma = row.get("gamma", 0)
        oi = row["openInterest"]
        # Dealer gamma from puts: -gamma * OI * 100 * spot (notional)
        dealer_gex = -gamma * oi * 100 * spot
        gex_by_strike[strike] = gex_by_strike.get(strike, 0) + dealer_gex

    total_gex = sum(gex_by_strike.values())

    # Find GEX flip strike (where cumulative GEX changes sign)
    flip_strike = None
    sorted_strikes = sorted(gex_by_strike.keys())
    cumulative = 0
    for s in sorted_strikes:
        prev_cum = cumulative
        cumulative += gex_by_strike[s]
        if prev_cum < 0 and cumulative >= 0:
            flip_strike = s
            break
        elif prev_cum >= 0 and cumulative < 0:
            flip_strike = s
            break

    if total_gex > 0:
        interpretation = "POSITIVE GEX — dealers long gamma → mean-reversion, suppressed vol"
    elif total_gex < 0:
        interpretation = "NEGATIVE GEX — dealers short gamma → momentum amplifier, elevated vol"
    else:
        interpretation = "NEUTRAL GEX"

    # Top 5 GEX strikes
    top_strikes = sorted(gex_by_strike.items(), key=lambda x: abs(x[1]), reverse=True)[:5]

    return {
        "total_gex": round(total_gex, 0),
        "gex_by_strike": {k: round(v, 0) for k, v in gex_by_strike.items()},
        "flip_strike": flip_strike,
        "top_strikes": [(s, round(g, 0)) for s, g in top_strikes],
        "interpretation": interpretation,
    }


def compute_dex(calls: pd.DataFrame, puts: pd.DataFrame, spot: float) -> dict:
    """Compute Delta Exposure (DEX) — net dealer delta by strike.

    Shows directional hedging pressure from dealers.
    """
    dex_by_strike = {}

    # Dealers short calls → negative delta (they sell calls, hedge by buying stock)
    for _, row in calls.iterrows():
        strike = row["strike"]
        delta = row.get("delta", 0)
        oi = row["openInterest"]
        # To hedge short calls, dealers buy shares: delta * OI * 100
        dealer_dex = delta * oi * 100
        dex_by_strike[strike] = dex_by_strike.get(strike, 0) + dealer_dex

    # Dealers short puts → positive delta (they sell puts, hedge by selling stock)
    for _, row in puts.iterrows():
        strike = row["strike"]
        delta = row.get("delta", 0)  # negative for puts
        oi = row["openInterest"]
        # To hedge short puts, dealers sell shares: |delta| * OI * 100
        dealer_dex = -delta * oi * 100  # flip sign since put delta is negative
        dex_by_strike[strike] = dex_by_strike.get(strike, 0) - dealer_dex

    total_dex = sum(dex_by_strike.values())

    return {
        "total_dex": round(total_dex, 0),
        "dex_by_strike": {k: round(v, 0) for k, v in dex_by_strike.items()},
    }


def find_oi_walls(calls: pd.DataFrame, puts: pd.DataFrame, top_n: int = 5) -> dict:
    """Find highest OI strikes — call walls (resistance) and put walls (support)."""
    call_walls = (
        calls[["strike", "openInterest"]]
        .sort_values("openInterest", ascending=False)
        .head(top_n)
    )
    put_walls = (
        puts[["strike", "openInterest"]]
        .sort_values("openInterest", ascending=False)
        .head(top_n)
    )

    return {
        "call_walls": [(row["strike"], int(row["openInterest"])) for _, row in call_walls.iterrows()],
        "put_walls": [(row["strike"], int(row["openInterest"])) for _, row in put_walls.iterrows()],
    }


def compute_options_sentiment(pc_ratio: dict, skew: dict, gex: dict,
                              max_pain: dict, spot: float) -> dict:
    """Compute composite options sentiment score (0-100, higher = more bullish).

    Components:
    - P/C ratio inverted (low P/C = bullish) — 25%
    - IV skew inverted (negative skew = calls expensive = bullish) — 25%
    - GEX sign (positive = mean-reversion = bullish for longs) — 25%
    - Max pain magnet (spot below max pain = bullish pull) — 25%
    """
    scores = []
    weights = []

    # P/C ratio → score (inverted: low ratio = bullish)
    vol_ratio = pc_ratio.get("volume_ratio")
    if vol_ratio is not None:
        # Map: 0.3 → 90, 0.7 → 65, 1.0 → 50, 1.5 → 25, 2.0 → 10
        pc_score = max(0, min(100, 100 - (vol_ratio - 0.3) * 52.9))
        scores.append(pc_score)
        weights.append(25)

    # IV skew → score (inverted: negative skew = bullish)
    skew_val = skew.get("skew")
    if skew_val is not None:
        # Map: -0.10 → 85, 0 → 50, +0.10 → 15
        skew_score = max(0, min(100, 50 - skew_val * 350))
        scores.append(skew_score)
        weights.append(25)

    # GEX sign → score
    total_gex = gex.get("total_gex", 0)
    if total_gex > 0:
        gex_score = 70  # Positive = supportive
    elif total_gex < 0:
        gex_score = 30  # Negative = volatile
    else:
        gex_score = 50
    scores.append(gex_score)
    weights.append(25)

    # Max pain magnet
    mp = max_pain.get("max_pain")
    if mp and spot and spot > 0.01:
        # Spot below max pain → bullish pull, spot above → bearish pull
        pct_from_mp = (mp - spot) / spot
        mp_score = max(0, min(100, 50 + pct_from_mp * 500))
        scores.append(mp_score)
        weights.append(25)

    if not scores:
        return {"score": 50, "label": "INSUFFICIENT DATA", "components": {}}

    total_weight = sum(weights)
    composite = sum(s * w for s, w in zip(scores, weights)) / total_weight

    if composite >= 75:
        label = "STRONG BULLISH"
    elif composite >= 60:
        label = "LEANING BULLISH"
    elif composite >= 40:
        label = "NEUTRAL"
    elif composite >= 25:
        label = "LEANING BEARISH"
    else:
        label = "STRONG BEARISH"

    return {
        "score": round(composite, 1),
        "label": label,
        "components": {
            "pc_ratio_score": round(scores[0], 1) if len(scores) > 0 else None,
            "iv_skew_score": round(scores[1], 1) if len(scores) > 1 else None,
            "gex_score": round(scores[2], 1) if len(scores) > 2 else None,
            "max_pain_score": round(scores[3], 1) if len(scores) > 3 else None,
        },
    }


# ── Expiration Selection ───────────────────────────────────────────────

def select_expirations(all_exps: list[str], max_dte: int = None,
                       max_count: int = None) -> list[str]:
    """Select up to 4 expirations: nearest 3 weeklies + nearest monthly (max 45 DTE).

    Args:
        all_exps: List of expiration date strings (YYYY-MM-DD)
        max_dte: Maximum days to expiration (default from config)
        max_count: Maximum number of expirations (default from config)
    """
    if max_dte is None:
        max_dte = OPTIONS["max_dte"]
    if max_count is None:
        max_count = OPTIONS["max_expirations"]

    today = date.today()
    valid = []
    for exp_str in all_exps:
        try:
            exp_date = date.fromisoformat(exp_str)
            dte = (exp_date - today).days
            if 0 < dte <= max_dte:
                valid.append((exp_str, exp_date, dte))
        except ValueError:
            continue

    valid.sort(key=lambda x: x[2])

    # Take nearest 3
    selected = valid[:3]

    # Add nearest monthly (3rd Friday) if not already included
    for exp_str, exp_date, dte in valid:
        if exp_date.weekday() == 4 and 15 <= exp_date.day <= 21:
            if exp_str not in [s[0] for s in selected]:
                selected.append((exp_str, exp_date, dte))
                break

    return [s[0] for s in selected[:max_count]]


# ── Cross-Verification ─────────────────────────────────────────────────

def cross_verify_with_polygon(ticker: str, calls: pd.DataFrame,
                              puts: pd.DataFrame) -> list[str]:
    """Cross-verify Yahoo option prices against Polygon prev close.

    Checks a sample of ATM options. Returns list of discrepancy notes.
    """
    if not POLYGON_API_KEY:
        return ["Polygon API key not set — skipping cross-verification"]

    notes = []
    # Sample: check 2 ATM calls and 2 ATM puts
    for label, df, opt_type in [("call", calls, "call"), ("put", puts, "put")]:
        if df.empty:
            continue
        # Get 2 highest-OI contracts
        top = df.nlargest(2, "openInterest")
        for _, row in top.iterrows():
            strike = row["strike"]
            yahoo_price = row.get("lastPrice", 0)
            if pd.isna(yahoo_price) or yahoo_price <= 0:
                continue
            # Need expiry from the contract symbol or pass it in
            # For now, skip if we can't determine expiry
            # This would need the expiry passed as context
            # Placeholder — polygon_option_prev_close needs expiry
    if not notes:
        notes.append("Cross-verification: no Polygon checks performed (need expiry context)")
    return notes


# ── Chart Generation ───────────────────────────────────────────────────

def generate_options_chart(ticker: str, spot: float,
                           chains_by_expiry: dict[str, tuple[pd.DataFrame, pd.DataFrame]],
                           max_pain: dict) -> str | None:
    """Generate interactive HTML chart with multi-select expiration checkboxes.

    All data is embedded as JSON. JavaScript recalculates GEX, OI, and IV
    on-the-fly when the user toggles expiration checkboxes.

    Args:
        ticker: Stock ticker symbol
        spot: Current spot price
        chains_by_expiry: Dict of {expiry_str: (calls_df, puts_df)} with greeks computed
        max_pain: Max pain dict from compute_max_pain()

    Returns:
        Path to saved HTML file, or None on failure.
    """
    try:
        import plotly  # just to confirm installed
    except ImportError:
        print("⚠ plotly not installed — skipping chart generation")
        return None

    # Serialize per-expiration data to JSON-safe dicts
    expiry_data = {}
    for exp, (calls, puts) in chains_by_expiry.items():
        exp_entry = {"calls": [], "puts": []}
        if not calls.empty:
            for _, row in calls.iterrows():
                exp_entry["calls"].append({
                    "strike": float(row.get("strike", 0)),
                    "oi": int(row.get("openInterest", 0)),
                    "volume": int(row.get("volume", 0)),
                    "iv": float(row.get("impliedVolatility", 0)),
                    "gamma": float(row.get("gamma", 0)),
                    "delta": float(row.get("delta", 0)),
                })
        if not puts.empty:
            for _, row in puts.iterrows():
                exp_entry["puts"].append({
                    "strike": float(row.get("strike", 0)),
                    "oi": int(row.get("openInterest", 0)),
                    "volume": int(row.get("volume", 0)),
                    "iv": float(row.get("impliedVolatility", 0)),
                    "gamma": float(row.get("gamma", 0)),
                    "delta": float(row.get("delta", 0)),
                })
        expiry_data[exp] = exp_entry

    mp_strike = max_pain.get("max_pain")
    expirations = sorted(expiry_data.keys())

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Options Analysis: {ticker}</title>
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ background: #111; color: #eee; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }}
  .header {{ padding: 16px 24px; display: flex; align-items: center; gap: 24px; flex-wrap: wrap;
             border-bottom: 1px solid #333; background: #1a1a1a; }}
  .header h1 {{ font-size: 20px; white-space: nowrap; }}
  .header .spot {{ color: #2196F3; font-size: 18px; font-weight: 600; }}
  .controls {{ display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }}
  .controls label {{ font-size: 13px; cursor: pointer; padding: 4px 10px; border-radius: 4px;
                     border: 1px solid #444; transition: all 0.15s; user-select: none; }}
  .controls label:hover {{ border-color: #888; }}
  .controls input:checked + span {{ color: #00E676; }}
  .controls label.checked {{ background: #263238; border-color: #00E676; }}
  .controls input {{ display: none; }}
  .btn {{ font-size: 12px; cursor: pointer; padding: 4px 10px; border-radius: 4px;
          border: 1px solid #555; background: #222; color: #aaa; margin-left: 4px; }}
  .btn:hover {{ background: #333; color: #fff; }}
  .summary {{ padding: 8px 24px; font-size: 13px; color: #aaa; background: #151515;
              border-bottom: 1px solid #222; display: flex; gap: 24px; flex-wrap: wrap; }}
  .summary .val {{ color: #fff; font-weight: 600; }}
  .summary .bullish {{ color: #00E676; }}
  .summary .bearish {{ color: #FF1744; }}
  .summary .neutral {{ color: #FFD600; }}
  #chart {{ width: 100%; height: calc(100vh - 100px); }}
</style>
</head>
<body>
<div class="header">
  <h1>Options: {ticker}</h1>
  <span class="spot">Spot ${spot:.2f}</span>
  <div class="controls">
    <span style="color:#888;font-size:12px;">Expirations:</span>
    {"".join(f'<label class="checked" id="lbl_{exp}"><input type="checkbox" checked value="{exp}" onchange="toggle(this)"><span>{exp}</span></label>' for exp in expirations)}
    <button class="btn" onclick="selectAll()">All</button>
    <button class="btn" onclick="selectNone()">None</button>
  </div>
</div>
<div class="summary" id="summary"></div>
<div id="chart"></div>

<script>
const SPOT = {spot};
const MAX_PAIN = {mp_strike if mp_strike else 'null'};
const DATA = {json.dumps(expiry_data, default=str)};
const EXPIRATIONS = {json.dumps(expirations)};

function getSelected() {{
  return EXPIRATIONS.filter(e => document.querySelector(`input[value="${{e}}"]`).checked);
}}

function toggle(cb) {{
  const lbl = cb.parentElement;
  if (cb.checked) lbl.classList.add('checked');
  else lbl.classList.remove('checked');
  rebuild();
}}

function selectAll() {{
  EXPIRATIONS.forEach(e => {{
    const cb = document.querySelector(`input[value="${{e}}"]`);
    cb.checked = true; cb.parentElement.classList.add('checked');
  }});
  rebuild();
}}

function selectNone() {{
  EXPIRATIONS.forEach(e => {{
    const cb = document.querySelector(`input[value="${{e}}"]`);
    cb.checked = false; cb.parentElement.classList.remove('checked');
  }});
  rebuild();
}}

function rebuild() {{
  const sel = getSelected();
  if (sel.length === 0) {{
    Plotly.purge('chart');
    document.getElementById('summary').innerHTML = '<span style="color:#FF1744">Select at least one expiration</span>';
    return;
  }}

  // Aggregate data across selected expirations
  const gexMap = {{}};
  const callOiMap = {{}};
  const putOiMap = {{}};
  const callIvMap = {{}};  // strike -> [iv*oi, oi] for weighted avg
  const putIvMap = {{}};
  let totalCallVol = 0, totalPutVol = 0, totalCallOi = 0, totalPutOi = 0;

  sel.forEach(exp => {{
    const d = DATA[exp];
    d.calls.forEach(c => {{
      const s = c.strike;
      // GEX: dealer short calls → positive gamma
      gexMap[s] = (gexMap[s] || 0) + c.gamma * c.oi * 100 * SPOT;
      callOiMap[s] = (callOiMap[s] || 0) + c.oi;
      totalCallVol += c.volume;
      totalCallOi += c.oi;
      if (c.iv > 0 && c.oi > 0) {{
        if (!callIvMap[s]) callIvMap[s] = [0, 0];
        callIvMap[s][0] += c.iv * c.oi;
        callIvMap[s][1] += c.oi;
      }}
    }});
    d.puts.forEach(p => {{
      const s = p.strike;
      // GEX: dealer short puts → negative gamma
      gexMap[s] = (gexMap[s] || 0) - p.gamma * p.oi * 100 * SPOT;
      putOiMap[s] = (putOiMap[s] || 0) + p.oi;
      totalPutVol += p.volume;
      totalPutOi += p.oi;
      if (p.iv > 0 && p.oi > 0) {{
        if (!putIvMap[s]) putIvMap[s] = [0, 0];
        putIvMap[s][0] += p.iv * p.oi;
        putIvMap[s][1] += p.oi;
      }}
    }});
  }});

  // Sort strikes
  const allStrikes = [...new Set([...Object.keys(gexMap), ...Object.keys(callOiMap), ...Object.keys(putOiMap)])].map(Number).sort((a,b) => a-b);
  const gexStrikes = Object.keys(gexMap).map(Number).sort((a,b) => a-b);
  const gexVals = gexStrikes.map(s => gexMap[s]);
  const gexColors = gexVals.map(v => v >= 0 ? '#00C853' : '#FF1744');
  const totalGex = gexVals.reduce((a,b) => a+b, 0);

  const callOiStrikes = Object.keys(callOiMap).map(Number).sort((a,b) => a-b);
  const callOiVals = callOiStrikes.map(s => callOiMap[s]);
  const putOiStrikes = Object.keys(putOiMap).map(Number).sort((a,b) => a-b);
  const putOiVals = putOiStrikes.map(s => putOiMap[s]);

  const callIvStrikes = Object.keys(callIvMap).map(Number).sort((a,b) => a-b);
  const callIvVals = callIvStrikes.map(s => (callIvMap[s][0] / callIvMap[s][1]) * 100);
  const putIvStrikes = Object.keys(putIvMap).map(Number).sort((a,b) => a-b);
  const putIvVals = putIvStrikes.map(s => (putIvMap[s][0] / putIvMap[s][1]) * 100);

  const pcRatio = totalCallVol > 0 ? (totalPutVol / totalCallVol).toFixed(3) : 'N/A';

  // Summary bar
  const gexClass = totalGex > 0 ? 'bullish' : totalGex < 0 ? 'bearish' : 'neutral';
  const gexLabel = totalGex > 0 ? 'Positive (mean-reversion)' : totalGex < 0 ? 'Negative (momentum)' : 'Neutral';
  const pcClass = pcRatio !== 'N/A' ? (pcRatio < 0.7 ? 'bullish' : pcRatio > 1.3 ? 'bearish' : 'neutral') : 'neutral';
  document.getElementById('summary').innerHTML =
    `<span>Expirations: <span class="val">${{sel.length}}</span></span>` +
    `<span>P/C Ratio: <span class="val ${{pcClass}}">${{pcRatio}}</span></span>` +
    `<span>Total GEX: <span class="val ${{gexClass}}">${{totalGex >= 0 ? '+' : ''}}$$${{(totalGex/1e6).toFixed(1)}}M</span> (${{gexLabel}})</span>` +
    (MAX_PAIN ? `<span>Max Pain: <span class="val">${{MAX_PAIN}}</span></span>` : '') +
    `<span>Call OI: <span class="val">${{totalCallOi.toLocaleString()}}</span> | Put OI: <span class="val">${{totalPutOi.toLocaleString()}}</span></span>`;

  // Build traces
  const traces = [];
  // Row 1: GEX
  traces.push({{
    x: gexStrikes, y: gexVals, type: 'bar', marker: {{ color: gexColors }},
    name: 'GEX', hovertemplate: 'Strike: $%{{x}}<br>GEX: %{{y:,.0f}}<extra></extra>',
    xaxis: 'x', yaxis: 'y'
  }});
  // Row 2: Call OI
  traces.push({{
    x: callOiStrikes, y: callOiVals, type: 'bar', name: 'Call OI',
    marker: {{ color: 'rgba(0, 200, 83, 0.6)' }},
    hovertemplate: 'Strike: $%{{x}}<br>Call OI: %{{y:,.0f}}<extra></extra>',
    xaxis: 'x2', yaxis: 'y2'
  }});
  // Row 2: Put OI
  traces.push({{
    x: putOiStrikes, y: putOiVals, type: 'bar', name: 'Put OI',
    marker: {{ color: 'rgba(255, 23, 68, 0.6)' }},
    hovertemplate: 'Strike: $%{{x}}<br>Put OI: %{{y:,.0f}}<extra></extra>',
    xaxis: 'x2', yaxis: 'y2'
  }});
  // Row 3: Call IV
  if (callIvStrikes.length > 0) {{
    traces.push({{
      x: callIvStrikes, y: callIvVals, type: 'scatter', mode: 'lines+markers',
      name: 'Call IV', line: {{ color: '#00C853' }},
      hovertemplate: 'Strike: $%{{x}}<br>IV: %{{y:.1f}}%<extra></extra>',
      xaxis: 'x3', yaxis: 'y3'
    }});
  }}
  // Row 3: Put IV
  if (putIvStrikes.length > 0) {{
    traces.push({{
      x: putIvStrikes, y: putIvVals, type: 'scatter', mode: 'lines+markers',
      name: 'Put IV', line: {{ color: '#FF1744' }},
      hovertemplate: 'Strike: $%{{x}}<br>IV: %{{y:.1f}}%<extra></extra>',
      xaxis: 'x3', yaxis: 'y3'
    }});
  }}

  // Vertical reference lines as shapes
  const shapes = [
    // Spot line on all 3 subplots
    ...['y','y2','y3'].map(ya => ({{
      type: 'line', x0: SPOT, x1: SPOT, y0: 0, y1: 1, yref: ya + ' domain',
      xref: ya === 'y' ? 'x' : ya === 'y2' ? 'x2' : 'x3',
      line: {{ color: '#2196F3', width: 2 }}
    }}))
  ];
  if (MAX_PAIN) {{
    shapes.push(...['y','y2'].map(ya => ({{
      type: 'line', x0: MAX_PAIN, x1: MAX_PAIN, y0: 0, y1: 1, yref: ya + ' domain',
      xref: ya === 'y' ? 'x' : 'x2',
      line: {{ color: '#FFD600', width: 1.5, dash: 'dash' }}
    }})));
  }}

  const annotations = [
    {{ x: SPOT, y: 1.02, yref: 'y domain', xref: 'x', text: `Spot $${{SPOT.toFixed(2)}}`,
       showarrow: false, font: {{ color: '#2196F3', size: 11 }} }},
    {{ x: 0.5, y: 1.08, xref: 'x domain', yref: 'y domain', text: 'Gamma Exposure (GEX) by Strike',
       showarrow: false, font: {{ color: '#ccc', size: 14 }} }},
    {{ x: 0.5, y: 1.08, xref: 'x2 domain', yref: 'y2 domain', text: 'Open Interest Distribution',
       showarrow: false, font: {{ color: '#ccc', size: 14 }} }},
    {{ x: 0.5, y: 1.08, xref: 'x3 domain', yref: 'y3 domain', text: 'IV Smile',
       showarrow: false, font: {{ color: '#ccc', size: 14 }} }},
  ];
  if (MAX_PAIN) {{
    annotations.push({{ x: MAX_PAIN, y: 0.98, yref: 'y domain', xref: 'x',
      text: `Max Pain $${{MAX_PAIN}}`, showarrow: false, font: {{ color: '#FFD600', size: 11 }} }});
  }}

  const layout = {{
    template: 'plotly_dark',
    paper_bgcolor: '#111',
    plot_bgcolor: '#111',
    showlegend: true,
    legend: {{ orientation: 'h', y: -0.02, x: 0.5, xanchor: 'center' }},
    margin: {{ t: 30, b: 40, l: 60, r: 20 }},
    barmode: 'overlay',
    shapes: shapes,
    annotations: annotations,
    grid: {{ rows: 3, columns: 1, subplots: [['xy'],['x2y2'],['x3y3']], roworder: 'top to bottom', ygap: 0.12 }},
    xaxis:  {{ anchor: 'y',  matches: 'x3' }},
    xaxis2: {{ anchor: 'y2', matches: 'x3' }},
    xaxis3: {{ anchor: 'y3', title: 'Strike Price' }},
    yaxis:  {{ anchor: 'x',  title: 'GEX ($)' }},
    yaxis2: {{ anchor: 'x2', title: 'Open Interest' }},
    yaxis3: {{ anchor: 'x3', title: 'IV (%)' }},
  }};

  Plotly.react('chart', traces, layout, {{ responsive: true }});
}}

// Initial render
rebuild();
</script>
</body>
</html>"""

    # Save to strategy_lab/
    out_dir = Path(__file__).parent.parent / "strategy_lab"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"{ticker.lower()}_options_chart.html"
    out_path.write_text(html)
    print(f"  📊 Chart saved: {out_path}")
    return str(out_path)


# ── Main Analysis Functions ────────────────────────────────────────────

def analyze_options(ticker: str, prefetched: dict | None = None,
                    include_chart: bool = True,
                    verify_polygon: bool = True) -> tuple[str, dict]:
    """Run full options analysis for a single ticker.

    Args:
        ticker: Stock ticker symbol
        prefetched: Optional dict with pre-fetched data (spot, expirations, chains)
        include_chart: Whether to generate HTML chart
        verify_polygon: Whether to cross-verify with Polygon

    Returns:
        Tuple of (report_text, structured_data).
    """
    now = datetime.now()
    lines = []
    structured = {"ticker": ticker, "date": now.strftime("%Y-%m-%d"), "type": "Options Analysis"}

    lines.append(f"╔{'═'*58}╗")
    lines.append(f"║  📊 OPTIONS ANALYSIS: {ticker:<36}║")
    lines.append(f"╚{'═'*58}╝")
    lines.append("")

    # Fetch spot price
    print(f"  → Fetching spot price for {ticker}...")
    spot = (prefetched or {}).get("spot") or fetch_spot_price(ticker)
    if not spot:
        msg = f"⚠ Could not fetch spot price for {ticker}"
        return msg, {"error": msg}
    structured["spot"] = spot
    lines.append(f"  Spot Price: ${spot:.2f}")

    # Fetch risk-free rate
    r = fred_latest("DGS2")
    if r is not None:
        r = r / 100  # Convert from percent
    else:
        r = 0.045  # Fallback
    structured["risk_free_rate"] = round(r * 100, 2)

    # Fetch expirations
    print(f"  → Fetching option expirations...")
    all_exps = (prefetched or {}).get("expirations") or fetch_option_expirations(ticker)
    if not all_exps:
        msg = f"⚠ No option expirations found for {ticker}"
        return msg, {"error": msg}

    selected_exps = select_expirations(all_exps)
    lines.append(f"  Expirations analyzed: {', '.join(selected_exps)}")
    lines.append(f"  Risk-free rate: {r*100:.2f}%")
    lines.append("")
    structured["expirations"] = selected_exps

    # Fetch chains per expiration (keep separate for chart, combine for analytics)
    chains_by_expiry = {}  # {exp: (calls_df, puts_df)}
    all_calls = []
    all_puts = []

    for exp in selected_exps:
        print(f"  → Fetching chain for {exp}...")
        calls, puts = fetch_option_chain(ticker, exp)
        if calls.empty and puts.empty:
            continue

        # Compute DTE
        exp_date = date.fromisoformat(exp)
        dte = (exp_date - date.today()).days
        dte_years = max(dte / 365, 1 / 365)  # Min 1 day

        # Compute greeks
        calls = compute_greeks_for_chain(calls, spot, r, dte_years, "call")
        puts = compute_greeks_for_chain(puts, spot, r, dte_years, "put")

        # Tag with expiry
        calls["expiry"] = exp
        calls["dte"] = dte
        puts["expiry"] = exp
        puts["dte"] = dte

        chains_by_expiry[exp] = (calls, puts)
        all_calls.append(calls)
        all_puts.append(puts)

        time.sleep(OPTIONS["chain_fetch_delay"])

    if not all_calls and not all_puts:
        msg = f"⚠ No option chain data available for {ticker}"
        return msg, {"error": msg}

    calls_combined = pd.concat(all_calls, ignore_index=True) if all_calls else pd.DataFrame()
    puts_combined = pd.concat(all_puts, ignore_index=True) if all_puts else pd.DataFrame()

    # ── 1. Put/Call Ratio ──
    lines.append("━" * 60)
    lines.append("  1. PUT/CALL RATIO")
    lines.append("━" * 60)
    pc = compute_put_call_ratio(calls_combined, puts_combined)
    structured["put_call_ratio"] = pc
    lines.append(f"  Volume P/C Ratio:  {pc['volume_ratio']}")
    lines.append(f"  OI P/C Ratio:      {pc['oi_ratio']}")
    lines.append(f"  Call Volume: {pc['call_volume']:,}  |  Put Volume: {pc['put_volume']:,}")
    lines.append(f"  Call OI: {pc['call_oi']:,}  |  Put OI: {pc['put_oi']:,}")
    lines.append(f"  → {pc['interpretation']}")
    lines.append("")

    # ── 2. IV Skew ──
    lines.append("━" * 60)
    lines.append("  2. IMPLIED VOLATILITY SKEW")
    lines.append("━" * 60)
    skew = compute_iv_skew(calls_combined, puts_combined, spot)
    structured["iv_skew"] = skew
    lines.append(f"  Put IV (OI-weighted):  {skew['put_iv_avg']*100:.1f}%")
    lines.append(f"  Call IV (OI-weighted): {skew['call_iv_avg']*100:.1f}%")
    lines.append(f"  Skew (put - call):     {skew['skew']*100:.2f}%")
    lines.append(f"  → {skew['interpretation']}")
    lines.append("")

    # ── 3. Max Pain ──
    lines.append("━" * 60)
    lines.append("  3. MAX PAIN")
    lines.append("━" * 60)
    mp = compute_max_pain(calls_combined, puts_combined)
    structured["max_pain"] = mp
    mp_strike = mp.get("max_pain")
    if mp_strike:
        distance = ((mp_strike - spot) / spot) * 100
        lines.append(f"  Max Pain Strike: ${mp_strike:.2f}")
        lines.append(f"  Spot Distance:   {distance:+.1f}%")
        if distance > 0:
            lines.append(f"  → Price may be pulled UP toward max pain (bullish magnet)")
        elif distance < 0:
            lines.append(f"  → Price may be pulled DOWN toward max pain (bearish magnet)")
        else:
            lines.append(f"  → Spot is AT max pain (neutral)")
    lines.append("")

    # ── 4. Gamma Exposure (GEX) ──
    lines.append("━" * 60)
    lines.append("  4. GAMMA EXPOSURE (GEX)")
    lines.append("━" * 60)
    gex = compute_gex(calls_combined, puts_combined, spot)
    structured["gex"] = {k: v for k, v in gex.items() if k != "gex_by_strike"}
    lines.append(f"  Total GEX: ${gex['total_gex']:,.0f}")
    if gex.get("flip_strike"):
        lines.append(f"  GEX Flip Strike: ${gex['flip_strike']:.2f}")
    lines.append(f"  Top GEX Strikes:")
    for strike, gex_val in gex.get("top_strikes", []):
        lines.append(f"    ${strike:>10.2f}  →  ${gex_val:>14,.0f}")
    lines.append(f"  → {gex['interpretation']}")
    lines.append("")

    # ── 5. Delta Exposure (DEX) ──
    lines.append("━" * 60)
    lines.append("  5. DELTA EXPOSURE (DEX)")
    lines.append("━" * 60)
    dex = compute_dex(calls_combined, puts_combined, spot)
    structured["dex"] = {"total_dex": dex["total_dex"]}
    lines.append(f"  Total DEX: {dex['total_dex']:,.0f} shares")
    if dex["total_dex"] > 0:
        lines.append(f"  → Net LONG delta — dealers hedging by buying shares (supportive)")
    else:
        lines.append(f"  → Net SHORT delta — dealers hedging by selling shares (pressure)")
    lines.append("")

    # ── 6. OI Walls ──
    lines.append("━" * 60)
    lines.append("  6. OPEN INTEREST WALLS")
    lines.append("━" * 60)
    walls = find_oi_walls(calls_combined, puts_combined)
    structured["oi_walls"] = walls
    lines.append("  Call Walls (Resistance):")
    for strike, oi in walls["call_walls"]:
        marker = " ◄ NEAREST" if strike > spot and not any(s < strike and s > spot for s, _ in walls["call_walls"]) else ""
        lines.append(f"    ${strike:>10.2f}  →  {oi:>10,} OI{marker}")
    lines.append("  Put Walls (Support):")
    for strike, oi in walls["put_walls"]:
        marker = " ◄ NEAREST" if strike < spot and not any(s > strike and s < spot for s, _ in walls["put_walls"]) else ""
        lines.append(f"    ${strike:>10.2f}  →  {oi:>10,} OI{marker}")
    lines.append("")

    # ── 7. Options Sentiment Score ──
    lines.append("━" * 60)
    lines.append("  7. OPTIONS SENTIMENT SCORE")
    lines.append("━" * 60)
    sentiment = compute_options_sentiment(pc, skew, gex, mp, spot)
    structured["options_sentiment"] = sentiment
    lines.append(f"  Composite Score: {sentiment['score']}/100 — {sentiment['label']}")
    comps = sentiment.get("components", {})
    if comps.get("pc_ratio_score") is not None:
        lines.append(f"    P/C Ratio:     {comps['pc_ratio_score']:.0f}/100")
    if comps.get("iv_skew_score") is not None:
        lines.append(f"    IV Skew:       {comps['iv_skew_score']:.0f}/100")
    if comps.get("gex_score") is not None:
        lines.append(f"    GEX:           {comps['gex_score']:.0f}/100")
    if comps.get("max_pain_score") is not None:
        lines.append(f"    Max Pain:      {comps['max_pain_score']:.0f}/100")
    lines.append("")

    # ── 8. Key Levels Summary ──
    lines.append("━" * 60)
    lines.append("  8. KEY LEVELS SUMMARY")
    lines.append("━" * 60)
    key_levels = {}
    if walls["put_walls"]:
        nearest_support = max((s for s, _ in walls["put_walls"] if s < spot), default=None)
        if nearest_support:
            key_levels["support"] = nearest_support
            lines.append(f"  Support (put wall):     ${nearest_support:.2f}")
    if walls["call_walls"]:
        nearest_resistance = min((s for s, _ in walls["call_walls"] if s > spot), default=None)
        if nearest_resistance:
            key_levels["resistance"] = nearest_resistance
            lines.append(f"  Resistance (call wall): ${nearest_resistance:.2f}")
    if mp_strike:
        key_levels["max_pain"] = mp_strike
        lines.append(f"  Max Pain:               ${mp_strike:.2f}")
    if gex.get("flip_strike"):
        key_levels["gex_flip"] = gex["flip_strike"]
        lines.append(f"  GEX Flip:               ${gex['flip_strike']:.2f}")
    structured["key_levels"] = key_levels
    lines.append("")

    # ── 9. Cross-Verification ──
    if verify_polygon and POLYGON_API_KEY:
        lines.append("━" * 60)
        lines.append("  9. CROSS-VERIFICATION (Polygon)")
        lines.append("━" * 60)
        verify_notes = cross_verify_with_polygon(ticker, calls_combined, puts_combined)
        structured["cross_verification"] = verify_notes
        for note in verify_notes:
            lines.append(f"  {note}")
        lines.append("")

    # ── Chart ──
    chart_path = None
    if include_chart:
        chart_path = generate_options_chart(ticker, spot, chains_by_expiry, mp)
        if chart_path:
            structured["chart_path"] = chart_path
            lines.append(f"  📊 Interactive chart: {chart_path}")
            lines.append("")

    lines.append(f"Generated at {now.strftime('%H:%M:%S')} local time")
    lines.append(f"{'━'*60}")

    # Build key signals string for Notion
    signals = []
    signals.append(f"P/C={pc.get('volume_ratio', 'N/A')}")
    signals.append(f"Skew={skew.get('skew', 0)*100:+.1f}%")
    signals.append(f"GEX={'+'if gex['total_gex']>0 else ''}{gex['total_gex']:,.0f}")
    if mp_strike:
        signals.append(f"MaxPain=${mp_strike:.0f}")
    signals.append(f"Sentiment={sentiment['score']:.0f}/100 {sentiment['label']}")
    structured["key_signals"] = " | ".join(signals)

    return "\n".join(lines), structured


def analyze_watchlist_options(tickers: list[str] | None = None) -> tuple[str, dict]:
    """Run options analysis for multiple tickers (batch mode).

    Args:
        tickers: List of tickers. If None, uses top equity tickers from watchlist.

    Returns:
        Tuple of (combined_report_text, combined_structured_data).
    """
    if tickers is None:
        # Use equity tickers from watchlist (skip crypto)
        tickers = [t for t in WATCHLIST_CONFIG if t != "BTCUSD"][:5]

    now = datetime.now()
    all_lines = []
    all_structured = {"date": now.strftime("%Y-%m-%d"), "type": "Options Analysis (Batch)", "tickers": {}}

    all_lines.append(f"╔{'═'*58}╗")
    all_lines.append(f"║  📊 OPTIONS WATCHLIST SCAN — {now.strftime('%Y-%m-%d')}{'':>17}║")
    all_lines.append(f"╚{'═'*58}╝")
    all_lines.append("")

    # Summary table header
    all_lines.append(f"  {'Ticker':<8} {'P/C':>6} {'Skew':>8} {'GEX':>12} {'MaxPain':>10} {'Score':>8} {'Signal':<16}")
    all_lines.append(f"  {'─'*8} {'─'*6} {'─'*8} {'─'*12} {'─'*10} {'─'*8} {'─'*16}")

    for ticker in tickers:
        print(f"\n{'='*40}")
        print(f"  Analyzing {ticker}...")
        print(f"{'='*40}")
        try:
            report, data = analyze_options(ticker, include_chart=False, verify_polygon=False)
            all_structured["tickers"][ticker] = data

            # Add summary row
            pc = data.get("put_call_ratio", {}).get("volume_ratio", "N/A")
            skew_val = data.get("iv_skew", {}).get("skew", 0)
            gex_val = data.get("gex", {}).get("total_gex", 0)
            mp_val = data.get("max_pain", {}).get("max_pain", 0)
            score = data.get("options_sentiment", {}).get("score", 50)
            label = data.get("options_sentiment", {}).get("label", "N/A")

            pc_str = f"{pc}" if pc != "N/A" else "N/A"
            all_lines.append(
                f"  {ticker:<8} {pc_str:>6} {skew_val*100:>+7.1f}% "
                f"${gex_val:>10,.0f} ${mp_val:>9.0f} "
                f"{score:>6.0f}/100 {label:<16}"
            )
        except Exception as e:
            print(f"⚠ Error analyzing {ticker}: {e}")
            all_lines.append(f"  {ticker:<8} {'ERROR':>6}")
            all_structured["tickers"][ticker] = {"error": str(e)}

    all_lines.append("")
    all_lines.append(f"{'━'*60}")
    all_lines.append("")

    # Append individual reports
    for ticker in tickers:
        data = all_structured["tickers"].get(ticker, {})
        if "error" not in data:
            report, _ = analyze_options(ticker, include_chart=True, verify_polygon=False)
            all_lines.append(report)
            all_lines.append("")

    return "\n".join(all_lines), all_structured


# ── CLI Entry Point ────────────────────────────────────────────────────

if __name__ == "__main__":
    ticker = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else None
    json_mode = "--json" in sys.argv

    if ticker:
        report, structured = analyze_options(ticker.upper())
    else:
        report, structured = analyze_watchlist_options()

    if json_mode:
        # Remove non-serializable items
        print(json.dumps(structured, indent=2, default=str))
    else:
        print(report)
