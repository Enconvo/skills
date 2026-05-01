---
name: fancy-website-builder
description: Build distinctive single-page websites with cinematic 3D hero treatments — Apple-style depth displacement, tilt+sheen, particle sample, glass refraction, volumetric slices, light caustics. Picks an aesthetic direction first, pulls palette from the actual subject photo, supports human portraits AND non-human subjects (products, logos, abstracts, scenes), ships multiple swappable shells, produces 7-language i18n (EN/CN/JP/ES/FR/KR/RU) via [data-i18n] slots, outputs a portable single-folder static site (no build step, no auto-deploy). Use when the user wants a personal brand site, founder portfolio, product landing page, company about page, launch teaser, or any one-page hero-driven site — or asks for "fancy website", "3D website", "Apple-style depth", "portrait website", "product landing", "brand site", "公司官网", "产品落地页", or provides a hero photo + brand text.
---

# fancy-website-builder

Build a single-folder, single-page site with a distinctive 3D hero. No build step. No auto-deploy. The user owns deploy decisions.

## Core philosophy

The X-post / generic prompt trap is "React + Three.js + Tailwind, please." That gives AI-slop. This skill produces *non-slop* output by:

1. **Choosing aesthetic direction BEFORE writing code.** Never default to dark-mode-cyan-glow.
2. **Pulling palette from the actual subject photo**, not from Tailwind defaults.
3. **Treating the hero as a 3D object** (depth-displaced, tilted, particled, refracted), not a flat `<img>`.
4. **Decoupling shell from hero technique** — any of 6 shells × any of 6 heroes.
5. **Honest critique over silent tuning** — if a hero technique fails the brand goal, switch techniques, don't tune.

## Required inputs from the user

1. **Subject** — one of: `human` / `product` / `brand-mark` / `abstract` / `scene`
2. **Site purpose** — short sentence (e.g. "personal brand", "skincare product launch", "B2B SaaS landing")
3. **Brand name + tagline** — for the hero typography
4. **Languages** — default `en`; add any of `zh`/`ja`/`es`/`fr`/`ko`/`ru`
5. **Optional**: aesthetic direction (otherwise auto-pick from purpose using the table below)

If the user gives a vague request ("build me a fancy website with this photo"), confirm the 5 inputs above before generating code.

## Workflow

### Phase 1 — Direction (no code yet)

Three orthogonal choices:

1. **Subject type** → drives Phase 2 asset prep + Phase 4 hero compatibility.
2. **Page shell** → from `assets/shells/` (see `references/shells.md`).
3. **Hero technique** → from `references/hero-shaders.md`.

Auto-pick rules when the user is silent:

| Purpose | Default shell | Default hero |
|---|---|---|
| Personal brand / founder | Editorial Nightscape | A · Depth Displacement |
| Product launch | Glass Library | D · Glass Refraction |
| B2B SaaS | Studio Black | E · Volumetric Slices |
| Annual report / press | Brutalist Index | B · Tilt & Sheen |
| Lifestyle / consumer | Sunbleached Memo | F · Light Caustics |
| Indie / event | Riso Pop | C · Particle Sample |

Never silently default to a hero that's wrong for the subject (e.g. C on a human face → eyes void → dehumanises). The compatibility matrix is in `references/hero-shaders.md`.

### Phase 2 — Asset prep

Run `scripts/prep_subject.py` with the subject type:

```bash
uv run scripts/prep_subject.py <subject_image> <output_dir> --type <human|product|brand-mark|abstract|scene>
```

The script branches:
- **human / product / scene**: downscale to 900px wide, run Depth Anything V2 (MPS/CUDA/CPU), save `hero.jpg` + `hero_depth.jpg`.
- **product (additional)**: also generate alpha matte via rembg.
- **brand-mark**: keep PNG/SVG with transparency, skip depth.
- **abstract**: just downscale.

Then extract palette:
```bash
uv run scripts/extract_palette.py <subject_image> --out <output_dir>/palette.json
```
Output: 5 dominant OKLCH colors that the chosen shell will use as `--brand-1` through `--brand-5`.

### Phase 3 — Pick + initialize the project

```bash
uv run scripts/init_project.py <output_dir> --shell <shell-name> --langs en,zh,ja
```

This:
1. Copies the chosen shell from `assets/shells/<shell-name>/` into `<output_dir>/`
2. Applies the extracted palette to the shell's CSS custom properties
3. Sets up `i18n/` with the requested languages (creates blank `<lang>.json` for each; `en.json` is populated from the shell's defaults)
4. Adds the chosen hero `<script>` block from `references/hero-shaders.md`

Each shell is a single `index.html` plus optional shared CSS. Shells share the same `[data-i18n]` keys so heroes and i18n are interchangeable across them.

### Phase 4 — Inject hero technique

If `init_project.py` was run with `--hero <id>`, the technique is already injected. To swap, replace the contents of `<script id="hero-technique" type="module">…</script>` in `index.html` with a different block from `references/hero-shaders.md`.

| # | Technique | Best for | Avoid for |
|---|---|---|---|
| A | Depth Displacement | Human portrait, product on background | Logos, abstracts |
| B | Tilt & Sheen | Mid-shot subject, glossy product | Wide scenes, abstracts |
| C | Particle Sample | Abstract, art-leaning portfolio | Faces (eyes void out) |
| D | Glass Refraction | Lifestyle, beverage, mood-driven | High-detail product |
| E | Volumetric Slices | Mobile-first, low-GPU, products | Fine portrait detail |
| F | Light Caustics | Editorial, beauty, perfume | B2B / corporate |

Full shader code lives in `references/hero-shaders.md`.

### Phase 5 — Translate (if requested)

```bash
uv run scripts/i18n_translate.py <output_dir>/i18n/en.json --langs zh,ja,es,fr,ko,ru
```

Calls the configured LLM with a translation prompt that preserves brand tone. Outputs `i18n/<lang>.json` for each requested language.

The shell loads i18n at runtime via a 30-line vanilla loader (already embedded). It reads `?lang=<code>` from URL, falls back to `navigator.language`, then to `en`. No framework, no React-i18next.

See `references/i18n.md` for the data-attribute contract and how to add new languages.

### Phase 6 — Variant exploration (optional)

If the user wants to compare hero techniques side-by-side, copy the project N times and inject a different shader in each:

```bash
cp -r project/ project-a/   # inject A
cp -r project/ project-b/   # inject B
cp -r project/ project-d/   # inject D
```

The user opens each locally or deploys each separately. **This skill never auto-deploys.** Output the local paths and stop.

### Phase 7 — Visual verification

Always verify in real Chrome (headless WebGL is unreliable):

```bash
cd <output_dir>
python3 -m http.server 7531 &
open -a "Google Chrome" http://127.0.0.1:7531/
sleep 3
screencapture -x /tmp/site_check.png
```

Inspect the screenshot:
- Shell loads, fonts render (Google Fonts requires network).
- Hero canvas paints (subject visible, not a black rectangle).
- i18n switches work — open `?lang=zh`, `?lang=ja` and confirm strings change.

If a hero technique visually fails for the subject, **flag honestly** to the user and propose a different technique. Do not silently tune parameters and call it "fixed".

## Critical rules

1. **Aesthetic direction BEFORE code.** Never start with "I'll set up Tailwind and Three.js" — that's the prompt-template trap.
2. **Pull palette from the actual subject** via `extract_palette.py`. Never default to dark-mode-cyan-glow.
3. **Subject type gates technique choice.** Don't run particle sample (C) on a face. Don't run depth displacement (A) on a logo. Warn the user if they ask for a bad pairing.
4. **Single-file static output, always.** No npm install, no build step, no React boilerplate unless the user explicitly asks. The whole project is a folder you can email.
5. **i18n is data-attribute driven**, not React-i18next. Every shell ships with the 30-line vanilla loader. Adding a language is editing one JSON file.
6. **Headless WebGL screenshots lie.** Verify in real Chrome via `screencapture`, not `--headless --screenshot`.
7. **Honesty over silent tuning.** If a hero technique doesn't serve the brand goal, switch techniques and tell the user why.
8. **Never auto-deploy.** End at the file output. The user owns the deploy decision.

## Anti-patterns (the AI-slop test)

If the result has any of these, redesign — see `references/ai-slop-fingerprints.md` for the full list:

- Cyan-on-dark with glowing borders
- Purple-to-blue gradient text
- Glassmorphism applied decoratively to every card
- KPI card grid: big number + colored sparkline + icon, repeated
- Centered everything
- Inter / Roboto / system-ui anywhere
- Rounded rectangles with soft drop shadows on the hero
- Modals as a default UI pattern

## Bundled resources

### `scripts/`
- `prep_subject.py` — depth map + downscale + alpha matte (subject-type-aware)
- `extract_palette.py` — 5 OKLCH colors from subject image
- `init_project.py` — copies chosen shell + applies palette + sets up i18n + injects hero
- `i18n_translate.py` — fans EN strings out to other languages via configured LLM

### `assets/shells/`
- `editorial-nightscape/` — proven on the Cleo project; default for human/founder
- `glass-library/` — calm, high-end product, wide whitespace
- `studio-black/` — B2B, restrained
- (Sunbleached Memo / Brutalist Index / Riso Pop are scaffolded; populate as use-cases demand)

### `references/`
- `subject-types.md` — what each subject type allows / disallows
- `shells.md` — full visual + content spec per shell, when to use each
- `hero-shaders.md` — 6 drop-in `<script type="module">` blocks (A–F)
- `i18n.md` — data-attribute contract, loader code, language fallback rules
- `ai-slop-fingerprints.md` — what to avoid
- `depth-portrait-tuning.md` — knobs for variant A (uStrength, uParallax, segmentation, vignette)

## Concrete examples this skill serves

| Request | Subject | Shell | Hero | Languages |
|---|---|---|---|---|
| "Personal brand site with my photo" | human | Editorial Nightscape | A | en |
| "Landing page for my new fragrance, here's the bottle" | product | Glass Library | D | en |
| "我们公司要做个官网，logo 在附件里，中英双语" | brand-mark | Studio Black | E | en, zh |
| "Tech founder portfolio, EN+JP" | human | Editorial Nightscape | A | en, ja |
| "Annual report microsite for our nonprofit" | abstract | Brutalist Index | B | en |
| "SaaS launch teaser, no real photo yet" | abstract | Studio Black | E | en |

## Out of scope

- React/Vite/Next scaffolding (single-file first; React only on explicit request)
- Multi-page sites (this is one-page, hero-driven)
- CMS integration (Sanity/Contentful is a separate skill)
- Heavy animation libraries (no GSAP/Framer/Lenis; vanilla CSS + IntersectionObserver in shell)
- Full WCAG audit (shells aim for keyboard-nav + reduced-motion respect; full audit is a separate skill)
- Auto-deploy (user runs `vercel`/`netlify` themselves)
