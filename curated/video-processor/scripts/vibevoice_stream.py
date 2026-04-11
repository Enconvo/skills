#!/usr/bin/env python3
"""
Streaming TTS with VibeVoice — sentence-level pipeline with overlapped generation.
Generates next sentence while current one plays, eliminating gaps.

Usage:
    python3 vibevoice_stream.py "Your text here"
    python3 vibevoice_stream.py "Your text here" --voice en-Emma_woman
    python3 vibevoice_stream.py "Your text here" --model mlx-community/VibeVoice-Realtime-0.5B-8bit
    python3 vibevoice_stream.py "Your text here" --save output.wav
"""
import argparse
import re
import time
import threading
import queue
import numpy as np
import sounddevice as sd


def split_sentences(text):
    """Split text into sentences, keeping short ones together."""
    raw = re.split(r'(?<=[.!?])\s+', text.strip())
    sentences = []
    buf = ""
    for s in raw:
        buf = (buf + " " + s).strip() if buf else s
        if len(buf) >= 30 or s == raw[-1]:
            sentences.append(buf)
            buf = ""
    if buf:
        sentences.append(buf)
    return sentences


def stream_tts(text, model_path="mlx-community/VibeVoice-Realtime-0.5B-4bit",
               voice="en-Emma_woman", save_path=None):
    from mlx_audio.tts.utils import load_model

    # Accept preloaded model object or string path
    if isinstance(model_path, str):
        print(f"Loading model: {model_path}")
        t0 = time.time()
        model = load_model(model_path=model_path)
        print(f"Model loaded in {time.time()-t0:.1f}s (sample rate: {model.sample_rate})")
    else:
        model = model_path  # Already loaded

    sr = model.sample_rate
    print(f"Voice: {voice}")
    print(f"Text: {text[:80]}{'...' if len(text) > 80 else ''}")

    sentences = split_sentences(text)
    print(f"Sentences: {len(sentences)} chunks")
    print(f"Streaming with overlapped generation...\n")

    # Audio queue — generator thread pushes, main thread plays
    audio_q = queue.Queue()
    all_audio = []
    t_start = time.time()

    def generator_thread():
        """Generate audio for each sentence and push to queue."""
        for i, sentence in enumerate(sentences):
            for result in model.generate(text=sentence, voice=voice, verbose=False):
                if result.audio is not None:
                    audio_np = np.array(result.audio, dtype=np.float32).flatten()
                    # Normalize
                    peak = np.max(np.abs(audio_np))
                    if peak > 0:
                        audio_np = audio_np / peak * 0.9
                    audio_q.put((i, sentence, audio_np))
        audio_q.put(None)  # Sentinel

    # Start generation in background thread
    gen_thread = threading.Thread(target=generator_thread, daemon=True)
    gen_thread.start()

    # Play audio as it arrives — no gaps between sentences
    stream = sd.OutputStream(samplerate=sr, channels=1, dtype='float32')
    stream.start()
    first_chunk = True

    while True:
        item = audio_q.get()
        if item is None:
            break

        i, sentence, audio_np = item
        dur = len(audio_np) / sr

        if first_chunk:
            latency = time.time() - t_start
            print(f"  First audio: {latency:.2f}s latency, {dur:.1f}s audio")
            first_chunk = False

        print(f"  [{i+1}/{len(sentences)}] {dur:.1f}s  \"{sentence[:50]}{'...' if len(sentence) > 50 else ''}\"")

        stream.write(audio_np)
        all_audio.append(audio_np)

    # Wait for playback to finish
    if all_audio:
        total_samples = sum(len(a) for a in all_audio)
        elapsed = time.time() - t_start
        remaining = max(0, total_samples / sr - elapsed)
        if remaining > 0.1:
            sd.sleep(int(remaining * 1000))

    stream.stop()
    stream.close()
    gen_thread.join(timeout=1)

    total_audio = np.concatenate(all_audio) if all_audio else np.array([])
    total_time = time.time() - t_start
    audio_dur = len(total_audio) / sr if len(total_audio) > 0 else 0

    print(f"\n  Total: {audio_dur:.1f}s audio in {total_time:.1f}s")
    print(f"  Realtime factor: {audio_dur / total_time:.1f}x" if total_time > 0 else "")

    if save_path and len(total_audio) > 0:
        import soundfile as sf
        sf.write(save_path, total_audio, sr)
        print(f"  Saved: {save_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Streaming TTS with VibeVoice (overlapped generation)")
    parser.add_argument("text", nargs="?", default=None, help="Text to speak (omit for REPL mode)")
    parser.add_argument("--model", default="mlx-community/VibeVoice-Realtime-0.5B-4bit",
                        help="Model repo ID (default: 4bit)")
    parser.add_argument("--voice", default="en-Emma_woman", help="Voice name")
    parser.add_argument("--save", default=None, help="Save audio to file")
    parser.add_argument("--repl", action="store_true", help="Keep model hot, interactive REPL mode")
    args = parser.parse_args()

    if args.text and not args.repl:
        stream_tts(args.text, model_path=args.model, voice=args.voice, save_path=args.save)
    else:
        # REPL mode — load model once, keep hot in memory
        from mlx_audio.tts.utils import load_model

        print(f"Loading model: {args.model}")
        t0 = time.time()
        _model = load_model(model_path=args.model)
        print(f"Model loaded in {time.time()-t0:.1f}s (HOT — stays in memory)")
        print(f"Voice: {args.voice}")
        print(f"Type text and press Enter to speak. Ctrl+C to exit.\n")

        if args.text:
            stream_tts(args.text, model_path=_model, voice=args.voice, save_path=args.save)

        while True:
            try:
                text = input(">>> ").strip()
                if not text:
                    continue
                if text.lower() in ("quit", "exit", "q"):
                    break
                stream_tts(text, model_path=_model, voice=args.voice)
            except (KeyboardInterrupt, EOFError):
                print("\nBye.")
                break
