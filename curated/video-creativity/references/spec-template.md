# Spec Template

Fill in every section. Delete bracketed placeholder comments. Write the final spec to `<session_dir>/<project-slug>-spec.md`. Once approved, this is the single source of truth the `hyperframes` skill will consume.

---

```markdown
# <Title>: <Subtitle or one-line synopsis>

**Project slug:** <lowercase-hyphenated>
**Style preset:** <one of the 11 presets, or "Custom — <name>">
**Duration target:** <seconds>  (measured after TTS; may shift ±20%)
**Aspect ratio:** 1920×1080 | 1080×1920 | 1080×1080
**FPS:** 30 (default) | 60 (high motion)
**Voice-over:** yes / no  —  if yes: <character description, pacing>
**Captions:** yes / no  —  if yes: word-synced, bottom-center
**Primary transition:** <cross-warp morph | sine crossfade 0.6s | push slide 0.3s | hard cut | etc>

## One-line synopsis
<A single sentence. If the viewer forgot everything else, what's the one thing they should remember?>

---

## Visual Identity

### Palette
| Role | Hex | Use |
|---|---|---|
| Canvas | `#______` | body bg |
| Surface | `#______` | panels |
| Foreground | `#______` | primary text |
| Accent 1 | `#______` | <what this accent is used for> |
| Accent 2 | `#______` | <what this accent is used for> |
| Accent 3 | `#______` | <what this accent is used for> |

### Typography
- **Display / headings:** <font name>, weights <500 / 700>, <tracking notes>
- **Body / secondary:** <font name>, weight <400>, minimum <20px>
- **Numbers / telemetry:** <mono font if used>, weight <500>, `font-variant-numeric: tabular-nums`
- **Captions:** <font>, <size>, <color>, <drop-shadow>

### Motion signature
- **Entrance eases:** <list 3+ eases: power3.out, expo.out, power2.out, etc>
- **Ambient loops:** `sine.inOut`, <cycle duration>s
- **Counter eases:** `power1.out` or `power2.out`, <1.5–3s> duration
- **Transitions:** <shader type or CSS transition>, <duration>s, <ease>
- **Scene entrance offset:** 0.1–0.3s (never at t=0)

---

## Media Assets

List every generated still and video clip that will appear in the composition. Delete any sub-table you don't need. All filenames are relative to the project root. Generate these BEFORE invoking the hyperframes build.

### Generated stills (T2I)
| ID | Aspect | Prompt | Used in scene |
|---|---|---|---|
| `<filename>.png` | <16:9 / 9:16 / 1:1> | `"<full prompt; end with anti-AI realism directive>"` | Scene <N> <role> |

### Reference-driven stills (I2I)
| ID | Source image | Aspect | Prompt | Used in scene |
|---|---|---|---|---|
| `<filename>.png` | `<source.jpg>` | <aspect> | `"<prompt>"` | Scene <N> <role> |

### Generated motion (T2V / I2V)
| ID | Type | Duration | Aspect | Source (for I2V) | Prompt | Used in scene |
|---|---|---|---|---|---|---|
| `<filename>.mp4` | <T2V / I2V> | <4s / 6s / 8s> | <16:9 / 9:16 / 1:1> | `<source.png or —>` | `"<prompt>"` | Scene <N> <role (ambient bg / hero / overlay)> |

**If no generated media is needed, write "None — pure SVG/CSS composition."**

---

## Music & Sound

**Approach:** <full-score / BGM-only / ambient-bed / silent-by-design>
**Justification:** <one sentence on why this choice serves the chosen style + narrative arc>

### Score brief (if commissioning music via `acestep`)

- **Genre/mood:** <e.g. "cinematic orchestral, restrained, low ambient drones">
- **BPM:** <60–180>
- **Key / scale:** <e.g. "D minor">
- **Duration:** <match measured audio duration>
- **Structural arc:**
  - 0–<t1>s: <intro — sparse, establishes tonality>
  - <t1>–<t2>s: <build — layers add gradually>
  - <t2>–<t3>s: <climax — aligned to hero scene <N>>
  - <t3>–end: <wind-down — instruments drop out; clean tail>
- **Full acestep caption:** `"<write as a music director's brief — instrument, timbre, tempo, what enters when, emotional descriptor>"`

### Mix & levels

- **VO level:** -3 to -6 dB peak (primary channel)
- **Music level under VO:** -18 to -24 dB (ducked)
- **Music level in VO gaps:** -12 to -15 dB (breathe)
- **Tail trim:** <seconds> of natural decay at the end; no hard cut

### Silence decisions
- <e.g. "Scene 5 hero moment: BGM drops out for 2s at closest-approach marker; VO + ambient starfield hum only">

---

## Scene Breakdown

Total scenes: <N>. Total runtime: <seconds>s (matches measured audio duration after TTS).

### Scene 1 — <Title Card / Intro / etc> · <start>–<end>s

**Archetype:** <Title Card | Launch/Intro | Data Reveal | Hero Moment | Return | Contrast | Outro>

**Heading:** `<exact text>`
**Body:** `<exact text>`
**Data / decoratives:**
- <concrete element: "stat card showing X", "SVG rocket", "live counter from A to B">
- <another element>

**Media references (if any):**
- Background image: `<filename>.png` (T2I) with dark overlay `linear-gradient(rgba(5,7,13,0.55), rgba(5,7,13,0.75))` for text contrast
- Ambient video: `<filename>.mp4` (T2V, muted playsinline loop) z-index 1

**Music cue for this scene (if scored):**
- <e.g. "enters at 0:10 with low cello drone; builds by +6 dB through the scene">

**Motion beats:**
1. <t=0.1s> — Anchor element scales in, 0.9→1.0, `power3.out`, 1.0s
2. <t=0.3s> — Heading slams up from y:60, `expo.out`, 0.8s
3. <t=0.5s> — Body fades + slides, `power3.out`, 0.6s
4. <t=1.2s> — Stat counter begins rolling, `power2.out`, 2.5s

**Narration (if voiced):**
> <exact words of narration for this scene, 15–25 words>

**Anti-patterns reminder:**
- Every element must use `gsap.from()` — no element appears fully-formed
- No exit animations on this scene (transition handles the exit)

---

### Scene 2 — …

<repeat pattern>

---

### Scene N — Outro · <start>–<end>s

**Archetype:** Outro / CTA

<…>

**Motion beats:**
- Fade-to-canvas at scene end, 1.0–1.2s `power2.in` — **this is the only scene where exit animations are allowed.**

---

## Technical Block

| Field | Value |
|---|---|
| Root composition `data-duration` | <measured audio duration, e.g. 77.52> |
| Audio file | `narration.wav` |
| Transcript source | `transcript.json` (verbose_json from Groq Whisper-Large-V3) |
| Caption groups | `captions.json` (3–5 words per group, 30–50 groups) |
| Starfield / ambient layer | <yes/no, duration, seed> |
| Transition type | <shader / CSS crossfade / hard cut> |
| Render quality | standard (default) | high (final delivery) |
| Render FPS | 30 |

### Audio pipeline
1. Run `local_api tts/tts` with the combined narration script; save as `narration.wav`.
2. `ffprobe` the actual duration; update root `data-duration` to match.
3. Fetch Groq key via `local_api credentials/load_credentials {"providerName":"groq"}`.
4. POST to `https://api.groq.com/openai/v1/audio/transcriptions` with `model=whisper-large-v3`, `response_format=verbose_json`, `timestamp_granularities[]=word`.
5. Group `words[]` into caption groups (3–5 words, break on `. ? !` or 0.3s+ pauses).
6. Feed to HyperFrames captions sub-composition.

---

## What NOT to Do

Include at minimum 5 bullets, including the mandatory ones below.

### Mandatory (every voiced multi-scene video)
- **Every sub-composition must include a no-op hold tween** `tl.to({}, { duration: SCENE_DURATION }, 0)` before `window.__timelines[id] = tl`. Without it the runtime hides the scene once the last real tween ends. (HYP-1)
- **Do not call `local_api transcribe/transcribe_audio_video` from this agent context** — it silently returns empty. Use the direct Groq path described in the Audio pipeline. (STT-1)
- **Do not read `credentials|<provider>.json` directly for API keys** — the stored string is encrypted. Use `credentials/load_credentials`. (STT-2)
- **Never `repeat: -1`** on any tween — calculate exact repeat counts from composition duration.
- **Only the final scene may use exit animations** — all intermediate scenes rely on the transition to handle their exit.

### Style-specific (derived from chosen preset's anti-patterns)
- <copy the 5 anti-patterns from the chosen style preset verbatim>

### H.264 hygiene (dark-canvas styles only)
- **No full-screen linear gradients on dark backgrounds** — use radial gradients, solid fills with localised glow, or seeded noise overlays (4–8% opacity). H.264 bands visibly on smooth dark ramps. (GRAD-1)

---

## Handoff to HyperFrames

Once approved, load the `hyperframes` skill with this spec and say:

> *Build the video described in `<session_dir>/<project-slug>-spec.md`. The spec is self-contained — palette, fonts, scene breakdown, narration, and anti-patterns are all inline. Follow the spec's 'What NOT to Do' section strictly.*

HyperFrames will:
1. `hyperframes init <project-slug>` to scaffold the project.
2. Write DESIGN.md from the spec's Visual Identity section.
3. Run the Audio pipeline exactly as specified.
4. Author one sub-composition per scene, each with its mandatory hold tween.
5. Wire the root index.html with the declared transition type.
6. `hyperframes lint && hyperframes validate`, fix any warnings.
7. `hyperframes render --quality standard --fps 30 --output <project-slug>.mp4`.

```
