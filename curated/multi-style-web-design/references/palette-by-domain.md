# Palette by domain

Use when there is no subject photo to extract from. Curated from each domain's *actual* visual vocabulary, not Tailwind defaults.

Format: `name #hex — role`

---

## Finance / banking / markets / trading

```
ink black     #14110f   — primary text
paper cream   #f3ede1   — background
gold-leaf     #b58a3b   — accent (italic, kickers)
old money     #2f5d3a   — positive / growth
oxblood       #6b1f24   — risk / loss
```

Rationale: gold + ink + paper is the actual visual register of finance (Bloomberg Businessweek, FT, Berkshire Hathaway annuals). Not navy + blue.

---

## Beauty / fragrance / wellness

```
cream         #f4ece1   — background
ink           #1f1a16   — text
clay          #c89881   — primary accent
faded peach   #e8b9a3   — soft accent
sage          #a8b29a   — secondary
```

Rationale: Aesop / Le Labo / Byredo. Always warm, never cold.

---

## Tech / dev tool / SaaS

```
paper         #fafafa   — background
charcoal      #0a0a0a   — text
electric blue #2563eb   — accent (used ONCE per page)
slate         #6b7280   — secondary text
warm gray     #f5f5f4   — subtle bg variations
```

Rationale: Linear / Vercel / Stripe. Charcoal-on-paper, NOT cyan-on-dark.

---

## Editorial / press / annual report / lesson microsite

```
ink black     #14110f   — primary
paper cream   #f3ede1   — bg
italic gold   #b58a3b   — accent
oxblood       #6b1f24   — risk / dark callouts
slate         #6b6357   — secondary
```

Rationale: Bloomberg Businessweek + Pentagram. Same as finance because the editorial register overlaps.

---

## Indie / event / zine

```
riso blue     #3552c2   — primary
fluoro pink   #ff5482   — overprint accent
paper         #f4ece1   — bg
ink           #1f1a16   — text
halftone gray #c0bbb3   — texture
```

Rationale: Risograph studios + MSCHF. Two-color logic.

---

## Wellness / kids / craft / soft brands

```
warm cream    #f7efe2   — bg
sage          #9aa896   — primary accent
blush         #e8c4b0   — secondary
ochre         #c89860   — earthy accent
soft ink      #2a2520   — text (warmer than pure ink)
```

Rationale: Family.co / Studio Dumbar. Warmth without childishness.

---

## Architecture / luxury / Japanese-influenced

```
bone          #ece8df   — bg
sumi ink      #1b1715   — text
soft red      #a4322a   — accent (hanko-stamp red)
mineral grey  #7d7a73   — secondary
gold          #b58a3b   — sparingly, for emphasis
```

Rationale: Ryosuke Fukusada / Kenya Hara school. Bone + sumi + a single red.

---

## Hospitality / restaurant / wine

```
cream         #f0e8d8   — bg
deep wine     #4a1c24   — primary accent
ink           #1f1a16   — text
brass         #a08552   — secondary
sage          #8a9685   — soft balance
```

Rationale: trattoria menus + Noma cookbook aesthetic.

---

## Health / medical / clinical (without being sterile)

```
soft white    #fafafa   — bg
deep navy     #0e1e2e   — text
sage          #93a796   — accent (calm)
warm gray     #4a4a48   — secondary
peach (sparing) #f0c8a8 — humanity
```

Rationale: avoids the hospital-blue + green default. Reads as calm-human-clinical.

---

## Music / event / nightlife (dark)

```
near black    #0a0a0a   — bg
paper         #ece5d4   — accent text (cream on black)
crimson       #c2363a   — primary
electric green #66ff66  — strobe accent (used VERY sparingly)
slate         #45433f   — secondary
```

Rationale: club flyer / Resident Advisor / Boiler Room.

---

## Default for "I don't know" / abstract / manifesto

When unsure, use the **editorial** palette. It's the most versatile — works for lesson, essay, manifesto, annual report, founder portfolio. Never wrong.

```
ink + cream + italic gold + oxblood + slate
```

---

## Rules

1. **Always 5 colors.** Not 3, not 7. Five fits the cognitive grid.
2. **One accent earns the loud move.** Don't use both gold AND oxblood as primary accents — pick one.
3. **Background should be warm-paper or cool-ink, rarely pure white.** Pure `#fff` is sterile.
4. **Save to `palette.json` with rationale.** Future iterations need to know why.
