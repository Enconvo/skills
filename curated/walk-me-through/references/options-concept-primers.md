# Options Concept Primers (Mentor Library)

This is the teaching backbone of the skill. When Mentorship Mode is active, the copilot uses these primers to explain a concept **the first time it appears** in a session, then references it lightly afterwards. The goal is that an apprentice leaves the session understanding *why* each chart matters, not just *what* the conclusion was.

## How to use this library

For each concept, the primer has six parts:

1. **Plain definition** — one or two sentences, no jargon.
2. **Mental model / analogy** — a picture the apprentice can hold in their head.
3. **Why it matters** — what decision the metric informs.
4. **Read it on OptionCharts** — exactly where it lives and what to look at.
5. **Common misread** — the trap beginners fall into.
6. **Check-for-understanding prompt** — a short Socratic question the mentor can ask before moving on.

Teaching depth is set by the apprentice's level (see `SKILL.md` → Mentorship Mode):

- **Novice**: give parts 1–2 in full, 3 briefly, skip heavy math, always ask the check question.
- **Intermediate**: give parts 1, 3, 4, 5; analogy only if the apprentice hesitates.
- **Advanced**: skip the primer; go straight to interpretation and discuss edge cases and second-order effects.

Never lecture all six parts mechanically. Teach the part the apprentice needs, tie it to the live chart on screen, then check understanding.

**Site-agnostic note:** the options theory in these primers is the same wherever the same metric exists. The "Read it on OptionCharts" pointers name the default options site; when working in TradingView, use `tradingview-docs-map.md` for chart-tool locations and bridge only the overlapping concepts (price action, volume, support/resistance, alerts, watchlists, screeners). TradingView does not replace OptionCharts-only metrics such as GEX, DEX, max pain, or options P&L modeling unless those exact views are visibly available.

---

## Foundations

### Call and Put (the absolute basics)

1. A **call** is the right to buy 100 shares at a set strike price before expiry; a **put** is the right to sell 100 shares at a set strike. Buyers pay a premium; sellers collect it and take on the obligation.
2. A call is a "reserved buy price"; a put is "price insurance." The buyer of insurance pays the premium; the seller is the insurance company.
3. Direction, leverage, and hedging all start here. Everything else on OptionCharts is built from millions of these contracts.
4. Read it on OptionCharts: the **Option Chain** tab lists every strike/expiry with bid, ask, volume, OI, IV, and Greeks.
5. Common misread: thinking a cheap out-of-the-money option is "low risk" because it costs little — it has a high chance of expiring worthless.
6. Check: "If you buy a $130 call and the stock finishes at $125 at expiry, what is that call worth?" (Answer: zero — it expired out of the money.)

### Premium, intrinsic value, and time value

1. **Premium** is the option's price. It splits into **intrinsic value** (how far in-the-money it already is) and **time value** (everything else — the chance it gets *more* in-the-money before expiry).
2. Intrinsic value is the cash you'd get exercising right now; time value is the price of hope and uncertainty, and it melts as expiry nears.
3. Explains why options lose value even when the stock doesn't move (see Theta), and why earnings/events inflate premiums.
4. Read it on OptionCharts: compare an in-the-money option's price to (spot − strike) on the **Option Chain** or **Option Contract** page; the excess is time value.
5. Common misread: blaming a losing long option on direction when the real culprit was time/IV decay.
6. Check: "A $120 call with the stock at $124 costs $7. How much of that is intrinsic, and how much is time value?" ($4 intrinsic, $3 time.)

---

## Positioning and Liquidity

### Open Interest (OI)

1. **Open interest** is the number of option contracts that currently exist (opened and not yet closed) at a given strike/expiry.
2. Think of it as the *standing crowd* already in the trade — a map of where money is parked, updated once a day.
3. High-OI strikes are liquid, hard-to-ignore price levels; clusters can act like magnets or barriers into expiry.
4. Read it on OptionCharts: **Option Charts → Open Interest**. Use *Open Interest by Strike* for the map, *Highest Open Interest Options* for the biggest single contracts, and *Total by Expiry* for where positioning concentrates.
5. Common misread: treating OI as live. It updates once daily (around the open), so it is stale versus intraday volume and quotes — and big OI alone doesn't tell you whether it's bullish or bearish.
6. Check: "OI is huge at the $130 call strike. Does that tell us traders are bullish?" (Not by itself — someone is long and someone is short that strike; context from price, volume, and GEX is needed.)

### Volume

1. **Volume** is how many contracts traded *today* — the day's activity, not the standing crowd.
2. If OI is the crowd already in the stadium, volume is the turnstile count for today.
3. Volume reveals *fresh* interest and where today's attention and hedging pressure are landing.
4. Read it on OptionCharts: **Option Charts → Volume**, and the **Overview** aggregate volume vs 30-day average (a reading well above 100% signals an unusually active day).
5. Common misread: assuming high volume = bullish. Volume is direction-agnostic; pair it with the volume put/call ratio and *Unusual Options*.
6. Check: "Today's volume is 170% of average and the volume put/call ratio is 0.4. What does that combination hint at?" (Heavy, call-skewed activity — a bullish *lean* in today's flow, to be confirmed elsewhere.)

### Put/Call Ratio

1. The **put/call ratio** divides put activity by call activity. Below ~0.7 leans bullish, near 1.0 is balanced, well above 1.0 leans bearish/defensive. It exists for both volume (today's flow) and open interest (standing positioning).
2. A crowd-sentiment thermometer — but a noisy one.
3. Quick directional tilt of the options crowd; the *volume* ratio is today's mood, the *OI* ratio is the durable stance.
4. Read it on OptionCharts: shown on the **Overview** for volume and OI, and per-expiry in the **Option Chain Statistics** table.
5. Common misread: reading it as a clean signal. Deep-OTM "tail" puts (financing/hedge structures) can inflate put numbers without anyone being bearish.
6. Check: "Volume put/call is 0.4 but OI put/call is 0.95. Why might today's flow look more bullish than the standing book?" (Today's traders are buying calls, but the parked positioning is balanced.)

### Unusual Options Activity

1. **Unusual options** rank contracts by volume relative to their existing open interest — i.e., where *new* activity is large compared to what was already there.
2. A spotlight on "something happened here today" rather than the usual background trading.
3. Surfaces fresh conviction, possible informed positioning, and where a catalyst may be anticipated.
4. Read it on OptionCharts: **Option Charts → Unusual Options**, sorted by the volume/OI ratio. Note strike, expiry, and call vs put.
5. Common misread: assuming unusual = smart money or a sure thing. Much of it is hedging, spreads, or rolls; same-day 0DTE churn inflates the list.
6. Check: "We see big fresh call buying at strikes *above* a known call wall. Is that more interesting as a continuation bet or a fade?" (Discuss both — it can mean upside chase *or* call-writing supply; confirm with GEX.)

---

## Pinning and Expiration

### Max Pain

1. **Max pain** is the price at which the largest dollar amount of options expires worthless — the level that's most painful for option *buyers* and least costly for *sellers*.
2. Imagine a tug-of-war where the rope tends to settle where the most contracts die; that settling point is max pain.
3. A weak, expiration-week magnet/reference level — useful context, never a rule.
4. Read it on OptionCharts: **Option Charts → Max Pain**, and the *Max Pain vs Current Price* column in the **Option Chain Statistics** table per expiry.
5. Common misread: trading max pain as a target. It's derived from once-daily OI, drifts, and is weak for hyper-liquid mega-caps and index products (SPY/QQQ).
6. Check: "Max pain for Friday's expiry is $133 and the stock is $124. Is that a reason to expect a rally to $133?" (No — it's a soft reference; only meaningful near expiry and only with confirming structure.)

### Expected Move

1. The **expected move** is the price range (roughly ±1 standard deviation) the options market implies by a given expiry, derived from IV.
2. The market's own "error bars" around the current price for that date.
3. Sizes how big a move is already priced in — essential for setting targets, stops, and judging whether a forecast is ambitious or modest.
4. Read it on OptionCharts: the **Expected Move** chart and the *Expected Move* column in the **Option Chain Statistics** table per expiry.
5. Common misread: treating the band as a ceiling. It's ~68% probability for ±1σ; price exceeds it routinely, especially in high-vol names.
6. Check: "The 6-day expected move is ±7%. If your thesis needs a 20% move in a week, what does that tell you?" (The market thinks that's a low-probability tail — possible but you're paying for, or betting on, a big surprise.)

### Probability Distribution

1. The **probability distribution** shows the option-implied odds of the stock finishing at each price by expiry — a bell-ish curve widening with time.
2. A weather forecast turned into a curve: most likely outcomes in the fat middle, tails for surprises.
3. Translates IV into intuitive odds for finishing above/below a strike, helping size conviction and pick strikes.
4. Read it on OptionCharts: **Option Charts → Probability Distribution** (lognormal vs implied; PDF vs CDF view).
5. Common misread: treating it as truth rather than the market's current implied estimate — it shifts as IV and price move, and assumes no drift/news.
6. Check: "The curve for next week is tall and narrow; for six months out it's low and wide. Why?" (More time = more uncertainty = wider distribution.)

---

## Volatility

### Implied Volatility (IV)

1. **Implied volatility** is the market's forecast of how much the stock will move (annualized %), backed out of option prices. Higher IV = pricier options.
2. The "weather forecast" baked into premiums — and like weather, it's about *range of motion*, not direction.
3. Tells you whether options are expensive or cheap and how much an IV change can help or hurt a position.
4. Read it on OptionCharts: **Overview** aggregate IV, the **Volatility Skew** page, and per-contract IV on the chain.
5. Common misread: confusing high IV with bullishness. IV says "big moves expected," not "up." Buying high-IV options into a known event often leads to an IV-crush loss even if direction is right.
6. Check: "IV is 75%. After earnings it drops to 50% while the stock barely moves. What happens to a long option you bought before earnings?" (It loses value from IV crush despite flat price.)

### IV Rank and IV Percentile

1. **IV Rank** places current IV between its 1-year low and high (0–100%); **IV Percentile** is the share of days in the past year IV was *lower* than now.
2. A speedometer that's been re-scaled to this specific stock's own history, so "is 75% high?" gets a contextual answer.
3. Helps decide whether to be a net buyer (cheap vol) or net seller (rich vol) of options.
4. Read it on OptionCharts: **Overview** options statistics block (IV Rank, IV Percentile, plus IV high/low dates).
5. Common misread: using the raw IV number across stocks. 75% IV is sky-high for a utility and routine for a crypto-proxy — rank/percentile normalize that.
6. Check: "IV Rank 37 but IV Percentile 81. What's the nuance?" (IV sits mid-way between its yearly extremes, yet it has spent most days lower than now — moderately elevated, not extreme.)

### Volatility Skew

1. **Skew** is how IV differs across strikes. Most equities show higher IV for downside puts ("put skew") because investors pay up for crash protection.
2. The *shape* of fear: a steeper downside curve means the market is paying more to insure against a drop.
3. Reveals where the market prices tail risk, which side is "expensive," and informs spread construction (sell the rich wing, buy the cheap one).
4. Read it on OptionCharts: **Option Charts → Volatility Skew**, comparing put-wing vs call-wing IV across strikes and expiries.
5. Common misread: ignoring that deep-OTM strikes can show extreme IV from thin liquidity or structural hedges, distorting the curve.
6. Check: "Downside puts carry much higher IV than upside calls. What is the market paying up for?" (Crash/downside protection — a defensive posture.)

### Historical Volatility (HV)

1. **Historical volatility** is how much the stock *actually* moved over a past window — the realized counterpart to implied.
2. IV is the forecast; HV is the box score of what really happened.
3. Comparing IV vs HV shows whether options are pricing more or less movement than the stock has been delivering.
4. Read it on OptionCharts: **Overview** options statistics (Historical Volatility alongside IV).
5. Common misread: expecting IV to equal HV. A persistent IV > HV gap is the "volatility risk premium" sellers harvest; IV < HV can flag underpriced options.
6. Check: "IV is 74% and HV is 75%. Are options pricing more or less movement than the stock has recently shown?" (About the same — roughly fairly priced.)

---

## The Greeks (option sensitivities)

### Delta

1. **Delta** estimates how much an option's price moves per $1 move in the stock (0 to 1 for calls, 0 to −1 for puts). It also approximates the option's share-equivalent exposure and a rough probability of finishing in-the-money.
2. The "speed" of the option relative to the stock — and how many shares it currently behaves like.
3. Core to directional sizing and to understanding dealer hedging (see DEX).
4. Read it on OptionCharts: **Option Charts → Greeks → Delta**, and per-contract on the chain.
5. Common misread: treating delta as a fixed probability. It shifts as price, time, and IV change (that change is Gamma).
6. Check: "A call has 0.30 delta. Roughly how much does it move if the stock rises $1, and what's the loose read on its odds of expiring in-the-money?" (~$0.30; ~30%.)

### Gamma

1. **Gamma** is the rate of change of delta — how fast an option's directional exposure shifts as the stock moves.
2. Delta is speed; gamma is acceleration. High gamma means exposure changes quickly, so hedges must be adjusted often.
3. Drives pinning, squeezes, and dealer-hedging feedback loops near big strikes and near expiry (see GEX).
4. Read it on OptionCharts: **Option Charts → Greeks → Gamma**; concentration near spot foreshadows pin behavior.
5. Common misread: ignoring that gamma explodes near expiry for at-the-money strikes, making 0DTE behavior violent and unlike longer-dated positioning.
6. Check: "Gamma is concentrated right at the current price into Friday. What kind of price behavior does that tend to encourage?" (Pinning / sticky price, if dealers are long gamma.)

### Theta

1. **Theta** is the daily time decay — how much value an option loses per day from the clock alone, all else equal.
2. The melting ice cube: every day a little time value drips away, fastest in the final weeks for at-the-money options.
3. Tells option *buyers* what they pay to hold and option *sellers* what they collect to wait.
4. Read it on OptionCharts: **Option Charts → Greeks → Theta**, and per-contract.
5. Common misread: forgetting theta accelerates into expiry, so a "right but early" long option can still bleed out.
6. Check: "You're long a weekly at-the-money call and the stock sits still for three days. What's quietly happening to your position?" (Theta is eroding it.)

### Vega

1. **Vega** is sensitivity to a 1-point change in implied volatility — how much the option gains or loses if IV rises or falls.
2. Your exposure to the "weather forecast" changing, independent of where the stock goes.
3. Critical around earnings/events: vega is why long options can lose on an IV crush even when direction is right.
4. Read it on OptionCharts: **Option Charts → Greeks → Vega**; longer-dated options carry more vega.
5. Common misread: buying options just before a known event without respecting that the priced-in IV will likely collapse afterward.
6. Check: "Two calls, same delta — one expires in a week, one in a year. Which has more vega, and why does that matter into an IV spike?" (The year-dated one; it gains more if IV rises, loses more if IV falls.)

---

## Dealer Positioning (the advanced lenses)

> Teaching note: GEX and DEX are where apprentices most often nod along without truly understanding. Always anchor them in the same story: **market makers sell options to the public, end up with risk they don't want, and continuously buy/sell the underlying stock to stay hedged. Those hedging trades push the stock around.** Build every GEX/DEX explanation on that one sentence.

### Dealer Hedging (the prerequisite mental model)

1. When you buy an option, a **market maker** usually takes the other side. To avoid betting on direction, they offset (hedge) by trading shares of the stock — and they re-adjust that hedge as the stock moves.
2. Picture a tightrope walker (the dealer) holding a balance pole (their stock hedge), constantly making small corrections to stay neutral. Those corrections move the rope (the stock).
3. This is *why* options open interest can influence the stock itself — the tail that can wag the dog near big expiries. It's the foundation under GEX and DEX.
4. Read it on OptionCharts: not a single chart — it's the interpretation lens for GEX, DEX, and gamma concentration.
5. Common misread: believing dealer hedging *dictates* price. It's one force among many (fundamentals, macro, the underlying — e.g., bitcoin for a BTC-proxy) and dominates mainly near large-OI expiries.
6. Check: "Why would the existence of a lot of options at one strike ever affect the actual stock price?" (Because dealers hedge those options by trading the stock, and near that strike their hedging can intensify.)

### Gamma Exposure (GEX)

1. **GEX** estimates the dollar amount of stock dealers must buy or sell for each ~1% move to stay hedged, aggregated across all options. **Positive net GEX** generally means dealers buy dips and sell rips (volatility-dampening, pinning). **Negative net GEX** means they sell weakness and buy strength (volatility-amplifying).
2. Positive gamma is a shock absorber on the stock; negative gamma is an accelerator that can turn a slide into a slide-and-crash (or a pop into a squeeze).
3. Tells you whether the current structure tends to *suppress* or *amplify* moves, and where regime changes lie.
4. Read it on OptionCharts: **Option Charts → Gamma Exposure (GEX)**. Extract **Net GEX**, **Call Wall** (often resistance/upper magnet), **Put Wall** (often support), and the **Gamma Flip / Zero Gamma** (the price where the regime flips from positive to negative). Check *GEX by Open Interest* vs *by Volume*, and the per-expiry table.
5. Common misread (two): (a) reading aggregate "all-expiries" GEX as the live picture when a giant 0DTE/expired contract dominates it — after that expiry rolls off, the structure changes, so always inspect the forward expiry separately; (b) forgetting GEX is built on a *convention*, not observed dealer books — it typically assumes dealers are long calls and short puts versus customers. When customer flow breaks that assumption (e.g. heavy speculative call *buying*), the signs can mislead. Treat GEX as an estimate with stated assumptions, not a measurement.
6. Check: "Net GEX is positive and the stock is above the gamma flip. If price drifts down toward the flip, what changes mechanically below it?" (It crosses into negative gamma — dealers flip from cushioning to selling into weakness, so downside can accelerate.)

### Delta Exposure (DEX)

1. **DEX** estimates the net directional (delta) hedging exposure dealers carry from the options book — which way, and how heavily, the hedge leans. OptionCharts expresses it as the dollar value option sellers must hedge per 1% move in the underlying to stay delta-neutral.
2. If GEX is about *acceleration* of hedging, DEX is about the *direction* of the hedge currently in place — which way the book leans.
3. Net positive vs negative DEX hints at whether dealer hedging is a tailwind or headwind, and which strikes anchor it.
4. Read it on OptionCharts: **Option Charts → Delta Exposure (DEX)**. Extract **Net DEX**, call/put DEX, and the DEX page's own call/put walls (computed from delta, so they can differ from the GEX walls); compare *by Open Interest* vs *by Volume*, and read the per-expiry table.
5. Common misread: same aggregation trap as GEX — expired/0DTE and far-dated LEAPS can dominate the total; the near-month is what bites first.
6. Check: "Forward-month DEX is net negative across the next several expiries even though today's call volume looks bullish. Why might those two signals point different directions?" (Today's flow is fresh sentiment; DEX reflects the larger standing book of puts/hedges that can pressure the stock.)

### Call Wall, Put Wall, Gamma Flip (the levels)

1. The **call wall** is the strike with the largest concentration of call gamma (usually above spot; frequent resistance/magnet); the **put wall** is the put-gamma equivalent below (frequent support); the **gamma flip** is the price where net dealer gamma crosses zero.
2. Walls are the guardrails; the gamma flip is the line between the "calm highway" (positive gamma) and the "icy road" (negative gamma).
3. They give concrete, testable levels for theses, triggers, and invalidation — far more actionable than a vague "support/resistance."
4. Read it on OptionCharts: labeled directly on the **GEX** chart and listed in the GEX/DEX stats tables (per expiry too). Note the **DEX page computes its own call/put walls**, which can sit at different strikes than the GEX walls — say which page a wall came from.
5. Common misread: treating walls as fixed. They move as OI and volume change daily, and which way a wall "pushes" depends on which side of those options dealers actually hold (an assumption, not a fact — see the GEX primer's convention note).
6. Check: "Why does the call wall usually act as resistance — and what has to be different for a break above it to *accelerate* instead?" (Under the usual assumption dealers are *long* those calls — e.g. from investors selling covered calls — so their hedge sells into strength near the wall: resistance. Upside accelerates only in the opposite case: when dealers are *short* upside calls because customers have been buying them, dealer re-hedging must chase price up — the squeeze case. So the wall's behavior depends on who holds which side, which GEX can only estimate by convention.)

---

## Position Work (Profit & Loss modeling)

### Profit & Loss Chart

1. The **P&L chart** draws a position's profit/loss across stock prices, at expiration and before, so you can see max gain, max loss, and breakevens.
2. A flight simulator for a trade: test the bumps before risking real capital.
3. Turns an abstract position into a concrete risk picture and stress-tests it against IV and time.
4. Read it on OptionCharts: **Profit & Loss Chart** tab — add legs (and shares), set actual entry prices, use *Analyze at Date* for pre-expiry, and shift IV to model crush/expansion.
5. Common misread: trusting the pre-expiry curve as exact. It uses Black-Scholes theoretical values; real fills, early assignment, dividends, and IV shifts move the real outcome.
6. Check: "Your P&L looks great at expiration but you plan to exit in five days. Which view should you actually be reading?" (The *Analyze at Date* / pre-expiration curve, not the at-expiry payoff.)

---

## Putting it together: the apprentice's mental checklist

Teach the apprentice to read any name through five questions, each answered by a chart group above:

1. **Where's the crowd and is it liquid?** → Open Interest, Volume, Put/Call.
2. **What move is priced in?** → IV, IV Rank/Percentile, Expected Move, Probability.
3. **Which way is fear leaning?** → Volatility Skew, Put Wall vs Call Wall.
4. **Will dealer hedging calm or amplify moves, and where does that flip?** → GEX, DEX, Gamma Flip.
5. **What's the plan, and where am I wrong?** → key levels, triggers, invalidation, and (for a held position) the P&L chart.

A confident apprentice can name which chart answers each question and state the one level that would change their mind. That is the bar the mentor is teaching toward.
