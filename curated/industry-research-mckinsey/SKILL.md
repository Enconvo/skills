---
name: industry-research-mckinsey
description: "Conduct rigorous, McKinsey-style industry / sector research and produce a structured research report. Use when the user says /industry-research-mckinsey or asks to research an industry/sector/market/value chain, wants market sizing (TAM/SAM/SOM), competitive landscape, value-chain / industry-chain analysis, profit pools, demand-supply dynamics, industry drivers, or trend/outlook analysis, or asks for a 行业研究 / 产业研究 / 行业报告 / 赛道分析 / 投研报告 / industry report / sector deep-dive / market analysis. Also fires when the user wants to find supply bottlenecks, pricing-power chokepoints, or the source of excess returns (超额收益) along a value chain (the 产业投资人 / bottleneck lens). Bilingual: follows the user's language. Do NOT use for company-only financial modeling unrelated to an industry, or for pure document formatting."
version: 1.0.0
author: maneai
category: research
user_invocable: true
metadata:
  short-description: McKinsey-method industry research with a bottleneck / excess-return investing lens (bilingual)
---

# Industry Research — McKinsey Method (麦肯锡式行业/产业研究)

## What this skill does

Produces a **structured, hypothesis-driven industry research report** built on the
McKinsey problem-solving method, fused with an **industry-investor "bottleneck" lens**
(find where supply is scarce while demand already exists — the real source of excess
returns / 超额收益, rather than chasing hype / 风口).

The skill is **bilingual**: detect the user's language from their request and write the
report and section headings in that language (中文 or English). Keep proper nouns,
ticker-like names, and standard framework names recognizable in both.

## Core principle (读懂这一条就够了)

> **找瓶颈，不是找风口。** The excess return lives at the chokepoint of a value chain:
> the node where **demand is already present but supply is structurally scarce**, so that
> node holds pricing power. Map the chain, locate the chokepoint *before* institutional
> money rotates in, and you have a thesis. Chasing the hottest, largest, most-crowded part
> of the market ("the model", "the風口") is following crowd sentiment, not finding edge.

This principle is operationalized in `references/bottleneck-investing-lens.md`. It is the
distinctive module of this skill and should always be applied when the user's intent is
investment-oriented (赛道/投研/选股/产业链). For neutral strategic research it becomes an
optional "Where does value concentrate?" section.

## When to ask before you run

Before producing the full report, confirm scope **only if these are unclear** — otherwise
infer sensible defaults and state them:

1. **Subject & boundary** — which industry/sub-sector, geography, and time horizon?
2. **Purpose** — strategic/market-entry research, or investment thesis (changes how heavily
   the bottleneck lens is weighted)?
3. **Depth & length** — quick scan (2–3 pages) vs. deep-dive (10+ pages)?
4. **Output format** — Markdown (default), Word (.docx via the `docx` skill), or slides
   (.pptx via the `pptx` skill)?

If the user gave enough to proceed, do not stall — pick defaults (their language, both
strategic + bottleneck lens, ~6–8 page Markdown deep-dive) and note them in one line.

## Workflow (执行流程)

Work **top-down and hypothesis-first** — the McKinsey way. Do NOT data-dump then summarize.

### Step 0 — Frame the question (MECE issue tree)
State the central question, break it into a MECE issue tree, and write **2–4 starting
hypotheses** you will try to confirm or kill. Everything downstream serves these.
See `references/mckinsey-frameworks.md` §1–2.

### Step 1 — Gather evidence (research)
Use `WebSearch` + `web_fetch` (and any connected data MCPs). Triangulate every key number
from ≥2 sources. Prefer primary sources: regulators, statistical bureaus, company filings
(10-K/年报/招股书), industry associations, trade press. Log source + date for each material
claim — these become citations. See `references/data-sources.md` for where to look.

### Step 2 — Size the market (TAM / SAM / SOM)
Do **both** top-down and bottom-up sizing and reconcile the gap. Show the formula and every
assumption. State the CAGR and what drives it. See `references/mckinsey-frameworks.md` §3.

### Step 3 — Map the value chain / industry chain (价值链/产业链)
Lay out the chain end to end (upstream → midstream → downstream). For each node estimate
**value-add, margin, concentration (HHI / top-N share), and who has pricing power**. This
produces the **profit pool**. See `references/mckinsey-frameworks.md` §4.

### Step 4 — Structure & competition
Apply **Porter's Five Forces** and **PESTEL** for drivers; profile the key players and
market structure (fragmented vs. consolidated). See `references/mckinsey-frameworks.md` §5–6.

### Step 5 — Apply the bottleneck lens (核心增值模块)
Walk the chain and find the **chokepoint**: node with scarce/constrained supply + present
demand + high switching cost + pricing power. Trace demand *upstream* until supply gets
scarce (the video's "AI → not the model → … → laser chips → ever scarcer supply" move).
Assess **timing**: is institutional money already in, or is this ahead of the rotation?
Full procedure + scorecard in `references/bottleneck-investing-lens.md`.

### Step 6 — Synthesize (Pyramid Principle)
Lead with the **answer first**, then supporting arguments, then evidence. Every section must
end with a **"So what?"** — the implication, not just the fact. Add scenarios (bull/base/
bear) and explicit risks/disconfirming evidence. See `references/mckinsey-frameworks.md` §7.

### Step 7 — Assemble the report
Fill `assets/report-template.md` in the user's language. Then:
- **Markdown** → write the `.md` directly to the output folder.
- **Word** → read `docx` SKILL.md and build the `.docx`.
- **Slides** → read `pptx` SKILL.md and build the deck.
Always end with a **Sources** section (Title — publisher — date — URL).

### Step 8 — Verify (do not skip)
Re-check every headline number against its sources, confirm top-down vs. bottom-up sizing
reconcile, and stress-test the central thesis with the strongest counter-argument. Flag any
figure you could not corroborate as *[unverified]* rather than dropping or guessing it.

## Quality bar (麦肯锡标准)

- **MECE** — no overlaps, no gaps in any breakdown.
- **Hypothesis-driven** — conclusions stated up front, then defended.
- **So-what discipline** — every chart/number carries an implication.
- **Quantified** — ranges and assumptions shown, not vague adjectives.
- **Triangulated & cited** — material claims sourced ≥2x, dated.
- **Falsifiable** — name what would prove the thesis wrong.

## Anti-patterns to avoid

- Data-dumping then a thin summary (bottom-up storytelling).
- Chasing the most-hyped node and calling it a thesis (跟风口 ≠ 研究).
- Single-source numbers presented as fact.
- Five Forces / PESTEL as a filled-in checklist with no "so what".
- Burying the answer at the end.

## Reference files

- `references/mckinsey-frameworks.md` — issue trees, MECE, market sizing, value chain,
  profit pools, Five Forces, PESTEL, Pyramid Principle, scenarios.
- `references/bottleneck-investing-lens.md` — the 产业投资人 bottleneck method, chokepoint
  scorecard, upstream-tracing, institutional-rotation timing.
- `references/data-sources.md` — where to find credible industry data (global + China).
- `assets/report-template.md` — the report skeleton to fill in.
