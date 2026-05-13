#!/usr/bin/env python3
"""
Economic Calendar — generates upcoming key events with dates.
Uses known recurring release patterns + FOMC schedule + web search for specifics.

NOT static text — computes actual dates for recurring events.
"""

import json
import os
import urllib.request
from datetime import datetime, date, timedelta


def _next_weekday(d, weekday):
    """Find the next occurrence of a weekday (0=Mon, 6=Sun) on or after date d."""
    days_ahead = weekday - d.weekday()
    if days_ahead < 0:
        days_ahead += 7
    return d + timedelta(days=days_ahead)


def _nth_weekday_of_month(year, month, weekday, n):
    """Get the nth occurrence of a weekday in a given month."""
    first_day = date(year, month, 1)
    first_occ = _next_weekday(first_day, weekday)
    return first_occ + timedelta(weeks=n - 1)


def get_upcoming_events(from_date=None, days_ahead=7):
    """
    Get key economic events for the next N days.
    Returns list of {"date": str, "event": str, "event_cn": str, "impact": "high"|"medium"|"low", "asset_relevance": [str]}
    """
    if from_date is None:
        from_date = date.today()
    
    end_date = from_date + timedelta(days=days_ahead)
    events = []
    
    # ── Recurring Weekly Events ──
    for d in _daterange(from_date, end_date):
        # Jobless Claims — every Thursday
        if d.weekday() == 3:  # Thursday
            events.append({
                "date": d.isoformat(),
                "event": f"Weekly Initial Jobless Claims ({d.strftime('%b %d')})",
                "event_cn": f"每周初请失业金人数（{d.strftime('%m/%d')}）",
                "impact": "medium",
                "asset_relevance": ["S&P 500", "Nasdaq 100", "Gold", "Euro FX"],
            })
    
    # ── Monthly Events (computed from known patterns) ──
    for month_offset in range(2):  # check this month and next
        year = from_date.year
        month = from_date.month + month_offset
        if month > 12:
            month -= 12
            year += 1
        
        # NFP — First Friday of the month
        nfp_date = _nth_weekday_of_month(year, month, 4, 1)  # Friday = 4
        if from_date <= nfp_date <= end_date:
            events.append({
                "date": nfp_date.isoformat(),
                "event": f"Nonfarm Payrolls — {nfp_date.strftime('%b %d')}",
                "event_cn": f"非农就业报告 — {nfp_date.strftime('%m/%d')}",
                "impact": "high",
                "asset_relevance": ["S&P 500", "Nasdaq 100", "Gold", "Euro FX", "Crude Oil"],
            })
        
        # CPI — typically 2nd or 3rd week, ~10th-14th
        # Approximate: 2nd Wednesday
        cpi_approx = _nth_weekday_of_month(year, month, 2, 2)  # 2nd Wednesday
        if from_date <= cpi_approx <= end_date:
            events.append({
                "date": cpi_approx.isoformat(),
                "event": f"CPI Inflation Report (approx. {cpi_approx.strftime('%b %d')})",
                "event_cn": f"CPI通胀报告（约{cpi_approx.strftime('%m/%d')}）",
                "impact": "high",
                "asset_relevance": ["S&P 500", "Gold", "Euro FX"],
                "note": "Date is approximate — verify against BLS calendar",
            })
        
        # PMI (ISM) — First business day of the month
        first_biz = date(year, month, 1)
        while first_biz.weekday() >= 5:
            first_biz += timedelta(days=1)
        if from_date <= first_biz <= end_date:
            events.append({
                "date": first_biz.isoformat(),
                "event": f"ISM Manufacturing PMI — {first_biz.strftime('%b %d')}",
                "event_cn": f"ISM制造业PMI — {first_biz.strftime('%m/%d')}",
                "impact": "high",
                "asset_relevance": ["S&P 500", "Crude Oil"],
            })
        
        # Flash PMIs (S&P Global) — typically 3rd week, around 21st-24th
        flash_approx = date(year, month, 22)
        while flash_approx.weekday() >= 5:
            flash_approx += timedelta(days=1)
        if from_date <= flash_approx <= end_date:
            events.append({
                "date": flash_approx.isoformat(),
                "event": f"S&P Global Flash PMIs (approx. {flash_approx.strftime('%b %d')})",
                "event_cn": f"S&P全球PMI初值（约{flash_approx.strftime('%m/%d')}）",
                "impact": "high",
                "asset_relevance": ["S&P 500", "Euro FX", "Crude Oil"],
                "note": "Date is approximate",
            })
        
        # EIA Weekly Petroleum Report — every Wednesday
        for d in _daterange(from_date, end_date):
            if d.weekday() == 2:  # Wednesday
                events.append({
                    "date": d.isoformat(),
                    "event": f"EIA Weekly Petroleum Status ({d.strftime('%b %d')})",
                    "event_cn": f"EIA周度石油库存报告（{d.strftime('%m/%d')}）",
                    "impact": "medium",
                    "asset_relevance": ["Crude Oil"],
                })
                break  # only need the next one
        
        # COT Report — every Friday
        for d in _daterange(from_date, end_date):
            if d.weekday() == 4:  # Friday
                events.append({
                    "date": d.isoformat(),
                    "event": f"CFTC COT Report ({d.strftime('%b %d')}, as-of prev. Tuesday)",
                    "event_cn": f"CFTC COT持仓报告（{d.strftime('%m/%d')}，截至上周二）",
                    "impact": "medium",
                    "asset_relevance": ["S&P 500", "Nasdaq 100", "Bitcoin", "Gold", "Crude Oil", "Euro FX"],
                })
                break
    
    # ── FOMC Events ──
    try:
        from fomc_tracker import get_next_meeting, ALL_MEETINGS
        
        # Check if any FOMC meeting falls in our window
        for date_str, mtype, details in ALL_MEETINGS:
            meeting_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            if from_date <= meeting_date <= end_date:
                is_sep = "SEP" in details
                events.append({
                    "date": date_str,
                    "event": f"FOMC Rate Decision + Press Conference — {meeting_date.strftime('%b %d')}" + (" ⚠️ SEP + DOT PLOT" if is_sep else ""),
                    "event_cn": f"FOMC利率决议 + 新闻发布会 — {meeting_date.strftime('%m/%d')}" + (" ⚠️ 含SEP+点阵图" if is_sep else ""),
                    "impact": "high",
                    "asset_relevance": ["S&P 500", "Nasdaq 100", "Bitcoin", "Gold", "Crude Oil", "Euro FX"],
                })
        
        # Also mention next meeting even if outside window
        nm = get_next_meeting()
        if nm and nm["days_until"] <= 14 and nm["days_until"] > days_ahead:
            events.append({
                "date": nm["date"],
                "event": f"FOMC Meeting in {nm['days_until']}d — {nm['details']}",
                "event_cn": f"FOMC会议{nm['days_until']}天后 — {nm['details']}",
                "impact": "high",
                "asset_relevance": ["S&P 500", "Nasdaq 100", "Bitcoin", "Gold", "Crude Oil", "Euro FX"],
            })
    except ImportError:
        pass
    
    # Sort by date and impact
    impact_order = {"high": 0, "medium": 1, "low": 2}
    events.sort(key=lambda e: (e["date"], impact_order.get(e["impact"], 2)))
    
    # Deduplicate by date+event
    seen = set()
    unique = []
    for e in events:
        key = (e["date"], e["event"][:30])
        if key not in seen:
            seen.add(key)
            unique.append(e)
    
    return unique


def get_asset_events(asset, from_date=None, days_ahead=7):
    """Get events relevant to a specific asset."""
    all_events = get_upcoming_events(from_date, days_ahead)
    return [e for e in all_events if asset in e.get("asset_relevance", [])]


def format_watch_list(events, lang='en', max_items=7):
    """Format events into the 'Watch Next Week' HTML."""
    if not events:
        return ""
    
    high = [e for e in events if e["impact"] == "high"][:5]
    medium = [e for e in events if e["impact"] == "medium"][:3]
    
    items = high + medium
    if not items:
        items = events[:max_items]
    
    if lang == 'cn':
        parts = []
        for i, e in enumerate(items[:max_items], 1):
            d = datetime.strptime(e["date"], "%Y-%m-%d").strftime("%m/%d %a")
            icon = "🔴" if e["impact"] == "high" else "🟡"
            parts.append(f"({i}) {icon} {d} — {e['event_cn']}")
        return "；".join(parts)
    else:
        parts = []
        for i, e in enumerate(items[:max_items], 1):
            d = datetime.strptime(e["date"], "%Y-%m-%d").strftime("%b %d (%a)")
            icon = "🔴" if e["impact"] == "high" else "🟡"
            parts.append(f"({i}) {icon} {d} — {e['event']}")
        return "; ".join(parts)


def _daterange(start, end):
    """Generate dates from start to end (exclusive)."""
    current = start
    while current < end:
        yield current
        current += timedelta(days=1)


if __name__ == "__main__":
    events = get_upcoming_events(days_ahead=10)
    print(f"📅 Upcoming Events ({len(events)}):\n")
    for e in events:
        icon = "🔴" if e["impact"] == "high" else "🟡" if e["impact"] == "medium" else "⚪"
        print(f"  {icon} {e['date']} — {e['event']}")
        if e.get("note"):
            print(f"      ⚠️ {e['note']}")
    
    print(f"\n📋 Watch List (EN):\n  {format_watch_list(events, 'en')}")
    print(f"\n📋 Watch List (CN):\n  {format_watch_list(events, 'cn')}")
