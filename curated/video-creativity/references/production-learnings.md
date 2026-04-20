# Production Learnings

Every gotcha below was discovered during a real render. Each one cost time. Each one is now a spec-level anti-pattern that the "What NOT to Do" section of the spec must quote if relevant.

## HYP-1 · Sub-composition visibility derives from GSAP timeline duration, NOT `data-duration`

**Severity:** CRITICAL.

**Observed:** Artemis II render. Scenes 2, 3, 7 appeared correctly for their opening ~8 seconds then went black — only starfield, audio, and captions continued. `data-duration` on the host clip said 14.8s for scene 2, but scene 2's content vanished at 14s global time (≈8s local time).

**Root cause:** The HyperFrames runtime IIFE (`hyperframe.runtime.iife.js`) strips `data-duration` and `data-end` from every `[data-composition-id]` element except the document root. It then uses the GSAP timeline's actual `.duration()` to compute effective lifetime, and hides the sub-comp via `visibility: hidden` once `currentTime >= clipStart + tl.duration()`.

**Fix (must be in every sub-comp):**
```js
window.__timelines = window.__timelines || {};
var tl = gsap.timeline({ paused: true });
// ... entrance tweens ...
// HOLD TWEEN — extend tl.duration() to full intended lifetime
tl.to({}, { duration: SCENE_DURATION_SECONDS }, 0);
window.__timelines['scene-N'] = tl;
```

**Add to spec's anti-patterns:** "Every sub-composition must include a no-op hold tween `tl.to({}, { duration: SCENE_DURATION }, 0)` before the timeline registration. Without it, scenes go black mid-playback."

## HYP-2 · Framework strips `data-duration` from non-root composition hosts

**Severity:** HIGH.

**Observed:** Same as HYP-1. Setting `data-duration="14.8"` on the scene-2 host div in root index.html had no effect on when the scene was hidden.

**Implication:** You cannot rely on the host clip's `data-duration` to control scene lifetime. You must pad the inner GSAP timeline via HYP-1's hold-tween fix. Don't duplicate `data-duration` and expect it to work.

## CAP-1 · Caption layer at high z-index must have `pointer-events: none` AND no background

**Severity:** MEDIUM.

If the caption sub-composition root has any non-transparent background, it clips scenes beneath it during the render. Even `rgba(0,0,0,0.01)` is enough to shift composited colours.

**Fix:** Caption composition root must declare `background: transparent; pointer-events: none;`.

## CAP-2 · Caption groups must have a hard `tl.set` kill at group.end

**Severity:** MEDIUM.

Exit animations that only tween opacity to 0 can leave captions fractionally visible when GSAP rounding kicks in. Always add a `tl.set(el, { opacity: 0, visibility: 'hidden' }, group.end)` after the exit tween.

## GRAD-1 · Full-screen linear gradients on dark backgrounds cause H.264 banding

**Severity:** HIGH in rendered MP4.

In Studio preview everything looks clean. After render, the gradient shows visible banding stripes. This is unavoidable with H.264's 8-bit colour on smooth dark ramps.

**Fix:** Use radial gradients (localised), solid fills with a single localised glow, or a subtle noise overlay (seeded PRNG, 4–8% opacity) to break up the banding. Applies to all dark-canvas styles (Mission Control, Data Drift, Neon Frequency, Shadow Cut, Broadcast Bulletin).

## POS-1 · `position: absolute; inset: 0` inside sub-comp roots collapses unpredictably

**Severity:** MEDIUM.

The framework wraps sub-composition roots with its own sizing. Children that rely on `inset: 0` sometimes size to 0 before content renders.

**Fix:** Prefer explicit `width: 1920px; height: 1080px` on the sub-comp root, OR use `top/left/width/height` with explicit pixel values on children, OR use flex with `padding` (not absolute positioning) on full-bleed containers.

## GSAP-1 · Overlapping tweens on the same property trigger lint warnings

**Severity:** LOW (warning), but affects choreography.

If two tweens animate the same property on the same element with overlapping time windows, `hyperframes lint` warns. Fix by adding `overwrite: 'auto'` to the later tween OR by separating their time windows.

## GSAP-2 · Never `repeat: -1`

**Severity:** CRITICAL for rendering.

Infinite-repeat tweens break the deterministic capture engine. Calculate exact repeat counts:
```js
repeat: Math.ceil(COMP_DURATION / CYCLE_DURATION) - 1
```

## STT-1 · Enconvo transcribe endpoint returns empty outside a command runtime

**Severity:** HIGH (blocks caption generation).

**Observed:** `local_api transcribe/transcribe_audio_video {...}` returned `{content: ""}` for a 77-second audio file even though the Enconvo Cloud Plan is configured with `groq/whisper-large-v3`.

**Root cause:** The handler calls `TranscriptionProvider.fromEnv()` which reads `runtime.preferences.stt`. That value is only populated by Enconvo's command launcher — not by `local_api` passthrough from an agent session.

**Fix (working path):**
1. `local_api credentials/load_credentials {"providerName":"groq"}` → returns decrypted `apiKey`.
2. `curl -X POST https://api.groq.com/openai/v1/audio/transcriptions -H "Authorization: Bearer $KEY" -F file=@narration.wav -F model=whisper-large-v3 -F response_format=verbose_json -F "timestamp_granularities[]=word"`.
3. Parse `words[]` into HyperFrames caption format `{text, start, end}`.

**Fallback:** Local Python `whisper small.en --word_timestamps True --output_format json`.

## STT-2 · Disk credentials JSON contains encrypted strings, not raw keys

**Severity:** HIGH.

`~/.config/enconvo/installed_preferences/credentials|<provider>.json` stores an **encrypted reference** under `apiKey`. Reading it directly and using the string as a Bearer token returns 401.

**Fix:** Always fetch via `local_api credentials/load_credentials {"providerName": "<provider>"}` which decrypts on demand.

## DEBUG-1 · When scenes mysteriously go black, extract frames at 1s intervals first

**Severity:** N/A (methodology).

Rather than theorising about transitions / z-index / CSS issues, extract actual frames from the rendered MP4 at 1-second intervals with `ffmpeg -ss N -i video.mp4 -vframes 1 out.jpg` and visually inspect. The disappearance pattern (which scenes fail, at what local time, what ambient layers survive) usually reveals the cause in 30 seconds.

## AUDIO-1 · TTS duration rarely matches the natural word count

**Severity:** LOW.

A 150-word script does NOT reliably produce a 60-second voice clip. Documentary pacing often runs slower (77s for 150 words in the Artemis example). Generate audio first, read its actual duration via `ffprobe`, THEN finalise scene durations.

```bash
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 narration.wav
```

Use the measured duration as the composition's `data-duration`, not the target.

## SHADER-1 · `@hyperframes/shader-transitions` is a separate optional package

**Severity:** LOW.

If shader transitions are wanted and the package isn't installed, don't fail — fall back to CSS sine crossfades (0.6s `sine.inOut`). Document the fallback in the spec's Technical block.

## FONT-1 · Just declare `font-family`; the compiler embeds it

**Severity:** LOW.

Don't inject `<link rel="stylesheet">` for Google Fonts. The HyperFrames compiler auto-detects `font-family` declarations and embeds supported fonts via @font-face. If a font isn't supported, the compiler warns.

## TIMING-1 · Narration word timestamps are authoritative for scene cuts

**Severity:** LOW.

Don't guess where to split scenes based on the script text. After transcription, grep the actual word start times and align scene transitions 0.2–0.4s AFTER a sentence-ending word (never mid-sentence).

---

## How to use this file

When authoring the "What NOT to Do" section of a spec, pull anti-patterns from here that apply to the chosen style + scene structure. Minimum 5 bullets per spec. Every dark-canvas style MUST include GRAD-1. Every multi-scene video MUST include HYP-1 and HYP-2. Every voiced video MUST include STT-1/STT-2 (so the downstream hyperframes build knows the correct transcribe path).
