---
name: highlight-reels-for-product-tv-commercial
description: Build premium, TV-commercial-grade product highlight-reel promo videos from a handful of screen recordings. Music-only by default (optional VO-narrated cut), HyperFrames + paused GSAP, rendered and muxed locally. Ships a full kit — 16:9 + 9:16 films and matching key-art posters — in three swappable, production-proven themes. Use when the user asks for a product promo / launch film / hero reel / app commercial / "video like <reference>" / feature sizzle from screen captures, or says "highlight reel", "product TV commercial", "aurora theme", "minimal / notion-style promo". Three theme presets: AURORA (dark, glowing, chromatic, bold), MINIMAL (light Notion-white, floating cards, one accent, confident restraint), and LINE ART (cream paper, bold navy ink, one gold accent, hand-drawn framed panels). Ships a self-contained EnConvo scaffold (bundled logo, keycaps, SFX, music bed) that reproduces the launch film by dropping in new product clips.
version: 1.2.0
---

# Highlight Reels for Product TV Commercial

A repeatable pipeline for turning raw product screen recordings into a polished, music-driven promo reel that looks like a real launch commercial. Battle-tested on the EnConvo launch kit.

## What it produces
- **Two films per theme**: 16:9 (feed / landing / YouTube) and 9:16 (Reels / TikTok / Stories).
- **Key-art posters**: a still of the close lockup for each film (post preview, link cards, email).
- **Three themes** you can render the *same* composition in: **Aurora**, **Minimal**, and **Line Art**. Offer all three; let the user pick.
- **Self-contained EnConvo scaffold** (`scaffold/`): the shipped v4 launch film with every brand asset bundled — drop in new product clips to reproduce it (§EnConvo scaffold).
- Default spec: **42s, 1920×1080 / 1080×1920, 30fps, music-only.** All timings are beat-locked to one score.

## When to use
Product launch films, feature sizzles, app/website promos, "make it look like this reference reel", hero videos for a landing page. Inputs are **screen recordings of the product** + a **logo PNG** + a short list of feature claims. Default is **music-only**; a longer **VO-narrated cut** is also supported (§VO-narrated variant + `reference/AUDIO_VO.md`). Not for talking-head or documentary edits.

---

## EnConvo scaffold — self-contained, drop-in-clips

For **EnConvo** films (or any product reusing this exact structure), `scaffold/` is a turn-key, fully self-contained copy of the shipped v4 launch film — you don't rebuild from templates, you **swap clips**. It bundles every brand asset (gold logo, ⌘⇧D keycaps, tick/tock/whoosh SFX, the 50.5s `ambient.wav` bed) plus demo clips + demo VO, so it renders out of the box with **no external paths**.

- **Fixed (the brand):** the 8-scene / 50.5s timeline, all motion, and the S1 open + **S8 close/CTA** (gold logo → ENCONVO → tagline → ⌘⇧D keycaps → enconvo.com, with the tick·tick·tock press). Identical across every film.
- **You swap (per product):** the 7 body clips in `scaffold/assets/clips/`, the scene copy in the `<div id="s2">…<div id="s7">` blocks, and body VO `scaffold/assets/vo/vo2..vo7.wav`. Keep `vo8` (the fixed EnConvo outro line).
- **Skins:** `minimal-*.html` (shipped v4) and `lineart-*.html` (cream/navy/gold — §Theme presets). `python3 scaffold/scripts/make_themes.py` regenerates Line Art from the Minimal base after copy edits, so structure never drifts.
- **Audio is turn-key:** `bash scaffold/scripts/build_audio.sh <silent.mp4> <final.mp4>` builds the VO + ducked bed + tick·tick·tock and muxes. Markers + SFX times are locked to the timeline, so the *same* mix fits both orientations and both skins.
- **Per-project steps:** `scaffold/BUILD.md`. Aurora isn't ported into the scaffold yet (it's the 42s cinematic music-only variant below); the scaffold path is Minimal + Line Art (50.5s, VO).

---

## The pipeline (7 steps)

1. **Gather inputs** — screen recordings (`.mov/.mp4`), a logo PNG (ideally white-on-transparent), product vocabulary (real feature names), and 4–6 feature claims. If a reference video is given, mine it for pacing, scene count, and the tilted-panel motif — don't copy content.
2. **Stage hero clips** — trim each recording to its best ~2–6s beat, **mute**, normalize to 1280×720@30. One clip per feature scene + 3 for the capability montage:
   ```bash
   ffmpeg -i src.mov -ss <in> -t <dur> -an -vf "scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720" -r 30 assets/clips/<name>.mp4
   ```
3. **Author the composition** — copy a template from `assets/templates/` (see Theme presets). Swap in the feature copy, clip filenames, logo, and CTA. Keep the scene **data-start** times (they're beat-anchored — §Storyboard).
4. **Synthesize the score** — run `assets/scripts/synth_music.py` (numpy+scipy) to emit a 42s `score.wav` with impacts on the beat anchors, or drop in a licensed track of matching length. Peak ≈ −1 dBFS.
5. **Validate** — `hyperframes check` (isolate other root files first — §Commands). Fix errors; the listed infos/warnings are benign.
6. **Render + mux** — `hyperframes render -q high -c <entry>.html -o renders/x.mp4`, then mux the score with ffmpeg (§Commands). **Audio is always muxed after render, never an `<audio>` element.**
7. **Cut posters + verify** — pull the close-lockup frame per film; build a 3×3 frame sheet and eyeball it before delivering.

---

## Theme presets

Same layout, timeline, and storyboard — only the *skin* changes. Full token tables in `reference/THEMES.md`.

### Aurora — dark, bold, cinematic
Templates: `aurora-landscape.html`, `aurora-vertical.html`.
- **Stage:** near-black radial `#0a0d16 → #06070d → #030308`; a blue eclipse **orb** that hue-rotates blue→violet→magenta via `--orbHue` (0→22→52→92→70), a faint conic **oil-slick**, SVG grain, vignette.
- **Type:** white ink, eyebrow `#aeb9ff`, accent gradient `#6f7bff→#c07bff`. Titles + logo carry a **chromatic RGB split** (`.chroma` text-shadow / logo drop-shadows).
- **Panels:** dark cards with a blue glow shadow. **Chip:** neon green `#7dffb0`.
- **Logo:** white ribbon PNG used directly (chromatic edges).

### Minimal — light, Notion-white, confident restraint
Templates: `minimal-landscape.html`, `minimal-vertical.html`.
- **Stage:** warm paper radial `#FAF9F6 → #F4F3EF → #EEEDE8`; one nearly-invisible cool whisper-radial for life. **No** orb hue-shift, **no** conic slick, **no** grain.
- **Type:** near-black ink `#1A1915` / mega `#131210`, secondary `#6B6862`, muted `#8A867E`. **One** accent: indigo `#3B5BDB` (eyebrow bar, URL, separators). **No** chromatic split.
- **Panels:** white **floating cards** — realistic soft shadow `rgba(20,22,44,0.34)` + `1px` hairline, no glow. **Chip:** muted green `#157F4C` on a 10% tint.
- **Logo:** white ribbon PNG **inside a dark app-icon tile** (`#2B2B34→#17171B`, radius ~44px, soft shadow) so it reads on the light page. This is the key move that makes a white logo work on light.

### Line Art — cream paper, bold navy ink, gold accent
Templates: `scaffold/lineart-landscape.html`, `scaffold/lineart-vertical.html` (regenerate via `scaffold/scripts/make_themes.py`).
- **Stage:** warm cream-paper radial `#F8F4E9 → #F2EEE1 → #EBE6D6`; a faint gold whisper-radial. Flat and clean — no orb, no grain.
- **Type:** deep navy ink `#1E2C62` / mega `#15224E`, muted navy `#5A6488`. **One** accent: gold `#E7B62C` (eyebrow bar, URL dot, separators, caret). Titles are **heavy (800)** — the bold editorial voice.
- **Panels:** real clips in a **hand-drawn navy frame** — `4px solid #1E2C62` + a **flat-offset (blur-0) navy shadow** `16px 16px 0`. That blur-0 offset is the whole line-art signature (also on the SmartBar pill + logo). **Chip:** navy on a gold tint.
- **Logo:** gold ribbon PNG on paper with a flat-offset navy drop-shadow (no tile).
- Built as a CSS **override skin** appended to the Minimal body → layout is provably identical to Minimal.

> Rule of thumb: Aurora sells *energy*; Minimal sells *taste*; **Line Art sells *editorial clarity***. When a brand wants “high-tech but calm / like Notion / not AI-slop,” reach for Minimal.

---

## Storyboard blueprint (42s @ 30fps — keep these start times)

| # | Scene | Window (s) | Content |
|---|-------|-----------|---------|
| S1 | Logo bloom | 0–5.2 | Icon/logo + wordmark + kicker |
| S2 | Thesis | 4.8–10.2 | eyebrow + head + **mega** headline + product command-bar pill |
| S3 | Feature A | 9.8–15.7 | panel **right** / caption **left** |
| S4 | Feature B | 15.3–20.7 | panel **left** / caption **right** |
| S5 | Feature C | 20.3–26.3 | panel **right** / caption **left** |
| S6 | Feature D | 25.8–31.3 | panel **left** / caption **right** + metric **chip** |
| S7 | Capability montage | 30.8–36.0 | **3 big panels one-at-a-time** + 1 faint keyword row + “…and everything between.” |
| S8 | Close / CTA | 35.6–42.0 | icon + wordmark + tagline + URL |

**Beat anchors (score impacts / whooshes):** 9.4, 20.0, 30.4 s. **Aurora orb hue shifts:** 9, 20, 26, 36 s. If you re-time the score, move these together.

---

## VO-narrated variant

The default reel is music-only. For a narrated cut (like the shipped **EnConvo launch film**) the composition runs **longer — 50.5s**, with one clean single-voice narration over a **ducked** music bed plus a keypress-SFX outro. Same layout / themes; only the timeline lengthens and a voice track is added. Both 16:9 and 9:16 share the identical timeline, so build **one** audio mix and mux it onto **both** silent renders.

- **Scene starts (VO cut):** S1 0 · S2 4.4 · S3 9.4 · S4 17.1 · S5 24.5 · S6 31.9 · S7 38.5 · S8 43.8. VO lands ~0.5s after each start.
- **Mix:** per-scene VO (`adelay` at each marker) + `ambient.wav` bed (vol ~0.42, `sidechaincompress`-double-ducked under the VO **and** the keypress SFX) + tick·tick·tock keypress SFX → `alimiter` → mux `-c:v copy -c:a aac`. Keep `ambient.wav` (music-only) separate from any VO+music mix, or you double-track the voice.
- **Outro SFX:** ⌘⇧D = **tick (⌘) · tick (⇧) · tock (D)** at the keycap press times, tock loudest (the shortcut firing). Full recipe, levels, and measurement-based verification (you can't audition) in **`reference/AUDIO_VO.md`**.

---

## Layout math (the “big panel + caption” system)

The signature look is a **large tilted UI panel** you can actually read, paired with a compact side/below caption. Learned tuning:

- **Landscape panel:** `1260×709`, x-center **30% / 70%** (alternating), y-center **42%**, tilt `rotateY ±10` settling to `±6`, `rotateX 5`. Small off-canvas bleed (~50px) is fine — mark intentional overflow, don't shrink the panel.
- **Exception — edge-UI clips (landscape only):** the shipped EnConvo MINIMAL kit uses larger `1480×833` panels at `left:34%/66%`, bleeding ~90px off the near edge, and `rotateY` enlarges that edge further. If a clip's essential UI sits on the bleeding edge — e.g. a selection toolbar whose leftmost button ("Ask AI") is on the left — the bleed clips it off-frame. For that clip only, shrink it (~`1320×743`) and nudge toward center (`left:37%`) until the full UI is in-frame without colliding with the side caption. Vertical panels are centered (no bleed), so edge-UI is safe there. **Check each clip's key UI against the bleeding edge before accepting the bleed.**
- **Landscape caption:** side column `width:560`, `left/right:6%`, `top ~35–37%`, **title 56px** (supporting, not competing). ~39px gap to the panel edge.
- **Vertical panel:** `1000×563`, centered, `top:33%`, same tilt. **Caption below**, centered, `top ~58–60%`, title 66–68px.
- **Capability montage (S7):** one panel at a time, centered `50% / 41%` (landscape) or `50% / 34%` (vertical), ~1.9s each with a 0.4s cross-blur, on **separate tracks (5/6/7)**. A single keyword row drifts behind at very low opacity (Aurora ~0.10, Minimal ~0.055). This is what fixed the “too busy” capability scene — never stack 3 panels + a loud word-wall at once.

Motion helpers (in every template): `tiltIn / tiltOut` (panels), `montageBig` (S7), `wordsIn` (per-word headline reveal), `groupOut` (scene exit). Reduce skew for readability; a flatter panel shows more detail.

---

## HyperFrames authoring contract (hard rules — violating these = blank frames / non-determinism)

- **Monolithic standalone:** one root `<div id="root">` (`position:relative; overflow:hidden`) with `data-width/height/fps/duration`; one `gsap.timeline({paused:true})` built synchronously and published to `window.__timelines["<composition-id>"]`. Duration = root `data-duration`.
- **MEDIA RULE:** every `<video>`/`<audio>` must be a **DIRECT child of `#root`** or it renders blank. `<video>` must be `muted playsinline`. Trim by pre-cutting the file (don't rely on in/out points).
- Full-screen fills go on a full-bleed **child** (`position:absolute; inset:0`), never on `#root` itself.
- **Determinism:** no `letterSpacing` tweens; never combine CSS `translate(-50%,-50%)` with a GSAP transform on the same node — use `xPercent/yPercent`; no two clips overlapping on the **same track**; no two tweens animating the **same property** of the same node at the same time.
- **Audio is muxed with ffmpeg AFTER render** — an `<audio>` element renders `audioCount=0`. 
- Fonts auto-alias at render: `SF Pro Display/Text → Inter`, `SF Mono → JetBrains Mono`. Design with those.
- Benign and expected: `pointer_events_none` infos, `panel_out_of_canvas` infos (intentional bleed), sparse-keyframe notes on montage clips (HyperFrames pre-extracts ~150 frames/clip; no real freeze).

---

## Commands cheat-sheet

**Invoke the CLI directly — `npx hyperframes` mis-routes to npm. Use `hyperframes <cmd>`.** If no global `hyperframes` is on PATH (or Node/`npx` is version-mismatched), use the **local binary** `node_modules/.bin/hyperframes <cmd>` (install once with `npm install hyperframes@<ver> --no-save --include=dev`). Renders are **silent** either way — audio is muxed after.

```bash
# CHECK — needs exactly ONE root composition file. Move other root .html into a holder first:
mkdir -p _variants && mv other-root-*.html _variants/   # avoids `multiple_root_compositions` hard-fail
hyperframes check                                        # 0 errors + WCAG AA pass = good

# RENDER — use -c for any entry that isn't index.html:
hyperframes render -q high -c minimal-landscape.html -o renders/minimal.mp4
# optional integer-multiple upscale (aspect must match; not with --hdr):
#   --resolution=landscape|portrait|landscape-4k|portrait-4k|square

# MUX score (canonical):
ffmpeg -y -loglevel error -i renders/x.mp4 -i assets/audio/score.wav \
  -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 320k -ar 48000 -shortest out.mp4

# POSTER (close lockup ≈ frame 1185 @30fps):
ffmpeg -y -i out.mp4 -vf "select=eq(n\,1185)" -frames:v 1 -q:v 2 keyart.png

# VERIFY sheet (always eyeball before delivery):
ffmpeg -y -i out.mp4 -vf "select='eq(n\,210)+eq(n\,525)+eq(n\,945)',scale=620:-1,tile=3x1" -frames:v 1 /tmp/sheet.jpg
```

Multi-root projects (all four cuts in one folder) render fine with `-c` — the multi-root rule is a **check-only** hard-fail, so isolate roots only when running `check`.

---

## Assets in this skill
- `assets/templates/aurora-landscape.html`, `minimal-landscape.html`, `aurora-vertical.html`, `minimal-vertical.html` — complete, render-ready reference compositions. Start by copying one.
- `assets/scripts/synth_music.py` — local 42s score synth (numpy/scipy), impacts on the beat anchors.
- `reference/THEMES.md` — exhaustive palette + component token tables for both themes.
- `reference/STORYBOARD.md` — the full beat map with per-scene animation cues.
- `reference/AUDIO_VO.md` — the **VO-narrated variant**: 50.5s timeline, VO generation, ducked music bed, and the tick·tick·tock keypress-outro SFX recipe.
- `scaffold/` — **self-contained EnConvo film factory**: canonical Minimal + Line Art templates (16:9 + 9:16), all brand assets bundled (logo, keycaps, `ambient.wav` bed, tick/tock/whoosh SFX), demo clips + VO, `scripts/make_themes.py` + `scripts/build_audio.sh`, and `BUILD.md`. Copy it, swap the clips, render, mux.

## Quality checklist before delivery
- [ ] `hyperframes check`: 0 errors, WCAG AA passes (esp. the Minimal light theme's muted labels).
- [ ] Every hero panel is large enough to read the real UI; skew not so steep it hides content.
- [ ] S7 shows one panel at a time — no pile-up, keyword row is a whisper.
- [ ] Headlines break on intended lines (check `.mega .line` blocks, esp. vertical).
- [ ] Score peak ≈ −1 dBFS; muxed (not an `<audio>` element); `-shortest` trims clean.
- [ ] Edge-UI clips (toolbars / left-anchored panels): key buttons fully in-frame in the **landscape** cut — reframe if the left bleed clips them (safe in vertical).
- [ ] VO cut: keypress outro is **tick·tick·tock** (not per-key ticks); the D tock clearly audible over the spoken "D"; one shared mix muxed onto both orientations; VO intelligible over the ducked bed (transcribe to confirm).
- [ ] Line Art: every panel carries the navy frame + flat-offset shadow; gold is the *only* accent; titles are heavy navy on cream.
- [ ] Both orientations + posters exported; frame sheet eyeballed.
