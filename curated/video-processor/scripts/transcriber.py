#!/usr/bin/env python3
"""
Transcriber - Extract transcript from video/audio using Groq Whisper Large V3
Supports: Local files (MP4, MP3, WAV, M4A, etc.) and URLs (YouTube, Twitter, etc.)
Usage: transcriber.py <video_file_or_url> [groq_api_key]
"""
import sys
import os
import re
import json
import subprocess
from pathlib import Path

# Import URL helper
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
from url_helper import is_url, download_from_url

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def get_video_info(video_file):
    """Get video duration and basic info"""
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
         '-of', 'default=noprint_wrappers=1:nokey=1', video_file],
        capture_output=True, text=True
    )
    duration = float(result.stdout.strip())
    return {'duration': duration}

def transcribe_video(video_file, groq_api_key, source_lang='en'):
    """Transcribe video/audio using Groq Whisper Large V3"""
    from groq import Groq

    # Detect file type
    ext = Path(video_file).suffix.lower()
    if ext in ['.mp3', '.m4a', '.wav', '.flac', '.ogg', '.aac']:
        file_type = "Audio"
    else:
        file_type = "Video"

    print_header(f"Step 1: Transcribing {file_type}")
    print(f"Using: Groq Whisper Large V3")
    print(f"Language: {source_lang}")
    print(f"This should be very fast (20-30x realtime)...\n")

    client = Groq(api_key=groq_api_key)

    with open(video_file, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            file=(video_file, audio_file.read()),
            model="whisper-large-v3",
            response_format="verbose_json",
            language=source_lang,
            timestamp_granularities=["segment"]
        )

    # Convert to SRT
    srt_content = ""
    for i, segment in enumerate(transcription.segments, 1):
        start = segment['start']
        end = segment['end']
        text = segment['text'].strip()

        start_time = seconds_to_srt_time(start)
        end_time = seconds_to_srt_time(end)

        srt_content += f"{i}\n{start_time} --> {end_time}\n{text}\n\n"

    # Save original SRT
    base_name = Path(video_file).stem
    original_srt = f"{base_name}_original.srt"
    with open(original_srt, 'w', encoding='utf-8') as f:
        f.write(srt_content)

    print(f"Transcript saved: {original_srt}")
    print(f"   Segments: {len(transcription.segments)}")
    if transcription.segments:
        print(f"   Preview: {transcription.segments[0]['text'][:60]}...")

    return srt_content, original_srt

def seconds_to_srt_time(seconds):
    """Convert seconds to SRT timestamp format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

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

def extract_plain_text(srt_content):
    """Convert SRT content to plain text transcript"""
    lines = []
    for block in srt_content.strip().split('\n\n'):
        block_lines = block.split('\n')
        if len(block_lines) >= 3:
            text = '\n'.join(block_lines[2:])
            lines.append(text.strip())
    return '\n'.join(lines)

def main():
    if len(sys.argv) < 2:
        print("Usage: transcriber.py <video_file_or_url> [groq_api_key]")
        print("Example: transcriber.py video.mp4")
        print("Example: transcriber.py https://youtube.com/watch?v=xxx gsk_xxx")
        print("Supports: Local files (MP4, MP3, WAV, M4A) and URLs (YouTube, Twitter, etc.)")
        sys.exit(1)

    input_source = sys.argv[1]
    groq_api_key = sys.argv[2] if len(sys.argv) > 2 else os.getenv('GROQ_API_KEY')

    if not groq_api_key:
        print("Error: GROQ_API_KEY not provided")
        print("")
        print("   Groq API key is needed for Whisper transcription only.")
        print("   All text intelligence (translation, summarization, condensation)")
        print("   is handled by the host agent — no LLM API needed.")
        print("")
        print("   Groq Whisper Large V3:")
        print("   - Fast (20-30x realtime)")
        print("   - Free tier available")
        print("   - Native SRT output with timestamps")
        print("   - Stable for long videos (tested 2h+, 1500+ segments)")
        print("")
        print("   Get your free key at: https://console.groq.com")
        print("   Then: export GROQ_API_KEY=gsk_xxx")
        print("   Or add to .env file in the skill root directory")
        sys.exit(1)

    # Check if input is URL or local file
    if is_url(input_source):
        # Download from URL
        video_file, file_type = download_from_url(input_source, output_dir=".")
        print(f"Downloaded {file_type}: {video_file}\n")
    else:
        # Local file
        video_file = input_source
        if not os.path.exists(video_file):
            print(f"Error: File not found: {video_file}")
            sys.exit(1)

    base_name = Path(video_file).stem

    # Step 1: Transcribe
    original_srt_content, original_srt_file = transcribe_video(video_file, groq_api_key)

    # Step 2: Extract plain text transcript
    transcript_text = extract_plain_text(original_srt_content)
    transcript_file = f"{base_name}_transcript.txt"
    with open(transcript_file, 'w', encoding='utf-8') as f:
        f.write(transcript_text)
    print(f"Plain text transcript: {transcript_file}")

    # Output status file for agent to check
    status = {
        'video_file': video_file,
        'original_srt': original_srt_file,
        'transcript_txt': transcript_file,
        'segments': len(parse_srt(original_srt_content)),
        'status': 'transcribed'
    }

    with open(f"{base_name}_status.json", 'w') as f:
        json.dump(status, f, indent=2)

    print("\n" + "="*60)
    print("Transcription complete!")
    print("="*60)
    print(f"\nFiles created:")
    print(f"  {original_srt_file} (SRT with timestamps)")
    print(f"  {transcript_file} (plain text)")
    print(f"\nNext: Agent handles cleanup, translation, summary, or dubbing")

if __name__ == "__main__":
    main()
