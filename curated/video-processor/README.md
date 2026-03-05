# Video/Audio Processor

Comprehensive media processing for Claude Code: transcribe, translate, summarize, and dub videos/audio with professional TTS.
Claude Code 上的全能媒体处理工具：转录、翻译、摘要、配音，支持专业 TTS。

## Features / 功能

- **Transcription** — Ultra-fast via Groq Whisper Large V3, SRT + plain text output / 极速转录，Groq Whisper Large V3，输出 SRT 及纯文本
- **Translation** — Natural translation via EnConvo API, context-aware / 自然翻译，EnConvo API，上下文感知
- **Dubbing** — Full pipeline: transcribe → clean → translate → review → TTS → dubbed video / 完整配音流水线：转录→清理→翻译→审核→TTS→配音视频
- **Summary** — Intelligent summaries with timestamps and key points / 智能摘要，含时间戳和要点提取
- **Transcript Cleanup** — Removes filler words and verbal tics before translation / 翻译前清除填充词和口语习惯
- **Agent-Driven Condensation** — Host agent shortens overlong translations for natural timing / 代理驱动压缩过长翻译，确保自然时间
- **3 TTS Engines** — edge-tts (default, 50+ langs), Kokoro (local, offline), voicebox (voice cloning) / 三引擎：edge-tts（默认）、Kokoro（本地离线）、voicebox（声音克隆）
- **Voice Cloning** — Use any voicebox profile (cloned, designed, or preset voices) / 支持 voicebox 声音克隆配置文件
- **URL Support** — YouTube, Twitter/X, TikTok, Instagram, 1000+ sites via yt-dlp / 支持 YouTube、Twitter、TikTok 等 1000+ 网站
- **Audio + Video** — MP4, MKV, MOV, MP3, M4A, WAV, FLAC, and more / 支持 MP4、MKV、MOV、MP3、M4A、WAV、FLAC 等格式
- **Burned-In Dual Subtitles** — Original (top/yellow) + translated (bottom/white), always visible / 双字幕烧录，原文在上（黄色）+译文在下（白色），始终可见
- **Word-Level Captioning** — Karaoke-style captions with per-word timestamps via Groq Whisper / 逐字字幕，每个词精确时间戳，卡拉OK高亮效果
- **Language Detection** — Auto-detects request language, responds in same language / 自动检测请求语言，以相同语言回复

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

**Output:**
- `{name}_original.srt` - Original transcript
- `{name}_{target_lang}.srt` - Translated subtitles
- `{name}_dubbed.mp4` - Final dubbed video with burned-in dual subs

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

### 5. Word-Level Captioning
Burn word-accurate captions into video with karaoke-style highlighting. Each word highlights at the exact moment it's spoken. Groups words by clause/sentence boundaries for natural readability.

**Usage:**
```
/video-caption video.mp4
/video-caption video.mp4 --style=appear --position=top
/video-caption https://youtube.com/watch?v=xxx
```

**Options:**
- `--style=highlight` (default) — karaoke fill: words highlight as spoken
- `--style=appear` — words appear one by one
- `--style=underline` — full line shown, current word underlined
- `--position=bottom|top|center` — caption position
- `--font-size=24` — font size
- `--words-per-line=8` — max words per caption line
- `--srt-only` — only generate ASS file, don't burn into video

**Output:**
- `{name}_captioned.mp4` - Video with burned-in word-level captions
- `{name}_captions.ass` - ASS subtitle file (reusable)
- `{name}_words.json` - Raw word timestamps from Whisper

**Note:** Requires ffmpeg built with libass (`brew install homebrew-ffmpeg/ffmpeg/ffmpeg`).

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

Groq provides **Whisper Large V3** for transcription — fast and free. Translation is handled by **EnConvo API** (must be running on `localhost:54535`). Summarization, condensation, and filler cleanup are handled by the host agent.

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

The dubbing system uses a pipeline for natural-sounding dubbed audio:

1. **TTS Generation** - Each subtitle entry gets its own TTS audio file
2. **Timing Analysis** - Measures each segment's spoken duration against its time window.
   Overlong segments (>1.3x) are flagged in a timing report. The host agent condenses
   the translated text and re-runs TTS for those segments.
3. **Speed Adjustment** - Conservative tempo tuning for remaining mismatches:
   - Never slows down (silence fills gaps instead)
   - Mild speedup only, capped at 2.0x (rare after condensation)
4. **Numpy Timeline Assembly** - Places each segment at its exact SRT timestamp in a
   pre-allocated numpy array. Scales to 1500+ segments without ffmpeg input limits.
5. **Subtitle Burn-In** - Burns dual subtitles into video (original top/yellow + translated bottom/white)
   using ffmpeg `subtitles` filter. Re-encodes video with `-c:v libx264 -crf 20 -preset fast`.

**Benefits:**
- Natural-sounding audio (no slow-motion or chipmunk effect)
- Perfect timing sync (no drift over time)
- Maintains original video duration
- Scales to 1500+ segments
- Burned-in dual subtitles (always visible, no player support needed)
- Works with any TTS engine (Kokoro, edge-tts, voicebox)

### Voice Cloning Support

Use any voicebox profile for dubbing:

```bash
# Dub with cloned voice
generate_tts_and_dub.sh video.mp4 original.srt translated.srt chinese "Trump"
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

**Translation:** 50+ languages via EnConvo API

## Example Sessions

### Transcription (Video/Audio/URL)
```
User: "Transcribe this video"
Claude: Extracts transcript → video_original.srt + video_transcript.txt

User: "Transcribe podcast.mp3"
Claude: Extracts audio transcript → podcast_original.srt + podcast_transcript.txt

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
Claude: Transcribe → Clean filler → Translate → Review → TTS → Dubbed video

User: "把这个音频配音成中文" (podcast.mp3)
Claude: Transcribe audio → Clean filler → Translate to Chinese → Review → TTS

User: "Dub this YouTube video to Spanish: https://youtube.com/watch?v=xxx"
Claude: Downloads → Transcribes → Clean filler → Translates → TTS → Dubbed video
```

### Word-Level Captioning
```
User: "Caption this video with word-level timestamps"
Claude: Transcribes with word timestamps → Burns karaoke-style captions → video_captioned.mp4

User: "Add word captions, appear style, top position"
Claude: python3 scripts/caption_video.py video.mp4 --style=appear --position=top
```

## Performance

- **Transcription**: ~3 seconds for 1-minute video (Groq Whisper)
- **Translation**: ~10 seconds for 14 segments (EnConvo API)
- **TTS Generation**: ~30-60 seconds for 1-minute video (segment-by-segment)
- **Video Export**: ~10-30 seconds (re-encode for burned-in subtitles)

**Total**: ~1-2 minutes for 1-minute video

## Troubleshooting

### Groq API Error
```
Error: GROQ_API_KEY not provided
```
**Fix**: Get free API key from [console.groq.com](https://console.groq.com) (needed for Whisper ASR). Translation uses EnConvo API (localhost:54535).

### YouTube Download Error
```
Error downloading video
```
**Fix**: Update yt-dlp: `pip install -U yt-dlp`

### Kokoro Import Error
```
ModuleNotFoundError: No module named 'kokoro'
```
**Fix**: Skill falls back to edge-tts automatically for Chinese

## Notes

- All modes start with transcription (Groq Whisper ASR)
- Translation via EnConvo API (natural, context-aware phrasing)
- Transcript cleanup removes filler words before translation
- Dubbing includes perfect audio-subtitle sync (segment-by-segment)
- **Burns in dual subtitles** (original top/yellow + translated bottom/white, always visible)
- Summaries are comprehensive but concise

## License

MIT License - Free to use and modify
