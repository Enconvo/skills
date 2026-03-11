# screen-to-promo

Turn screen recordings into polished, goal-driven videos — viral marketing promos, user guides, product demos, and more.

## What it does

Give it a screen recording and a goal. It figures out the right strategy, plans the edit, and produces a finished video with narration, zooms, captions, and audio — all from a JSON config and a Python compositor.

### Supported video types

| Type | Duration | Use case |
|------|----------|----------|
| **Viral Marketing** | 30-90s | TikTok/Reels/Shorts promo — hook, fast cuts, dramatic VO, CTA |
| **User Guide** | 3-15min | Step-by-step tutorial — calm narrator, many zooms for readability |
| **Product Demo** | 1-3min | Feature showcase — confident tone, one zoom per feature |
| **Changelog** | 30-90s | What's new montage — fast clips, feature labels |

### How it decides

The skill detects intent from your words and source material, selects a strategy, and recommends a plan:

```
Based on your 5-minute screen recording of EnConvo, I recommend:

- Mode: Viral marketing promo (60-90s)
- Strategy: Pain → Solution → Magic → Payoff
- Hook: "Building an AI agent used to mean... all of this."
- Zooms: 3 focused moments — setup, creation, result
- Captions: Bold pop, word-by-word

Going with this — let me know if you want to adjust.
```

You say "go", or correct what you don't like, or say "your call" and it runs autonomously.

## Pipeline

```
Intent Detection → Strategy Selection → Source Analysis → Storyboard Planning → Production
```

1. **Intent & Strategy** — detect goal, pick playbook (marketing/guide/demo/changelog)
2. **Source Analysis** — probe video, extract key frames, identify UI regions, detect artifacts
3. **Planning** — map VO to source timestamps, pre-calculate zoom targets from actual frames, build zoom table
4. **Prep** — normalize to 1920x1080 @ 30fps
5. **Script & VO** — write script (style matches strategy), generate voice via voicebox, get word timestamps via Groq Whisper
6. **Compose** — frame-by-frame compositing with zooms, captions, transitions, time-mapping
7. **Audio Mix & Encode** — loudness normalization, final h264 encode

## Features

- **Goal-aware strategy** — different editing approach for marketing vs tutorial vs demo
- **Multi-zoom** — multiple zoom regions per segment with cosine ease-in-out
- **Zoom playbook** — timing, frequency, scale discipline rules to avoid dizzying the audience
- **Caption styles** — pop (word-by-word bounce), karaoke (phrase with highlight), static
- **CJK-aware** — karaoke captions work with Chinese/Japanese/Korean (no-space joining)
- **Bold/outline control** — configurable font, size, outline toggle
- **Time-mapping** — VO-to-source interpolation for speed-matched playback
- **Smooth jumps** — cross-fade on UI state changes instead of hard cuts
- **Presenter overlay** — AI-generated character with rembg cutout + dissolve transitions
- **Letterbox handling** — auto-detect and crop content bounds before compositing

## Quick start

```bash
# Prep source
bash scripts/prep_source.sh ~/Desktop/demo.mov ./frames/source/ 30

# Compose + encode (config.json defines everything)
python3 scripts/compose.py --config config.json --output final.mp4

# Mix audio separately if needed
bash scripts/audio_mix.sh output.m4a -25 hook.wav gap vo.wav
```

## Config example

```json
{
  "fps": 30,
  "width": 1920,
  "height": 1080,
  "segments": [
    {
      "type": "screenrec",
      "source": "./frames/source/",
      "source_pattern": "f_%04d.jpg",
      "duration": 145.0,
      "words_json": "./vo_words.json",
      "time_map": {
        "vo_times":  [0, 5, 10, 22, 40, 60, 90, 120, 145],
        "src_times": [0, 8, 15, 30, 55, 95, 150, 200, 250]
      },
      "smooth_jumps": [30, 95, 150],
      "zooms": [
        {
          "cx": 1200, "cy_start": 185, "cy_end": 185, "scale": 2.0,
          "in_start": 22, "in_end": 24, "hold_end": 30, "out_end": 32,
          "_note": "Zoom 1: Feature peek"
        },
        {
          "cx": 1200, "cy_start": 170, "cy_end": 220, "scale": 2.0,
          "in_start": 53, "in_end": 55, "hold_end": 101, "out_end": 104,
          "_note": "Zoom 2: Sustained detail"
        },
        {
          "cx": 335, "cy_start": 700, "cy_end": 750, "scale": 2.2,
          "in_start": 106, "in_end": 108, "hold_end": 125, "out_end": 127,
          "_note": "Zoom 3: Result payoff"
        }
      ]
    }
  ],
  "captions": {
    "enabled": true,
    "style": "pop",
    "font": "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "font_size": 96,
    "position_y": -180,
    "color": [255, 255, 255],
    "outline_color": [0, 0, 0],
    "accent_color": [255, 200, 50]
  }
}
```

## Zoom rules

- **Never guess coordinates** — extract the actual frame, measure pixels
- **2.0x scale** is the sweet spot for 1080p. 2.2-2.5x for small targets. Never exceed 3.0x
- **Max 3-4 zooms** per 2-minute video. Min 15-20s gap between zooms
- **Zoom in 1-2s before** VO mentions it. Zoom out during natural pauses
- **Hold 8-20s** for focused moments, up to 45s for sustained action
- **Narrative arc**: peek (short) → sustained focus (long) → payoff (medium)

## Dependencies

- Python 3, PIL/Pillow, numpy
- ffmpeg / ffprobe
- Groq API key (Whisper word timestamps)
- Optional: voicebox (VO), nanobanana (presenter image), veo (I2V), rembg (cutout)

## Reference

- `SKILL.md` — full skill documentation with strategy tables and interaction flow
- `references/pipeline.md` — detailed pipeline reference, strategy playbooks, zoom playbook, caption reference, Whisper gotchas
