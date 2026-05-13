"""Macro Liquidity Monitor — the article's core risk engine.

Implements the 4-indicator trigger system:
- Net Liquidity = Fed Assets - TGA - ON RRP (weekly drop >5% → warning)
- SOFR (>5.5% → reduce positions)
- MOVE Index (>130 → stop loss, >100 → warning)
- USDJPY + US2Y-JP2Y spread (yen carry trade unwind risk)

Output: Risk level (GREEN / YELLOW / RED) with detailed breakdown.
"""
from data_sources import fetch_all_macro, fetch_net_liquidity_history
from config import TRIGGERS, SENTIMENT


def assess_liquidity_risk(data: dict) -> dict:
    """Assess macro liquidity risk level from fetched data."""
    alerts = []
    warnings = []
    score = 0  # 0 = safe, higher = more risk

    liq = data.get("liquidity", {})

    # 1. SOFR check
    sofr = liq.get("sofr")
    if sofr is not None:
        if sofr > TRIGGERS["sofr_reduce_threshold"]:
            alerts.append(f"🔴 SOFR at {sofr:.2f}% — above {TRIGGERS['sofr_reduce_threshold']}% threshold → REDUCE POSITIONS")
            score += 3
        elif sofr > TRIGGERS["sofr_reduce_threshold"] - 0.5:
            warnings.append(f"🟡 SOFR at {sofr:.2f}% — approaching reduction threshold")
            score += 1

    # 2. Net liquidity trend
    net_liq = liq.get("net_liquidity")
    if net_liq is not None:
        # Get historical for trend
        hist = fetch_net_liquidity_history(days=14)
        if not hist.empty and len(hist) >= 7:
            week_ago = hist["net_liquidity"].iloc[-7] if len(hist) >= 7 else hist["net_liquidity"].iloc[0]
            current = hist["net_liquidity"].iloc[-1]
            if week_ago != 0:
                weekly_change_pct = ((current - week_ago) / abs(week_ago)) * 100
                if weekly_change_pct < -TRIGGERS["net_liquidity_weekly_drop_pct"]:
                    alerts.append(f"🔴 Net liquidity dropped {weekly_change_pct:.1f}% this week → WARNING")
                    score += 3
                elif weekly_change_pct < -2:
                    warnings.append(f"🟡 Net liquidity fell {weekly_change_pct:.1f}% this week")
                    score += 1
                else:
                    warnings.append(f"🟢 Net liquidity {weekly_change_pct:+.1f}% this week")

    # 3. MOVE index (bond volatility)
    move = data.get("move")
    if move:
        if move["current"] > TRIGGERS["move_stop_loss"]:
            alerts.append(f"🔴 MOVE at {move['current']:.1f} — above {TRIGGERS['move_stop_loss']} → STOP LOSS")
            score += 3
        elif move["current"] > TRIGGERS["move_warning"]:
            alerts.append(f"🟡 MOVE at {move['current']:.1f} — above {TRIGGERS['move_warning']} → ELEVATED BOND VOLATILITY")
            score += 2
        else:
            warnings.append(f"🟢 MOVE at {move['current']:.1f} — bond volatility contained")

    # 4. USDJPY / Yen carry trade risk
    usdjpy = data.get("usdjpy")
    if usdjpy:
        if usdjpy.get("week_change_pct", 0) < -2:
            alerts.append(f"🔴 USDJPY dropped {usdjpy['week_change_pct']:.1f}% this week — yen carry unwind risk")
            score += 2
        elif usdjpy.get("week_change_pct", 0) < -1:
            warnings.append(f"🟡 USDJPY slid {usdjpy['week_change_pct']:.1f}% — monitoring yen strength")
            score += 1

    # 4. Yield curve
    yields = data.get("yields", {})
    spread = yields.get("spread_2s10s")
    if spread is not None:
        if spread < 0:
            warnings.append(f"🟡 Yield curve inverted ({spread:.3f}%) — recession signal")
            score += 1
        elif spread < 0.2:
            warnings.append(f"🟡 Yield curve very flat ({spread:.3f}%)")

    # 5. Fear & Greed
    fg = data.get("fear_greed")
    if fg:
        if fg["score"] > SENTIMENT["fear_greed_extreme_greed"]:
            warnings.append(f"🟡 Fear & Greed at {fg['score']} ({fg['rating']}) — EXTREME GREED")
            score += 1
        elif fg["score"] < SENTIMENT["fear_greed_extreme_fear"]:
            warnings.append(f"🟢 Fear & Greed at {fg['score']} ({fg['rating']}) — EXTREME FEAR (contrarian buy)")

    # Determine overall risk level
    if score >= 5:
        risk_level = "RED"
        action = "REDUCE POSITIONS / HEDGE"
    elif score >= 3:
        risk_level = "YELLOW"
        action = "CAUTION — tighten stops, reduce new entries"
    else:
        risk_level = "GREEN"
        action = "NORMAL — proceed with strategy"

    return {
        "risk_level": risk_level,
        "score": score,
        "action": action,
        "alerts": alerts,
        "warnings": warnings,
        "data": data,
    }


def format_risk_report(result: dict) -> str:
    """Format the risk assessment into a readable report."""
    lines = []
    risk = result["risk_level"]
    emoji = {"RED": "🔴", "YELLOW": "🟡", "GREEN": "🟢"}[risk]

    lines.append(f"{'='*60}")
    lines.append(f"  {emoji} MACRO RISK LEVEL: {risk} (score: {result['score']})")
    lines.append(f"  ACTION: {result['action']}")
    lines.append(f"{'='*60}")
    lines.append("")

    # Key metrics
    data = result["data"]
    liq = data.get("liquidity", {})
    lines.append("📊 KEY METRICS")
    lines.append(f"  Net Liquidity:  {_fmt_trillions(liq.get('net_liquidity'))}")
    lines.append(f"  Fed Assets:     {_fmt_trillions(liq.get('fed_assets'))}")
    lines.append(f"  TGA Balance:    {_fmt_trillions(liq.get('tga_balance'))}")
    lines.append(f"  Reverse Repo:   {_fmt_trillions(liq.get('rrp'))}")
    lines.append(f"  SOFR:           {_fmt_pct(liq.get('sofr'))}")
    lines.append("")

    yd = data.get("yields", {})
    lines.append("📈 YIELDS")
    lines.append(f"  US 2Y:          {_fmt_pct(yd.get('us2y'))}")
    lines.append(f"  US 10Y:         {_fmt_pct(yd.get('us10y'))}")
    lines.append(f"  2s10s Spread:   {_fmt_pct(yd.get('spread_2s10s'))}")
    lines.append("")

    move = data.get("move")
    if move:
        lines.append(f"📊 MOVE Index:    {move['current']} ({move['week_change_pct']:+.1f}% 1w)")

    usdjpy = data.get("usdjpy")
    if usdjpy:
        lines.append(f"💱 USDJPY:        {usdjpy['current']} ({usdjpy['week_change_pct']:+.2f}% 1w)")

    sp = data.get("sp500")
    if sp:
        lines.append(f"📉 S&P 500 (SPY): ${sp['current']} ({sp['week_change_pct']:+.2f}% 1w)")

    fg = data.get("fear_greed")
    if fg:
        lines.append(f"😱 Fear & Greed:  {fg['score']} ({fg['rating']})")
    lines.append("")

    # Alerts
    if result["alerts"]:
        lines.append("⚠️  ALERTS")
        for a in result["alerts"]:
            lines.append(f"  {a}")
        lines.append("")

    if result["warnings"]:
        lines.append("📋 NOTES")
        for w in result["warnings"]:
            lines.append(f"  {w}")
        lines.append("")

    lines.append(f"{'='*60}")
    return "\n".join(lines)


def _fmt_trillions(val):
    if val is None:
        return "N/A"
    if abs(val) >= 1_000_000:
        return f"${val/1_000_000:.2f}T"
    elif abs(val) >= 1_000:
        return f"${val/1_000:.1f}B"
    return f"${val:.1f}M"


def _fmt_pct(val):
    if val is None:
        return "N/A"
    return f"{val:.3f}%"


def run_monitor() -> tuple[str, dict]:
    """Full monitor run: fetch data → assess → format report.

    Returns:
        Tuple of (report_text, structured_data) for Notion sync.
    """
    from datetime import datetime as _dt
    data = fetch_all_macro()
    result = assess_liquidity_risk(data)
    report = format_risk_report(result)

    structured = {
        "date": _dt.now().strftime("%Y-%m-%d"),
        "type": "Macro Monitor",
        "risk_level": result["risk_level"],
        "risk_score": result["score"],
        "risk_action": result["action"],
        "alerts": result["alerts"],
        "warnings": result["warnings"],
        "key_signals": "; ".join(result["alerts"]) if result["alerts"] else "No alerts",
    }
    return report, structured


if __name__ == "__main__":
    import sys
    import json as _json

    report, structured = run_monitor()

    if "--json" in sys.argv:
        print(_json.dumps(structured, indent=2, default=str))
    else:
        print(report)
