#!/usr/bin/env bash
# concat_with_xfade.sh — concat N anchor clips into one ACT mp4 with a 0.15s
# video xfade + audio acrossfade at every seam. Hides per-clip micro-cuts
# without bleeding identity drift across the ACT.
#
# Usage:
#   concat_with_xfade.sh <output.mp4> <clip1.mp4> <clip2.mp4> [clip3.mp4 ...]
#
# Assumes every clip is the same duration (default 10s). If you mix durations,
# adapt the offset math below — each xfade offset is
# (cumulative_duration_so_far − 0.15).

set -euo pipefail

XFADE_DURATION=0.15
CLIP_DURATION=10  # seconds; adjust if your clips are not 10s each

if [ "$#" -lt 3 ]; then
  echo "usage: $0 <output.mp4> <clip1.mp4> <clip2.mp4> [clip3.mp4 ...]" >&2
  exit 1
fi

OUT="$1"; shift
CLIPS=("$@")
N=${#CLIPS[@]}

INPUTS=()
for c in "${CLIPS[@]}"; do
  INPUTS+=(-i "$c")
done

# Build the filter graph.
# For N clips:
#   [0:v][1:v]xfade=...:offset=O1[v01];
#   [v01][2:v]xfade=...:offset=O2[v02];
#   ...
#   [v_{N-2}][N-1:v]xfade=...:offset=O_{N-1}[vout]
# Audio mirrors with acrossfade.
FILTER=""
for ((i=1; i<N; i++)); do
  PREV_V=$([ $i -eq 1 ] && echo "[0:v]" || printf "[v%02d]" $((i-1)))
  PREV_A=$([ $i -eq 1 ] && echo "[0:a]" || printf "[a%02d]" $((i-1)))
  THIS_V="[${i}:v]"
  THIS_A="[${i}:a]"
  OFFSET=$(awk -v c=$CLIP_DURATION -v x=$XFADE_DURATION -v i=$i \
            'BEGIN{printf "%.3f", i*c - i*x}')
  if [ $i -eq $((N-1)) ]; then
    OUT_V="[vout]"
    OUT_A="[aout]"
  else
    OUT_V=$(printf "[v%02d]" $i)
    OUT_A=$(printf "[a%02d]" $i)
  fi
  FILTER+="${PREV_V}${THIS_V}xfade=transition=fade:duration=${XFADE_DURATION}:offset=${OFFSET}${OUT_V};"
  FILTER+="${PREV_A}${THIS_A}acrossfade=d=${XFADE_DURATION}${OUT_A};"
done

# Strip trailing semicolon
FILTER="${FILTER%;}"

ffmpeg -y "${INPUTS[@]}" -filter_complex "$FILTER" \
  -map "[vout]" -map "[aout]" \
  -c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p \
  -c:a aac -b:a 192k \
  "$OUT"

echo "→ wrote $OUT (concat of $N clips with ${XFADE_DURATION}s xfade per seam)"
