#!/usr/bin/env python3
"""
Generate bilingual captions: Chinese MAIN (karaoke) + English SECONDARY.
Reads existing _words.json (word-level timestamps), translates to Chinese,
then burns into video.

Usage:
  python3 make_bilingual_zh_main.py <video.mp4> <words.json> <output.mp4>
"""
import sys, os, json, subprocess, urllib.request
from pathlib import Path

def seconds_to_ass(s):
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    sec = int(s % 60)
    cs = int((s - int(s)) * 100)
    return f"{h}:{m:02d}:{sec:02d}.{cs:02d}"

def group_words(words, max_per_line=8):
    lines = []
    current = []
    for w in words:
        current.append(w)
        if len(current) >= max_per_line:
            lines.append(current)
            current = []
    if current:
        lines.append(current)
    return lines

def get_line_text(line_words):
    return ' '.join(w['word'].strip() for w in line_words)

def translate_to_chinese(lines_text, groq_api_key):
    """Translate English lines to Chinese via Groq LLM (llama-3.3-70b)."""
    from groq import Groq
    client = Groq(api_key=groq_api_key)
    print(f"  Translating {len(lines_text)} lines to Chinese via Groq LLM...")
    translations = []
    for text in lines_text:
        try:
            resp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{
                    "role": "user",
                    "content": (
                        "Translate to Simplified Chinese. Return ONLY the Chinese translation, "
                        "no explanation, no quotes. Natural subtitle Chinese:\n\n" + text
                    )
                }],
                max_tokens=200
            )
            zh = resp.choices[0].message.content.strip()
            if not zh:
                zh = text
            translations.append(zh)
            print(f"    EN: {text}")
            print(f"    ZH: {zh}")
        except Exception as e:
            print(f"    Translation error: {e}")
            translations.append(text)
    return translations

def generate_ass_zh_main(lines, zh_translations, video_w=1320, video_h=722):
    """Generate ASS: Chinese main (karaoke) + English secondary."""
    scale = video_h / 1080
    main_size = max(16, round(45 * scale))
    secondary_size = max(12, round(30 * scale))
    outline = max(1, round(2 * scale))
    main_margin_v = round(0.133 * video_h)
    secondary_margin_v = round(0.09 * video_h)

    ass = f"""[Script Info]
Title: Bilingual ZH Main EN Secondary
ScriptType: v4.00+
PlayResX: {video_w}
PlayResY: {video_h}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Main,PingFang SC,{main_size},&H0000FFFF,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,{outline},1,2,20,20,{main_margin_v},1
Style: Secondary,Helvetica Neue,{secondary_size},&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,{outline},1,2,20,20,{secondary_margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    for i, line_words in enumerate(lines):
        if not line_words:
            continue
        start = line_words[0]['start']
        end = line_words[-1]['end']
        start_ts = seconds_to_ass(start)
        end_ts = seconds_to_ass(end)
        dur_cs = int((end - start) * 100)

        # Chinese MAIN: single \kf tag over full segment = whole line highlights at once
        zh_text = zh_translations[i] if i < len(zh_translations) else ''
        if zh_text:
            main_text = f"{{\\kf{dur_cs}}}{zh_text}"
            events.append(f"Dialogue: 0,{start_ts},{end_ts},Main,,0,0,0,,{main_text}")

        # English SECONDARY: plain text
        en_text = get_line_text(line_words)
        events.append(f"Dialogue: 1,{start_ts},{end_ts},Secondary,,0,0,0,,{en_text}")

    return ass + '\n'.join(events) + '\n'

def burn_captions(video_file, ass_file, output_file):
    print(f"\nBurning captions into video...")
    ass_path = os.path.abspath(ass_file).replace('\\', '/').replace(':', '\\:')
    cmd = [
        'ffmpeg', '-y', '-i', video_file,
        '-vf', f"subtitles='{ass_path}'",
        '-c:v', 'libx264', '-crf', '20', '-preset', 'fast',
        '-c:a', 'copy',
        output_file
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"FFmpeg error:\n{result.stderr[-500:]}")
        return False
    print(f"Done: {output_file}")
    return True

def main():
    if len(sys.argv) < 4:
        print("Usage: make_bilingual_zh_main.py <video.mp4> <words.json> <output.mp4>")
        sys.exit(1)

    video_file = sys.argv[1]
    words_json = sys.argv[2]
    output_file = sys.argv[3]

    print(f"\nReading word timestamps from: {words_json}")
    with open(words_json, 'r') as f:
        data = json.load(f)

    words = data if isinstance(data, list) else data.get('words', [])
    print(f"  Words loaded: {len(words)}")

    lines = group_words(words, max_per_line=8)
    print(f"  Lines grouped: {len(lines)}")

    # Get English text for each line
    lines_text = [get_line_text(line) for line in lines]

    groq_api_key = os.environ.get('GROQ_API_KEY', '')
    if not groq_api_key:
        print("Error: GROQ_API_KEY not set")
        sys.exit(1)

    # Translate to Chinese
    zh_translations = translate_to_chinese(lines_text, groq_api_key)

    # Generate ASS
    print("\nGenerating ASS file...")
    ass_content = generate_ass_zh_main(lines, zh_translations)
    ass_file = Path(video_file).stem + '_zh_main.ass'
    with open(ass_file, 'w', encoding='utf-8') as f:
        f.write(ass_content)
    print(f"ASS file: {ass_file}")

    # Burn into video
    burn_captions(video_file, ass_file, output_file)
    print(f"\n✅ Done! Output: {output_file}")

if __name__ == '__main__':
    main()
