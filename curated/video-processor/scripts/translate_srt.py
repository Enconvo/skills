#!/usr/bin/env python3
"""
Translate SRT subtitles using Groq Llama 3.3 70B
Usage: translate_srt.py <srt_file> <target_lang> [groq_api_key]
"""
import sys
import os
import re
import json

# Load .env from project root if present (for GROQ_API_KEY)
_env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env')
if os.path.exists(_env_file):
    with open(_env_file) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith('#') and '=' in _line:
                _k, _, _v = _line.partition('=')
                _k, _v = _k.strip(), _v.strip().strip('"').strip("'")
                if _k and not os.getenv(_k):
                    os.environ[_k] = _v


def parse_srt(srt_content):
    """Parse SRT content into segments"""
    segments = []
    blocks = srt_content.strip().split('\n\n')

    for block in blocks:
        lines = block.split('\n')
        if len(lines) >= 3:
            index = lines[0]
            timestamp = lines[1]
            text = '\n'.join(lines[2:])

            match = re.match(r'(\d{2}):(\d{2}):(\d{2}),(\d{3}) --> (\d{2}):(\d{2}):(\d{2}),(\d{3})', timestamp)
            if match:
                h1, m1, s1, ms1, h2, m2, s2, ms2 = map(int, match.groups())
                start_sec = h1*3600 + m1*60 + s1 + ms1/1000
                end_sec = h2*3600 + m2*60 + s2 + ms2/1000

                segments.append({
                    'index': int(index),
                    'timestamp': timestamp,
                    'start': start_sec,
                    'end': end_sec,
                    'text': text.strip()
                })

    return segments


def translate_subtitle(srt_content, target_lang, groq_api_key):
    """Translate SRT content to target language using Groq Llama 3.3 70B"""
    from groq import Groq

    print(f"\n{'='*60}")
    print(f"  Translating Subtitles")
    print(f"{'='*60}\n")
    print(f"Target language: {target_lang}")
    print(f"Using: Groq Llama 3.3 70B\n")

    client = Groq(api_key=groq_api_key)
    segments = parse_srt(srt_content)

    translated_segments = []
    for i, seg in enumerate(segments):
        print(f"  Translating segment {i+1}/{len(segments)}...", end='\r')

        translation_prompt = f"""Translate this video subtitle from English to {target_lang}.

CRITICAL RULES:
1. Use NATURAL {target_lang} phrasing - avoid word-for-word translation
2. Match the TONE and STYLE of the original (casual, formal, enthusiastic, etc.)
3. Keep technical terms, brand names, and proper nouns in ENGLISH (e.g., "Google Gemini", "ChatGPT", "YouTube")
4. Preserve the RHYTHM and FLOW for speech - translate for listening, not reading
5. Use colloquial expressions when appropriate - sound like a native speaker
6. Keep numbers, dates, and measurements in their original format
7. DROP any remaining filler words entirely — do NOT translate them. Examples: "you know", "um", "uh", "like" (filler), "I mean", "basically", "actually" (filler), "sort of", "kind of" (when used as verbal tics). These must be silently removed, never rendered in {target_lang}.

EXAMPLE (English to Chinese):
- Bad: "我想到了你，在我看到这个以后。" (machine translation)
- Good: "我一看到这个，就想到了你。" (natural Chinese)

SUBTITLE TEXT:
{seg['text']}

OUTPUT: Only the natural {target_lang} translation, nothing else."""

        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": f"You are a professional video subtitle translator specializing in natural, culturally-aware {target_lang} translations. Your translations sound like a native speaker, not a machine. You preserve the original tone, style, and intent while adapting idioms and expressions for the target culture."
                },
                {
                    "role": "user",
                    "content": translation_prompt
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.5
        )

        translated_text = response.choices[0].message.content.strip()
        translated_segments.append({
            'index': seg['index'],
            'timestamp': seg['timestamp'],
            'original': seg['text'],
            'translated': translated_text,
            'start': seg['start'],
            'end': seg['end']
        })

    print(f"\nTranslation complete!")
    return translated_segments


def display_translation_review(segments, max_display=5):
    """Display translation for review"""
    print(f"\n{'='*60}")
    print(f"  Translation Review")
    print(f"{'='*60}\n")
    print(f"Showing first {min(max_display, len(segments))} of {len(segments)} segments:\n")

    for i, seg in enumerate(segments[:max_display]):
        print(f"[{seg['index']}] {seg['timestamp']}")
        print(f"  EN: {seg['original']}")
        print(f"  ->: {seg['translated']}")
        print()

    if len(segments) > max_display:
        print(f"... and {len(segments) - max_display} more segments")
        print()


def save_translated_srt(segments, output_file):
    """Save translated segments to SRT file"""
    srt_content = ""
    for seg in segments:
        srt_content += f"{seg['index']}\n{seg['timestamp']}\n{seg['translated']}\n\n"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(srt_content)

    print(f"Translated SRT saved: {output_file}")
    return srt_content


def main():
    if len(sys.argv) < 3:
        print("Usage: translate_srt.py <srt_file> <target_lang> [groq_api_key]")
        print("Example: translate_srt.py video_original.srt chinese")
        print("Example: translate_srt.py video_original.srt spanish gsk_xxx")
        sys.exit(1)

    srt_file = sys.argv[1]
    target_lang = sys.argv[2]
    groq_api_key = sys.argv[3] if len(sys.argv) > 3 else os.getenv('GROQ_API_KEY')

    if not groq_api_key:
        print("Error: GROQ_API_KEY not provided")
        print("")
        print("   Get your free key at: https://console.groq.com")
        print("   Then: export GROQ_API_KEY=gsk_xxx")
        print("   Or add to .env file in the skill root directory")
        sys.exit(1)

    if not os.path.exists(srt_file):
        print(f"Error: File not found: {srt_file}")
        sys.exit(1)

    # Read SRT
    with open(srt_file, 'r', encoding='utf-8') as f:
        srt_content = f.read()

    # Translate
    translated_segments = translate_subtitle(srt_content, target_lang, groq_api_key)

    # Review
    display_translation_review(translated_segments)

    # Save
    base_name = os.path.splitext(srt_file)[0].replace('_original', '')
    output_file = f"{base_name}_{target_lang}.srt"
    save_translated_srt(translated_segments, output_file)

    # Status JSON
    status = {
        'srt_file': srt_file,
        'translated_srt': output_file,
        'target_lang': target_lang,
        'segments': len(translated_segments),
        'status': 'awaiting_review'
    }
    status_file = f"{base_name}_status.json"
    with open(status_file, 'w') as f:
        json.dump(status, f, indent=2)

    print(f"\n{'='*60}")
    print("Translation ready for review!")
    print(f"{'='*60}")
    print(f"\nFiles created:")
    print(f"  {output_file} (translated subtitles)")
    print(f"\nNext: Review translation and approve to continue")


if __name__ == "__main__":
    main()
