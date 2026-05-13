#!/usr/bin/env python3
"""
Geopolitical & Market News Scanner
Pulls real headlines from RSS/news sources and categorizes by asset relevance.

Sources (no API key required):
- Google News RSS (multiple queries)
- Reuters RSS
- MarketWatch RSS

Categories:
- GEOPOLITICAL: Wars, sanctions, territorial disputes, Hormuz, Taiwan
- TRADE_POLICY: Tariffs, trade wars, sanctions, export controls
- CENTRAL_BANK: Fed, ECB, BOJ, PBOC decisions/speeches
- ENERGY: OPEC, oil supply, pipelines, Hormuz Strait
- CRYPTO_REGULATION: SEC, exchange regulation, CBDC
- MACRO_DATA: Jobs, GDP, inflation surprises
- FISCAL: Government spending, debt ceiling, stimulus

Output: list of categorized headlines with asset relevance scores
"""

import json
import os
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from html import unescape
import ssl

# Disable SSL verification for RSS feeds (some have cert issues)
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE


# ── Asset-Topic Mapping ──────────────────────────────────────────────
# Keywords that link news to specific assets

ASSET_KEYWORDS = {
    "S&P 500": [
        "wall street", "s&p", "stock market", "equities", "nasdaq", "dow jones",
        "earnings", "recession", "gdp", "employment", "jobs report", "consumer spending",
        "tech stocks", "mega cap", "market crash", "rally", "correction",
        "tariff", "trade war", "sanctions",
    ],
    "Nasdaq 100": [
        "tech", "ai", "artificial intelligence", "semiconductor", "nvidia", "apple",
        "google", "microsoft", "meta", "amazon", "tesla", "chip", "antitrust",
        "mag-7", "magnificent seven", "ai bubble",
    ],
    "Gold": [
        "gold", "safe haven", "central bank buying", "geopolitical", "war",
        "inflation", "real rates", "dollar weakness", "de-dollarization",
        "treasury", "debt", "crisis", "iran", "middle east", "nuclear",
    ],
    "Crude Oil": [
        "oil", "crude", "opec", "hormuz", "iran", "saudi", "pipeline",
        "energy", "petroleum", "eia", "drilling", "shale", "refinery",
        "middle east", "strait", "shipping", "tanker", "houthi",
        "russia", "ukraine", "sanctions", "lng", "natural gas",
    ],
    "Euro FX": [
        "euro", "ecb", "lagarde", "europe", "eu", "eurozone",
        "dollar", "dxy", "forex", "currency", "rate differential",
        "european", "germany", "france", "trade deficit",
        "tariff", "trade war",
    ],
    "Bitcoin": [
        "bitcoin", "crypto", "btc", "ethereum", "digital asset",
        "sec", "regulation", "exchange", "stablecoin", "cbdc",
        "coinbase", "binance", "defi", "etf",
    ],
}

# Geopolitical hotspot patterns — these get HIGH impact scores
GEO_HOTSPOTS = {
    "hormuz": {
        "keywords": ["hormuz", "strait of hormuz", "persian gulf", "iran navy", "iran strait"],
        "impact": "CRITICAL",
        "assets": ["Crude Oil", "Gold"],
        "context_en": "Hormuz Strait — 20% of global oil transits through here. Any disruption = immediate oil spike + gold bid.",
        "context_cn": "霍尔木兹海峡——全球20%石油经此运输。任何中断=油价立即飙升+黄金受益。",
    },
    "iran": {
        "keywords": ["iran", "tehran", "iranian", "irgc", "nuclear deal", "jcpoa"],
        "impact": "HIGH",
        "assets": ["Crude Oil", "Gold"],
        "context_en": "Iran tensions — risk of Hormuz disruption, sanctions escalation, or military confrontation.",
        "context_cn": "伊朗紧张局势——存在霍尔木兹中断、制裁升级或军事对抗风险。",
    },
    "taiwan": {
        "keywords": ["taiwan", "taipei", "tsmc", "taiwan strait", "china military", "pla"],
        "impact": "CRITICAL",
        "assets": ["S&P 500", "Nasdaq 100", "Gold"],
        "context_en": "Taiwan Strait — semiconductor supply chain risk + potential US-China military escalation.",
        "context_cn": "台湾海峡——半导体供应链风险+潜在中美军事升级。",
    },
    "ukraine_russia": {
        "keywords": ["ukraine", "russia", "kyiv", "moscow", "nato", "crimea", "zelensky", "putin"],
        "impact": "HIGH",
        "assets": ["Crude Oil", "Gold", "Euro FX"],
        "context_en": "Russia-Ukraine — energy supply risk, European security, sanctions impact.",
        "context_cn": "俄乌冲突——能源供应风险、欧洲安全、制裁影响。",
    },
    "trade_war": {
        "keywords": ["tariff", "trade war", "trade deal", "import duty", "export ban", "chip ban", "trade deficit"],
        "impact": "HIGH",
        "assets": ["S&P 500", "Nasdaq 100", "Euro FX"],
        "context_en": "Trade policy — tariffs and export controls directly impact corporate earnings and FX.",
        "context_cn": "贸易政策——关税和出口管制直接影响企业盈利和汇率。",
    },
    "middle_east": {
        "keywords": ["middle east", "israel", "gaza", "hamas", "hezbollah", "lebanon", "syria", "red sea", "houthi", "yemen"],
        "impact": "HIGH",
        "assets": ["Crude Oil", "Gold"],
        "context_en": "Middle East escalation — shipping disruption risk, oil supply premium, safe-haven flows.",
        "context_cn": "中东升级——航运中断风险、石油供应溢价、避险资金流入。",
    },
    "debt_ceiling": {
        "keywords": ["debt ceiling", "government shutdown", "treasury", "fiscal cliff", "us default"],
        "impact": "HIGH",
        "assets": ["S&P 500", "Gold", "Bitcoin"],
        "context_en": "US fiscal risk — debt ceiling/shutdown impacts treasury markets, dollar confidence.",
        "context_cn": "美国财政风险——债务上限/关门影响国债市场和美元信心。",
    },
}

# RSS feed sources
RSS_FEEDS = [
    # Google News — targeted queries
    ("https://news.google.com/rss/search?q=iran+hormuz+oil+strait&hl=en-US&gl=US&ceid=US:en", "Google News (Hormuz)"),
    ("https://news.google.com/rss/search?q=tariff+trade+war+2026&hl=en-US&gl=US&ceid=US:en", "Google News (Trade)"),
    ("https://news.google.com/rss/search?q=federal+reserve+fomc+rate&hl=en-US&gl=US&ceid=US:en", "Google News (Fed)"),
    ("https://news.google.com/rss/search?q=geopolitical+risk+market&hl=en-US&gl=US&ceid=US:en", "Google News (Geopolitical)"),
    ("https://news.google.com/rss/search?q=opec+oil+supply+crude&hl=en-US&gl=US&ceid=US:en", "Google News (OPEC)"),
    ("https://news.google.com/rss/search?q=bitcoin+crypto+regulation&hl=en-US&gl=US&ceid=US:en", "Google News (Crypto)"),
    # MarketWatch
    ("https://feeds.marketwatch.com/marketwatch/topstories/", "MarketWatch"),
    # CNBC
    ("https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114", "CNBC"),
]


def _fetch_rss(url, source_name, max_age_hours=72):
    """Fetch and parse an RSS feed. Returns list of headline dicts."""
    headlines = []
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) COT-Report/1.0"
        })
        data = urllib.request.urlopen(req, timeout=10, context=SSL_CTX).read()
        root = ET.fromstring(data)
        
        # Handle both RSS and Atom formats
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        items = root.findall(".//item") or root.findall(".//atom:entry", ns)
        
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        
        for item in items[:15]:  # limit per feed
            title = item.findtext("title") or item.findtext("atom:title", "", ns)
            title = unescape(title).strip()
            if not title:
                continue
            
            # Parse date
            pub_date = item.findtext("pubDate") or item.findtext("atom:published", "", ns)
            parsed_date = None
            if pub_date:
                for fmt in [
                    "%a, %d %b %Y %H:%M:%S %Z",
                    "%a, %d %b %Y %H:%M:%S %z",
                    "%Y-%m-%dT%H:%M:%S%z",
                    "%Y-%m-%dT%H:%M:%SZ",
                ]:
                    try:
                        parsed_date = datetime.strptime(pub_date.strip(), fmt)
                        if parsed_date.tzinfo:
                            parsed_date = parsed_date.replace(tzinfo=None)
                        break
                    except ValueError:
                        continue
            
            # Skip old items
            if parsed_date and parsed_date < cutoff:
                continue
            
            link = item.findtext("link") or ""
            desc = item.findtext("description") or item.findtext("atom:summary", "", ns) or ""
            desc = unescape(re.sub(r'<[^>]+>', '', desc))[:200]
            
            headlines.append({
                "title": title,
                "source": source_name,
                "date": parsed_date.isoformat() if parsed_date else None,
                "link": link,
                "description": desc,
            })
    except Exception as e:
        pass  # Silently skip failed feeds
    
    return headlines


def _score_headline(headline):
    """Score a headline for asset relevance and geopolitical impact."""
    title_lower = (headline["title"] + " " + headline.get("description", "")).lower()
    
    result = {
        "title": headline["title"],
        "source": headline["source"],
        "date": headline.get("date"),
        "link": headline.get("link"),
        "assets": {},  # asset -> relevance score
        "hotspots": [],  # matched geopolitical hotspots
        "impact": "LOW",
    }
    
    # Check against asset keywords
    for asset, keywords in ASSET_KEYWORDS.items():
        score = 0
        matched_kw = []
        for kw in keywords:
            if kw in title_lower:
                score += 1
                matched_kw.append(kw)
        if score > 0:
            result["assets"][asset] = {"score": score, "keywords": matched_kw}
    
    # Check against geopolitical hotspots
    for hotspot_id, hotspot in GEO_HOTSPOTS.items():
        for kw in hotspot["keywords"]:
            if kw in title_lower:
                result["hotspots"].append({
                    "id": hotspot_id,
                    "impact": hotspot["impact"],
                    "context_en": hotspot["context_en"],
                    "context_cn": hotspot["context_cn"],
                    "assets": hotspot["assets"],
                })
                # Boost asset scores for hotspot-relevant assets
                for asset in hotspot["assets"]:
                    if asset not in result["assets"]:
                        result["assets"][asset] = {"score": 0, "keywords": []}
                    result["assets"][asset]["score"] += 3  # hotspot bonus
                break  # one match per hotspot is enough
    
    # Determine overall impact
    if any(h["impact"] == "CRITICAL" for h in result["hotspots"]):
        result["impact"] = "CRITICAL"
    elif any(h["impact"] == "HIGH" for h in result["hotspots"]):
        result["impact"] = "HIGH"
    elif sum(a["score"] for a in result["assets"].values()) >= 3:
        result["impact"] = "MEDIUM"
    
    return result


def scan_geopolitical_news(max_age_hours=72):
    """
    Scan all news sources, score headlines, and return categorized results.
    Returns: {
        "scan_date": str,
        "headline_count": int,
        "hotspot_alerts": [{"hotspot": str, "headlines": [...], "impact": str}],
        "by_asset": {"asset": [headlines]},
        "top_headlines": [top N by impact],
    }
    """
    print("  Scanning news feeds...")
    all_headlines = []
    for url, name in RSS_FEEDS:
        items = _fetch_rss(url, name, max_age_hours)
        all_headlines.extend(items)
        if items:
            print(f"    ✓ {name}: {len(items)} items")
    
    if not all_headlines:
        print("    ✗ No headlines fetched")
        return {"scan_date": datetime.now().isoformat(), "headline_count": 0,
                "hotspot_alerts": [], "by_asset": {}, "top_headlines": []}
    
    # Deduplicate by title similarity
    seen_titles = set()
    unique = []
    for h in all_headlines:
        # Simple dedup: first 50 chars lowercased
        key = h["title"][:50].lower()
        if key not in seen_titles:
            seen_titles.add(key)
            unique.append(h)
    
    # Score all headlines
    scored = [_score_headline(h) for h in unique]
    
    # Filter to only relevant ones (at least one asset match or hotspot)
    relevant = [s for s in scored if s["assets"] or s["hotspots"]]
    
    # Sort by impact
    impact_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    relevant.sort(key=lambda x: (impact_order.get(x["impact"], 3), -sum(a["score"] for a in x["assets"].values())))
    
    # Group by hotspot
    hotspot_alerts = {}
    for h in relevant:
        for hs in h["hotspots"]:
            hs_id = hs["id"]
            if hs_id not in hotspot_alerts:
                hotspot_alerts[hs_id] = {
                    "hotspot": hs_id,
                    "impact": hs["impact"],
                    "context_en": hs["context_en"],
                    "context_cn": hs["context_cn"],
                    "assets": hs["assets"],
                    "headlines": [],
                }
            hotspot_alerts[hs_id]["headlines"].append(h["title"])
    
    # Group by asset
    by_asset = {}
    for h in relevant:
        for asset in h["assets"]:
            if asset not in by_asset:
                by_asset[asset] = []
            by_asset[asset].append({
                "title": h["title"],
                "source": h["source"],
                "impact": h["impact"],
                "date": h.get("date"),
            })
    
    # Trim to top 5 per asset
    for asset in by_asset:
        by_asset[asset] = by_asset[asset][:5]
    
    result = {
        "scan_date": datetime.now().isoformat(),
        "headline_count": len(relevant),
        "total_scanned": len(unique),
        "hotspot_alerts": list(hotspot_alerts.values()),
        "by_asset": by_asset,
        "top_headlines": [{"title": h["title"], "impact": h["impact"], "source": h["source"],
                          "hotspots": [hs["id"] for hs in h["hotspots"]]} for h in relevant[:10]],
    }
    
    return result


def get_asset_news_context(asset, news_data, lang='en'):
    """Get news context paragraph for a specific asset."""
    if not news_data:
        return ""
    
    headlines = news_data.get("by_asset", {}).get(asset, [])
    hotspots = [h for h in news_data.get("hotspot_alerts", []) if asset in h.get("assets", [])]
    
    if not headlines and not hotspots:
        return ""
    
    if lang == 'cn':
        parts = []
        if hotspots:
            for hs in hotspots[:2]:
                parts.append(f'⚠️ <strong>{hs["hotspot"].upper()}:</strong> {hs["context_cn"]}')
                if hs["headlines"]:
                    parts.append(f'<em>"{hs["headlines"][0]}"</em>')
        elif headlines:
            for h in headlines[:3]:
                icon = "🔴" if h["impact"] in ("CRITICAL", "HIGH") else "🟡"
                parts.append(f'{icon} {h["title"]} <small>({h["source"]})</small>')
        
        if parts:
            return f'<p><strong>📰 相关新闻：</strong><br>{"<br>".join(parts)}</p>'
    else:
        parts = []
        if hotspots:
            for hs in hotspots[:2]:
                parts.append(f'⚠️ <strong>{hs["hotspot"].upper()}:</strong> {hs["context_en"]}')
                if hs["headlines"]:
                    parts.append(f'<em>"{hs["headlines"][0]}"</em>')
        elif headlines:
            for h in headlines[:3]:
                icon = "🔴" if h["impact"] in ("CRITICAL", "HIGH") else "🟡"
                parts.append(f'{icon} {h["title"]} <small>({h["source"]})</small>')
        
        if parts:
            return f'<p><strong>📰 In the news:</strong><br>{"<br>".join(parts)}</p>'
    
    return ""


def build_geopolitical_panel(news_data, lang='en'):
    """Build HTML panel summarizing geopolitical risk landscape."""
    if not news_data or news_data.get("headline_count", 0) == 0:
        return ""
    
    hotspots = news_data.get("hotspot_alerts", [])
    top = news_data.get("top_headlines", [])
    
    # Determine overall risk level
    if any(h["impact"] == "CRITICAL" for h in hotspots):
        risk = "ELEVATED"
        risk_color = "#DC2626"
        risk_cn = "升高"
    elif any(h["impact"] == "HIGH" for h in hotspots):
        risk = "HEIGHTENED"
        risk_color = "#D97706"
        risk_cn = "偏高"
    else:
        risk = "MODERATE"
        risk_color = "#16A34A"
        risk_cn = "适中"
    
    # Hotspot alerts
    hotspot_html = ""
    for hs in hotspots[:4]:
        impact_color = "#DC2626" if hs["impact"] == "CRITICAL" else "#D97706" if hs["impact"] == "HIGH" else "#666"
        hl_list = "".join(f'<li style="font-size:0.82em;color:#555">{h}</li>' for h in hs["headlines"][:2])
        
        if lang == 'cn':
            hotspot_html += f"""
            <div style="background:#FAF7F2;border-left:3px solid {impact_color};border-radius:6px;padding:10px 14px;margin-bottom:8px">
                <strong style="color:{impact_color}">⚠️ {hs["hotspot"].upper()}</strong> <small style="color:{impact_color}">({hs["impact"]})</small>
                <br><span style="font-size:0.85em">{hs["context_cn"]}</span>
                <ul style="margin:4px 0 0 16px;padding:0">{hl_list}</ul>
            </div>"""
        else:
            hotspot_html += f"""
            <div style="background:#FAF7F2;border-left:3px solid {impact_color};border-radius:6px;padding:10px 14px;margin-bottom:8px">
                <strong style="color:{impact_color}">⚠️ {hs["hotspot"].upper()}</strong> <small style="color:{impact_color}">({hs["impact"]})</small>
                <br><span style="font-size:0.85em">{hs["context_en"]}</span>
                <ul style="margin:4px 0 0 16px;padding:0">{hl_list}</ul>
            </div>"""
    
    # Top headlines
    headlines_html = ""
    for h in top[:6]:
        icon = "🔴" if h["impact"] in ("CRITICAL", "HIGH") else "🟡" if h["impact"] == "MEDIUM" else "⚪"
        hs_tags = " ".join(f'<span style="background:#FEF3C7;color:#92400E;font-size:0.7em;padding:1px 6px;border-radius:8px">{t}</span>' for t in h.get("hotspots", []))
        headlines_html += f'<div style="font-size:0.85em;padding:4px 0;border-bottom:1px solid #f0ede8">{icon} {h["title"]} <small style="color:#999">{h["source"]}</small> {hs_tags}</div>'
    
    scan_time = news_data.get("scan_date", "?")[:16]
    total = news_data.get("total_scanned", 0)
    relevant = news_data.get("headline_count", 0)
    
    return f"""
    <div style="background:white;border-radius:12px;padding:24px;margin-bottom:30px;box-shadow:0 2px 8px rgba(0,0,0,0.06);border-left:4px solid {risk_color}" id="geopolitical">
        <h3 style="margin-bottom:4px">
            <span class="lang-en">🌍 Geopolitical & News Risk</span>
            <span class="lang-cn" style="display:none">🌍 地缘政治与新闻风险</span>
        </h3>
        <p style="color:#888;font-size:0.78em;margin-bottom:14px">
            <span class="lang-en">Live scan of {total} headlines — {relevant} market-relevant. Updated {scan_time}</span>
            <span class="lang-cn" style="display:none">实时扫描{total}条新闻——{relevant}条与市场相关。更新于{scan_time}</span>
        </p>
        <div style="display:inline-block;padding:6px 16px;border-radius:20px;background:{risk_color}11;color:{risk_color};font-weight:700;font-size:0.95em;border:1px solid {risk_color}33;margin-bottom:14px">
            <span class="lang-en">Geopolitical Risk: {risk}</span>
            <span class="lang-cn" style="display:none">地缘风险：{risk_cn}</span>
        </div>
        {hotspot_html}
        <details style="margin-top:10px">
            <summary style="cursor:pointer;font-size:0.88em;color:#555;font-weight:600">
                <span class="lang-en">📋 Top Headlines ({relevant})</span>
                <span class="lang-cn" style="display:none">📋 热门头条 ({relevant})</span>
            </summary>
            <div style="margin-top:8px">{headlines_html}</div>
        </details>
    </div>"""


if __name__ == "__main__":
    data = scan_geopolitical_news()
    print(f"\n📊 Scan Results: {data['headline_count']} relevant / {data['total_scanned']} total")
    
    if data["hotspot_alerts"]:
        print("\n⚠️ HOTSPOT ALERTS:")
        for hs in data["hotspot_alerts"]:
            print(f"  [{hs['impact']}] {hs['hotspot'].upper()} — {len(hs['headlines'])} headlines")
            for h in hs["headlines"][:2]:
                print(f"    • {h}")
    
    print("\n📰 TOP HEADLINES:")
    for h in data["top_headlines"][:8]:
        icon = "🔴" if h["impact"] in ("CRITICAL", "HIGH") else "🟡"
        print(f"  {icon} [{h['impact']}] {h['title']} ({h['source']})")
    
    print("\n📊 BY ASSET:")
    for asset, headlines in data["by_asset"].items():
        print(f"  {asset}: {len(headlines)} headlines")
        for h in headlines[:2]:
            print(f"    • {h['title']}")
