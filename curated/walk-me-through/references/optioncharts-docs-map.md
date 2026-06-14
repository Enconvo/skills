# OptionCharts Docs Map

Use this as the starting map, then verify against the live docs because OptionCharts can change.

## Core Docs URLs

- Getting Started: `https://optioncharts.io/docs`
- FAQ: `https://optioncharts.io/docs/faq`
- Chart Guides index: `https://optioncharts.io/docs/chart-guides` (marked "under construction" — as of mid-2026 only Open Interest, Max Pain, and Profit & Loss guides exist; GEX, DEX, skew, Greeks, and the rest are documented only by each chart page's description text and ⓘ info buttons)
- Open Interest: `https://optioncharts.io/docs/open-interest`
- Max Pain: `https://optioncharts.io/docs/max-pain`
- Profit and Loss Chart: `https://optioncharts.io/docs/profit-and-loss-chart`
- Chart Features: `https://optioncharts.io/docs/features/chart-features`
- Real-time Options Data: `https://optioncharts.io/docs/features/realtime-options-data`
- Watchlists: `https://optioncharts.io/docs/features/watchlist`
- Saving Trades: `https://optioncharts.io/docs/features/saving-trades`

## Site and Data Boundaries

- OptionCharts provides options charts and tools for options traders using OPRA options data through Intrinio.
- OptionCharts calculates some values itself, including IV and Greeks.
- Free and Premium users see about 15-minute-delayed options data. Ultimate users can access real-time OPRA data after completing required agreements.
- Market Trends updates around every 10 minutes during market hours, even when real-time data is enabled.
- Open interest is not real-time; exchanges update it once daily. OptionCharts says OI is available at regular market open for real-time subscribers and around 9:45 AM Eastern for standard users.
- OptionCharts currently does not offer a public API. Use the website, account-permitted CSV downloads, and visible browser interaction.

## Navigation Map

Ticker view structure from the docs:

1. Overview: price history, company profile, aggregate options statistics.
2. Profit and Loss Chart: interactive risk graph for single-leg and multi-leg strategies.
3. Option Charts: open interest, volume, max pain, volatility skew, probability distribution, Greeks, unusual options, GEX, and DEX.
4. Option Chain: table of contracts by strike and expiration.
5. Option Contract: detailed individual contract view.
6. Historical Data: historical option statistics such as volume, put/call ratios, and IV.

Use the search icon or `Cmd+K` / `Ctrl+K` to search by ticker or company name.

Chart pages live at predictable URLs: `optioncharts.io/options/<TICKER>/<chart>` where `<chart>` includes `gamma-exposure`, `delta-exposure`, `open-interest`, `volume`, `max-pain`, `volatility-skew`, `greeks`, `expected-move`, `probability-distribution`, `unusual-options`.

**Deep links carry filter state.** Setting filters rewrites the URL query string, e.g. `?option_type=all&expiration_dates=all&gamma_exposure_type=open_interest&strike_range=moneyness_percent:10&indicators=gex_profile,call_wall,put_wall,gamma_flip&view_type=net`. Copy the address bar after configuring a chart and share it as the M6/M7 deep link so the user opens the exact zoomed, filtered view.

Deep-link cautions (verified live):

- The expiry token format is `expiration_dates=YYYY-MM-DD:w` or `:m` (type suffix required). An invalid or non-existent date **silently falls back to a default expiry** — possibly an already-expired weekly — so never hand-build the expiry token; copy the URL the site generated after you set the filter.
- Expiry labels: `(w)` weekly, `(m)` monthly. A **holiday-shifted monthly OPEX may be labeled `(w)`** — e.g. June 2026's third Friday (Juneteenth, market closed) shifted OPEX to Thu 2026-06-18, which the site lists as `(w)`. Identify the monthly OPEX by the calendar (third Friday, holiday-shifted), not by the site's tag alone.

## GEX and DEX Page Facts (verified on the live site)

- GEX page definition: gamma exposure is the estimated dollar value option *sellers* must hedge per 1% move in the underlying to remain gamma-neutral. Stats block shows Net/Call/Put GEX, Call Wall, Put Wall, Gamma Flip (Zero Gamma).
- DEX page definition: delta exposure is the estimated dollar value of shares option *sellers* must hedge per 1% move to remain delta-neutral. Stats block shows Net/Call/Put DEX plus the DEX page's **own** call/put walls, which can differ from the GEX walls — cite which page a wall came from.
- Both pages offer by-Open-Interest vs by-Volume toggles, an Expiration Dates filter, a View Range filter (presets ±1/2/5/10/20/50% moneyness or custom min/max), an Indicators menu, a per-expiry table, and history charts (GEX History / DEX History).
- Watch the defaults: chart pages may default to a single later monthly expiry (e.g. next monthly OPEX) or to "all expiries" depending on ticker — set the expiry filter explicitly before citing numbers.

## Chart Features to Use Actively

- Filter calls, puts, or both.
- Filter one or multiple expirations.
- Filter strike range by custom values or moneyness such as +/-5%.
- Zoom by dragging over chart regions; reset zoom when done.
- Use chart info buttons to confirm definitions.
- For supported charts and plans, use full-screen and CSV download.
- Chart tools may support annotations and indicators on Premium accounts.
- Clicking some chart points opens the corresponding option contract page.

## Open Interest

Open interest is total outstanding contracts not yet settled. Use it for liquidity, crowding, and sentiment context, not as a standalone prediction.

Interpretation reminders:

- High OI usually improves liquidity and identifies important strikes.
- Rising OI with rising price can support bullish sentiment.
- Rising OI with falling price can support bearish sentiment.
- OI plus price and volume can help confirm breakouts or reversals.
- OI is updated daily by OCC data, so it is stale intraday relative to volume/quotes.

OptionCharts provides:

- Open Interest by Strike.
- Highest Open Interest Options.
- Open Interest Total by Expiry.

## Max Pain

Max pain is the price where option buyers experience the largest aggregate loss and option sellers have the least aggregate payout at expiration. Treat it as a theory and an expiration-week reference point, not a rule.

Interpretation reminders:

- Most useful near expiration.
- Combine with spot price, volume, OI, and gamma-related charts.
- More relevant for smaller, less-liquid names than highly efficient mega-cap or index products.
- Less applicable to index options like SPY or QQQ per the OptionCharts guide.
- OptionCharts says max pain updates once daily because it is derived from open interest.

## Profit and Loss Chart

Use this for position-specific work.

Core flow:

1. Search ticker.
2. Open Profit and Loss Chart.
3. Pick a strategy or add custom legs.
4. Adjust legs: strike, delta, price, call/put, buy/sell, quantity.
5. Add shares for covered calls, protective puts, or stock-option combinations.
6. Match entry prices to actual fills.
7. Use Update Prices for best/mid/worst/custom assumptions.
8. Use Analyze at Date for pre-expiration outcomes and fractional DTE near expiry.
9. Adjust IV globally or per leg to model IV expansion/crush.
10. Use View Range to focus on relevant spot scenarios.

Risk notes from docs:

- At expiration, P&L is based on intrinsic value minus entry cost.
- Before expiration, OptionCharts uses Black-Scholes theoretical values.
- Real-world P&L can differ because of IV changes, early assignment, fill prices, dividends, and transaction costs.
- Calendar and diagonal spreads are modeled at earliest expiration with later legs valued via Black-Scholes.

## Watchlists and Saved Trades

Watchlists are Premium. They can monitor tickers and metrics such as IV, IV Rank, open interest, and volume.

Saved Trades are Premium. They are part of the P&L workflow and can track strategy performance over time, support paper-trading, and generate a shareable URL.
