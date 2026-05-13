"""Data fetchers for all financial data sources."""
import os
import requests
import time
import logging
import functools
import pandas as pd
from datetime import datetime, timedelta
from config import FRED_API_KEY, POLYGON_API_KEY, FRED_SERIES, TREASURY_API_BASE

logger = logging.getLogger(__name__)


def retry_on_failure(max_retries=2, delay=2.0, backoff=2.0, exceptions=(requests.RequestException,)):
    """Decorator that retries a function on transient failures with exponential backoff."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            wait = delay
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exc = e
                    if attempt < max_retries:
                        logger.warning("%s failed (attempt %d/%d): %s — retrying in %.1fs",
                                       func.__name__, attempt + 1, max_retries + 1, e, wait)
                        time.sleep(wait)
                        wait *= backoff
                    else:
                        logger.error("%s failed after %d attempts: %s", func.__name__, max_retries + 1, e)
            raise last_exc
        return wrapper
    return decorator


class TTLCache:
    """Simple in-memory TTL cache to avoid redundant API calls during a briefing run."""

    def __init__(self, default_ttl=300):
        self._cache = {}
        self._default_ttl = default_ttl

    def get(self, key):
        if key in self._cache:
            value, expiry = self._cache[key]
            if time.time() < expiry:
                logger.debug("Cache hit: %s", key)
                return value
            del self._cache[key]
        return None

    def set(self, key, value, ttl=None):
        ttl = ttl or self._default_ttl
        self._cache[key] = (value, time.time() + ttl)

    def clear(self):
        self._cache.clear()


_api_cache = TTLCache(default_ttl=300)  # 5-minute default


# ── FRED API ─────────────────────────────────────────────────────────────

def fred_fetch(series_id: str, start: str = None, end: str = None) -> pd.DataFrame:
    """Fetch a FRED time series. Returns DataFrame with date index and 'value' column."""
    if not FRED_API_KEY or FRED_API_KEY == "YOUR_KEY_HERE":
        logger.warning("FRED API key not set. Skipping %s.", series_id)
        return pd.DataFrame()

    if not start:
        start = (datetime.now() - timedelta(days=365 * 2)).strftime("%Y-%m-%d")
    if not end:
        end = datetime.now().strftime("%Y-%m-%d")

    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "observation_start": start,
        "observation_end": end,
        "sort_order": "desc",
    }
    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        data = r.json().get("observations", [])
        if not data:
            return pd.DataFrame()
        df = pd.DataFrame(data)
        df["date"] = pd.to_datetime(df["date"])
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        df = df[["date", "value"]].dropna().set_index("date").sort_index()
        return df
    except requests.RequestException as e:
        logger.warning("FRED fetch error for %s: %s", series_id, e)
        return pd.DataFrame()
    except (KeyError, ValueError) as e:
        logger.warning("FRED parse error for %s: %s", series_id, e)
        return pd.DataFrame()


def fred_latest(series_id: str) -> float | None:
    """Get the most recent value for a FRED series. Cached for 60 minutes."""
    cache_key = f"fred_latest:{series_id}"
    cached = _api_cache.get(cache_key)
    if cached is not None:
        return cached
    df = fred_fetch(series_id)
    if df.empty:
        return None
    value = float(df["value"].iloc[-1])
    _api_cache.set(cache_key, value, ttl=3600)  # FRED data changes daily at most
    return value


def fetch_macro_liquidity() -> dict:
    """Fetch all components needed for net liquidity calculation.
    Net Liquidity = Fed Assets - TGA - Reverse Repo
    """
    result = {}
    for name, series_id in [
        ("fed_assets", FRED_SERIES["fed_assets"]),
        ("tga_balance", FRED_SERIES["tga_balance"]),
        ("rrp", FRED_SERIES["rrp"]),
        ("sofr", FRED_SERIES["sofr"]),
    ]:
        val = fred_latest(series_id)
        result[name] = val

    # Calculate net liquidity if all components available
    if all(result.get(k) is not None for k in ["fed_assets", "tga_balance", "rrp"]):
        # Fed assets in millions, TGA in millions, RRP in billions → normalize
        result["net_liquidity"] = result["fed_assets"] - result["tga_balance"] - result["rrp"]
    else:
        result["net_liquidity"] = None

    return result


def fetch_net_liquidity_history(days: int = 90) -> pd.DataFrame:
    """Fetch historical net liquidity for trend analysis."""
    start = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    fed = fred_fetch(FRED_SERIES["fed_assets"], start=start)
    tga = fred_fetch(FRED_SERIES["tga_balance"], start=start)
    rrp = fred_fetch(FRED_SERIES["rrp"], start=start)

    if fed.empty or tga.empty or rrp.empty:
        return pd.DataFrame()

    # Resample all to daily and forward-fill (fed/tga are weekly, rrp is daily)
    fed = fed.resample("D").ffill()
    tga = tga.resample("D").ffill()
    rrp = rrp.resample("D").ffill()

    combined = pd.DataFrame({
        "fed_assets": fed["value"],
        "tga": tga["value"],
        "rrp": rrp["value"],
    }).dropna()
    combined["net_liquidity"] = combined["fed_assets"] - combined["tga"] - combined["rrp"]
    return combined


# ── Treasury Fiscal Data API (TGA - no auth needed) ─────────────────────

def fetch_tga_balance() -> dict | None:
    """Fetch latest TGA balance from Treasury Fiscal Data API (no auth).
    Uses the Operating Cash Balance table from the Daily Treasury Statement.
    Note: Since April 2022, close_today_bal is null; the actual balance is in open_today_bal
    for the "Closing Balance" row.
    """
    url = f"{TREASURY_API_BASE}/v1/accounting/dts/operating_cash_balance"
    params = {
        "sort": "-record_date",
        "page[size]": 20,
    }
    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        data = r.json().get("data", [])
        for row in data:
            if "Closing Balance" in row.get("account_type", ""):
                bal_str = row.get("open_today_bal", "0")
                if bal_str and bal_str != "null":
                    balance = float(bal_str)
                    return {
                        "date": row.get("record_date"),
                        "balance_millions": balance,
                        "balance_billions": round(balance / 1000, 2),
                    }
    except requests.RequestException as e:
        logger.warning("Treasury API error: %s", e)
    return None


# ── Polygon.io (Starter plan — 5 calls/min) ────────────────────────────

_polygon_calls = []  # timestamps of recent calls

def _polygon_rate_limit():
    """Enforce Starter plan rate limit: max 5 calls per 60s window."""
    global _polygon_calls
    now = time.time()
    # Remove calls older than 60s
    _polygon_calls = [t for t in _polygon_calls if now - t < 60]
    if len(_polygon_calls) >= 5:
        wait = 60 - (now - _polygon_calls[0]) + 0.5
        if wait > 0:
            logger.info("Polygon rate limit: waiting %.0fs...", wait)
            time.sleep(wait)
    _polygon_calls.append(time.time())


def polygon_fetch_price(ticker: str, days: int = 30) -> pd.DataFrame:
    """Fetch daily OHLCV from Polygon.io (Starter plan)."""
    if not POLYGON_API_KEY:
        logger.warning("Polygon API key not set.")
        return pd.DataFrame()

    _polygon_rate_limit()

    end = datetime.now().strftime("%Y-%m-%d")
    start = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{start}/{end}"
    params = {"apiKey": POLYGON_API_KEY, "adjusted": "true", "sort": "asc", "limit": 5000}

    try:
        r = requests.get(url, params=params, timeout=15)
        if r.status_code == 429:
            logger.info("Rate limited on %s, waiting 60s...", ticker)
            time.sleep(60)
            _polygon_calls.clear()
            _polygon_rate_limit()
            r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        results = r.json().get("results", [])
        if not results:
            return pd.DataFrame()
        df = pd.DataFrame(results)
        df["date"] = pd.to_datetime(df["t"], unit="ms")
        df = df.rename(columns={"o": "Open", "h": "High", "l": "Low", "c": "Close", "v": "Volume"})
        df = df[["date", "Open", "High", "Low", "Close", "Volume"]].set_index("date")
        return df
    except requests.RequestException as e:
        logger.warning("Polygon fetch error for %s: %s", ticker, e)
        return pd.DataFrame()
    except (KeyError, ValueError) as e:
        logger.warning("Polygon parse error for %s: %s", ticker, e)
        return pd.DataFrame()


def fetch_usdjpy(days: int = 30) -> pd.DataFrame:
    """Fetch USD/JPY exchange rate from Polygon."""
    return polygon_fetch_price("C:USDJPY", days)


def fetch_sp500(days: int = 30) -> pd.DataFrame:
    """Fetch S&P 500 (SPY) data from Polygon."""
    return polygon_fetch_price("SPY", days)


# ── Public Data Scrapers (no auth) ──────────────────────────────────────

def fetch_fear_greed() -> dict | None:
    """Fetch CNN Fear & Greed Index (public API)."""
    # Try multiple known endpoints (CNN changes these periodically)
    endpoints = [
        "https://production.dataviz.cnn.io/index/fearandgreed/graphdata",
        f"https://production.dataviz.cnn.io/index/fearandgreed/graphdata/{datetime.now().strftime('%Y-%m-%d')}",
    ]
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Referer": "https://www.cnn.com/markets/fear-and-greed",
    }
    for url in endpoints:
        try:
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code != 200:
                continue
            data = r.json()
            score = data.get("fear_and_greed", {}).get("score")
            rating = data.get("fear_and_greed", {}).get("rating")
            if score is not None:
                return {"score": round(float(score), 1), "rating": rating}
        except Exception:
            continue

    # Fallback: try alternative-me crypto fear & greed (different market but useful)
    try:
        r = requests.get("https://api.alternative.me/fng/?limit=1", timeout=10)
        if r.status_code == 200:
            data = r.json().get("data", [{}])[0]
            return {
                "score": float(data.get("value", 0)),
                "rating": data.get("value_classification", "Unknown"),
                "source": "crypto (alternative.me)",
            }
    except Exception:
        pass

    logger.warning("Fear & Greed: all endpoints failed")
    return None


def fetch_move_index() -> dict | None:
    """Fetch ICE BofA MOVE Index (bond volatility) from Yahoo Finance. No auth needed."""
    url = "https://query1.finance.yahoo.com/v8/finance/chart/%5EMOVE"
    params = {"range": "5d", "interval": "1d"}
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
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
                "week_change_pct": round((current / prev - 1) * 100, 2) if prev else 0,
            }
    except Exception as e:
        logger.warning("MOVE index fetch error: %s", e)
    return None


def fetch_treasury_yields() -> dict:
    """Fetch current US Treasury yields from FRED."""
    yields = {}
    for name, series_id in [("us2y", "DGS2"), ("us10y", "DGS10")]:
        val = fred_latest(series_id)
        if val is not None:
            yields[name] = val
    if "us2y" in yields and "us10y" in yields:
        yields["spread_2s10s"] = round(yields["us10y"] - yields["us2y"], 3)
    return yields


# ── Watchlist Configuration ────────────────────────────────────────────

# Default watchlist for daily briefing / sentiment / TA scans.
# Override at runtime via WATCHLIST="NVDA,AAPL,..." env var, or by passing
# `watchlist=...` to the consumer functions.
WATCHLIST_CONFIG = {
    "NVDA":   ("NASDAQ", "america"),
    "AAPL":   ("NASDAQ", "america"),
    "MSFT":   ("NASDAQ", "america"),
    "GOOGL":  ("NASDAQ", "america"),
    "META":   ("NASDAQ", "america"),
    "TSLA":   ("NASDAQ", "america"),
    "AMZN":   ("NASDAQ", "america"),
    "SPY":    ("NYSE", "america"),
    "QQQ":    ("NASDAQ", "america"),
    "BTCUSD": ("BITSTAMP", "crypto"),
}

# Env-driven override.
_env_wl = os.environ.get("WATCHLIST", "").strip()
if _env_wl:
    _exchanges = dict(WATCHLIST_CONFIG)
    WATCHLIST_CONFIG = {
        sym.strip().upper(): _exchanges.get(sym.strip().upper(), ("NASDAQ", "america"))
        for sym in _env_wl.split(",") if sym.strip()
    }

# Polygon ticker mapping (some differ from display symbols)
POLYGON_TICKER_MAP = {
    "BTCUSD": "X:BTCUSD",
}


# ── Polygon-based Technical Analysis (Starter plan) ───────────────────

def compute_indicators(df: pd.DataFrame) -> dict | None:
    """Compute technical indicators from OHLCV DataFrame using pandas_ta."""
    if df.empty or len(df) < 30:
        return None

    # Validate required columns exist
    required_cols = {"Close", "High", "Low"}
    if not required_cols.issubset(df.columns):
        logger.warning("compute_indicators: missing columns %s", required_cols - set(df.columns))
        return None

    # Drop rows where all OHLC are NaN (bad data)
    df = df.dropna(subset=["Close", "High", "Low"])
    if len(df) < 30:
        return None

    try:
        import pandas_ta as ta

        close = df["Close"]
        high = df["High"]
        low = df["Low"]

        rsi = ta.rsi(close, length=14)
        macd_df = ta.macd(close)
        adx_df = ta.adx(high, low, close, length=14)
        ema20 = ta.ema(close, length=20)
        sma50 = ta.sma(close, length=50)
        sma200 = ta.sma(close, length=200)
        bb = ta.bbands(close, length=20, std=2)
        atr = ta.atr(high, low, close, length=14)

        current_close = float(close.iloc[-1])
        current_rsi = float(rsi.iloc[-1]) if rsi is not None and not rsi.empty else 0
        current_adx = float(adx_df.iloc[-1, 0]) if adx_df is not None and not adx_df.empty else 0
        current_macd = float(macd_df.iloc[-1, 0]) if macd_df is not None and not macd_df.empty else 0
        macd_signal = float(macd_df.iloc[-1, 1]) if macd_df is not None and len(macd_df.columns) > 1 else 0
        current_ema20 = float(ema20.iloc[-1]) if ema20 is not None and not ema20.empty else 0
        current_sma50 = float(sma50.iloc[-1]) if sma50 is not None and not sma50.empty else 0
        current_sma200 = float(sma200.iloc[-1]) if sma200 is not None and not sma200.empty else 0
        current_atr = float(atr.iloc[-1]) if atr is not None and not atr.empty else 0

        bb_upper = float(bb.iloc[-1, 0]) if bb is not None and not bb.empty else 0
        bb_lower = float(bb.iloc[-1, 2]) if bb is not None and len(bb.columns) > 2 else 0

        # Generate recommendation based on multiple signals
        buy_signals = 0
        sell_signals = 0
        total_signals = 0

        # RSI
        if current_rsi < 30: buy_signals += 2
        elif current_rsi < 40: buy_signals += 1
        elif current_rsi > 70: sell_signals += 2
        elif current_rsi > 60: sell_signals += 1
        total_signals += 2

        # MACD vs signal line
        if current_macd > macd_signal: buy_signals += 1
        else: sell_signals += 1
        total_signals += 1

        # Price vs EMAs/SMAs
        if current_close > current_ema20: buy_signals += 1
        else: sell_signals += 1
        if current_close > current_sma50: buy_signals += 1
        else: sell_signals += 1
        if current_sma200 and current_close > current_sma200: buy_signals += 1
        else: sell_signals += 1
        total_signals += 3

        # EMA20 vs SMA50 (golden/death cross proxy)
        if current_ema20 > current_sma50: buy_signals += 1
        else: sell_signals += 1
        total_signals += 1

        # Bollinger Band position
        if current_close < bb_lower: buy_signals += 1
        elif current_close > bb_upper: sell_signals += 1
        total_signals += 1

        # Determine recommendation
        buy_pct = buy_signals / total_signals if total_signals else 0.5
        if buy_pct >= 0.75:
            rec = "STRONG_BUY"
        elif buy_pct >= 0.55:
            rec = "BUY"
        elif buy_pct <= 0.25:
            rec = "STRONG_SELL"
        elif buy_pct <= 0.45:
            rec = "SELL"
        else:
            rec = "NEUTRAL"

        return {
            "recommendation": rec,
            "buy": buy_signals,
            "sell": sell_signals,
            "neutral": total_signals - buy_signals - sell_signals,
            "close": round(current_close, 2),
            "rsi": round(current_rsi, 1),
            "adx": round(current_adx, 1),
            "macd": round(current_macd, 3),
            "ema20": round(current_ema20, 2),
            "sma50": round(current_sma50, 2),
            "sma200": round(current_sma200, 2),
            "vs_sma200_pct": round((current_close / current_sma200 - 1) * 100, 1) if current_sma200 else None,
            "bb_upper": round(bb_upper, 2),
            "bb_lower": round(bb_lower, 2),
            "atr": round(current_atr, 2),
            "volume": int(df["Volume"].iloc[-1]) if "Volume" in df.columns else 0,
        }
    except Exception as e:
        logger.warning("Indicator computation error: %s", e)
        return None


_YF_TICKER_MAP = {"BTCUSD": "BTC-USD"}

def _yf_fetch_one(symbol: str) -> tuple[str, dict | None]:
    try:
        import yfinance as yf
        yf_ticker = _YF_TICKER_MAP.get(symbol, symbol)
        df = yf.Ticker(yf_ticker).history(period="1y", interval="1d", auto_adjust=True)
        if df is None or df.empty:
            return symbol, None
        df = df.rename(columns=str.capitalize)
        df.index = df.index.tz_localize(None) if df.index.tz is not None else df.index
        return symbol, compute_indicators(df)
    except Exception as e:
        logger.warning("yfinance TA error for %s: %s", symbol, e)
        return symbol, None


def fetch_watchlist_ta(watchlist: dict | None = None) -> dict:
    """Fetch OHLCV from yfinance (parallel) and compute TA indicators.

    Switched from Polygon to yfinance: free, no rate limit, daily data is fine
    for SMA/RSI/ADX/etc on mega-cap tickers. Falls back to Polygon per-symbol
    on failure.
    """
    from concurrent.futures import ThreadPoolExecutor

    if watchlist is None:
        watchlist = WATCHLIST_CONFIG

    results: dict = {}
    symbols = list(watchlist)
    with ThreadPoolExecutor(max_workers=10) as ex:
        for sym, ind in ex.map(_yf_fetch_one, symbols):
            results[sym] = ind

    # Fallback to Polygon for any that failed
    for sym in symbols:
        if results.get(sym) is None:
            logger.info("yfinance failed for %s, falling back to Polygon", sym)
            polygon_ticker = POLYGON_TICKER_MAP.get(sym, sym)
            df = polygon_fetch_price(polygon_ticker, days=350)
            if not df.empty:
                results[sym] = compute_indicators(df)
    return results


# ── TradingView Technical Analysis (free second opinion) ──────────────

def fetch_tv_analysis(symbol: str, exchange: str, screener: str,
                      interval: str = "1d") -> dict | None:
    """Fetch TradingView technical analysis for a single ticker."""
    try:
        from tradingview_ta import TA_Handler, Interval
        interval_map = {
            "1h": Interval.INTERVAL_1_HOUR,
            "4h": Interval.INTERVAL_4_HOURS,
            "1d": Interval.INTERVAL_1_DAY,
            "1w": Interval.INTERVAL_1_WEEK,
        }
        h = TA_Handler(
            symbol=symbol,
            screener=screener,
            exchange=exchange,
            interval=interval_map.get(interval, Interval.INTERVAL_1_DAY),
        )
        a = h.get_analysis()
        return {
            "recommendation": a.summary["RECOMMENDATION"],
            "buy": a.summary["BUY"],
            "sell": a.summary["SELL"],
            "neutral": a.summary["NEUTRAL"],
        }
    except Exception as e:
        logger.warning("TradingView TA error for %s: %s", symbol, e)
        return None


def fetch_watchlist_tv_consensus(watchlist: dict | None = None) -> dict:
    """Fetch TradingView consensus as a second opinion (free, no auth)."""
    if watchlist is None:
        watchlist = WATCHLIST_CONFIG
    results = {}
    for symbol, (exchange, screener) in watchlist.items():
        results[symbol] = fetch_tv_analysis(symbol, exchange, screener)
    return results


# ── Yahoo Finance Fundamentals (yfinance — no auth needed) ─────────────

def fetch_watchlist_fundamentals(symbols: list[str] | None = None) -> dict:
    """Fetch analyst targets, earnings dates, and recommendations via yfinance."""
    if symbols is None:
        symbols = [s for s in WATCHLIST_CONFIG if s != "BTCUSD"]
    try:
        import yfinance as yf
    except ImportError:
        logger.error("yfinance not installed. Run: pip3 install yfinance")
        return {}

    results = {}
    for sym in symbols:
        try:
            t = yf.Ticker(sym)
            info = t.info
            cal = t.calendar or {}
            earnings_dates = cal.get("Earnings Date", [])
            results[sym] = {
                "price": info.get("currentPrice"),
                "target_mean": info.get("targetMeanPrice"),
                "target_high": info.get("targetHighPrice"),
                "target_low": info.get("targetLowPrice"),
                "recommendation": info.get("recommendationKey"),
                "num_analysts": info.get("numberOfAnalystOpinions"),
                "earnings_date": str(earnings_dates[0]) if earnings_dates else None,
                "eps_estimate": cal.get("Earnings Average"),
                "revenue_estimate": cal.get("Revenue Average"),
                "forward_pe": info.get("forwardPE"),
                "peg_ratio": info.get("pegRatio"),
            }
        except Exception as e:
            logger.warning("yfinance error for %s: %s", sym, e)
            results[sym] = None
    return results


# ── Yahoo Finance Options Data ──────────────────────────────────────────

def fetch_spot_price(ticker: str) -> float | None:
    """Fetch current spot price via yfinance."""
    try:
        import yfinance as yf
        t = yf.Ticker(ticker)
        info = t.info
        price = info.get("currentPrice") or info.get("regularMarketPrice")
        return float(price) if price else None
    except Exception as e:
        logger.warning("Spot price fetch error for %s: %s", ticker, e)
        return None


def fetch_option_expirations(ticker: str) -> list[str]:
    """Fetch available option expiration dates via yfinance."""
    try:
        import yfinance as yf
        t = yf.Ticker(ticker)
        return list(t.options)
    except Exception as e:
        logger.warning("Options expirations fetch error for %s: %s", ticker, e)
        return []


def fetch_option_chain(ticker: str, expiry: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Fetch calls and puts for a specific expiration via yfinance.

    Returns (calls_df, puts_df) with NaN-filled for missing greeks.
    """
    try:
        import yfinance as yf
        t = yf.Ticker(ticker)
        chain = t.option_chain(expiry)
        calls = chain.calls.copy()
        puts = chain.puts.copy()
        # Ensure key columns exist, fill NaN
        for col in ["impliedVolatility", "openInterest", "volume", "lastPrice", "strike"]:
            if col not in calls.columns:
                calls[col] = float("nan")
            if col not in puts.columns:
                puts[col] = float("nan")
        calls["openInterest"] = calls["openInterest"].fillna(0)
        calls["volume"] = calls["volume"].fillna(0)
        puts["openInterest"] = puts["openInterest"].fillna(0)
        puts["volume"] = puts["volume"].fillna(0)
        return calls, puts
    except Exception as e:
        logger.warning("Option chain fetch error for %s %s: %s", ticker, expiry, e)
        return pd.DataFrame(), pd.DataFrame()


def polygon_option_prev_close(ticker: str, strike: float, option_type: str, expiry: str) -> float | None:
    """Fetch previous close for an options contract from Polygon.

    Args:
        ticker: Underlying ticker (e.g., "NVDA")
        strike: Strike price
        option_type: "call" or "put"
        expiry: Expiration date string (YYYY-MM-DD)

    Returns:
        Previous close price or None if unavailable.
    """
    if not POLYGON_API_KEY:
        return None

    _polygon_rate_limit()

    # Build Polygon options ticker: O:NVDA250321C00130000
    exp_date = expiry.replace("-", "")  # YYYYMMDD
    exp_short = exp_date[2:]  # YYMMDD
    cp = "C" if option_type.lower() == "call" else "P"
    strike_int = int(strike * 1000)  # Polygon uses strike * 1000, 8 digits
    opt_ticker = f"O:{ticker}{exp_short}{cp}{strike_int:08d}"

    url = f"https://api.polygon.io/v2/aggs/ticker/{opt_ticker}/prev"
    params = {"apiKey": POLYGON_API_KEY, "adjusted": "true"}

    try:
        r = requests.get(url, params=params, timeout=15)
        if r.status_code == 429:
            time.sleep(60)
            _polygon_calls.clear()
            _polygon_rate_limit()
            r = requests.get(url, params=params, timeout=15)
        if r.status_code != 200:
            return None
        results = r.json().get("results", [])
        if results:
            return float(results[0].get("c", 0))
    except Exception as e:
        logger.warning("Polygon option prev close error: %s", e)
    return None


# ── Master Data Fetcher ─────────────────────────────────────────────────

def fetch_all_macro() -> dict:
    """Fetch all macro data in one call. Returns a comprehensive dict."""
    logger.info("Fetching macro data...")
    data = {}

    # Net liquidity components
    logger.info("FRED: Fed assets, TGA, RRP, SOFR...")
    data["liquidity"] = fetch_macro_liquidity()

    # Treasury yields
    logger.info("FRED: Treasury yields...")
    data["yields"] = fetch_treasury_yields()

    # USD/JPY
    logger.info("Polygon: USD/JPY...")
    usdjpy = fetch_usdjpy(days=7)
    if not usdjpy.empty:
        data["usdjpy"] = {
            "current": round(float(usdjpy["Close"].iloc[-1]), 2),
            "week_change_pct": round(
                (float(usdjpy["Close"].iloc[-1]) / float(usdjpy["Close"].iloc[0]) - 1) * 100, 2
            ),
        }
    else:
        data["usdjpy"] = None

    # S&P 500
    logger.info("Polygon: S&P 500 (SPY)...")
    spy = fetch_sp500(days=7)
    if not spy.empty:
        data["sp500"] = {
            "current": round(float(spy["Close"].iloc[-1]), 2),
            "week_change_pct": round(
                (float(spy["Close"].iloc[-1]) / float(spy["Close"].iloc[0]) - 1) * 100, 2
            ),
        }
    else:
        data["sp500"] = None

    # Fear & Greed
    logger.info("CNN: Fear & Greed Index...")
    data["fear_greed"] = fetch_fear_greed()

    # MOVE index (bond volatility)
    logger.info("Yahoo: MOVE index...")
    data["move"] = fetch_move_index()

    # TGA from Treasury (backup/cross-check)
    logger.info("Treasury: TGA balance...")
    data["tga_direct"] = fetch_tga_balance()

    logger.info("Macro data fetch complete.")
    return data
