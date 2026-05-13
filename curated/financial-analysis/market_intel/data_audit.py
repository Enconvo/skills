#!/usr/bin/env python3
"""
Data Reliability Audit Layer
Validates all data sources before they're used in analysis/reports.
Every data point gets a confidence score and provenance tag.

Confidence levels:
  ✅ HIGH (80-100)   — Live API data, fresh (<24h), from authoritative source
  🟡 MEDIUM (50-79)  — Live but stale (1-7d), or secondary source
  🟠 LOW (20-49)     — Very stale (>7d), or unverified secondary source
  🔴 UNVERIFIED (0-19) — Static/hardcoded data, no API validation, or fabrication risk

Rules:
  1. Static hardcoded data ALWAYS starts at confidence 0 (UNVERIFIED)
  2. Static data with web_search verification gets bumped to MEDIUM (50-60)
  3. Live API data starts at HIGH (90) and degrades with staleness
  4. Any data point that fails validation is flagged, not silently used
  5. Reports must show aggregate confidence score
"""

import os
import json
from datetime import datetime, timedelta
from typing import Any, Optional


# ── Data Source Registry ──────────────────────────────────────────────
# Every data source must be registered with its type and properties

DATA_SOURCES = {
    "fomc_decisions": {
        "type": "static",  # hardcoded in fomc_tracker.py
        "base_confidence": 0,  # static = starts at zero
        "authority": "federalreserve.gov",
        "risk": "FABRICATION — AI may hallucinate plausible-sounding decisions",
        "mitigation": "Must be verified against federalreserve.gov after each meeting",
        "last_verified": "2026-03-21",  # date of last web_search verification
        "verified_entries": [  # which entries have been checked
            "2025-01-29", "2025-03-19", "2025-05-07", "2025-06-18",
            "2025-07-30", "2025-09-17", "2025-10-29", "2025-12-10",
            "2026-01-28", "2026-03-18",
        ],
    },
    "fomc_schedule": {
        "type": "static",
        "base_confidence": 0,
        "authority": "federalreserve.gov",
        "risk": "Meeting dates may be wrong if not verified",
        "mitigation": "Check against FOMC calendar page",
        "last_verified": "2026-03-21",
    },
    "fred_data": {
        "type": "live_api",
        "base_confidence": 95,
        "authority": "Federal Reserve Economic Data (FRED)",
        "risk": "API downtime, delayed publication (weekends/holidays)",
        "mitigation": "Check observation_date vs current date",
    },
    "cot_data": {
        "type": "live_api",
        "base_confidence": 90,
        "authority": "CFTC via Polygon.io",
        "risk": "Weekly data, always 3-4 days old. API key required.",
        "mitigation": "Check data_as_of date in metadata",
    },
    "price_data": {
        "type": "live_api",
        "base_confidence": 90,
        "authority": "Yahoo Finance",
        "risk": "Weekend/holiday staleness, occasional API failures",
        "mitigation": "Check last trade date",
    },
    "fear_greed": {
        "type": "live_api",
        "base_confidence": 85,
        "authority": "CNN Fear & Greed Index",
        "risk": "Scraping-based, endpoint may change",
        "mitigation": "Validate value is 0-100 range",
    },
    "naaim": {
        "type": "live_api",
        "base_confidence": 80,
        "authority": "NAAIM Exposure Index",
        "risk": "Weekly survey, published Wednesdays. Scraping-based.",
        "mitigation": "Check survey date",
    },
    "reddit_sentiment": {
        "type": "live_api",
        "base_confidence": 70,
        "authority": "Reddit JSON API",
        "risk": "Sentiment analysis is heuristic-based, not ground truth",
        "mitigation": "Flag as 'sentiment estimate' not 'fact'",
    },
    "vix_data": {
        "type": "live_api",
        "base_confidence": 90,
        "authority": "CBOE via Yahoo Finance",
        "risk": "Weekend staleness",
        "mitigation": "Check last trade date",
    },
    "portfolio_data": {
        "type": "static_file",
        "base_confidence": 60,
        "authority": "User-maintained portfolio_data.json",
        "risk": "May be outdated if not refreshed. Prices are snapshot, not live.",
        "mitigation": "Check file modification date, compare prices to live",
    },
    "geopolitical_news": {
        "type": "live_api",
        "base_confidence": 75,
        "authority": "Google News RSS, MarketWatch, CNBC",
        "risk": "Headlines only — no full article analysis. Keyword matching may misclassify.",
        "mitigation": "Cross-reference hotspot alerts with multiple sources",
    },
    "ai_commentary": {
        "type": "ai_generated",
        "base_confidence": 40,
        "authority": "LLM-generated analysis",
        "risk": "HALLUCINATION — AI may generate plausible but wrong analysis",
        "mitigation": "Commentary should cite specific data points that can be verified",
    },
}


class AuditResult:
    """Result of auditing a single data point or source."""
    
    def __init__(self, source: str, confidence: int, value: Any = None,
                 issues: list = None, timestamp: str = None):
        self.source = source
        self.confidence = max(0, min(100, confidence))
        self.value = value
        self.issues = issues or []
        self.timestamp = timestamp or datetime.now().isoformat()
    
    @property
    def level(self) -> str:
        if self.confidence >= 80:
            return "HIGH"
        elif self.confidence >= 50:
            return "MEDIUM"
        elif self.confidence >= 20:
            return "LOW"
        return "UNVERIFIED"
    
    @property
    def icon(self) -> str:
        return {"HIGH": "✅", "MEDIUM": "🟡", "LOW": "🟠", "UNVERIFIED": "🔴"}[self.level]
    
    @property
    def color(self) -> str:
        return {"HIGH": "#16A34A", "MEDIUM": "#D97706", "LOW": "#EA580C", "UNVERIFIED": "#DC2626"}[self.level]
    
    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "confidence": self.confidence,
            "level": self.level,
            "issues": self.issues,
            "timestamp": self.timestamp,
        }
    
    def __repr__(self):
        return f"{self.icon} {self.source}: {self.confidence}/100 ({self.level}) {' | '.join(self.issues) if self.issues else ''}"


class DataAuditor:
    """Audits all data sources and produces a reliability report."""
    
    def __init__(self):
        self.results: list[AuditResult] = []
        self.blocked: list[AuditResult] = []  # data too unreliable to use
    
    def audit_static_data(self, source_key: str, data: Any, 
                          verified_date: str = None) -> AuditResult:
        """Audit static/hardcoded data. Starts at base_confidence 0."""
        src = DATA_SOURCES.get(source_key, {})
        confidence = src.get("base_confidence", 0)
        issues = []
        
        # Bump confidence if verified recently
        if verified_date:
            try:
                vd = datetime.strptime(verified_date, "%Y-%m-%d")
                days_since = (datetime.now() - vd).days
                if days_since <= 1:
                    confidence = max(confidence, 70)  # verified today/yesterday
                elif days_since <= 7:
                    confidence = max(confidence, 55)  # verified this week
                elif days_since <= 30:
                    confidence = max(confidence, 40)  # verified this month
                    issues.append(f"Last verified {days_since}d ago — consider re-verifying")
                else:
                    issues.append(f"⚠️ Last verified {days_since}d ago — STALE, re-verify required")
            except ValueError:
                issues.append("Invalid verification date")
        else:
            issues.append("⚠️ NEVER VERIFIED — do not use without verification")
        
        # Check if data is empty/None
        if data is None or (isinstance(data, (list, dict)) and len(data) == 0):
            confidence = 0
            issues.append("No data present")
        
        result = AuditResult(source_key, confidence, data, issues)
        self.results.append(result)
        
        if confidence < 20:
            self.blocked.append(result)
        
        return result
    
    def audit_live_data(self, source_key: str, data: Any,
                        data_date: str = None, 
                        max_age_hours: int = 24) -> AuditResult:
        """Audit live API data. Degrades confidence with staleness."""
        src = DATA_SOURCES.get(source_key, {})
        confidence = src.get("base_confidence", 90)
        issues = []
        
        # Check data freshness
        if data_date:
            try:
                # Try multiple date formats
                dd = None
                for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%m/%d/%Y", "%Y-%m-%d %H:%M:%S"]:
                    try:
                        dd = datetime.strptime(str(data_date).strip(), fmt)
                        break
                    except ValueError:
                        continue
                
                if dd:
                    age_hours = (datetime.now() - dd).total_seconds() / 3600
                    if age_hours > max_age_hours * 7:  # >7x max age
                        confidence -= 40
                        issues.append(f"⚠️ Data is {age_hours/24:.0f} days old — VERY STALE")
                    elif age_hours > max_age_hours * 3:
                        confidence -= 20
                        issues.append(f"Data is {age_hours/24:.1f} days old")
                    elif age_hours > max_age_hours:
                        confidence -= 10
                        issues.append(f"Data is {age_hours:.0f}h old (max: {max_age_hours}h)")
                else:
                    issues.append(f"Could not parse data date: {data_date}")
                    confidence -= 15
            except Exception as e:
                issues.append(f"Date check error: {e}")
                confidence -= 10
        else:
            # No date provided — mild penalty
            confidence -= 5
            issues.append("No data timestamp provided")
        
        # Check for empty data
        if data is None:
            confidence = 0
            issues.append("API returned no data")
        elif isinstance(data, dict) and data.get("error"):
            confidence = 0
            issues.append(f"API error: {data['error']}")
        
        # Sanity checks for known sources
        if source_key == "fear_greed" and data is not None:
            try:
                val = float(data) if not isinstance(data, dict) else float(data.get("value", -1))
                if not (0 <= val <= 100):
                    confidence -= 30
                    issues.append(f"Fear & Greed value {val} outside 0-100 range")
            except (ValueError, TypeError):
                confidence -= 20
                issues.append("Fear & Greed value not numeric")
        
        if source_key == "vix_data" and data is not None:
            try:
                val = float(data) if not isinstance(data, dict) else float(data.get("value", -1))
                if not (5 <= val <= 100):
                    confidence -= 20
                    issues.append(f"VIX value {val} outside normal range (5-100)")
            except (ValueError, TypeError):
                pass
        
        result = AuditResult(source_key, confidence, data, issues)
        self.results.append(result)
        
        if confidence < 20:
            self.blocked.append(result)
        
        return result
    
    def audit_ai_generated(self, source_key: str, content: str,
                           cites_data: bool = False) -> AuditResult:
        """Audit AI-generated content (commentary, verdicts, scenarios)."""
        src = DATA_SOURCES.get(source_key, {})
        confidence = src.get("base_confidence", 40)
        issues = ["AI-generated content — treat as analysis, not fact"]
        
        if cites_data:
            confidence += 15
        else:
            issues.append("Does not cite specific verifiable data points")
        
        if content and len(content) > 50:
            # Has substance
            pass
        else:
            confidence -= 10
            issues.append("Content too short for meaningful analysis")
        
        result = AuditResult(source_key, confidence, content, issues)
        self.results.append(result)
        return result
    
    def get_aggregate_confidence(self) -> dict:
        """Compute overall report confidence score."""
        if not self.results:
            return {"score": 0, "level": "UNVERIFIED", "icon": "🔴", "count": 0}
        
        # Weighted by source importance
        weights = {
            "fomc_decisions": 3,
            "cot_data": 3,
            "fred_data": 2,
            "price_data": 2,
            "fear_greed": 1,
            "naaim": 1,
            "reddit_sentiment": 0.5,
            "vix_data": 1,
            "ai_commentary": 0.5,
            "fomc_schedule": 1,
            "portfolio_data": 2,
        }
        
        total_weight = 0
        weighted_sum = 0
        for r in self.results:
            w = weights.get(r.source, 1)
            weighted_sum += r.confidence * w
            total_weight += w
        
        score = round(weighted_sum / total_weight) if total_weight > 0 else 0
        
        if score >= 80:
            level, icon = "HIGH", "✅"
        elif score >= 50:
            level, icon = "MEDIUM", "🟡"
        elif score >= 20:
            level, icon = "LOW", "🟠"
        else:
            level, icon = "UNVERIFIED", "🔴"
        
        return {
            "score": score,
            "level": level,
            "icon": icon,
            "count": len(self.results),
            "blocked_count": len(self.blocked),
            "results": [r.to_dict() for r in self.results],
            "blocked": [r.to_dict() for r in self.blocked],
        }
    
    def generate_html_badge(self) -> str:
        """Generate HTML badge showing data confidence for the report."""
        agg = self.get_aggregate_confidence()
        
        # Individual source rows
        source_rows = ""
        for r in self.results:
            issues_html = ""
            if r.issues:
                issues_html = '<br>'.join(f'<small style="color:#888">{i}</small>' for i in r.issues)
            source_rows += f"""
            <tr>
                <td style="font-size:0.85em">{r.icon} {r.source.replace('_', ' ').title()}</td>
                <td style="text-align:center"><strong style="color:{r.color}">{r.confidence}</strong></td>
                <td style="text-align:center;font-size:0.8em;color:{r.color}">{r.level}</td>
                <td style="font-size:0.8em">{issues_html}</td>
            </tr>"""
        
        blocked_warning = ""
        if self.blocked:
            names = ", ".join(r.source for r in self.blocked)
            blocked_warning = f"""
            <div style="background:#FEF2F2;border:1px solid #FECACA;border-radius:6px;padding:10px;margin-top:10px;font-size:0.85em;color:#991B1B">
                ⛔ <strong>Blocked sources ({len(self.blocked)}):</strong> {names}
                <br><small>These data sources scored below 20/100 and should NOT be used for decisions.</small>
            </div>"""
        
        return f"""
        <div class="audit-panel" id="data-audit" style="background:white;border-radius:12px;padding:24px;margin-bottom:30px;box-shadow:0 2px 8px rgba(0,0,0,0.06);border-left:4px solid {agg['icon'] == '✅' and '#16A34A' or agg['icon'] == '🟡' and '#D97706' or '#DC2626'}">
            <h3 style="margin-bottom:4px">
                <span class="lang-en">🔍 Data Reliability Audit</span>
                <span class="lang-cn" style="display:none">🔍 数据可靠性审计</span>
            </h3>
            <p style="color:#888;font-size:0.82em;margin-bottom:16px">
                <span class="lang-en">Every data source is scored for confidence before use in analysis.</span>
                <span class="lang-cn" style="display:none">每个数据源在用于分析前均经过可信度评分。</span>
            </p>
            <div style="display:flex;align-items:center;gap:16px;margin-bottom:16px;padding:12px 16px;background:#FAF7F2;border-radius:8px">
                <div style="font-size:2em">{agg['icon']}</div>
                <div>
                    <div style="font-size:1.3em;font-weight:700;color:{'#16A34A' if agg['score'] >= 80 else '#D97706' if agg['score'] >= 50 else '#DC2626'}">
                        {agg['score']}/100 — {agg['level']}
                    </div>
                    <div style="font-size:0.8em;color:#888">
                        <span class="lang-en">Aggregate confidence across {agg['count']} data sources</span>
                        <span class="lang-cn" style="display:none">基于{agg['count']}个数据源的综合可信度</span>
                    </div>
                </div>
            </div>
            {blocked_warning}
            <details style="margin-top:12px">
                <summary style="cursor:pointer;font-size:0.9em;color:#555;font-weight:600">
                    <span class="lang-en">📋 Source-by-Source Audit</span>
                    <span class="lang-cn" style="display:none">📋 逐源审计详情</span>
                </summary>
                <table style="width:100%;border-collapse:collapse;margin-top:10px">
                    <tr style="border-bottom:2px solid #e5e1db">
                        <th style="text-align:left;padding:6px;font-size:0.8em">Source</th>
                        <th style="text-align:center;padding:6px;font-size:0.8em">Score</th>
                        <th style="text-align:center;padding:6px;font-size:0.8em">Level</th>
                        <th style="text-align:left;padding:6px;font-size:0.8em">Notes</th>
                    </tr>
                    {source_rows}
                </table>
            </details>
        </div>"""
    
    def print_report(self):
        """Print CLI audit report."""
        agg = self.get_aggregate_confidence()
        print(f"\n{'='*60}")
        print(f"  🔍 DATA RELIABILITY AUDIT: {agg['icon']} {agg['score']}/100 ({agg['level']})")
        print(f"{'='*60}")
        for r in self.results:
            print(f"  {r}")
        if self.blocked:
            print(f"\n  ⛔ BLOCKED ({len(self.blocked)}):")
            for r in self.blocked:
                print(f"     {r}")
        print(f"{'='*60}\n")


def audit_report_data(macro_ctx: dict = None, cot_meta: dict = None) -> DataAuditor:
    """
    Run full audit on all data sources used in the COT report.
    Call this before generating HTML to get the audit badge.
    """
    auditor = DataAuditor()
    
    # 1. FOMC decisions — now FRED-verified on every run
    fomc_data = None
    if macro_ctx and macro_ctx.get("fomc"):
        fomc_data = macro_ctx["fomc"]
    
    if fomc_data and fomc_data.get("fred_verified") is True:
        # FRED cross-check passed — rate from authoritative source
        result = AuditResult("fomc_decisions", 92, fomc_data,
                            [f"✅ Rate verified against FRED API (source: {fomc_data.get('rate_source', '?')})"])
        auditor.results.append(result)
    elif fomc_data and fomc_data.get("fred_discrepancies"):
        # FRED found problems
        issues = [f"⚠️ FRED discrepancy: {d['issue']}" for d in fomc_data["fred_discrepancies"][:3]]
        issues.insert(0, "Static data conflicts with FRED ground truth")
        result = AuditResult("fomc_decisions", 30, fomc_data, issues)
        auditor.results.append(result)
    elif fomc_data and fomc_data.get("rate_source") == "FRED":
        # FRED live rate but couldn't run full verification
        result = AuditResult("fomc_decisions", 85, fomc_data,
                            ["Rate from FRED live; full decision history not cross-checked"])
        auditor.results.append(result)
    else:
        # No FRED verification — fall back to date-based audit
        src = DATA_SOURCES.get("fomc_decisions", {})
        last_verified = src.get("last_verified")
        auditor.audit_static_data("fomc_decisions", fomc_data, verified_date=last_verified)
    
    # 2. FOMC schedule (static — low risk, just dates)
    src = DATA_SOURCES.get("fomc_schedule", {})
    auditor.audit_static_data("fomc_schedule", True, verified_date=src.get("last_verified"))
    
    # 3. COT data (live API)
    if cot_meta:
        data_date = cot_meta.get("data_as_of")
        auditor.audit_live_data("cot_data", cot_meta, data_date=data_date, max_age_hours=96)
    
    # 4. FRED / Macro data (live API)
    if macro_ctx and macro_ctx.get("macro"):
        macro = macro_ctx["macro"]
        auditor.audit_live_data("fred_data", macro, max_age_hours=48)
    
    # 5. Price data (live API — always fetched during report gen)
    auditor.audit_live_data("price_data", True, max_age_hours=24)
    
    # 6. Sentiment components
    if macro_ctx and macro_ctx.get("sentiment"):
        sent = macro_ctx["sentiment"]
        
        # Fear & Greed — may be nested in dict or flat
        fg = sent.get("fear_greed", {})
        fg_val = fg.get("score") if isinstance(fg, dict) else sent.get("fear_greed_value")
        auditor.audit_live_data("fear_greed", fg_val, 
                               data_date=sent.get("date"), max_age_hours=24)
        
        # NAAIM — nested dict with date field
        naaim = sent.get("naaim", {})
        naaim_date = naaim.get("date") if isinstance(naaim, dict) else sent.get("naaim_date")
        naaim_val = naaim.get("exposure") if isinstance(naaim, dict) else sent.get("naaim_exposure")
        auditor.audit_live_data("naaim", naaim_val,
                               data_date=naaim_date, max_age_hours=168)
        
        # Reddit sentiment
        reddit = sent.get("reddit_summary", sent.get("reddit_sentiment"))
        auditor.audit_live_data("reddit_sentiment", reddit,
                               data_date=sent.get("date"), max_age_hours=24)
    
    # 7. Geopolitical news (live RSS)
    if macro_ctx and macro_ctx.get("geopolitical"):
        geo = macro_ctx["geopolitical"]
        auditor.audit_live_data("geopolitical_news", geo,
                               data_date=geo.get("scan_date", "")[:10], max_age_hours=6)
    
    # 8. AI-generated content (commentary, verdicts)
    auditor.audit_ai_generated("ai_commentary", "report commentary", cites_data=True)
    
    return auditor


# ── Staleness Guard ──────────────────────────────────────────────────
# Prevents using data that's too old without explicit acknowledgment

def check_staleness(data_date_str: str, max_days: int = 7, label: str = "data") -> dict:
    """
    Check if data is too stale to use.
    Returns: {"ok": bool, "age_days": float, "warning": str or None}
    """
    try:
        for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%Y-%m-%dT%H:%M:%S"]:
            try:
                dd = datetime.strptime(str(data_date_str).strip(), fmt)
                break
            except ValueError:
                continue
        else:
            return {"ok": False, "age_days": -1, "warning": f"Cannot parse date: {data_date_str}"}
        
        age = (datetime.now() - dd).total_seconds() / 86400
        if age > max_days:
            return {"ok": False, "age_days": round(age, 1), 
                    "warning": f"{label} is {age:.0f} days old (max: {max_days}d)"}
        return {"ok": True, "age_days": round(age, 1), "warning": None}
    except Exception as e:
        return {"ok": False, "age_days": -1, "warning": f"Staleness check error: {e}"}


# ── Verification Reminder ────────────────────────────────────────────

def get_verification_reminders() -> list:
    """Return list of data sources that need re-verification."""
    reminders = []
    for key, src in DATA_SOURCES.items():
        if src["type"] == "static":
            last_v = src.get("last_verified")
            if not last_v:
                reminders.append(f"⚠️ {key}: NEVER VERIFIED")
                continue
            try:
                days = (datetime.now() - datetime.strptime(last_v, "%Y-%m-%d")).days
                if days > 30:
                    reminders.append(f"🟠 {key}: last verified {days}d ago — re-verify needed")
                elif days > 7:
                    reminders.append(f"🟡 {key}: last verified {days}d ago — consider re-verifying")
            except ValueError:
                reminders.append(f"⚠️ {key}: invalid verification date")
    return reminders


if __name__ == "__main__":
    # Demo audit with no data
    auditor = audit_report_data()
    auditor.print_report()
    
    reminders = get_verification_reminders()
    if reminders:
        print("📋 Verification Reminders:")
        for r in reminders:
            print(f"  {r}")
