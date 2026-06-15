# Walk Me Through Analysis Playbook

Use these templates while operating the visible browser. `SKILL.md` language/concision rules override every template here. Use long templates only when the user asks for a full memo, full recap, detail, or breakdown.

For user requests such as "help me understand GEX" or "what do these numbers mean", use Live Tutoring rather than Standard Analysis. Teach one viewport at a time: page/filter state, stats cards, main chart, lower table/details, then recap. Do not collapse those beats into one summary. After each viewport, wait for explicit confirmation such as `next`, `go ahead`, `move forward`, `continue`, or `yes` before scrolling, clicking, changing filters, or inspecting the next section.

Keep internal setup silent. Do not show messages about loading skills, reading docs, browser companion status, tab/window inventory, or debugging controllability unless the user needs to do something. Start the lesson when a visible page/viewport is ready. Keep tutor messages brief and natural: a few short lines, one takeaway, one stop-and-wait prompt.

## Ticker Read

0. (Mentorship Mode) Calibrate the apprentice's level and goal with one light question before drilling charts; default to novice teaching if unsure.
1. Open ticker overview and note spot, trend, and aggregate options statistics.
2. Inspect the expiration calendar and choose the four expiry lenses required by `SKILL.md` rule 8 for broad stock analysis: nearest/0DTE, the current-month monthly OPEX (checking for holiday shifts), the next regular monthly OPEX, and one later monthly or quarterly expiry. Add the next weekly if it differs materially from the monthly setup. Note that chart pages may default to a later monthly or to "all expiries" — set the expiry filter explicitly rather than trusting the default.
3. For each selected expiry, check open interest by strike and total by expiry. Identify call walls, put walls, high-OI pin zones, and whether OI is call-heavy, put-heavy, or balanced.
4. Check volume and unusual options for current flow. Separate intraday/0DTE flow from durable positioning in monthly or later expiries.
5. Check max pain across selected expiries, not just the nearest expiry. Mark whether max pain supports pinning, conflicts across expiries, or is too far/stale to rely on.
6. Check GEX and DEX in a dedicated drill-down. Use full-screen or expanded chart mode when available; zoom into the spot-adjacent strike region; scroll through lower tables/indicators; extract net exposure, call wall, put wall, gamma flip/zero gamma, and largest positive/negative strike clusters. Explain pin, squeeze, stabilizing positive gamma, or destabilizing negative gamma implications.
7. Check IV/skew, probability distribution, and Greeks for implied expectations, tail pricing, and options buyer/seller risk.
8. Open option chain for actionable strikes, spreads, liquidity, IV, and Greeks around spot, support, resistance, and the user's relevant strikes.
9. Conclude with directional view, key levels, invalidation, and next checks. State which expiries drove the conclusion and which signals were only tactical.

### Visible Browser Walkthrough Standard

When the user is watching the analysis, act like a hands-on copilot:

- Show the page, not only the extracted text.
- Scroll down and back up through the full chart page so lower charts, tables, and indicators are visible.
- Use full-screen chart mode when available for OI, volume, max pain, GEX, DEX, volatility skew, probability distribution, Greeks, and unusual options.
- Zoom or drag-select around key strikes/expiries (the View Range filter's moneyness presets per `SKILL.md` M7), then reset zoom before leaving the chart.
- Anchor every cited number per `SKILL.md` M6: precise where-to-look pointer, a deep link carrying the URL's filter/zoom state, and a snapshot — or, when screenshots cannot persist in this environment, a clearly-labeled inline recreation of the same numbers.
- Briefly explain what each page answers: liquidity, flow, pin risk, dealer hedging, volatility pricing, probability, or trade execution quality.
- If hover data, full-screen, zoom, or lower-page extraction fails, say that limitation out loud in the written recap and avoid overstating the conclusion.

### Expiry Coverage Rule

Do not treat the nearest weekly or 0DTE chart as sufficient for a buy/sell call on the stock. Use this hierarchy:

- 0DTE/nearest weekly: tactical pin, scalp, and same-day risk.
- Next weekly: near-term continuation or reversal pressure.
- Monthly OPEX: more durable positioning, larger OI walls, and stronger pin/roll context.
- Later monthly/quarterly: swing/investor positioning and whether the market's options structure confirms or contradicts short-term flow.

If the expiries disagree, make the conclusion conditional rather than binary.

## Existing Position Review

Inputs to collect:

- Ticker, contracts, call/put, long/short, strike, expiration, quantity, entry price.
- Shares held, if any.
- User objective: hedge, income, speculation, repair, exit timing, or learning.
- Risk tolerance and horizon if relevant.

Workflow:

1. Recreate the position in Profit and Loss Chart.
2. Set actual entry prices and quantities.
3. Model at expiration and planned exit date.
4. Test IV up/down and spot scenarios.
5. Cross-check option chain liquidity for exits or rolls.
6. Use OI, max pain, GEX, DEX, and unusual options around the position's strikes.
7. Recommend risk actions as choices: hold, reduce, hedge, roll, set alert, or avoid adding.

## Alert Design

Build alerts as conditions the user can monitor manually or via their preferred automation:

- Price crosses key OI/GEX/DEX strike.
- Spot moves away from max pain near expiration.
- Bid/ask spread widens beyond acceptable threshold.
- Option volume spikes against position direction.
- IV changes enough to affect P&L materially.
- Delta/theta exposure moves outside user's tolerance.
- P&L chart loss at planned exit date breaches user-defined limit.

Phrase alerts as "watch if/then" rules, not guaranteed signals.

## Strategy Comparison

Compare strategies on:

- Max gain, max loss, breakevens, probability shape, and capital at risk.
- Theta/vega exposure and IV dependency.
- Liquidity and slippage by leg.
- Sensitivity to spot paths before expiration.
- Fit with market structure from OI, max pain, GEX, DEX, and skew.

Prefer tables for final comparisons.

## Written Phase Recap Template

For Live Tutoring, keep written recaps natural and short:

"On screen: [visible chart/table/section]. [One short reason it matters]. Takeaway: [one plain-English sentence]. Say 'next' or 'go ahead' when you want to continue."

Use brief written recaps after major phase transitions only. In Live Tutoring, each recap ends with an explicit stop-and-wait prompt. Keep them conversational and short; do not label them like a report. In Standard Analysis, keep moving unless the user is actively learning or asking questions.

## Mentor Teaching Beats

Pair each analytical step above with a teaching beat. Pull the concept content from `references/options-concept-primers.md`; this table maps where each lesson lands. Depth scales to the apprentice's level (novice gets the analogy and the check; advanced gets a one-line interpretation).

| Analysis step | Concept(s) to teach | Check-for-understanding prompt |
| --- | --- | --- |
| Overview / aggregate stats | IV, IV Rank vs Percentile, HV vs IV, put/call ratio | "Is this IV high *for this stock*? What tells us?" |
| Expiration ladder | expiry lenses (0DTE → monthly OPEX → LEAPS), expected move | "Why isn't the nearest weekly enough for a swing decision?" |
| Open Interest | OI as standing positioning, liquidity, walls | "Does big OI at a strike tell us bull or bear by itself?" |
| Volume + Unusual Options | volume vs OI, fresh flow, vol/OI ratio | "What does 170% of average volume with a 0.4 put/call hint at?" |
| Max Pain | weak expiry-week magnet, once-daily OI source | "Is max pain a target to trade toward?" |
| Volatility Skew | put skew = paid-up downside fear | "Which wing is the market paying up for, and why?" |
| Greeks | delta/gamma/theta/vega in plain terms | "You're long a weekly ATM call and price sits still — what's happening?" |
| GEX | dealer hedging, positive vs negative gamma, gamma flip, walls | "Above the flip vs below it — how does dealer behavior change?" |
| DEX | directional lean of the standing book | "Why can bullish day-flow and negative forward DEX disagree?" |
| Option Chain / P&L | breakevens, time vs intrinsic, Analyze-at-Date | "Exiting in 5 days — read the at-expiry or the pre-expiry curve?" |

Teaching beat micro-loop (rule M2): frame the question -> prime the concept (first time only) -> point to it on the live chart -> interpret in plain English -> ask one check or continue prompt -> stop. In Live Tutoring, bridge to the next chart only after explicit user confirmation; no browser movement or hidden inspection while waiting. Keep each beat to a few short lines unless the user asks for depth. Do not run all beats for every chart; teach what this apprentice needs now. In Standard Analysis, bridge and keep moving unless the user is actively responding.

## Learning Recap Template

Default recap is only 2-3 short lines. Use the full template below only when the user explicitly asks for a full recap.

```text
What you learned today

Concepts (2-4):
- [Concept] — [one apprentice-friendly sentence tied to what we saw on the live chart].
- ...

Mental model to keep:
- [The reusable rule of thumb, e.g., "positive gamma cushions moves, negative gamma accelerates them; the gamma flip is the line between."]

Practice next:
- [1-2 concrete things to watch or try on OptionCharts to reinforce it.]

Your glossary (optional):
- [Term]: [plain definition].

Where to go next: drill one chart deeper, model a position on the P&L chart, or pick the next concept to learn.
```

Do not use this full template during viewport-by-viewport tutoring unless the user asks to wrap up in detail.
