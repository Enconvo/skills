---
name: screen-to-promo
description: >
  Turn screen recordings into marketing-ready promo videos for TikTok/Reels/Shorts.
  Full pipeline: source prep → script writing → VO generation → frame-by-frame compositing → 
  audio mixing → final encode. Supports animated presenters (AI animal/character with rembg cutout), 
  per-word caption sync, zoom animations, overlay dissolve transitions, time-mapped VO-to-source sync,
  and letterbox-aware cropping. Use when: (1) user has screen recordings of product features and wants
  a social media marketing video, (2) user says "make a promo video", "TikTok video from this recording",
  "marketing video", "highlight reel", (3) user provides .mov/.mp4 screen recordings to turn into
  polished product demos with narration and captions.
---

# Screen-to-Promo

Transform screen recordings into scroll-stopping social media promo videos.

## Pipeline Overview

1. **Prep sources** → `scripts/prep_source.sh` (any resolution → 1920×1080 @ 30fps)
2. **Analyze content** → identify key moments, map timestamps
3. **Write script** → simple words, dramatic delivery (match product beats to VO beats)
4. **Generate VO** → voicebox skill (clone or pick voice), get word timestamps via Groq Whisper
5. **Optional: AI presenter** → nanobanana image → Veo I2V → extract frames → rembg cutout
6. **Build config** → JSON config for compositor (segments, zoom, transitions, captions)
7. **Compose frames** → `python3 scripts/compose.py --config config.json --output-frames ./frames/out/`
8. **Mix audio** → `scripts/audio_mix.sh output.m4a -25 audio1.wav gap audio2.wav ...`
9. **Encode** → ffmpeg h264 with `setsar=1`

## Quick Start

```bash
SKILL_DIR="$(dirname "$0")/.."  # adjust to skill root

# 1. Prep screen recording
bash "$SKILL_DIR/scripts/prep_source.sh" ~/Desktop/demo.mov ./frames/demo/ 30

# 2. Build config.json (see compose.py docstring for schema)
# 3. Compose
python3 "$SKILL_DIR/scripts/compose.py" --config config.json --output-frames ./frames/output/

# 4. Mix audio
bash "$SKILL_DIR/scripts/audio_mix.sh" final_audio.m4a -25 hook.wav gap demo_vo.wav

# 5. Encode
ffmpeg -y -r 30 -i ./frames/output/f_%04d.jpg -i final_audio.m4a \
  -c:v libx264 -preset fast -crf 23 -pix_fmt yuv420p -vf "setsar=1" \
  -c:a copy -map 0:v -map 1:a final.mp4
```

## Key Rules

- **AR lock**: always `ch = cw × H / W` in zoom math. One slip = visible squish.
- **Letterboxed sources**: crop content FIRST, re-center, then zoom. Never zoom the full padded frame.
- **Audio**: never loudnorm original Veo audio. Use concat not amix. 0.5s gaps between sections.
- **Transitions**: overlay_dissolve with rembg cutout for presenter→screenrec. BG fades in first, presenter dissolves out second.
- **Captions**: Groq Whisper word-level timestamps, pop style (scale bounce + yellow underline).
- **Script writing**: simple everyday words + dramatic voice delivery > complex vocabulary.
- **UI jumps**: add source timestamps to `smooth_jumps` list — compositor auto cross-fades 0.5s.

## Detailed Reference

For full pipeline walkthrough, config schema, and all rules: read `references/pipeline.md`.

## Dependencies

- Python 3: PIL/Pillow, numpy, rembg (for presenter cutout)
- ffmpeg/ffprobe
- Groq API (Whisper word timestamps)
- Optional: nanobanana skill (presenter image), voicebox skill (VO), veo skill (I2V)
