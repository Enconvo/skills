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
10. **Generate VO** → voicebox skill (clone or pick voice), get word timestamps via Groq Whisper
11. **Optional: AI presenter** → nanobanana image → Veo I2V → extract frames → rembg cutout
12. **Build config** → JSON config for compositor (segments, zooms, transitions, captions)
13. **Compose frames** → `python3 scripts/compose.py --config config.json --output final.mp4`
14. **Mix audio** → `scripts/audio_mix.sh output.m4a -25 audio1.wav gap audio2.wav ...`
15. **Encode** → ffmpeg h264 with `setsar=1` (or use `--output final.mp4` in compose.py)

## Quick Start

```bash
SKILL_DIR="$HOME/.agents/skills/screen-to-promo"

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

## Detailed Reference

For full pipeline walkthrough, planning protocol, zoom playbook, strategy playbooks, caption reference, and all rules: read `references/pipeline.md`.

## Dependencies

- Python 3: PIL/Pillow, numpy, rembg (for presenter cutout)
- ffmpeg/ffprobe
- Groq API (Whisper word timestamps)
- Optional: nanobanana skill (presenter image), voicebox skill (VO), veo skill (I2V)
