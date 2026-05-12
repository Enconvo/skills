# multi-style-web-design

Studio-grade single-page web design skill with 17 swappable shells (Harvard Review *(default)*, Editorial Nightscape, Glass Library, Studio Black, Brutalist Index, Riso Pop, Swiss Modernist, Soft Organic, Atelier Couture, Studio Spectrum, Stadium, Neon Arcade, Panel, Gallery White, Quartermaster, Holographic Future, Reportage) and an opt-in 3D / motion / special-effects toolkit. When no style is specified, the skill initializes from **Harvard Review** — a calm ink-on-cream editorial shell with crimson accent.

See `SKILL.md` for the full spec.

## Privacy & network notes

This skill makes no outbound network calls on its own, and ships no telemetry. There are three points where the user's environment reaches the network — all opt-in or scoped to a workflow the user explicitly invokes:

1. **`scripts/i18n_translate.py`** shells out to the [`llm`](https://llm.datasette.io/) CLI with `-m gpt-4o-mini` by default to translate UI strings. **Your i18n source strings are sent to whichever provider `llm` is configured for** (OpenAI by default). Override with your own `llm` config or run translations manually if your strings are sensitive.
2. **Generated sites** load from public CDNs at runtime: `fonts.googleapis.com`, `fonts.gstatic.com`, `cdn.jsdelivr.net` (three.js), `cdn.tailwindcss.com`. End-user IP addresses hit those CDNs. Self-host the assets if that's a concern for your audience.
3. **`scripts/prep_subject.py`** downloads ML models on first run from Hugging Face: `depth-anything/Depth-Anything-V2-Small-hf` (~100 MB) and, for `--type product`, the rembg `u2net` weights. Skip the script (it's only needed for human / product / scene heroes with depth) if you don't want the model fetch.

No API keys, tokens, or secrets are stored or read by the skill. No analytics, beacons, cookies, or storage usage in the generated shells.

## Inputs the scripts accept

All four scripts are stdlib + a few well-known PyPI deps; no environment variables are read. File paths come from CLI args (the scripts write where you tell them to). See `SKILL.md` §3 for the workflow and `scripts/*.py` for argparse signatures.
