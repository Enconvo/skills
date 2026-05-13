"""FCN Portfolio Risk Checker.

Fetches live prices for all FCN underlyings and checks distance to strike.
Outputs risk status per note and flags any DANGER/WARNING positions.

Usage:
    python3 fcn_checker.py          # Human-readable report
    python3 fcn_checker.py --json   # Structured JSON for Notion
"""

import json
import sys
from calendar import monthrange
from datetime import datetime, timedelta

import yfinance as yf

# ── Redaction Mode ────────────────────────────────────────────────────────
REDACT = "--redact" in sys.argv

def _amt(amount):
    """Format amount, redacted if needed."""
    if REDACT:
        return "***"
    return f"${amount:,.0f}"

def _isin(isin):
    """Redact ISIN."""
    if REDACT:
        return isin[:4] + "****" + isin[-4:]
    return isin


def _obs_date_for_month(year, month, obs_day):
    """Get observation date for a given month, clamped to valid day.

    Adjusts weekends to next Monday (trading day).
    """
    max_day = monthrange(year, month)[1]
    day = min(obs_day, max_day)
    dt = datetime(year, month, day)
    # Shift weekends to next Monday
    weekday = dt.weekday()  # 0=Mon, 5=Sat, 6=Sun
    if weekday == 5:  # Saturday → Monday
        dt += timedelta(days=2)
    elif weekday == 6:  # Sunday → Monday
        dt += timedelta(days=1)
    return dt


def next_observation_date(today, expiry_str, issue_str=None):
    """Find the next monthly observation date from today.

    Observation day-of-month is derived from the expiry date.
    Returns (next_obs_date, days_until) or (None, None) if past expiry.
    """
    expiry = datetime.strptime(expiry_str, "%Y-%m-%d")
    obs_day = expiry.day  # monthly obs on same day as expiry

    # If note not yet issued, first obs is ~1 month after issue
    if issue_str:
        issue = datetime.strptime(issue_str, "%Y-%m-%d")
        if today < issue:
            # First observation is roughly 1 month after issue
            first_obs = _obs_date_for_month(
                issue.year + (issue.month // 12),
                (issue.month % 12) + 1,
                obs_day,
            )
            days_until = (first_obs - today).days
            return first_obs, days_until

    # Walk forward from current month to find next obs >= today
    year, month = today.year, today.month
    for _ in range(14):  # max 14 months ahead
        candidate = _obs_date_for_month(year, month, obs_day)
        if candidate.date() >= today.date() and candidate <= expiry:
            days_until = (candidate - today).days
            return candidate, days_until
        # Advance month
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1

    return None, None


def all_observation_dates(expiry_str, issue_str=None):
    """Generate all monthly observation dates for a note."""
    expiry = datetime.strptime(expiry_str, "%Y-%m-%d")
    obs_day = expiry.day
    dates = []

    # Start from issue + 1 month, or a reasonable lookback
    if issue_str:
        start = datetime.strptime(issue_str, "%Y-%m-%d")
    else:
        # Estimate: start ~18 months before expiry
        start = datetime(expiry.year - 1, expiry.month, 1)

    year, month = start.year, start.month
    # Advance 1 month from issue for first obs
    if month == 12:
        year += 1
        month = 1
    else:
        month += 1

    for _ in range(36):
        candidate = _obs_date_for_month(year, month, obs_day)
        if candidate > expiry:
            break
        dates.append(candidate)
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1

    return dates


# ── FCN Portfolio Definition ─────────────────────────────────────────────

# ── Portfolio data loaded from external JSON (not tracked in git) ──
import pathlib as _pathlib

def _validate_fcn_note(note, idx):
    """Validate required fields in a single FCN note. Returns list of error strings."""
    errors = []
    required = ["isin", "product", "amount", "coupon", "expiry", "underlyings"]
    for field in required:
        if field not in note:
            errors.append(f"FCN note #{idx}: missing required field '{field}'")
    if "underlyings" in note:
        if not isinstance(note["underlyings"], list) or not note["underlyings"]:
            errors.append(f"FCN note #{idx} ({note.get('isin', '?')}): 'underlyings' must be a non-empty list")
        else:
            for j, u in enumerate(note["underlyings"]):
                for uf in ["ticker", "strike", "call_price"]:
                    if uf not in u:
                        errors.append(f"FCN note #{idx}, underlying #{j}: missing '{uf}'")
                if u.get("strike", 1) <= 0:
                    errors.append(f"FCN note #{idx}, underlying #{j}: strike must be positive")
                if u.get("call_price", 1) <= 0:
                    errors.append(f"FCN note #{idx}, underlying #{j}: call_price must be positive")
    return errors


def _load_portfolio_data():
    """Load and validate portfolio positions from portfolio_data.json."""
    _data_file = _pathlib.Path(__file__).parent / "portfolio_data.json"
    if not _data_file.exists():
        msg = "Portfolio data file not found: " + str(_data_file)
        raise FileNotFoundError(msg)
    with open(_data_file) as _f:
        data = json.load(_f)

    # Validate structure
    if not isinstance(data, dict):
        raise ValueError("portfolio_data.json must be a JSON object")
    if "FCN_PORTFOLIO" not in data:
        raise ValueError("portfolio_data.json must contain 'FCN_PORTFOLIO' key")

    # Validate each FCN note
    all_errors = []
    for i, note in enumerate(data["FCN_PORTFOLIO"]):
        all_errors.extend(_validate_fcn_note(note, i))
    if all_errors:
        raise ValueError("Portfolio data validation errors:\n  " + "\n  ".join(all_errors))

    return data

_portfolio_data = _load_portfolio_data()
FCN_PORTFOLIO = _portfolio_data['FCN_PORTFOLIO']
FX_OPTIONS = _portfolio_data.get('FX_OPTIONS', [])
SELL_PUTS = _portfolio_data.get('SELL_PUTS', [])
ACCUMULATORS = _portfolio_data.get('ACCUMULATORS', [])



def fetch_live_prices(tickers: list[str]) -> dict[str, float]:
    """Fetch current prices for a list of tickers via yfinance."""
    prices = {}
    for t in tickers:
        try:
            info = yf.Ticker(t)
            price = info.fast_info.get("lastPrice") or info.fast_info.get("previousClose")
            if price:
                prices[t] = round(float(price), 2)
        except Exception:
            pass
    return prices


# ── Historical Price Checking (Memory Knockout Detection) ─────────────

def fetch_historical_daily(tickers: list[str], start_str: str) -> dict:
    """Fetch historical daily close data for tickers from start_str to today.

    Returns {ticker: pandas.DataFrame} with Date index and Close column.
    """
    import pandas as pd

    hist = {}
    end_str = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    for t in tickers:
        try:
            df = yf.download(t, start=start_str, end=end_str, interval="1d", progress=False)
            if df is not None and not df.empty:
                # Flatten multi-level columns from yfinance
                if isinstance(df.columns, pd.MultiIndex):
                    df = df.droplevel(1, axis=1)
                hist[t] = df
        except Exception:
            pass
    return hist


def _get_close_on_date(df, target_date: datetime) -> tuple[float | None, datetime | None]:
    """Look up closing price on target_date or nearest following trading day.

    Returns (close_price, actual_date) or (None, None).
    """
    import pandas as pd

    if df is None or df.empty:
        return None, None

    # Check target date and up to 3 following days (covers holidays)
    for offset in range(4):
        check = target_date + timedelta(days=offset)
        check_ts = pd.Timestamp(check.strftime("%Y-%m-%d"))
        try:
            if check_ts in df.index:
                close = float(df.loc[check_ts, "Close"])
                return close, check
        except (KeyError, TypeError):
            pass

    return None, None


def check_memory_knockouts(note: dict, hist_data: dict, today: datetime) -> dict:
    """Check which underlyings have been KO'd on past observation dates.

    Looks at every past observation date and checks if the closing price
    was >= the autocall trigger (call_price). Once KO'd, it stays KO'd
    (Memory feature).

    Returns {ticker: {"ko": bool, "ko_date": str|None, "ko_price": float|None,
                       "history": [(obs_date_str, close, above_call), ...]}}
    """
    result = {}
    obs_dates = all_observation_dates(note["expiry"], note.get("issue_date"))
    past_obs = [d for d in obs_dates if d.date() < today.date()]

    for u in note["underlyings"]:
        ticker = u["ticker"]
        call_price = u["call_price"]
        df = hist_data.get(ticker)
        ko_info = {"ko": False, "ko_date": None, "ko_price": None, "history": []}

        for obs_date in past_obs:
            close, actual = _get_close_on_date(df, obs_date)
            if close is not None:
                above = close >= call_price
                ko_info["history"].append((
                    obs_date.strftime("%Y-%m-%d"),
                    round(close, 2),
                    above,
                ))
                if above and not ko_info["ko"]:
                    ko_info["ko"] = True
                    ko_info["ko_date"] = obs_date.strftime("%Y-%m-%d")
                    ko_info["ko_price"] = round(close, 2)

        result[ticker] = ko_info

    return result


def check_fcn_portfolio(
    prices: dict[str, float] | None = None,
    skip_history: bool = False,
) -> tuple[str, dict]:
    """Check all FCN positions against live prices.

    Args:
        prices: Pre-fetched prices (or None to fetch live).
        skip_history: If True, skip historical observation-date checks.

    Returns (report_text, structured_json).
    """
    today = datetime.now()

    # Gather all unique tickers
    all_tickers = set()
    for note in FCN_PORTFOLIO:
        for u in note["underlyings"]:
            all_tickers.add(u["ticker"])
    for sp in SELL_PUTS:
        all_tickers.add(sp["ticker"])
    for acc in ACCUMULATORS:
        all_tickers.add(acc["ticker"])

    # Fetch prices if not provided
    if prices is None:
        print("  → Fetching live prices for FCN underlyings...", file=sys.stderr)
        prices = fetch_live_prices(sorted(all_tickers))

    # Fetch historical daily data for memory knockout detection
    hist_data = {}
    if not skip_history:
        # Find earliest issue date across active notes
        active_notes = [n for n in FCN_PORTFOLIO if not n.get("autocalled")]
        issue_dates = []
        for n in active_notes:
            if n.get("issue_date"):
                issue_dates.append(n["issue_date"])
        if issue_dates:
            earliest = min(issue_dates)
            fcn_tickers = set()
            for n in active_notes:
                for u in n["underlyings"]:
                    fcn_tickers.add(u["ticker"])
            print("  → Fetching historical data for memory knockout detection...", file=sys.stderr)
            hist_data = fetch_historical_daily(sorted(fcn_tickers), earliest)

    lines = []
    results = []
    total_exposure = 0
    danger_count = 0
    warning_count = 0
    danger_exposure = 0
    warning_exposure = 0

    # Structured section outputs
    fx_options_data = []
    sell_puts_data = []
    accumulators_data = []
    blockers_data = []

    lines.append("╔══════════════════════════════════════════════════════════╗")
    lines.append(f"║  FCN PORTFOLIO CHECK — {today.strftime('%A, %B %d, %Y'):<34}║")
    lines.append("╚══════════════════════════════════════════════════════════╝")
    lines.append("")

    autocalled_notes = []  # Track autocalled notes for summary

    for note in FCN_PORTFOLIO:
        expiry_date = datetime.strptime(note["expiry"], "%Y-%m-%d")
        days_to_expiry = (expiry_date - today).days

        # Skip autocalled notes
        if note.get("autocalled"):
            autocalled_notes.append(note)
            results.append({
                "isin": note["isin"],
                "account": note.get("account", ""),
                "product": note["product"],
                "amount": note["amount"],
                "coupon": note["coupon"],
                "expiry": note["expiry"],
                "days_to_expiry": days_to_expiry,
                "status": "AUTOCALLED",
                "autocalled_date": note["autocalled"],
                "worst_performer": None,
                "worst_distance_pct": None,
                "all_above_call": None,
            })
            continue

        # Skip expired notes
        if days_to_expiry < 0:
            status = "EXPIRED"
            worst_ticker = "N/A"
            worst_distance = 0
        else:
            # Find worst performer
            worst_distance = float("inf")
            worst_ticker = ""
            all_above_call = True
            underlying_details = []

            for u in note["underlyings"]:
                ticker = u["ticker"]
                strike = u["strike"]
                call_price = u["call_price"]
                current = prices.get(ticker, 0)

                if current == 0 or strike <= 0:
                    underlying_details.append(
                        f"    {ticker}: NO DATA (strike ${strike:.2f})"
                    )
                    continue

                distance_pct = ((current / strike) - 1) * 100
                vs_call = "above" if current >= call_price else "BELOW"

                if distance_pct < worst_distance:
                    worst_distance = distance_pct
                    worst_ticker = ticker

                if current < call_price:
                    all_above_call = False

                marker = ""
                if distance_pct < 0:
                    marker = " ⚠️  BELOW STRIKE"
                elif distance_pct < 20:
                    marker = " ⚠️  CLOSE"

                underlying_details.append(
                    f"    {ticker:<6} ${current:>8.2f}  strike ${strike:>8.2f}  "
                    f"({distance_pct:+.1f}%) call {vs_call}{marker}"
                )

            if worst_distance < 0:
                status = "DANGER"
                danger_count += 1
                danger_exposure += note["amount"]
            elif worst_distance < 20:
                status = "WARNING"
                warning_count += 1
                warning_exposure += note["amount"]
            else:
                status = "SAFE"

        total_exposure += note["amount"]

        # Status emoji
        emoji = {"DANGER": "🔴", "WARNING": "🟡", "SAFE": "🟢", "EXPIRED": "⚫"}.get(
            status, "⚪"
        )

        lines.append(f"  {emoji} {_isin(note['isin'])} — {status}")
        lines.append(f"     {note['product']}")
        lines.append(
            f"     {_amt(note['amount'])} | {note['coupon']}% coupon | "
            f"Exp: {note['expiry']} ({days_to_expiry}d)"
        )
        if status != "EXPIRED":
            lines.append(f"     Worst: {worst_ticker} at {worst_distance:+.1f}% from strike")
            for detail in underlying_details:
                lines.append(detail)
            if all_above_call and days_to_expiry > 0:
                lines.append("     ✅ All above call — may autocall")
        lines.append("")

        # Build underlying price details for JSON output
        underlying_json = []
        if status != "EXPIRED":
            for u in note["underlyings"]:
                ticker = u["ticker"]
                strike = u["strike"]
                call_price = u["call_price"]
                current = prices.get(ticker, 0)
                if current > 0:
                    distance_pct = ((current / strike) - 1) * 100
                    call_gap_pct = ((current / call_price) - 1) * 100
                    underlying_json.append({
                        "ticker": ticker,
                        "current": round(current, 2),
                        "strike": round(strike, 2),
                        "call_price": round(call_price, 2),
                        "distance_to_strike_pct": round(distance_pct, 1),
                        "distance_to_call_pct": round(call_gap_pct, 1),
                    })

        # Calculate next observation date for this note
        issue_str_note = note.get("issue_date")
        next_obs_note, days_to_obs_note = next_observation_date(today, note["expiry"], issue_str_note)

        results.append({
            "isin": note["isin"],
            "account": note.get("account", ""),
            "product": note["product"],
            "amount": note["amount"],
            "coupon": note["coupon"],
            "expiry": note["expiry"],
            "days_to_expiry": days_to_expiry,
            "status": status,
            "worst_performer": worst_ticker,
            "worst_distance_pct": round(worst_distance, 1) if worst_distance != float("inf") else None,
            "all_above_call": all_above_call if status != "EXPIRED" else None,
            "underlyings": underlying_json,
            "next_observation": next_obs_note.strftime("%Y-%m-%d") if next_obs_note else None,
            "days_to_next_obs": days_to_obs_note,
        })

    # ── Autocalled Notes Section ──
    if autocalled_notes:
        lines.append("╔══════════════════════════════════════════════════════════╗")
        lines.append("║  AUTOCALLED (REDEEMED EARLY)                           ║")
        lines.append("╚══════════════════════════════════════════════════════════╝")
        lines.append("")
        for note in autocalled_notes:
            lines.append(f"  ✅ {_isin(note['isin'])} — AUTOCALLED on {note['autocalled']}")
            lines.append(f"     {note['product']}")
            lines.append(f"     {_amt(note['amount'])} | {note['coupon']}% coupon | Original expiry: {note['expiry']}")
            tickers = ", ".join(u["ticker"] for u in note["underlyings"])
            if note.get("memory"):
                lines.append(f"     Memory note — underlyings KO'd independently: {tickers}")
            else:
                lines.append(f"     Underlyings: {tickers}")
            lines.append("")

    # ── FX Options Section ──
    if FX_OPTIONS:
        lines.append("╔══════════════════════════════════════════════════════════╗")
        lines.append("║  FX OPTIONS CHECK                                      ║")
        lines.append("╚══════════════════════════════════════════════════════════╝")
        lines.append("")

        for fx in FX_OPTIONS:
            expiry_date = datetime.strptime(fx["expiry"], "%Y-%m-%d")
            days_to_expiry = (expiry_date - today).days

            if days_to_expiry < 0:
                fx_status = "EXPIRED"
                spot_rate = 0
                distance_pct = 0
            else:
                # Fetch FX rate
                try:
                    yf_ticker = fx["yf_ticker"]
                    info = yf.Ticker(yf_ticker)
                    raw_price = info.fast_info.get("lastPrice") or info.fast_info.get("previousClose")
                    if raw_price and raw_price > 0:
                        # HKDUSD=X gives HKD per USD inverted — we need USDHKD
                        spot_rate = round(1.0 / float(raw_price), 4)
                    else:
                        spot_rate = 0
                except Exception:
                    spot_rate = 0

                if spot_rate == 0:
                    fx_status = "NO DATA"
                    distance_pct = 0
                else:
                    # For "above" direction: safe when spot > strike
                    if fx["direction"] == "above":
                        distance_pct = ((spot_rate / fx["strike"]) - 1) * 100
                    else:
                        distance_pct = ((fx["strike"] / spot_rate) - 1) * 100

                    if distance_pct < 0:
                        fx_status = "DANGER"
                        danger_count += 1
                        danger_exposure += fx["amount"]
                    elif distance_pct < 0.5:  # Very tight for FX (0.5%)
                        fx_status = "WARNING"
                        warning_count += 1
                        warning_exposure += fx["amount"]
                    else:
                        fx_status = "SAFE"

            total_exposure += fx["amount"]

            emoji = {"DANGER": "🔴", "WARNING": "🟡", "SAFE": "🟢", "EXPIRED": "⚫", "NO DATA": "⚪"}.get(
                fx_status, "⚪"
            )

            lines.append(f"  {emoji} {fx['ref']} — {fx_status}")
            lines.append(f"     {fx['product']}")
            lines.append(
                f"     {_amt(fx['amount'])} | {fx['premium_pct']}% premium | "
                f"Exp: {fx['expiry']} ({days_to_expiry}d)"
            )
            if fx_status not in ("EXPIRED", "NO DATA"):
                lines.append(
                    f"     {fx['pair']}: spot {spot_rate:.4f} vs strike {fx['strike']:.4f} "
                    f"({distance_pct:+.2f}%)"
                )
                lines.append(f"     {fx['notes']}")
            lines.append("")

            results.append({
                "ref": fx["ref"],
                "product": fx["product"],
                "amount": fx["amount"],
                "expiry": fx["expiry"],
                "days_to_expiry": days_to_expiry,
                "status": fx_status,
                "pair": fx["pair"],
                "spot_rate": spot_rate if spot_rate else None,
                "strike": fx["strike"],
                "distance_pct": round(distance_pct, 2) if fx_status not in ("EXPIRED", "NO DATA") else None,
            })

            fx_options_data.append({
                "id": fx["ref"],
                "description": fx["product"],
                "notional": fx["amount"],
                "spot_strike": f"{spot_rate:.4f} / {fx['strike']:.4f}" if spot_rate else f"- / {fx['strike']:.4f}",
                "buffer": f"{distance_pct:+.2f}%" if fx_status not in ("EXPIRED", "NO DATA") else "N/A",
                "expiry": fx["expiry"],
                "status": fx_status,
            })

    # ── Sell Puts Section ──
    if SELL_PUTS:
        lines.append("╔══════════════════════════════════════════════════════════╗")
        lines.append("║  SELL PUT POSITIONS                                    ║")
        lines.append("╚══════════════════════════════════════════════════════════╝")
        lines.append("")

        closed_puts = []
        for sp in SELL_PUTS:
            # Closed positions shown separately
            if sp.get("closed"):
                closed_puts.append(sp)
                continue

            expiry_date = datetime.strptime(sp["expiry"], "%Y-%m-%d")
            days_to_expiry = (expiry_date - today).days
            ticker = sp["ticker"]
            current = prices.get(ticker, 0) if prices else 0

            if days_to_expiry < 0:
                sp_status = "EXPIRED"
                distance_pct = 0
            elif current == 0:
                sp_status = "NO DATA"
                distance_pct = 0
            else:
                distance_pct = ((current / sp["strike"]) - 1) * 100
                if distance_pct < -10:
                    sp_status = "DANGER"
                elif distance_pct < 0:
                    sp_status = "WARNING"
                else:
                    sp_status = "SAFE"

            emoji = {"DANGER": "🔴", "WARNING": "🟡", "SAFE": "🟢", "EXPIRED": "⚫", "NO DATA": "⚪"}.get(sp_status, "⚪")
            lines.append(f"  {emoji} [{sp['account']}] {ticker} x{sp['shares']} — {sp_status}")
            lines.append(f"     Strike ${sp['strike']:.2f} | Current ${current:.2f} ({distance_pct:+.1f}%) | Exp: {sp['expiry']} ({days_to_expiry}d)")
            if sp.get("rolled_from"):
                lines.append(f"     ↩️  Rolled from: {sp['rolled_from']}")
            if sp_status == "DANGER":
                lines.append(f"     ⚠️  BELOW STRIKE — assignment risk!")
            lines.append("")

            sell_puts_data.append({
                "account": sp["account"],
                "ticker": f"{ticker} x{sp['shares']}",
                "strike": sp["strike"],
                "current": current,
                "buffer_pct": round(distance_pct, 1) if sp_status not in ("EXPIRED", "NO DATA") else 0,
                "expiry": sp["expiry"],
                "status": sp_status,
            })

        # Show closed sell puts
        if closed_puts:
            lines.append("  ── Closed ──")
            for sp in closed_puts:
                reason = sp["closed"].upper()
                lines.append(f"  ⚫ [{sp['account']}] {sp['ticker']} x{sp['shares']} — CLOSED ({reason})")
                lines.append(f"     Strike ${sp['strike']:.2f} | Exp: {sp['expiry']}")
                lines.append("")

                sell_puts_data.append({
                    "account": sp["account"],
                    "ticker": f"{sp['ticker']} x{sp['shares']}",
                    "strike": sp["strike"],
                    "current": 0,
                    "buffer_pct": 0,
                    "expiry": sp["expiry"],
                    "status": "CLOSED",
                })

    # ── Accumulators Section ──
    if ACCUMULATORS:
        lines.append("╔══════════════════════════════════════════════════════════╗")
        lines.append("║  ACCUMULATOR POSITIONS                                 ║")
        lines.append("╚══════════════════════════════════════════════════════════╝")
        lines.append("")

        for acc in ACCUMULATORS:
            expiry_date = datetime.strptime(acc["expiry"], "%Y-%m-%d")
            days_to_expiry = (expiry_date - today).days
            ticker = acc["ticker"]
            current = prices.get(ticker, 0) if prices else 0

            if days_to_expiry < 0:
                acc_status = "EXPIRED"
                distance_pct = 0
            elif current == 0:
                acc_status = "NO DATA"
                distance_pct = 0
            else:
                distance_pct = ((current / acc["strike"]) - 1) * 100
                if distance_pct < -10:
                    acc_status = "DANGER"  # deep below strike, forced double-down
                elif distance_pct < 0:
                    acc_status = "WARNING"  # below strike, accumulating at loss
                else:
                    acc_status = "SAFE"

            emoji = {"DANGER": "🔴", "WARNING": "🟡", "SAFE": "🟢", "EXPIRED": "⚫", "NO DATA": "⚪"}.get(acc_status, "⚪")
            above_call = current >= acc["call_price"] if current > 0 else False
            call_note = " 🛑 ABOVE CALL — knocked out" if above_call else ""
            lines.append(f"  {emoji} [{acc['account']}] {ticker} x{acc['shares_per_day']}/day — {acc_status}{call_note}")
            lines.append(f"     Strike ${acc['strike']:.2f} | Call ${acc['call_price']:.2f} | Current ${current:.2f} ({distance_pct:+.1f}%) | Exp: {acc['expiry']} ({days_to_expiry}d)")
            if acc_status == "DANGER":
                lines.append(f"     ⚠️  BELOW STRIKE — forced 2x accumulation!")
            lines.append("")

            accumulators_data.append({
                "account": acc["account"],
                "description": f"{ticker} x{acc['shares_per_day']}/day",
                "strike_call": f"${acc['strike']:.2f} / ${acc['call_price']:.2f}",
                "current": current,
                "buffer_pct": round(distance_pct, 1) if acc_status not in ("EXPIRED", "NO DATA") else 0,
                "expiry": acc["expiry"],
                "status": acc_status,
            })

    # ── Autocall Proximity Section (with Memory Knockout Detection) ──
    lines.append("╔══════════════════════════════════════════════════════════╗")
    lines.append("║  AUTOCALL (KO) PROXIMITY                               ║")
    lines.append("╚══════════════════════════════════════════════════════════╝")
    lines.append("")
    if hist_data:
        lines.append("  ℹ️  Memory knockout detection: ON (checking past obs dates)")
    else:
        lines.append("  ℹ️  Memory knockout detection: OFF (use without --no-history)")
    lines.append("")

    autocall_data = []  # for JSON output

    # Build autocall entries with memory knockout info
    autocall_entries = []
    for note in FCN_PORTFOLIO:
        # Skip autocalled and expired notes
        if note.get("autocalled"):
            continue
        expiry_date = datetime.strptime(note["expiry"], "%Y-%m-%d")
        days_to_expiry = (expiry_date - today).days
        if days_to_expiry < 0:
            continue

        # Run memory knockout check if historical data available
        memory_ko = {}
        if hist_data:
            memory_ko = check_memory_knockouts(note, hist_data, today)

        underlying_info = []
        worst_call_gap = float("inf")
        all_cleared = True  # True if every underlying is either KO'd or currently above
        blockers = []
        ko_count = 0
        total_underlyings = len(note["underlyings"])

        for u in note["underlyings"]:
            ticker = u["ticker"]
            call_price = u["call_price"]
            current = prices.get(ticker, 0)
            ko_info = memory_ko.get(ticker, {})
            is_ko = ko_info.get("ko", False)

            if current == 0:
                ui_entry = {
                    "ticker": ticker, "current": 0,
                    "call_price": call_price, "gap_pct": None,
                    "memory_ko": is_ko,
                    "ko_date": ko_info.get("ko_date"),
                    "ko_price": ko_info.get("ko_price"),
                }
                underlying_info.append(ui_entry)
                if not is_ko:
                    all_cleared = False
                    blockers.append(f"{ticker} (NO DATA)")
                else:
                    ko_count += 1
                continue

            gap_pct = ((current / call_price) - 1) * 100
            ui_entry = {
                "ticker": ticker, "current": current,
                "call_price": call_price, "gap_pct": round(gap_pct, 1),
                "memory_ko": is_ko,
                "ko_date": ko_info.get("ko_date"),
                "ko_price": ko_info.get("ko_price"),
            }
            underlying_info.append(ui_entry)

            if is_ko:
                # Already KO'd — doesn't block autocall regardless of current price
                ko_count += 1
            elif gap_pct >= 0:
                # Currently above call — would KO at next observation
                pass
            else:
                # Below call and not KO'd — this is a real blocker
                all_cleared = False
                blockers.append(f"{ticker} ({gap_pct:+.1f}%)")
                if gap_pct < worst_call_gap:
                    worst_call_gap = gap_pct

        # If all are KO'd or above call, worst_call_gap stays inf → set to 0
        if all_cleared:
            worst_call_gap = 0

        autocall_entries.append({
            "note": note,
            "days_to_expiry": days_to_expiry,
            "underlying_info": underlying_info,
            "worst_call_gap": worst_call_gap,
            "all_cleared": all_cleared,
            "blockers": blockers,
            "ko_count": ko_count,
            "total_underlyings": total_underlyings,
        })

    # Sort: all_cleared first, then by worst_call_gap descending
    autocall_entries.sort(key=lambda x: (not x["all_cleared"], -x["worst_call_gap"]))

    for entry in autocall_entries:
        note = entry["note"]
        all_cleared = entry["all_cleared"]
        blockers = entry["blockers"]
        days = entry["days_to_expiry"]
        ko_count = entry["ko_count"]
        total_ul = entry["total_underlyings"]

        if all_cleared:
            tag = "🟢 READY"
        elif entry["worst_call_gap"] > -5:
            tag = "🟡 CLOSE"
        elif entry["worst_call_gap"] > -15:
            tag = "🔵 POSSIBLE"
        else:
            tag = "⚪ FAR"

        # Compute observation dates
        issue_str = note.get("issue_date")
        next_obs, days_to_obs = next_observation_date(today, note["expiry"], issue_str)
        obs_dates = all_observation_dates(note["expiry"], issue_str)
        obs_passed = sum(1 for d in obs_dates if d.date() < today.date())
        obs_total = len(obs_dates)
        obs_remaining = obs_total - obs_passed

        # Header with memory KO count
        memory_label = ""
        if ko_count > 0:
            memory_label = f" [Memory: {ko_count}/{total_ul} KO'd]"
        lines.append(f"  {tag} — {_isin(note['isin'])} ({note['coupon']}%, {days}d){memory_label}")
        lines.append(f"     {note['product']}")

        # Observation info line
        if next_obs:
            obs_str = next_obs.strftime("%Y-%m-%d")
            weekday = next_obs.strftime("%a")
            lines.append(
                f"     Next obs: {obs_str} ({weekday}, {days_to_obs}d) "
                f"| {obs_passed}/{obs_total} passed, {obs_remaining} remaining"
            )
        else:
            lines.append(f"     Observations complete ({obs_total} total)")

        for ui in entry["underlying_info"]:
            t = ui["ticker"]
            is_ko = ui.get("memory_ko", False)
            ko_date = ui.get("ko_date")
            ko_price = ui.get("ko_price")

            if ui["gap_pct"] is None:
                if is_ko:
                    lines.append(f"    🔓 {t:<6} NO DATA  call ${ui['call_price']:.2f}  [KO'd {ko_date} @ ${ko_price:.2f}]")
                else:
                    lines.append(f"    {t:<6} NO DATA  call ${ui['call_price']:.2f}")
            else:
                gap = ui["gap_pct"]
                cur = ui["current"]
                cp = ui["call_price"]

                if is_ko:
                    # Already KO'd from a past observation — permanently cleared
                    bar = "🔓"
                    dist_str = f"KO'd {ko_date} @ ${ko_price:.2f} (now ${cur:.2f})"
                elif gap >= 0:
                    bar = "✅"
                    dist_str = f"+{gap:.1f}% above call"
                else:
                    bar = "❌"
                    dollar_gap = cp - cur
                    dist_str = f"{gap:.1f}% (${dollar_gap:.2f} to go)"
                lines.append(f"    {bar} {t:<6} ${cur:>8.2f}  call ${cp:>8.2f}  {dist_str}")

        if all_cleared:
            if next_obs:
                lines.append(
                    f"     → AUTOCALL at {next_obs.strftime('%Y-%m-%d')} obs — "
                    f"{_amt(note['amount'])} redeems in {days_to_obs}d"
                )
            else:
                lines.append(f"     → AUTOCALL — {_amt(note['amount'])} redeems")
        elif blockers:
            lines.append(f"     → Blocker(s): {', '.join(blockers)}")
        lines.append("")

        autocall_data.append({
            "isin": note["isin"],
            "account": note.get("account", ""),
            "product": note["product"],
            "amount": note["amount"],
            "coupon": note["coupon"],
            "days_to_expiry": days,
            "all_cleared": all_cleared,
            "proximity_tag": tag.split(" ", 1)[1] if " " in tag else tag,
            "worst_call_gap_pct": round(entry["worst_call_gap"], 1) if entry["worst_call_gap"] != float("inf") else None,
            "blockers": blockers,
            "memory_ko_count": ko_count,
            "total_underlyings": total_ul,
            "underlyings": entry["underlying_info"],
            "next_observation": next_obs.strftime("%Y-%m-%d") if next_obs else None,
            "days_to_next_obs": days_to_obs,
            "observations_passed": obs_passed,
            "observations_total": obs_total,
            "observations_remaining": obs_remaining,
        })

    # ── Ticker Impact Summary (which tickers unlock the most autocalls) ──
    # Only count underlyings that are NOT already memory-KO'd and below call
    ticker_impact = {}
    for entry in autocall_entries:
        if entry["all_cleared"]:
            continue
        for ui in entry["underlying_info"]:
            if ui.get("memory_ko"):
                continue  # Already KO'd — not a blocker
            if ui["gap_pct"] is not None and ui["gap_pct"] < 0:
                t = ui["ticker"]
                if t not in ticker_impact:
                    ticker_impact[t] = {"count": 0, "exposure": 0, "gap_pcts": []}
                ticker_impact[t]["count"] += 1
                ticker_impact[t]["exposure"] += entry["note"]["amount"]
                ticker_impact[t]["gap_pcts"].append(ui["gap_pct"])

    if ticker_impact:
        lines.append("  ── Ticker Impact (blockers ranked by exposure) ──")
        sorted_impact = sorted(ticker_impact.items(), key=lambda x: -x[1]["exposure"])
        for t, info in sorted_impact:
            avg_gap = sum(info["gap_pcts"]) / len(info["gap_pcts"])
            lines.append(
                f"    {t:<6} blocks {info['count']} note(s), "
                f"{_amt(info['exposure'])} exposure, avg {avg_gap:+.1f}% from call"
            )
            blockers_data.append({
                "ticker": t,
                "blocks": info["count"],
                "exposure": info["exposure"],
                "avg_gap": round(avg_gap, 1),
            })
        lines.append("")

    # Summary
    active_notes = len(FCN_PORTFOLIO) - len(autocalled_notes)
    autocalled_amt = sum(n["amount"] for n in autocalled_notes)

    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("  PORTFOLIO SUMMARY")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"  Active: {active_notes} notes, {_amt(total_exposure)} exposure")
    if autocalled_notes:
        lines.append(f"  ✅ Autocalled: {len(autocalled_notes)} note(s), {_amt(autocalled_amt)} redeemed")
    if danger_count:
        lines.append(f"  🔴 DANGER: {danger_count} note(s), {_amt(danger_exposure)} at risk")
    if warning_count:
        lines.append(f"  🟡 WARNING: {warning_count} note(s), {_amt(warning_exposure)} close to strike")
    if not danger_count and not warning_count:
        lines.append("  🟢 ALL SAFE — no positions near strike")
    lines.append("")

    report = "\n".join(lines)

    structured = {
        "date": today.strftime("%Y-%m-%d"),
        "type": "FCN Check",
        "total_exposure": total_exposure,
        "danger_count": danger_count,
        "danger_exposure": danger_exposure,
        "warning_count": warning_count,
        "warning_exposure": warning_exposure,
        "notes": results,
        "autocall_proximity": autocall_data,
        "sell_puts": sell_puts_data,
        "fx_options": fx_options_data,
        "accumulators": accumulators_data,
        "blockers": blockers_data,
        "key_signals": (
            f"{danger_count} DANGER ({_amt(danger_exposure)}), "
            f"{warning_count} WARNING ({_amt(warning_exposure)}), "
            f"{len(FCN_PORTFOLIO) - danger_count - warning_count} SAFE"
        ),
    }

    return report, structured


if __name__ == "__main__":
    skip_hist = "--no-history" in sys.argv
    report, data = check_fcn_portfolio(skip_history=skip_hist)
    if "--json" in sys.argv:
        print(json.dumps(data, indent=2))
    else:
        print(report)
