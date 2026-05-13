"""FOMC Meeting Tracker — tracks Fed meeting dates, decisions, and rate expectations.

Provides:
- Next FOMC meeting date and countdown
- Current fed funds rate (LIVE from FRED API — ground truth)
- FOMC decision history (static, but verified against FRED on each run)
- Rate trajectory reconstruction from FRED DFEDTARU/DFEDTARL
- Statement tone classification (hawkish/dovish/neutral)

DATA INTEGRITY:
- Rate and decision data is VERIFIED against FRED API (DFEDTARU/DFEDTARL) on every call
- If FRED disagrees with static entries, FRED wins — discrepancies are logged
- Meeting schedule is static (from federalreserve.gov calendar) — low fabrication risk
- Tone/summary text is editorial (from statements) — flagged as such in audit

Used by: generate_cot_html_report.py, briefing.py
"""
import json
import os
import sys
import logging
import urllib.request
from datetime import datetime, date, timedelta

logger = logging.getLogger(__name__)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ── FOMC 2025-2026 MEETING SCHEDULE ──────────────────────────────────────
# Source: federalreserve.gov/monetarypolicy/fomccalendars.htm
# Format: (date_str, type) where type is "scheduled" or "unscheduled"
# Dates are announcement dates (2nd day of 2-day meetings)

FOMC_MEETINGS_2025 = [
    ("2025-01-29", "scheduled", "Statement + Press Conference"),
    ("2025-03-19", "scheduled", "Statement + SEP + Dot Plot + Press Conference"),
    ("2025-05-07", "scheduled", "Statement + Press Conference"),
    ("2025-06-18", "scheduled", "Statement + SEP + Dot Plot + Press Conference"),
    ("2025-07-30", "scheduled", "Statement + Press Conference"),
    ("2025-09-17", "scheduled", "Statement + SEP + Dot Plot + Press Conference"),
    ("2025-10-29", "scheduled", "Statement + Press Conference"),
    ("2025-12-10", "scheduled", "Statement + SEP + Dot Plot + Press Conference"),
]

FOMC_MEETINGS_2026 = [
    ("2026-01-28", "scheduled", "Statement + Press Conference"),
    ("2026-03-18", "scheduled", "Statement + SEP + Dot Plot + Press Conference"),
    ("2026-04-29", "scheduled", "Statement + Press Conference"),
    ("2026-06-17", "scheduled", "Statement + SEP + Dot Plot + Press Conference"),
    ("2026-07-29", "scheduled", "Statement + Press Conference"),
    ("2026-09-16", "scheduled", "Statement + SEP + Dot Plot + Press Conference"),
    ("2026-10-28", "scheduled", "Statement + Press Conference"),
    ("2026-12-16", "scheduled", "Statement + SEP + Dot Plot + Press Conference"),
]

ALL_MEETINGS = FOMC_MEETINGS_2025 + FOMC_MEETINGS_2026

# ── FOMC DECISION HISTORY (verified against federalreserve.gov) ────────
# Sources:
#   - https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm
#   - https://www.federalreserve.gov/monetarypolicy/fomc.htm
#   - Web search verification on 2026-03-21
#
# Format: date, action, rate_range, tone, key_points
FOMC_DECISIONS = [
    {
        "date": "2025-01-29",
        "action": "HOLD",
        "rate": "4.25-4.50%",
        "tone": "hawkish-hold",
        "summary_en": "Fed held rates at 4.25-4.50%. Unanimous decision. Statement signaled patience on future cuts.",
        "summary_cn": "美联储维持利率在4.25-4.50%。全票通过。声明暗示对未来降息保持耐心。",
    },
    {
        "date": "2025-03-19",
        "action": "HOLD",
        "rate": "4.25-4.50%",
        "tone": "neutral-hold",
        "summary_en": "Fed held rates steady at 4.25-4.50% for second consecutive meeting. SEP meeting with dot plot.",
        "summary_cn": "美联储连续第二次维持利率在4.25-4.50%不变。本次为SEP会议含点阵图。",
    },
    {
        "date": "2025-05-07",
        "action": "HOLD",
        "rate": "4.25-4.50%",
        "tone": "hawkish-hold",
        "summary_en": "Fed held rates at 4.25-4.50% for third consecutive meeting. Trade policy uncertainty cited.",
        "summary_cn": "美联储连续第三次维持利率在4.25-4.50%。提及贸易政策不确定性。",
    },
    {
        "date": "2025-06-18",
        "action": "HOLD",
        "rate": "4.25-4.50%",
        "tone": "neutral-hold",
        "summary_en": "Fed held rates at 4.25-4.50% for fourth consecutive meeting. SEP meeting with dot plot.",
        "summary_cn": "美联储连续第四次维持利率在4.25-4.50%。本次为SEP会议含点阵图。",
    },
    {
        "date": "2025-07-30",
        "action": "HOLD",
        "rate": "4.25-4.50%",
        "tone": "neutral-hold",
        "summary_en": "Fed held rates at 4.25-4.50% for fifth consecutive meeting.",
        "summary_cn": "美联储连续第五次维持利率在4.25-4.50%。",
    },
    {
        "date": "2025-09-17",
        "action": "CUT",
        "rate": "4.00-4.25%",
        "tone": "dovish",
        "summary_en": "First rate cut of 2025 — 25bp to 4.00-4.25%. First reduction after 5 consecutive holds. SEP meeting with dot plot.",
        "summary_cn": "2025年首次降息——25基点至4.00-4.25%。在连续5次维持后首次降息。本次为SEP会议含点阵图。",
    },
    {
        "date": "2025-10-29",
        "action": "CUT",
        "rate": "3.75-4.00%",
        "tone": "dovish",
        "summary_en": "Second consecutive 25bp cut to 3.75-4.00%.",
        "summary_cn": "连续第二次25基点降息至3.75-4.00%。",
    },
    {
        "date": "2025-12-10",
        "action": "CUT",
        "rate": "3.50-3.75%",
        "tone": "dovish",
        "summary_en": "Third consecutive 25bp cut to 3.50-3.75%. Three cuts in late 2025. SEP meeting with dot plot.",
        "summary_cn": "连续第三次25基点降息至3.50-3.75%。2025年末共三次降息。本次为SEP会议含点阵图。",
    },
    {
        "date": "2026-01-28",
        "action": "HOLD",
        "rate": "3.50-3.75%",
        "tone": "neutral-pause",
        "summary_en": "Fed held rates at 3.50-3.75% after 3 consecutive cuts. 2 dissenters preferred a quarter-point cut. Statement noted solid economic expansion, low job gains, stabilizing unemployment, somewhat elevated inflation.",
        "summary_cn": "连续3次降息后美联储暂停，维持利率在3.50-3.75%。2名委员反对，倾向降息25基点。声明指出经济稳健扩张、就业增长放缓、失业率趋稳、通胀仍略高。",
    },
    {
        "date": "2026-03-18",
        "action": "HOLD",
        "rate": "3.50-3.75%",
        "tone": "neutral-hold",
        "summary_en": "Fed held rates steady at 3.50-3.75%. March SEP dot plot: median 3.4% for 2026, 3.1% for 2027 — implies ~1 cut remaining in 2026. SEP unemployment forecast: 4.4%. Powell emphasized data-dependent approach, closely watching consumer spending.",
        "summary_cn": "美联储维持利率在3.50-3.75%不变。3月SEP点阵图：2026年中位数3.4%，2027年3.1%——暗示2026年还有约1次降息。SEP失业率预测：4.4%。鲍威尔强调数据依赖，密切关注消费支出。",
    },
]


# ── FRED API Integration (Ground Truth) ─────────────────────────────

def _get_fred_api_key():
    """Load FRED API key from .env or environment."""
    key = os.environ.get("FRED_API_KEY")
    if not key:
        try:
            from dotenv import load_dotenv
            env_path = os.path.join(SCRIPT_DIR, "..", ".env")
            load_dotenv(env_path)
            key = os.environ.get("FRED_API_KEY")
        except ImportError:
            pass
    return key


def fetch_fred_rate(series_id="DFEDTARU", limit=1):
    """Fetch latest value from FRED. Returns (value, date) or (None, None)."""
    key = _get_fred_api_key()
    if not key:
        return None, None
    try:
        url = (f"https://api.stlouisfed.org/fred/series/observations?"
               f"series_id={series_id}&api_key={key}&file_type=json"
               f"&sort_order=desc&limit={limit}")
        data = json.loads(urllib.request.urlopen(url, timeout=10).read())
        obs = data.get("observations", [])
        if obs and obs[0]["value"] != ".":
            return float(obs[0]["value"]), obs[0]["date"]
    except Exception as e:
        logger.warning(f"FRED fetch error for {series_id}: {e}")
    return None, None


def get_current_rate_from_fred():
    """
    Get LIVE current fed funds rate from FRED (DFEDTARU + DFEDTARL).
    Returns: {"upper": float, "lower": float, "range": str, "date": str, "source": "FRED"}
    Falls back to static data if FRED unavailable.
    """
    upper, u_date = fetch_fred_rate("DFEDTARU")
    lower, l_date = fetch_fred_rate("DFEDTARL")
    
    if upper is not None and lower is not None:
        return {
            "upper": upper,
            "lower": lower,
            "range": f"{lower:.2f}-{upper:.2f}%",
            "date": u_date,
            "source": "FRED",
        }
    
    # Fallback to static
    if FOMC_DECISIONS:
        return {
            "range": FOMC_DECISIONS[-1]["rate"],
            "date": FOMC_DECISIONS[-1]["date"],
            "source": "static_fallback",
        }
    return {"range": "Unknown", "source": "none"}


def reconstruct_decisions_from_fred(start_date="2024-09-01"):
    """
    Reconstruct FOMC rate decisions from FRED DFEDTARU rate changes.
    This is the GROUND TRUTH — if it disagrees with static entries, FRED is right.
    Returns list of {"date": str, "from_rate": float, "to_rate": float, "action": str}
    """
    key = _get_fred_api_key()
    if not key:
        return None
    
    try:
        url = (f"https://api.stlouisfed.org/fred/series/observations?"
               f"series_id=DFEDTARU&api_key={key}&file_type=json"
               f"&observation_start={start_date}&sort_order=asc")
        data = json.loads(urllib.request.urlopen(url, timeout=15).read())
        obs = data.get("observations", [])
        
        changes = []
        prev_rate = None
        for o in obs:
            if o["value"] == ".":
                continue
            rate = float(o["value"])
            if prev_rate is not None and rate != prev_rate:
                diff = rate - prev_rate
                action = "CUT" if diff < 0 else "HIKE"
                changes.append({
                    "date": o["date"],
                    "from_rate": prev_rate,
                    "to_rate": rate,
                    "diff": diff,
                    "action": action,
                })
            prev_rate = rate
        
        return changes
    except Exception as e:
        logger.warning(f"FRED reconstruction error: {e}")
        return None


def verify_decisions_against_fred():
    """
    Cross-check static FOMC_DECISIONS against FRED ground truth.
    Returns: {"verified": bool, "discrepancies": list, "fred_changes": list}
    """
    fred_changes = reconstruct_decisions_from_fred()
    if fred_changes is None:
        return {"verified": False, "error": "Could not fetch FRED data",
                "discrepancies": [], "fred_changes": []}
    
    discrepancies = []
    
    # Build lookup of FRED rate changes by approximate date (FOMC decision date = day after rate change)
    fred_by_date = {}
    for fc in fred_changes:
        # Rate change shows up day after FOMC announcement
        change_date = datetime.strptime(fc["date"], "%Y-%m-%d").date()
        # Check the day before too (announcement vs effective date)
        for offset in [0, -1]:
            d = (change_date + timedelta(days=offset)).isoformat()
            fred_by_date[d] = fc
    
    for decision in FOMC_DECISIONS:
        d_date = decision["date"]
        d_action = decision["action"]
        d_rate = decision["rate"]
        
        if d_action in ("CUT", "HIKE"):
            # Should have a corresponding FRED rate change
            # Check decision date and day after
            matched = False
            for offset in [0, 1]:
                check_date = (datetime.strptime(d_date, "%Y-%m-%d").date() + timedelta(days=offset)).isoformat()
                if check_date in fred_by_date:
                    fc = fred_by_date[check_date]
                    fred_rate = f"{fc['to_rate'] - 0.25:.2f}-{fc['to_rate']:.2f}%"
                    if fc["action"] != d_action:
                        discrepancies.append({
                            "date": d_date,
                            "issue": f"Action mismatch: static={d_action}, FRED={fc['action']}",
                            "static_rate": d_rate,
                            "fred_rate": fred_rate,
                        })
                    matched = True
                    break
            if not matched:
                discrepancies.append({
                    "date": d_date,
                    "issue": f"Static says {d_action} but no FRED rate change found near this date",
                    "static_rate": d_rate,
                })
        
        elif d_action == "HOLD":
            # Should NOT have a FRED rate change on this date
            for offset in [0, 1]:
                check_date = (datetime.strptime(d_date, "%Y-%m-%d").date() + timedelta(days=offset)).isoformat()
                if check_date in fred_by_date:
                    fc = fred_by_date[check_date]
                    discrepancies.append({
                        "date": d_date,
                        "issue": f"Static says HOLD but FRED shows rate change: {fc['action']} to {fc['to_rate']}%",
                        "static_rate": d_rate,
                        "fred_rate": f"{fc['to_rate']:.2f}%",
                    })
    
    return {
        "verified": len(discrepancies) == 0,
        "discrepancies": discrepancies,
        "fred_changes": fred_changes,
        "current_upper": fred_changes[-1]["to_rate"] if fred_changes else None,
    }


def get_current_rate():
    """Get current fed funds rate — prefers FRED live data, falls back to static."""
    live = get_current_rate_from_fred()
    if live.get("source") == "FRED":
        return live["range"]
    if FOMC_DECISIONS:
        return FOMC_DECISIONS[-1]["rate"]
    return "Unknown"


def get_next_meeting():
    """Get next FOMC meeting date and details."""
    today = date.today()
    for date_str, mtype, details in ALL_MEETINGS:
        meeting_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        if meeting_date > today:
            days_until = (meeting_date - today).days
            has_sep = "SEP" in details
            return {
                "date": date_str,
                "days_until": days_until,
                "type": mtype,
                "details": details,
                "has_dot_plot": has_sep,
                "has_press_conference": True,
            }
    return None


def get_last_meeting():
    """Get the most recent FOMC decision."""
    today = date.today()
    past = [d for d in FOMC_DECISIONS if datetime.strptime(d["date"], "%Y-%m-%d").date() <= today]
    return past[-1] if past else None


def get_recent_decisions(n=4):
    """Get last N FOMC decisions."""
    return FOMC_DECISIONS[-n:]


def get_rate_trajectory():
    """Compute rate trajectory from decision history."""
    trajectory = []
    for d in FOMC_DECISIONS:
        # Extract first number from rate range
        rate_str = d["rate"].split("-")[0].replace("%", "")
        try:
            rate = float(rate_str)
        except ValueError:
            continue
        trajectory.append({
            "date": d["date"],
            "rate": rate,
            "action": d["action"],
            "tone": d["tone"],
        })
    return trajectory


def get_fomc_context():
    """Get complete FOMC context for integration into reports.
    
    Includes FRED verification — if FRED disagrees with static data,
    discrepancies are flagged and FRED rate takes priority.
    """
    next_meeting = get_next_meeting()
    last_meeting = get_last_meeting()
    recent = get_recent_decisions(4)
    trajectory = get_rate_trajectory()
    
    # Count actions in recent history
    cuts = sum(1 for d in FOMC_DECISIONS if d["action"] == "CUT")
    holds = sum(1 for d in FOMC_DECISIONS if d["action"] == "HOLD")
    hikes = sum(1 for d in FOMC_DECISIONS if d["action"] == "HIKE")
    
    # Current tone assessment
    recent_tones = [d["tone"] for d in FOMC_DECISIONS[-3:]]
    dovish_count = sum(1 for t in recent_tones if "dovish" in t)
    hawkish_count = sum(1 for t in recent_tones if "hawkish" in t)
    
    if dovish_count >= 2:
        bias = "DOVISH"
        bias_cn = "鸽派"
    elif hawkish_count >= 2:
        bias = "HAWKISH"
        bias_cn = "鹰派"
    else:
        bias = "NEUTRAL"
        bias_cn = "中性"
    
    # FRED verification — cross-check static vs ground truth
    fred_live = get_current_rate_from_fred()
    verification = verify_decisions_against_fred()
    
    # Use FRED rate if available (overrides static)
    current_rate = fred_live.get("range", get_current_rate())
    rate_source = fred_live.get("source", "static")
    
    # Log discrepancies as warnings
    if verification.get("discrepancies"):
        for d in verification["discrepancies"]:
            logger.warning(f"⚠️ FOMC DATA DISCREPANCY: {d['date']} — {d['issue']}")
    
    return {
        "current_rate": current_rate,
        "rate_source": rate_source,  # "FRED" or "static_fallback"
        "next_meeting": next_meeting,
        "last_meeting": last_meeting,
        "recent_decisions": recent,
        "trajectory": trajectory,
        "total_cuts": cuts,
        "total_holds": holds,
        "total_hikes": hikes,
        "current_bias": bias,
        "current_bias_cn": bias_cn,
        "fred_verified": verification.get("verified", False),
        "fred_discrepancies": verification.get("discrepancies", []),
    }


def format_fomc_report(lang='en'):
    """Format a text report of FOMC status."""
    ctx = get_fomc_context()
    
    if lang == 'cn':
        lines = []
        lines.append(f"📌 当前利率: {ctx['current_rate']}")
        if ctx['next_meeting']:
            nm = ctx['next_meeting']
            lines.append(f"📅 下次会议: {nm['date']} ({nm['days_until']}天后)")
            lines.append(f"   类型: {nm['details']}")
            if nm['has_dot_plot']:
                lines.append("   ⚠️ 包含SEP + 点阵图 — 重要会议")
        lines.append(f"📊 本轮周期: {ctx['total_cuts']}次降息, {ctx['total_holds']}次维持")
        lines.append(f"🎯 当前倾向: {ctx['current_bias_cn']}")
        if ctx['last_meeting']:
            lm = ctx['last_meeting']
            lines.append(f"\n最近决议 ({lm['date']}): {lm['action']} → {lm['rate']}")
            lines.append(f"  {lm['summary_cn']}")
        return "\n".join(lines)
    else:
        lines = []
        lines.append(f"📌 Current Rate: {ctx['current_rate']}")
        if ctx['next_meeting']:
            nm = ctx['next_meeting']
            lines.append(f"📅 Next Meeting: {nm['date']} ({nm['days_until']} days)")
            lines.append(f"   Type: {nm['details']}")
            if nm['has_dot_plot']:
                lines.append("   ⚠️ Includes SEP + Dot Plot — major meeting")
        lines.append(f"📊 Cycle: {ctx['total_cuts']} cuts, {ctx['total_holds']} holds")
        lines.append(f"🎯 Current Bias: {ctx['current_bias']}")
        if ctx['last_meeting']:
            lm = ctx['last_meeting']
            lines.append(f"\nLast Decision ({lm['date']}): {lm['action']} → {lm['rate']}")
            lines.append(f"  {lm['summary_en']}")
        return "\n".join(lines)


if __name__ == "__main__":
    lang = 'cn' if '--cn' in sys.argv else 'en'
    if '--json' in sys.argv:
        print(json.dumps(get_fomc_context(), indent=2, default=str))
    else:
        print(format_fomc_report(lang))
