#!/bin/bash
# Audio mixer for screen-to-promo
# Usage: audio_mix.sh <output.m4a> <target_lufs> <audio1.wav> [gap] <audio2.wav> [gap] ...
# "gap" = insert 0.5s silence between segments

set -euo pipefail

OUTPUT="$1"; shift
TARGET_LUFS="$1"; shift

TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT

IDX=0
INPUTS=""
FILTER=""
CONCAT_N=0

while [[ $# -gt 0 ]]; do
    if [[ "$1" == "gap" ]]; then
        # Insert 0.5s silence
        SIL="$TMPDIR/silence_${IDX}.wav"
        ffmpeg -y -f lavfi -i anullsrc=r=44100:cl=stereo -t 0.5 -acodec pcm_s16le "$SIL" 2>/dev/null
        INPUTS="$INPUTS -i $SIL"
        FILTER="${FILTER}[$CONCAT_N]aresample=44100,aformat=sample_fmts=fltp:channel_layouts=stereo[s${CONCAT_N}]; "
        CONCAT_N=$((CONCAT_N + 1))
        shift
        continue
    fi

    FILE="$1"; shift
    INPUTS="$INPUTS -i $FILE"

    # Check if this is the first segment (often original audio — skip loudnorm to preserve quality)
    if [[ $IDX -eq 0 && "${SKIP_FIRST_NORM:-}" == "1" ]]; then
        FILTER="${FILTER}[$CONCAT_N]aresample=44100,aformat=sample_fmts=fltp:channel_layouts=stereo[s${CONCAT_N}]; "
    else
        FILTER="${FILTER}[$CONCAT_N]aresample=44100,aformat=sample_fmts=fltp:channel_layouts=stereo,loudnorm=I=${TARGET_LUFS}:TP=-3:LRA=11[s${CONCAT_N}]; "
    fi
    CONCAT_N=$((CONCAT_N + 1))
    IDX=$((IDX + 1))
done

# Build concat filter
CONCAT_INPUTS=""
for ((i=0; i<CONCAT_N; i++)); do
    CONCAT_INPUTS="${CONCAT_INPUTS}[s${i}]"
done
FILTER="${FILTER}${CONCAT_INPUTS}concat=n=${CONCAT_N}:v=0:a=1[out]"

eval ffmpeg -y $INPUTS -filter_complex "\"$FILTER\"" -map '"[out]"' -c:a aac -b:a 192k "$OUTPUT" 2>&1 | tail -3

DUR=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$OUTPUT")
echo "Mixed: ${DUR}s → $OUTPUT"
