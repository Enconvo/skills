# Video/Audio Processor Skill

Comprehensive media processing: transcribe, translate, summarize, and dub videos/audio with professional TTS.

## Features

✅ **Audio + Video support** (MP4, MP3, WAV, M4A, and more)
✅ **URL download** (YouTube, Twitter, TikTok, 1000+ sites via yt-dlp)
✅ Ultra-fast transcription (Groq Whisper Large V3)
✅ Natural translation (context-aware, preserves technical terms)
✅ **Segment-by-segment TTS** (precise timing per subtitle)
✅ **Smart condensation** (shortens overlong translations instead of speeding up audio)
✅ **Perfect audio sync** (natural speed with conservative adjustment)
✅ **Voice cloning support** (use any voicebox profile)
✅ Translation review (edit before TTS generation)
✅ **Auto subtitle embedding** (always adds original language subs)
✅ Dual subtitle support (original + translated)
✅ Multi-language TTS (Kokoro + edge-tts + voicebox)
✅ Intelligent summaries (with timestamps and key points)
✅ **Language-aware detection** (auto-detects request language)

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
- `{name}_transcript.srt` - Transcript with timestamps
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
Transcribe, translate, review, TTS, create dubbed video.

**Usage:**
```
/video-dub video.mp4 chinese
/video-dub podcast.mp3 spanish
/video-dub https://youtube.com/watch?v=xxx french

# With voice cloning
/video-dub video.mp4 chinese --voice "Trump_Voice"
```

**Output:**
- `{name}_original.srt` - Original transcript
- `{name}_{target_lang}.srt` - Translated subtitles
- `{name}_{target_lang}_audio.wav` - Synced TTS audio (intermediate, cleaned up after muxing)
- `{name}_dubbed.mp4` - Final dubbed video with dual subs

### 4. Summary
Transcribe video/audio and generate comprehensive summary.

**Usage:**
```
/video-summary video.mp4
/video-summary podcast.mp3
/video-summary https://youtube.com/watch?v=xxx

# In different languages (auto-detected)
"总结这段视频" video.mp4        # Chinese summary
"résumez cette vidéo" video.mp4  # French summary
"resume este video" video.mp4    # Spanish summary
```

**Output:**
- `{name}_summary.md` - Comprehensive summary:
  - Overview (2-3 sentences)
  - Key points (bullet list)
  - Detailed summary
  - Important timestamps
  - Action items (if applicable)

**Language Detection:**
- Detects request language and generates summary in that language
- "What's this video about?" → English summary
- "总结这段视频" → Chinese summary
- Can override with explicit parameter: `/video-summary video.mp4 spanish`

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

Groq provides **Whisper Large V3** for transcription — it's fast, free, outputs SRT format natively, and is stable for long video ASR (tested on 2h+ videos with 1500+ segments).

### Optional: Kokoro TTS (Local, Offline)

Fast local TTS engine — no internet required. Supports English, Chinese, Japanese, and more.

```bash
conda create -n kokoro python=3.10
conda activate kokoro
pip install kokoro soundfile numpy
```

If not installed, the skill automatically falls back to edge-tts.

### Optional: Voicebox (Voice Cloning & Design)

Install from: [github.com/EnConvo/skill/tree/main/curated/voicebox](https://github.com/EnConvo/skill/tree/main/curated/voicebox)

Voicebox supports three voice profile types:
- **Qwen-TTS Clone** — Clone any voice from reference audio
- **Descriptional Designed** — Design voices from text descriptions
- **Custom_Voice** — Preset profiles with customizable emotions

**Important:** Voicebox is ideal for short videos (1-5 minutes). For long videos (30+ min), voicebox generates segments sequentially which takes too long — use edge-tts instead (parallel generation, much faster).

If not installed, the skill automatically falls back to edge-tts with a helpful install guide.

## Technical Details

### Segment-by-Segment TTS Processing

The dubbing system uses a 4-step pipeline for natural-sounding dubbed audio:

1. **TTS Generation** - Each subtitle entry gets its own TTS audio file
2. **Smart Condensation** - Measures each segment's spoken duration against its time window.
   Overlong segments (>1.3x) get their translation condensed via LLM to fit naturally,
   then TTS is regenerated. This eliminates unnatural speedup artifacts.
3. **Speed Adjustment** - Conservative tempo tuning for remaining mismatches:
   - Never slows down (silence fills gaps instead)
   - Mild speedup only, capped at 2.0x (rare after condensation)
4. **Numpy Timeline Assembly** - Places each segment at its exact SRT timestamp in a
   pre-allocated numpy array. Scales to 1500+ segments without ffmpeg input limits.

**Benefits:**
- Natural-sounding audio (no slow-motion or chipmunk effect)
- Perfect timing sync (no drift over time)
- Maintains original video duration
- Scales to 1500+ segments
- Works with any TTS engine (Kokoro, edge-tts, voicebox)

### Voice Cloning Support

Use any voicebox profile for dubbing:

```bash
# Dub with cloned voice
video_dubber.py video.mp4 chinese --voice "Trump_Voice"
```

Available when voicebox skill is installed with cloned voice profiles.

## Supported Languages

### TTS Voices

| Voice | Engine | Scope |
|-------|--------|-------|
| Brian Multilingual (male, default) | edge-tts | All languages |
| Emma Multilingual (female) | edge-tts | All languages |
| YunxiNeural (male) | edge-tts | Chinese (auto-selected) |
| Kokoro voices (local) | Kokoro | English, Chinese |
| Voicebox profiles (cloned/designed) | Voicebox | Any language |

**Default:** Brian Multilingual handles all languages natively. Chinese defaults to YunxiNeural for better quality.
Users can always override with any edge-tts voice via the `voice_name` parameter.

**Translation:** 50+ languages via Groq Llama 3.3 70B

## Example Sessions

### Transcription (Video/Audio/URL)
```
User: "Transcribe this video"
Claude: Extracts transcript → video_transcript.srt + video_transcript.txt

User: "Transcribe podcast.mp3"
Claude: Extracts audio transcript → podcast_transcript.srt + podcast_transcript.txt

User: "Transcribe https://youtube.com/watch?v=xxx"
Claude: Downloads video → Transcribes → transcript files
```

### Summary (Language-Aware)
```
User: "What's this video about?"
Claude: Transcribes → Generates English summary in video_summary.md

User: "总结这段视频" (video.mp4)
Claude: Transcribes → Generates Chinese summary in video_summary.md

User: "Summarize https://twitter.com/user/status/xxx"
Claude: Downloads → Transcribes → Generates English summary

User: "这个YouTube视频讲什么？https://youtube.com/watch?v=xxx"
Claude: Downloads → Transcribes → Detects Chinese → Generates Chinese summary
```

### Dubbing (Audio Support)
```
User: "Dub this to Chinese"
Claude: Transcribe → Translate → Review → TTS → Dubbed video

User: "把这个音频配音成中文" (podcast.mp3)
Claude: Transcribe audio → Translate to Chinese → Review → TTS

User: "Dub this YouTube video to Spanish: https://youtube.com/watch?v=xxx"
Claude: Downloads → Transcribes → Translates → TTS → Dubbed video
```

## Performance

- **Transcription**: ~3 seconds for 1-minute video (Groq Whisper)
- **Translation**: ~10 seconds for 14 segments (Groq Llama 3.3)
- **TTS Generation**: ~30-60 seconds for 1-minute video (segment-by-segment)
- **Video Export**: ~2 seconds (no re-encoding)

**Total**: ~1-2 minutes for 1-minute video

## Troubleshooting

### Groq API Error
```
❌ Error: GROQ_API_KEY not provided
```
**Fix**: Get free API key from [console.groq.com](https://console.groq.com)

### YouTube Download Error
```
❌ Error downloading video
```
**Fix**: Update yt-dlp: `pip install -U yt-dlp`

### Kokoro Import Error
```
ModuleNotFoundError: No module named 'kokoro'
```
**Fix**: Skill falls back to edge-tts automatically for Chinese

### Subtitle Not Showing in QuickTime
- Use VLC Player instead (better subtitle support)
- Or: View → Subtitles → Choose track in QuickTime

## Notes

- All modes start with transcription
- Translation uses natural phrasing (not machine translation)
- Dubbing includes perfect audio-subtitle sync (segment-by-segment)
- **Always embeds original language subtitles** in output video
- Summaries are comprehensive but concise
- Original video quality is preserved

## License

MIT License - Free to use and modify
