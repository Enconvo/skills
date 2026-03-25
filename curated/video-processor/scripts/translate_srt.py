#!/usr/bin/env python3
"""
Translate SRT subtitles using EnConvo API
Usage: translate_srt.py <srt_file> <target_lang>
"""
import sys
import os
import re
import json


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


def groq_translate(text, target_lang):
    """Translate text via Groq LLM (llama-3.3-70b)."""
    from groq import Groq

    groq_api_key = os.environ.get('GROQ_API_KEY', '')
    if not groq_api_key:
        print("  ERROR: GROQ_API_KEY not set")
        sys.exit(1)

    client = Groq(api_key=groq_api_key)
    prompt = (
        f"Translate this video subtitle to natural {target_lang}. "
        f"Return ONLY the translation. Keep brand names/proper nouns in English. "
        f"Drop filler words. Be concise for subtitles.\n\n{text}"
    )

    try:
        resp = client.chat.completions.create(
            model='llama-3.3-70b-versatile',
            messages=[{'role': 'user', 'content': prompt}],
            max_tokens=500,
            temperature=0.3
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"\n  Translation error: {e}")
        return text


def translate_subtitle(srt_content, target_lang):
    """Translate SRT content to target language using EnConvo API"""

    print(f"\n{'='*60}")
    print(f"  Translating Subtitles")
    print(f"{'='*60}\n")
    print(f"Target language: {target_lang}")
    print(f"Using: Groq LLM (llama-3.3-70b)\n")

    segments = parse_srt(srt_content)

    translated_segments = []
    for i, seg in enumerate(segments):
        print(f"  Translating segment {i+1}/{len(segments)}...", end='\r')

        translated_text = groq_translate(seg['text'], target_lang)
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
        print("Usage: translate_srt.py <srt_file> <target_lang>")
        print("Example: translate_srt.py video_original.srt chinese")
        print("Example: translate_srt.py video_original.srt spanish")
        print("\nRequires EnConvo running on localhost:54535")
        sys.exit(1)

    srt_file = sys.argv[1]
    target_lang = sys.argv[2]

    if not os.path.exists(srt_file):
        print(f"Error: File not found: {srt_file}")
        sys.exit(1)

    # Read SRT
    with open(srt_file, 'r', encoding='utf-8') as f:
        srt_content = f.read()

    # Translate
    translated_segments = translate_subtitle(srt_content, target_lang)

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
