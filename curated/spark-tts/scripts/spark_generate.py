#!/usr/bin/env python3
"""
Spark TTS — Generate Chinese+English speech locally on Apple Silicon via MLX.

Usage:
    python spark_generate.py --text "你好世界" --gender female --output output.wav
    python spark_generate.py --text "Hello" --gender male --pitch 1.5 --output hi.ogg --format ogg
    python spark_generate.py --text "克隆" --ref-audio ref.wav --ref-text "参考" --output cloned.wav
"""

import argparse
import subprocess
import sys
import tempfile
import time

import numpy as np
import soundfile as sf


PITCH_SPEED_LEVELS = [0.0, 0.5, 1.0, 1.5, 2.0]
DEFAULT_MODEL = "mlx-community/Spark-TTS-0.5B-bf16"


def main():
    parser = argparse.ArgumentParser(description="Spark TTS — local Chinese+English speech synthesis")
    parser.add_argument("--text", required=True, help="Text to synthesize")
    parser.add_argument("--gender", default="female", choices=["male", "female"], help="Voice gender")
    parser.add_argument("--pitch", type=float, default=1.0, help="Pitch: 0.0/0.5/1.0/1.5/2.0")
    parser.add_argument("--speed", type=float, default=1.0, help="Speed: 0.0/0.5/1.0/1.5/2.0")
    parser.add_argument("--ref-audio", default=None, help="Reference audio for voice cloning")
    parser.add_argument("--ref-text", default=None, help="Transcript of reference audio")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="MLX model path or HuggingFace repo")
    parser.add_argument("--output", default="output.wav", help="Output file path")
    parser.add_argument("--format", default="wav", choices=["wav", "ogg", "mp3"], help="Output format")
    parser.add_argument("--temperature", type=float, default=0.8, help="Generation temperature")
    args = parser.parse_args()

    if args.pitch not in PITCH_SPEED_LEVELS:
        parser.error(f"Pitch must be one of {PITCH_SPEED_LEVELS}")
    if args.speed not in PITCH_SPEED_LEVELS:
        parser.error(f"Speed must be one of {PITCH_SPEED_LEVELS}")

    try:
        from mlx_audio.tts.utils import load
    except ImportError:
        print("❌ mlx-audio not installed. Run:")
        print("   pip install -U mlx-audio")
        sys.exit(1)

    # Check if model is already cached
    from huggingface_hub import try_to_load_from_cache
    cached = try_to_load_from_cache(args.model, "config.json")
    if cached is None or isinstance(cached, str) is False:
        print(f"⏳ First run — downloading Spark TTS model (~1GB). This only happens once.")
        print(f"   Model: {args.model}")
        print()

    print(f"Loading model: {args.model}")
    t0 = time.time()
    model = load(args.model)
    print(f"Loaded in {time.time() - t0:.1f}s")

    print(f"Generating: {args.text[:80]}{'...' if len(args.text) > 80 else ''}")
    print(f"Gender: {args.gender} | Pitch: {args.pitch} | Speed: {args.speed}")

    gen_kwargs = dict(
        text=args.text,
        gender=args.gender,
        pitch=args.pitch,
        speed=args.speed,
        temperature=args.temperature,
    )
    if args.ref_audio:
        gen_kwargs["ref_audio"] = args.ref_audio
        print(f"Voice cloning from: {args.ref_audio}")
    if args.ref_text:
        gen_kwargs["ref_text"] = args.ref_text

    t0 = time.time()
    pieces = []
    for result in model.generate(**gen_kwargs):
        pieces.append(np.array(result.audio))

    audio = np.concatenate(pieces)
    sample_rate = result.sample_rate  # always use model's native rate (16000)
    gen_time = time.time() - t0
    duration = len(audio) / sample_rate

    print(f"Generated {duration:.1f}s audio in {gen_time * 1000:.0f}ms (RTF: {gen_time / duration:.2f})")

    if args.format == "wav":
        sf.write(args.output, audio, sample_rate)
    else:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            tmp = f.name
        sf.write(tmp, audio, sample_rate)

        codec = "libopus" if args.format == "ogg" else "libmp3lame"
        bitrate = "96k" if args.format == "ogg" else "192k"

        try:
            subprocess.run(
                ["ffmpeg", "-y", "-i", tmp, "-c:a", codec, "-b:a", bitrate, args.output],
                capture_output=True, check=True,
            )
        except FileNotFoundError:
            print("ffmpeg not found — saving as WAV instead")
            args.output = args.output.rsplit(".", 1)[0] + ".wav"
            sf.write(args.output, audio, sample_rate)
        finally:
            import os
            os.unlink(tmp)

    print(f"Saved: {args.output}")


if __name__ == "__main__":
    main()
