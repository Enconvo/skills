# TradingView Docs Map

Use this as the starting map, then verify against the live TradingView Help Center because menus, plan limits, and UI labels change. The active source of truth is `https://www.tradingview.com/support/`.

## Contents

- Access Boundaries
- Core URLs
- Feature Inventory
- Domain Concepts And Terms
- Vocabulary Bridge
- Data Semantics And Freshness
- Deep-Link And Synchronization Notes
- TradingView Tutoring Coverage
- Default Teaching Paths

## Access Boundaries

- **Public/no login:** Help Center, chart pages, symbol pages, markets pages, screeners, heatmaps, calendars, community ideas, many indicators, and basic chart interaction.
- **Account/logged-in:** saved layouts, watchlists beyond public defaults, alerts, paper trading state, broker connections, publishing, and personalized settings.
- **Paid/plan-limited:** multiple charts per tab, number of indicators per chart, historical bars, chart data export, advanced chart types/timeframes, many alerts, multiple watchlists, Bar Replay scope, volume profile/footprint/TPO, webhook alerts, and some market data feeds. Check the pricing/features page before claiming availability.
- Never bypass logins, exchange agreements, broker connections, or plan gates. If a feature is gated, teach from the Help Center and demonstrate the closest accessible surface.

## Core URLs

- Help Center: `https://www.tradingview.com/support/`
- Supercharts: `https://www.tradingview.com/chart/`
- Chart help category: `https://www.tradingview.com/support/categories/chart/`
- Supercharts guide folder: `https://www.tradingview.com/support/folders/43000579050-supercharts-learn-how-everything-works/`
- Shortcuts and tips: `https://www.tradingview.com/support/folders/43000561752-shortcuts-and-tips/`
- Multi-chart layouts: `https://www.tradingview.com/support/folders/43000578567-how-to-work-in-the-multi-chart-mode/`
- Chart scales: `https://www.tradingview.com/support/folders/43000549291-how-to-adjust-the-scales-on-a-chart/`
- Indicators category: `https://www.tradingview.com/support/categories/indicators/`
- Alerts category: `https://www.tradingview.com/support/categories/alerts/`
- Screener category: `https://www.tradingview.com/support/categories/screener/`
- Watchlist category: `https://www.tradingview.com/support/categories/watchlist/`
- Pricing/features: `https://www.tradingview.com/pricing/`
- Options product: `https://www.tradingview.com/options/`

## Feature Inventory

| Feature | Access | What it shows | Teaching use |
| --- | --- | --- | --- |
| Supercharts | public + account features | symbol chart, interval, chart type, drawings, indicators, panes, scales, alerts, trading panel | Main live teaching surface for chart reading and tool usage |
| Symbol search | public | exchange-qualified symbols and asset classes | Teach why `NASDAQ:NVDA` differs from CFDs, futures, or other venues |
| Intervals and chart types | plan-limited for some types | candles, bars, line, range/second/tick/advanced types | Teach timeframe choice and what each view hides/reveals |
| Indicators | public + plan limits | built-in and community indicators, settings, panes | Teach indicator purpose, inputs, source, and common misreads |
| Drawing tools | public + account save/sync | trendlines, fibs, ranges, text, shapes, measure tool, magnet mode | Teach support/resistance, measured moves, and chart annotation hygiene |
| Layouts and multi-chart | plan-limited | saved layouts, multiple charts, symbol/timeframe sync | Teach repeatable analysis workspaces |
| Alerts | account + plan limits | price/indicator/drawing alerts, notifications, webhooks on some plans | Teach if/then monitoring without pretending alerts predict outcomes |
| Watchlists | account + plan limits | symbol lists, columns, flags, notes, details panel | Teach monitoring baskets and avoiding ticker confusion |
| Screeners | public + account features | stock/ETF/bond/crypto/Pine screeners, filters, columns, sort | Teach idea generation and filtering before chart review |
| Bar Replay | plan-limited | historical playback and replay controls | Teach practice/backtesting habits without hindsight leakage |
| Paper trading | account | simulated orders, positions, P&L, trading panel | Teach order mechanics in simulation only; never place live trades |

## Domain Concepts And Terms

- **Supercharts**: TradingView's main chart workspace. Teach it as the live textbook: symbol, interval, chart type, price scale, time scale, panes, drawings, indicators, and right-side panels.
- **Symbol/exchange prefix**: The exchange-qualified ticker matters. Always confirm the active symbol and exchange before teaching or analyzing.
- **Interval/timeframe**: The bar size controls the story. A 5-minute chart is tactical; daily/weekly charts show broader structure.
- **Chart type**: Candles show open/high/low/close; lines hide intrabar range; Heikin Ashi/Renko/range/tick charts transform price and can mislead if treated like raw candles.
- **Scale/session**: Log vs linear scale, auto-scale, regular vs extended hours, and adjusted data can change what the user thinks they see.
- **Indicator pane/source/input**: Teach what the indicator is measuring, which price source it uses, and whether it is lagging, derived, or volume-based.
- **Drawing object**: A user-created visual hypothesis. Treat drawings as analysis aids, not facts.
- **Alert**: An if/then monitor tied to price, indicator, drawing, or strategy conditions. Alerts notify; they do not validate a trade by themselves.
- **Paper trading**: Simulation for learning order mechanics. Keep it separate from brokerage execution.

## Vocabulary Bridge

| TradingView term | Shared workflow concept | Note |
| --- | --- | --- |
| Support/resistance drawing | Key levels / invalidation | Use with OptionCharts walls/OI only when both are visibly checked |
| Volume / Volume Profile | Liquidity and participation | Not the same as options open interest or GEX |
| Indicators | Evidence lens | Explain purpose and lag before using as confirmation |
| Alert | Monitoring trigger | Same final output style as OptionCharts alert design |
| Screener | Idea funnel | Must be followed by chart and data checks before conclusions |
| Watchlist | Monitoring surface | Useful for organization; not an analytical signal |
| Bar Replay | Practice / historical walk-through | Avoid hindsight-biased conclusions |
| Paper trading | Simulated execution learning | Never treat as live broker execution |

## Data Semantics And Freshness

- TradingView sources data from many exchanges and data partners; availability and real-time status vary by market, plan, exchange agreements, and broker/data subscriptions.
- Before analyzing, read the visible symbol, exchange, interval, session, currency, and any delayed/realtime or extended-hours labels.
- For U.S. stocks, distinguish regular-hours and extended-hours charts. For futures/crypto/forex, state the relevant session/venue.
- Paid plans can unlock more indicators, alerts, history, chart layouts, export, and special chart types, but paid access does not make every feed real-time.
- Community scripts and indicators may be unverified or repainting; inspect script/source notes when relevant and avoid treating them as authoritative.

## Deep-Link And Synchronization Notes

- Prefer the live chart URL after configuring symbol, interval, indicators, layout, or drawing context. Some TradingView layout state is account-local and may not reproduce from a public URL.
- If a chart state is not fully deep-linkable, pair the URL with a screenshot and a short visible setup path: symbol -> interval -> chart type -> indicators/drawings -> side panel.
- Keep the visible viewport matched to the lesson. For toolbars and panels, center the exact control being explained before teaching it.
- When teaching drawings, select or hover the drawing so handles/settings are visible; when teaching indicators, open the indicator legend/settings or pane so inputs and labels are visible.
- When teaching alerts or paper trading, avoid submitting actions that affect live accounts. Use preview/cancel, paper trading, or explain from the dialog unless the user explicitly confirms a safe simulated action.

## TradingView Tutoring Coverage

Use this checklist before giving a chart-read or tool-use conclusion:

- Symbol/exchange confirmed.
- Market/session/data freshness stated.
- Interval and chart type explained.
- Price scale/time scale readable.
- Relevant candles, range, or pattern visible.
- Indicators named, settings visible or stated, and lag/source explained.
- Drawings/levels selected or visibly anchored.
- Volume/volume profile interpreted separately from price.
- Alerts/watchlists/screeners/paper trading treated as workflow tools, not signals.
- Limits or unavailable plan features stated.

For options-specific conclusions, TradingView alone is usually `PARTIAL ANALYSIS` unless the relevant options chain/product is visible and sufficient. Complement with OptionCharts for GEX, DEX, max pain, open interest by strike, option chain Greeks, and P&L modeling.

## Default Teaching Paths

### Supercharts Basics

1. Open `https://www.tradingview.com/chart/`, set the symbol, and confirm exchange.
2. Viewport 1: symbol header, market/session, interval, chart type.
3. Viewport 2: candles, price scale, time scale, crosshair/legend.
4. Viewport 3: one indicator or volume pane; explain source, setting, and lag.
5. Viewport 4: one drawing/measurement; explain what the line/zone tests.
6. Recap: what the user can now identify without help.

### Alerts

1. Show the exact price level, indicator, or drawing condition first.
2. Open the alert dialog only after the condition is visible.
3. Teach condition, trigger direction, expiration, notification method, and message.
4. Stop before creating/enabling anything unless the user explicitly confirms.

### Watchlists And Screeners

1. Show the current list or screener table.
2. Teach columns, sort/filter, flags/notes, and the difference between discovery and confirmation.
3. Open one symbol from the list and connect the row back to the chart.

### Paper Trading

1. Confirm the account is paper/simulated, not live broker execution.
2. Show order ticket fields one viewport at a time: side, quantity, order type, price, time-in-force, risk.
3. Do not submit unless the user explicitly asks for a simulated order and the UI clearly says paper trading.
