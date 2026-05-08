# Taste Manifesto

The studios this skill is calibrated to. When in doubt, ask "would they ship this?"

---

## North-star studios

### Apple (apple.com)
- Cinematic full-bleed hero, single product as the protagonist
- Restrained type system: SF Pro display + body, mono only for technical specs
- Generous whitespace; scrolls reveal one idea at a time
- Depth is *narrative* — parallax tells you what matters, never decorative
- **Steal:** rhythm of hero → spec → callout → spec → footer; whitespace as content

### Pentagram
- Editorial confidence; type is the brand
- Hierarchy through scale + weight, not color
- One photo per page does 80% of the visual work
- **Steal:** typographic hierarchy without ornament

### Bureau Borsche
- Magazine sensibility: tension between display serif and mono labels
- Color used as accent only — typically one warm + one cool, sparing
- Italic body voice
- **Steal:** display-serif + mono-kicker pairing; restrained color

### Linear (linear.app)
- Calm dark UI, monochromatic + ONE electric accent (purple/blue)
- Micro-grid alignment — every edge lines up with another
- Subtle ambient gradient backdrops, never gradient text
- **Steal:** dark mode done right; electric accent earning its place

### Vercel / Geist
- Charcoal-on-paper minimalism
- One tasteful gradient per page, used once, on the hero
- Geist Sans + Geist Mono — engineering-aesthetic
- **Steal:** restraint; mono font as voice not decoration

### Stripe (stripe.com)
- Information-dense without crowding
- Subtle gradients on the hero (the iconic Stripe gradient)
- Cards earn their borders — only when they group meaningfully
- **Steal:** dense-but-breathable layouts; "earned" containers

### Klim Type Foundry (klim.co.nz)
- Type-specimen aesthetic — the website IS the type sample
- Vertical-axis numbers, ligatures, italic as voice
- Dark on cream paper
- **Steal:** type-as-hero; lining figures everywhere

### Order Design / Bloomberg Businessweek
- Brutalist-editorial: rule lines, oversized index numbers, mono kickers
- Italic gold/red accents on cream
- Hard hierarchy — every section announces itself
- **Steal:** numbered modules; mono-kicker + italic-accent pairing

### Aesop / Le Labo
- Sunbleached cream paper + ink
- All-caps tracked kicker labels
- Product-as-still-life photography
- Italic body for descriptions
- **Steal:** cream + ink + clay palette; tracked all-caps labels

### Family.co / Studio Dumbar / Soft brands
- Rounded sans (Söhne, Aktiv Grotesk)
- Soft cream + sage / blush / ochre
- Generous corner radius on cards
- **Steal:** warmth without childishness

### MSCHF / Risograph studios
- Two-color overprint (riso blue + fluoro pink)
- Deliberate registration drift (pink offset 2-4px from blue)
- Halftone textures
- **Steal:** indie energy; controlled imperfection

### Müller-Brockmann / Swiss modernist
- Tight grid, Helvetica/Inter-Tight, red accent
- One image, one type block, one rule
- **Steal:** grid discipline; manifesto pages

### Family.co specifically
- Ambient soft-gradient backdrops (not on text)
- Single hero gesture — one strong idea, executed once
- No scroll-jacking
- **Steal:** ambient gradient as backdrop, never as text fill

---

## Type pairings (battle-tested)

| Display | Body | Mono | Vibe |
|---|---|---|---|
| Fraunces | Inter Tight | JetBrains Mono | Editorial brutalist (lessons, reports) |
| GT Sectra | Söhne | GT America Mono | Bureau Borsche magazine |
| Editorial New | Neue Haas Grotesk | Berkeley Mono | Tech-luxe |
| Tiempos | Inter | IBM Plex Mono | Stripe-flavored |
| Söhne Breit | Söhne | Söhne Mono | Linear-flavored |
| Founders Grotesk | Founders Grotesk | Söhne Mono | Klim-flavored |
| GT Pressura | GT America | GT America Mono | Order Design / brutalist |
| Reckless | Söhne | — | Modern-luxury |
| Migra Italic + Inter Tight | Inter Tight | — | Editorial type-specimen |

**Avoid as primary display:** Inter, Roboto, Open Sans, Poppins, system-ui. These read as Webflow-default and immediately drag the page toward AI-slop.

---

## Anti-studios (do NOT look like)

- **Webflow templates 2022** — cyan-on-dark + glow + glassmorphism + Inter
- **DocuSign / Salesforce SaaS pages** — stock illustrations + KPI cards + blue CTAs
- **Tailwind UI hero blocks** — centered headline + gradient text + soft-shadow rounded card
- **"AI startup" launch pages** — purple→blue gradient text + a spinning cube + "the future of X"
- **ThemeForest agency themes** — parallax hero + slick slider + 3 bullet feature row
- **Bootstrap 4 dashboards** — sidebar + topbar + pie chart card

If you catch yourself building any of these, stop and re-read this file.

---

## The single test

Before shipping, ask:
> "Would Apple's marketing team / Pentagram / Aesop / Linear be happy to put this in their book?"

If the answer is "no" — redesign.
If the answer is "kind of" — the answer is no. Redesign.
If the answer is "yes, and it has its own voice" — ship.
