#!/usr/bin/env python3
"""
Caption Video - Burn word-level timestamp captions into video.
Uses Groq Whisper word-level timestamps to create karaoke-style captions
where each word highlights as it's spoken.

Usage: caption_video.py <video_file_or_url> [options]

Options:
  --style=<style>       Caption style: highlight (default), appear, underline
  --position=<pos>      Position: bottom (default), top, center
  --font-size=<size>    Font size (default: 26)
  --words-per-line=<n>  Max words per caption line (default: 8)
  --color=<hex>         Text color in hex BBGGRR (default: 00FFFFFF = white)
  --highlight=<hex>     Highlight color in hex BBGGRR (default: 0000FFFF = yellow)
  --output=<file>       Output filename (default: {name}_captioned.mp4)
  --srt-only            Only generate ASS subtitle file, don't burn into video
  --lang=<code>         Source language code (default: auto-detect)
  --bilingual=<lang>    Add secondary language translation below main captions
                        e.g. --bilingual=english, --bilingual=chinese
"""
import sys
import os
import re
import json
import subprocess
from pathlib import Path

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
from url_helper import is_url, download_from_url


def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def probe_video(video_file):
    """Get video dimensions and calculate optimal caption parameters.

    Returns dict with: width, height, aspect_ratio, play_res_x, play_res_y,
    main_font_size, secondary_font_size, main_margin_v, secondary_margin_v, outline.
    """
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-select_streams', 'v:0',
         '-show_entries', 'stream=width,height',
         '-of', 'json', video_file],
        capture_output=True, text=True
    )
    try:
        info = json.loads(result.stdout)
        w = info['streams'][0]['width']
        h = info['streams'][0]['height']
    except (json.JSONDecodeError, KeyError, IndexError):
        w, h = 1920, 1080  # fallback

    ar = w / h

    # PlayRes matches native resolution for pixel-perfect rendering
    play_res_x = w
    play_res_y = h

    # Font size scales with video height (base: 45pt main / 30pt secondary at 1080p)
    scale = h / 1080
    main_size = max(16, round(45 * scale))
    secondary_size = max(12, round(30 * scale))
    outline = max(1, round(2 * scale))

    # Margins as percentage of height (~13.3% main, ~9% secondary from bottom)
    # Slight AR adjustments: ultrawide pushes up a bit more
    if ar > 2.0:
        # Ultrawide (21:9, cinemascope) — push up slightly more
        main_margin_v = round(0.15 * h)
        secondary_margin_v = round(0.105 * h)
    else:
        # Standard (16:9, 4:3) and Portrait (9:16)
        main_margin_v = round(0.133 * h)
        secondary_margin_v = round(0.09 * h)

    params = {
        'width': w, 'height': h, 'aspect_ratio': ar,
        'play_res_x': play_res_x, 'play_res_y': play_res_y,
        'main_font_size': main_size, 'secondary_font_size': secondary_size,
        'main_margin_v': main_margin_v, 'secondary_margin_v': secondary_margin_v,
        'outline': outline,
    }

    print(f"  Video: {w}x{h} (AR {ar:.2f})")
    print(f"  Auto caption: font {main_size}pt, margins {main_margin_v}/{secondary_margin_v}px")

    return params


def transcribe_words(video_file, groq_api_key, source_lang=None):
    """Transcribe with word-level timestamps using Groq Whisper Large V3."""
    from groq import Groq

    print_header("Step 1: Word-Level Transcription")
    print("Using: Groq Whisper Large V3 (word timestamps)")
    print("This should be very fast (20-30x realtime)...\n")

    client = Groq(api_key=groq_api_key)

    kwargs = {
        "file": (video_file, open(video_file, "rb").read()),
        "model": "whisper-large-v3",
        "response_format": "verbose_json",
        "timestamp_granularities": ["word", "segment"],
    }
    if source_lang:
        kwargs["language"] = source_lang

    transcription = client.audio.transcriptions.create(**kwargs)

    words = []
    if hasattr(transcription, 'words') and transcription.words:
        for w in transcription.words:
            words.append({
                'word': w['word'].strip() if isinstance(w, dict) else w.word.strip(),
                'start': w['start'] if isinstance(w, dict) else w.start,
                'end': w['end'] if isinstance(w, dict) else w.end,
            })

    # Also get segments for fallback grouping
    segments = []
    if hasattr(transcription, 'segments') and transcription.segments:
        for s in transcription.segments:
            seg = s if isinstance(s, dict) else {'start': s.start, 'end': s.end, 'text': s.text}
            segments.append(seg)

    print(f"  Words: {len(words)}")
    print(f"  Segments: {len(segments)}")
    if words:
        preview = ' '.join(w['word'] for w in words[:10])
        print(f"  Preview: {preview}...")

    # Save word-level JSON
    base_name = Path(video_file).stem
    words_file = f"{base_name}_words.json"
    with open(words_file, 'w', encoding='utf-8') as f:
        json.dump({'words': words, 'segments': segments}, f, indent=2, ensure_ascii=False)
    print(f"  Word timestamps: {words_file}")

    return words, segments


def group_words_into_lines(words, max_words_per_line=8):
    """Group words into caption lines by clause/sentence boundaries.

    Strategy: split at punctuation boundaries first (commas, periods, etc.),
    then merge short clauses or split long ones. This ensures captions always
    show complete, meaningful phrases — never breaking mid-clause.
    """
    # Punctuation that marks clause/sentence boundaries (covers CJK + Latin)
    SENTENCE_END = set('。！？.!?')
    CLAUSE_END = set('，,、；;：:')

    def ends_with_punct(word_text):
        """Check if word ends with clause/sentence punctuation."""
        stripped = word_text.rstrip()
        if not stripped:
            return False, False
        last = stripped[-1]
        return last in SENTENCE_END, last in CLAUSE_END

    # Step 1: Split words into clauses at every punctuation boundary
    clauses = []
    current = []
    for w in words:
        current.append(w)
        is_sent, is_clause = ends_with_punct(w['word'])
        if is_sent or is_clause:
            clauses.append(current)
            current = []
    if current:
        clauses.append(current)

    # Step 2: Merge tiny clauses with neighbors, split oversized ones
    # A clause is "tiny" if it has fewer chars than a threshold
    MIN_CHARS = 4
    MAX_CHARS = max_words_per_line * 2  # generous limit for display

    merged = []
    for clause in clauses:
        char_count = sum(len(w['word'].rstrip('，,。.！!？?、；;：:')) for w in clause)

        if merged and char_count < MIN_CHARS:
            # Merge tiny clause into previous line
            merged[-1].extend(clause)
        elif char_count > MAX_CHARS:
            # Split oversized clause at roughly the midpoint
            mid = len(clause) // 2
            merged.append(clause[:mid])
            merged.append(clause[mid:])
        else:
            merged.append(clause)

    return merged


def translate_lines(lines, target_lang):
    """Translate each caption line to target language via EnConvo API."""
    import urllib.request

    print(f"  Translating {len(lines)} lines to {target_lang}...")
    translations = []

    for line_words in lines:
        text = ''.join(w['word'] for w in line_words)
        prompt = (
            f"Translate to {target_lang}. Return ONLY the translation, nothing else. "
            f"Keep it natural and concise for subtitles.\n\n{text}"
        )

        payload = json.dumps({
            "messages": [{"role": "user", "content": prompt}],
            "model": "anthropic/claude-sonnet-4-20250514",
            "stream": False
        }).encode()

        req = urllib.request.Request(
            "http://localhost:54535/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"}
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read())
                translated = result.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
                translations.append(translated)
        except Exception as e:
            # Fallback: return empty
            print(f"    Translation failed for '{text}': {e}")
            translations.append("")

    return translations


def get_line_text(line_words):
    """Extract plain text from a line of words."""
    return ''.join(w['word'] for w in line_words)


def generate_ass_bilingual(lines, translations, style_config):
    """Generate ASS with main language karaoke (top) + translation (below).

    Cinema-style bilingual subtitles:
    - Main language: PingFang SC (CJK) or Helvetica Neue, with karaoke highlighting
    - Secondary language: Helvetica Neue, clean white text below
    """
    vp = style_config.get('video_params', {})
    font_size = style_config.get('font_size', vp.get('main_font_size', 26))
    secondary_size = vp.get('secondary_font_size', max(int(font_size * 0.7), 16))
    highlight = style_config.get('highlight', '&H0000FFFF')  # yellow
    color = style_config.get('color', '&H00FFFFFF')  # white
    outline_color = '&H00000000'
    outline = vp.get('outline', 2)
    play_res_x = vp.get('play_res_x', 1920)
    play_res_y = vp.get('play_res_y', 1080)
    main_margin_v = vp.get('main_margin_v', 62)
    secondary_margin_v = vp.get('secondary_margin_v', 30)

    # Detect if main language is CJK (check first line's text)
    sample = get_line_text(lines[0]) if lines else ''
    is_cjk = any('\u4e00' <= c <= '\u9fff' or '\u3040' <= c <= '\u30ff' or '\uac00' <= c <= '\ud7af' for c in sample)
    main_font = 'PingFang SC' if is_cjk else 'Helvetica Neue'
    secondary_font = 'Helvetica Neue'

    ass_content = f"""[Script Info]
Title: Bilingual Word-Level Captions
ScriptType: v4.00+
PlayResX: {play_res_x}
PlayResY: {play_res_y}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Main,{main_font},{font_size},{highlight},{color},{outline_color},&H80000000,0,0,0,0,100,100,0,0,1,{outline},1,2,20,20,{main_margin_v},1
Style: Secondary,{secondary_font},{secondary_size},{color},{color},{outline_color},&H80000000,0,0,0,0,100,100,0,0,1,{outline},1,2,20,20,{secondary_margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    events = []
    for i, line_words in enumerate(lines):
        if not line_words:
            continue

        line_start = line_words[0]['start']
        line_end = line_words[-1]['end']
        start_ts = seconds_to_ass_time(line_start)
        end_ts = seconds_to_ass_time(line_end)

        # Main language with karaoke
        kara_parts = []
        for w in line_words:
            word_dur_cs = int((w['end'] - w['start']) * 100)
            if word_dur_cs < 1:
                word_dur_cs = 1
            kara_parts.append(f"{{\\kf{word_dur_cs}}}{w['word']} ")
        kara_text = ''.join(kara_parts).rstrip()
        events.append(f"Dialogue: 0,{start_ts},{end_ts},Main,,0,0,0,,{kara_text}")

        # Secondary language translation
        if i < len(translations) and translations[i]:
            events.append(f"Dialogue: 1,{start_ts},{end_ts},Secondary,,0,0,0,,{translations[i]}")

    return ass_content + '\n'.join(events) + '\n'


def seconds_to_ass_time(seconds):
    """Convert seconds to ASS timestamp: H:MM:SS.cc (centiseconds)."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int((seconds - int(seconds)) * 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def generate_ass_highlight(lines, style_config):
    """Generate ASS subtitle with karaoke-style word highlighting.

    Each word starts in the base color and switches to the highlight color
    at the exact moment it's spoken, using ASS \\kf (karaoke fill) tags.
    """
    vp = style_config.get('video_params', {})
    font_size = style_config.get('font_size', vp.get('main_font_size', 24))
    position = style_config.get('position', 'bottom')
    color = style_config.get('color', '&H00FFFFFF')  # white
    highlight = style_config.get('highlight', '&H0000FFFF')  # yellow
    outline_color = style_config.get('outline_color', '&H00000000')  # black
    outline = vp.get('outline', 2)
    play_res_x = vp.get('play_res_x', 1920)
    play_res_y = vp.get('play_res_y', 1080)
    main_margin_v = vp.get('main_margin_v', 40)

    # Position alignment
    if position == 'top':
        alignment = 8  # top center
        margin_v = vp.get('secondary_margin_v', 30)
    elif position == 'center':
        alignment = 5  # center
        margin_v = 0
    else:
        alignment = 2  # bottom center
        margin_v = main_margin_v

    ass_header = f"""[Script Info]
Title: Word-Level Captions
ScriptType: v4.00+
PlayResX: {play_res_x}
PlayResY: {play_res_y}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,PingFang SC,{font_size},{highlight},{color},{outline_color},&H80000000,0,0,0,0,100,100,0,0,1,{outline},1,{alignment},20,20,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    events = []
    for line_words in lines:
        if not line_words:
            continue

        line_start = line_words[0]['start']
        line_end = line_words[-1]['end']
        start_ts = seconds_to_ass_time(line_start)
        end_ts = seconds_to_ass_time(line_end)

        # Build karaoke text with \kf tags
        # \kf<duration_cs> = karaoke fill effect, duration in centiseconds
        # PrimaryColour = highlighted (spoken) color
        # SecondaryColour = unhighlighted (upcoming) color
        # \kf makes text transition from SecondaryColour to PrimaryColour
        kara_parts = []
        for w in line_words:
            word_dur_cs = int((w['end'] - w['start']) * 100)
            if word_dur_cs < 1:
                word_dur_cs = 1
            # Add gap before word if there's a pause from line start or previous word
            kara_parts.append(f"{{\\kf{word_dur_cs}}}{w['word']} ")

        kara_text = ''.join(kara_parts).rstrip()
        events.append(f"Dialogue: 0,{start_ts},{end_ts},Default,,0,0,0,,{kara_text}")

    return ass_header + '\n'.join(events) + '\n'


def generate_ass_appear(lines, style_config):
    """Generate ASS subtitle where words appear one by one as spoken."""
    vp = style_config.get('video_params', {})
    font_size = style_config.get('font_size', vp.get('main_font_size', 24))
    position = style_config.get('position', 'bottom')
    color = style_config.get('color', '&H00FFFFFF')
    outline_color = style_config.get('outline_color', '&H00000000')
    outline = vp.get('outline', 2)
    play_res_x = vp.get('play_res_x', 1920)
    play_res_y = vp.get('play_res_y', 1080)
    main_margin_v = vp.get('main_margin_v', 40)

    if position == 'top':
        alignment = 8
        margin_v = vp.get('secondary_margin_v', 30)
    elif position == 'center':
        alignment = 5
        margin_v = 0
    else:
        alignment = 2
        margin_v = main_margin_v

    ass_header = f"""[Script Info]
Title: Word-Level Captions
ScriptType: v4.00+
PlayResX: {play_res_x}
PlayResY: {play_res_y}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,PingFang SC,{font_size},{color},{color},{outline_color},&H80000000,0,0,0,0,100,100,0,0,1,{outline},1,{alignment},20,20,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    events = []
    for line_words in lines:
        if not line_words:
            continue

        line_end = line_words[-1]['end']

        # Each word appears at its start time and stays until the line ends
        accumulated = ""
        for i, w in enumerate(line_words):
            accumulated += w['word'] + " "
            start_ts = seconds_to_ass_time(w['start'])
            if i + 1 < len(line_words):
                end_ts = seconds_to_ass_time(line_words[i + 1]['start'])
            else:
                end_ts = seconds_to_ass_time(line_end)
            events.append(f"Dialogue: 0,{start_ts},{end_ts},Default,,0,0,0,,{accumulated.rstrip()}")

    return ass_header + '\n'.join(events) + '\n'


def generate_ass_underline(lines, style_config):
    """Generate ASS subtitle with the current word underlined/bolded."""
    vp = style_config.get('video_params', {})
    font_size = style_config.get('font_size', vp.get('main_font_size', 24))
    position = style_config.get('position', 'bottom')
    color = style_config.get('color', '&H00FFFFFF')
    highlight = style_config.get('highlight', '&H0000FFFF')
    outline_color = style_config.get('outline_color', '&H00000000')
    outline = vp.get('outline', 2)
    play_res_x = vp.get('play_res_x', 1920)
    play_res_y = vp.get('play_res_y', 1080)
    main_margin_v = vp.get('main_margin_v', 40)

    if position == 'top':
        alignment = 8
        margin_v = vp.get('secondary_margin_v', 30)
    elif position == 'center':
        alignment = 5
        margin_v = 0
    else:
        alignment = 2
        margin_v = main_margin_v

    ass_header = f"""[Script Info]
Title: Word-Level Captions
ScriptType: v4.00+
PlayResX: {play_res_x}
PlayResY: {play_res_y}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,PingFang SC,{font_size},{color},{color},{outline_color},&H80000000,0,0,0,0,100,100,0,0,1,{outline},1,{alignment},20,20,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    events = []
    for line_words in lines:
        if not line_words:
            continue

        line_start = line_words[0]['start']
        line_end = line_words[-1]['end']

        # For each word's duration, show full line with current word highlighted
        for i, w in enumerate(line_words):
            start_ts = seconds_to_ass_time(w['start'])
            end_ts = seconds_to_ass_time(w['end'])

            parts = []
            for j, ww in enumerate(line_words):
                if j == i:
                    # Current word: highlighted color + bold + underline
                    parts.append(f"{{\\c{highlight}\\b1\\u1}}{ww['word']}{{\\c{color}\\b0\\u0}}")
                else:
                    parts.append(ww['word'])

            text = ' '.join(parts)
            events.append(f"Dialogue: 0,{start_ts},{end_ts},Default,,0,0,0,,{text}")

    return ass_header + '\n'.join(events) + '\n'


def burn_captions(video_file, ass_file, output_file):
    """Burn ASS subtitles into video using ffmpeg."""
    print_header("Step 3: Burning Captions into Video")
    print(f"Encoding: {output_file}")

    # Use absolute path and escape for ffmpeg filter graph
    abs_ass = os.path.abspath(ass_file)
    # ffmpeg filter escaping: backslash, colon, single-quote, brackets
    escaped = abs_ass.replace('\\', '/').replace(':', '\\:').replace("'", "'\\''")

    cmd = [
        'ffmpeg', '-y',
        '-i', video_file,
        '-vf', f"ass='{escaped}'",
        '-c:v', 'libx264', '-crf', '20', '-preset', 'fast',
        '-c:a', 'copy',
        output_file
    ]

    # Run via shell to handle the filter escaping properly
    shell_cmd = f'''ffmpeg -y -i "{video_file}" -vf "ass='{escaped}'" -c:v libx264 -crf 20 -preset fast -c:a copy "{output_file}"'''
    result = subprocess.run(shell_cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        # Fallback: copy ASS to a simple temp path to avoid escaping issues
        import shutil
        tmp_ass = '/tmp/_caption_burn.ass'
        shutil.copy2(abs_ass, tmp_ass)
        cmd2 = [
            'ffmpeg', '-y',
            '-i', video_file,
            '-vf', f'ass={tmp_ass}',
            '-c:v', 'libx264', '-crf', '20', '-preset', 'fast',
            '-c:a', 'copy',
            output_file
        ]
        result2 = subprocess.run(cmd2, capture_output=True, text=True)
        if result2.returncode != 0:
            print(f"ERROR: ffmpeg failed:\n{result2.stderr[-500:]}")
            return False

    print(f"Done: {output_file}")
    return True


def parse_hex_color(color_str):
    """Parse color from various formats to ASS format &HBBGGRR."""
    color_str = color_str.strip().lstrip('&H').lstrip('#')
    if len(color_str) == 6:
        # Assume BBGGRR format already
        return f"&H00{color_str}"
    return f"&H00{color_str}"


def main():
    args = sys.argv[1:]

    if not args or args[0] in ('-h', '--help'):
        print(__doc__)
        sys.exit(0)

    # Parse positional arg
    input_source = args[0]

    # Parse options — all None means "auto from video probe"
    style = 'highlight'
    position = 'bottom'
    font_size = None  # auto from video
    words_per_line = 8
    color = '&H00FFFFFF'
    highlight = '&H0000FFFF'
    output_file = None
    srt_only = False
    source_lang = None
    bilingual = None

    for arg in args[1:]:
        if arg.startswith('--style='):
            style = arg.split('=', 1)[1]
        elif arg.startswith('--position='):
            position = arg.split('=', 1)[1]
        elif arg.startswith('--font-size='):
            font_size = int(arg.split('=', 1)[1])
        elif arg.startswith('--words-per-line='):
            words_per_line = int(arg.split('=', 1)[1])
        elif arg.startswith('--color='):
            color = parse_hex_color(arg.split('=', 1)[1])
        elif arg.startswith('--highlight='):
            highlight = parse_hex_color(arg.split('=', 1)[1])
        elif arg.startswith('--output='):
            output_file = arg.split('=', 1)[1]
        elif arg == '--srt-only':
            srt_only = True
        elif arg.startswith('--lang='):
            source_lang = arg.split('=', 1)[1]
        elif arg.startswith('--bilingual='):
            bilingual = arg.split('=', 1)[1]

    groq_api_key = os.getenv('GROQ_API_KEY')
    if not groq_api_key:
        print("Error: GROQ_API_KEY not set. Get your free key at https://console.groq.com")
        sys.exit(1)

    # Handle URL input
    if is_url(input_source):
        video_file, file_type = download_from_url(input_source, output_dir=".")
        print(f"Downloaded {file_type}: {video_file}\n")
    else:
        video_file = input_source
        if not os.path.exists(video_file):
            print(f"Error: File not found: {video_file}")
            sys.exit(1)

    base_name = Path(video_file).stem

    # Probe video for auto-sizing
    vp = probe_video(video_file)

    # Apply auto values, user overrides take precedence
    if font_size is None:
        font_size = vp['main_font_size']

    # Step 1: Transcribe with word-level timestamps
    words, segments = transcribe_words(video_file, groq_api_key, source_lang)

    if not words:
        print("ERROR: No word-level timestamps returned. Groq Whisper may not support")
        print("word timestamps for this audio. Try a different file.")
        sys.exit(1)

    # Step 2: Group words into lines
    print_header("Step 2: Generating Caption Subtitles")
    lines = group_words_into_lines(words, max_words_per_line=words_per_line)
    print(f"  Style: {style}")
    print(f"  Lines: {len(lines)}")
    print(f"  Words per line: {words_per_line}")

    style_config = {
        'font_size': font_size,
        'position': position,
        'color': color,
        'highlight': highlight,
        'video_params': vp,
    }

    if bilingual:
        # Bilingual mode: translate each line, then generate dual-language ASS
        translations = translate_lines(lines, bilingual)
        ass_content = generate_ass_bilingual(lines, translations, style_config)
    elif style == 'appear':
        ass_content = generate_ass_appear(lines, style_config)
    elif style == 'underline':
        ass_content = generate_ass_underline(lines, style_config)
    else:
        ass_content = generate_ass_highlight(lines, style_config)

    ass_file = f"{base_name}_captions.ass"
    with open(ass_file, 'w', encoding='utf-8') as f:
        f.write(ass_content)
    print(f"  Caption file: {ass_file}")

    if srt_only:
        print(f"\nDone! Caption file: {ass_file}")
        print("Use --srt-only was set, skipping video burn-in.")
        return

    # Step 3: Burn into video
    if not output_file:
        output_file = f"{base_name}_captioned.mp4"

    success = burn_captions(video_file, ass_file, output_file)

    if success:
        print(f"\n{'='*60}")
        print("  DONE!")
        print(f"{'='*60}")
        print(f"\nOutput: {output_file}")
        print(f"Captions: {ass_file}")
        print(f"Word data: {base_name}_words.json")
    else:
        print(f"\nCaption file generated: {ass_file}")
        print("Video burn-in failed. You can manually burn with:")
        print(f"  ffmpeg -i {video_file} -vf ass={ass_file} -c:v libx264 -crf 20 {output_file}")


if __name__ == "__main__":
    main()
