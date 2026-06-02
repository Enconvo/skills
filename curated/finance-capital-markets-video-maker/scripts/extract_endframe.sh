#!/usr/bin/env bash
# extract_endframe.sh <input.mp4> <output.jpg>
# Extracts the last frame of <input.mp4> as a high-quality JPEG.
# Usage: bash extract_endframe.sh v8_clips/v8_s03.mp4 v8_clips/v8_s03_end.jpg
set -euo pipefail
if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <input.mp4> <output.jpg>" >&2
  exit 1
fi
INPUT="$1"
OUTPUT="$2"
ffmpeg -hide_banner -loglevel error -sseof -0.1 -i "$INPUT" -frames:v 1 -q:v 2 -y "$OUTPUT"
echo "endframe: $OUTPUT"
