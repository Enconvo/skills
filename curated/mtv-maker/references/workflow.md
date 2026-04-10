# MTV Maker v2 — Detailed Workflow Reference

## Architecture

```
Song Concept + Character Photo
        │
        ▼
┌─────────────────┐
│  Phase 1: Song  │  acestep skill → 2 MP3 versions
│  Generation     │  acestep-songwriting for lyrics
└────────┬────────┘
         │ User picks version + time range
         ▼
┌─────────────────┐
│  Phase 2: Trim  │  ffmpeg -ss BEFORE -i → chorus clip
│  Chorus Clip    │  + fade in/out + volume verification
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Phase 3: Scene │  image_to_image × 6 (with character ref)
│  Images (6x)    │  16:9, cinematic, I2V-optimized
└────────┬────────┘
         │ User approves (1-by-1 or autonomous)
         ▼
┌─────────────────┐
│  Phase 4: I2V   │  grok-video-gen or seedance-api × 6
│  Video Clips    │  ~5-6s each, motion matches mood
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Phase 5: Video │  ffmpeg upscale → crossfade → mux audio
│  Assembly       │  1920×1080, 24fps, clean base
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Phase 6: Lyric │  Groq Whisper transcription → SRT
│  Timing         │  Correct lyrics, keep timestamps
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Phase 7: Final │  ASS captions (bilingual) + credits
│  Render         │  Black frame ending + audio fade
│                 │  Burn onto CLEAN source only
└─────────────────┘
```

## Interaction Model

The skill supports two modes:

### Interactive Mode (Default)
- Phase 1: Show lyrics for approval before generating
- Phase 2: User listens to 2 versions, picks one, specifies time range
- Phase 3: Show images one-by-one for approval
- Phase 4: Show first I2V test for quality check, then proceed
- Phase 5-7: Autonomous (unless user wants to review captions)

### Autonomous Mode
- User says "do it on your own" or "I trust you" at any phase
- Agent takes full creative control from that point forward
- Still delivers checkpoints (e.g., "here are all 6 photos") but doesn't wait for per-item approval

## Skill Dependencies

| Skill | Purpose | Required? |
|-------|---------|-----------|
| `acestep` | Music generation | Yes |
| `acestep-songwriting` | Lyrics writing guide | Yes |
| `grok-video-gen` | I2V video (primary) | Yes (or seedance) |
| `seedance-api` | I2V video (alternate) | Optional |
| `video-processor` | Groq Whisper transcription | Recommended |
| `nanobanana` | Image generation (no character ref) | Optional |

## External Tools

| Tool | Purpose |
|------|---------|
| `image_to_image` | Scene images with character reference |
| `text_to_image` | Scene images without character reference |
| `ffmpeg` | Audio/video processing, assembly, caption burn |
| `ffprobe` | Duration/format inspection |

## ASS Style Definitions (Complete)

```ass
[Script Info]
Title: {Song Title} MTV
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Title,PingFang SC,100,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,1,0,0,0,100,100,15,0,1,5,0,5,50,50,80,1
Style: OpenCredit,PingFang SC,48,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,8,0,1,3,0,5,50,50,60,1
Style: LyricCN,Noto Serif TC,56,&H00FFFFFF,&H000000FF,&H60000000,&HA0000000,0,0,0,0,100,100,5,0,1,3,5,2,50,50,100,1
Style: LyricEN,PingFang SC,32,&H80FFFFFF,&H000000FF,&H50000000,&HA0000000,0,1,0,0,100,100,3,0,1,2,3,2,50,50,55,1
Style: EndCredit,PingFang SC,62,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,1,0,0,0,100,100,10,0,1,0,0,5,50,50,80,1
Style: Brand,PingFang SC,42,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,6,0,1,0,0,5,50,50,30,1
```

### Style Details

| Style | Size | Font | Purpose | Alignment |
|-------|------|------|---------|-----------|
| Title | 100pt | PingFang SC Bold | Song title, centered | 5 (center-center) |
| OpenCredit | 48pt | PingFang SC | Artist · Brand credit | 5 (center-center) |
| LyricCN | 56pt | Noto Serif TC | Chinese lyrics, bottom | 2 (bottom-center) |
| LyricEN | 32pt | PingFang SC Italic | English translation, below CN | 2 (bottom-center) |
| EndCredit | 62pt | PingFang SC Bold | End credits, centered | 5 (center-center) |
| Brand | 42pt | PingFang SC | Brand line, centered | 5 (center-center) |

### Caption Timing Template

```ass
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text

; === TITLE (first 4.5 seconds) ===
Dialogue: 0,0:00:00.00,0:00:04.50,Title,,0,0,0,,{\fad(2000,1200)\pos(960,420)}{SONG_TITLE}
Dialogue: 0,0:00:01.20,0:00:04.00,OpenCredit,,0,0,0,,{\fad(1500,1000)\pos(960,540)}{ARTIST} · EnConvo

; === LYRICS (synced to audio timestamps) ===
; Chinese line
Dialogue: 0,{START},{END},LyricCN,,0,0,0,,{\fad(800,600)}{CHINESE_LYRIC_LINE}
; English translation (same timing, positioned below)
Dialogue: 0,{START},{END},LyricEN,,0,0,0,,{\fad(800,600)}{ENGLISH_TRANSLATION}

; === END CREDITS (on black frames, 6+ seconds) ===
Dialogue: 0,{SONG_END+1.5s},{SONG_END+8s},EndCredit,,0,0,0,,{\fad(1500,3000)\pos(960,460)}词 · 曲 · 演唱  {ARTIST}
Dialogue: 0,{SONG_END+2.0s},{SONG_END+8s},Brand,,0,0,0,,{\fad(1500,3000)\pos(960,560)}Powered by EnConvo
```

## Scene Design Patterns by Genre

### Sad Ballad (e.g., Jay Chou《安静》style)
1. Window/rain — isolation, looking out
2. Street in rain — walking alone
3. Empty luxury space — what's left behind
4. Piano/instrument — inner monologue
5. Moonlit balcony/terrace — regret washing over
6. Rooftop/bridge at dawn — letting go, wide shot

### Upbeat Pop
1. Urban street — confidence, walking with purpose
2. Neon-lit club/bar — energy, movement
3. Rooftop party — social, lights
4. Dance floor — full body motion
5. Car interior — freedom, driving
6. Sunrise cityscape — triumphant ending

### Romantic
1. Café meeting — intimate, close
2. Park/garden walk — side by side (or alone remembering)
3. Beach/waterfront — golden hour
4. Candlelit dinner — warmth
5. Starlit balcony — whispered confessions
6. Embrace or separation — emotional climax

## I2V Motion Vocabulary

Keep a consistent vocabulary when prompting I2V to ensure mood-appropriate motion:

**Slow/Sad:**
- "subtle breathing movement"
- "gentle wind moving hair slightly"
- "slow deliberate blink"
- "barely perceptible head tilt downward"
- "slow defeated walk, camera tracking backward maintaining distance"
- "rain falling past the window, slight condensation movement"

**Medium/Reflective:**
- "slowly turns head to look at camera"
- "hand gently traces along surface"
- "walks at natural relaxed pace"
- "slight smile fading"
- "fingers lightly touch piano keys"

**Fast/Energetic:**
- "quick hair flip with confident smile"
- "dynamic dance movement"
- "walking briskly, coat flowing"
- "spinning with arms outstretched"
- "laughing, natural body movement"

## File Size Optimization

Target: < 50MB for Telegram delivery.

| Setting | When | CRF |
|---------|------|-----|
| Clip generation | Phase 3 upscale | -crf 20 |
| Assembly | Phase 5 xfade | -crf 20 |
| Final burn | Phase 7 ASS burn | -crf 18 |

For longer MTVs (full song, 3+ min), use `-crf 22` throughout to stay under 50MB.
