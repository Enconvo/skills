# Shells

A shell is the page structure + typography + color tokens + section layout. The hero technique slot is the same across every shell, so any shell × any hero combination works (subject to the compatibility matrix in `hero-shaders.md`).

## Editorial Nightscape (default for human/founder)

Proven on the Cleo project. The starting point for personal-brand and founder portfolios.

- **Tone**: editorial magazine, after-hours, intimate-but-authoritative.
- **Type**: Fraunces (display, serif, italic-capable) + Inter Tight (body).
- **Palette**: deep night blue base + warm tungsten amber accent + lipstick rouge for emphasis + cream/pearl for ink. Pulled from photo at runtime via `extract_palette.py`.
- **Layout**: asymmetric 12-col grid; oversized italicized headline left, full-bleed portrait right; vertical rule between manifesto and body; KPIs as a definition list (NOT KPI cards).
- **Sections**: Hero · Marquee ribbon · Manifesto (drop-cap) · Dispatch (3 work cards) · Numbers (definition list) · Quote · Brief Me form · Footer.
- **Decorative motifs**: corner brackets, vignette fades, accent gold rules, film grain overlay.
- **Use when**: personal brand, founder, creative consultant, editorial/agency portfolio.

Lives at `assets/shells/editorial-nightscape/`.

## Glass Library (default for product launch)

Calm, white-space-rich, high-end product showcase. Think Apple `aria-hero` page meets Aesop product page.

- **Tone**: serene, considered, premium.
- **Type**: GT Sectra or Tiempos (serif display) + GT America Mono (caption labels) + Söhne or Inter Tight (body). Free fallbacks: Fraunces + JetBrains Mono + Inter.
- **Palette**: warm bone / cream backgrounds, ink black text, single saturated accent pulled from product. No dark mode default.
- **Layout**: generous whitespace, strict baseline grid, hero centered, captions in mono.
- **Sections**: Hero · Single accent line · Product description (long-form) · Detail grid · Quote · Quiet CTA · Minimal footer.
- **Use when**: skincare, fragrance, hardware product launch, anything where the product is precious.

NOT YET BUNDLED — scaffold next.

## Studio Black (default for B2B SaaS)

Restrained, all-business, subtly luxurious. Stripe-meets-Linear-meets-a-Swiss-design-book.

- **Tone**: serious, confident, no flourishes.
- **Type**: Söhne or GT America (sans, varied weights) + JetBrains Mono (data). Free fallbacks: Inter Tight + JetBrains Mono.
- **Palette**: near-black background (#0E0F12, never #000), single high-contrast accent (electric-blue, sodium-yellow, or oxblood — pick one). White space-aware, not glow-aware.
- **Layout**: precise 12-col grid, no asymmetry, content-dense but airy.
- **Sections**: Hero · Logo bar · Three-column "what we do" · Data table · Long-form quote · CTA · Compact footer.
- **Use when**: B2B SaaS, fintech, infrastructure, agency-of-record sites.

NOT YET BUNDLED — scaffold next.

## Brutalist Index (annual report / press)

Mono-spaced, raw, archive-feeling. Looks like a typewriter who learned web standards.

- **Tone**: institutional, declarative, "this is the record."
- **Type**: ABC Diatype Mono or JetBrains Mono everywhere. Single weight. Maybe one slab serif for headlines.
- **Palette**: bone paper, ink black, single warning red. No gradients. No shadows.
- **Layout**: 8 px hard baseline, strict left-aligned columns, numbered sections, hard rules.
- **Use when**: annual reports, press microsites, manifesto pages, exhibition catalogs.

NOT YET BUNDLED.

## Sunbleached Memo (lifestyle/consumer)

Warm, daylight, magazine-spread. Bay Area summer.

- **Tone**: friendly, sun-warmed, hand-typed.
- **Type**: GT Alpina (serif, italic-strong) + GT America (body). Free fallbacks: Fraunces + Inter Tight.
- **Palette**: cream paper, sun-bleached terracotta, washed sage, navy ink. No black.
- **Layout**: irregular, mixes hand-drawn rules with web grid, photos overlap typography.
- **Use when**: lifestyle, food, travel, consumer-goods stories.

NOT YET BUNDLED.

## Riso Pop (indie/event)

Loud two-spot-color print energy. Risograph posters meet event landing page.

- **Tone**: indie, joyful, "show up."
- **Type**: Authentic Sans + Authentic Serif, or Pally + Roboto Mono. Loud weights, bouncy line height.
- **Palette**: two saturated spot colors (electric pink + cobalt, or fluo orange + bottle green) on bone paper. Halftone overlays.
- **Layout**: stickers, badges, rotated text, deliberate "off-register" misalignments.
- **Use when**: indie events, music releases, comic launches, anything with a beat.

NOT YET BUNDLED.

---

## Adding new shells

A shell folder must contain:

```
assets/shells/<name>/
├── index.html                    # full single-file page (with <script id="hero-technique"> placeholder)
├── i18n/
│   └── en.json                   # default English strings keyed by [data-i18n] attributes
└── (optional) shared.css         # if separating styles
```

Each shell must:
1. Use the same `[data-i18n="..."]` attribute keys so the i18n loader is universal.
2. Provide an empty `<canvas id="hero-depth-canvas">` inside a `<figure>` with `aspect-[3/4]` (3:4 portrait) — heroes assume this slot.
3. Define CSS custom properties `--brand-1` through `--brand-5` so `init_project.py` can write the extracted palette into them.
4. Include the i18n loader script (`<script id="i18n-loader">…</script>`) — see `i18n.md`.
5. Include the hero technique placeholder (`<script id="hero-technique" type="module"></script>`) at the end of `<body>`.
