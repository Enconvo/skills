---
name: video-processor
version: 1.0.0
author: zanearcher
category: media
description: "Comprehensive media processing: transcribe, translate, summarize, and dub videos/audio with professional TTS. Supports local files (MP4, MP3, WAV, M4A, etc.) and URLs (YouTube, Twitter, TikTok, 1000+ sites). Use when user says /video-transcribe, /video-translate, /video-dub, /video-summary, or asks to transcribe, translate, dub, or summarize any video/audio."
user_invocable: true
---

# Video/Audio Processor Skill

Comprehensive media processing: transcribe, translate, summarize, and dub videos/audio with professional TTS.

**Supports:**
- 🎬 **Video files**: MP4, MKV, AVI, MOV, WebM, FLV
- 🎵 **Audio files**: MP3, M4A, WAV, FLAC, OGG, AAC
- 🌐 **URLs**: YouTube, Twitter/X, TikTok, Instagram, and 1000+ sites via yt-dlp

## Activation

Use this skill when the user:
- Says `/video-transcribe`, `/video-translate`, `/video-dub`, or `/video-summary`
- Asks to "transcribe this video"
- Wants to "translate and dub a video"
- Needs "video summary" or "summarize this video"
- Requests "extract transcript from video"
- Asks in ANY language (e.g., "总结这段视频", "résumez cette vidéo", "resume este video")

**Language Detection:**
- Automatically detects the language of the user's request
- Generates output in the same language as the request
- Example: "总结这段视频" → Summary in Chinese
- Example: "summarize this video" → Summary in English
- Can be overridden with explicit language parameter

## Modes

### 1. Transcription Only
Extract transcript with timestamps from video.

**Triggers:** `/video-transcribe`, "transcribe this video"

**Output:**
- `{video_name}_transcript.srt` - Transcript with timestamps
- `{video_name}_transcript.txt` - Plain text transcript

### 2. Translation
Transcribe + translate to target language (no TTS, subtitles only).

**Triggers:** `/video-translate`, "translate this video to {lang}"

**Output:**
- `{video_name}_original.srt` - Original transcript
- `{video_name}_{target_lang}.srt` - Translated subtitles
- Side-by-side review before saving

### 3. Dubbing (Full Pipeline)
Transcribe, translate, review, TTS, create dubbed video.

**Triggers:** `/video-dub`, "dub this video to {lang}"

**Output:**
- `{video_name}_original.srt` - Original transcript
- `{video_name}_{target_lang}.srt` - Translated subtitles
- `{video_name}_{target_lang}_audio.wav` - Synced TTS audio (intermediate, cleaned up after muxing)
- `{video_name}_dubbed.mp4` - Final dubbed video with dual subs

### 4. Summary
Transcribe video and generate comprehensive summary.

**Triggers:**
- `/video-summary`, "summarize this video" (English)
- "总结这段视频" (Chinese)
- "résumez cette vidéo" (French)
- "resume este video" (Spanish)
- Any natural language request

**Output:**
- `{video_name}_summary.md` - Comprehensive summary:
  - Overview (2-3 sentences)
  - Key points (bullet list)
  - Detailed summary
  - Important timestamps
  - Action items (if applicable)

**Language Detection (Automatic):**
- Detects request language and generates summary in that language
- "What's this video about?" → English summary
- "总结这段视频" → Chinese summary
- "这个视频讲什么？" → Chinese summary
- Can override with explicit parameter: `/video-summary video.mp4 spanish`

## Parameters

- `input` (required): Path to video/audio file OR URL
  - Local: `video.mp4`, `audio.mp3`, `podcast.m4a`
  - URL: `https://youtube.com/watch?v=xxx`, `https://twitter.com/user/status/xxx`
- `target_lang` (optional): Target language (chinese, spanish, french, etc.)
- `groq_api_key` (optional): Groq API key (will prompt if not in env)

## Features

- ✅ **Audio + Video support** (MP4, MP3, WAV, M4A, and more)
- ✅ **URL download** (YouTube, Twitter, TikTok, 1000+ sites)
- ✅ Ultra-fast transcription (Groq Whisper Large V3)
- ✅ Natural translation (context-aware, preserves technical terms)
- ✅ **Segment-by-segment TTS** (precise timing per subtitle)
- ✅ **Smart condensation** (shortens overlong translations instead of speeding up audio)
- ✅ **Perfect audio sync** (natural speed with conservative adjustment)
- ✅ **Voice cloning support** (use any voicebox profile)
- ✅ Translation review (edit before TTS generation)
- ✅ **Auto subtitle embedding** (always adds original language subs)
- ✅ Dual subtitle support (original + translated)
- ✅ Multi-language TTS (Kokoro + edge-tts + voicebox)
- ✅ Intelligent summaries (with timestamps and key points)
- ✅ **Language-aware detection** (auto-detects request language)

## Requirements

### Required
- **ffmpeg** (video/audio processing): `brew install ffmpeg`
- **yt-dlp** (URL downloads): `brew install yt-dlp`
- **Groq API key** (transcription & translation): Free at [console.groq.com](https://console.groq.com)
  - Uses Whisper Large V3 for ASR — fast, free, supports SRT output, stable for long videos
  - Set: `export GROQ_API_KEY=gsk_xxx` or add to `.env` file in skill root
- **edge-tts** (default TTS engine): `pip install edge-tts`
- **Python packages**: `pip install groq numpy soundfile`

### Optional TTS Engines

**Kokoro** (local, offline, no internet needed):
- Fast local TTS, supports English/Chinese/Japanese + more
- Install: `conda create -n kokoro python=3.10 && conda activate kokoro && pip install kokoro soundfile numpy`
- If not installed, the skill automatically falls back to edge-tts

**Voicebox** (voice cloning & design):
- Install from: [github.com/EnConvo/skill/tree/main/curated/voicebox](https://github.com/EnConvo/skill/tree/main/curated/voicebox)
- Supports three voice profile types:
  - **Qwen-TTS Clone**: Cloned from reference audio (e.g., celebrity voice)
  - **Descriptional Designed**: Designed from text description (e.g., "calm male narrator")
  - **Custom_Voice**: Preset voice profiles with customizable emotions
- **Important**: Voicebox is best for short videos (1-5 minutes). For long videos (30+ min), voicebox generates segments sequentially which takes too long — use edge-tts instead (parallel generation, much faster)
- If not installed, the skill automatically falls back to edge-tts with a helpful install guide

## Example Sessions

**Transcription (Video/Audio/URL):**
```
User: "Transcribe this video"
Claude: Extracts transcript → video_transcript.srt + video_transcript.txt

User: "Transcribe podcast.mp3"
Claude: Extracts audio transcript → podcast_transcript.srt + podcast_transcript.txt

User: "Transcribe https://youtube.com/watch?v=xxx"
Claude: Downloads video → Transcribes → transcript files
```

**Summary (Language-Aware):**
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

**Dubbing (Audio Support):**
```
User: "Dub this to Chinese"
Claude: Transcribe → Translate → Review → TTS → Dubbed video

User: "把这个音频配音成中文" (podcast.mp3)
Claude: Transcribe audio → Translate to Chinese → Review → TTS

User: "Dub this YouTube video to Spanish: https://youtube.com/watch?v=xxx"
Claude: Downloads → Transcribes → Translates → TTS → Dubbed video
```

## Technical Details

### Segment-by-Segment TTS Processing

The dubbing system uses a 4-step pipeline that scales to 1500+ segments:

1. **TTS Generation** - Each subtitle entry becomes a separate TTS audio file
   - **edge-tts**: Async parallel generation in batches of 10 (fastest for large files)
   - **Kokoro**: Single-process batch generation via KPipeline
   - **voicebox**: Sequential generation with voice cloning
2. **Smart Condensation** - Measures each TTS segment's actual duration against its SRT time
   window. Segments exceeding 1.3x their target duration get their translation condensed
   via Groq LLM (shorter text preserving core meaning), then TTS is regenerated for those
   segments. Up to 2 condensation passes. This eliminates the need for extreme speed
   adjustment that made dubbed audio sound unnatural.
3. **Speed Adjustment** - Conservative tempo tuning for remaining timing mismatches
   - **Never slows down** — audio shorter than its window plays at natural speed (silence fills gaps)
   - **Mild speedup only** — capped at 2.0x via single ffmpeg `atempo` filter (rare after condensation)
   - Most segments need no adjustment after condensation
4. **Numpy Timeline Assembly** - Places each adjusted segment at its exact SRT start position
   in a pre-allocated numpy array. Scales to any number of segments without ffmpeg input limits.
5. **Video Mux** - Uses `-c:v copy` (no re-encode) + soft subtitle tracks for speed

**Performance (tested on 2h22m video, 1,554 segments):**
- edge-tts TTS generation: ~12 min (parallel batches of 10)
- Smart condensation: ~30-60s (only for segments that need it)
- Speed adjustment: ~48s
- Numpy timeline assembly: ~1.3s
- Video muxing: ~43s
- **Total: ~14-15 min for a 2h22m video**

**Benefits:**
- Natural-sounding audio (no slow-motion or chipmunk effect)
- Scales to 1500+ segments (numpy, not ffmpeg amix)
- edge-tts parallel batches for 10x faster generation
- No video re-encoding (`-c:v copy`)
- Soft subtitle tracks (toggle in player)
- Resume support (skips already-generated segments)

### TTS Engine Selection

**Default: edge-tts** — Used automatically unless the user explicitly requests otherwise.
- Male default: `en-US-BrianMultilingualNeural` (Brian Multilingual) — handles all languages natively
- Female default: `en-US-EmmaMultilingualNeural` (Emma Multilingual) — handles all languages natively
- Chinese male override: `zh-CN-YunxiNeural` (dedicated Chinese voice, better for Chinese dubbing)
- If user doesn't specify gender, default to Brian Multilingual (Male)
- Full voice list: `edge-tts --list-voices`

**Kokoro (local, no internet)** — Only used when the user explicitly asks for Kokoro.
- Trigger phrases: "use Kokoro", "use local TTS", "offline TTS"
- English: `am_michael`, `am_adam`, `af_heart`
- Chinese: `zf_001` (and 100+ Chinese voices)

**Voicebox (voice cloning/design)** — Used when the user requests a specific voice persona, cloned voice, or voice description.

**Install:** [github.com/EnConvo/skill/tree/main/curated/voicebox](https://github.com/EnConvo/skill/tree/main/curated/voicebox)
If not installed, the skill prints the install URL and falls back to edge-tts automatically.

**Duration caveat:** Voicebox generates segments sequentially (voice cloning is compute-intensive).
Best for short videos (1-5 minutes). For long videos (30+ min), it takes too long and makes no practical sense — use edge-tts instead.

**Three voice profile types:**

| Type | Description | Example |
|------|-------------|---------|
| **Qwen-TTS Clone** | Cloned from reference audio | Celebrity voice, your own voice |
| **Descriptional Designed** | Designed from text description | "calm male narrator", "energetic female host" |
| **Custom_Voice** | Preset profiles with customizable emotions | Adjust pitch, speed, emotion per profile |

**Profile lookup:** Voicebox stores all profiles in `~/.claude/skills/voicebox/data/profiles.json`.
Each profile has a `name`, `type` ("cloned" or "designed"), and `language`.
- List all profiles: `uv run ~/.claude/skills/voicebox/scripts/voicebox.py list`
- Lookup is case-insensitive with substring fallback (e.g., "trump" matches "Trump", "panic" matches "Panic Granny")

**Scenario A: Cloned voice** — User asks for a known cloned voice (e.g., "use Trump's voice")
- Run `voicebox.py list` to find the existing clone profile by name
- If found (type: "cloned") → use it directly for TTS
- Example: "Dub this video using Trump's voice" → lookup "Trump" → finds cloned profile → TTS with it

**Scenario B: Named designed voice** — User asks for a named voice persona (e.g., "use Panic Granny voice")
- Run `voicebox.py list` to search for an existing designed profile by name
- If found → use it for TTS
- If not found → invoke voicebox skill to design the voice profile first, then use it for TTS
- Example: "Dub this using Panic Granny voice" → lookup "Panic Granny" → found (type: "designed") → TTS with it

**Scenario C: Voice description** — User describes voice characteristics (e.g., "a male mid-aged calm narrator")
- Invoke voicebox skill to design a new voice profile matching the description
- Then use the newly created profile for TTS
- Example: "Dub this with a calm male narrator" → voicebox designs voice with those traits → saves profile → TTS with it

```bash
# Dub with a cloned/designed voice profile
generate_tts_and_dub.sh video.mp4 original.srt translated.srt chinese "Trump"
```

**Selection logic summary:**
1. User names a cloned voice → **voicebox** (find clone profile → TTS)
2. User names a voice persona → **voicebox** (find or design profile → TTS)
3. User describes voice traits → **voicebox** (design profile → TTS)
4. User explicitly asks for Kokoro → **Kokoro** (falls back to edge-tts if not installed)
5. Everything else → **edge-tts** (Brian Multilingual male / Emma Multilingual female)

### Same-Language Re-voicing

The dubbing pipeline supports re-voicing in the same language (no translation needed).
Use the original SRT as both the original and translated SRT:
```bash
generate_tts_and_dub.sh video.mp4 transcript.srt transcript.srt english none en-US-BrianMultilingualNeural
```

## Notes

- All modes start with transcription
- Translation uses natural phrasing (not machine translation)
- Dubbing includes perfect audio-subtitle sync (segment-by-segment)
- **Always embeds original language subtitles** in output video (soft subs)
- Summaries are comprehensive but concise
- Original video quality is preserved (`-c:v copy`, no re-encode)
- Long videos (1000+ segments) handled efficiently via numpy timeline
