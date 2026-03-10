# 🎬 Screen-to-Promo

Turn screen recordings into marketing-ready promo videos for TikTok, Reels, and YouTube Shorts.

## What It Does

Give it a screen recording of your product → get back a polished social media video with:
- 🎙️ AI voiceover narration synced to visual beats
- 📝 Word-by-word animated captions (pop/bounce style)
- 🔍 Smart zoom animations on the action areas
- 🎭 Optional AI presenter overlay with dissolve transitions
- 🎵 Audio mixing with volume normalization

## Pipeline

```
Screen Recording → Prep (1920×1080) → Script → VO → Composite → Mix → Export
```

1. **Prep** — Any resolution/fps screen recording → normalized 1920×1080 @ 30fps frames
2. **Script** — Write narration that matches product demo beats
3. **VO Generation** — Use any TTS/voice cloning tool, get word-level timestamps
4. **Composite** — Config-driven frame-by-frame engine handles zoom, transitions, captions
5. **Audio Mix** — Sequential concat with per-segment loudness normalization
6. **Export** — H.264 with proper SAR/DAR for social media players

## Quick Start

```bash
# 1. Prep your screen recording
bash scripts/prep_source.sh ~/Desktop/my-demo.mov ./frames/demo/

# 2. Create a config.json (see compose.py for full schema)

# 3. Composite frames
python3 scripts/compose.py --config config.json --output-frames ./frames/output/

# 4. Mix audio segments
bash scripts/audio_mix.sh final.m4a -25 hook.wav gap narration.wav

# 5. Encode final video
ffmpeg -y -r 30 -i ./frames/output/f_%04d.jpg -i final.m4a \
  -c:v libx264 -preset fast -crf 23 -pix_fmt yuv420p \
  -vf "setsar=1" -c:a copy -map 0:v -map 1:a output.mp4
```

## Features

### Smart Zoom
- Configurable center point, scale, and timing
- Aspect ratio locked at every frame (no distortion)
- Letterbox-aware: auto-crops content area before zooming

### Transitions
- **Overlay Dissolve** — Presenter cutout (via rembg) on top layer, background fades in, presenter fades out
- **Cross-fade** — Simple alpha blend between segments
- **UI Jump Smoothing** — Auto cross-fades at source timestamps where UI changes abruptly

### Captions
- Word-level sync via Whisper timestamps
- Pop style: scale-bounce entrance + accent underline swipe
- Configurable font, size, color, position

### Audio
- Sequential concat (not amix — preserves amplitude)
- Per-segment loudness normalization (LUFS target)
- Configurable silence gaps between segments

## Requirements

- Python 3.8+ with Pillow, NumPy
- ffmpeg / ffprobe
- Optional: [rembg](https://github.com/danielgatis/rembg) (for presenter cutout)
- Optional: Whisper API access (for word-level timestamps)

## Config Schema

See the docstring in `scripts/compose.py` for the full JSON config schema, including:
- Segment types: `presenter`, `screenrec`, `transition`, `card`
- Zoom configuration
- Time mapping (VO beats → source video timestamps)
- Caption styling
- Audio mix settings

## Cross-Platform

- **macOS**: Helvetica font auto-detected
- **Linux**: DejaVu Sans fallback
- **Windows**: Arial/Segoe UI fallback
- Custom font path configurable in config JSON

## License

MIT
