# THEMES.md — exhaustive token tables

All three themes share the layout, timeline, and storyboard. Only these tokens change. Values are the production-locked ones from the EnConvo kit. (Minimal + Line Art also drive the 50.5s VO scaffold in `../scaffold/`.)

## Shared layout tokens (theme-independent)

| Token | Landscape | Vertical |
|---|---|---|
| Canvas | 1920×1080 | 1080×1920 |
| Panel `.screen` | 1260×709 | 1000×563 |
| Panel x-center | 30% / 70% (alt) | 50% |
| Panel y-center | 42% | 33% |
| Panel tilt | rotateY ±10→±6, rotateX 5 | same |
| Caption | side, width 560, left/right 6%, top ~36% | below, centered, top ~58–60% |
| Title size | 56px | 66–68px |
| Mega size | 112px | 104px (2 lines) |
| Montage panel center | 50% / 41% | 50% / 34% |
| fps / duration | 30 / 42s | 30 / 42s |

---

## AURORA (dark)

| Role | Value |
|---|---|
| Stage bg | `radial-gradient(120% 88% at 50% 40%, #0a0d16, #06070d 50%, #030308)` |
| Orb (primary) | radial `hsla(226,96%,70%,.92) → hsla(250,90%,58%,.5)`, blur 66px, `hue-rotate(var(--orbHue)deg)` |
| Orb hue keyframes | `--orbHue` 0 → 22 (t9) → 52 (t20) → 92 (t26) → 70 (t36) = blue→violet→magenta |
| Oil-slick | conic `#4de8ff,#7a6bff,#ff5ec4,#ffd76a,#58ffcf`, blur 130px, opacity .09 |
| Grain | fractalNoise SVG, opacity .045, screen |
| Vignette | `radial(120% 100% at 50% 42%, transparent 52%, rgba(0,0,0,.62))` |
| Ink | `#fff` |
| Eyebrow | `#aeb9ff`, bar gradient `#6f7bff→#c07bff` + glow |
| Accent (CTA/url) | gradient `#9fb4ff→#d59bff` |
| Chromatic split | `.chroma` text-shadow `.018em 0 rgba(255,44,120,.42), -.018em 0 rgba(0,204,255,.42), 0 0 40px rgba(150,140,255,.34)` |
| Panel shadow | `0 70px 170px -36px rgba(70,90,240,.6), 0 0 0 1px rgba(255,255,255,.10)` |
| Chip | text `#7dffb0`, bg `rgba(60,220,130,.14)`, border `rgba(90,240,150,.5)`, glow |
| Command-bar pill | `linear(#1a1c26,#0b0c12)`, border `rgba(255,255,255,.10)`, blue drop shadow |
| Logo | white ribbon PNG, chromatic drop-shadows via `--ca` (16→3 on entrance) |
| Keyword row opacity | ~0.10 |

## MINIMAL (light, Notion-white)

| Role | Value |
|---|---|
| Stage bg | `radial-gradient(130% 100% at 50% 26%, #FAF9F6, #F4F3EF 46%, #EEEDE8)` |
| Whisper radial | `rgba(92,112,210,0.06) → transparent`, blur 30px (subtle life; slow drift only) |
| Vignette | `radial(125% 105% at 50% 40%, transparent 60%, rgba(22,22,30,.055))` |
| Ink (title) | `#1A1915`; mega `#131210`; head `#524F49` |
| Secondary | `#6B6862` (ticks, eyebrow label) |
| Muted | `#8A867E` (kicker, cta sub) |
| Accent (single) | indigo `#3B5BDB` (eyebrow bar, url, `.sep`, caret, dot) |
| Chromatic split | **none** (`.chroma { text-shadow:none }`) |
| Hairline | `rgba(22,22,28,0.09)` |
| Panel = floating card | bg `#fff`, `0 60px 130px -42px rgba(20,22,44,.34), 0 8px 24px -12px rgba(20,22,44,.18), 0 0 0 1px rgba(22,22,28,.08)` |
| Chip | text `#157F4C`, bg `rgba(21,127,76,.10)`, border `rgba(21,127,76,.34)` |
| Command-bar pill | bg `#fff`, border `rgba(22,22,28,.09)`, soft shadow, indigo dot/caret |
| Logo | white ribbon PNG **inside dark app-icon tile**: `linear(158deg,#2B2B34,#17171B)`, radius 44–46px, `0 34px 80px -26px rgba(22,22,34,.5)`, img width 58% |
| Keyword row opacity | ~0.055 |
| Removed vs Aurora | orb hue-shift, conic slick, grain, all glows, chromatic split |

### Minimal contrast notes
Near-black ink on warm paper ≈ 13:1 (excellent). Keep secondary at `#6B6862` (~4.8:1, passes AA). `#8A867E` (~3:1) is acceptable only for tiny decorative uppercase labels; darken to `#706C64` if a WCAG check flags it.

## LINE ART (cream paper, bold navy ink, gold accent)

Editorial / hand-drawn explainer skin (ref: navy line-art illustration). Same layout + timeline as Minimal — implemented as a CSS **override skin** appended to the Minimal body (`scaffold/scripts/make_themes.py`), so every size/position is inherited, not re-declared. Drives the 50.5s VO scaffold alongside Minimal.

| Role | Value |
|---|---|
| Stage bg | `radial-gradient(130% 100% at 50% 26%, #F8F4E9, #F2EEE1 46%, #EBE6D6)` |
| Whisper radial | `rgba(231,182,44,0.08) → transparent` (faint gold warmth) |
| Vignette | `radial(125% 105% at 50% 40%, transparent 58%, rgba(20,26,60,.07))` |
| Ink (title) | navy `#1E2C62`, **weight 800**; mega `#15224E`; head `#49517A` |
| Secondary | muted navy `#5A6488` (ticks, eyebrow label, url, pill placeholder) |
| Muted | `#6A7099` (kicker) |
| Accent (single) | gold `#E7B62C` (eyebrow bar, url dot, `.sep`, caret, pill dot) |
| Chromatic split | **none** |
| Panel = framed clip | `border:4px solid #1E2C62; border-radius:12px;` + **flat-offset** `box-shadow:16px 16px 0 rgba(27,42,99,.15)` (blur-0 = the line-art signature) |
| Chip | text `#7A5B10`, bg `rgba(231,182,44,.20)`, border `rgba(231,182,44,.62)` |
| Command-bar pill | bg `#FBF7EC`, `border:2.5px solid #1E2C62`, flat shadow `7px 7px 0 rgba(27,42,99,.13)`, gold dot/caret |
| Logo | **gold** ribbon PNG on paper, flat-offset navy drop-shadow `7px 9px 0 rgba(27,42,99,.14)` (no tile) |
| Key-glow (D press) | `rgba(231,182,44,.36) → transparent` (gold) |
| Keyword row | color navy `#1E2C62`, `.sep` gold `#E7B62C`, opacity ~0.055 |
| Removed vs Aurora | orb hue-shift, conic slick, grain, all soft glows, chromatic split |

### Line Art contrast notes
Navy `#1E2C62` on cream `#F2EEE1` ≈ 9:1 (excellent). Muted navy `#5A6488` ≈ 4.6:1 (passes AA). Gold `#E7B62C` is an **accent only** — never body text on cream (fails AA); it lives in bars, dots, separators, and tinted chip backgrounds.

### Adding a fourth theme
**Line Art** is the worked third theme, and it shows the cleanest method: instead of cloning a whole template, append a CSS **override skin** that re-declares only the changed tokens (see `scaffold/scripts/make_themes.py`), so the layout is provably identical to the base. (Cloning a full template and changing only this token set also works.) Good candidates: "Mono" (grayscale + single warm accent), "Editorial" (serif display + cream), "Neon-grid" (dark + synthwave). Re-run the quality checklist — contrast is the usual failure on light variants.
