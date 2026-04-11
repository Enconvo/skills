# Video/Audio Processor

Comprehensive media processing for Claude Code: transcribe, translate, summarize, dub, caption, and visually analyze videos/audio with professional TTS.

## Features

- **Transcription** — Ultra-fast via Groq Whisper Large V3, SRT + plain text output
- **Translation** — Natural translation via host LLM (default) or Groq LLM fallback, context-aware
- **Dubbing** — Full pipeline: transcribe → clean → translate → review → TTS → dubbed video with professional audio mixing
- **Summary** — Intelligent summaries with timestamps and key points, language-aware
- **Word-Level Captioning** — Karaoke-style word highlighting with 8 animation styles (highlight, appear, bounce, zoom, etc.)
- **Visual Analysis** — Describe silent videos via keyframe extraction + host LLM (or local MLX VLM fallback)
- **Transcript Cleanup** — Removes filler words and verbal tics before translation
- **Agent-Driven Condensation** — Host agent shortens overlong translations for natural timing
- **3 TTS Engines** — edge-tts (default, 50+ langs), Kokoro (local, offline), voicebox (voice cloning)
- **Voice Cloning** — Use any voicebox profile (cloned, designed, or preset voices)
- **URL Support** — YouTube, Twitter/X, TikTok, Instagram, 1000+ sites via yt-dlp
- **Audio + Video** — MP4, MKV, MOV, MP3, M4A, WAV, FLAC, and more
- **Professional Audio Mixing** — Original audio at ~15% + dubbed voice at full volume (like Netflix/Disney+ dubs)
- **Burned-In Dual Subtitles** — Original (top/yellow) + translated (bottom/white), optional
- **Language Detection** — Auto-detects request language, responds in same language

## Supported Formats

### Video Files
MP4, MKV, AVI, MOV, WebM, FLV

### Audio Files
MP3, M4A, WAV, FLAC, OGG, AAC

### URLs
YouTube, Twitter/X, TikTok, Instagram, and 1000+ sites via yt-dlp

## Modes

### 1. Transcription Only
Extract transcript with timestamps from video/audio.

**Usage:**
```
/video-transcribe video.mp4
/video-transcribe podcast.mp3
/video-transcribe https://youtube.com/watch?v=xxx
```

**Output:**
- `{name}_original.srt` - Transcript with timestamps
- `{name}_transcript.txt` - Plain text transcript

### 2. Translation
Transcribe + translate to target language (subtitles only, no TTS).

**Usage:**
```
/video-translate video.mp4 spanish
/video-translate https://youtube.com/watch?v=xxx chinese
```

**Output:**
- `{name}_original.srt` - Original transcript
- `{name}_{target_lang}.srt` - Translated subtitles
- Side-by-side review before saving

### 3. Dubbing (Full Pipeline)
Transcribe, clean, translate, review, TTS, create dubbed video.

**Usage:**
```
/video-dub video.mp4 chinese
/video-dub podcast.mp3 spanish
/video-dub https://youtube.com/watch?v=xxx french

# With voice cloning
/video-dub video.mp4 chinese --voice "Trump_Voice"
```

**Audio Mix Modes:**
- **`mix`** (default): Original audio lowered to ~15% + dubbed voice at full volume. Professional dubbing style.
- **`replace`**: Only dubbed audio, no original track.

**Output:**
- `{name}_original.srt` - Original transcript
- `{name}_{target_lang}.srt` - Translated subtitles
- `{name}_dubbed.mp4` - Final dubbed video

### 4. Summary
Transcribe video/audio and generate comprehensive summary.

**Usage:**
```
/video-summary video.mp4
/video-summary podcast.mp3
/video-summary https://youtube.com/watch?v=xxx

# Language-aware (auto-detected)
"总结这段视频" video.mp4        # Chinese summary
"résumez cette vidéo" video.mp4  # French summary
```

**Output:**
- `{name}_summary.md` - Overview, key points, detailed summary, timestamps, action items

### 5. Word-Level Captioning
Burn word-accurate captions into video with karaoke-style highlighting.

**Usage:**
```
/video-caption video.mp4
/video-caption video.mp4 --style=bounce
/video-caption video.mp4 --bilingual=english --main-lang=chinese
/video-caption https://youtube.com/watch?v=xxx
```

**Caption Styles:**

| Style | Description |
|-------|-------------|
| `highlight` (default) | Full line shown; current word sweeps white → yellow |
| `appear` | Words appear one by one and accumulate |
| `underline` | Current word is yellow + bold + underlined |
| `bounce` | Word-by-word pop with spring physics |
| `fade` | Current word fades in bright yellow |
| `zoom` | Word scales from 0% → 115% → 100% |
| `slide` | Word slides up into position |
| `wave` | Current word rocks with settling oscillation |
| `typewriter` | Characters appear one by one per word |

**Output:**
- `{name}_captioned.mp4` - Video with burned-in captions
- `{name}_captions.ass` - ASS subtitle file
- `{name}_words.json` - Word-level timestamps (reusable)

### 6. Visual Analysis (Silent Video)
Analyze video frames visually and generate scene descriptions.

**Usage:**
```
"analyze this video" video.mp4
"what's happening in this video" video.mp4
"describe this silent video" video.mp4
```

**Output:**
- `{name}_captions.srt` - SRT file with visual descriptions synced to timestamps

## Installation

### Required Dependencies

```bash
# System tools (macOS with Homebrew)
brew install ffmpeg yt-dlp

# Python packages
pip install groq edge-tts numpy soundfile
```

### Groq API Key (Free)

Get your free API key at [console.groq.com](https://console.groq.com)

```bash
export GROQ_API_KEY=gsk_xxx
# Or add to .env file in the skill root directory
```

Groq provides **Whisper Large V3** for transcription — fast and free. Translation is handled by the **host LLM** (default) or Groq LLM fallback. Summarization, condensation, and filler cleanup are handled by the host agent.

### Optional: Kokoro TTS (Local, Offline)

Fast local TTS engine — no internet required. Supports English, Chinese, Japanese, and more.

```bash
conda create -n kokoro python=3.10
conda activate kokoro
pip install kokoro soundfile numpy
```

If not installed, the skill automatically falls back to edge-tts.

### Optional: Voicebox (Voice Cloning & Design)

Install from: [github.com/Enconvo/skills/tree/main/curated/voicebox](https://github.com/Enconvo/skills/tree/main/curated/voicebox)

Voicebox supports three voice profile types:
- **Qwen-TTS Clone** — Clone any voice from reference audio
- **Descriptional Designed** — Design voices from text descriptions
- **Custom_Voice** — Preset profiles with customizable emotions

**Important:** Voicebox is ideal for short videos (1-5 minutes). For long videos (30+ min), use edge-tts instead (parallel generation, much faster).

If not installed, the skill automatically falls back to edge-tts with a helpful install guide.

## Technical Details

### Segment-by-Segment TTS Processing

The dubbing system uses a pipeline for natural-sounding dubbed audio:

1. **TTS Generation** - Each subtitle entry gets its own TTS audio file
2. **Timing Analysis** - Measures each segment's spoken duration against its time window. Overlong segments (>1.3x) are flagged. The host agent condenses the translated text and re-runs TTS.
3. **Speed Adjustment** - Conservative tempo tuning for remaining mismatches (never slows down, mild speedup capped at 2.0x)
4. **Numpy Timeline Assembly** - Places each segment at its exact SRT timestamp. Scales to 1500+ segments.
5. **Subtitle Burn-In** - Optional dual subtitles via ffmpeg subtitles filter.

### Word-Level Captioning

- Auto-sizes font based on video resolution (scaled from 1080p baseline)
- Sentence-aware line breaking (Whisper segments → punctuation → time-gap heuristic)
- Cinema-style fonts: PingFang SC for CJK, Helvetica Neue for Latin
- Bilingual layout: main language on top (karaoke) + secondary below (white)

## Performance

- **Transcription**: ~3 seconds for 1-minute video (Groq Whisper)
- **Translation**: ~10 seconds for 14 segments (host LLM)
- **TTS Generation**: ~30-60 seconds for 1-minute video (segment-by-segment)
- **Video Export**: ~10-30 seconds (re-encode for burned-in subtitles)

**Total**: ~1-2 minutes for 1-minute video

## License

MIT License - Free to use and modify
