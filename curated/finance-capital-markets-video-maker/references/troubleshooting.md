# Troubleshooting

Every entry here = a bug we actually hit on the SpaceX IPO ACT 1 build. Skip the pain by skimming this before each new ACT.

## Visual Bleed Bugs

### Light streak appears on anchor's body

**Symptom:** A bright diagonal gradient cuts across the anchor's torso every time the shimmer animation plays.

**Root cause:** Shimmer was implemented as `.panel::before` with `mix-blend-mode: screen`, `position: absolute; inset: 0; transform: translateX(-110%)`. Panel had no `overflow: hidden`. The pseudo-element's bright gradient band sat at `panel_left - 320px`, landing on the anchor.

**Fix:**
1. Add `overflow: hidden` to `.panel`.
2. Replace `::before` with a real `<span class="shimmer">` inside each panel.
3. Remove `mix-blend-mode: screen` — use plain `z-index: 5` instead.
4. Animate the real element, not the pseudo.

### Dark shadow band appears left of the panel

**Symptom:** A soft black fall-off bleeds ~60px to the left of the panel edge, dimming the anchor's right side.

**Root cause:** `box-shadow: -18px 0 60px rgba(0,0,0,0.35)` extends outward from the panel.

**Fix:** Use only `inset` shadows on the panel. Example: `box-shadow: inset 4px 0 0 var(--gold), inset 8px 0 30px rgba(255,214,104,0.08)`.

## HF Lint Errors

### `composition_self_attribute_selector`

This is a WARNING, not an error. Acceptable on the root `[data-composition-id="root"]` selector. If it fires on scene `#sN` selectors, switch to scoped IDs instead of nested attribute selectors.

### `overlapping_gsap_tweens`

**Symptom:** Lint flags two tweens animating the same property on the same element in overlapping time windows.

**Fix:** Add `overwrite: 'auto'` to the later tween, or move its start time so it begins after the earlier tween ends. Common case: an entrance `back.out` tween ends at T+0.5, then a pulse tween starts at T+0.4. Move the pulse to T+0.6.

### `GSAP target #sN .x:nth-of-type(M) not found`

**Root cause:** HF's DOM scoping doesn't resolve `:nth-of-type` against the composition root reliably.

**Fix:** Add unique IDs or classes to those elements and target them directly. e.g. replace `#s1 .stat-row:nth-of-type(1) .label` with `#s1 .label-raise`.

### `GSAP target  not found` (target is blank)

**Root cause:** A `shimmer(scopeSel + '::before', ...)` call — GSAP can't animate pseudo-elements.

**Fix:** Use real DOM elements, never pseudo-elements, as GSAP targets.

### Lint passes but render shows no animation

**Root cause:** Missing `data-start="0"` on the root composition div. HF can't probe duration.

**Fix:** Add `data-start="0" data-width="1280" data-height="720"` to the root.

## Font / CJK Issues

### Chinese characters render as boxes or fall back to system serif

**Symptom:** 本期拆解路线 renders as Latin-only fallback or empty squares in the rendered MP4.

**Root cause:** Headless Chromium in HF doesn't ship macOS PingFang SC. Font stack falls through to a generic that has no CJK glyphs.

**Fix:** Add a `<link>` to Google Fonts for `Noto Sans SC` + `Noto Serif SC` in the HTML `<head>`. HF compiler auto-fetches and inlines (~900 font faces per family). Yes, the lint will warn about `google_fonts_import` — acceptable.

### Fraunces serif numbers look chunky in CJK headers

**Root cause:** Fraunces has no CJK glyphs and the browser substitutes with whatever serif is available.

**Fix:** Use Fraunces only for Latin numerals and English. Use `Noto Serif SC` for CJK headers when a serif feel is needed.

## Layout / Text Overflow Bugs

### A seal / verdict / card-title wraps with a lone trailing glyph (shipped into the video)

**Symptom:** A gold seal that should read on one line broke as `其余凭空消` on line 1 + a lone `失` on line 2 — and it was already burned into the rendered MP4 and sent to the user before anyone caught it.

**Root cause:** The seal copy (`只成一半 · 其余凭空消失`, 11 glyphs) at 26px with 0.30em tracking + padding overflowed the ~44% panel's usable width, so it wrapped. `hyperframes lint` passed clean — lint checks STRUCTURE, not rendered pixel layout. No visual audit step existed, so the overflow went straight to burn.

**Fix (two layers):**
1. **CSS guardrail (primary):** give seals/verdicts/card-titles `white-space: nowrap` + short copy (a seal ≤ 8 CJK glyphs) + restrained tracking (~0.14em). Shorten the copy first (`一半成交 · 凭空消失`, 8 glyphs); only then drop font-size (~23px) if still tight.
2. **Phase 4.5 frame audit (backstop):** after EVERY render, extract a frame at each scene's text peak (`ffmpeg -ss <t> -i composite.mp4 -frames:v 1 qa_<t>.jpg`) and EYEBALL each for wrap orphans, overflow, clipping, and tofu before shipping. Lint/validate never replace the eyeball.

**Lesson:** lint 0-errors ≠ visually clean. A composite is not shippable until you have looked at a frame from every scene.

## i2v Pipeline Issues

### Identity drifts across clips

**Symptom:** By clip 4, anchor's face geometry has subtly shifted — different chin, different eye spacing.

**Root cause:** Cumulative drift from feeding endframe-to-endframe without re-anchoring.

**Mitigation:**
1. Every 4–6 clips, re-anchor by setting `image` back to the canonical reference URL. Accept a small visible cut.
2. Strengthen the IDENTITY LOCK block in every prompt.
3. Use a high-fidelity reference image (1024px+ JPEG, well-lit, neutral expression).

### Hands lift off desk into right-40 panel zone

**Symptom:** Anchor gestures, hand crosses into the overlay panel area, overlay sits on top of fingers.

**Fix:** Strengthen the MOTION LOCK clause: "Hands stay FIRMLY locked on the desk surface. No gestures. No hand lift. Right 40% of frame remains COMPLETELY clean negative space."

### Background pans or zooms

**Symptom:** Studio LED plate slowly drifts left or zooms in.

**Fix:** Repeat the static-bg clause twice with different phrasing. Example: "STATIC LED plate behind anchor. The background is COMPLETELY FROZEN. No pan, no drift, no zoom, no camera movement of any kind. Only the anchor's micro-expressions move."

### Subject clipped at the frame edge

**Symptom:** Anchor's crown, shoulder, elbow, or fingers are cut off by the frame edge, or the body is pressed against an edge so the right-45 overlay zone is not clean.

**Root cause:** Either the source render framed the subject too large, OR someone tried to "reach the edges" with a centered `scale=1.10` zoom-crop in ffmpeg. The zoom-crop just magnifies the same composition and pushes the already-marginal parts (crown, elbow, fingers) out of frame.

**Fix:** REGENERATE the anchor at a larger scale / with more headroom so the whole body sits comfortably inside the frame. NEVER force edge-reach by zoom-cropping a finished render. The canonical anchor is the raw model output with the whole body INSIDE the frame, nothing clipped — keep it that way. Add/keep the SUBJECT FRAMING block (block 8) in every prompt: "whole body INSIDE frame, crown/shoulders/elbows/hands never cropped or touching an edge, do NOT zoom or scale the subject to reach the edges."

### Person name / brand term gets transliterated or mangled in the VO

**Symptom:** The Chinese cut should SPEAK proper nouns in English (Brad Katsuyama, RBC, Reg NMS), but the render either says a Chinese transliteration (布拉德·胜山) or garbles the English surname.

**Root cause:** The `[VO LINE]` block carried the English token without telling the model it is English, so grok-imagine guessed at pronunciation.

**Fix:** In the `[VO LINE]` block, after the line, explicitly flag the tokens: *"with 'Brad Katsuyama' and 'RBC' pronounced naturally in English."* Keep the token in Latin letters in the VO text itself (not pinyin). Then VERIFY by transcribing the rendered clip (`transcribe/...`) — a rough phonetic in the transcript (e.g. "Brad Casiema" for Katsuyama) is whisper mis-hearing and acceptable; a full Chinese transliteration is a defect → re-render. Rule lives in `references/script-writing.md` → "Keep brand / tech / person names in ENGLISH."

### VO audio is missing or garbled

**Symptom:** Rendered clip has the visual but no anchor speech.

**Root cause:** xAI sometimes drops the VO bake. No deterministic fix.

**Recovery:** Regenerate the clip. No rescue path — do not try to layer separate TTS, the lipsync will be off.

## ffmpeg / Concat Issues

### Concat fails with "non-monotonous DTS"

**Root cause:** Clips have inconsistent keyframe spacing.

**Fix:** Re-encode each clip to a uniform GOP before concat:
```bash
ffmpeg -i input.mp4 -c:v libx264 -r 30 -g 30 -keyint_min 30 -movflags +faststart -c:a aac out.mp4
```

Alternatively use `concat demuxer` with a `.txt` file of inputs.

### Sparse keyframes warning from HF

**Symptom:** `WARNING: Video "anchor-v" has sparse keyframes (max interval: 10.04s)`.

**Mitigation:** Acceptable for one-shot composition. For long acts (>60s) re-encode with `-g 30 -keyint_min 30` to dense GOP.

### Joining two composited ACT MP4s corrupts at the seam

**Symptom:** After joining `act1_composite.mp4` + `act2_composite.mp4` with the ffmpeg **concat demuxer** (or `-c copy`), the join point shows a freeze, a green/garbled flash, or audio desync — even though each ACT plays clean on its own.

**Root cause:** The two composites have independent keyframe placement and timestamps. A stream-copy concat splices them at non-aligned keyframes, so the decoder seeks into a frame it cannot reconstruct.

**Fix:** Do NOT concat-demux composited acts. Join with a single re-encoding `xfade` pass and a dense GOP:
```bash
ffmpeg -i act1_composite.mp4 -i act2_composite.mp4 -filter_complex \
  "[0:v][1:v]xfade=transition=fade:duration=0.3:offset=<act1_dur-0.3>[v];[0:a][1:a]acrossfade=d=0.3[a]" \
  -map [v] -map [a] -c:v libx264 -r 30 -g 30 -keyint_min 30 -crf 19 \
  -preset medium -movflags +faststart -c:a aac -b:a 192k FULL.mp4
```
This is the same lesson as the within-act seam fix — always re-encode through `xfade` for any join, never stream-copy two finished composites together. For 3+ ACTs, chain the xfades pairwise.

### Dangling / frozen final frame after the join

**Symptom:** The very last frame of the assembled film is blank, frozen, or a duplicate — a ~1–2 frame tail that should not be there.

**Root cause:** HF composites often render ~1–2 frames longer than the anchor source they were built on. When you xfade-join, the trailing surplus survives past the intended end.

**Fix:** Set the final xfade `offset` just inside the last clip (trim the surplus into the transition). QA the tail by byte size: extract the last frame and the second-to-last frame as JPEGs — a real final frame is roughly full-size (e.g. ~170 KB), a blank/frozen tail frame is a small fraction of it (e.g. ~50 KB). If the tail frame is tiny, shorten the offset by a frame or two and re-render.

## Telegram Delivery Issues

### `parse_mode` 400 errors on underscores

**Root cause:** Markdown V2 treats `_` as italic toggle.

**Fix:** Either escape underscores `\_` or send without `parse_mode`.

### File >50MB rejected

**Fix:** Telegram Bot API hard limit. Either compress (`-crf 28`) or split into segments. For 720p 60s composites, 13–20MB is normal — should never hit the limit.
