# Harvard Review

> Editorial business essay shell. Harvard Business Review × Pentagram × Atlantic essay register.

**Use for:** business essays, executive education microsites, case studies, thought leadership, B-school argument pages, strategy whitepapers.

## DNA

- **Paper-on-ink**, not ink-on-paper. Cream background, ink body, **Harvard crimson** as the sole accent.
- **Type does all the work.** Fraunces (display + body, variable opsz/SOFT axes) + Inter Tight (kickers, byline, mono-feel labels). No mono font, no third family.
- **Hero is typographic** — italic Fraunces "Big Idea" headline, one accented word in crimson. No 3D shader, no photograph required.
- **Modules carry hanging Roman numerals** (I · II · III) in italic crimson serif. Editorial register, not corporate.
- **The "Idea in Brief" callout** is HBR's signature — implemented as the canonical equation section, with the dark ink block and 3 numbered points.
- **Sticky thin masthead** (Tier B navigation) with crimson top rule, mono uppercase TOC links, section-symbol § active marker, hairline scroll progress.

## Editorial details (§0.5 of SKILL.md)

This shell hits **8 of 10** items in the checklist:

- ✅ Drop cap on every module's lede paragraph (italic crimson Fraunces)
- ✅ Marginalia rule — 1px crimson left rule next to italic editor's note
- ✅ Displaced quote glyph — giant `\201C` behind every pull quote, opacity 0.16
- ✅ Hanging Roman numerals in italic crimson serif (I, II, III) for modules; lowercase italic Roman (i, ii, iii) for the brief points + takeaways
- ✅ Em-dash flanked label (`—— END OF THE ARGUMENT ——`)
- ✅ Colophon in footer — italic Fraunces sentence: "Set in Fraunces and Inter Tight. A quarterly of business and decision."
- ✅ Ligature-aware variable-axis typography — every Fraunces block sets `font-variation-settings: "opsz" N, "SOFT" M`
- ✅ Folio edition mark in masthead — "Vol. CII · №3 · Spring 2026"
- ⬜ Plate folios (no photographs in this shell)
- ⬜ Vertical rotated mono captions (no gutter figures)

## Section IDs and scrollspy aliases

This shell uses HBR-natural section IDs that don't match the canonical aliases. Per SKILL.md §6 B17, the scrollspy resolves these locally:

| Canonical | This shell's ID | Reason |
|---|---|---|
| `#hero` | `#hero` | matches |
| `#curriculum` / `#articles` | `#article` | HBR essays have one article, not a list |
| `#equation` | `#brief` | the "Idea in Brief" IS the cinematic-block equation here |
| `#takeaways` | `#takeaways` | matches |

The scrollspy script at the bottom of `index.html` reads section IDs directly from the nav `href` attributes, so no init-script alias map is needed — the wiring is local to the shell.

## Palette

| Token | Default | Role |
|---|---|---|
| `--brand-1` | `#f5f1ea` | paper cream (page bg) |
| `--brand-2` | `#161311` | ink black (body, Idea-in-Brief bg) |
| `--brand-3` | `#a51c30` | Harvard crimson (accent) |
| `--brand-4` | `#7a0a13` | deep crimson (CTA hover) |
| `--brand-5` | `#5c5852` | warm gray (meta, lede, captions) |

`init_project.py --palette palette.json` rewrites all five via regex; the named aliases (`--paper`, `--ink`, `--crimson`, etc.) downstream pick up the new values automatically.

## When NOT to use this shell

- Product launches, fragrance, beauty → **Glass Library**
- B2B SaaS / dev tool → **Studio Black** (Linear-flavored)
- Founder portfolio with a photograph → **Editorial Nightscape**
- Indie events / kids / zine → **Riso Pop**
- Anything with a single hero photograph that needs to dominate → wrong register; switch to Editorial Nightscape and apply §6.5 spread typology

## When TO use this shell

- The user gives you an *idea* (a thesis, an argument, a piece of executive-education content) without a photograph.
- The user references HBR, The Atlantic, MIT Sloan Review, Foreign Affairs, or "business essay" register.
- The brief is a strategy whitepaper, case study microsite, or B-school argument page.
