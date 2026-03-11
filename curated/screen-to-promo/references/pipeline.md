# Screen-to-Promo Pipeline Reference

## Full Pipeline (7 Steps)

### 1. Analyze Source Material
```bash
# Prep each screen recording into 1920x1080 frames
scripts/prep_source.sh ~/Desktop/feature-demo.mov ./frames/feature1/ 30
```
- Note content bounds if letterboxed (CONTENT_BOUNDS output)
- Check key moments: when does the action happen? Map timestamps.

### 2. Generate Presenter (Optional)
- Use nanobanana skill with `--reference` for consistent character
- 1/5 left framing: presenter occupies leftmost 20-25%, right 75-80% pure white
- PHOTOREALISTIC style, not cartoon/3D
- Generate I2V clip via Veo skill (8s, native audio)
- Extract frames: `ffmpeg -i presenter.mp4 -r 30 -q:v 2 frames/presenter/f_%04d.jpg`
- rembg cutout: `from rembg import remove, new_session` (batch all frames)

### 3. Write Script + Generate VO
- Simple everyday words, dramatic delivery tone
- Use voicebox skill to clone presenter voice from Veo native audio
- Generate per-section VOs
- Get word timestamps: Groq Whisper API with `timestamp_granularities[]=word`

### 4. Time-Map VO to Source
Map VO script beats to source video timestamps:
```python
import numpy as np
vo_times = [0, 2.5, 5.0, 10.0, 15.0]   # when VO says each beat
src_times = [0, 2.0, 4.0, 8.0, 18.0]    # matching source moment
src_t = float(np.interp(vo_t, vo_times, src_times))
```

### 5. Build Config JSON
See compose.py docstring for full schema. Key decisions:
- Zoom targets: where does the action happen? (cx, cy coordinates)
- Transition type: overlay_dissolve for presenter→screenrec
- Smooth jumps: identify source times where UI changes abruptly

### 6. Compose + Mix Audio
```bash
python3 scripts/compose.py --config config.json --output-frames ./frames/output/
bash scripts/audio_mix.sh output.m4a -25 hook.wav gap explain_vo.wav transition_vo.wav spelling_vo.wav
```

### 7. Encode Final Video
```bash
# Option A: Use compose.py --output for one-step compose+encode
python3 scripts/compose.py --config config.json --output final.mp4 --audio output.m4a

# Option B: Manual encode from frames
ffmpeg -y -r 30 \
  -i ./frames/output/f_%04d.jpg \
  -i output.m4a \
  -c:v libx264 -preset fast -crf 23 -pix_fmt yuv420p \
  -vf "setsar=1" \
  -c:a copy -map 0:v -map 1:a \
  final.mp4
```

## Critical Rules (Learned the Hard Way)

### AR Distortion Prevention
- **ALWAYS** lock aspect ratio in zoom: `ch = cw × H / W`
- **NEVER** zoom letterboxed frames directly — crop content first, re-center, then zoom
- **ALWAYS** `setsar=1` in final encode
- **ALWAYS** send to Telegram with explicit `width=1920 height=1080`

### Audio Rules
- **Never loudnorm original Veo/source audio** — use untouched, it distorts quality
- **concat > amix** for sequential segments (amix divides amplitude)
- **Check word timestamps before cutting** — don't cut at round numbers, verify the last word ended
- **0.5s silence gaps** between sections for breathing room
- **Target -25 LUFS** for VO segments (loudnorm I=-25:TP=-3:LRA=11)

### Transitions
- Presenter→screenrec: use overlay_dissolve (cutout on top, BG fades in gradually, presenter fades out)
- BG fade should start 0.5-1s BEFORE presenter fade for smooth layered feel
- Cosine ease-in-out for all fades: `0.5 - 0.5 * cos(progress * π)`
- If source has UI jumps (panels appearing), add to smooth_jumps list

### Captions
- Word-level timestamps via Groq Whisper (`timestamp_granularities[]=word`)
- Pop style: scale bounce + underline swipe looks best on TikTok
- Position: H - 130px from bottom
- White text, black outline (3px), yellow accent underline

### Source Prep
- Always prep to 1920x1080 at 30fps regardless of source resolution/fps
- Record content bounds for letterboxed sources
- Screen recordings from retina displays may be 2x — scale down
