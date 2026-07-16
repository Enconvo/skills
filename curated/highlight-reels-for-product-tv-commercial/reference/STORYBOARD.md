# STORYBOARD.md — beat map + per-scene cues (42s @ 30fps)

Start times are **beat-anchored to the score** — keep them when re-skinning or swapping copy. Only change copy, clips, and theme tokens.

## Beat anchors
- **Transition whooshes / impacts:** 9.4, 20.0, 30.4 s
- **Aurora orb hue shifts:** 9, 20, 26, 36 s
- Scene starts: 0, 4.8, 9.8, 15.3, 20.3, 25.8, 30.8, 35.6 s

## Scenes

### S1 — Logo bloom (0–5.2)
- Logo/icon scales + de-blurs in (0.35s), chromatic `--ca` 16→3 (Aurora) or plain (Minimal), wordmark rises (1.55s), kicker fades (2.2s). `groupOut` 4.7.
- Copy: wordmark = product name; kicker = one-line positioning.

### S2 — Thesis (4.8–10.2)
- eyebrow (5.0) → `head` per-word reveal (5.15) → `mega` headline per-word (5.45) → product command-bar pill rises (6.4) with a blinking caret (7.2). `groupOut` 9.5.
- Copy: head = setup line; mega = the promise (“a command center.”). Pill = the product's primary input surface.

### S3–S6 — Feature scenes (9.8 / 15.3 / 20.3 / 25.8)
Each ~5.4s: `tiltIn` panel (alternating side & tilt direction) → eyebrow → title per-word `wordsIn` → ticks/chip → `tiltOut` + `groupOut` at the next boundary.
- S3 panel **right** / text left. S4 panel **left** / text right. S5 panel **right** / text left. S6 panel **left** / text right + **metric chip** (`back.out` pop at +1.3s).
- Copy: eyebrow = feature name; title = 2–3 short lines (the benefit, not the feature); ticks = 3 supporting nouns.
- Clip: the single most legible ~5s beat of that feature's recording.

### S7 — Capability montage (30.8–36.0)
- Faint keyword row fades in (30.8) and drifts. **Three big panels, one at a time** via `montageBig`: 30.9 / 32.4 / 33.9, each ~1.9s with a 0.4s cross-blur, on **separate tracks 5/6/7**. Mega “…and everything between.” per-word (32.6). `groupOut` 35.5; row fades 35.4.
- This scene conveys breadth. **Never** show all three panels simultaneously or a loud full word-wall — that's the “too busy” failure mode this design fixes.

### S8 — Close / CTA (35.6–42.0)
- Icon bloom (35.9) → wordmark (36.7) → tagline (37.3) → CTA block (37.9) with URL `back.out` pop (37.95) → slow 1.015× push-in (38.2) → whole lockup fades (41.5).
- Copy: wordmark; tagline = the promise restated; url + “what it is · free to try” sub. **Poster frame ≈ 1185** (39.5s) — fully settled, before the fade.

## Retiming
To change total length, scale all start times proportionally and regenerate the score so impacts land on the new transition anchors. The per-scene internal cues are relative offsets from each scene start, so they follow automatically.
