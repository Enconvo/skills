"""Market Sentiment Scanner — composite sentiment scoring.

Sources:
- NAAIM Exposure Index (institutional positioning)
- CNN Fear & Greed Index (market-wide sentiment)
- VIX (equity volatility / fear gauge)
- Reddit (retail sentiment from WSB, r/stocks, r/investing)
- X/Twitter via bird (KOL sentiment)
- TradingView TA summary (technical consensus)

Output: Composite sentiment score with breakdown and contrarian signals.
"""
import subprocess
import json
import logging
import re
import requests
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from data_sources import fetch_fear_greed, fetch_move_index, fred_latest, fetch_watchlist_ta, fetch_watchlist_tv_consensus
from config import SENTIMENT

logger = logging.getLogger(__name__)


# ── NAAIM Exposure Index ────────────────────────────────────────────────

def fetch_naaim() -> dict | None:
    """Scrape NAAIM Exposure Index from naaim.org (public, weekly data)."""
    url = "https://www.naaim.org/programs/naaim-exposure-index/"
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.find("table")
        if not table:
            return None
        rows = table.find_all("tr")
        if len(rows) < 2:
            return None

        # First data row (most recent week)
        cells = [td.text.strip() for td in rows[1].find_all("td")]
        if len(cells) < 8:
            return None

        current = float(cells[1])
        # Previous week for trend
        prev = None
        if len(rows) >= 3:
            prev_cells = [td.text.strip() for td in rows[2].find_all("td")]
            if len(prev_cells) >= 2:
                prev = float(prev_cells[1])

        return {
            "date": cells[0],
            "exposure": current,
            "bearish": float(cells[2]),
            "q1": float(cells[3]),
            "median": float(cells[4]),
            "q3": float(cells[5]),
            "bullish": float(cells[6]),
            "prev_week": prev,
            "change": round(current - prev, 2) if prev else None,
        }
    except (requests.RequestException, ValueError, IndexError) as e:
        logger.warning("NAAIM scrape error: %s", e)
        return None


# ── VIX ─────────────────────────────────────────────────────────────────

def fetch_vix() -> dict | None:
    """Fetch VIX from Yahoo Finance."""
    try:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/%5EVIX"
        params = {"range": "5d", "interval": "1d"}
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, params=params, timeout=10)
        r.raise_for_status()
        result = r.json().get("chart", {}).get("result", [{}])[0]
        closes = result.get("indicators", {}).get("quote", [{}])[0].get("close", [])
        closes = [c for c in closes if c is not None]
        if closes:
            current = closes[-1]
            prev = closes[0] if len(closes) > 1 else current
            return {
                "current": round(current, 2),
                "week_change": round(current - prev, 2),
                "week_change_pct": round((current / prev - 1) * 100, 1) if prev else 0,
            }
    except (requests.RequestException, KeyError, IndexError) as e:
        logger.warning("VIX fetch error: %s", e)
    return None


# ── Reddit Sentiment ────────────────────────────────────────────────────

def fetch_reddit_sentiment(subreddits: list[str] | None = None, limit: int = 10) -> dict:
    """Fetch recent posts from finance subreddits and analyze sentiment.
    Uses the reddit skill's get_posts.py script.
    """
    if subreddits is None:
        subreddits = ["wallstreetbets", "stocks", "investing"]

    results = {}
    scripts_dir = None

    # Find the reddit skill scripts (resolve from home dir, not hardcoded path)
    import glob
    home = str(Path.home())
    matches = glob.glob(f"{home}/.claude/skills/reddit/scripts/get_posts.py")
    if not matches:
        matches = glob.glob(f"{home}/.claude/skills/*/scripts/get_posts.py")
    if matches:
        scripts_dir = matches[0]

    for sub in subreddits:
        try:
            if scripts_dir:
                # Use reddit skill script
                cmd = f"python3 {scripts_dir} {sub} --sort hot -n {limit} --json"
                proc = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=15)
                if proc.returncode == 0:
                    posts = json.loads(proc.stdout)
                    results[sub] = _analyze_reddit_posts(posts, sub)
                    continue

            # Fallback: direct Reddit JSON API
            url = f"https://www.reddit.com/r/{sub}/hot.json?limit={limit}"
            headers = {"User-Agent": "FinanceAgent/1.0"}
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                data = r.json().get("data", {}).get("children", [])
                posts = [p["data"] for p in data]
                results[sub] = _analyze_reddit_posts(posts, sub)
        except Exception as e:
            results[sub] = {"error": str(e)}

    return results


def _analyze_reddit_posts(posts: list, subreddit: str) -> dict:
    """Simple keyword-based sentiment analysis on Reddit posts."""
    bullish_words = {"bull", "bullish", "moon", "rocket", "buy", "calls", "long",
                     "breakout", "undervalued", "dip", "accumulate", "upside"}
    bearish_words = {"bear", "bearish", "crash", "puts", "short", "overvalued",
                     "dump", "bubble", "correction", "downside", "sell", "recession"}

    bull_count = 0
    bear_count = 0
    total = 0
    hot_tickers = {}
    top_posts = []

    for post in posts:
        title = post.get("title", "")
        selftext = post.get("selftext", "")
        score = post.get("score", 0) or post.get("ups", 0)
        text = f"{title} {selftext}".lower()
        total += 1

        # Count sentiment words
        for word in text.split():
            word = re.sub(r"[^a-z]", "", word)
            if word in bullish_words:
                bull_count += 1
            elif word in bearish_words:
                bear_count += 1

        # Extract tickers ($AAPL or all-caps 2-5 letter words)
        tickers = re.findall(r"\$([A-Z]{1,5})", title + " " + selftext)
        tickers += re.findall(r"\b([A-Z]{2,5})\b", title)
        for t in tickers:
            if t not in {"THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL",
                         "CAN", "HER", "WAS", "ONE", "OUR", "OUT", "HAS", "HIS",
                         "HOW", "ITS", "MAY", "NEW", "NOW", "OLD", "SEE", "WAY",
                         "WHO", "DID", "GET", "HAS", "HIM", "LET", "SAY", "SHE",
                         "TOO", "USE", "WSB", "IMO", "EDIT", "TLDR", "PSA", "FYI",
                         "CEO", "CFO", "IPO", "ETF", "GDP", "CPI", "FED", "SEC"}:
                hot_tickers[t] = hot_tickers.get(t, 0) + 1

        if score and score > 50:
            top_posts.append({"title": title[:100], "score": score})

    # Calculate sentiment ratio
    total_sentiment = bull_count + bear_count
    if total_sentiment > 0:
        bull_ratio = bull_count / total_sentiment
    else:
        bull_ratio = 0.5  # neutral

    # Sort tickers by mention count
    sorted_tickers = sorted(hot_tickers.items(), key=lambda x: -x[1])[:10]

    return {
        "posts_analyzed": total,
        "bull_signals": bull_count,
        "bear_signals": bear_count,
        "bull_ratio": round(bull_ratio, 2),
        "sentiment": "bullish" if bull_ratio > 0.6 else "bearish" if bull_ratio < 0.4 else "neutral",
        "hot_tickers": sorted_tickers,
        "top_posts": sorted(top_posts, key=lambda x: -x["score"])[:3],
    }


# ── TradingView Consensus ──────────────────────────────────────────────

def get_tv_consensus(tv_data: dict | None = None) -> dict:
    """Compute consensus from TradingView TA across watchlist."""
    if tv_data is None:
        tv_data = fetch_watchlist_ta()

    buys = 0
    sells = 0
    neutrals = 0
    total = 0

    for symbol, ta in tv_data.items():
        if ta is None:
            continue
        total += 1
        rec = ta["recommendation"]
        if "BUY" in rec:
            buys += 1
        elif "SELL" in rec:
            sells += 1
        else:
            neutrals += 1

    if total == 0:
        return {"consensus": "N/A", "buy_pct": 0, "sell_pct": 0}

    return {
        "total": total,
        "buys": buys,
        "sells": sells,
        "neutrals": neutrals,
        "buy_pct": round(buys / total * 100),
        "sell_pct": round(sells / total * 100),
        "consensus": "BULLISH" if buys > sells + neutrals else "BEARISH" if sells > buys + neutrals else "MIXED",
    }


# ── Composite Sentiment Score ───────────────────────────────────────────

def compute_composite_sentiment(naaim, fear_greed, vix, reddit, tv_consensus) -> dict:
    """Compute a weighted composite sentiment score (0-100).
    0 = extreme fear/bearish, 50 = neutral, 100 = extreme greed/bullish.

    Weights:
    - NAAIM: 25% (institutional)
    - Fear & Greed: 25% (market-wide)
    - VIX: 20% (volatility)
    - Reddit: 15% (retail)
    - TradingView TA: 15% (technical)
    """
    scores = {}
    weights = {}

    # NAAIM: 0-200 scale → normalize to 0-100
    if naaim:
        naaim_score = min(100, max(0, naaim["exposure"] / 2))
        scores["naaim"] = naaim_score
        weights["naaim"] = 0.25

    # Fear & Greed: already 0-100
    if fear_greed:
        scores["fear_greed"] = fear_greed["score"]
        weights["fear_greed"] = 0.25

    # VIX: invert (high VIX = fear = low score). VIX 10=euphoria(90), VIX 40=panic(10)
    if vix:
        vix_score = max(0, min(100, 100 - (vix["current"] - 10) * (90 / 30)))
        scores["vix"] = round(vix_score, 1)
        weights["vix"] = 0.20

    # Reddit: bull_ratio average across subreddits → 0-100
    if reddit:
        ratios = [v.get("bull_ratio", 0.5) for v in reddit.values() if isinstance(v, dict) and "bull_ratio" in v]
        if ratios:
            avg_ratio = sum(ratios) / len(ratios)
            scores["reddit"] = round(avg_ratio * 100, 1)
            weights["reddit"] = 0.15

    # TradingView consensus: buy_pct → 0-100
    if tv_consensus and tv_consensus.get("total", 0) > 0:
        scores["tv_consensus"] = tv_consensus["buy_pct"]
        weights["tv_consensus"] = 0.15

    # Weighted composite
    if not weights:
        return {"composite": 50, "label": "N/A", "components": {}}

    # Normalize weights to sum to 1
    total_weight = sum(weights.values())
    composite = sum(scores[k] * (weights[k] / total_weight) for k in scores)
    composite = round(composite, 1)

    if composite >= 75:
        label = "EXTREME GREED"
    elif composite >= 60:
        label = "GREED"
    elif composite >= 40:
        label = "NEUTRAL"
    elif composite >= 25:
        label = "FEAR"
    else:
        label = "EXTREME FEAR"

    return {
        "composite": composite,
        "label": label,
        "components": scores,
        "weights": weights,
    }


# ── Main Report ─────────────────────────────────────────────────────────

def run_sentiment_scan(prefetched: dict | None = None) -> tuple[str, dict]:
    """Full sentiment scan: fetch all sources → compute composite → format report.

    Args:
        prefetched: Optional dict with pre-fetched data to avoid duplicate API calls.
            Keys: 'fear_greed', 'move', 'tv_data' (from TradingView TA fetch).
            Missing keys will be fetched fresh.

    Returns:
        Tuple of (report_text, structured_data) for Notion sync.
    """
    if prefetched is None:
        prefetched = {}
    now = datetime.now()
    structured = {"date": now.strftime("%Y-%m-%d"), "type": "Sentiment Scan"}
    lines = []
    lines.append(f"╔{'═'*58}╗")
    lines.append(f"║  🧠 SENTIMENT SCANNER — {now.strftime('%A, %B %d, %Y')}       ║")
    lines.append(f"╚{'═'*58}╝")
    lines.append("")

    # Fetch data (reuse prefetched where available)
    logger.info("Running sentiment scan...")

    logger.info("Fetching NAAIM Exposure Index...")
    naaim = fetch_naaim()

    if "fear_greed" in prefetched:
        logger.info("CNN Fear & Greed (cached)")
        fear_greed = prefetched["fear_greed"]
    else:
        logger.info("Fetching CNN Fear & Greed...")
        fear_greed = fetch_fear_greed()

    logger.info("Fetching VIX...")
    vix = fetch_vix()

    if "move" in prefetched:
        logger.info("MOVE Index (cached)")
        move = prefetched["move"]
    else:
        logger.info("Fetching MOVE Index...")
        move = fetch_move_index()

    logger.info("Fetching Reddit sentiment (WSB, stocks, investing)...")
    reddit = fetch_reddit_sentiment()

    if "tv_data" in prefetched:
        logger.info("TA consensus (cached)")
        tv_data = prefetched["tv_data"]
    else:
        logger.info("Fetching TradingView consensus...")
        tv_data = fetch_watchlist_tv_consensus()
    tv_consensus = get_tv_consensus(tv_data)

    # Compute composite
    composite = compute_composite_sentiment(naaim, fear_greed, vix, reddit, tv_consensus)

    # ── Composite Score ──
    emoji = "🔴" if composite["composite"] > 75 else "🟢" if composite["composite"] < 25 else "🟡"
    lines.append(f"{'='*60}")
    lines.append(f"  {emoji} COMPOSITE SENTIMENT: {composite['composite']:.0f}/100 — {composite['label']}")
    lines.append(f"{'='*60}")
    lines.append("")

    # Component breakdown
    lines.append("📊 COMPONENT BREAKDOWN")
    comp = composite["components"]
    if "naaim" in comp:
        lines.append(f"  NAAIM Exposure (25%):     {comp['naaim']:.0f}/100  {'⚠️ HIGH' if comp['naaim'] > 80 else ''}")
    if "fear_greed" in comp:
        lines.append(f"  Fear & Greed (25%):       {comp['fear_greed']:.0f}/100  ({fear_greed['rating'] if fear_greed else ''})")
    if "vix" in comp:
        lines.append(f"  VIX Inverse (20%):        {comp['vix']:.0f}/100  (VIX: {vix['current'] if vix else 'N/A'})")
    if "reddit" in comp:
        lines.append(f"  Reddit Retail (15%):      {comp['reddit']:.0f}/100")
    if "tv_consensus" in comp:
        lines.append(f"  TradingView TA (15%):     {comp['tv_consensus']:.0f}/100  ({tv_consensus['consensus']})")
    lines.append("")

    # ── NAAIM Detail ──
    if naaim:
        lines.append("📈 NAAIM EXPOSURE INDEX")
        lines.append(f"  Current: {naaim['exposure']:.1f}  (date: {naaim['date']})")
        if naaim.get("prev_week"):
            lines.append(f"  Previous: {naaim['prev_week']:.1f}  (change: {naaim['change']:+.1f})")
        lines.append(f"  Range: {naaim['bearish']:.0f} (bearish) to {naaim['bullish']:.0f} (bullish)")
        if naaim["exposure"] > SENTIMENT["naaim_overbought"]:
            lines.append(f"  ⚠️  ABOVE {SENTIMENT['naaim_overbought']} — institutions heavily long, potential topping signal")
        lines.append("")

    # ── VIX + MOVE ──
    lines.append("📊 VOLATILITY")
    if vix:
        lines.append(f"  VIX:  {vix['current']} ({vix['week_change_pct']:+.1f}% 1w)")
    if move:
        lines.append(f"  MOVE: {move['current']} ({move['week_change_pct']:+.1f}% 1w)")
    lines.append("")

    # ── Reddit ──
    lines.append("💬 REDDIT SENTIMENT")
    for sub, data in reddit.items():
        if "error" in data:
            lines.append(f"  r/{sub}: Error — {data['error']}")
            continue
        lines.append(f"  r/{sub}: {data['sentiment'].upper()} (bull ratio: {data['bull_ratio']:.0%})")
        if data.get("hot_tickers"):
            tickers_str = ", ".join(f"{t}({c})" for t, c in data["hot_tickers"][:5])
            lines.append(f"    Hot tickers: {tickers_str}")
        if data.get("top_posts"):
            for p in data["top_posts"][:2]:
                lines.append(f"    📝 [{p['score']}↑] {p['title'][:70]}")
    lines.append("")

    # ── TradingView Consensus ──
    lines.append("📉 TRADINGVIEW TA CONSENSUS")
    lines.append(f"  {tv_consensus['consensus']}: {tv_consensus.get('buys',0)} buy / {tv_consensus.get('sells',0)} sell / {tv_consensus.get('neutrals',0)} neutral")
    lines.append("")

    # Populate structured data
    structured["sentiment_score"] = composite["composite"]
    structured["sentiment_label"] = composite["label"]
    structured["components"] = composite["components"]
    structured["naaim"] = naaim
    structured["vix"] = vix
    structured["move"] = move
    structured["fear_greed"] = fear_greed
    structured["tv_consensus"] = tv_consensus
    structured["reddit_summary"] = {
        sub: {"sentiment": d.get("sentiment"), "bull_ratio": d.get("bull_ratio")}
        for sub, d in reddit.items() if isinstance(d, dict) and "sentiment" in d
    }

    # ── Contrarian Signals ──
    lines.append("━" * 60)
    lines.append("  💡 CONTRARIAN SIGNALS")
    lines.append("━" * 60)
    signals = []
    if composite["composite"] > 75:
        signals.append("🔴 Sentiment extremely bullish — contrarian SELL zone")
    elif composite["composite"] < 25:
        signals.append("🟢 Sentiment extremely bearish — contrarian BUY zone")

    if naaim and naaim["exposure"] > 90:
        signals.append(f"🔴 NAAIM at {naaim['exposure']:.0f} — institutions max long, historically precedes pullbacks")
    elif naaim and naaim["exposure"] < 25:
        signals.append(f"🟢 NAAIM at {naaim['exposure']:.0f} — institutions very defensive, historically precedes rallies")

    if fear_greed and fear_greed["score"] > 80:
        signals.append(f"🔴 Fear & Greed at {fear_greed['score']:.0f} — extreme greed")
    elif fear_greed and fear_greed["score"] < 20:
        signals.append(f"🟢 Fear & Greed at {fear_greed['score']:.0f} — extreme fear")

    if vix and vix["current"] > 30:
        signals.append(f"🟢 VIX at {vix['current']:.1f} — panic levels, historically a buy zone")
    elif vix and vix["current"] < 12:
        signals.append(f"🔴 VIX at {vix['current']:.1f} — complacency, historically precedes spikes")

    if signals:
        for s in signals:
            lines.append(f"  {s}")
    else:
        lines.append("  No extreme contrarian signals at this time.")

    structured["contrarian_signals"] = signals
    structured["key_signals"] = "; ".join(signals) if signals else "No extreme contrarian signals"

    lines.append("")
    lines.append(f"Generated at {now.strftime('%H:%M:%S')} local time")
    lines.append(f"{'━'*60}")

    logger.info("Sentiment scan complete.")
    return "\n".join(lines), structured


if __name__ == "__main__":
    import sys
    import json as _json

    report, structured = run_sentiment_scan()

    if "--json" in sys.argv:
        print(_json.dumps(structured, indent=2, default=str))
    else:
        print(report)
