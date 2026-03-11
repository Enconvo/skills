#!/bin/bash
# Audio mixer for screen-to-promo pipeline
# Concatenates audio segments with optional silence gaps and loudness normalization.
#
# Usage: audio_mix.sh <output.m4a> <target_lufs> <audio1.wav> [gap] <audio2.wav> [gap] ...
#   "gap" = insert 0.5s silence between segments
#
# Environment:
#   SKIP_FIRST_NORM=1  — skip loudnorm on the first audio file (preserve original quality,
#                        useful for Veo/source audio that shouldn't be re-normalized)
#
# Example:
#   audio_mix.sh output.m4a -25 hook.wav gap demo_vo.wav gap outro_vo.wav
#   SKIP_FIRST_NORM=1 audio_mix.sh output.m4a -25 veo_audio.wav gap vo.wav

set -euo pipefail

# --- Dependency check ---
if ! command -v ffmpeg &>/dev/null; then
    echo "Error: ffmpeg not found." >&2
    exit 1
fi

if [[ $# -lt 3 ]]; then
    echo "Usage: audio_mix.sh <output.m4a> <target_lufs> <audio1.wav> [gap] <audio2.wav> ..." >&2
    exit 1
fi

OUTPUT="$1"; shift
TARGET_LUFS="$1"; shift

TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

# Collect inputs and build filter
declare -a INPUT_FILES
FILTER=""
CONCAT_N=0
AUDIO_IDX=0

while [[ $# -gt 0 ]]; do
    if [[ "$1" == "gap" ]]; then
        # Insert 0.5s silence
        SIL="$TMPDIR/silence_${CONCAT_N}.wav"
        ffmpeg -y -f lavfi -i anullsrc=r=44100:cl=stereo -t 0.5 -acodec pcm_s16le "$SIL" 2>/dev/null
        INPUT_FILES+=("$SIL")
        FILTER="${FILTER}[${CONCAT_N}]aresample=44100,aformat=sample_fmts=fltp:channel_layouts=stereo[s${CONCAT_N}]; "
        CONCAT_N=$((CONCAT_N + 1))
        shift
        continue
    fi

    FILE="$1"; shift
    if [[ ! -f "$FILE" ]]; then
        echo "Error: Audio file not found: $FILE" >&2
        exit 1
    fi
    INPUT_FILES+=("$FILE")

    # Skip loudnorm on first audio file if SKIP_FIRST_NORM=1
    if [[ $AUDIO_IDX -eq 0 && "${SKIP_FIRST_NORM:-}" == "1" ]]; then
        FILTER="${FILTER}[${CONCAT_N}]aresample=44100,aformat=sample_fmts=fltp:channel_layouts=stereo[s${CONCAT_N}]; "
    else
        FILTER="${FILTER}[${CONCAT_N}]aresample=44100,aformat=sample_fmts=fltp:channel_layouts=stereo,loudnorm=I=${TARGET_LUFS}:TP=-3:LRA=11[s${CONCAT_N}]; "
    fi
    CONCAT_N=$((CONCAT_N + 1))
    AUDIO_IDX=$((AUDIO_IDX + 1))
done

if [[ $CONCAT_N -eq 0 ]]; then
    echo "Error: No audio inputs provided." >&2
    exit 1
fi

# Build concat filter
CONCAT_INPUTS=""
for ((i = 0; i < CONCAT_N; i++)); do
    CONCAT_INPUTS="${CONCAT_INPUTS}[s${i}]"
done
FILTER="${FILTER}${CONCAT_INPUTS}concat=n=${CONCAT_N}:v=0:a=1[out]"

# Build ffmpeg command with proper quoting via array
CMD=(ffmpeg -y)
for f in "${INPUT_FILES[@]}"; do
    CMD+=(-i "$f")
done
CMD+=(-filter_complex "$FILTER" -map "[out]" -c:a aac -b:a 192k "$OUTPUT")

"${CMD[@]}" 2>&1 | tail -3

DUR=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$OUTPUT")
echo "Mixed: ${DUR}s → $OUTPUT"
