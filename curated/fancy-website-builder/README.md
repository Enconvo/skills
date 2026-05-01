# fancy-website-builder

Build a single-folder, single-page site with a distinctive 3D hero — no build step, no auto-deploy.

## What it does

Produces a static HTML/CSS/JS site that combines:

- A **shell** (page structure + typography + palette + section grid) — pick from 6 editorial directions
- A **hero technique** (WebGL, Three.js) — pick from 6 cinematic treatments: depth displacement, tilt & sheen, particle sample, glass refraction, volumetric slices, light caustics
- A palette **pulled from the actual subject photo** via Depth Anything V2 + OKLCH extraction (no Tailwind defaults)
- An i18n loader driven by `data-i18n` attributes (no React-i18next)

Output is a single folder you can email or `vercel deploy`.

## Why it's not just "React + Three.js + Tailwind"

The skill enforces decisions *before* code:

1. Aesthetic direction is chosen first; never default to dark-mode-cyan-glow.
2. Hero technique is gated by subject type — particle sample is forbidden on faces (eyes void out), depth displacement is wrong for logos, etc.
3. Single-file output, always. No npm install, no React boilerplate unless explicitly requested.
4. Real Chrome verification — headless WebGL screenshots lie.
5. Honesty over silent tuning — if a technique doesn't serve the brand, switch techniques and say why.

## Required inputs

1. Subject — `human` / `product` / `brand-mark` / `abstract` / `scene`
2. Site purpose — short sentence
3. Brand name + tagline
4. Languages (default `en`; supports `zh`/`ja`/`es`/`fr`/`ko`/`ru`)
5. Optional: aesthetic override

## Workflow

See `SKILL.md` for the full 7-phase workflow (direction → asset prep → init → hero injection → translate → variant exploration → visual verification).

## Bundled

- `scripts/prep_subject.py` — depth map + downscale + alpha matte
- `scripts/extract_palette.py` — 5 OKLCH brand tokens from subject
- `scripts/init_project.py` — copy shell + apply palette + inject hero + scaffold i18n
- `scripts/i18n_translate.py` — fan English strings out to other languages via configured LLM
- `assets/shells/editorial-nightscape/` — proven on the Cleo and Great Lionheart projects
- `references/` — shell catalog, hero shader code, AI-slop fingerprints, depth-portrait tuning knobs

## Out of scope

React/Vite/Next, multi-page sites, CMS integration, GSAP/Framer/Lenis, full WCAG audit, auto-deploy.
