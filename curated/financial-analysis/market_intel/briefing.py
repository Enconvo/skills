"""Daily Market Briefing Generator.

Chains: macro risk → FOMC → geopolitical → sentiment → TA → action items.
Designed to be run every morning or on-demand via /daily-briefing skill.
Reuses data across sections to avoid duplicate API calls.

v2 (2026-03-21): Added FOMC context, geopolitical scanner, economic calendar,
data audit layer. All data verified against primary sources.
"""
import logging
from datetime import datetime, date
from data_sources import fetch_all_macro, fetch_watchlist_ta, fetch_watchlist_fundamentals, WATCHLIST_CONFIG
from macro_monitor import assess_liquidity_risk, format_risk_report
from sentiment_scanner import run_sentiment_scan

logger = logging.getLogger(__name__)


def generate_briefing(watchlist: dict | None = None) -> tuple[str, dict]:
    """Generate a complete daily market briefing.

    Chains macro monitor + sentiment scanner + TA + fundamentals into one report.
    Passes shared data between sections to avoid re-fetching.

    Args:
        watchlist: Optional dict of {symbol: (exchange, screener)} pairs.
                   If None, uses WATCHLIST_CONFIG default.

    Returns:
        Tuple of (report_text, structured_data) for Notion sync.
    """
    if watchlist is None:
        watchlist = WATCHLIST_CONFIG

    now = datetime.now()
    structured = {"date": now.strftime("%Y-%m-%d"), "type": "Daily Briefing"}
    lines = []
    lines.append(f"╔{'═'*58}╗")
    lines.append(f"║  📰 DAILY MARKET BRIEFING — {now.strftime('%A, %B %d, %Y')}  ║")
    lines.append(f"╚{'═'*58}╝")
    lines.append("")

    # ── Section 1: Macro Risk Assessment ──
    lines.append("━" * 60)
    lines.append("  SECTION 1: MACRO RISK ASSESSMENT")
    lines.append("━" * 60)
    macro_data = {}
    risk = {"risk_level": "UNKNOWN", "score": 0, "action": "Data unavailable", "alerts": [], "warnings": []}
    try:
        macro_data = fetch_all_macro()
        risk = assess_liquidity_risk(macro_data)
        structured["risk_level"] = risk["risk_level"]
        structured["risk_score"] = risk["score"]
        structured["risk_action"] = risk["action"]
        structured["alerts"] = risk["alerts"]
        structured["warnings"] = risk["warnings"]
        structured["macro_data"] = {
            k: v for k, v in macro_data.items()
            if k in ("fear_greed", "usdjpy", "sp500", "move")
        }
        lines.append(format_risk_report(risk))
    except Exception as e:
        logger.error("Section 1 (Macro Risk) failed: %s", e)
        lines.append("  ⚠ Macro risk assessment unavailable")
        structured["risk_level"] = "UNKNOWN"
    lines.append("")

    # ── Section 1.5: FOMC & Rate Context ──
    lines.append("━" * 60)
    lines.append("  SECTION 1.5: FOMC & RATE CONTEXT")
    lines.append("━" * 60)
    fomc_ctx = {}
    try:
        from fomc_tracker import get_fomc_context, format_fomc_report
        fomc_ctx = get_fomc_context()
        structured["fomc"] = {
            "current_rate": fomc_ctx.get("current_rate"),
            "rate_source": fomc_ctx.get("rate_source"),
            "bias": fomc_ctx.get("current_bias"),
            "next_meeting": fomc_ctx.get("next_meeting", {}).get("date"),
            "next_meeting_days": fomc_ctx.get("next_meeting", {}).get("days_until"),
            "fred_verified": fomc_ctx.get("fred_verified"),
            "total_cuts": fomc_ctx.get("total_cuts"),
            "total_holds": fomc_ctx.get("total_holds"),
        }
        lines.append(format_fomc_report('en'))
        
        # Verification status
        if fomc_ctx.get("fred_verified"):
            lines.append(f"  ✅ Rate verified against FRED API (source: {fomc_ctx.get('rate_source', '?')})")
        elif fomc_ctx.get("fred_discrepancies"):
            lines.append(f"  ⚠️ FRED discrepancies found: {len(fomc_ctx['fred_discrepancies'])}")
            for d in fomc_ctx["fred_discrepancies"][:2]:
                lines.append(f"     {d['date']}: {d['issue']}")
    except Exception as e:
        logger.error("Section 1.5 (FOMC) failed: %s", e)
        lines.append("  ⚠ FOMC context unavailable")
    lines.append("")

    # ── Section 1.6: Geopolitical & News Risk ──
    lines.append("━" * 60)
    lines.append("  SECTION 1.6: GEOPOLITICAL & NEWS RISK")
    lines.append("━" * 60)
    geo_data = {}
    try:
        from geopolitical_scanner import scan_geopolitical_news
        geo_data = scan_geopolitical_news()
        structured["geopolitical"] = {
            "headline_count": geo_data.get("headline_count", 0),
            "hotspots": [{"id": h["hotspot"], "impact": h["impact"], 
                         "headline_count": len(h["headlines"])} 
                        for h in geo_data.get("hotspot_alerts", [])],
        }
        
        hotspots = geo_data.get("hotspot_alerts", [])
        if hotspots:
            # Determine overall risk
            if any(h["impact"] == "CRITICAL" for h in hotspots):
                lines.append("  🔴 GEOPOLITICAL RISK: ELEVATED")
            elif any(h["impact"] == "HIGH" for h in hotspots):
                lines.append("  🟡 GEOPOLITICAL RISK: HEIGHTENED")
            else:
                lines.append("  🟢 GEOPOLITICAL RISK: MODERATE")
            lines.append("")
            
            for hs in hotspots[:4]:
                impact_icon = "🔴" if hs["impact"] == "CRITICAL" else "🟡" if hs["impact"] == "HIGH" else "⚪"
                lines.append(f"  {impact_icon} [{hs['impact']}] {hs['hotspot'].upper()} — {len(hs['headlines'])} headlines")
                lines.append(f"     {hs['context_en']}")
                for h in hs["headlines"][:2]:
                    lines.append(f"     • {h}")
                lines.append("")
        else:
            lines.append("  🟢 No significant geopolitical hotspots detected")
        
        # Top headlines
        top = geo_data.get("top_headlines", [])[:5]
        if top:
            lines.append(f"  📰 TOP HEADLINES ({geo_data.get('headline_count', 0)} relevant):")
            for h in top:
                icon = "🔴" if h["impact"] in ("CRITICAL", "HIGH") else "🟡"
                lines.append(f"     {icon} {h['title'][:80]}")
                if h.get("hotspots"):
                    lines.append(f"        Tags: {', '.join(h['hotspots'])}")
    except Exception as e:
        logger.error("Section 1.6 (Geopolitical) failed: %s", e)
        lines.append("  ⚠ Geopolitical scan unavailable")
    lines.append("")

    # ── Section 1.7: Economic Calendar ──
    lines.append("━" * 60)
    lines.append("  SECTION 1.7: ECONOMIC CALENDAR (NEXT 10 DAYS)")
    lines.append("━" * 60)
    try:
        from econ_calendar import get_upcoming_events
        events = get_upcoming_events(days_ahead=10)
        structured["upcoming_events"] = [{"date": e["date"], "event": e["event"], "impact": e["impact"]} for e in events[:10]]
        
        if events:
            for e in events[:10]:
                icon = "🔴" if e["impact"] == "high" else "🟡" if e["impact"] == "medium" else "⚪"
                d = datetime.strptime(e["date"], "%Y-%m-%d").strftime("%b %d (%a)")
                lines.append(f"  {icon} {d} — {e['event']}")
                if e.get("note"):
                    lines.append(f"     ⚠️ {e['note']}")
        else:
            lines.append("  No major events in the next 10 days")
    except Exception as e:
        logger.error("Section 1.7 (Calendar) failed: %s", e)
        lines.append("  ⚠ Economic calendar unavailable")
    lines.append("")

    # ── Section 2: Watchlist Technical Analysis (TradingView) ──
    lines.append("━" * 60)
    lines.append("  SECTION 2: WATCHLIST — TRADINGVIEW TECHNICAL ANALYSIS")
    lines.append("━" * 60)

    strong_buys = []
    strong_sells = []
    oversold = []
    overbought = []
    tv_data = {}

    try:
        logger.info("TradingView: Fetching watchlist TA...")
        tv_data = fetch_watchlist_ta(watchlist)

        lines.append(f"  {'Ticker':<8} {'Signal':<14} {'Close':>10} {'RSI':>6} {'ADX':>6} {'vs200':>8}")
        lines.append(f"  {'─'*8} {'─'*14} {'─'*10} {'─'*6} {'─'*6} {'─'*8}")

        for symbol, ta in tv_data.items():
            if ta is None:
                lines.append(f"  {symbol:<8} {'N/A':<14}")
                continue

            rec = ta["recommendation"]
            close = ta["close"]
            rsi = ta["rsi"]
            adx = ta["adx"]
            vs200 = ta.get("vs_sma200_pct")
            vs200_str = f"{vs200:+.1f}%" if vs200 is not None else "N/A"

            lines.append(f"  {symbol:<8} {rec:<14} {close:>10.2f} {rsi:>6.1f} {adx:>6.1f} {vs200_str:>8}")

            if rec == "STRONG_BUY":
                strong_buys.append(symbol)
            elif rec in ("STRONG_SELL", "SELL"):
                strong_sells.append(symbol)
            if rsi < 30:
                oversold.append((symbol, rsi))
            elif rsi > 70:
                overbought.append((symbol, rsi))
    except Exception as e:
        logger.error("Section 2 (TA) failed: %s", e)
        lines.append("  ⚠ Technical analysis unavailable")

    lines.append("")

    # ── Section 3: Analyst Consensus & Upcoming Earnings ──
    lines.append("━" * 60)
    lines.append("  SECTION 3: ANALYST CONSENSUS & EARNINGS")
    lines.append("━" * 60)

    fundamentals = {}
    upcoming_earnings = []

    try:
        logger.info("Yahoo Finance: Analyst targets & earnings...")
        fundamentals = fetch_watchlist_fundamentals()
        structured["fundamentals"] = fundamentals

        lines.append(f"  {'Ticker':<8} {'Rec':<12} {'Price':>8} {'Target':>8} {'Upside':>8} {'Earnings':>12}")
        lines.append(f"  {'─'*8} {'─'*12} {'─'*8} {'─'*8} {'─'*8} {'─'*12}")

        for sym, fd in fundamentals.items():
            if fd is None:
                lines.append(f"  {sym:<8} {'N/A':<12}")
                continue
            price = fd.get("price") or 0
            target = fd.get("target_mean") or 0
            rec = (fd.get("recommendation") or "N/A").replace("_", " ")
            upside = f"{((target / price) - 1) * 100:+.0f}%" if price and target else "N/A"
            ed = fd.get("earnings_date") or "N/A"
            lines.append(f"  {sym:<8} {rec:<12} ${price:>7.2f} ${target:>7.2f} {upside:>8} {ed:>12}")

            if fd.get("earnings_date"):
                try:
                    ed_date = date.fromisoformat(fd["earnings_date"])
                    days_until = (ed_date - date.today()).days
                    if 0 <= days_until <= 7:
                        eps_est = fd.get("eps_estimate")
                        upcoming_earnings.append((sym, days_until, eps_est))
                except (ValueError, TypeError):
                    pass

        if upcoming_earnings:
            lines.append("")
            lines.append("  ⏰ EARNINGS THIS WEEK:")
            for sym, days, eps in upcoming_earnings:
                day_str = "TODAY" if days == 0 else f"in {days}d"
                eps_str = f" (EPS est: ${eps:.2f})" if eps else ""
                lines.append(f"     • {sym} — {day_str}{eps_str}")
    except Exception as e:
        logger.error("Section 3 (Fundamentals) failed: %s", e)
        lines.append("  ⚠ Analyst consensus unavailable")

    lines.append("")

    # ── Section 4: Sentiment Scan (chained — reuses macro + TA data) ──
    lines.append("━" * 60)
    lines.append("  SECTION 4: MARKET SENTIMENT")
    lines.append("━" * 60)

    sentiment_data = {}
    try:
        sentiment_report, sentiment_data = run_sentiment_scan(prefetched={
            "fear_greed": macro_data.get("fear_greed"),
            "move": macro_data.get("move"),
            "tv_data": tv_data,
        })
        structured["sentiment_score"] = sentiment_data.get("sentiment_score")
        structured["sentiment_label"] = sentiment_data.get("sentiment_label")
        structured["sentiment_components"] = sentiment_data.get("components")

        # Extract the key parts from the sentiment report (skip the header/footer)
        in_content = False
        for sline in sentiment_report.split("\n"):
            if "COMPOSITE SENTIMENT" in sline:
                in_content = True
            if in_content:
                if "Generated at" in sline:
                    break
                lines.append(sline)
    except Exception as e:
        logger.error("Section 4 (Sentiment) failed: %s", e)
        lines.append("  ⚠ Sentiment scan unavailable")

    lines.append("")

    # ── Section 4.5: Options Overlay (top 3 tickers) ──
    try:
        from options_analyzer import analyze_options
        lines.append("━" * 60)
        lines.append("  SECTION 4.5: OPTIONS OVERLAY")
        lines.append("━" * 60)
        logger.info("Options: Analyzing top tickers...")
        # Analyze top 3 equity tickers
        options_tickers = [t for t in watchlist if t != "BTCUSD"][:3]
        options_results = {}
        for opt_ticker in options_tickers:
            try:
                _, opt_data = analyze_options(opt_ticker, include_chart=False, verify_polygon=False)
                options_results[opt_ticker] = opt_data
            except Exception as e:
                logger.warning("Options error for %s: %s", opt_ticker, e)

        if options_results:
            lines.append(f"  {'Ticker':<8} {'P/C':>6} {'Skew':>8} {'GEX':>12} {'MaxPain':>10} {'Score':>8}")
            lines.append(f"  {'─'*8} {'─'*6} {'─'*8} {'─'*12} {'─'*10} {'─'*8}")
            for sym, od in options_results.items():
                pc = od.get("put_call_ratio", {}).get("volume_ratio", "N/A")
                skew_val = od.get("iv_skew", {}).get("skew", 0)
                gex_val = od.get("gex", {}).get("total_gex", 0)
                mp_val = od.get("max_pain", {}).get("max_pain", 0)
                score = od.get("options_sentiment", {}).get("score", 50)
                lines.append(
                    f"  {sym:<8} {pc!s:>6} {skew_val*100:>+7.1f}% "
                    f"${gex_val:>10,.0f} ${mp_val:>9.0f} {score:>6.0f}/100"
                )
            structured["options_overlay"] = options_results
        else:
            lines.append("  ⚠ Options data unavailable")
        lines.append("")
    except ImportError:
        pass  # options_analyzer not available — skip gracefully
    except Exception as e:
        logger.error("Options overlay error: %s", e)

    # ── Section 4.75: FCN Portfolio Check ──
    try:
        from fcn_checker import check_fcn_portfolio
        lines.append("━" * 60)
        lines.append("  SECTION 4.75: FCN PORTFOLIO CHECK")
        lines.append("━" * 60)
        logger.info("FCN: Checking portfolio positions...")
        fcn_report, fcn_data = check_fcn_portfolio()
        structured["fcn_check"] = fcn_data
        # Extract summary lines (skip the header box)
        in_content = False
        for fline in fcn_report.split("\n"):
            if fline.strip().startswith(("🔴", "🟡", "🟢", "⚫")):
                in_content = True
            if "PORTFOLIO SUMMARY" in fline:
                in_content = True
            if in_content:
                lines.append(fline)
        lines.append("")
    except ImportError:
        pass
    except Exception as e:
        logger.error("FCN check error: %s", e)

    # ── Section 5: Key Signals & Action Items ──
    lines.append("━" * 60)
    lines.append("  SECTION 5: KEY SIGNALS & ACTION ITEMS")
    lines.append("━" * 60)

    # Macro risk signals
    risk_level = risk["risk_level"]
    if risk_level == "RED":
        lines.append("  🔴 MACRO RISK ELEVATED:")
        lines.append("     • Reduce position sizes")
        lines.append("     • Tighten stop losses")
        lines.append("     • Increase cash allocation")
        lines.append("     • Consider hedges (VIX calls, put spreads)")
    elif risk_level == "YELLOW":
        lines.append("  🟡 MACRO CAUTION:")
        lines.append("     • No new large positions")
        lines.append("     • Review stop losses")
        lines.append("     • Monitor key levels closely")
    else:
        lines.append("  🟢 MACRO CONDITIONS NORMAL")
    lines.append("")

    # FOMC proximity warning
    nm = fomc_ctx.get("next_meeting", {})
    if nm and nm.get("days_until", 999) <= 14:
        lines.append(f"  🏛️ FOMC IN {nm['days_until']} DAYS ({nm['date']})")
        if nm.get("has_dot_plot"):
            lines.append("     ⚠️ SEP + Dot Plot meeting — expect elevated volatility")
        lines.append("     • Reduce pre-meeting position sizing")
        lines.append("     • Watch Fed funds futures for rate expectations shift")

    # Geopolitical risk signals
    geo_hotspots = geo_data.get("hotspot_alerts", [])
    critical_geo = [h for h in geo_hotspots if h["impact"] == "CRITICAL"]
    if critical_geo:
        lines.append("")
        lines.append("  🌍 CRITICAL GEOPOLITICAL RISK:")
        for h in critical_geo:
            lines.append(f"     ⚠️ {h['hotspot'].upper()}: {h['context_en']}")
            assets = ", ".join(h.get("assets", []))
            lines.append(f"     Affected assets: {assets}")
            lines.append("     • Monitor for supply disruption headlines")
            lines.append("     • Consider hedges on affected commodities")

    lines.append("")

    # Technical signals
    if strong_buys:
        lines.append(f"  📈 STRONG BUY signals: {', '.join(strong_buys)}")
    if strong_sells:
        lines.append(f"  📉 SELL signals: {', '.join(strong_sells)}")
    if oversold:
        lines.append(f"  🔵 OVERSOLD (RSI<30): {', '.join(f'{s} ({r:.0f})' for s, r in oversold)}")
    if overbought:
        lines.append(f"  🔴 OVERBOUGHT (RSI>70): {', '.join(f'{s} ({r:.0f})' for s, r in overbought)}")

    # Sentiment contrarian signals
    contrarian = sentiment_data.get("contrarian_signals", [])
    if contrarian:
        lines.append("")
        lines.append("  💡 CONTRARIAN SIGNALS:")
        for sig in contrarian:
            lines.append(f"     {sig}")

    # Earnings alerts
    if upcoming_earnings:
        lines.append("")
        lines.append("  ⏰ EARNINGS WATCH:")
        for sym, days, eps in upcoming_earnings:
            day_str = "TODAY" if days == 0 else f"in {days}d"
            lines.append(f"     • {sym} reports {day_str}")

    lines.append("")

    # Build key signals summary for Notion
    key_signals = []
    if risk_level == "RED":
        key_signals.append("MACRO RISK ELEVATED")
    elif risk_level == "YELLOW":
        key_signals.append("MACRO CAUTION")
    if strong_buys:
        key_signals.append(f"Strong buys: {', '.join(strong_buys)}")
    if strong_sells:
        key_signals.append(f"Sell signals: {', '.join(strong_sells)}")
    if oversold:
        key_signals.append(f"Oversold: {', '.join(s for s, _ in oversold)}")
    if overbought:
        key_signals.append(f"Overbought: {', '.join(s for s, _ in overbought)}")
    sl = sentiment_data.get("sentiment_label", "")
    if sl in ("EXTREME GREED", "EXTREME FEAR"):
        key_signals.append(f"Sentiment: {sl}")
    # Geopolitical alerts
    if critical_geo:
        key_signals.append(f"GEO CRITICAL: {', '.join(h['hotspot'].upper() for h in critical_geo)}")
    # FOMC proximity
    if nm and nm.get("days_until", 999) <= 14:
        key_signals.append(f"FOMC in {nm['days_until']}d")
    # FCN alerts
    fcn = structured.get("fcn_check", {})
    if fcn.get("danger_count"):
        key_signals.append(f"FCN DANGER: {fcn['danger_count']} note(s) ${fcn['danger_exposure']:,.0f}")
        lines.append(f"  🔴 FCN DANGER: {fcn['danger_count']} note(s) below strike (${fcn['danger_exposure']:,.0f})")
    if fcn.get("warning_count"):
        key_signals.append(f"FCN WARNING: {fcn['warning_count']} note(s)")
        lines.append(f"  🟡 FCN WARNING: {fcn['warning_count']} note(s) close to strike (${fcn['warning_exposure']:,.0f})")
    if upcoming_earnings:
        key_signals.append(f"Earnings: {', '.join(s for s, _, _ in upcoming_earnings)}")
    structured["key_signals"] = "; ".join(key_signals) if key_signals else "No extreme signals"
    structured["strong_buys"] = strong_buys
    structured["strong_sells"] = strong_sells

    # ── Data Audit Summary ──
    lines.append("")
    lines.append("━" * 60)
    lines.append("  DATA RELIABILITY AUDIT")
    lines.append("━" * 60)
    try:
        from data_audit import DataAuditor, AuditResult, audit_report_data
        macro_ctx_for_audit = {
            "fomc": fomc_ctx,
            "macro": risk,
            "sentiment": sentiment_data,
            "geopolitical": geo_data,
        }
        auditor = audit_report_data(macro_ctx=macro_ctx_for_audit, 
                                     cot_meta=structured.get("cot_meta"))
        agg = auditor.get_aggregate_confidence()
        lines.append(f"  {agg['icon']} AGGREGATE CONFIDENCE: {agg['score']}/100 ({agg['level']})")
        lines.append("")
        for r in auditor.results:
            lines.append(f"  {r}")
        if auditor.blocked:
            lines.append("")
            lines.append(f"  ⛔ BLOCKED SOURCES ({len(auditor.blocked)}):")
            for r in auditor.blocked:
                lines.append(f"     {r}")
        structured["audit"] = agg
    except Exception as e:
        logger.error("Data audit failed: %s", e)
        lines.append("  ⚠ Data audit unavailable")
    lines.append("")

    lines.append(f"Generated at {now.strftime('%H:%M:%S')} local time")
    lines.append(f"{'━'*60}")

    return "\n".join(lines), structured


def generate_tts_summary(briefing_text: str) -> str:
    """Create a concise spoken summary from the full briefing for TTS output."""
    lines = briefing_text.split("\n")
    risk_line = ""
    sp500_line = ""
    action_line = ""
    sentiment_line = ""

    for line in lines:
        if "MACRO RISK LEVEL" in line:
            risk_line = line.strip()
        elif "S&P 500" in line:
            sp500_line = line.strip()
        elif "ACTION:" in line:
            action_line = line.strip()
        elif "COMPOSITE SENTIMENT" in line:
            sentiment_line = line.strip()

    geo_line = ""
    fomc_line = ""

    for line in lines:
        if "MACRO RISK LEVEL" in line:
            risk_line = line.strip()
        elif "S&P 500" in line and "SPY" in line:
            sp500_line = line.strip()
        elif "ACTION:" in line:
            action_line = line.strip()
        elif "COMPOSITE SENTIMENT" in line:
            sentiment_line = line.strip()
        elif "CRITICAL GEOPOLITICAL" in line or "GEOPOLITICAL RISK: ELEVATED" in line:
            geo_line = line.strip()
        elif "FOMC IN" in line:
            fomc_line = line.strip()

    parts = []
    if risk_line:
        level = "green" if "GREEN" in risk_line else "yellow" if "YELLOW" in risk_line else "red"
        parts.append(f"Macro risk level is {level}.")
    if geo_line:
        parts.append("Geopolitical risk is elevated with active hotspots.")
    if sp500_line:
        parts.append(sp500_line.replace("📉", "").replace("📈", "").replace("$", "").strip() + ".")
    if sentiment_line:
        parts.append("Sentiment: " + sentiment_line.split("COMPOSITE SENTIMENT:")[-1].strip().rstrip(".") + ".")
    if fomc_line:
        parts.append(fomc_line.replace("🏛️", "").strip() + ".")
    if action_line:
        parts.append(action_line.replace("ACTION:", "Recommended action:").strip())

    return " ".join(parts) if parts else "Daily briefing generated. Check the full report for details."


if __name__ == "__main__":
    import sys
    import json as _json

    report, structured = generate_briefing()

    if "--json" in sys.argv:
        print(_json.dumps(structured, indent=2, default=str))
    else:
        print(report)
        print("\n🎙️ TTS Summary:")
        print(generate_tts_summary(report))
