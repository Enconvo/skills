# BUILD.md — make an EnConvo product film from this scaffold

This folder renders the **stable 50.5s EnConvo launch film** — the exact structure behind
`EnConvo_Minimal_16x9_v4` / `9x16`. Everything EnConvo-branded is fixed; you swap the
product clips + copy + body narration, pick a theme, render, and mux. Out of the box (no
edits) it reproduces the EnConvo demo film in **Minimal** or **Line Art**.

## What's fixed vs what you swap

**FIXED — the EnConvo brand (don't touch):**
- The 8-scene / 50.5s timeline and every animation (the GSAP `<script>`).
- **S1 open** and **S8 close / CTA**: gold logo → ENCONVO → “Your Mac's command center.” → ⌘⇧D keycaps → enconvo.com, with the tick·tick·tock keypress.
- `assets/brand/*` (gold logo + keycaps), `assets/audio/ambient.wav` (music bed),
  `assets/audio/sfx/*` (tick / tock / whoosh), and `assets/vo/vo8.wav` (the fixed outro line).

**SWAP — per product:**
- `assets/clips/*.mp4` — 7 body clips: `smartbar, popbar_full, agent, quant, m_excel, m_tools, vivwalk`.
  Reuse the same filenames (or edit the `src=` in the template). Pre-trim each to its best ~2–7s,
  muted, and roughly 16:9 (they're shown in framed panels).
- **Scene copy** — eyebrow / title / ticks inside `<div id="s2">` … `<div id="s7">`.
- `assets/vo/vo2..vo7.wav` — body narration. Regenerate with your TTS (one voice for the whole
  film). VO markers are locked; just replace the files. Recipe: `../reference/AUDIO_VO.md`.

## Themes
- `minimal-landscape.html` / `minimal-vertical.html` — light Notion-white (the shipped v4). **Canonical base.**
- `lineart-landscape.html` / `lineart-vertical.html` — cream paper, bold navy ink, gold accent, hand-drawn framed panels.

Line Art is generated from Minimal (a CSS override skin), so after editing copy in the Minimal
files, regenerate Line Art so it stays in sync:
```bash
python3 scripts/make_themes.py
```

## Build (run from this scaffold root)

Renders are **silent** by design; audio is always muxed after. Needs the HyperFrames CLI —
use a global `hyperframes`, or a local binary (`node_modules/.bin/hyperframes`, install once with
`npm install hyperframes@<ver> --no-save --include=dev`). **Never `npx hyperframes`** (mis-routes).

```bash
# 1. Render each cut silent. `check`/`render` want ONE root .html per dir, so isolate:
for f in lineart-landscape lineart-vertical; do
  d=/tmp/hf_$f; rm -rf $d; mkdir -p $d; ln -s "$PWD/assets" $d/assets; cp $f.html $d/
  ( cd $d && hyperframes render -c $f.html -o /tmp/$f.mp4 . )
done

# 2. Build the VO+bed+SFX mix once and mux onto BOTH orientations
#    (same mix fits 16:9, 9:16, Minimal, and Line Art — they share the timeline):
bash scripts/build_audio.sh /tmp/lineart-landscape.mp4 EnConvo_LineArt_16x9.mp4
bash scripts/build_audio.sh /tmp/lineart-vertical.mp4  EnConvo_LineArt_9x16.mp4

# 3. Verify: h264 + aac, 50.5s, whole-file volumedetect max ~ -1 to -0.3 dB,
#    and the tick·tick·tock outro is the loudest moment (~48.0-48.1s).
```

Swap `lineart` → `minimal` above for the Minimal cut. `build_audio.sh` caches the mix at
`enconvo_mix.wav`; set `FORCE=1` to rebuild after changing any VO, or `FFMPEG=/path/to/ffmpeg`
if plain `ffmpeg` isn't on PATH.

## Poster (optional)
```bash
ffmpeg -y -i EnConvo_LineArt_16x9.mp4 -ss 46.5 -frames:v 1 -q:v 2 EnConvo_LineArt_16x9_poster.png
```
