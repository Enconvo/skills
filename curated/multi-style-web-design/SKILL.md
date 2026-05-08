---
name: multi-style-web-design
description: Studio-grade single-page web design with **swappable design shells across 16+ styles** (auto-picked by industry or manually chosen) and an opt-in **3D / motion / special-effects toolkit** (depth displacement, tilt+sheen, glass refraction, volumetric slices, light caustics, particle samplers, three.js on demand). Designs with the taste of a tier-1 studio (Apple / Pentagram / Bureau Borsche / Linear / Vercel / Aesop / Klim / Order / MSCHF). Picks aesthetic direction BEFORE writing code, pulls palette from the actual subject, ships portable single-folder static sites with built-in navigation (3 tiers), 7-language i18n via [data-i18n] slots, and zero build step. Use for personal brand sites, founder portfolios, product landings, company about pages, launch teasers, lookbooks, lesson microsites, annual reports, or any one-page site — or when the user asks for "fancy website", "multi-style website", "3D website", "Apple-style depth", "portrait website", "product landing", "brand site", "公司官网", "产品落地页", or provides hero text + (optional) photo.
---

# multi-style-web-design

> A taste-first single-page web design skill. Designs like a tier-1 studio. Codes like a meticulous engineer. **3D is one tool in the kit, not the entire kit.**

Build a single-folder, single-page site. No build step. No auto-deploy. The user owns deploy decisions. The default output is *web design first*, with 3D / motion as opt-in enhancements that get used **only when they serve the subject**.

---

## 0 · The taste manifesto (read this first)

These are the studios this skill is calibrated to. When in doubt, ask "what would they ship?":

| Studio / brand | What we steal from them |
|---|---|
| **Apple** | Cinematic hero, restrained typography, generous whitespace, depth as narrative not decoration |
| **Pentagram** | Editorial typographic confidence, hierarchy without ornament |
| **Bureau Borsche** | Magazine-grade type, tension between display + body, color as accent only |
| **Linear** | Calm dark UI, monochromatic + one electric accent, micro-grid alignment |
| **Vercel / Geist** | Minimal sans-serif, charcoal-on-paper, tasteful gradients used ONCE per page |
| **Stripe** | Information-dense without feeling crowded; cards that earn their borders |
| **Klim Type Foundry** | Type-specimen aesthetic, vertical-axis numbers, ligatures, italics as voice |
| **Order Design** | Rule-driven brutalism, oversized index numbers, mono labels |
| **MSCHF / Riso shops** | Two-color overprint, deliberate registration drift, indie/event energy |
| **Aesop / Le Labo** | Sunbleached cream + ink, all-caps spaced kicker, product-as-still-life |
| **Linear's marketing site & Family.co** | Ambient gradient backdrops, single hero gesture, no scroll-jacking |
| **Bloomberg Businessweek** | Numbered modules, mono kickers, hard rules, italic gold accents |

Anti-studios (avoid the look of):
- Webflow templates from 2022 (cyan-on-dark + glow + glassmorphism + Inter)
- DocuSign/Salesforce-era SaaS marketing pages
- Default Tailwind UI hero blocks
- "AI startup" launch pages with purple→blue gradient text and a cube
- ThemeForest "agency" themes

If the output looks like any of those, **redesign** — see `references/ai-slop-fingerprints.md`.

---

## 0.5 · Editorial details checklist (the marginalia that separates designed from templated)

Magazine-grade typography and good bleeds aren't enough on their own. The small marginalia is what makes a page read as designed-by-a-human vs templated. Any editorial-register page (Editorial Nightscape, Brutalist Index, Atelier Couture, Reportage, Quartermaster) should hit **at least 5** of these:

- [ ] **Plate folios** — every photograph gets a "Plate I/II/III…" label somewhere (book convention). Mono uppercase, gold accent, e.g. `<em>Plate III</em> · The Gallery`.
- [ ] **Drop cap** on the lede paragraph (`::first-letter { font-size: 1.6em; float: left; padding: 6px 10px 0 0; color: var(--gold); font-weight: 500; font-style: italic; }`).
- [ ] **Marginalia rule** — gold/accent vertical 1px rule next to italic captions or pull quotes (Pentagram annual-report move). `border-left: 1px solid rgba(gold, 0.4); padding-left: 18px;`.
- [ ] **Displaced quote glyph** — for any oversized quoted blurb, place a giant `clamp(220px, 26vw, 360px)` quotation-mark character with `opacity: 0.16` behind the text. Single character, serif italic, accent color.
- [ ] **Vertical rotated mono captions** in gutters. `writing-mode: vertical-rl; transform: rotate(180deg);` for figure stamps like "FIG. IV · Plate III".
- [ ] **Folio edition mark** in masthead — "№ 001 — 2026" or "Vol. I · 2026" in mono, gold accent.
- [ ] **Hanging Roman numerals** (I·II·III·IV in italic gold serif at `font-size: 36px`) for ordered lists when the page has editorial register. NOT mono "— I" tags — those read corporate.
- [ ] **Em-dash flanked labels** ("—— A NOTE FROM YOUR HOST ——") for section dividers. Use `::before, ::after { content: "——"; color: var(--ink-faint); margin: 0 14px; }`.
- [ ] **Colophon** in footer — italic serif, lowercase, a real sentence ("Set in Fraunces, Inter Tight, and JetBrains Mono. Six plates photographed for this edition."). Not a copyright line.
- [ ] **Ligature-aware variable-axis typography** — `font-variation-settings: "SOFT" 30;` on Fraunces titles, `"opsz" 144` on display sizes.

If a page has zero of these, it's a template. If it has 5+, it reads designed.

---

## 1 · Core philosophy

1. **Aesthetic direction BEFORE writing code.** Always declare *what it should feel like* in plain words first ("Aesop pull-out", "Bloomberg Businessweek module", "Linear's calm dark UI") — then build to that brief.
2. **Pull palette from the actual subject** when there is one (photo, logo, product). Otherwise curate from the *domain's vocabulary* (finance = ink/gold/oxblood/money-green/paper, beauty = cream/peach/clay/ink, tech = paper/charcoal/electric-accent).
3. **Type does most of the work.** A serif/sans pair with strong italic + mono labels carries 70% of the design. Get that right before any animation.
4. **Whitespace is content.** Sites that breathe feel premium. Refuse to fill empty space with decorative junk.
5. **Motion is earned, not decorative.** A tilt or parallax must reveal something (depth, hierarchy, attention) — never "because the brief said fancy".
6. **3D is optional.** Many of the best sites this skill produces have **zero 3D** and still feel cinematic.
7. **Shell ⊥ hero ⊥ motion.** Any shell × any hero × any motion level. Always orthogonal.
8. **Honest critique > silent tuning.** If a technique is wrong for the subject, switch techniques and tell the user why.
9. **Single-folder static output.** A folder you can email. No npm install. No React boilerplate (unless explicitly requested).
10. **Verify in real Chrome.** Headless WebGL/canvas screenshots lie.

---

## 2 · Inputs the skill needs

Confirm these 5 if the request is vague. If the user gives a clear brief, infer and proceed.

1. **Subject type** — `human` / `product` / `brand-mark` / `abstract` / `scene` / **`text-only`** (no image, type-driven hero — e.g. a lesson page, an essay, a manifesto)
2. **Site purpose** — short sentence ("personal brand", "skincare launch", "B2B SaaS landing", "finance lesson microsite", "annual report", "indie event")
3. **Brand name + tagline** — for hero typography
4. **Languages** — default `en`; add any of `zh` `ja` `es` `fr` `ko` `ru`
5. **Optional** — explicit aesthetic reference ("like Aesop", "like Linear", "Bureau Borsche-flavored")

For `text-only` subjects: skip image prep entirely. Type *is* the subject.

---

## 3 · Workflow

### Phase 1 — Direction (declare BEFORE coding)

Write a 4-line brief in your reply, in this exact format:

```
Subject:    <type>
Reference:  <studio / brand / movement to channel>
Shell:      <shell name>
Hero:       <hero technique OR "typographic, no 3D">
Palette:    <5 colors named, with the rationale>
```

**Auto-pick rules** (industry → shell). 16 shells, all populated as live variants in `assets/shells/`:

| Industry / use case | Shell | Default hero | Reference DNA |
|---|---|---|---|
| Personal brand / founder (with photo) | **Editorial Nightscape** | A · Depth Displacement | Apple × Klim |
| Product launch (physical product) | **Glass Library** | D · Glass Refraction | Aesop × Le Labo |
| B2B SaaS / dev tool / AI infra | **Studio Black** | none (typographic) | Linear × Vercel |
| Lesson / essay / annual report / finance | **Brutalist Index** | E · Volumetric Slices (typographic) | Bloomberg Businessweek × Pentagram |
| Lifestyle / consumer / beauty | **Glass Library** | F · Light Caustics | Aesop × Le Labo |
| Indie / event / zine / podcast / kids | **Riso Pop** | C · Particle Sample | MSCHF × risograph |
| Manifesto / poster-page / museum | **Swiss Modernist** | none | Müller-Brockmann × Order |
| Wellness / kids / family / craft / mental health | **Soft Organic** | F · low intensity | Family.co × Calm × Headspace |
| Fashion / jewelry / runway / fashion media | **Atelier Couture** | B · Tilt & Sheen | Bureau Borsche × Vogue Italia |
| Creative agency / design portfolio / animation studio | **Studio Spectrum** | none (saturated blocks) | Pentagram × Studio Dumbar × IDEO |
| Sports / athleisure / fitness app / esports | **Stadium** | B · Tilt & Sheen (motion blur) | Nike × Athletics × ESPN |
| Entertainment / streaming / music / film | **Neon Arcade** | F · Light Caustics (gradient mesh) | A24 × Netflix × Resident Advisor |
| Comic / cartoon / animation / kids' IP | **Panel** | none (panel-grid hero) | Cartoon Brew × Adventure Time × Pixar dev |
| Architecture / photography / fine art / luxury real estate | **Gallery White** | none (whitespace + lining figures) | Zaha Hadid × MoMA × Magnum |
| Outdoor / gear / hardware / tools / makers / coffee | **Quartermaster** | none (field-manual stamps) | Snow Peak × Best Made × Ace Hotel |
| AI / ML products / Web3 / futuristic hardware | **Holographic Future** | none (iridescent gradient + bento) | Arc Browser × Linear marketing × Gradient |
| News / longform / documentary / NGO / public health | **Reportage** | none (newsprint + drop caps) | NYT × The Guardian × Magnum |

**3D-skip rule:** if the subject is `text-only` or `abstract` AND the purpose is *informational* (lesson, essay, report), **default to typographic hero with no 3D shader**. Use type weight + size + italics + rule lines as the hero treatment. 3D is opt-in, not opt-out.

### Phase 2 — Asset prep (skip for text-only)

```bash
uv run scripts/prep_subject.py <subject_image> <output_dir> --type <human|product|brand-mark|abstract|scene>
```

Branches:
- **human / product / scene** → downscale 900px wide + Depth Anything V2 → `hero.jpg` + `hero_depth.jpg`
- **product (additional)** → rembg alpha matte
- **brand-mark** → keep PNG/SVG transparency, skip depth
- **abstract** → just downscale
- **text-only** → SKIP entirely

Then palette:
```bash
uv run scripts/extract_palette.py <subject_image> --out <output_dir>/palette.json
```

For text-only / abstract subjects with no image, **curate** the palette from the domain (see §4 palette-by-domain table). Do NOT default to dark-mode-cyan-glow.

### Phase 3 — Pick + initialize

```bash
uv run scripts/init_project.py <output_dir> --shell <shell-name> --langs en,zh,ja [--hero <id>|none]
```

This:
1. Copies `assets/shells/<shell-name>/` into `<output_dir>/`
2. Applies palette to CSS custom properties (`--brand-1` … `--brand-5`)
3. Sets up `i18n/` with the requested languages
4. Injects hero technique block if `--hero` is set; otherwise leaves the typographic hero in place

### Phase 4 — Inject hero technique (only if needed)

| # | Technique | Best for | Avoid for | Performance |
|---|---|---|---|---|
| **none** | **Typographic only** | **Text-only, essays, lessons, reports, manifestos** | — | Free |
| A | Depth Displacement | Human portrait, product on background | Logos, abstracts, text-only | Mid |
| B | Tilt & Sheen | Mid-shot subject, glossy product, single-element heroes | Wide scenes | Free (CSS) |
| C | Particle Sample | Abstract, art-leaning portfolio | Faces (eyes void), readable type | High |
| D | Glass Refraction | Lifestyle, beverage, mood-driven | High-detail product specs | Mid |
| E | Volumetric Slices | Mobile-first, low-GPU, products, **typographic depth** | Fine portrait detail | Low |
| F | Light Caustics | Editorial, beauty, perfume | B2B / corporate / dev tools | Mid |

Hero shaders live in `references/hero-shaders.md`. The **`none`** option is the new default for informational sites.

### Phase 4.5 — Add navigation (mandatory for any page with ≥ 3 sections)

Waterfall single-flow pages with no nav are a regression to 2014. The skill's content scaffold (masthead → hero → modules → equation → takeaways → footer) has 4 anchorable sections; **always wire them up**.

Pick **ONE of three navigation tiers** based on the shell's register:

| Tier | Visual register | Components | Default for these shells |
|---|---|---|---|
| **A — Full** | App-polish, sticky pill nav | Sticky blur-glass nav bar + 4 link pills + active-section dot + scroll-progress bar + kbd hint chip + floating back-to-top | `studio-black` `stadium` `neon-arcade` `holographic-future` `reportage` |
| **B — Editorial** | Sticky masthead-style TOC | Sticky thin masthead + 4 mono uppercase TOC links separated by hairline rules + section-symbol active marker + 1px scroll progress | `brutalist-index` `editorial-nightscape` `atelier-couture` `studio-spectrum` `panel` `quartermaster` |
| **C — Whisper-quiet** | Almost invisible | Right-edge dot rail (5px dots) + tiny scroll-progress hairline; **both fade in only after scrolling past 200px**; original masthead stays untouched | `glass-library` `swiss-modernist` `riso-pop` `gallery-white` `soft-organic` |

**Required structural pieces in every variant** (regardless of tier):
- Section IDs: `#hero`, `#curriculum` (or `#products`/`#features` per content), `#equation` (or whatever the cinematic-block section is named), `#takeaways`
- `html { scroll-behavior: smooth; }` for native smooth scroll
- `section[id], article[id] { scroll-margin-top: 60–80px; }` so anchors don't sit under the sticky nav
- A scrollspy script (~25 lines vanilla JS) that toggles `.active` on nav links as the user scrolls
- Tier A also gets `.show` class toggled on `.to-top` after 600px scroll

**Defensive overflow pattern — mandatory in every shell:**
```css
html { overflow-x: clip; }
body { overflow-x: clip; width: 100%; max-width: 100vw; }
.nav-bar { width: 100%; box-sizing: border-box; }
.nav-bar .nav-inner { max-width: 1280px; margin: 0 auto; } /* centering wrapper */
```
This prevents a wide nav from pushing `body` past the viewport, which would offset every `margin: 0 auto` content section. **Without this, you get the v4 Studio Black bug where Chrome shows content shifted left while Safari renders fine** — different font metrics caused different overflow behavior.

**Tier-A label conventions** — the kbd-style chip on the right of the nav must carry shell-flavored personality:

| Shell | Brand label | kbd chip |
|---|---|---|
| Studio Black | `L01/07` | `⌘K` |
| Stadium | `L01/07` | `GAME 01` |
| Neon Arcade | `EP 01/07` | `NOW PLAYING` |
| Holographic Future | `v1.0` | `⌘K` |
| Reportage | `Section A 01` | `Vol I` |

Generic labels ("Menu", "Section 1") are forbidden — the chip is a microbrand moment.

Full HTML+CSS templates per tier live in `references/navigation-tiers.md`.

### Phase 4.6 — Figure-grid `.fx3d` effect (opt-in for multi-image editorial pages)

When a page carries ≥3 content photographs (any §6.5 spread typology page), opt in to the `.fx3d` shared-physics figure effect to lift photos off the page with **static depth at rest** and **pointer-driven tilt + sheen on hover**. Distinct from §4 hero shaders — those run once on the hero. `.fx3d` runs on every figure container in the article.

**What it does:**
- **Static depth at rest** (visible in screenshots, satisfies critical rule 12): multi-layer `box-shadow` (deep ambient + inset highlight + 1px gold rim) makes each figure float off the page background.
- **Pointer-driven tilt** (±5° / ±4°): mousemove updates `--rx` / `--ry` CSS variables; the container `transform: perspective(1400px) rotateX rotateY` follows the cursor with a 0.18s ease.
- **Pointer-driven sheen**: a `radial-gradient` `::after` with `mix-blend-mode: screen` follows the cursor (`--mx` / `--my`), revealing a soft warm highlight that traces where the user is looking.
- **Image parallax** on hover only: the `<img>` translates `Z(40px)` and `scale(1.025)` against its frame, creating real depth between photo and shadow.
- **Reduced-motion respect**: `prefers-reduced-motion: reduce` retains the static box-shadow lift but drops all transform / sheen.

**CSS skeleton** (drop into shell stylesheet, after the figure typography rules):
```css
.fx3d {
  --rx: 0deg; --ry: 0deg; --mx: 50%; --my: 50%; --lift: 0px;
  --fx-radius: 14px;
  border-radius: var(--fx-radius);
  transform-style: preserve-3d;
  transform: perspective(1400px) rotateX(var(--rx)) rotateY(var(--ry)) translateZ(var(--lift));
  transition: transform 0.45s cubic-bezier(0.2,0.7,0.2,1), box-shadow 0.45s cubic-bezier(0.2,0.7,0.2,1);
  will-change: transform;
  box-shadow:
    0 1px 0 rgba(243,237,225,0.06) inset,
    0 -1px 0 rgba(0,0,0,0.4) inset,
    0 18px 40px -12px rgba(0,0,0,0.55),
    0 40px 80px -20px rgba(0,0,0,0.45),
    0 0 0 1px rgba(212,175,91,0.08);
}
.fx3d > img { border-radius: inherit; transition: transform 0.45s cubic-bezier(0.2,0.7,0.2,1); }
.fx3d:hover { --lift: 6px; transition-duration: 0.18s;
  box-shadow:
    0 1px 0 rgba(243,237,225,0.10) inset,
    0 -1px 0 rgba(0,0,0,0.5) inset,
    0 24px 56px -10px rgba(0,0,0,0.65),
    0 56px 110px -16px rgba(0,0,0,0.55),
    0 0 0 1px rgba(212,175,91,0.18);
}
.fx3d:hover > img { transition-duration: 0.18s; transform: translateZ(40px) scale(1.025); }
.fx3d::after {
  content: ""; position: absolute; inset: 0; pointer-events: none; z-index: 4;
  border-radius: inherit;
  background: radial-gradient(circle at var(--mx) var(--my), rgba(232,201,122,0.18), transparent 40%);
  opacity: 0; transition: opacity 0.35s ease; mix-blend-mode: screen;
}
.fx3d:hover::after { opacity: 1; }
.fx3d.fx3d-round { --fx-radius: 50%; border-radius: 50%; }
.fx3d.fx3d-round::after { border-radius: 50%; }
@media (prefers-reduced-motion: reduce) {
  .fx3d, .fx3d > img { transition: none; transform: none; }
  .fx3d:hover, .fx3d:hover > img { transform: none; }
  .fx3d::after, .fx3d:hover::after { opacity: 0; }
}
```

**JS skeleton** (≈30 lines vanilla, no dependency, drop into the shell's existing inline `<script>`):
```js
(function () {
  if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  document.querySelectorAll('.fx3d').forEach(function (el) {
    var raf = null, lastE = null;
    function apply() {
      if (!lastE) return;
      var r = el.getBoundingClientRect();
      var x = (lastE.clientX - r.left) / r.width;
      var y = (lastE.clientY - r.top) / r.height;
      el.style.setProperty('--rx', ((0.5 - y) * 8).toFixed(2) + 'deg');
      el.style.setProperty('--ry', ((x - 0.5) * 10).toFixed(2) + 'deg');
      el.style.setProperty('--mx', (x * 100).toFixed(1) + '%');
      el.style.setProperty('--my', (y * 100).toFixed(1) + '%');
      raf = null;
    }
    el.addEventListener('mousemove', function (e) { lastE = e; if (!raf) raf = requestAnimationFrame(apply); });
    el.addEventListener('mouseleave', function () {
      el.style.setProperty('--rx', '0deg'); el.style.setProperty('--ry', '0deg');
      el.style.setProperty('--mx', '50%'); el.style.setProperty('--my', '50%');
      lastE = null;
    });
  });
})();
```

**Wiring:** add the `fx3d` class to every figure container that wraps a content photo. For circular portraits (host band, testimonial avatar) add `fx3d-round` alongside.

**Per-figure radius tuning** (drop into the shell stylesheet to override the 14px default):
| Figure size / role | `--fx-radius` |
|---|---|
| Hero figure, closer figure, cinematic 21:9 | `16px` |
| Default full-bleed split (Spread A) | `14px` |
| Tall inset (Spread B), pull-quote inset (Spread D) | `12px` |
| Round portrait (Spread E half-circle) | `50%` |

**Where it earns its place:**
- Multi-image editorial pages (§6.5 spread typology) where the photographs are protagonist-grade and need to *feel* lifted off the dark page background.
- Hosted-edition variants (B21 fix) — makes the host's portraits feel cinematic rather than CMS rectangles.
- Personal brand / founder portfolio sites with 3+ supporting photos.

**Where to NOT use it:**
- Single-hero pages (§4 hero shaders A–F already provide depth there).
- Light-paper shells (Glass Library, Gallery White, Soft Organic) — the dark `box-shadow` reads as muddy on cream paper. Tune the shadow stack to lighter / smaller offsets, or skip.
- Comic / Riso / Panel shells — the flat-color register actively rejects soft 3D depth; the playful flatness *is* the design.
- Newspaper / Reportage shells — newsprint is meant to look 2D. Lifting figures violates the medium.

**Compatibility with §4 hero shaders:** orthogonal. A page can run hero shader B (Tilt & Sheen) on the hero photograph AND run `.fx3d` on every supporting figure below; both share the same physics vocabulary and don't fight each other visually.

Full HTML drop-in + tuning knobs live in `references/figure-fx3d.md`.

### Phase 5 — Translate (if requested)

```bash
uv run scripts/i18n_translate.py <output_dir>/i18n/en.json --langs zh,ja,es,fr,ko,ru
```

The shell loads i18n at runtime via a 30-line vanilla loader (already embedded). Reads `?lang=<code>`, falls back to `navigator.language`, then `en`.

### Phase 6 — Variant exploration (optional)

To compare hero techniques side-by-side, copy the project N times and inject different shaders. The skill **never auto-deploys**.

### Phase 7 — Visual verification (mandatory)

```bash
cd <output_dir>
python3 -m http.server 7531 &
SERVER_PID=$!
sleep 1
open -a "Google Chrome" "http://127.0.0.1:7531/?v=$(date +%s)"   # cache-bust query
sleep 3
screencapture -x /tmp/site_check.png
# inspect screenshot, then:
kill $SERVER_PID
```

**Cache-busting is mandatory** — append `?v=<timestamp>` to bypass disk cache. Without it, the user re-loads stale HTML and reports "no change".

Inspect:
- Shell + fonts render (Google Fonts requires network)
- Hero paints correctly (subject visible OR type rendered with depth)
- i18n switches work (`?lang=zh`, `?lang=ja`)
- **Decorative elements don't bleed into content below the hero** (see §6 known-bug list)

If a technique visually fails for the subject, **flag honestly** and propose a different technique. Do not silently tune.

---

## 4 · Shells (genre menu)

Each shell is a single `index.html` plus optional shared CSS. All shells share the same `[data-i18n]` keys so heroes and i18n are interchangeable.

### Existing
- **`editorial-nightscape/`** — dark, Apple-cinematic, founder/portrait. Proven on Cleo project. Serif headlines + neon accent.
- **`glass-library/`** — calm, wide whitespace, high-end product. Aesop-flavored.
- **`studio-black/`** — restrained B2B, monochrome, mono kickers, no decoration. Linear-flavored.

### To populate
- **`brutalist-index/`** — Bloomberg Businessweek + Pentagram. Ink-on-paper, oversized numbered modules, mono kickers, italic gold accents, hard rules. **Best for lessons, essays, annual reports, editorial microsites.**
- **`sunbleached-memo/`** — Aesop pull-out. Cream paper + ink + clay + faded peach. Sparse, generous, italic body, all-caps spaced kickers.
- **`riso-pop/`** — two-color overprint with registration drift. Indie/event/zine. Risograph texture, halftone, off-register accents.
- **`swiss-modernist/`** — Müller-Brockmann grid. Helvetica/Inter-Tight + tight grid + red accent. For manifestos, single-message pages.
- **`soft-organic/`** — Family.co / Studio Dumbar. Rounded sans + soft cream + sage / blush / ochre. Wellness, kids, craft.

Full visual + content spec per shell in `references/shells.md`.

### Shell content scaffold (every shell ships with these slots)

```
masthead    → small mono kicker, vol/edition number, dot accent
hero        → headline + lede + 4 stat columns (or 3 KPI items)
modules     → numbered editorial sections (works for lessons, features, products)
equation    → single cinematic dark-block "the lesson behind the lesson"
takeaways   → 4 final-thought cards
footer      → mono, restrained
```

This scaffold is **opinionated on purpose**. It's the structure that makes lesson, report, manifesto, and brand pages all feel like they came from the same studio.

---

## 5 · Palette-by-domain (when there is no subject photo)

Never default to dark-cyan. Curate from the domain:

| Domain | Palette (ink + paper + 2 accents + risk) |
|---|---|
| Finance / banking / markets | ink black `#14110f` · paper cream `#f3ede1` · gold-leaf `#b58a3b` · old-money green `#2f5d3a` · oxblood `#6b1f24` |
| Beauty / fragrance / wellness | cream `#f4ece1` · ink `#1f1a16` · clay `#c89881` · faded peach `#e8b9a3` · sage `#a8b29a` |
| Tech / dev tool / SaaS | paper `#fafafa` · charcoal `#0a0a0a` · electric blue `#2563eb` (used ONCE) · slate `#6b7280` · subtle warm gray `#f5f5f4` |
| Editorial / press / annual report | ink · paper · italic gold · oxblood · slate |
| Indie / event / zine | risograph blue `#3552c2` · risograph fluoro pink `#ff5482` · paper · ink · halftone gray |
| Wellness / kids / craft | warm cream · sage · blush · ochre · soft ink (#2a2520) |
| Architecture / luxury / Japanese | bone `#ece8df` · sumi ink `#1b1715` · soft red `#a4322a` · mineral grey `#7d7a73` · accent gold |

Save the chosen palette in `palette.json` with rationale.

---

## 6 · Known bugs / lessons learned (must read before coding)

These came from real builds. Prevent them, don't repeat them.

### B1 · Decorative slabs leaking into content below the hero
**Symptom:** thin black/gold line drawn as a "depth marker" inside the title-stack appears as a strikethrough across the lede paragraph below.
**Cause:** `position: absolute` slab inside a container with `overflow: visible`, positioned with `bottom: -12%` etc., which leaks past the container's box and into siblings.
**Fix:** any decorative slab with negative offsets MUST live inside a container with `overflow: hidden`, OR have its position constrained by `bottom: 0` / `top: 0` so it can't leak. Better: don't add decorative slabs unless they pay rent — the layered headlines alone deliver depth.

### B2 · Empty mono labels look like UI debris
**Symptom:** floating `LAYER · 01` / `DEPTH · ∞` mono labels with no semantic value confuse the user — "what's that, empty meaningless space?"
**Cause:** importing decorative scaffolding from a demo without earning it on the real page.
**Fix:** every visible label must carry meaning *for this site's content*. If a label is just visual filler, delete it. The 3D depth must come from the *content layers themselves* (headline echoes, slabs that frame real content, rules that mark real sections), not from arbitrary "layer" tags.

### B3 · Cache-stale screenshot
**Symptom:** user reloads, sees the old version, says "no change".
**Cause:** Chrome disk cache.
**Fix:** ALWAYS append `?v=<timestamp>` to the URL when re-verifying. Tell the user "Cmd+Shift+R" if they refresh manually.

### B4 · Local server refused after kill
**Symptom:** `127.0.0.1:7531 refused to connect` after a teardown.
**Fix:** either keep the server alive across iterations, OR explicitly tell the user to open the file via `file://` URL — the static site works without any server.

### B5 · Tilt is invisible in screenshots
**Symptom:** "I see no 3D." Because the tilt is pointer-driven, a stationary screenshot captures the rest state.
**Fix:** the hero must show depth even at rest. Use static z-translated layers + drop shadows + subtle blurs. The pointer interaction *enhances* depth — it must not be the *only* source of depth. If a technique only "works" in motion, it's not the right technique for a screenshot-driven web.

### B6 · Tilt-Only on type with no photo = "3D-adjacent, not 3D"
**Symptom:** user expects visible 3D, sees only a faint sheen on type.
**Fix:** for typographic heroes, prefer **technique E (Volumetric Slices)** with multiple z-stacked headline layers (back: blurred ghost, mid: gold ghost, front: sharp ink with drop shadow). Tilt-only is *not* enough on type without a photo.

### B7 · `mix-blend-mode: multiply` on translucent gold over cream
**Symptom:** middle-layer gold ghost looks brown/muddy on cream paper.
**Fix:** use `mix-blend-mode: multiply` only on layers ≥ 50% opacity. For lighter ghosts, use plain alpha + a saturated gold base color.

### B8 · Slabs/shadows clipped by `overflow: hidden` on hero
**Symptom:** drop shadows from front-layer headline get cut off at the hero edge.
**Fix:** if you need `overflow: hidden` on `.hero` (to clip back-slice drift), give the title-stack itself `overflow: visible` AND ensure the parent `.hero` has enough bottom padding to hold the shadow.

### B9 · "DEPTH · ∞" / "LAYER · 01" demo labels shipped to production
**Symptom:** user asks "what's that empty meaningless space" pointing at hard-coded debug labels.
**Fix:** demo/debug labels are stripped before shipping. If a label exists in the final HTML, it must be content the user wrote, not scaffolding from the skill.

### B10 · Skill loaded the second time on the same task
**Symptom:** `<inline_skill>` already includes the SKILL.md content, but the agent calls `Skill` again to load it.
**Fix:** if `<inline_skill>` is present in the conversation, follow it directly. Don't reload.

### B11 · Waterfall single-flow page with no navigation
**Symptom:** user says "all pages are like waterfall, on page, kinda lack of navigation bar to make the page more structure".
**Cause:** the skill historically shipped one long scroll page with no anchors, no TOC, no scroll progress. Fine for a 1-section landing page, regression-tier for any content with 3+ sections.
**Fix:** Phase 4.5 is now mandatory — every variant gets section IDs, smooth-scroll, scrollspy, and tier-appropriate nav. See §6.5 below for tier mapping.

### B12 · Chrome content offset left, Safari perfectly centered — phantom horizontal overflow
**Symptom:** in Chrome the page sits visibly left-of-center on a wide monitor ("my fault, I pushed the browser to the right out of screen" red herring — actually a real overflow before the user moved the window).
**Cause:** sticky `<nav>` with `flex-wrap: wrap` and a long brand string + 4 nav links + meta block computes a slightly different total width in Chrome's font metrics vs Safari's. Chrome's renders the nav slightly past viewport edge, which makes `body.scrollWidth > body.clientWidth` — then every `margin: 0 auto` content section centers against the wider scroll-width and visually shifts.
**Fix:** the **defensive overflow pattern** in Phase 4.5 (`html/body { overflow-x: clip; max-width: 100vw }` + `.nav-inner` 1280px wrapper) prevents this. Apply it to every shell.

### B13 · `overflow-x: clip` silently chops content instead of revealing the bug
**Symptom:** v6 Riso headline "MECHANICS!" was overflowing the viewport — `overflow-x: clip` hid the overflow so the page *looked* contained, but content was being chopped off the right edge.
**Cause:** defensive `overflow-x: clip` (added to fix B12) silently clips overflowing content. If a `clamp(min, vw, max)` headline is sized aggressively (e.g. `clamp(64px, 12vw, 180px)`), at 1440px viewport `12vw = 172.8px`, very close to the cap — with letter-spacing and per-character drift, the rendered word can exceed the viewport.
**Fix:** before shipping, audit every title's `clamp()` upper bound. Rule of thumb: at 1440px viewport, the rendered headline width must be ≤ 1280px (the content frame). If a `clamp(_, _, X)` produces overflow, reduce `X` until it fits. Test specifically at 1440×900 and 1920×1080. **Don't trust `overflow: clip` to hide the bug** — the user will catch it later.

### B14 · Layered text-shadow `::before` desyncs from wrapping text
**Symptom:** v6 Riso pink underprint shadow showed orphan "MEME" fragments next to the actual word "MECHANICS". Pink shadow was at one position, black text at another.
**Cause:** the structure was `<span class="row3 pink-shadow" data-text="Mechanics!">Mechanics!</span>` with `::before { content: attr(data-text); position: absolute; left: -6px; }`. Two compounding bugs: (1) the staircase indent used `padding-left: 160px` on the parent span, but `position: absolute` children resolve `left: -6px` relative to the span's **padding box** — so the pink `::before` started at row-left while the black text started at row-left + 160px. (2) When the span was treated as inline (default for `<span>`), the `::before` only aligned with the first inline line-box, so any wrapping fragmented the shadow.
**Fix:** for any layered-shadow design (Riso, Memphis, neo-brutalist offset shadow):
1. Use `display: inline-block` on the shadow-bearing span so the `::before` has a proper bounding box
2. Use `white-space: nowrap` to prevent the text from wrapping internally
3. Use `margin-left` (not `padding-left`) for staircase indents — absolute children are positioned relative to the parent's border-box, so margin shifts the entire shadow stack together

### B15 · Light-shell got dark-glass nav (or vice versa)
**Symptom:** v15 Holographic Future has a near-white pastel hero, but the auto-injected Tier-A nav rendered with `rgba(8,10,20,0.65)` (dark navy translucent) — visually clashed.
**Cause:** shell tokens for `bg_glass` were assumed dark for all dark-bg shells, but v15's hero is actually **light** despite living in the "futuristic" category.
**Fix:** the `bg_glass` token must be derived from the shell's actual base luminance, not its category. Light-base shells get `rgba(255,255,255,0.55–0.92)`; dark-base shells get `rgba(8–20,8–20,8–20,0.65–0.88)`. Inspect the rendered shell at rest before picking glass.

### B16 · Markup parity bug — one row in a stanza forgot a class
**Symptom:** v6 Riso Pop's row 2 ("MARKETS &") had no pink underprint while rows 1 and 3 did — user spotted it: "is the designed on purpose or it's bug got it missed?"
**Cause:** simple typo / oversight. Row 1 had `class="row1 pink-shadow" data-text="Money,"`, row 3 had `class="row3 pink-shadow" data-text="Mechanics!"`, but row 2 had only `class="row2 blue"` — missing both `pink-shadow` and `data-text`.
**Fix:** for any design where a single visual treatment is meant to apply uniformly across a stanza of structural siblings (rows of a multi-line headline, modules in a grid, takeaways), **verify class parity by grep before shipping**. A line like `grep -c 'pink-shadow' index.html` should equal the number of stanza rows.

### B17 · Section name variance breaks scrollspy
**Symptom:** v16 Reportage uses `<section class="pullquote">` instead of `<section class="equation">`, so the auto-injection script that adds `id="equation"` failed silently for that shell.
**Cause:** shell authors took creative liberty with section class names without updating the canonical alias map.
**Fix:** every shell's four canonical sections must end up with these IDs: `#hero`, `#curriculum` (or `#articles` aliased), `#equation` (or `#pullquote` aliased), `#takeaways`. The init script must accept aliases. Document any shell-specific aliases in that shell's `README.md`.

### B18 · "Card-with-image" syndrome on multi-image pages (rectangle syndrome)
**Symptom:** user says "pics of scenes are all rectangles, seem not designer's taste, simple html coding". Every figure on the page ends up as the same 3:2 or 2:3 box with the same border treatment and the same caption position. Reads as CMS template within seconds.
**Cause:** copying a single `<figure>` template across all images and just changing the `src`. Same aspect ratio + same border + same caption = visual tedium. The skill historically taught *hero* layout (1 photo) and *typographic* layout (0 photos) really well, but skipped *editorial multi-image* layout (3+ photos).
**Fix:** when a page carries ≥3 content photographs, follow §6.5 spread typology and use **at least 3 different spread types**. Repeating the same spread layout across 3+ modules in a row is a redesign trigger.

### B19 · Default `border: 1px solid` rings on content figures
**Symptom:** "rectangles, not designer's taste". Hairline borders around every photo are the universal CMS-template tell.
**Cause:** defaulting to `border: 1px solid var(--rule-strong)` on `<figure>` because it's the safe option.
**Fix:** **never wrap a content photograph in a 1px border by default.** The photo's edge IS the edge. Use tonal gradient falloff (`linear-gradient(to top, rgba(bg,0.45), transparent 55%)`) at the bleeding edge for cinematic photos on dark shells. Borders are only allowed when the frame *evokes a specific medium* (polaroid, contact sheet, gallery mat) and earns its place — not as a default safety move.

### B20 · Captions all in the same lower-left gradient bar
**Symptom:** identical caption position + treatment across 6 images = the page reads as a slideshow.
**Cause:** reusing a single `figcaption` styled with `position: absolute; left: 14px; bottom: 12px;` + bottom gradient overlay across every figure.
**Fix:** caption position MUST vary by spread type. See §6.5 — each spread has a different caption convention (top-left mono stamp, italic Fraunces below the figure with gold left rule, vertical rotated mono in the gutter, mix-blend-mode difference against the photo, displaced open-quote glyph at lower-left with offset). Pick one PER spread, not one for all of them.

### B23 · `repeat(N, 1fr)` grids overflow viewport when a cell holds an unbreakable long string
**Symptom:** on iPhone (393px viewport) the hero-stats row in v1, v2, v17 is sliced — "CONCEPTS · 52" and "GOAL · Vocabulary & intuition" sit completely off the right edge of the screen. Desktop and tablet look fine; mobile gets cut. Hidden by `html { overflow-x: clip }` so the page silently sheds content instead of revealing the bug.
**Cause:** the canonical content scaffold uses a `.hero-stats { display: grid; grid-template-columns: repeat(4, 1fr); }` row of 4 KPI columns. CSS Grid `1fr` resolves to `minmax(auto, 1fr)`, where `auto` = the *content's intrinsic minimum width*. When a stat value is an unbreakable string like `Beginner→Intermediate` or `Vocabulary & intuition`, that intrinsic minimum is wider than `viewport / 4`. The grid then **overflows its container** to satisfy the minimum, and the overflow is silently clipped. The `@media (max-width: 720px) { repeat(2, 1fr) }` fallback inherits the same bug at 2-up.
**Fix:** every multi-column grid that holds user-facing text must use the **defensive grid pattern**:
```css
.hero-stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));   /* minmax(0, 1fr), NOT 1fr */
  border-top: 1px solid var(--rule-strong);
}
.hero-stats .stat {
  min-width: 0;                                        /* allow shrink below intrinsic */
  padding: 22px 20px 22px 0;
  border-right: 1px solid var(--rule);
}
.hero-stats .stat:last-child { border-right: none; }
.hero-stats .v {
  font-family: var(--serif);
  font-size: 24px;
  word-break: break-word;                              /* break unbreakable words */
  overflow-wrap: anywhere;                             /* allow break at any char if needed */
  line-height: 1.2;
}
@media (max-width: 980px) {
  .hero-stats { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .hero-stats .stat { padding-right: 12px; border-bottom: 1px solid var(--rule); }
  .hero-stats .stat:nth-child(2n) { border-right: none; }
  .hero-stats .v { font-size: 20px; }
}
@media (max-width: 480px) {
  .hero-stats { grid-template-columns: 1fr; }
  .hero-stats .stat { border-right: none !important; }
  .hero-stats .v { font-size: 18px; }
}
```
Three changes do the work: (1) `minmax(0, 1fr)` overrides the auto-min so columns can shrink below intrinsic; (2) `min-width: 0` on the cell unblocks flex/grid shrink; (3) `word-break: break-word` + `overflow-wrap: anywhere` on the value text lets unbreakable strings wrap at any character when columns are too narrow. **Plus**: add a 480px fallback that goes single-column — at iPhone widths, 4 stats stacked vertically reads better than 2×2 cramped.
**Also affected — same defensive pattern applies to:**
- Any `.modules` / `.features` / `.takeaways` grid with `repeat(N, 1fr)`
- Spread-04 / spread-06 / spread-07 inner heads with `grid-template-columns: 90px 1fr 0.85fr` etc.
- Footer link rows that flex-wrap unbreakable email/URL strings
**Symmetric fix for negative-margin bleeds:** any `figure { margin-right: -32px }` (full-bleed pattern) must scale its negative margin **in lockstep** with parent padding when padding shrinks at small viewports. If you change `.hero { padding: 0 32px → 0 20px }` at 600px, you MUST also change `.hero-figure { margin-right: -32px → -20px }` at the same breakpoint, or the figure overshoots the viewport by 12px.
**Audit tooling:** run a CDP-based mobile audit at 393px viewport and check `getBoundingClientRect().right > clientWidth` on every element. False positives are limited to elements inside a parent with `overflow: hidden` (decorative blobs, spread-07 figures with parent overflow). A 25-line audit script lives in `references/mobile-audit.md`.

### B22 · Relative image paths break under Vercel `cleanUrls` at non-trailing-slash URLs
**Symptom:** site works perfectly on `python3 -m http.server`, ships to Vercel, then ALL images fail to load — only `alt` text shows. Direct `curl` to `/path/images/foo.jpg` returns 200, but the browser silently 404s.
**Cause:** `vercel.json` has `"cleanUrls": true`. When the user visits `https://site.com/v17-page` (no trailing slash, no `.html`), Vercel internally rewrites that to `/v17-page/index.html` and serves it — but the URL bar stays `/v17-page`. The browser treats `/v17-page` as a *file*, not a directory. So when the HTML contains `<img src="images/foo.jpg">`, the browser resolves it relative to the parent of `/v17-page` → `/images/foo.jpg`, which 404s.
**Fix:** in any subfolder variant deployed under Vercel `cleanUrls`, use **absolute paths** rooted at the variant folder: `src="/v17-page/images/foo.jpg"`, not `src="images/foo.jpg"`. Run a sed pass before deploying:
```bash
sed -i '' 's|src="images/|src="/<variant-folder>/images/|g' index.html
```
Alternative: turn off `cleanUrls` for subfolder pages, OR add a redirect rule that always appends a trailing slash. Absolute-path rewrite is the most portable fix.
**Watch for:** the bug is invisible to `curl` if you happen to type the right path manually — only a real browser (or `puppeteer.requestfailed` listener) will reveal the 404 because only the browser does relative-path resolution.

### B21 · Hosted-variant misclassification (text-only → founder-with-photo)
**Symptom:** original lesson built on Brutalist Index (correct for text-only finance). Then a host (Vivieen) is added with 6 portraits — but the page is still treated as text-only and the photos get bolted onto the same scaffold as rectangles.
**Cause:** the auto-pick table treats subject type as fixed at start of session. Adding a named human host with ≥3 photographs *changes the subject type* mid-task.
**Fix:** if a page acquires a named human host carrying ≥3 photographs, **switch shell** to Editorial Nightscape (or any Tier-B editorial shell), follow §6.5 spread typology, and apply the §0.5 editorial details checklist. The text-only Brutalist Index pick only applies when the type is the only protagonist.

---

## 6.5 · Spread typology (multi-image editorial pages)

The skill scaffold (masthead → hero → modules → equation → takeaways → footer) handles the *sequence* of sections, but doesn't tell you how a *photograph* should live inside a section. This is what was missing — and is what produces the rectangle-syndrome bug (B18) when omitted.

**Use this table whenever a page carries ≥3 content photographs.** Pick at least 3 different spread types across the page; never repeat the same type 3+ times in a row.

| Spread | When to use | Visual signature | Caption treatment |
|---|---|---|---|
| **A · Full-bleed split** | Hero, opening of a section, host band | Image bleeds to one viewport edge (`margin-right: -32px` or `-left`), content column on the other half. Tonal gradient on the dark side of the image fades into page background — NO border. | Mono stamp on photo top-left (`<em>Plate II</em> — The Kitchen, Morning`) OR vertical rotated mono in the margin |
| **B · Gutter mark + tall inset** | Module dividers in long content, especially when the lesson rhythm needs a vertical breath | Vertical rotated mono "FIG. IV · Plate III" running up the left margin in gold. Body text in middle column. 4:5 portrait inset on the right. | Italic Fraunces caption *below* the figure with a gold 1px left rule. NEVER overlay the caption on the photo — the marginal rule does the framing. |
| **C · Cinematic 21:9 letterbox** | A standout module that needs movie-poster drama | Wide 21:9 crop bleeding full viewport edge-to-edge (`left: -32px; right: -32px; width: calc(100% + 64px);`). Subtle gradient from edges inward to keep faces readable. | Italic Fraunces caption inside the photo at lower-left with a giant displaced open-quote glyph (`::before { content: "“"; font-size: 80px; left: -40px; color: gold; opacity: 0.5; }`) anchoring it. |
| **D · Pull-quote dominant + edge-bleed image** | A module where the *idea* in the pull quote is bigger than the photograph illustrating it | Body column carries an oversized pull quote (clamp 28-36px serif italic) with a 2px gold left rule and one accented word (e.g. "zero" in gold). Image at right with `margin-right: -32px` bleeding past the viewport gutter, 3:4 aspect. | Folio at image lower-left in mono: `<em>Plate V</em> — Mykonos · Golden Hour`. |
| **E · Half-circle break** | Host band, "about the author", testimonial | Large circular portrait (140-180px) with subtle gold ring + radial highlight. The circle visually breaks the rectangular band. Paired with a giant displaced quote glyph behind the blurb (§0.5). | No caption — the displaced quote glyph and the italic blurb do the work. |
| **F · Right-edge break-out** | Closer / sign-off / takeaways pair | Image extends past the right viewport edge (`margin-right: -80px`), no border. Tonal gradient at left blends image into page background. Sign-off text overlays at lower-left with mono kicker + italic CTA. | Folio at top-left in mono (`<em>Plate VI</em> — The Closer`), italic Fraunces sign-off at bottom-left ("End · Vol I / See you in the next lesson."). |

**Composition rule (the one that prevents B18):**
- 3 photographs → use 3 distinct spread types
- 4-6 photographs → use 4 distinct spread types, and break repetition with at least one typographic-only module between consecutive spreads
- 7+ photographs → reconsider whether this should be a one-page site at all (multi-page is out of scope; see §11)

**Vary three axes simultaneously across spreads:**
1. **Aspect ratio** — alternate 3:2 / 4:5 / 21:9 / 3:4. Never repeat the same ratio twice in a row.
2. **Caption position** — top-left mono / below-figure with rule / vertical-rotated gutter / mix-blend overlay / displaced-quote anchored. Each spread gets a different one.
3. **Bleed direction** — left-bleed / right-bleed / full-bleed / inset-with-gutter. Mix them so the page rhythm doesn't fall into a slideshow.

If you can't name 3+ distinct treatments before writing the first `<figure>`, you're about to ship rectangles. Stop and re-plan.

**Hosted-variant rule:** any "lesson / essay / report / finance" page with a named human host carrying ≥3 photographs of them → switch shell to **Editorial Nightscape** (or any Tier-B editorial register shell), apply this spread typology, and run the §0.5 editorial details checklist. The text-only Brutalist Index pick only applies when the type is the only protagonist.

---

## 7 · Critical rules (the short list)

1. **Direction BEFORE code.** Write the 4-line brief first.
2. **3D is opt-in.** Default for text-only / informational sites is *no shader*.
3. **Type does most of the work.** Get the type pair + scale right before any motion.
4. **Pull palette from subject OR curate from domain.** Never dark-cyan-default.
5. **Subject type gates technique.** No particle-sample on faces. No depth-displacement on logos.
6. **Single-file static output.** No build step, no React.
7. **i18n is `[data-i18n]` + 30-line vanilla loader.** Never React-i18next.
8. **Headless WebGL screenshots lie. Use real Chrome + cache-bust.**
9. **Honest swap > silent tune.**
10. **Never auto-deploy.**
11. **Strip demo/debug labels before shipping.**
12. **Static depth at rest** — never rely on hover/tilt to create the 3D illusion.
13. **Every variant gets navigation — tier-mapped, not skipped.** Section IDs + smooth-scroll + scrollspy is the new baseline. Waterfall pages are forbidden when content has ≥3 sections.
14. **Defensive overflow pattern in every shell.** `html/body { overflow-x: clip; max-width: 100vw }` + `.nav-inner` 1280px wrapper. Prevents Chrome-vs-Safari rendering drift.
15. **Audit `clamp()` upper bounds at 1440px and 1920px.** If a headline overflows, reduce the cap — don't trust `overflow: clip` to hide the bug.
16. **Layered shadows need `inline-block` + `nowrap` + `margin-left` (not padding) for staircase indents.** Otherwise `::before` desyncs when text wraps.
17. **Class parity in repeating stanzas.** When a treatment applies uniformly across rows of a headline, modules in a grid, or items in a takeaway list, every sibling must carry the same class. Grep-verify before shipping.
18. **Glass tint follows base luminance, not category.** Light-base shell → light glass nav. Dark-base → dark glass nav. Inspect the shell at rest first.
19. **No rectangle syndrome on multi-image pages.** When a page carries ≥3 content photographs, use ≥3 different spread types from §6.5. Same aspect ratio + same border + same caption position across 3+ images is a redesign trigger, not a stylistic choice.
20. **No default `border: 1px solid` rings on content figures.** The photo's edge IS the edge. Use tonal gradient falloff at bleeding edges instead. Borders only when they evoke a specific medium (polaroid, contact sheet, gallery mat).
21. **Re-evaluate subject type when a host is added.** If a text-only / informational page acquires a named human host with ≥3 photographs mid-task, switch shell to a Tier-B editorial register and apply §6.5 spread typology. Subject type is not fixed at start of session.
22. **Hit ≥5 items from the §0.5 editorial details checklist** on any editorial-register page. Plate folios, drop caps, marginalia rules, displaced quote glyphs, vertical rotated captions, hanging Roman numerals, em-dash flanked labels, colophon — the marginalia is what separates designed from templated.
23. **Use absolute paths for assets in any Vercel subfolder variant.** When deploying multi-variant gallery sites under `cleanUrls: true`, write `src="/<folder>/images/..."` not `src="images/..."` — otherwise the browser resolves relative paths against the parent (`/images/...`) and silently 404s. Always run puppeteer with a `requestfailed` listener post-deploy, not just `curl` — only a real browser does the wrong relative resolution that exposes the bug.
24. **Defensive mobile-grid pattern is mandatory on every `repeat(N, 1fr)` row that holds user text.** Use `minmax(0, 1fr)` (not `1fr`), `min-width: 0` on cells, and `word-break: break-word` + `overflow-wrap: anywhere` on the value text. Add 980 / 720 / 480 breakpoints with progressively narrower column counts (4 → 2 → 1). Negative-margin bleeds (`margin-right: -32px` on full-bleed figures) must scale in lockstep with parent padding when padding shrinks at small viewports — otherwise the figure overshoots viewport by the difference. Verify with a 393px CDP audit before shipping (see B23 + `references/mobile-audit.md`).

---

## 8 · Anti-patterns (the AI-slop test)

If the result has any of these, redesign:

- Cyan-on-dark with glowing borders
- Purple-to-blue gradient text on the hero headline
- Glassmorphism on every card
- Repeated KPI cards (big number + sparkline + icon)
- Centered everything
- `Inter` / `Roboto` / `system-ui` as the primary display face (use Fraunces, GT Sectra, Editorial New, Söhne, Geist, Founders Grotesk, Tiempos, etc.)
- Rounded rectangles with soft drop shadows on the hero
- Modals as a default UI pattern
- Decorative `<canvas>` cube spinning in the corner
- "Layer · 01" / "DEPTH · ∞" labels with no meaning (B2/B9)
- **All photographs use the same aspect ratio + same border treatment** (B18/B19 — rectangle syndrome)
- **Every figure has the same caption position** (B20 — slideshow tedium)
- **Repeated card layout for 3+ content modules** (CMS tedium)
- **Hairline `1px solid` border around content photography** (B19 — template tell)
- **Mono "— I" / "— II" tags as ordered list markers in editorial register** (use hanging Roman numerals in italic gold serif instead)

Full list: `references/ai-slop-fingerprints.md`.

---

## 9 · Bundled resources

### `scripts/`
- `prep_subject.py` — depth + downscale + alpha (skip for text-only)
- `extract_palette.py` — 5 OKLCH colors from subject image
- `init_project.py` — copy shell + apply palette + set up i18n + inject hero (or `--hero none`)
- `i18n_translate.py` — fan EN strings out via configured LLM

### `assets/shells/` (all 16 populated as reference variants)

**Original six (light + dark fundamentals)**
- `brutalist-index/` ✅ — Editorial brutalist (lessons, reports, finance)
- `editorial-nightscape/` ✅ — Apple-cinematic dark (founder, premium)
- `glass-library/` ✅ — Aesop pull-out (beauty, lifestyle, wellness)
- `studio-black/` ✅ — Linear/Vercel calm dark (B2B SaaS, dev tools)
- `swiss-modernist/` ✅ — Müller-Brockmann grid (manifesto, museum)
- `riso-pop/` ✅ — Risograph indie (events, kids, comedy)

**Industry-specific ten**
- `atelier-couture/` ✅ — Bureau Borsche × Vogue Italia (Fashion)
- `studio-spectrum/` ✅ — Pentagram × Studio Dumbar (Creative agencies)
- `stadium/` ✅ — Nike × ESPN (Sports / fitness / esports)
- `neon-arcade/` ✅ — A24 × Netflix × RA (Entertainment / streaming / music)
- `panel/` ✅ — Cartoon Brew × Pixar dev (Comic / cartoon / animation / kids' IP)
- `gallery-white/` ✅ — Zaha Hadid × MoMA × Magnum (Architecture / fine art / photo)
- `soft-organic/` ✅ — Family.co × Calm × Headspace (Wellness / kids / family)
- `quartermaster/` ✅ — Snow Peak × Best Made × Ace Hotel (Outdoor / gear / makers)
- `holographic-future/` ✅ — Arc × Linear × Gradient (AI / ML / Web3 / frontier)
- `reportage/` ✅ — NYT × Guardian × Magnum (News / longform / documentary / NGO)

All 16 shells share the same content scaffold (masthead → hero → modules → equation → takeaways → footer), so heroes, palettes, and i18n are interchangeable across them.

### `references/`
- `taste-manifesto.md` ✅ — the studio inspiration list expanded with screenshots / DNA notes
- `shells.md` ✅ — visual + content spec per shell
- `hero-shaders.md` ✅ — 6 drop-in `<script type="module">` blocks (A–F) + the `none` typographic baseline
- `navigation-tiers.md` ✅ — full HTML+CSS+JS templates for Tier A / B / C nav patterns, plus per-shell tier mapping and label conventions
- `spread-typology.md` ✅ — full HTML+CSS templates for the 6 spread types (A–F) in §6.5
- `editorial-details.md` ✅ — ready-to-paste CSS snippets for each item in the §0.5 checklist (drop caps, marginalia rules, displaced quote glyphs, vertical rotated captions, hanging Roman numerals, em-dash flanked labels)
- `figure-fx3d.md` ✅ — full CSS + JS for the `.fx3d` figure-grid effect (§4.6) with tuning knobs for tilt range, lift amount, sheen color/opacity, per-shell radius scale, and reduced-motion fallbacks. Includes do/don't pairs (when to skip on light shells, comic shells, newsprint shells).
- `subject-types.md` ✅ — what each type allows / disallows
- `i18n.md` ✅ — data-attribute contract + loader
- `ai-slop-fingerprints.md` ✅ — the avoid list
- `palette-by-domain.md` ✅ — extracted from §5
- `known-bugs.md` ✅ — extracted from §6, includes B11–B22
- `depth-portrait-tuning.md` ✅ — knobs for variant A

---

## 10 · Concrete examples this skill serves

| Request | Subject | Shell | Hero | Reference vibe |
|---|---|---|---|---|
| "Personal brand site with my photo" | human | Editorial Nightscape | A | Apple + Klim |
| "Landing for my fragrance" | product | Glass Library | D | Aesop + Apple |
| "公司官网，logo + 中英双语" | brand-mark | Studio Black | E | Linear |
| "Tech founder portfolio, EN+JP" | human | Editorial Nightscape | A | Apple |
| "Annual report microsite" | abstract | Brutalist Index | E (typographic) | Bloomberg + Pentagram |
| "SaaS launch teaser, no photo" | abstract | Studio Black | none | Linear + Vercel |
| **"Finance lesson microsite"** | **text-only** | **Brutalist Index** | **E (volumetric type)** | **Bloomberg Businessweek** |
| **"Hosted-edition lesson with 6 portraits of the host"** | **human (host)** | **Editorial Nightscape** | **none + §6.5 spread typology** | **Bureau Borsche × Pentagram × Klim** |
| "Wellness brand, soft, kids" | product | Soft Organic | F (low) | Family.co |
| "Indie event poster page" | abstract | Riso Pop | C | MSCHF |
| "One-page manifesto" | text-only | Swiss Modernist | none | Müller-Brockmann |

---

## 11 · Out of scope

- React / Vite / Next scaffolding (single-file first; React only on explicit request)
- Multi-page sites
- CMS integration (Sanity / Contentful is a separate skill)
- Heavy animation libraries (no GSAP / Framer / Lenis; vanilla CSS + IntersectionObserver)
- Full WCAG audit (shells aim for keyboard-nav + reduced-motion respect; full audit is a separate skill)
- Auto-deploy (user runs `vercel` / `netlify` themselves)

---

## 12 · The one rule above all rules

**This skill produces sites that feel hand-crafted by a tier-1 studio.**
If the output looks like a Webflow template, a Tailwind UI hero block, or a 2022 SaaS launch — it is wrong, and you redesign. The taste bar is *Apple / Pentagram / Aesop / Linear*, not "fancy gradient with a cube".
