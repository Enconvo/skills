# Voicebox

All-in-one voice toolkit for Claude Code on Apple Silicon Macs.

## Features

- **Voice Design** — Create custom voices from text descriptions
- **Voice Cloning** — Clone any voice from a 10s audio sample
- **CustomVoice** — 9 preset premium speakers with per-line emotion control via `--instruct`
- **Text-to-Speech** — Generate speech in 10 languages
- **Multi-Speaker Conversations** — Generate dialogues, dramas, news broadcasts
- **Transcription** — Speech-to-text for audio & video, 52 languages with auto-detection

## Install

Copy this skill folder to your Claude Code skills directory:

```bash
cp -r voicebox ~/.claude/skills/voicebox
```

Or clone from the skills repo:

```bash
git clone https://github.com/Enconvo/skills.git /tmp/enconvo-skills
cp -r /tmp/enconvo-skills/curated/voicebox ~/.claude/skills/voicebox
```

That's it. Dependencies and models auto-download on first use.

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

## Voice Profile Types

| Type | Source | Emotion Control | Best For |
|------|--------|----------------|----------|
| **Designed** | Text description | Baked into description | Custom character voices |
| **Cloned** | Audio sample | Limited | Reproducing real voices |
| **CustomVoice** | 9 preset speakers | Per-line `--instruct` | Emotional delivery, dramas |

28 profiles are included out of the box — ready to use immediately.

## CustomVoice Speakers

| Speaker | Language | Style |
|---------|----------|-------|
| dylan | Chinese | Young, energetic male |
| vivian | Chinese | Clear, professional female |
| serena | Chinese | Warm, expressive female |
| uncle_fu | Chinese | Mature, authoritative male |
| eric | Chinese | Calm, steady male |
| aiden | English | Warm, articulate male |
| ryan | English | Natural, conversational male |
| ono_anna | Japanese | Soft, expressive female |
| sohee | Korean | Bright, clear female |

## Quality Options

All commands default to **high** (1.7B models). Use `--quality standard` for faster 0.6B models.

| Category | High (default) | Standard |
|----------|---------------|----------|
| Voice Design | 1.7B | (same) |
| Voice Clone | 1.7B (~3.5GB) | 0.6B (~1.5GB) |
| CustomVoice | 1.7B (~3.5GB) | 0.6B (~1.5GB) |
| Transcription | 1.7B (~3.5GB) | 0.6B (~1.5GB) |

## Supported Languages

**TTS:** English, Chinese, Japanese, Korean, German, French, Russian, Portuguese, Spanish, Italian

**ASR:** 52 languages with auto-detection

## Script Commands

```bash
# List profiles
uv run ~/.claude/skills/voicebox/scripts/voicebox.py list

# List CustomVoice speakers
uv run ~/.claude/skills/voicebox/scripts/voicebox.py speakers

# Generate speech
uv run ~/.claude/skills/voicebox/scripts/voicebox.py generate "Profile" "text" --play

# Generate with emotion (CustomVoice)
uv run ~/.claude/skills/voicebox/scripts/voicebox.py generate "Dylan" "text" --instruct "angry tone" --play

# Create designed voice
uv run ~/.claude/skills/voicebox/scripts/voicebox.py create-designed "Name" --desc "description" --lang en

# Create CustomVoice profile
uv run ~/.claude/skills/voicebox/scripts/voicebox.py create-custom "Name" <speaker>

# Clone from audio file
uv run ~/.claude/skills/voicebox/scripts/voicebox.py create-cloned "Name" --audio /path/to.wav --ref-text "transcript" --lang en

# Record from mic and clone
uv run ~/.claude/skills/voicebox/scripts/voicebox.py record "Name" --duration 10 --lang en

# Transcribe audio/video
uv run ~/.claude/skills/voicebox/scripts/transcribe.py /path/to/file.wav

# Multi-speaker conversation from JSON script
uv run ~/.claude/skills/voicebox/scripts/voicebox.py conversation /tmp/script.json --play

# Delete a profile
uv run ~/.claude/skills/voicebox/scripts/voicebox.py delete "Name"
```
