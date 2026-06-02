# Script Writing

## Voice / Tone / Register Doctrine (Goldilocks)

This is the canonical voice spec for Vivieen across both Mandarin and English. Re-read before writing any script. Goldilocks = between institutional Bloomberg dry recital and Tucker-Carlson polemic; never either extreme.

## Native-Speaker Gate (HARD — applies to EVERY spoken line, EVERY language)

**The VO is authored in the target language, never translated into it.** A line that is correct but reads like translated English is a DEFECT and must be rewritten before it enters the i2v prompt. This gate is non-negotiable and applies clip-by-clip — Mandarin, English, or any future language. When working from an existing English script, treat the English as raw *meaning*, throw away its *syntax*, and re-express the meaning the way a native finance commentator would actually say it out loud across a desk.

### The read-aloud test (run on every line)

Say the line out loud in the target language. If any clause maps word-for-word onto English word order, uses a dictionary-literal verb, or no real person would phrase it that way in speech — rewrite it. Ask: *would a sharp native speaker actually say this, unscripted, to one person?* If not, it fails the gate.

### Worked example (the canonical fail → fix)

- ❌ Translationese (literal, fails the gate):
  > 高频交易公司读到这个破绽，立刻沿着更快的专线冲向其他交易所——赶在你剩下的订单到达之前。它在你自己的交易上，跑赢了你。
- ✅ Native (passes the gate):
  > 高频交易公司一看出这个破绽，马上通过更快的专线赶到其他交易所，在你剩余订单成交之前布好局。说白了，它用你自己的单子，反手赚了你的钱。

What changed, and why it matters:
- 读到这个破绽 → 一看出这个破绽 — 读到 is a literal calque of "read"; 一…就/一看出 is how Mandarin actually expresses "the moment it spots it."
- 沿着更快的专线冲向 → 通过更快的专线赶到 — 冲向 is over-dramatic English-action literalism; 赶到 is the natural verb.
- 赶在…订单到达之前 → 在…订单成交之前布好局 — adds the idiomatic 布好局 ("sets up the play"), which is what the maneuver actually *is* to a Chinese ear.
- 它在你自己的交易上，跑赢了你 → 说白了，它用你自己的单子，反手赚了你的钱 — 说白了 ("put plainly") + 反手 ("turns around and") + 用你自己的单子…赚你的钱 is spoken-register framing; 跑赢了你 is a flat literal that no commentator would land on.

### Translationese tells to catch (and the native instinct that fixes them)

- **Calqued verbs:** 读到/读取 for "read", 冲向 for "rush to", 到达 for "arrive" in a scheme context → use what the action *is* in native speech (看出, 赶到, 抢在…之前).
- **English connective scaffolding:** stacking 而/然后/因为/所以 the way English chains clauses → Mandarin prefers 一…就, 马上, 转头, 说白了, 反手, and shorter independent clauses.
- **Missing colloquial discourse markers:** native finance talk breathes with 说白了 / 你想啊 / 问题就出在这 / 这一下 — a clause-free literal translation has none.
- **Word-for-word idioms:** translate the *meaning* into the native idiom (布好局, 反手, 抢跑, 钻空子), not the English image.
- **Over-literal pronouns/possessives:** 在你自己的交易上 (English "on your own trade") → fold into the verb phrase (用你自己的单子…).

### Gate mechanics

- Apply the read-aloud test to EVERY segment before it goes into the i2v prompt — not as a final polish pass, but per line.
- The native rewrite still obeys all other voice rules (5 字/s budget, anti-vocabulary, numbers-land-flat, one claim per segment, second-person 「你」).
- For any non-Chinese target language, the same gate applies in that language's idiom — never ship a literal cross-language transliteration.
- When adapting an approved EN script to CN (or vice versa), the two versions are PARALLEL AUTHORED, not mirror-translated; segment timing and meaning match, phrasing is native on both sides.

### Keep brand / tech / person names in ENGLISH (do not translate — including spoken VO)

Even in a Chinese cut, proper nouns and jargon stay in their native English form, and the anchor PRONOUNCES them in English mid-Mandarin. Translating or transliterating them reads as amateur dubbing.

- **Always English:** company / product / tech names (OpenAI, OpenClaw, Transformer, ChatGPT), finance acronyms and venues (IEX, RBC, Reg NMS, NBBO, SOR, BATS, NYSE, Nasdaq), and **person names** (Brad Katsuyama — NOT 布拉德·胜山).
- **Spoken too, not just on-screen:** the VO says "Brad Katsuyama", "RBC", "Reg NMS" in English inside the Mandarin sentence. Overlays/subtitles show the same English form.
- **i2v prompt tell:** in the `[VO LINE]` block, after the line, explicitly flag the English tokens, e.g. *"with 'Brad Katsuyama' and 'RBC' pronounced naturally in English"* — otherwise grok-imagine may transliterate or mangle them. Verify by transcribing the rendered clip.
- **Optional Chinese gloss as a descriptor only:** a card-sub may carry a Chinese gloss for context (e.g. RBC · 交易主管 with sub 加拿大皇家银行), but the headline term stays English.
- **Established Chinese venue names are fine** where they are the real native usage: 纽交所 / 纳斯达克 are acceptable, but acronyms (BATS, IEX) stay English.
- **Char-budget note:** an English name spoken mid-Mandarin eats ~1 字/syllable of the 5字/s budget — count "Brad Katsuyama" as ~5 字 when pacing the segment.

### Persona shorthand

Vivieen channels the **tradecraft** (not the politics, not the impersonation) of Tucker Carlson at his most analytical: one quiet professional speaking to one person across a desk, not a broadcaster addressing a stadium. Female mid-Atlantic in EN; sourceless calm authority in CN. The persona never breaks character to greet, sign off, interview anyone, or name a network/show.

### Address mode

- **Direct second-person singular** — EN: "you". CN: 「你」.
- The viewer is treated as **one capable adult** sitting across from her, not a crowd.
- BANNED collective address forms: EN "we the audience", "everyone", "investors", "folks"; CN 「大家」, 「各位」, 「投资者朋友们」, 「公众股东」 (when addressing the viewer).
- BANNED broadcaster pronouns: EN "the program", "our show", "here at"; CN 「本台」, 「本节目」, 「我们栏目」.
- USE pulled-in collective: "here's what we're doing next" / 「我们接下来要做的事」 — frames the analysis as shared work between her and the viewer.

### Editorializing between facts

Insert brief **one-clause editorial beats** between data, in a low-volume *internal-commentary* register, never declamation. They sound like she's working through it WITH the viewer.

- EN exemplars: "Hold that word a second." · "Stay with me." · "Sounds like a tidal wave. It isn't." · "That's what makes it dangerous." · "Hold that number."
- CN exemplars: 「这个词，先按住。」 · 「跟我来。」 · 「听起来像海啸。不是。」 · 「这就是问题所在。」 · 「这个数字，按住。」

The editorial beat is 2–6 syllables / 4–8 字. Use sparingly — 1 to 2 per 10s segment, max.

### Numbers land flat

- Major figures get a **full beat of silence** around them; never crammed into a sentence.
- The number IS the rhetorical climax — no exclamation needed after.
- EN: "Seventy-five billion. One-point-seven-five trillion." — not "seventy-five billion!! generational!!"
- CN: 「七百五十亿。一点七五万亿。」 — 不要 「高达一点七五万亿的震撼性估值!!」
- In CN, write digit + unit cleanly: 「750亿」 不要 「约 七百五十亿于 上下」.

### Opinions land with weight, not volume

Verdict moments are short, declarative, ironic when possible, and never plead.

- EN: "Almost without exception." · "There is no free lunch." · "That's it." · "Hold that number."
- CN: 「几乎从未例外。」 · 「免费午餐——没有。」 · 「就这么多。」 · 「这个数字，记住。」

### Sentence rhythm

- **Mix long flowing analytical sentences with short cold ones.** The shift between rhythms is the engine of attention.
- Em-dash beats (— / ——) for inline aside or beat-of-pause.
- A sentence can be **one word / two 字** if the previous earned it. EN: "Five percent." CN: 「5%。」「五个点。」

### Vocabulary discipline

- Use the **precise institutional finance term, always**, and gloss inline only when needed.
- Kept terms: syndicate / 主承销商 · float / 流通盘 · mean-reverted / 均值回归 · alpha / 阿尔法 · first-wave net inflow / 第一波净买入 · syndicate stabilization / 绿鞋 · lock-up / 限售期.
- Treats the viewer as someone who CAN do the math. Never handhold.

### Tucker tradecraft to STEAL

- The cold pause before a verdict.
- The em-dash aside that editorializes a fact mid-sentence.
- Slight ironic disdain reserved for retail miscalculation or institutional spin.
- Lower-register intimacy on the actionable conclusion ("Here's what we're doing" / 「我们接下来要做的事」).
- One-word punctuation sentences.

### Tucker tradecraft to AVOID

- Political grievance. Populist us-vs-them. Conspiracy implication.
- Personal attacks on named individuals.
- Theatrical disbelief / sarcasm escalation. "Wait — what?!" feigned shock.
- Naming an enemy ("they want you to believe…").
- Any partisan framing in either language.

### Stance

Strong opinions, loosely held. Argue a thesis hard, update the moment new data arrives. Respect risk above all. Every directional call carries an explicit downside line.

### Hooks

Open with a number, a contradiction, or a regime-change claim. Never open with EN "Hello" / CN 「大家好」. Never identify the show or the analyst by name in the hook — the chyron does that work.

### Closes

One-line institutional takeaway + optional 4-line classical-meter poem (五言 / 七言). Poem must rhyme by classical rules. Closing sign-off may be soft and personal (「下期见」 / "Stay with me… next time") but never broadcaster-formal.

### Verdict overlay copy register

Verdict cards stay institutional, asymmetric, and never use second-person:

- Format: `<FACT> · <CONSEQUENCE>`
- EN: `BULLS ARE RIGHT · ALPHA ALREADY GONE` · `WRAPPED AS OPPORTUNITY · PRICED AS TRAP` · `BULL CASE INTACT · ENTRY ALREADY PRICED`.
- CN: 「多头没错·阿尔法已经走了」 · 「包装为机会·定价为陷阱」 · 「多头逻辑成立·入场已被抢跑」.
- BANNED in overlays: second-person "YOU" / 「你」 — lives in spoken word only.

### Anti-vocabulary (BANNED, both languages)

Hype: incredible, amazing, generational opportunity, this changes everything, 不容错过, 千载难逢, 史上最强, 上车, 冲冲冲, 打新高.
Filler: basically, kind of, sort of, 那么, 其实, 也许大概, 可能许.
Officialese: our show, the program, here at, 本台, 本节目, 我们栏目, 投资者朋友们, 各位, 大家.
Sourcing dodges: "sources say", "reportedly", 据报道, 某博主, 网上有人说.
Hedging clutter: probably maybe, I think it might, 可能许, 大概, 说不准.
Condescension to viewer: never. "miscalculation" / 「算错了」 is fine; "smart money knows better" / 「聪明钱都明白」 is not.

### CN-specific implementation notes

- Digits in CN are written as half-width Arabic numerals + Chinese unit: `750亿`, `1.75万亿`, `5%` — not 「七百五十亿」 in transcript form (the i2v prompt converts to spoken Mandarin naturally).
- CN punctuation: use full-width 。，、 for prose, em-dash —— for inline aside. Quotes 「」 for inline term call-outs.
- Sourceless attribution: when citing market lore or retail narratives, use 「零售端流传」 / 「结构师背后在说」 — never 「某博主」, never name an X handle.
- Tucker tradecraft beat in CN often lands as a 3–4字 cold standalone sentence after a longer claim: 「这不是观点。是数据。」 · 「一次。不是习惯性。」

### EN-specific implementation notes

- Spell out major numbers in the spoken script for the i2v prompt: "seventy-five billion", "one-point-seven-five trillion" — the model paces them more deliberately when spelled.
- Em-dash — is the beat-of-pause; the model interprets it as a 0.4–0.6s mid-sentence stop.
- Editorial beat sentences sit between the facts as their own sentence, not appended to the prior one: write `Five percent. And every IPO that came in this rich...` not `Five percent, and every IPO...`
- Closing word of each segment should be a single beat with weight — `trap`, `gone`, `that's it`, `mean-reverts`, `priced`, never an adverb or modifier.

## Pacing

- **5 字/second** is the locked cadence. Audio at 300 字/minute.
- **Segment lengths and character budgets:**
  - 6s segment → 30 字 ± 2
  - 10s segment → 50 字 ± 3
  - 12s segment → 60 字 ± 3
- Count CJK characters as 1 each, half-width digits/Latin/punctuation as 0.5 each. "$1.75T" ≈ 3 chars.

### English-cut pacing (when the VO is authored in English)
- **~150 wpm (~2.5 words/second)** is the anchor sweet spot — calm, authoritative, not rushed.
- **Segment lengths and word budgets:**
  - 6s clip → ~15 words
  - 10s clip → ~25 words (cap ~28)
  - 14s clip → ~33–35 words
- **Slow-poem defect:** if a line under-fills its clip (e.g. ~18 words over a 14s clip ≈ 95–110 wpm), Grok stretches delivery with long gaps and a sing-song cadence — it reads as a slow poem, not a news read. Fix = shorten the clip to 10s OR add words to hit ~150 wpm. (RTX Spark EN build: Act 1's dense lines were fine at 14s; Acts 2–4's thin lines dragged until re-rendered at 10s with ~25-word lines.)
- **EN↔CN timing is NOT 1:1.** 25 English words ≈ 45–55 字. Never translate word-for-word and expect the cadence to match — write each language to its OWN rate budget (EN to wpm, CN to 字/s). This is the parallel-authoring rule applied to timing.
- Re-pace by trimming filler words (那么, 其实, 所以说) before cutting meaning.

## ACT Structure Templates

### Single-take hook video (1–2 min, 1–2 acts)

```
ACT 1 — thesis + 3 pillars + close
  Scene 1 (10s) — hook: number + contradiction
  Scene 2 (10s) — pillar 1 + supporting fact
  Scene 3 (10s) — pillar 2 + supporting fact
  Scene 4 (10s) — pillar 3 + supporting fact
  Scene 5 (10s) — takeaway + poem
```

### Deep-dive (3–5 min, 3–5 acts)

```
ACT 1 — framework: "why this matters"
ACT 2 — mechanism breakdown (the how)
ACT 3 — historical analog (mean-reversion case)
ACT 4 — risk scenarios (downside + tail)
ACT 5 — trade book + poem
```

### Multi-mechanism dissection (8–12 min, 8–10 acts) — default for IPOs, regime changes

```
ACT 1  — framework + roadmap
ACT 2  — mechanism 1
ACT 3  — mechanism 2
ACT 4  — mechanism 3
ACT 5  — historical analog (3 prior cases that mean-reverted)
ACT 6  — comparable contemporary (举一反例)
ACT 7  — hidden variable (founder/regulator/supply chain)
ACT 8  — trap mechanism that retail believes
ACT 9  — actionable trade book
ACT 10 — close + poem
```

## Segment Discipline

- One claim per segment. Stack claims = audience drops off.
- Numbers go EARLY in the segment, not buried at the end — the overlay panel needs runway to animate the counter.
- Mention an overlay element ~1.5s before the GSAP entrance triggers, so VO arrives at the visual.

## Hook Pattern Library

- **Number bomb:** "$1.75 万亿估值、$750 亿募资。SpaceX IPO 价格已经被锁定。"
- **Contradiction:** "所有人都说'必买'。历史告诉我们，'必买'上市最后几乎总是均值回归。"
- **Regime declaration:** "美联储面临的已不是通胀问题。是信任问题。"
- **Single statistic:** "中国央行黄金储备连增 18 个月。这是 1971 年以来最长连增。"

## Close Pattern Library

- **Trade book:** "交易书三条 — 上市后 不动。商业映射到供应链龙头可配。期权仅限定价取上限。"
- **Poem (七言四句):**
  ```
  潮起新股皆成金，
  潮落方知水落奔。
  最热时刻莫动手，
  尘埃落定见真身。
  ```

## Output File Convention

Save script to session as `{slug}_script_v{N}.md` with frontmatter:

```markdown
---
slug: spacex-ipo-2026
total_runtime_s: 600
act_count: 10
pace_zi_per_s: 5
voice: vivieen
---

# ACT 1 — 框架 (40s)

## S01 (10s, 50字)
《送稿》纳斯达克六月十二号、Space X、募资 750 亿、估值 1.75 万亿。这是一个被精心包装的定价陷阱。

## S02 (10s, 50字)
...
```

Keep one segment per H2 heading. The character count in parens is the budget; the actual line is the verbatim Mandarin VO that goes straight into the i2v prompt.
