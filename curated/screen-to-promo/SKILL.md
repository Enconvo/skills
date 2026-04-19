---
name: screen-to-promo
description: >
  Turn screen recordings into polished videos — marketing promos, user guides, product demos,
  and more. Goal-aware pipeline: detects user intent, selects strategy, recommends a plan,
  then executes. Full pipeline: intent detection → strategy selection → source analysis →
  storyboard planning → source prep → VO generation → frame-by-frame compositing →
  audio mixing → final encode. Supports animated presenters (AI animal/character with rembg cutout),
  per-word caption sync (pop, karaoke, static styles), multi-zoom animations, overlay dissolve
  transitions, time-mapped VO-to-source sync, CJK-aware captions, and letterbox-aware cropping.
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

### HyperFrames (title cards — hook & CTA)

HTML/CSS/JS composition engine for hook and CTA cards. Gives you spring animations, light leaks, per-word captions, and proper motion design.

- Install per-project (node_modules don't copy cleanly between dirs):
  ```bash
  cd <project-dir> && npm init -y && npm install hyperframes
  ./node_modules/.bin/hyperframes lint .
  ./node_modules/.bin/hyperframes render .
  ```
- `npx hyperframes` alone doesn't work — npm treats it as unknown. Use the local binary.
- Skill reference: `~/.claude/skills/hyperframes` (+ `hyperframes-cli`, `gsap`).

### ffmpeg + compose.py (middle content — screen recording)

Shell + Python frame-by-frame compositing. Used by `scripts/compose.py` for zooms, captions, transitions, multi-segment screen-recording sequences.

**Canonical pipeline:** HyperFrames hook.mp4 + compose.py middle.mp4 + HyperFrames cta.mp4 → concat.

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

The skill uses a **recommend-and-confirm** pattern — never a questionnaire:

1. **User knows what they want** — "make a TikTok viral promo" → detect intent, pick strategy, run
2. **User needs guidance** — "make a video from this" → analyze source, recommend strategy, get thumbs up
3. **User delegates** — "your call" / "do your best" → infer best strategy, briefly show plan, run unless user objects

**Rules:**
- **Never ask more than 1-2 questions** — prefer recommending over asking
- **Show the full plan at once** so user can approve with one word or correct what they disagree with
- **Infer before asking** — source is 5min dev tool recording + user said "viral"? That's a marketing promo, don't ask

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

### Phase 0: Intent & Strategy
1. **Detect intent** from user's words + source material
2. **Select strategy** (viral_marketing | user_guide | product_demo | changelog | custom)
3. **Recommend plan** — brief summary of mode, duration, narrative, zoom/caption/hook/CTA approach
4. **Confirm** — proceed on "go" / adjust on corrections / infer on "your call"

### Phase 1: Analysis & Planning
5. **Source Analysis** — probe resolution/duration/fps/audio, extract key frames every 10s, identify UI regions (app windows, sidebars, chat areas), detect artifacts (recording bars, idle cursor, blank screens, notification popups)
6. **Context & Audience** — research product/brand, community terminology, target platform constraints, language/localization needs (CJK font requirements, caption style choice)
7. **Storyboard & Planning** — map VO lines to source timestamps, pre-calculate zoom targets from actual key frame pixel coordinates (never guess cx/cy), build zoom table, flag problems (time jumps needing smooth_jumps, missing fonts, duration vs platform limits)

### Phase 2: Production
8. **Prep sources** → `scripts/prep_source.sh` (any resolution → 1920×1080 @ 30fps)
9. **Write script** → style driven by strategy (dramatic for marketing, instructional for guides)
10. **Generate VO** → TTS fallback sequence: **Enconvo active TTS** (if available) → **Voicebox** → **Edge-TTS** → **Kokoro**. Get word timestamps via Groq Whisper.
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
- **Captions**: Groq Whisper word-level timestamps, choose style based on language and strategy.
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

## Detailed Reference

For full pipeline walkthrough, planning protocol, zoom playbook, strategy playbooks, caption reference, and all rules: read `references/pipeline.md`.

## Dependencies

- Python 3: PIL/Pillow, numpy, rembg (for presenter cutout)
- ffmpeg/ffprobe
- Groq API (Whisper word timestamps)
- VO skills (fallback chain): Enconvo active TTS → voicebox → edge-tts → kokoro
- Optional: nanobanana skill (presenter image), veo skill (I2V), acestep (BGM)

## Lessons Learned (Hard-Won — from real production runs)

Capture discoveries that cost hours the first time. Check this list BEFORE starting any iteration loop.

### Script Authoring & Timing

- **Writers block gate**: do NOT start TTS generation until the full script, zoom plan, and segment durations are approved by the user. TTS burns time + credits. User-visible feedback loops (show the plan, get "go") are cheaper than regenerating audio.
- **Reuse VO across iterations**: if only zoom timing / frames / cuts change, keep old VO WAVs — don't regenerate. Only regenerate the specific segment whose TEXT changed.
- **Delay pattern for late-landing words**: when a specific word (e.g. "Approve", "ALIVE") must sync to a specific video frame, compute delay = `target_seg_time - raw_word_start_in_wav`, then apply via `ffmpeg -af "adelay=Nms|Nms,apad=pad_dur=D,atrim=0:D,asetpts=PTS-STARTPTS"`. Also shift the word-timings JSON by the same delay so captions stay synced.
- **Word timing estimation fallback**: if Groq Whisper API key isn't available, evenly distribute words across `(duration - start_pad - end_pad)`. This is "good enough" for pop captions — perfect sync is not required for non-karaoke styles.

### VO Providers

- **TTS fallback sequence**: **Enconvo active TTS** (if available) → **Voicebox** → **Edge-TTS** → **Kokoro**. Check Enconvo's active TTS first via `~/.config/enconvo/installed_preferences/tts.json` → `selected` field; Gemini TTS (Puck / other prebuilt voices) via `tts/gemini_tts/generate` produces cleaner articulation on technical terms (BotFather, Ollama, IM Channels) than cloned voices. Fall through to Voicebox if Enconvo TTS is unavailable, then Edge-TTS (cloud, 50+ languages), then Kokoro (local, offline).
- **Credentials are in Enconvo's credential manager — use the API, not the raw JSON file**. For Groq (Whisper word timestamps) and any other provider, call `local_api credentials/load_credentials {"providerName": "groq"}`. The returned `apiKey` is the real, usable key. Do NOT `cat ~/.config/enconvo/installed_preferences/credentials|groq.json` directly — that file stores an encrypted/hashed placeholder (128-char hex), not the working `gsk_...` key. Same pattern for `openai`, `elevenlabs`, `anthropic`, etc.
- **Gemini TTS phonetic quirks**: `ANN` capitalized is read as "A-N-N" spelled out. Use the full phrase `Ann the Uncensored` for natural pronunciation. `I M Channels` (space-separated) reads cleaner than `IM Channels`.
- **Preview before committing**: when user requests a voice/text change, generate to a `_new.wav` or `_v2.wav` filename FIRST, deliver preview, wait for approval, THEN swap into the master file. Never overwrite an approved VO in place.
- **Voice switch workflow**: user can change Enconvo's active TTS voice between calls. To re-record with a new voice, just call `tts/tts` or `tts/gemini_tts/generate` with the same text — the active voice is picked up automatically.

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

### Hook & CTA Design (HyperFrames)

- **Use HyperFrames for title cards** — install locally per-project: `cd dir && npm init -y && npm install hyperframes`, then `./node_modules/.bin/hyperframes lint/render .`. `npx hyperframes` alone doesn't work because npm treats it as an unknown command.
- **HyperFrames root composition requires `data-start="0"` AND `data-duration="N"`** on the composition div. The lint warning makes this obvious but it's easy to miss the first time.
- **Standalone compositions must NOT use `<template>`** — the sub-composition wrapper pattern only applies when loaded via `data-composition-src`. For a standalone card, put the `data-composition-id` div directly in `<body>`.
- **Node modules don't copy cleanly between project dirs**: if you `cp -r node_modules` from one hyperframes project to another, renders may fail with "Missing manifest" errors. Always fresh `npm install hyperframes` per project dir.
- **Message > brand for product CTAs**: when the video is about a specific feature ("channel agent"), the CTA should lead with the feature name as hero, not the brand. Layout: small brand wordmark on top (`ENCONVO`) → hero feature name (`CHANNEL AGENT`) → amber promise tag (`SET UP IN SECONDS`). The feature is what the viewer wants; the brand is who made it.
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
