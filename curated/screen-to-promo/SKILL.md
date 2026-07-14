---
name: screen-to-promo
description: >
  Turn screen recordings into polished videos — marketing promos, user guides, product demos,
  and more. Goal-aware pipeline: detects user intent, selects strategy, recommends a plan,
  then executes. Full pipeline: intent detection → strategy selection → source analysis →
  storyboard planning → source prep → VO generation → frame-by-frame compositing →
  audio mixing → final encode. Supports animated presenters (AI animal/character with rembg cutout),
  per-word caption sync (pop, karaoke, static styles), multi-zoom animations, overlay dissolve
  transitions, time-mapped VO-to-source sync, CJK-aware captions, letterbox-aware cropping,
  and keypress + shortcut animation overlays with frame-aligned tick/tock SFX (canonical pattern
  for product demos that show hotkeys; ships proven SFX library at assets/sfx/).
  Use when: (1) user has screen recordings and wants a polished video — marketing, tutorial,
  demo, or changelog, (2) user says "make a promo video", "tutorial from this recording",
  "TikTok video", "marketing video", "user guide", "highlight reel", (3) user provides
  .mov/.mp4 screen recordings to turn into any kind of video with narration and captions.
---

# Screen-to-Promo

Transform screen recordings into polished, goal-driven videos — from viral marketing promos to step-by-step user guides.

## Intent & Strategy

Before production, determine the video's purpose. Different goals demand different strategies.

### Intent Detection

Detect intent from the user's words + source material:

| Signal | Likely Intent |
|--------|--------------|
| "promo", "marketing", "viral", "TikTok", "Reels" | Viral Marketing |
| "tutorial", "guide", "how to", "walkthrough", "show how" | User Guide |
| "demo", "showcase", "feature demo", "sales" | Product Demo |
| "changelog", "what's new", "release notes" | Changelog Montage |
| "bug report", "repro steps", "issue" | Bug Report |
| Ambiguous or no clear signal | Ask or recommend |

### Strategy Differences

| Dimension | Viral Marketing | User Guide | Product Demo |
|-----------|----------------|------------|-------------|
| **Goal** | Make user WANT to try it | Teach user HOW to do it | Show features to convince |
| **Hook** | Must hook in 0-3s | None needed | Brief value prop |
| **Duration** | 30-90s (SNS-fit) | As long as needed (3-15min) | 1-3 minutes |
| **Pacing** | Fast cuts, dramatic pauses | Slow, methodical, follow cursor | Medium, feature-by-feature |
| **Source usage** | 20-30%, reordered for drama | 80-90%, in order | 50-70%, highlight features |
| **Narrative** | Pain → Solution → Magic → Payoff | Step 1 → Step 2 → ... → Done | Problem → Feature → Benefit |
| **Zoom strategy** | 3-4 dramatic reveals, quick peek + payoff | Many — every step gets a zoom, stay zoomed | Feature-focused, moderate frequency |
| **Zoom frequency** | Few, each earns its moment | High, readability-driven | Medium, one per feature |
| **Captions** | Bold pop/karaoke, word-by-word | Step labels, numbered, persistent | Clean, informative |
| **Trimming** | Ruthless — only "wow" moments | Keep everything, skip only dead time | Cut transitions, keep features |
| **VO style** | Dramatic, emotional, multi-voice | Calm, instructional, single narrator | Confident, persuasive |
| **CTA** | "Link in bio" / hard CTA | "Now try it yourself" | "Get started at..." |
| **End card** | Logo + tagline + social | Summary of steps | Logo + pricing/link |
| **Music** | Dramatic bed / upbeat | None or subtle | Subtle background |

## Compositing Engines

Two engines work together — each owns a different part of the video.

### HyperFrames (title cards + animated overlays)

HTML/CSS/JS composition engine. Used for THREE things in this skill:

1. **Hook card** — opening title with VO, light leaks, spring animations.
2. **CTA card** — closing logo + tagline + keypress chord animation (see CTA card pattern below).
3. **Keypress / shortcut overlays** — floating `<kbd>` key caps with GSAP staggered entrance, rendered to a transparent-background MP4 (ProRes 4444 with alpha) and overlaid onto the screen recording via ffmpeg. See **Keypress Animation & SFX** section.

HyperFrames gives you GSAP timing, CSS keyframes, alpha output, system fonts, and proper motion design — things ffmpeg drawtext + raw frame compositing simply cannot match for animated UI elements.

- Install per-project (node_modules don't copy cleanly between dirs):
  ```bash
  cd <project-dir> && npm init -y && npm install hyperframes
  ./node_modules/.bin/hyperframes lint .
  ./node_modules/.bin/hyperframes render .
  ```
- `npx hyperframes` alone doesn't work — npm treats it as unknown. Use the local binary.
- Skill references: `~/.agents/skills/hyperframes` (composition authoring), `~/.agents/skills/hyperframes-cli` (CLI commands), `~/.agents/skills/gsap` (animation reference), `~/.agents/skills/hyperframes-design` (first-draft scaffolding).

### ffmpeg + compose.py (middle content — screen recording)

Shell + Python frame-by-frame compositing. Used by `scripts/compose.py` for zooms, captions, transitions, multi-segment screen-recording sequences. NOT used for animated overlays — those go through HyperFrames.

**Canonical pipeline:** HyperFrames hook.mp4 + compose.py middle.mp4 (with HyperFrames keypress overlays composited on top) + HyperFrames cta.mp4 → concat.

## Design Language — Apple Keynote Style

Default aesthetic for all promo videos. Do NOT deviate without explicit user request.

### Colors
- Background: Pure black (#0a0a0a)
- Text: White only — NO colored accents (no yellow, blue, purple, red)
- Light leaks: Warm amber (hue ~25), MAX 8% opacity, `mixBlendMode: "screen"`
- Text glow: Pure white only, very subtle (opacity 0.15 max)

### Captions (over screen recordings)
- NO backdrop box/pill — text floats freely with multi-layer drop shadow
- Shadow: `0 2px 4px rgba(0,0,0,0.7), 0 4px 20px rgba(0,0,0,0.5), 0 8px 40px rgba(0,0,0,0.3)`
- Active word: pure white, bold (800), scale 1.15
- Past words: white at 90%, Future words: white at 45%
- Font: SF Pro Display, 44-46px

### Typography hierarchy
- Subheads: weight 300, uppercase, letter-spacing 0.08em, white at 70%
- Hero text: weight 700, normal case, letter-spacing -0.02em, pure white
- Brand: weight 500, uppercase, letter-spacing 0.3em, white at 60%

### SFX Timing Rules
- **Dings** fire at word START time (not end time)
- **Captions** need +250ms visual lead over audio
- **Page-turn** SFX for transitions between narrative phases
- **Ding** SFX for achievements ("Bot created.", "Token secured.", etc.)
- Hook/payoff text MUST match VO content exactly (audio-visual coherency)

### Interaction Flow

The skill uses a **survey → understanding → plan → implement** flow with TWO explicit confirmation gates before ANY production render. Both gates are mandatory — they apply even in delegate mode.

**Step A — Full survey (always).** Before proposing anything, review the WHOLE recording end to end — sample frames across the entire duration, not just the obvious beats. Explicitly hunt for distinctive product features the user is likely proud of: a unique gesture, a custom tool, an unusual interaction, an "aha" moment — not just the happy-path task. A feature that flashes by for 5 seconds can be the single most important shot in the promo.

**Step B — Present your understanding.** Report back, beat by beat, what you believe the recording shows and what each moment demonstrates. Name the features by name. This is where the user catches anything you misread or under-weighted.

**Gate 1 — Confirm the understanding.** Ask for comments and iterate on the beat-by-beat read until the user explicitly confirms your understanding is correct. Do NOT move on to planning until the read is confirmed.

**Step C — Present the production plan.** Once the understanding is locked, lay out the concrete plan so the user can see exactly what will be built: mode + duration, the narrative arc, the per-beat script / VO lines, which source moments become which shots, zoom targets, caption style, hook + CTA, and music/SFX. Keep it scannable.

**Gate 2 — Confirm the plan, then implement.** Iterate on the plan until the user explicitly approves it. Only AFTER plan approval do you run the real generation job (extract frames, generate VO, render, mix). Do NOT render the full promo before the plan is approved.

Interaction modes still shape HOW you present, but none skip either gate:
1. **User knows what they want** — "make a TikTok viral promo" → survey, confirm understanding, present + confirm plan, run
2. **User needs guidance** — "make a video from this" → survey, confirm understanding, recommend + confirm plan, run
3. **User delegates** — "your call" / "do your best" → survey, confirm understanding, present plan for a quick thumbs-up, run once approved

**Rules:**
- **Survey the entire timeline first** — missing a distinctive feature beat is the most expensive mistake; it forces a full re-render.
- **Two gates, in order** — confirm the *understanding* before you write the plan; confirm the *plan* before you render. Never collapse them into one "go."
- **Both gates are cheap; a wrong 40s render is not** — a misread caught at Gate 1 or a wrong arc caught at Gate 2 saves a full re-render.
- **Prefer validating over interrogating** — 1-2 crisp questions max per gate; the loops are about checking your read and your plan, not a questionnaire.

**Recommendation format:**
```
Based on your 5-minute screen recording of [product], I recommend:

- Mode: Viral marketing promo (60-90s)
- Strategy: Pain → Solution → Magic → Payoff arc
- Hook: "[pain point opening line]"
- Zooms: 3 focused moments — [setup], [creation], [result]
- Captions: Bold pop, word-by-word
- CTA: Product name + tagline end card

Going with this — let me know if you want to adjust anything.
```

## Pipeline Overview

### Phase 0: Intent, Survey & Two Confirmation Gates
1. **Detect intent** from user's words + source material
2. **Full-timeline survey** — sample frames across the ENTIRE recording; identify every beat AND every distinctive product feature (unique tools, gestures, "aha" interactions), not just the main task
3. **Present understanding + Gate 1** — report the beat-by-beat read (features named); iterate until the user confirms the understanding is correct. Do not plan until confirmed.
4. **Select strategy + present production plan** (viral_marketing | user_guide | product_demo | changelog | custom) — mode, duration, narrative, per-beat script/VO, zoom targets, caption style, hook/CTA, music/SFX
5. **Gate 2 (mandatory)** — iterate on the plan until the user approves it, then start the real generation job. Never extract frames, generate VO, or render the full promo before plan approval.

### Phase 1: Analysis & Planning
5. **Source Analysis** — probe resolution/duration/fps/audio, extract key frames every 10s, identify UI regions (app windows, sidebars, chat areas), detect artifacts (recording bars, idle cursor, blank screens, notification popups)
6. **Context & Audience** — research product/brand, community terminology, target platform constraints, language/localization needs (CJK font requirements, caption style choice)
7. **Storyboard & Planning** — map VO lines to source timestamps, pre-calculate zoom targets from actual key frame pixel coordinates (never guess cx/cy), build zoom table, flag problems (time jumps needing smooth_jumps, missing fonts, duration vs platform limits)

### Phase 2: Production
8. **Prep sources** → `scripts/prep_source.sh` (any resolution → 1920×1080 @ 30fps)
9. **Write script** → style driven by strategy (dramatic for marketing, instructional for guides)
10. **Generate VO** → **ALWAYS use Enconvo's active TTS provider — no fallback, no exceptions.** Call `local_api tts/tts {input_text, audio_file_name, output_dir, speed}` (or read `~/.config/enconvo/installed_preferences/tts.json` → `selected` to confirm which provider is active). The user controls the voice/provider via Enconvo's TTS settings — respect their choice. If active TTS fails, STOP and surface the error to the user; do NOT silently fall through to Voicebox / Edge-TTS / Kokoro / any other engine. Get word timestamps via Groq Whisper after generation.
11. **Optional: AI presenter** → nanobanana image → Veo I2V → extract frames → rembg cutout
12. **Build config** → JSON config for compositor (segments, zooms, transitions, captions)
13. **Compose frames** → `python3 scripts/compose.py --config config.json --output final.mp4`
14. **Mix audio** → `scripts/audio_mix.sh output.m4a -25 audio1.wav gap audio2.wav ...`
15. **Encode** → ffmpeg h264 with `setsar=1` (or use `--output final.mp4` in compose.py)

## Quick Start

```bash
SKILL_DIR="$HOME/.claude/skills/screen-to-promo"

# 1. Prep screen recording
bash "$SKILL_DIR/scripts/prep_source.sh" ~/Desktop/demo.mov ./frames/demo/ 30

# 2. Build config.json (see compose.py docstring for schema)

# 3a. Compose frames only
python3 "$SKILL_DIR/scripts/compose.py" --config config.json --output-frames ./frames/output/

# 3b. Or compose + encode in one step
python3 "$SKILL_DIR/scripts/compose.py" --config config.json --output final.mp4 --audio mixed.m4a

# 4. Mix audio (if not using --output)
bash "$SKILL_DIR/scripts/audio_mix.sh" final_audio.m4a -25 hook.wav gap demo_vo.wav

# 5. Encode manually (if not using --output)
ffmpeg -y -r 30 -i ./frames/output/f_%04d.jpg -i final_audio.m4a \
  -c:v libx264 -preset fast -crf 23 -pix_fmt yuv420p -vf "setsar=1" \
  -c:a copy -map 0:v -map 1:a final.mp4

# Validate config without composing
python3 "$SKILL_DIR/scripts/compose.py" --config config.json --output-frames /dev/null --validate-only
```

## Config Features

### Multi-Zoom (`zooms` array)

Segments can use a `zooms` array for multiple zoom regions. The compositor picks the first active zoom at each timestamp.

```json
{
  "type": "screenrec",
  "zooms": [
    {"cx": 960, "cy_start": 300, "cy_end": 300, "scale": 2.0, "in_start": 2.0, "in_end": 3.5, "hold_end": 12.0, "out_end": 13.5},
    {"cx": 1200, "cy_start": 500, "cy_end": 600, "scale": 2.2, "in_start": 18.0, "in_end": 19.5, "hold_end": 28.0, "out_end": 29.5}
  ]
}
```

Both `zoom` (single dict) and `zooms` (array) are supported.

### Caption Styles

- **`pop`** — word-by-word with scale bounce + accent underline swipe. Good for English, high-energy marketing.
- **`karaoke`** — full phrase visible, active word highlighted with accent color + pop bounce. CJK-aware (no spaces between characters). Good for Chinese/Japanese/Korean.
- **`static`** — simple static text display.

### Caption Options

| Option | Type | Default | Notes |
|--------|------|---------|-------|
| `font` | string | system default | Path to TTF/TTC. CJK requires Arial Unicode or similar |
| `font_size` | int | 52 | Base size in px. 96 for large bold impact |
| `no_outline` | bool | false | Removes 3px stroke outline for clean solid text |
| `color` | [R,G,B] | [255,255,255] | Main text color |
| `accent_color` | [R,G,B] | [255,200,50] | Active word highlight + underline color |
| `outline_color` | [R,G,B] | [0,0,0] | Stroke color (ignored when no_outline is true) |
| `position_y` | int | -130 | Offset from frame bottom (negative = up from bottom) |

### Font Recommendations

- **English bold**: `/System/Library/Fonts/Supplemental/Arial Bold.ttf`
- **CJK (Chinese/Japanese)**: `/Library/Fonts/Arial Unicode.ttf` — REQUIRED, default fonts show boxes
- **Fallback**: system Helvetica (macOS), DejaVu Sans Bold (Linux)

## Key Rules

- **AR lock**: always `ch = cw * H / W` in zoom math. One slip = visible squish.
- **Letterboxed sources**: crop content FIRST, re-center, then zoom.
- **Audio**: never loudnorm original Veo audio (`SKIP_FIRST_NORM=1`). Use concat not amix. 0.5s gaps.
- **Transitions**: overlay_dissolve with rembg cutout for presenter→screenrec.
- **Captions / SRT timestamps**: word-level timestamps come from Groq Whisper (Large V3 or Turbo). **The Enconvo `transcribe/transcribe_audio_video` wrapper returns plain text only** — even when the active provider is Groq Whisper via the Enconvo Cloud relay, timestamps are stripped. To get real SRT/word timestamps you MUST call Groq's API directly with `response_format=verbose_json` + `timestamp_granularities[]=word,segment`, which requires a real `gsk_...` key in Enconvo's credential manager. See **ASR & Timestamps Setup** section below for the exact steps to walk a user through getting a free Groq key and validating it. Choose caption style based on language and strategy.
- **Script writing**: style matches strategy — dramatic for marketing, instructional for guides.
- **UI jumps**: add source timestamps to `smooth_jumps` list — compositor auto cross-fades 0.5s.
- **Frame numbering**: all frames are 1-indexed (`f_0001.jpg`, `f_0002.jpg`, ...).
- **Zoom easing**: cosine ease-in-out on both zoom in and zoom out.
- **Zoom accuracy**: never guess cx/cy — extract actual frames and measure pixel coordinates.
- **ALWAYS use HyperFrames for hook/CTA**: never fall back to plain ffmpeg drawtext for title cards. HyperFrames gives spring animations, light leaks, and proper motion design. ffmpeg drawtext produces static, lifeless cards.
- **ALWAYS read the Design Language section first**: before ANY visual compositing, check the aesthetic rules in this file. Do NOT default to colored text, navy backgrounds, or any non-approved palette.
- **CJK font on macOS**: `/System/Library/Fonts/PingFang.ttc` does NOT work in ffmpeg drawtext. Use the full AssetsV2 path from `fc-list | grep PingFang`. Or better — use HyperFrames which handles system fonts natively.
- **Concat codec matching**: when concatenating segments with ffmpeg `-f concat`, ALL segments MUST have identical codec params (fps, sample rate, channels, pixel format). Re-encode all to matching params BEFORE concat, or use full re-encode concat. Mismatched params cause DTS warnings and audio dropout.
- **Voicebox output path**: voicebox `--output` flag appends `.wav` to the filename — if you pass `seg.wav`, you get `seg.wav.wav`. Account for this double extension.
- **Silent video analysis**: DEFAULT — use the host LLM (Claude) to analyze extracted frames directly (ffmpeg extract keyframes → read images → describe scenes). FALLBACK — use `video_captioner.py` (MLX VLM, Qwen2.5-VL-3B) from video-processor skill when the host LLM is unavailable or the pipeline must run unattended. The host LLM produces significantly better scene descriptions than the local 3B model.
- **Cross-skill pipeline**: video-processor (analysis/fallback) → screen-to-promo (production) is a valid workflow. Use host LLM for scene analysis by default, video_captioner.py as offline fallback, transcriber for videos with speech.

## ASR & Timestamps Setup (Groq BYOK — required for SRT sync)

Word/segment timestamps are required for: sync-locked dubbing, karaoke captions, pop captions with per-word highlighting, click-moment alignment, time-stretch fitting per cue.

### Why Groq BYOK (and not the Enconvo Cloud Whisper)

Enconvo ships **two** Groq Whisper choices in Settings → Transcription Models:

| Provider entry | API key needed | Returns timestamps via Enconvo wrapper? |
|---|---|---|
| **Groq (Enconvo Cloud)** — `transcribe|groq-enconvo` | No — uses Enconvo Cloud Plan | ❌ Plain text only |
| **Groq** (BYOK) — `transcribe|groq` | Yes — your own `gsk_...` key | ❌ Plain text via wrapper, but ✅ FULL `verbose_json` when called directly |

The wrapper strips timestamps from every provider regardless of model. The BYOK path lets the agent skip the wrapper and hit `https://api.groq.com/openai/v1/audio/transcriptions` directly with `response_format=verbose_json`, which is the only way to get SRT/word-level data.

### Walk the user through this once (then it works forever)

When you (the agent) detect that the user wants SRT-synced dubbing, word-level captions, or karaoke, and you call `local_api credentials/load_credentials {"providerName": "groq"}` and find no `apiKey`, give them this exact set of steps:

```
For sync-locked dubbing / word-level captions, I need a Groq API key — it's free and 30 seconds:

  1. Get a free key: https://console.groq.com/keys
     (sign in with Google/GitHub → "Create API Key" → copy the gsk_... string)

  2. Open Enconvo Settings → Transcription Models
     Scroll down to "Whisper Large V3" or "Whisper Large V3 Turbo"
     (the one labelled just "Groq" — NOT "Groq (Enconvo Cloud)")

  3. Click the gear / Settings icon next to that entry

  4. Click the pen / edit icon on the API Key field

  5. Paste the gsk_... key, then click Validate

  6. Set this entry as your default ASR provider

Once validated, tell me "done" and I'll re-run transcription with full SRT timestamps.
```

### How to verify before transcribing

```python
# 1. Confirm the active provider is the BYOK Groq (not the Enconvo Cloud one)
local_api("transcribe/get_default_stt_provider", {})
# → look for commandName == "groq" (BYOK).  "groq-enconvo" is the Cloud wrapper and won't give timestamps.

# 2. Pull the real key out of the credential manager
local_api("credentials/load_credentials", {"providerName": "groq"})
# → response.apiKey should start with "gsk_"
```

### How to call Groq directly for verbose_json

```bash
curl -s -X POST "https://api.groq.com/openai/v1/audio/transcriptions" \
  -H "Authorization: Bearer $GROQ_API_KEY" \
  -F "file=@source_audio.wav" \
  -F "model=whisper-large-v3" \
  -F "response_format=verbose_json" \
  -F "timestamp_granularities[]=word" \
  -F "timestamp_granularities[]=segment" \
  -o transcript.json
```

Resulting JSON gives you `language`, `duration`, `segments[]` (with `start`/`end`/`text`), and `words[]` (with `word`/`start`/`end`). Trivial to render to SRT and to map per-cue TTS clips into their slots.

### Fallback ladder if Groq BYOK isn't available

If the user refuses to set up a key, walk down in this order:

1. **whisper-mlx (local, free, offline)** — installed for the Enconvo MLX stack. Native SRT + word timestamps, ~25 sec for a 90-sec clip on Apple Silicon. Great zh/en handling.
2. **AssemblyAI BYOK** — solid SRT + word timestamps if they already have a key.
3. **ElevenLabs Scribe BYOK** — accurate word timestamps.
4. **Inferred timing** — if nothing else works, evenly distribute words across the segment duration (acceptable for non-karaoke pop captions only; do NOT use for sync-locked dubbing).

Never silently fall back without telling the user — name the provider you're using and why before you transcribe.

## Detailed Reference

For full pipeline walkthrough, planning protocol, zoom playbook, strategy playbooks, caption reference, and all rules: read `references/pipeline.md`.

## Dependencies

- Python 3: PIL/Pillow, numpy, rembg (for presenter cutout)
- ffmpeg/ffprobe
- Groq API (Whisper word timestamps — REQUIRED for SRT-synced dubbing / word-level captions; the Enconvo transcribe wrapper does NOT return timestamps. See ASR & Timestamps Setup below.)
- VO: **Enconvo active TTS only** (call `local_api tts/tts`; respects whatever provider/voice the user has selected in Enconvo's TTS settings). No fallback to voicebox/edge-tts/kokoro — if it fails, surface the error.
- Optional: nanobanana skill (presenter image), veo skill (I2V), acestep (BGM)

## Keypress Animation & SFX (for product demo videos)

Product demos almost always show shortcuts and hotkeys. This is what separates a screen recording from a polished promo: the viewer SEES the key animation AND HEARS the click. Without SFX, a key-press overlay is just a floating graphic — with SFX, it feels like the user is sitting at the keyboard.

This section is the canonical pattern for any video that demos shortcuts (Enconvo, Raycast, Cursor, any app with a power-user surface).

### When to add keypress SFX

- Every visible shortcut press — modifier chord OR single key.
- Every overlay reveal triggered by a hotkey (command bar, menu unfurl, palette open).
- Every "action fires" moment where the user expects feedback (e.g. translate runs, AI summarizes).

Do NOT add SFX for: ambient typing in a text field (would be machine-gun noise), cursor clicks (that's a different SFX category), passive UI states.

### The two-layer rule (tick + tock)

A single sound never feels like a real key. Always layer two:

| Layer | File | Volume | Delay | Role |
|-------|------|--------|-------|------|
| Strike | `tick.wav` | 0.85 | 0ms | Finger contact / key onset |
| Bottom | `tock.wav` | 0.95 | +100–150ms | Key bottom-out / action fires |

For multi-key chords (`⌘⇧D`, `⌥Space`), stack ticks for each modifier with 80–180ms spacing, then ONE tock for the triggering letter at the action moment. See `assets/sfx/README.md` for the full recipe and ffmpeg commands.

### Cue-timing discipline (the v7→v9 lesson)

**SFX must land on the FRAME the on-screen animation reveals, not the moment the user's finger hit the key off-camera.** A 1-second misalignment between SFX and animation is the most immediately audible sync bug in screen-recording videos.

The verification loop that worked:

```bash
# 1. Sample frames every 0.2-0.3s around the suspected cue point
for t in 36.5 37.0 37.3 37.5 37.7 38.0 38.3; do
  ffmpeg -y -ss $t -i source.mp4 -frames:v 1 frame_${t}.png
done

# 2. Read each frame with the host LLM, identify the EXACT frame
#    where the reveal starts (command bar emerging, menu unfurling).
# 3. Lock the tick to that timestamp. Tock 100-150ms after.
# 4. After mixing, verify with volumedetect that the cue actually peaks:
ffmpeg -y -ss 37.0 -t 0.4 -i out.mp4 -af "volumedetect" -f null - 2>&1 | grep max_volume
# Healthy peak: -6 to -10 dB.
```

If the user reports "the sound is 1s early/late," you have two options:

1. **Move the SFX cue** (cheap, fast — just adjust `adelay`). Always preferred.
2. **Re-render the keypress animation overlay at a different timestamp** (expensive — requires re-compositing the overlay onto the screen recording from upstream sources).

Before offering option 2, check whether the keypress animation is baked into the source you have (it usually is, by the time you're mixing audio). If so, tell the user that shifting the SFX is equivalent and ship that.

### Animation overlay patterns

For the visual side of the keypress, use HyperFrames composited as an overlay layer onto the screen recording:

- **Floating key caps** — render `⌘`, `⇧`, `D` as styled `<kbd>` divs on a transparent canvas, animate them with GSAP (scale 0.9 → 1.0, opacity 0 → 1, ~150ms each, staggered), hold for ~600ms, fade out 300ms.
- **Position**: bottom-center or bottom-right, 80–120px from the edge. Never cover the active UI.
- **Style**: dark-glass key caps (`background: rgba(20,20,20,0.9)`, `border: 1px solid rgba(255,255,255,0.15)`, `border-radius: 10px`, `box-shadow: 0 8px 24px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.1)`). White glyphs, SF Pro Display 600.
- **Sync rule**: the modifier keys appear FIRST (ticks fire), then the letter highlights/animates (final tick), then the action fires on screen (tock fires). This mirrors the natural rhythm of a chord.

Render as a separate transparent-background MP4 with alpha (`-c:v prores_ks -profile:v 4444 -pix_fmt yuva444p10le`), then overlay onto the screen recording with ffmpeg `-filter_complex "[0:v][1:v]overlay=..."`.

### Enconvo-specific: the `⌘⇧D` story

For any Enconvo-branded promo, **the `⌘⇧D` shortcut is the hero gesture** — it's the single keystroke that opens Enconvo from anywhere on the system, and the most important muscle-memory we want viewers to walk away with.

When producing Enconvo videos:

- **Show `⌘⇧D` at least twice** — once in the hook ("smarter macOS, one shortcut away"), once in the CTA outro (the closing key animation that fades into the logo).
- **Always pair the visual with audible tick+tick+tick+tock** so the chord feels physical.
- **Voiceover should name it** — the CTA VO `"Enconvo. Smarter macOS, one shortcut away."` works specifically because the on-screen `⌘⇧D` animation fires while "one shortcut" is spoken. Audio + visual + meaning land on the same beat.
- **In tutorials/guides**, the FIRST time `⌘⇧D` appears, hold the key animation on screen for 1.5–2s (longer than normal) and let the SFX breathe. Subsequent appearances can be quicker. Repetition with rhythm is how a shortcut becomes muscle memory for the viewer.

This is a brand commitment — every Enconvo promo should reinforce `⌘⇧D` as THE entry point. Other shortcuts get standard treatment; `⌘⇧D` gets the hero treatment.

### Reusable SFX library

The skill ships three production-tested files at `assets/sfx/` (validated across the Enconvo dub v7→v9 pipeline):

- `tick.wav` — 44.1k mono, 0.08s — sharp key-strike attack
- `tock.wav` — 44.1k mono, 0.18s — deeper bottom-out resonance
- `whoosh.wav` — 48k mono, 0.6s — motion sweep for transitions / logo reveals

Use them directly — do NOT regenerate per-project. Consistent SFX across videos becomes part of the brand audio identity.

## Lessons Learned (Hard-Won — from real production runs)

Capture discoveries that cost hours the first time. Check this list BEFORE starting any iteration loop.

### Content Survey & Feature Coverage

- **Survey the WHOLE recording before scripting — distinctive features hide in short moments**: On a Coupa-Cafe app-design promo, the first cut missed the single coolest beat — the user opened Enconvo's **Doodle** tool and hand-drew red swap arrows directly on the design ("move avatar and greeting to opposite sides"), and Enconvo read the sketch and applied it. It flashed by in ~10s of a 23-min recording, so a happy-path skim treated the final screen as just "the finished app" instead of "the result of a hand-drawn instruction." Cost: a full re-render (new beat frames + 2 new VO lines + re-timed audio). Lesson: sample frames across the ENTIRE timeline and explicitly ask "what unusual/branded interactions happen here?" — a unique gesture or custom tool is usually the most sellable shot, not the polished end state.
- **Turn a feature beat into a before→after pair when possible**: the Doodle beat became far stronger by showing the doodle (avatar on the right + red swap arrows) immediately followed by the payoff (avatar swapped to the left), with VO "It reads your sketch, and ships it — exactly as drawn." A feature shown *causing a visible change* beats a feature shown in isolation.
- **Present your beat-by-beat understanding and get confirmation BEFORE the real render** (see Phase 0 gate). The Doodle miss would have been caught in one sentence of user feedback if the read had been shown first. The confirm gate is cheap; a wrong 40s render is not.

### Script Authoring & Timing

- **Writers block gate**: do NOT start TTS generation until the full script, zoom plan, and segment durations are approved by the user. TTS burns time + credits. User-visible feedback loops (show the plan, get "go") are cheaper than regenerating audio.
- **Reuse VO across iterations**: if only zoom timing / frames / cuts change, keep old VO WAVs — don't regenerate. Only regenerate the specific segment whose TEXT changed.
- **Delay pattern for late-landing words**: when a specific word (e.g. "Approve", "ALIVE") must sync to a specific video frame, compute delay = `target_seg_time - raw_word_start_in_wav`, then apply via `ffmpeg -af "adelay=Nms|Nms,apad=pad_dur=D,atrim=0:D,asetpts=PTS-STARTPTS"`. Also shift the word-timings JSON by the same delay so captions stay synced.
- **Word timing estimation fallback**: if Groq Whisper API key isn't available, evenly distribute words across `(duration - start_pad - end_pad)`. This is "good enough" for pop captions — perfect sync is not required for non-karaoke styles.

### VO Providers

- **TTS rule — Enconvo active TTS ONLY, no fallback**: ALWAYS generate VO via `local_api tts/tts` (or the `tts--tts` tool). This routes through whatever provider the user has set as Enconvo's active TTS in Settings → Text-to-Speech. To confirm which provider is currently active, read `~/.config/enconvo/installed_preferences/tts.json` → `selected` field (e.g. `tts|enconvo_xai`, `tts|enconvo_gemini`, `tts|mlx_kokoro`, etc.) and tell the user which one will be used before generating. NEVER silently fall through to Voicebox, Edge-TTS, Kokoro, or any other engine — that hijacks the user's chosen voice. If active TTS errors, STOP and ask the user to either fix their config or explicitly approve a different engine.
- **Voice switch workflow**: the user can change Enconvo's active TTS provider/voice between calls. To re-record with a new voice, they switch the provider in Enconvo settings, then you call `tts/tts` again with the same text — the new active voice is picked up automatically. Always re-read `tts.json` → `selected` before each major regenerate so you can name the provider in your reply.
- **Credentials are in Enconvo's credential manager — use the API, not the raw JSON file**. For Groq (Whisper word timestamps) and any other provider, call `local_api credentials/load_credentials {"providerName": "groq"}`. The returned `apiKey` is the real, usable key. Do NOT `cat ~/.config/enconvo/installed_preferences/credentials|groq.json` directly — that file stores an encrypted/hashed placeholder (128-char hex), not the working `gsk_...` key. Same pattern for `openai`, `elevenlabs`, `anthropic`, etc.
- **Gemini TTS phonetic quirks** (when user has Gemini selected): `ANN` capitalized is read as "A-N-N" spelled out. Use the full phrase `Ann the Uncensored` for natural pronunciation. `I M Channels` (space-separated) reads cleaner than `IM Channels`. Apply similar phonetic-spell tricks for whichever provider the user has active.
- **Gemini TTS caches by output filename — ALWAYS bump the filename on re-record**. If you call `tts/tts` with `audio_file_name: cue01.wav` once, then call it again with the SAME filename but DIFFERENT `input_text`, Gemini short-circuits and silently returns the original cached audio (the tool reports success and returns the same path, but the file content does not change). This silently breaks any iteration loop where the user edits a line and you regenerate. Fix: on re-record, use a versioned filename (`cue01_v2.wav`, `cue01_fresh.wav`, `cue01_${hash}.wav`), then `mv` over the original. ALWAYS verify regeneration actually happened by comparing file size or duration before vs after — if identical, the cache hit you. Even better, after rebuilding the composite dub track, run it back through Whisper to confirm the spoken content matches the new plan.
- **Preview before committing**: when user requests a voice/text change, generate to a `_new.wav` or `_v2.wav` filename FIRST, deliver preview, wait for approval, THEN swap into the master file. Never overwrite an approved VO in place.

### Zoom Accuracy & Framing

- **Subtle zoom is a zoom too**: when the frame already has all the content the viewer needs (hero layout with multiple panels), a scale of **1.05–1.10 with no cy shift** is enough to signal intentional motion without clipping anything. Don't force 1.5+ zoom when a 1.08 push-in tells the same story.
- **Zoom preserves edge elements**: before picking scale/cx/cy, enumerate ALL UI elements that must stay in the final crop. Compute the required crop window (`cw = W/scale`, `ch = cw*H/W`, `x1 = cx - cw/2`, `y1 = cy - ch/2`) and check every element's bbox fits inside. A 1.4x zoom on a full-screen layout will clip the top OR the sidebar OR the phone mockup — you can't have all three.
- **Wide-view beats zoom for "show all panels"**: if the user wants viewers to see both the Telegram chat AND the app UI AND the notes, DON'T zoom. Show the full 1920×1080 frame. Zoom is for "here is the detail that matters" moments.
- **Sync click moments by measuring, not guessing**: for any action word ("click", "approve", "start") that must match a cursor click, extract frames around the expected action time at 2fps, find the exact source-time of the click, then compute the VO delay needed to land the word there. Don't estimate from transcript position.

### Trim Surgery & Segment Preservation

- **Trim destroys downstream payoff**: if you `ffmpeg -ss X -to Y` a chunk out of the middle, you may accidentally delete the payoff moment (the reveal frame + its synced VO word). Before every trim, ask: "Does this cut remove any synced audio-visual beat?" If yes, refuse or restructure.
- **Preserve the payoff rule**: the climax moment (e.g. "Your pairing request is approved" + "ALIVE!" VO) is sacred. Never cut it. If the user wants to trim boring middle footage, trim BEFORE the approve-click or AFTER the payoff holds, not across it.
- **Clean rebuild > patch**: after 3+ iterative trims/swaps, the video's audio-visual sync degrades. It's faster and safer to rebuild from config (hook.mp4 + middle from compose.py + cta.mp4) than to keep patching a mangled MP4.
- **Verify from the user's reported timestamp**: when user says "it's broken at 42s", immediately extract frames at 0.5s intervals starting from 42s, read them with the host LLM, and confirm the problem is what you think it is. Don't re-edit blind.

### Audio Mixing with BGM

- **BGM volume sweet spot**: `volume=0.18` under a clean VO. Any louder and it fights the narration; any quieter and you can't hear it. Verify by ear on the final render.
- **BGM fade choreography**: 1.5s fade-in at video start (blooms with hook), 1.5-2s fade-out before final black. Never hard-cut BGM into or out of silence.
- **Preserve BGM when swapping only a CTA segment**: slice the matching BGM range from the original BGM file (same offset), add a local fade-out, mix with new VO, and splice back in. Don't re-mix the whole video.
- **amix filter preserves both tracks**: `[voice]volume=1.0;[music]volume=0.18;[voice][music]amix=inputs=2:duration=first:dropout_transition=0:normalize=0` — the `normalize=0` is critical; without it, adding the BGM will attenuate the voice.
- **ACE-Step for instrumental BGM**: use `~/.claude/skills/acestep` for cinematic/tech promo tracks. Good caption pattern: genre + instruments + mood + structural cues ("building tension with rising filter sweeps, triumphant major-key drop at the end"). Request `instrumental`, explicit `no vocals` if Gemini/Puck VO is on top. BPM 85–100 for narrator-driven videos. ALWAYS stop the server after generation (`pkill -f acestep-api`) — it holds ~27GB RAM.

### Brand Assets

The skill ships with Enconvo brand material at `assets/brand/` and a production-tested SFX library at `assets/sfx/`:

- `assets/brand/enconvo_icon_white.png` — pure-white Enconvo "leaf-fold" mark on transparent background, square. Use on the default #0a0a0a dark canvas.
- `assets/brand/README.md` — full usage spec (sizing, drop-shadow, wordmark pairing).
- `assets/sfx/tick.wav`, `assets/sfx/tock.wav`, `assets/sfx/whoosh.wav` — keypress + motion SFX (44.1/48k mono). See `assets/sfx/README.md` for cue patterns and ffmpeg recipes.

When the video is **Enconvo-branded** (Enconvo product demos, channel agent videos, skill showcases, or any video the user labels "for Enconvo"), the hook/CTA/outro cards SHOULD include the icon:

- **Hook**: 64–96 px icon centered above the hero title, with subtle white drop-shadow `drop-shadow(0 0 24px rgba(255,255,255,0.15))`.
- **CTA hero**: 120–160 px icon, paired with `ENCONVO` wordmark below in SF Pro Display weight 500, uppercase, letter-spacing 0.3em, white at 60%.
- **Outro watermark**: 48 px icon top-right at 60% opacity.

Do NOT tint the icon, do NOT place it on a light background, do NOT use it on third-party videos unless the user explicitly says Enconvo is the producer.

### Hook & CTA Design (HyperFrames)

#### CTA card with keypress animation (the v6 pattern)

The CTA outro that landed for Enconvo and is now the canonical pattern:

**8.5 second timeline:**

| Time | Visual | Audio |
|------|--------|-------|
| 0.00s | Card fades up on black | — |
| 0.10s | `⌘` key cap pops in (scale 0.9→1.0) | tick (vol 0.85) |
| 0.28s | `⇧` key cap pops in | tick |
| 0.46s | `D` key cap pops in | tick |
| 1.45s | All three keys flash white briefly | tock ("action fires") |
| 2.10s | Keys + subline fade out | whoosh |
| 2.50s | Logo + wordmark fade in | whoosh (softer) |
| 3.10s | VO begins (`"Enconvo. Smarter macOS, one shortcut away."`) | VO + sustained ambient |
| 7.80s | Fade to black | VO tails out |

**Wordmark proportions** (learned the hard way through v4→v6):

- Logo: 320×320 px centered
- Wordmark below: 84px (NOT 144px — too big), letter-spacing 0.18em, weight 500
- Lockup gap: 18px between logo bottom and wordmark top
- Tagline below wordmark: 36px, weight 300, white at 70%

Wordmark too big = mark looks like a label for the wordmark (wrong hierarchy). Logo must visually dominate.

#### General HyperFrames rules


- **Use HyperFrames for title cards** — install locally per-project: `cd dir && npm init -y && npm install hyperframes`, then `./node_modules/.bin/hyperframes lint/render .`. `npx hyperframes` alone doesn't work because npm treats it as an unknown command.
- **HyperFrames root composition requires `data-start="0"` AND `data-duration="N"`** on the composition div. The lint warning makes this obvious but it's easy to miss the first time.
- **Standalone compositions must NOT use `<template>`** — the sub-composition wrapper pattern only applies when loaded via `data-composition-src`. For a standalone card, put the `data-composition-id` div directly in `<body>`.
- **Node modules don't copy cleanly between project dirs**: if you `cp -r node_modules` from one hyperframes project to another, renders may fail with "Missing manifest" errors. Always fresh `npm install hyperframes` per project dir.
- **Message > brand for product CTAs**: when the video is about a specific feature ("channel agent"), the CTA should lead with the feature name as hero, not the brand. Layout: small brand wordmark on top (`ENCONVO` + the icon from `assets/brand/enconvo_icon_white.png`, ~48–64 px) → hero feature name (`CHANNEL AGENT`) → amber promise tag (`SET UP IN SECONDS`). The feature is what the viewer wants; the brand is who made it.
- **CTA VO should echo a climax word from the payoff**: if the video's emotional peak is "ALIVE!", the CTA VO should include "ALIVE" again. This creates a callback that makes the whole video feel like one argument. Avoid generic closings like "That's it" — they die on landing.

### Scene Pacing & Breathing

- **Insert a breath between content and CTA**: a 1.0–1.5s black silent pause after content fades and before CTA fades up gives the viewer a moment to absorb. Without it, the CTA feels rushed. Pattern: 0.4s video/audio fade-out → 1.2s black silent pause → 0.5s CTA fade-up (built into the HyperFrames CTA timeline already).
- **Hook needs to hold the final word**: if the hook VO ends with "Watch this.", extend the card duration so "this." lands and has 0.2s of hold time before cutting to the next segment. Cutting mid-word is jarring.

### Pipeline Efficiency

- **Keep source-frame extraction cached**: `frames_src/` costs ~2GB for a 4min source but saves 20s per recompose. Only delete once the final render is approved.
- **Compose.py handles the middle, HyperFrames handles the ends**: the canonical pipeline is HF hook.mp4 + compose.py middle.mp4 + HF cta.mp4 → concat. Don't try to render hook/CTA via compose.py's card type — it produces static, lifeless cards.
- **Reuse word-timing JSON across delay iterations**: instead of regenerating word JSON from scratch, shift existing entries by the new delta. Example pattern: `for w in d: w['start'] += delta; w['end'] += delta`. Much faster than re-transcribing.
- **Concat codec matching (restated for emphasis)**: before `ffmpeg -f concat -c copy`, re-encode ALL input clips to identical (codec, fps, sample_rate, channels, pixel_format). The safest pattern: `-c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -r 30 -vf "scale=1920:1080,setsar=1" -c:a aac -b:a 192k -ar 48000 -ac 2`.

### User Interaction Patterns

- **When user says "wrong, wrong and wrong" without specifics, STOP**. Don't guess. Ask: "can you describe what you saw starting at timestamp X?" OR extract frames from their reported timestamp, read them with the host LLM, and verify the problem. Multiple wrong guesses erode trust faster than one pause to ask.
- **"Continue" after a design change means: apply the change and build the NEXT logical thing** (regenerate VO, re-render, re-concat). It does NOT mean wait for more instructions.
- **Deliver previews for irreversible-feeling changes**: voice swap, BGM, major CTA copy changes — always deliver the isolated asset first (WAV, preview MP3) for approval, THEN splice into the master.
- **Cleanup at the end, not between iterations**: keep `frames_src/`, `vo_gemini/`, `hf_hook/`, `hf_cta/` until the user confirms final. Deleting between iterations forces full re-extraction every time.
