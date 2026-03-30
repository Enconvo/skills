#!/usr/bin/env python3
"""
Voxtral TTS — Generate speech locally on Apple Silicon via MLX.

Usage:
    python voxtral_generate.py --text "Hello world" --voice cheerful_female --output output.wav
    python voxtral_generate.py --text "Bonjour le monde" --voice fr_female --output bonjour.ogg --format ogg
"""

import argparse
import subprocess
import sys
import tempfile
import time

import numpy as np
import soundfile as sf


VOICES = [
    "casual_female", "casual_male", "cheerful_female", "neutral_female", "neutral_male",
    "pt_male", "pt_female", "nl_male", "nl_female",
    "it_male", "it_female", "fr_male", "fr_female",
    "es_male", "es_female", "de_male", "de_female",
    "ar_male", "hi_male", "hi_female",
]

DEFAULT_MODEL = "mlx-community/Voxtral-4B-TTS-2603-mlx-4bit"


def main():
    parser = argparse.ArgumentParser(description="Voxtral TTS — local speech synthesis on Apple Silicon")
    parser.add_argument("--text", required=True, help="Text to synthesize")
    parser.add_argument("--voice", default="cheerful_female", choices=VOICES, help="Voice name")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="MLX model path or HuggingFace repo")
    parser.add_argument("--output", default="output.wav", help="Output file path")
    parser.add_argument("--format", default="wav", choices=["wav", "ogg", "mp3"], help="Output format")
    parser.add_argument("--list-voices", action="store_true", help="List available voices and exit")
    args = parser.parse_args()

    if args.list_voices:
        print("Available voices:")
        for v in VOICES:
            print(f"  {v}")
        return

    try:
        from mlx_audio.tts.utils import load
    except ImportError:
        print("❌ mlx-audio not installed. Run:")
        print('   pip install "mlx-audio @ git+https://github.com/lucasnewman/mlx-audio.git@main"')
        sys.exit(1)

    # Check if model is already cached
    from huggingface_hub import try_to_load_from_cache
    cached = try_to_load_from_cache(args.model, "config.json")
    if cached is None or isinstance(cached, str) is False:
        size = "~2.5GB (4-bit)" if "4bit" in args.model else "~3.5GB (6-bit)" if "6bit" in args.model else "~8GB (bf16)"
        print(f"⏳ First run — downloading Voxtral model ({size}). This only happens once.")
        print(f"   Model: {args.model}")
        print()

    print(f"Loading model: {args.model}")
    t0 = time.time()
    model = load(args.model)
    print(f"Loaded in {time.time() - t0:.1f}s")

    print(f"Generating: {args.text[:80]}{'...' if len(args.text) > 80 else ''}")
    print(f"Voice: {args.voice}")

    t0 = time.time()
    pieces = []
    for result in model.generate(text=args.text, voice=args.voice):
        pieces.append(np.array(result.audio))

    audio = np.concatenate(pieces)
    sample_rate = result.sample_rate  # always use model's native rate
    gen_time = time.time() - t0
    duration = len(audio) / sample_rate

    print(f"Generated {duration:.1f}s audio in {gen_time * 1000:.0f}ms (RTF: {gen_time / duration:.2f})")

    if args.format == "wav" or args.format == "wav":
        output = args.output if args.output.endswith(".wav") else args.output
        sf.write(output, audio, sample_rate)
    else:
        # Write WAV first, then convert
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            tmp = f.name
        sf.write(tmp, audio, sample_rate)

        codec = "libopus" if args.format == "ogg" else "libmp3lame"
        bitrate = "96k" if args.format == "ogg" else "192k"
        output = args.output

        try:
            subprocess.run(
                ["ffmpeg", "-y", "-i", tmp, "-c:a", codec, "-b:a", bitrate, output],
                capture_output=True, check=True,
            )
        except FileNotFoundError:
            print("ffmpeg not found — saving as WAV instead")
            output = args.output.rsplit(".", 1)[0] + ".wav"
            sf.write(output, audio, sample_rate)
        finally:
            import os
            os.unlink(tmp)

    print(f"Saved: {output}")


if __name__ == "__main__":
    main()
