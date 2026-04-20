# Artemis II: Return to the Moon

**Project slug:** `artemis-ii`
**Style preset:** Mission Control Cinematic
**Duration target:** 78s (measured after TTS; originally targeted 60s, documentary pacing added ~17s)
**Aspect ratio:** 1920×1080
**FPS:** 30
**Voice-over:** yes — authoritative documentary, measured pace, neutral gender, no affect
**Captions:** yes — word-synced, bottom-center, JetBrains Mono 44px, bone-white on void with drop shadow
**Primary transition:** CSS sine crossfade, 0.6s, `sine.inOut` (shader transitions package not installed; graceful fallback)

## One-line synopsis
The first crewed lunar flyby in over 50 years, told in 7 timed beats: launch, trans-lunar injection, outbound coast, lunar flyby (hero), return coast, re-entry, splashdown.

---

## Visual Identity

### Palette
| Role | Hex | Use |
|---|---|---|
| Canvas | `#05070D` | body bg (void black) |
| Surface | `#0B1426` | stat cards, panels (deep navy) |
| Foreground | `#E8EEF7` | all text — bone white, cool-tinted, never pure white |
| Ignition | `#FF6B35` | launches, burns, CTAs, countdown pulses |
| Telemetry | `#4FC3F7` | trajectories, data labels, cyan accents |
| Lunar gold | `#FFD166` | Moon surface, closest-approach marker, final stats |

### Typography
- **Display / headings:** Space Grotesk, weights 500 / 700, tracking -0.01em on 100px+, +0.08em on small caps
- **Body / secondary:** Space Grotesk 400, minimum 24px
- **Numbers / telemetry:** JetBrains Mono 500, `font-variant-numeric: tabular-nums` always on
- **Captions:** JetBrains Mono 44px, `#E8EEF7`, `text-shadow: 0 2px 12px rgba(0,0,0,0.85)`

### Motion signature
- **Entrance eases:** `power3.out`, `expo.out`, `power2.out` (vary minimum 3 per scene)
- **Ambient loops:** `sine.inOut`, 3–6s cycle (starfield drift, marker pulse, ghost text breathe)
- **Counter eases:** `power1.out` / `power2.out`, 1.5–3s duration
- **Transitions:** CSS sine crossfade, 0.6s `sine.inOut` between scenes
- **Scene entrance offset:** first tween at 0.15–0.3s (never t=0)

---

## Media Assets

### Generated stills (T2I)
| ID | Aspect | Prompt | Used in scene |
|---|---|---|---|
| `bg-ksc-pad39b.png` | 16:9 | `"Kennedy Space Center launch pad 39B at pre-dawn, NASA SLS rocket on the pad silhouetted against deep blue sky, mercury vapour lamps glowing amber, photorealistic press-kit style, shot on Sony A7R V 50mm f/1.4, real photograph, no AI smoothing, editorial quality, NASA image archive aesthetic"` | Scene 2 bg (behind SVG rocket, with dark overlay) |
| `moon-farside-hero.png` | 16:9 | `"Close-up of lunar far-side surface, dense crater field, cold low-angle light raking across regolith, pure black space at upper edge, photorealistic, NASA LRO imagery aesthetic, no AI gloss, editorial quality"` | Scene 5 full-frame hero |

### Generated motion (T2V via Veo)
| ID | Type | Duration | Aspect | Source | Prompt | Used in scene |
|---|---|---|---|---|---|---|
| `plume-loop.mp4` | T2V | 6s | 16:9 | — | `"Slow-motion rocket exhaust plume, vertical column of orange and yellow flame with grey smoke trail, isolated on pure pitch-black background, seamless loop, cinematic realism, real footage aesthetic"` | Scene 2, composited beneath SVG rocket, z-index 1, muted playsinline loop |
| `pacific-dawn.mp4` | T2V | 8s | 16:9 | — | `"Calm Pacific Ocean at dawn, gentle low waves, warm orange horizon glow transitioning to cool violet sky above, static camera, cinematic realism, no people, real footage aesthetic"` | Scene 7 ambient background (behind line-art Orion + parachutes SVG) |

*Total generation cost: ~45s (2× T2I) + ~4min (2× T2V Veo) = under 5 minutes before hyperframes build.*

---

## Music & Sound

**Approach:** full-score with VO ducking.
**Justification:** Mission Control Cinematic benefits from a restrained orchestral bed that tracks the mission's emotional arc — silence would read documentary-TV, too loud reads Hollywood. A quiet score with one timpani hit on the closest-approach reveal punches scene 5 without stepping on the VO.

### Score brief (via `acestep`)

- **Genre/mood:** cinematic orchestral, restrained; low strings + brushed timpani + ambient synth pad; no percussion kit; no melodic lead.
- **BPM:** 72
- **Key / scale:** D minor
- **Duration:** 78 seconds (matches measured narration.wav)
- **Structural arc:**
  - 0–5.6s: solo low sustained D drone (pad), ambient, establishes void.
  - 5.6–20.4s (launch): cellos enter at 0:06 with subtle dotted rhythm, gradual crescendo +4 dB by 0:18.
  - 20.4–33s (TLI): bass synth adds a deep pulse at 0:22; sustained brass swell begins at 0:28.
  - 33–41s (outbound coast): brass swell resolves; cellos drop to a whisper; high sine drone enters — lonely, vast.
  - 41.2–60s (hero moment): **2-second silence at 0:45 before one timpani hit at 0:47** aligned to the "6,545" value slam. Strings re-enter at 0:50 with minor-key emotional swell lasting through the crew-name stagger.
  - 59.4–68s (return coast): full texture, steady, confident.
  - 68–78s (splashdown): descending string line; pad holds last note through the fade-to-black tail.
- **Full acestep caption:**
  > `"Cinematic orchestral score, 72 BPM, D minor, restrained and weighted. Solo low D drone from 0:00. Cellos enter at 0:06 with a subtle dotted rhythm, crescendoing gently to 0:18. At 0:22 a deep bass synth pulse enters. 0:28 brass swell rises and resolves. 0:33 cellos whisper, high sine drone enters — lonely, vast. Full SILENCE from 0:45 to 0:47. Single deep timpani hit at 0:47. Strings re-enter at 0:50 with a slow minor-key emotional swell that holds through 1:00. From 1:00–1:08 full texture, steady, confident. From 1:08 descending string line to end, pad holds the last note through 1:18, long natural decay. No percussion kit, no melodic lead line, no vocals. NASA mission brief aesthetic, Hans Zimmer restraint."`

### Mix & levels

- VO: -4 dB peak (bone-white narration is primary channel)
- Music under VO: -22 dB (ducked)
- Music in VO gaps (0:02–0:04, 0:18–0:20, 0:45–0:47, 0:53–0:54, 1:09–1:12): -14 dB (breathe)
- Tail trim: 2s natural decay at end; no hard cut

### Silence decisions

- **0:45–0:47 (scene 5 opening)** — the 2-second total silence immediately before the closest-approach timpani hit is the single most important sound design moment in the piece. Do not fill it.
- **Starfield ambient hum** (subtle white noise + ~60Hz low pad) runs continuously 0:00–1:18 at -30 dB, z-index below the score. Gives spatial depth without competing.

---

## Scene Breakdown

Total scenes: 7. Total runtime: 78s. Ambient starfield runs continuously 0–78s at z-index 0.

### Scene 1 — TITLE CARD · 0.0–6.2s

**Archetype:** Title Card

**Heading:** `ARTEMIS II`
**Kicker:** `NASA · MISSION BRIEF`
**Subtitle:** `First Crewed Lunar Flyby in Over 50 Years`
**Data:**
- Mission patch silhouette (large radial gradient circle, inset glyph "ARTEMIS II" in mono, 14px 0.35em tracked)
- Datetime stamp bottom-left: `● APR 01 2026 · 22:35 UTC · KSC LC-39B` (mono, ignition-orange dot)
- Corner metadata: "FLIGHT · A-II" (top-right), "CLASSIFICATION / MISSION BRIEF" (bottom-right)

**Motion beats:**
1. 0.15s — Mission patch scales 0.85→1, `power3.out`, 1.4s; then slow 6s rotation to 6°, `sine.inOut`
2. 0.4s — Kicker slides up y:30, `power3.out`, 0.7s
3. 0.55s — Title slams up y:90, `expo.out`, 0.95s
4. 1.0s — Subtitle fades+slides y:40, `power3.out`, 0.8s
5. 1.3s — Horizontal rule scales from `scaleX: 0 → 1`, `power2.out`, 0.7s
6. 1.5s — Stamp slides x:-40, `power2.out`, 0.7s; stamp dot scales from 0, then pulses opacity for 5 cycles

**Narration:**
> Artemis Two. The first crewed lunar flyby in over fifty years.

---

### Scene 2 — PHASE 01 · LAUNCH + HEO · 5.6–20.4s

**Archetype:** Launch / Intro

**Phase label:** `PHASE 01 · LAUNCH + HEO` (ignition orange, mono, +0.32em tracked)
**Heading:** `SLS lights up<br/>Pad 39B.`
**Body:** `Four astronauts climb toward a high elliptical orbit — system checkouts before committing to the Moon.`
**Annotation:** `~24 h ELLIPTICAL ORBIT · CHECKOUTS`
**Data (live ticker, bottom-bar):**
- `T+` counter: `00:00:28 → 00:13:40` (hh:mm:ss, `power1.inOut`, 6.5s)
- `ALT` counter: `842 km → 1,742 km` (`power2.out`, 6.5s)
- `VEL` counter: `7.92 km/s → 10.36 km/s` (`power2.out`, 6.5s)
- `STATUS` badge: `NOMINAL` (ignition orange)
**Decoratives:**
- SLS line-art SVG (white 1.8px stroke, 380px tall) — core stage, boosters, upper stage, Orion capsule
- Plume beneath rocket (radial gradient lunar-gold → ignition-orange, blur(10px)), pulses `sine.inOut` 0.14s × 41 repeats
- Grid background (80px × 80px hairlines, `rgba(79,195,247,0.04)`)

**Motion beats:**
1. 0.2s — Phase label slides x:-40, `power3.out`, 0.6s
2. 0.4s — Heading slams up y:40, `expo.out`, 0.8s
3. 0.5s — Rocket slides up from y:120, `power3.out`, 1.1s; then continues rising y→-60 over 6.5s `power1.in`
4. 0.7s — Body fades, `power3.out`, 0.7s
5. 1.0s — Annotation fades in
6. 1.2s — All three telemetry counters begin rolling simultaneously
7. 1.4s — Plume scales from `scaleY: 0`, `power2.out`, 0.5s; then begins 40-repeat yoyo pulse
8. 1.9s — Plume pulse begins (40 repeats × 0.14s duration, ~11.2s total)

**Narration:**
> On April first, twenty twenty-six, NASA lights the Space Launch System at Kennedy pad thirty-nine B. Four astronauts climb toward a high Earth orbit, twenty-four hours of system checkouts before committing to the Moon.

---

### Scene 3 — PHASE 02 · TRANS-LUNAR INJECTION · 19.8–33.6s

**Archetype:** Data Reveal (with trajectory diagram)

**Phase label:** `PHASE 02 · TRANS-LUNAR INJECTION`
**Heading:** `Bending toward the Moon.`
**Body:** `A 6-minute burn slips Orion onto a free-return trajectory. Gravity will do the rest.`
**Burn annotation:** `● TLI BURN · 6 MIN` (ignition orange, flame dot with box-shadow glow)
**Stat card (right-side, elevated surface):**
- Label: `Δv` (mono 12px, 0.28em tracked)
- Value: `+0.00 → +3.05` (telemetry cyan, 64px JetBrains Mono, `power2.out` 3.0s)
- Unit: `km/s`
**Decoratives:**
- SVG diagram full-width bottom half: Earth (radial gradient telemetry-cyan → deep navy, r=110), Moon (radial gradient lunar-gold → dark, r=58), trajectory arc drawn with `stroke-dashoffset` animation (telemetry cyan, 3px, 3.6s `power2.inOut`)
- Orion dot travels the trajectory via keyframes: 3 segments × (1.2s / 2.2s / 2.1s)

**Motion beats:**
1. 0.15s — Phase label slides x:-40, `power3.out`, 0.6s
2. 0.3s — Heading slams up y:40, `expo.out`, 0.75s
3. 0.55s — Body fades, `power3.out`, 0.7s
4. 0.4s — Earth scales from 0.7, `power3.out`, 0.9s
5. 0.55s — Moon scales from 0.7, `power3.out`, 0.9s
6. 0.8s — Trajectory path draws in, `power2.inOut`, 3.6s
7. 1.6s — Burn marker scales in at mid-trajectory, `power2.out`, 0.4s; then pulse yoyo 10 repeats
8. 1.7s — Burn label slides x:-30
9. 2.5s — Stat card slides up y:40, `power3.out`, 0.75s
10. 2.8s — Δv counter counts 0 → 3.05, `power2.out`, 3.0s
11. 1.6s — Orion dot begins traveling along trajectory keyframes

**Narration:**
> Then, the Trans-Lunar Injection burn. Six minutes of thrust. Delta-v plus three point zero five kilometers per second, bending their path into a free-return trajectory.

---

### Scene 4 — PHASE 03 · OUTBOUND COAST · 33.0–41.8s

**Archetype:** Hero Moment (setup) / Stat Reveal

**Phase label:** `PHASE 03 · OUTBOUND COAST`
**Heading:** `Four days<br/>to the Moon.`
**Body:** `Orion drifts on momentum. Earth recedes. The Moon grows in the window.`
**Distance counter (upper right):** `384,000 → 6,545 km · CLOSING` (92px mono)
**Day counter (lower right):** `T+ 00D 00H → T+ 04D 00H` (16px, +0.32em tracked, telemetry cyan)
**Progress track (bottom):** `EARTH → OUTBOUND → MOON`, filling left-to-right over 6.5s
**Decoratives:**
- Earth (520×520 radial gradient, upper-left, shadow glow)
- Moon (growing 140 → 190 over 7.5s, upper-right)
- Orion capsule SVG on the progress track dot (small, line-art)

**Motion beats:** See production spec. Earth stays, Moon scales up linearly. Distance counter winds down, progress bar fills.

**Narration:**
> For four days, Orion coasts outbound. Earth shrinks behind them. Ahead, the Moon grows.

---

### Scene 5 — PHASE 04 · LUNAR FLYBY · 41.2–60.0s  (HERO MOMENT)

**Archetype:** Hero Moment

**Phase label:** `PHASE 04 · LUNAR FLYBY` (lunar-gold)
**Date:** `APR 06 2026 · 18:42 UTC`
**Marker label:** `CLOSEST APPROACH` (lunar-gold, 14px, 0.32em tracked)
**Marker value:** `6,545` (Space Grotesk 120px 700)
**Marker unit:** `KILOMETERS · FAR SIDE`
**Note block:**
- Primary: `406,771 KM FROM EARTH` (Space Grotesk 22px 500)
- Context: `the farthest humans have ever traveled.`
**Crew nameplate (right, staggered entry):**
- `CREW · ARTEMIS II` (label)
- `REID WISEMAN`
- `VICTOR GLOVER`
- `CHRISTINA KOCH`
- `JEREMY HANSEN`
**Decoratives:**
- Full-frame Moon (1400×1400 radial-gradient with inset shadow to simulate sphere, warm-gold palette)
- 28 craters (seeded PRNG, sized 20–140px, scattered inside disk, mix-blend-mode multiply, 0.45 opacity)
- Trajectory arc sweeping behind the Moon (lunar-gold, 3px, `stroke-dashoffset` animation)
- Pulsing marker at closest-approach point (14px circle, lunar-gold, expanding box-shadow 0→40px)

**Motion beats (~18s of choreography):**
1. 0.0s — Moon fades in from scale 0.78, `power3.out`, 2.0s
2. 2.0s — Moon slowly scales to 1.08 over 12s, `power1.inOut` (camera push)
3. 0.3s — Phase label slides x:-40
4. 0.4s — Date slides x:40
5. 0.8s — Trajectory draws in, `power2.inOut`, 4.5s
6. 1.0s — CLOSEST APPROACH label fades
7. 1.2s — 6,545 value slams up y:60, `expo.out`, 0.9s
8. 3.0s — Pulsing marker activates, 5 pulse cycles
9. 7.5s — Crew label fades in
10. 7.7s — 4 crew names stagger in 0.18s apart, x:40 slide, `power3.out`, 0.6s each

**Narration:**
> On April sixth, closest approach. Just sixty-five hundred kilometers above the far side. Four hundred six thousand kilometers from Earth. The farthest humans have ever traveled. Wiseman. Glover. Koch. Hansen.

---

### Scene 6 — PHASE 05 · RETURN COAST · 59.4–68.2s

**Archetype:** Figure-Eight / Return

**Phase label:** `PHASE 05 · RETURN COAST`
**Heading:** `Free-return.<br/>Gravity brings them home.`
**Body:** `The figure-eight completes. Orion accelerates toward re-entry.`
**Corner stat (upper right):** `TRAJECTORY / FREE-RETURN · FIG 8` (telemetry cyan, 42px)
**Velocity reveal (lower left, bordered with ignition-orange rule):**
- Label: `RE-ENTRY VELOCITY`
- Value: `0.00 → 11.02` (ignition orange, JetBrains Mono 128px, `power2.inOut`, 5.2s)
- Unit: `km/s · CLIMBING`
**Decoratives:**
- Earth (growing 240 → 276 over 6s, lower-right)
- Moon (shrinking 120 → 90 over 6s, upper-left)
- Return trajectory arc (`stroke-dashoffset`, telemetry cyan, completes figure-8)
- Arrow tip at re-entry endpoint (ignition orange, fades in at 5.0s)

**Narration:**
> Gravity swings them home. Orion accelerates through re-entry at eleven kilometers per second.

---

### Scene 7 — PHASE 06 · SPLASHDOWN · 67.8–78.0s (OUTRO)

**Archetype:** Outro / Closing Stat Block

**Phase label:** `PHASE 06 · SPLASHDOWN`
**Date:** `APR 11 2026 · PACIFIC OCEAN`
**Title:** `Mission complete.` (56px, 500)
**Closing stat block (bottom):**
- `10` DAYS
- `1` FLYBY
- `4` ASTRONAUTS
- `∞` AMBITION (lunar gold)
**Next-mission callout (right):**
- `NEXT` (label)
- `ARTEMIS III` (ignition orange, 44px, 700)
- `Boots on the Moon.` (22px)
**Decoratives:**
- Sky gradient top 60% (radial ignition-orange glow at horizon → violet-tinted void at top)
- Ocean gradient bottom 40% (telemetry cyan tint → deep navy)
- Horizon rule (2px, `rgba(232,238,247,0.18)`)
- Setting sun (180×180 radial gradient lunar-gold)
- Orion capsule with 3 parachutes (line-art SVG, 220px, floats down via y:-160 → y:20, `sine.inOut`, 6s)
- Scan-line pattern on ocean (repeating linear-gradient, 1px × 12px)

**Motion beats:**
1. 0.1s — Sky fades in
2. 0.2s — Ocean fades in
3. 0.3s — Horizon rule scales from 0
4. 0.4s — Sun scales from 0.6, `power2.out`, 1.6s
5. 0.6s — Orion drops from y:-160, `power2.out`, 1.8s; then gently descends y:20 over 6s `sine.inOut`
6. 0.8s — Phase label slides
7. 0.95s — Date slides
8. 2.0s — 4 stat columns stagger in 0.18s apart
9. 3.4s — Title fades in
10. 3.6s — Closing block staggers (label, big, sub)
11. **8.6s — Fade-to-canvas 1.2s, `power2.in`** (THE ONLY EXIT ANIMATION IN THE ENTIRE VIDEO)

**Narration:**
> Three parachutes. Pacific dawn. Ten days. One flyby. Four astronauts. Infinite ambition. Artemis Three is next. Boots on the Moon.

---

## Technical Block

| Field | Value |
|---|---|
| Root composition `data-duration` | 78 |
| Audio file | `narration.wav` (77.52s measured) |
| Transcript source | `transcript.json` (Groq Whisper-Large-V3, verbose_json, word-level) |
| Caption groups | `captions.json` — 43 groups, 3–5 words each, break on `.?!` or 0.35s+ pauses |
| Starfield layer | yes, 0–78s, z-index 0, seed `20260401`, 240 stars in 3 parallax layers + 2 nebula clouds |
| Transition type | CSS sine crossfade 0.6s between scenes |
| Render quality | standard |
| Render FPS | 30 |

### Audio pipeline
1. `local_api tts/tts` with the 6 narration snippets concatenated into one script (~1027 chars).
2. `ffprobe` narration.wav → 77.52s. Update root `data-duration` to 78.
3. `local_api credentials/load_credentials {"providerName":"groq"}` → decrypted Groq key.
4. `curl POST https://api.groq.com/openai/v1/audio/transcriptions` with model whisper-large-v3, verbose_json, timestamp_granularities[]=word → 140 word-level timestamps.
5. Python-side group into 43 caption groups (3–5 words, break on sentence-ending punctuation).
6. Feed groups to captions sub-composition.

---

## What NOT to Do

### Mandatory
- **Every sub-composition must include a no-op hold tween** `tl.to({}, { duration: SCENE_DURATION_SECONDS }, 0)` before `window.__timelines['scene-N'] = tl;`. The HyperFrames runtime strips `data-duration` from non-root composition hosts and uses the GSAP timeline's actual `.duration()` to determine scene visibility lifetime. Without the hold tween, scenes go black once their last real tween ends. (HYP-1, HYP-2)
- **Do not call `local_api transcribe/transcribe_audio_video` from this agent context** — it silently returns empty because `runtime.preferences.stt` isn't populated outside a command launcher. Use the direct Groq path. (STT-1)
- **Do not read `credentials|groq.json` on disk for the API key** — the stored string is encrypted. Always call `credentials/load_credentials` first. (STT-2)
- **Never `repeat: -1`** — calculate exact repeats: `repeat: Math.ceil(duration / cycleDuration) - 1`.
- **Only Scene 7 uses exit animations** — all other scenes rely on the 0.6s sine crossfade to handle their exit. Exit tweens on intermediate scenes cause the transition to fire on an empty frame.

### Style-specific (Mission Control Cinematic)
- ❌ Generic tech-blue (`#3B82F6`, `#0EA5E9`). Telemetry cyan is `#4FC3F7` only.
- ❌ Roboto / Inter / Montserrat. Space Grotesk + JetBrains Mono, nothing else.
- ❌ `back.out`, `elastic`, or any overshoot easing. NASA doesn't bounce.
- ❌ Emoji or clipart rockets. Line-art SVG only.
- ❌ More than one hero colour visible at once (ignition orange, telemetry cyan, lunar gold — each has a domain).

### H.264 hygiene
- **No full-screen linear gradients on dark backgrounds** — visible banding in rendered MP4. Use radial gradients (Earth, Moon, Sun), solid fills with localised glow (burn marker), or seeded noise overlays. (GRAD-1)

### Layout hygiene
- **Avoid `position: absolute; inset: 0` on full-bleed content containers inside sub-comp roots.** The framework's wrapper sometimes collapses this to 0×0. Use explicit `width: 1920px; height: 1080px` or flex + padding instead. (POS-1)

---

## Handoff to HyperFrames

```
Load the `hyperframes` skill. Build the video described in
<session_dir>/artemis-ii-spec.md. The spec is self-contained —
palette, fonts, scene breakdown, narration, and anti-patterns
are all inline. Follow the spec's 'What NOT to Do' section
strictly, especially the mandatory hold-tween in every
sub-composition.
```
