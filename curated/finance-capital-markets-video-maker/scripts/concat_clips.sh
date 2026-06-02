#!/usr/bin/env bash
# concat_clips.sh <clips_dir> <output.mp4> [glob]
# Concatenates all matching mp4 clips in <clips_dir> in lexical order into <output.mp4>.
# Re-encodes to a uniform 30fps GOP for safe HF rendering.
# Usage: bash concat_clips.sh v8_clips hf_act1/act1_anchor.mp4 'v8_s0[1-4].mp4'
set -euo pipefail
if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <clips_dir> <output.mp4> [glob]" >&2
  exit 1
fi
DIR="$1"
OUT="$2"
GLOB="${3:-*.mp4}"

TMP_LIST=$(mktemp -t concatlistXXXX).txt
trap 'rm -f "$TMP_LIST"' EXIT

cd "$DIR"
for f in $(ls $GLOB | sort); do
  printf "file '%s'\n" "$(pwd)/$f" >> "$TMP_LIST"
done
cd - >/dev/null

# First pass: concat losslessly to verify timing
ffmpeg -hide_banner -loglevel error -f concat -safe 0 -i "$TMP_LIST" \
  -c:v libx264 -r 30 -g 30 -keyint_min 30 -movflags +faststart \
  -c:a aac -b:a 192k -y "$OUT"

echo "concat output: $OUT"
ffprobe -hide_banner -v error -show_entries format=duration -of default=nokey=1:noprint_wrappers=1 "$OUT"
