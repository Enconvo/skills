---
name: voxtral-tts
description: >
  Generate speech from text using Mistral's Voxtral TTS model locally on Apple Silicon via mlx-audio.
  20 preset voices across 9 languages (English, French, German, Spanish, Portuguese, Italian, Dutch, Arabic, Hindi).
  Does NOT support Chinese/Japanese/Korean.
  Use when: user asks to "generate speech", "text to speech", "TTS", "voxtral", "read aloud", "speak this",
  or needs high-quality multilingual voice synthesis locally. Preferred over cloud TTS for privacy and cost.
---

# Voxtral TTS

Local text-to-speech on Apple Silicon using Mistral's Voxtral-4B via MLX.

## Requirements

- Apple Silicon Mac (M1+)
- Python 3.10+
- ~2.5GB RAM (4-bit quantized) or ~8GB (bf16)

## Setup

```bash
pip install "mlx-audio @ git+https://github.com/lucasnewman/mlx-audio.git@main"
```

> **Note:** As of March 2026, Voxtral support requires mlx-audio from git (PR #607). Once released to PyPI, `pip install -U mlx-audio` will suffice.

## Quick Usage

```python
from mlx_audio.tts.utils import load
import numpy as np
import soundfile as sf

model = load("mlx-community/Voxtral-4B-TTS-2603-mlx-4bit")

for result in model.generate(text="Hello world!", voice="cheerful_female"):
    audio = np.array(result.audio)
    sf.write("output.wav", audio, result.sample_rate)  # 24000 Hz
```

**Always use `result.sample_rate`** — never hardcode the sample rate.

## Model Variants

| Model | Size | RAM | Speed |
|---|---|---|---|
| `mlx-community/Voxtral-4B-TTS-2603-mlx-4bit` | ~2.5GB | ~3GB | RTF ~0.70 |
| `mlx-community/Voxtral-4B-TTS-2603-mlx-6bit` | ~3.5GB | ~4GB | RTF ~0.75 |
| `mlx-community/Voxtral-4B-TTS-2603-mlx-bf16` | ~8GB | ~9GB | Best quality |

4-bit recommended for most use cases. RTF < 1.0 means faster than real-time.

## Voices (20 total)

### English (5)
`casual_female`, `casual_male`, `cheerful_female`, `neutral_female`, `neutral_male`

### Other Languages (15)
| Language | Voices |
|---|---|
| Portuguese 🇧🇷 | `pt_male`, `pt_female` |
| Dutch 🇳🇱 | `nl_male`, `nl_female` |
| Italian 🇮🇹 | `it_male`, `it_female` |
| French 🇫🇷 | `fr_male`, `fr_female` |
| Spanish 🇪🇸 | `es_male`, `es_female` |
| German 🇩🇪 | `de_male`, `de_female` |
| Arabic 🇸🇦 | `ar_male` |
| Hindi 🇮🇳 | `hi_male`, `hi_female` |

## Script Usage

Generate speech from the command line:

```bash
python scripts/voxtral_generate.py --text "Hello world" --voice cheerful_female --output output.wav
```

Options:
- `--text` — Text to synthesize (required)
- `--voice` — Voice name (default: `cheerful_female`)
- `--model` — Model variant (default: `mlx-community/Voxtral-4B-TTS-2603-mlx-4bit`)
- `--output` — Output file path (default: `output.wav`)
- `--format` — Output format: `wav`, `ogg`, `mp3` (default: `wav`; ogg/mp3 require ffmpeg)

## First Run

The first run downloads the model from HuggingFace (~2.5GB for 4-bit). The script auto-detects this and prints a notice. Subsequent runs load from cache in ~2-5 seconds.

## Performance (M5 MacBook Pro 32GB, 4-bit)

- **Load time:** ~2-5s (first load downloads model)
- **Generation RTF:** ~0.70 (10s audio ≈ 7s generation)
- **Sample rate:** 24000 Hz
- **Languages not supported:** Chinese, Japanese, Korean — use `spark-tts` skill for Chinese

## Integration Pattern

```python
from mlx_audio.tts.utils import load
import numpy as np
import sounddevice as sd

model = load("mlx-community/Voxtral-4B-TTS-2603-mlx-4bit")

def speak(text: str, voice: str = "cheerful_female"):
    for result in model.generate(text=text, voice=voice):
        audio = np.array(result.audio)
        sd.play(audio, result.sample_rate)
        sd.wait()
```

## Telegram Voice Message

To send as Telegram voice, convert to OGG Opus:

```bash
ffmpeg -y -i output.wav -c:a libopus -b:a 96k output.ogg
```

Then send with `asVoice: true`.
