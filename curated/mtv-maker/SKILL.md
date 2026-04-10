---
name: mtv-maker
version: 2.1.0
description: >-
  Full end-to-end MTV music video creator. From a song concept and optional character reference
  photo, produces a complete cinematic MTV: (1) writes lyrics and generates music with ACE-Step,
  (2) generates cinematic scene images, (3) animates with I2V (Grok/Seedance),
  (4) assembles clips with audio and crossfade transitions,
  (5) transcribes audio for accurate lyric timing, (6) burns synced lyric subtitles +
  opening/ending credits with branding.
  Use when user says "make an MTV", "create a music video", "generate MTV", "/mtv", or describes
  a song they want turned into a full visual music video.
---

# MTV Maker v2 — I2V Pipeline

End-to-end pipeline: song concept + character photo → music (ACE-Step) → scene images (image_to_image) → I2V video clips (Grok/Seedance) → assembled MTV with synced bilingual lyrics + credits.

## Inputs

The user provides:
1. **Song concept** — genre, mood, style, voice, language, any reference artist/style
2. **Character reference photo** (optional) — used for `image_to_image` to generate consistent scene photos. If none provided, generate original scene images with `text_to_image`.
3. **MTV length preference** — full song or chorus-only clip (default: 30-45s chorus clip)

## Pipeline Mode

**ALWAYS use I2V (image-to-video)**. NEVER use Ken Burns for MTV production — it looks cheap and static. Every scene must have real AI-generated motion.

| Mode | Description | Time | Quality |
|------|-------------|------|---------|
| **Photo + I2V** | Photos animated by Grok or Seedance AI | ~45 min | Cinematic |

## Phase Overview

| Phase | What | Tool/Skill | Output |
|-------|------|------------|--------|
| 1 | Song creation | `acestep` skill | Full MP3 |
| 2 | Chorus extraction | ffmpeg | Trimmed MP3 clip |
| 3 | Scene image generation | `image_to_image` or `text_to_image` | 6 cinematic photos (16:9) |
| 4 | **I2V animation** | `grok-video-gen` or `seedance-api` | 6 video clips (~5-6s each) |
| 5 | Video assembly + audio | ffmpeg xfade | Raw MTV with music |
| 6 | Lyric transcription | `video-processor` (Groq Whisper) or manual | SRT with timestamps |
| 7 | Caption burn + credits | ffmpeg + ASS subtitles | Final MTV |

---

## Phase 1: Song Planning & Generation

Use the `acestep` skill (which in turn uses `acestep-songwriting` for lyric craft).

### Workflow
1. **Plan the song** — decide genre, BPM, key, duration, vocal style, lyric theme
2. **Write complete lyrics** — structured with `[Intro]`, `[Verse]`, `[Chorus]`, `[Bridge]`, `[Outro]` tags
3. **Generate with ACE-Step** — always `--batch 2` for two versions
4. **User picks preferred version**

### Key Parameters
- Full song: 150-200s duration
- Chorus clip: user selects the best ~30-45s segment after listening
- Always generate 2 versions for A/B comparison

### Output
- `{song_name}_v1.mp3`, `{song_name}_v2.mp3`

---

## Phase 2: Chorus Extraction

After user picks a version and specifies the time range:

```bash
# CRITICAL: Use -ss BEFORE -i for accurate MP3 seeking
ffmpeg -y -ss {START} -i "{full_song}.mp3" -t {DURATION} \
  -af "afade=t=in:st=0:d=2,afade=t=out:st={DURATION-2}:d=2" \
  -b:a 192k \
  "{song_name}_chorus.mp3"
```

**CRITICAL BUG FIX**: When trimming MP3 files, always place `-ss` BEFORE `-i` (input seeking). Placing `-ss` after `-i` causes silent output due to MP3 frame boundary issues. This was a hard-won lesson.

### Verification
```bash
# Always verify the trimmed clip is not silent
ffmpeg -i "{song_name}_chorus.mp3" -af "volumedetect" -f null - 2>&1 | grep mean_volume
# mean_volume should be between -30 dB and 0 dB. If < -80 dB, it's silent — redo the trim.
```

---

## Phase 3: Scene Image Generation (6 Images)

### Planning the Visual Storyboard

Design 6 scenes that follow an **emotional arc** matching the lyrics. Each scene should:
- Correspond to a specific lyric section
- Progress the emotional narrative (e.g., intimacy → heartbreak → acceptance)
- Vary in composition: mix close-ups, medium shots, and wide shots
- Build from intimate/close to distant/wide for a "proximity to distance" narrative arc

### Storyboard Template

| # | Lyric Section | Scene Description | Emotion | Shot Type |
|---|---------------|-------------------|---------|-----------|
| 1 | Opening line | [setting + character + action] | [emotion] | Close-up / Medium |
| 2 | Next section | ... | ... | Medium |
| 3 | Building tension | ... | ... | Medium |
| 4 | Emotional peak | ... | ... | Close-up / Medium |
| 5 | Bridge/reflection | ... | ... | Medium / Wide |
| 6 | Final line | ... | ... | Wide / Silhouette |

### Image Generation Rules

**With character reference photo** (typical case):
- Use `image_to_image` tool with the reference photo
- Prompt must be cinematic — think Wong Kar-wai, Sofia Coppola, Fincher
- 16:9 aspect ratio, 2K resolution minimum
- **FACE MUST BE LARGE AND CLEAR** — use medium or medium-close shots so face fills at least 15-20% of the frame. If the face is too small (full-body wide shot), I2V will lose facial identity mid-generation, causing cross-eyes, morphing, or identity drift. This is the #1 cause of bad I2V output.
- **Face must be front-facing or 3/4 angle** — the image will be used as I2V reference, so face stability matters
- **NO accessories that clash with the mood** — match props to MTV emotion
- Lighting should be dramatic and atmospheric: neon reflections, candlelight, moonlight, golden hour, rain

**Without character reference** (abstract/scenic MTV):
- Use `text_to_image` tool
- Same cinematic quality requirements

### Image Prompt Structure

```
Cinematic [shot type] of [character description] in [setting].
[Emotional atmosphere description]. [Lighting description].
[Character pose/action — must be subtle, not posed].
16:9 widescreen composition, shallow depth of field, film grain,
[color palette]. Shot on Arri Alexa Mini, anamorphic lens flare.
```

### DO NOTs for Images
- NO stiff poses — character should look natural, candid
- NO cluttered backgrounds — MTV scenes need clean, atmospheric backdrops
- NO bright/cheerful lighting for sad songs (match mood!)
- NO tiny figures lost in the frame — character should be clearly visible
- Face must be recognizable for I2V consistency

### Naming Convention
- `mtv_photo_01_{scene_keyword}.jpg` through `mtv_photo_06_{scene_keyword}.jpg`

### User Approval Flow
Show images **one by one** for approval. If user says "do it on your own" or similar, generate all 6 autonomously using the storyboard plan.

---

## Phase 4a: Ken Burns Animation (Default — Photo Mode)

Convert each still photo into a ~7s cinematic clip using ffmpeg `zoompan`. This is fast, reliable, and looks great for emotional/melancholy MTVs.

### Ken Burns Presets

Vary the motion per scene for visual interest:

| Scene | Motion | ffmpeg filter |
|-------|--------|---------------|
| 1 | Slow zoom in | `zoompan=z='min(zoom+0.0015,1.5)':d=168:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'` |
| 2 | Pan left→right | `zoompan=z='1.3':d=168:x='iw*0.1+iw*0.4*(on/168)':y='ih/2-(ih/zoom/2)'` |
| 3 | Slow zoom out | `zoompan=z='max(zoom-0.0015,1.0)':d=168:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'` |
| 4 | Pan right→left | `zoompan=z='1.3':d=168:x='iw*0.5-iw*0.4*(on/168)':y='ih/2-(ih/zoom/2)'` |
| 5 | Zoom in + pan up | `zoompan=z='min(zoom+0.001,1.4)':d=168:x='iw/2-(iw/zoom/2)':y='ih*0.6-(ih/zoom/2)'` |
| 6 | Static + fade | `zoompan=z='1.2':d=168:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'` |

### Command Template

```bash
# d=168 = 7 seconds at 24fps. Adjust per desired clip length.
ffmpeg -y -loop 1 -i "{photo}.jpg" \
  -vf "zoompan=z='min(zoom+0.0015,1.5)':d=168:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)',scale=1920:1080" \
  -r 24 -t 7 -c:v libx264 -preset fast -crf 20 \
  "mtv_video_01_{keyword}.mp4"
```

**Important**: `-loop 1` is required for still images. Output must be at least as long as needed for the assembled MTV.

---

## Phase 4b: I2V Video Generation (Optional — Animated Mode)

### Tool Selection

**Primary: `grok-video-gen` skill** (recommended default)
- Fast, free, good motion quality
- Output: ~752×416 (will be upscaled in Phase 5)
- Use `--video --aspect 16:9 -r {photo_path}` flags

**Alternate: `seedance-api` skill**
- Higher resolution, better face consistency
- Output: native 1280×720
- Slower (1-4 min per clip)
- Use `--ref-image {photo_path} --duration 5`

### I2V Prompt Guidelines

**Every I2V prompt must carry the emotional DNA of the ENTIRE storyboard**, not just describe one scene in isolation. If the MTV is about heartbreak, every prompt should breathe heartbreak — the grief, the stillness, the loss.

**Motion must match the MTV mood:**

| MTV Mood | Motion Style | Example Prompt |
|----------|-------------|----------------|
| Sad/melancholy | Slow, subtle, minimal | "Subtle breathing, slight head tilt, wind gently moves hair, slow blink" |
| Energetic/upbeat | Dynamic, expressive | "Dancing, spinning, arms moving, hair flowing with movement" |
| Reflective/nostalgic | Medium, contemplative | "Slowly walking, looking around, hand touches surface gently" |
| Dramatic/powerful | Bold, sweeping | "Turns toward camera, dramatic wind, fabric flowing, strong pose" |

**Critical I2V Rules:**
- **SLOW motion for sad songs** — no fast walking, no catwalk strut
- **Maintain distance** — if camera is too close, face degrades. For walking scenes, camera tracks backward to maintain distance
- **Describe motion, not appearance** — I2V inherits appearance from the photo. Focus prompt on WHAT MOVES and HOW
- **Camera movement matters** — specify: "camera slowly tracks backward", "camera static", "slight camera drift to the right"
- **Match motion to storyboard context** — if the storyboard calls for stillness, prompt for stillness; if it calls for singing, let her sing. The storyboard is the source of truth for what each scene's motion should be

### Gacha Management (CRITICAL)

I2V is probabilistic. The same prompt can produce wildly different results. Follow this workflow:

1. **Generate raw I2V clip**
2. **Show raw clip to user for review BEFORE assembly** — never assemble blindly
3. **Common I2V artifacts to watch for:**
   - Character starts talking/moving lips (most common)
   - Eyes cross or drift mid-clip (caused by small face in reference)
   - Purposeful gazing instead of vacant stare
   - Unnatural head movement or body distortion
4. **If rejected, regenerate** — keep previous take as backup (sometimes the next roll is worse)
5. **Only proceed to assembly after all 6 clips are approved**
6. **Iterate on the weakest link** — don't redo everything, identify the one scene breaking coherence and fix just that

### Grok I2V Command
```bash
SKILL_DIR="/Users/zanearcher/.claude/skills/grok-video-gen"
npx -y bun ${SKILL_DIR}/scripts/main.ts --video \
  -r "{photo_path}" \
  --aspect 16:9 \
  "{motion_prompt}" \
  --output "{output_path}" \
  --timeout 600
```

### Seedance I2V Command
```bash
python3 ~/.claude/skills/seedance-api/scripts/seedance_worker.py \
  --prompt "{motion_prompt}" \
  --ref-image "{photo_path}" \
  --duration 5 \
  --output-dir "{session_dir}"
```

### Naming Convention
- `mtv_video_01_{scene_keyword}.mp4` through `mtv_video_06_{scene_keyword}.mp4`

---

## Phase 5: Video Assembly

### Step 1: Upscale & Slow Down Clips

Grok outputs ~752×416. Upscale to 1920×1080 and apply 0.75x slowdown for cinematic feel:

```bash
for i in 01 02 03 04 05 06; do
  ffmpeg -y -i "mtv_video_${i}_*.mp4" \
    -vf "setpts=1.33*PTS,scale=1920:1080:flags=lanczos" \
    -r 24 -c:v libx264 -preset fast -crf 20 \
    "clip_${i}_upscaled.mp4"
done
```

If using Seedance (1280×720), still upscale to 1920×1080 but skip the slowdown unless desired:
```bash
ffmpeg -y -i input.mp4 \
  -vf "scale=1920:1080:flags=lanczos" \
  -r 24 -c:v libx264 -preset fast -crf 20 \
  output_upscaled.mp4
```

### Step 2: Check Clip Durations
```bash
for f in clip_*_upscaled.mp4; do
  echo "$f: $(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$f")s"
done
```

### Step 3: Crossfade Assembly

Calculate total duration: `N clips × avg_clip_duration - (N-1) × crossfade_duration`

Target: match audio clip duration. Adjust clip speed or add/remove clips as needed.

```bash
# 6 clips with 1-second crossfade transitions
ffmpeg -y \
  -i clip_01_upscaled.mp4 \
  -i clip_02_upscaled.mp4 \
  -i clip_03_upscaled.mp4 \
  -i clip_04_upscaled.mp4 \
  -i clip_05_upscaled.mp4 \
  -i clip_06_upscaled.mp4 \
  -filter_complex "
    [0:v][1:v]xfade=transition=fade:duration=1:offset={OFF1}[v1];
    [v1][2:v]xfade=transition=fade:duration=1:offset={OFF2}[v2];
    [v2][3:v]xfade=transition=fade:duration=1:offset={OFF3}[v3];
    [v3][4:v]xfade=transition=fade:duration=1:offset={OFF4}[v4];
    [v4][5:v]xfade=transition=fade:duration=1:offset={OFF5}[v5];
    [v5]fade=t=in:st=0:d=2,fade=t=out:st={TOTAL-2}:d=2[vout]
  " \
  -map "[vout]" -c:v libx264 -preset fast -crf 20 -r 24 \
  "mtv_video_assembled.mp4"
```

**Offset calculation:**
- `OFF1` = duration_of_clip1 - 1
- `OFF2` = OFF1 + duration_of_clip2 - 1
- `OFF3` = OFF2 + duration_of_clip3 - 1
- ... and so on

### Step 4: Add Audio

```bash
ffmpeg -y -i mtv_video_assembled.mp4 -i "{chorus_clip}.mp3" \
  -c:v copy -c:a aac -b:a 192k \
  -shortest \
  "mtv_with_audio.mp4"
```

This produces the **clean base video** — never burn captions onto a previously captioned video.

---

## Phase 6: Lyric Timing via Transcription

### Method 1: Groq Whisper (Recommended)

Use the `video-processor` skill's transcriber to get accurate timestamps:

```bash
GROQ_API_KEY="{key}" python3 ~/.claude/skills/video-processor/scripts/transcriber.py \
  "{chorus_clip}.mp3"
```

This outputs `{name}_original.srt` with segment timestamps.

### Method 2: Manual Mapping

If transcription is unavailable or inaccurate (common with sung Chinese), manually map known lyrics to approximate timestamps by:
1. Dividing the audio duration by number of lyric lines
2. Adjusting based on musical structure (verses vs chorus timing)

### Why ASR Is Mandatory (Never Use Input Lyrics as Captions)

**CRITICAL**: The lyrics you feed into ACE-Step are a *prompt*, not a transcript. The AI model interprets them loosely — it may rearrange words, skip lines, change phrasing, add ad-libs, or alter sentence structure. The generated song's actual vocals will often differ from the input lyrics.

**Therefore: NEVER use the ACE-Step input lyrics directly as captions.** Always run ASR (Groq Whisper) on the final generated audio to transcribe what was *actually sung*. This gives you:
1. **Accurate timestamps** — synced to the real audio
2. **Actual phrasing** — what the model actually sang, not what you asked it to sing

### Lyrics Correction After ASR (MANDATORY)

Whisper will misrecognize some sung words (especially names, slang, or stylized delivery). After transcription:
1. Read the Whisper output (words JSON or SRT)
2. **Listen to the audio** and compare — fix obvious mishears (e.g., "y'all" → "Yao", "undecided" → "sends it")
3. Keep all timestamps intact — Whisper timing is accurate even when text recognition is wrong
4. The corrected words JSON becomes the source of truth for caption generation

### Caption Line Breaking (CRITICAL)

**Each caption line MUST be one complete, meaningful sentence.** Never break mid-sentence.

The `caption_video.py` script now uses Whisper segment boundaries for line grouping (segments = natural sentence breaks). But when manually building ASS files, follow these rules:

| DO | DON'T |
|----|-------|
| "Chalk on her hands and fire in her eyes" | "her eyes Edge of the" |
| "Edge of the mountain touching the sky" | "the sky First time hanging but" |
| "Teresa Yao don't mess around" | "around SHE SENDS IT no" |

Each lyric line should appear and disappear as a complete unit. Analyze lyrics grammatically — identify sentence boundaries, not arbitrary word counts.

### Caption Font & Styling (MTV Standard)

- **Font**: Impact or Bebas Neue — thick, bold, high-contrast. NOT thin fonts like PingFang SC or Helvetica Neue.
- **Size**: 50-56pt minimum for 1280x720, 70-80pt for 1920x1080. Captions must be readable at a glance.
- **Outline**: 3-4px black outline + 1-2px drop shadow for legibility on any background.
- **Chorus lines**: Use a distinct style (larger font, different color like gold/cyan) to differentiate from verses.

### Outro Best Practices

- **Pure black background** — not a video frame.
- **Fade in/out** — all text must animate in and out. Never snap on/off.
- **Differentiate credits** from title text:
  - Title ("SHE SENDS IT"): large, white, bold.
  - Attribution labels ("Credit to", "Powered by"): small, grey, subtle.
  - Names ("Mavis", "EnConvo"): medium, distinct color (gold, cyan), bold — visually separate from the title above.
  - Stagger fade-in timing: title first, credits delayed by 0.5-1s.

### Crossfade Transitions

Always use crossfade between intro→main and main→outro. 1s fade duration is standard. Use ffmpeg `xfade=transition=fade:duration=1:offset=X`.

---

## Phase 7: Captions & Credits (ASS Format)

### ASS File Structure

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

### Caption Layout

**Bilingual lyrics** (default):
- **Chinese (LyricCN)**: 56pt Noto Serif TC, white with dark outline + shadow, bottom-center
- **English (LyricEN)**: 32pt PingFang SC italic, semi-transparent white, below Chinese line
- Both use `\fad(800,600)` for smooth transitions

**Title card** (dedicated black frames, first 5-6 seconds):
- Title card MUST be on dedicated black frames, NOT overlaid on video content
- Song title: 100-120pt bold uppercase, centered, `\fad(2000,1200)`
- Artist/brand credit below: 48pt regular weight, `\fad(1500,1000)`
- Give the title card breathing room — at least 5-6 seconds
- Format: `{Artist Name}` on one line, `EnConvo` on next

**End credits** (on black frames, last 6+ seconds):
- Main credit: 62pt bold, `词 · 曲 · 演唱 {Artist}`
- Brand line: 42pt, `Powered by EnConvo`
- Both use `\fad(1500,3000)` — long 3-second fade-out
- **Must last at least 6 seconds** and extend to the final frame

### Timing Rules (CRITICAL)

| Element | When | Rule |
|---------|------|------|
| Title + OpenCredit | 0:00 - 0:04.5 | Must fade out COMPLETELY before first lyric |
| LyricCN + LyricEN | Synced to audio | NO credits visible during lyrics |
| EndCredit + Brand | Black frames only | Start at `song_end + 1.5s`, end at final frame |

### Black Frame Ending

Append 8 seconds of black frames + fade audio out 2s before song ends:

```bash
SONG_DUR=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 mtv_with_audio.mp4)
FADE_START=$(echo "$SONG_DUR - 2" | bc)
SOURCE_FPS=24  # MUST match source video fps

# Fade audio
ffmpeg -y -i mtv_with_audio.mp4 \
  -af "afade=t=out:st=${FADE_START}:d=2" \
  -vn -c:a aac -b:a 192k audio_faded.m4a

# Extend video with black frames (SAME FPS as source!)
ffmpeg -y \
  -i mtv_with_audio.mp4 \
  -f lavfi -i "color=black:s=1920x1080:r=${SOURCE_FPS}" \
  -filter_complex "[0:v][1:v]concat=n=2:v=1:a=0[outv]" \
  -map "[outv]" -c:v libx264 -preset fast -crf 20 -r ${SOURCE_FPS} \
  -t $(echo "$SONG_DUR + 8" | bc) video_extended.mp4

# Extend audio with silence
ffmpeg -y \
  -i audio_faded.m4a \
  -f lavfi -i "anullsrc=r=48000:cl=stereo" \
  -filter_complex "[0:a][1:a]concat=n=2:v=0:a=1[outa]" \
  -map "[outa]" -t $(echo "$SONG_DUR + 8" | bc) -c:a aac -b:a 192k audio_full.m4a

# Mux clean (no captions yet)
ffmpeg -y -i video_extended.mp4 -i audio_full.m4a \
  -c:v copy -c:a copy -shortest muxed_clean.mp4
```

**CRITICAL**: Black frame fps MUST match source video fps. Mismatch causes wrong duration.

### Final Burn (LAST STEP)

```bash
ffmpeg -y -i muxed_clean.mp4 \
  -vf "ass=captions.ass" \
  -c:v libx264 -preset fast -crf 18 \
  -c:a copy \
  "{SongTitle}_MTV_final.mp4"
```

**NEVER burn captions onto a previously captioned video** — captions stack and become unreadable. Always burn onto the clean source.

---

## Common Pitfalls & Lessons Learned

| Problem | Cause | Fix |
|---------|-------|-----|
| Trimmed MP3 is silent | `-ss` placed after `-i` | Put `-ss` BEFORE `-i` for input seeking |
| Face degrades in I2V | Camera too close, or fast motion | Keep distance, slow motion, camera tracks backward |
| Cross-eyed / identity drift in I2V | Face too small in reference photo | Use medium-close shots, face must fill 15-20% of frame |
| I2V motion doesn't match vibe | Prompt describes generic motion, not storyboard emotion | Every I2V prompt must carry the emotional DNA of the whole storyboard |
| Lyrics too bold/heavy | Bold weight + thick outline | Use regular weight (not bold) for elegance, 3px outline max |
| I2V looks like a fashion show | Prompt describes appearance, not motion | Focus on subtle motion: breathing, wind, slow turn |
| Catwalk walk in sad MTV | Default I2V motion is energetic | Explicitly prompt: "slow defeated walk", "subtle movement" |
| Subtitle timing wrong | Whisper misrecognizes sung lyrics | Keep Whisper timestamps, replace text with correct lyrics |
| Credits overlap lyrics | ASS timing miscalculation | Verify: OpenCredit fades out before first lyric line |
| Double captions | Burned onto already-burned video | Always use clean (no-caption) source for final burn |
| Framerate mismatch in concat | Black frames at 30fps, source at 24fps | Check source fps with ffprobe, match exactly |
| Video too large for sharing | High bitrate + long duration | Use `-crf 20` for clips, `-crf 18` for final |
| Ken Burns motion jerky | zoompan fps mismatch | Always set `-r 24` on output and `d=` to match: d=fps×seconds |
| Ken Burns black borders | Image resolution too small | Use images ≥1920×1080; add `scale=1920:1080` before zoompan |
| Caption breaks mid-sentence | Line grouping by word count, not meaning | Use Whisper segments for line breaks; manually verify each line is a complete phrase |
| Captions too thin/small | Using PingFang SC or Helvetica at small size | Use Impact or Bebas Neue at 50pt+ with 3-4px outline |
| Outro text snaps on/off | No fade animation on drawtext | Use ffmpeg `alpha` expression for fade in/out on every text element |
| Credits blend with title | Same font/color/size for everything | Differentiate: title=white/large, labels=grey/small, names=gold or cyan/medium |
| Captions don't match audio | Used ACE-Step input lyrics as captions | ACE-Step interprets lyrics loosely — always ASR the final audio with Groq Whisper, then correct mishears |

---

## Delivery

1. Save final MTV in session directory
2. Present with `Deliverable` tool
3. Optionally send via Telegram using `im_channels/telegram_actions/reply` with `files` array
4. Caption with song title

---

## Quick Reference: Full Command Sequence

```
1. acestep skill → generate song (2 versions)
2. User picks version + time range
3. ffmpeg -ss BEFORE -i → trim chorus with fade in/out
4. ffmpeg volumedetect → verify not silent
5. image_to_image × 6 → cinematic scene photos (16:9, 2K+)

--- I2V MODE (always) ---
6. grok-video-gen --video × 6 → I2V clips (review each raw clip before proceeding!)
7. ffmpeg upscale + slow → 1920×1080, 0.75x speed

--- ASSEMBLY ---
7. ffmpeg xfade → crossfade assembly
8. ffmpeg mux → add audio → mtv_with_audio.mp4 (CLEAN SOURCE)
9. Groq Whisper → transcribe for timing
10. Correct lyrics in SRT
11. Write ASS file (bilingual lyrics + title card + end credits on black frames)
12. Check source fps: ffprobe → match black frame fps exactly
13. ffmpeg: audio fade-out 2s before end, extend video + audio with 8s black/silence
14. ffmpeg mux → muxed_clean.mp4 (still no captions)
15. ffmpeg ass burn onto muxed_clean.mp4 → {SongTitle}_MTV_final.mp4
```
