# Voicebox

All-in-one voice toolkit for Claude Code on Apple Silicon Macs.
Apple Silicon Mac 上的一站式语音工具包，适用于 Claude Code。

## Features / 功能

- **TTS** — Generate speech from text using mlx-audio (local, no cloud) / 本地文字转语音，无需云端
- **Voice Design** — Create custom voices from text descriptions / 通过文字描述创建自定义语音
- **Voice Cloning** — Clone any voice from a 10s audio sample / 10秒音频即可克隆任意声音
- **9 Preset Speakers** — CustomVoice with per-line emotion control / 9个预置音色，支持逐句情感控制
- **Multi-Speaker** — Conversations, dramas, news broadcasts, audiobooks / 多角色对话、戏剧、新闻播报、有声书
- **Transcription** — Speech-to-text, 52 languages, audio & video / 语音转文字，支持52种语言及音视频
- **15 profiles** included out of the box (6 designed, 9 custom) / 开箱即用15个语音配置
- **10 languages** — EN, ZH, JA, KO, DE, FR, RU, PT, ES, IT / 支持10种语言
- Quality tiers: high (1.7B, default) / standard (0.6B, faster) — 高质量(1.7B)与标准(0.6B)双模式

## Install

Copy this skill folder to your Claude Code skills directory:

```bash
# Standard location
cp -r voicebox ~/.claude/skills/voicebox

# Or if using .agent/skills
cp -r voicebox ~/.agent/skills/voicebox
```

Or clone from the skills repo:

```bash
git clone https://github.com/Enconvo/skills.git /tmp/enconvo-skills
cp -r /tmp/enconvo-skills/curated/voicebox ~/.claude/skills/voicebox
```

That's it. The skill works from any install location — all paths are resolved relative to the script. Dependencies and models auto-download on first use.

## Requirements

- Apple Silicon Mac (M1/M2/M3/M4)
- [Claude Code](https://claude.com/claude-code)
- [uv](https://docs.astral.sh/uv/) (usually pre-installed with Claude Code)
- ffmpeg — for recording & video transcription (`brew install ffmpeg`)

## Quick Start

```
/voicebox "Hello world"                                    # Speak with default voice (Calm Narrator)
/voicebox "Calm Narrator" "Hello, this is a test."         # Explicit profile
/voicebox create a calm narrator voice profile             # Design a voice from description
/voicebox create a custom profile using Ryan               # Use a preset CustomVoice speaker
/voicebox clone my voice                                   # Record from mic & clone
/voicebox clone my voice from /path/to/audio.wav           # Clone from audio file
/voicebox transcribe /path/to/audio.wav                    # Transcribe audio/video
/voicebox create a news broadcast with anchor and reporter # Multi-speaker conversation
```

---

## Voice Profile Types

There are three types of voice profiles, each with different capabilities:

| Type | Source | Emotion Control (`--instruct`) | Best For |
|------|--------|-------------------------------|----------|
| **Designed** | Text description | Yes — baked into description, overridable | Custom character voices with unique personality |
| **Custom** (CustomVoice) | 9 preset speakers | Yes — per-line `--instruct` support | Emotional delivery, dramas, expressive speech |
| **Cloned** | Audio sample | No — `--instruct` not supported | Reproducing a specific real person's voice |

### When to use which

- **Custom** — Fast setup, consistent high-quality preset voices, best emotion control via `--instruct`
- **Designed** — Unlimited creativity, describe any voice you want (age, gender, pitch, pace, tone)
- **Cloned** — Reproduce a specific real person's voice from a 10-second audio sample

---

## Preset Profiles (Included Out of the Box)

### Designed Profiles (6)

These are created from text descriptions using the VoiceDesign model. Each has a unique voice identity baked into its description.

| Profile | Language | Description |
|---------|----------|-------------|
| **Calm Narrator** | English | Calm middle-aged male with deep warm baritone, slow measured pace, soothing and trustworthy tone — ideal for audiobook narration |
| **Cheerful Girl** | English | Young adult female with crisp energetic soprano, fast lively pace, cheerful and bubbly tone — ideal for upbeat narration and announcements |
| **News Anchor** | English | Professional middle-aged male with deep authoritative baritone, measured steady pace, confident and trustworthy — ideal for broadcast news |
| **Shakespeare** | English | Mature deep male with rich theatrical baritone, dramatic gravitas, slow commanding pace — like a seasoned Shakespearean stage actor |
| **Shakespeare Chinese** | Chinese | Mature deep male with theatrical baritone, dramatic gravitas and passionate intensity — performing a patriotic war poem with fierce emotion |
| **Panic Granny** | English | Elderly woman (late 70s) with high-pitched shaky trembling voice, fast frantic pace, panicked and breathless — ideal for dramatic alarmed storytelling |

### CustomVoice Profiles (9)

These use 9 preset high-quality speakers from the CustomVoice model. They support `--instruct` for per-line emotion/style control.

| Profile | Speaker ID | Language | Style |
|---------|-----------|----------|-------|
| **Dylan** | `dylan` | Chinese | Young, energetic male |
| **Vivian** | `vivian` | Chinese | Clear, professional female |
| **Serena** | `serena` | Chinese | Warm, expressive female |
| **Uncle Fu** | `uncle_fu` | Chinese | Mature, authoritative male |
| **Eric** | `eric` | Chinese | Calm, steady male |
| **Aiden** | `aiden` | English | Warm, articulate male |
| **Ryan** | `ryan` | English | Natural, conversational male |
| **Ono Anna** | `ono_anna` | Japanese | Soft, expressive female |
| **Sohee** | `sohee` | Korean | Bright, clear female |

### Default Profile Selection

| Context | Default Profile | Type |
|---------|----------------|------|
| General (English text, no emotion) | **Calm Narrator** | Designed |
| Emotional delivery — Chinese | **Dylan** | Custom |
| Emotional delivery — English | **Aiden** | Custom |
| Emotional delivery — Japanese | **Ono Anna** | Custom |

When emotion is requested (angry, sad, excited, etc.), the skill prefers CustomVoice defaults by language because they support `--instruct` for fine-grained emotion control.

---

## Voice Cloning

Clone any voice from an audio sample — no description needed. The cloned voice reproduces the speaker's identity from reference audio.

### From an audio file

```
/voicebox clone my voice from /path/to/audio.wav
```

- Accepts: WAV, MP3, FLAC, M4A, OGG, AAC, WMA
- Best results with 5–15 seconds of clear speech
- If no transcript is provided, it auto-transcribes using built-in Qwen3-ASR

### Record from microphone

```
/voicebox clone my voice
```

- Records from your Mac microphone (default 10 seconds)
- Auto-transcribes the recording
- Creates a cloned profile ready to use immediately
- Requires: ffmpeg (`brew install ffmpeg`) and macOS microphone permission

### Cloned voice limitations

- **No `--instruct` support** — Cloned voices cannot change emotion/style per-line
- The voice quality depends on the reference audio quality (clean, quiet environment is best)
- Works with the Base model (not VoiceDesign or CustomVoice)

---

## Emotion Segmentation (Auto-Emotion)

By default, long text is generated as a **single pass** with one consistent tone — no automatic splitting occurs.

### Opt-in only

Emotion segmentation activates **only** when you explicitly request it with phrases like:
- "with emotions", "auto-emotion", "segment emotions", "emotional delivery"
- "split by emotion", "vary the emotions", "make it expressive"

### How it works

1. The text is analyzed and split at natural emotional boundaries (sentence or clause level)
2. Each segment is tagged with an emotion instruction (excitement, sadness, calm, determination, etc.)
3. A conversation script is generated and rendered using the `conversation` command

### Critical rule: Same profile on every line

**Emotion segmentation is NOT a multi-speaker conversation.** It is ONE person speaking with varying emotions. Every line in the generated script uses the **exact same profile** — only the `"instruct"` field varies between segments.

Example script (correct):
```json
{
  "title": "emotional_speech",
  "gap": 0.15,
  "lines": [
    {"profile": "Aiden", "text": "I can't believe we won!", "instruct": "excited, enthusiastic tone"},
    {"profile": "Aiden", "text": "But then I heard the news...", "instruct": "worried, anxious, trembling voice"},
    {"profile": "Aiden", "text": "We have to keep going.", "instruct": "determined, resolute, firm tone"},
    {"profile": "Aiden", "text": "Thank you all for being here.", "instruct": "gentle, grateful, warm and tender"}
  ]
}
```

All four lines use **"Aiden"** — the same profile. This is intentional and required.

### Default profile for emotion segmentation

When no specific profile is requested, the skill uses the **CustomVoice default for the detected language**:
- **English** → Aiden
- **Chinese** → Dylan
- **Japanese** → Ono Anna

CustomVoice profiles are preferred for emotion segmentation because they support `--instruct`.

### Emotion palette

| Emotion | Example `instruct` values |
|---------|--------------------------|
| Joy / Excitement | `"excited, enthusiastic, joyful tone"`, `"ecstatic, breathless with joy"` |
| Anger | `"angry, furious, intense tone"`, `"irritated, sharp and impatient"` |
| Sadness / Sorrow | `"sorrowful, heartbroken, tearful voice"`, `"melancholic, quiet and reflective"` |
| Fear / Panic | `"panicked, terrified, desperate tone"`, `"anxious, nervous, trembling voice"` |
| Calm / Neutral | `"calm, steady, composed delivery"`, `"warm and reassuring tone"` |
| Surprise | `"shocked, astonished, wide-eyed disbelief"` |
| Determination | `"determined, resolute, firm and confident"` |
| Tenderness | `"gentle, tender, soft-spoken with warmth"` |

### Emotion segmentation vs Multi-speaker

| Feature | Emotion Segmentation | Multi-Speaker Conversation |
|---------|---------------------|---------------------------|
| Trigger | "with emotions", "auto-emotion" | "conversation", "drama", "dialogue" |
| Voices | ONE profile, same on every line | MULTIPLE profiles, different per line |
| `instruct` | Varies per line (different emotions) | Optional per line (style override) |
| Use case | Expressive monologue | Dialogue between characters |

---

## Quality Options

All commands default to **high** (1.7B models). Use `--quality standard` for faster 0.6B models.

| Category | High (default) | Standard |
|----------|---------------|----------|
| Voice Design | 1.7B | (same — only 1.7B exists) |
| Voice Clone | 1.7B (~3.5GB) | 0.6B (~1.5GB) |
| CustomVoice | 1.7B (~3.5GB) | 0.6B (~1.5GB) |
| Transcription | 1.7B (~3.5GB) | 0.6B (~1.5GB) |

## Supported Languages

**TTS:** English, Chinese, Japanese, Korean, German, French, Russian, Portuguese, Spanish, Italian

**ASR:** 52 languages with auto-detection

## Script Commands

Replace `$SKILL_DIR` with your install path (e.g., `~/.claude/skills/voicebox` or `~/.agent/skills/voicebox`).

```bash
# List profiles
uv run $SKILL_DIR/scripts/voicebox.py list

# List CustomVoice speakers
uv run $SKILL_DIR/scripts/voicebox.py speakers

# Generate speech
uv run $SKILL_DIR/scripts/voicebox.py generate "Profile" "text" --play

# Generate with emotion (CustomVoice)
uv run $SKILL_DIR/scripts/voicebox.py generate "Dylan" "text" --instruct "angry tone" --play

# Create designed voice
uv run $SKILL_DIR/scripts/voicebox.py create-designed "Name" --desc "description" --lang en

# Create CustomVoice profile
uv run $SKILL_DIR/scripts/voicebox.py create-custom "Name" <speaker>

# Clone from audio file
uv run $SKILL_DIR/scripts/voicebox.py create-cloned "Name" --audio /path/to.wav --ref-text "transcript" --lang en

# Record from mic and clone
uv run $SKILL_DIR/scripts/voicebox.py record "Name" --duration 10 --lang en

# Transcribe audio/video
uv run $SKILL_DIR/scripts/transcribe.py /path/to/file.wav

# Multi-speaker conversation from JSON script
uv run $SKILL_DIR/scripts/voicebox.py conversation /tmp/script.json --play

# Delete a profile
uv run $SKILL_DIR/scripts/voicebox.py delete "Name"
```
