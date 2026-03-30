---
name: spark-tts
description: >
  Generate speech from text using iFlytek's Spark TTS model locally on Apple Silicon via mlx-audio.
  Supports Chinese and English with controllable gender, pitch, and speed.
  Also supports voice cloning from a 3-second reference audio clip.
  Use when: user asks to "generate Chinese speech", "中文语音合成", "TTS in Chinese", "spark tts",
  "clone my voice", "read this in Chinese", or needs Chinese text-to-speech locally.
  Preferred over Voxtral for Chinese/CJK content. Lightweight 0.5B model (~1GB).
---

# Spark TTS

Local Chinese+English text-to-speech on Apple Silicon using iFlytek's Spark-TTS-0.5B via MLX.

## Requirements

- Apple Silicon Mac (M1+)
- Python 3.10+
- ~1GB RAM (bf16)

## Setup

```bash
pip install -U mlx-audio
```

## Quick Usage

```python
from mlx_audio.tts.utils import load
import numpy as np
import soundfile as sf

model = load("mlx-community/Spark-TTS-0.5B-bf16")

for result in model.generate(text="你好，世界！", gender="female"):
    audio = np.array(result.audio)
    sf.write("output.wav", audio, result.sample_rate)  # 16000 Hz
```

**Always use `result.sample_rate`** — Spark outputs at 16000 Hz (not 24000). Hardcoding the wrong rate causes audio to sound fast-forwarded.

## Parameters

```python
model.generate(
    text="Hello",           # required
    gender="female",        # "male" or "female"
    pitch=1.0,              # 0.0=very_low, 0.5=low, 1.0=moderate, 1.5=high, 2.0=very_high
    speed=1.0,              # 0.0=very_low, 0.5=low, 1.0=moderate, 1.5=high, 2.0=very_high
    temperature=0.8,        # generation temperature
    ref_audio="ref.wav",    # optional: reference audio for voice cloning
    ref_text="transcript",  # optional: transcript of reference audio
)
```

### Gender
- `"male"` — male voice
- `"female"` — female voice

### Pitch & Speed Levels
| Value | Level |
|---|---|
| 0.0 | very_low |
| 0.5 | low |
| 1.0 | moderate (default) |
| 1.5 | high |
| 2.0 | very_high |

### Voice Cloning

Clone any voice with ~3 seconds of reference audio:

```python
for result in model.generate(
    text="你好，我是克隆的声音。",
    ref_audio="reference.wav",
    ref_text="这是参考音频的文字内容。",
):
    sf.write("cloned.wav", np.array(result.audio), result.sample_rate)
```

## Script Usage

```bash
python scripts/spark_generate.py --text "你好世界" --gender female --output output.wav
python scripts/spark_generate.py --text "Hello" --gender male --pitch 1.5 --speed 1.5 --output fast_high.ogg --format ogg
python scripts/spark_generate.py --text "克隆声音" --ref-audio voice.wav --ref-text "参考文字" --output cloned.wav
```

Options:
- `--text` — Text to synthesize (required)
- `--gender` — `male` or `female` (default: `female`)
- `--pitch` — Pitch level: 0.0/0.5/1.0/1.5/2.0 (default: 1.0)
- `--speed` — Speed level: 0.0/0.5/1.0/1.5/2.0 (default: 1.0)
- `--ref-audio` — Reference audio for voice cloning
- `--ref-text` — Transcript of reference audio
- `--model` — Model variant (default: `mlx-community/Spark-TTS-0.5B-bf16`)
- `--output` — Output file path (default: `output.wav`)
- `--format` — Output format: `wav`, `ogg`, `mp3` (default: `wav`)

## First Run

The first run downloads the model from HuggingFace (~1GB). The script auto-detects this and prints a notice. Subsequent runs load from cache in ~2 seconds.

## Performance (M5 MacBook Pro 32GB)

- **Load time:** ~2s
- **Generation RTF:** ~0.63 (10s audio ≈ 6.3s generation)
- **Sample rate:** 16000 Hz
- **Languages:** Chinese, English (bilingual)
- **Model size:** ~1GB

## Language Comparison

| Feature | Spark TTS | Voxtral TTS |
|---|---|---|
| Chinese | ✅ | ❌ |
| English | ✅ | ✅ (better quality) |
| Other languages | ❌ | ✅ (9 languages) |
| Voice cloning | ✅ | ❌ |
| Pitch/speed control | ✅ | ❌ |
| Model size | ~1GB | ~2.5GB |
| Voices | 2 (M/F) × 5 levels | 20 presets |

**Use Spark for Chinese. Use Voxtral for other languages.**

## Telegram Voice Message

Convert to OGG Opus for Telegram:

```bash
ffmpeg -y -i output.wav -c:a libopus -b:a 96k output.ogg
```

Send with `asVoice: true`.
