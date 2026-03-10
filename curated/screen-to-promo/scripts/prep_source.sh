#!/bin/bash
# Prep a screen recording source into 1920x1080 frames at 30fps
# Handles any aspect ratio — scales to fit width, pads with white
# Usage: prep_source.sh <input_video> <output_frames_dir> [fps]

set -euo pipefail

INPUT="$1"
OUT_DIR="$2"
FPS="${3:-30}"

mkdir -p "$OUT_DIR"

# Get source dimensions
DIMS=$(ffprobe -v quiet -show_entries stream=width,height -of csv=p=0 "$INPUT" | head -1)
SRC_W=$(echo "$DIMS" | cut -d, -f1)
SRC_H=$(echo "$DIMS" | cut -d, -f2)

echo "Source: ${SRC_W}x${SRC_H}"

# Scale to fit 1920 width, pad to 1080 height with white
ffmpeg -y -i "$INPUT" \
  -vf "scale=1920:-2:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:white" \
  -r "$FPS" -q:v 2 -an \
  "$OUT_DIR/f_%04d.jpg" 2>&1 | tail -2

N=$(ls "$OUT_DIR"/f_*.jpg 2>/dev/null | wc -l | tr -d ' ')
echo "Extracted: $N frames at ${FPS}fps"

# Detect content bounds (for letterboxed sources)
python3 -c "
from PIL import Image
import numpy as np
img = Image.open('$OUT_DIR/f_0001.jpg')
arr = np.array(img)
rows = np.where(arr.mean(axis=(1,2)) < 250)[0]
if len(rows) and (rows[0] > 10 or rows[-1] < 1070):
    print(f'CONTENT_BOUNDS={rows[0]},{rows[-1]+1}')
    print(f'Content: {rows[-1]-rows[0]+1}px tall (letterboxed)')
else:
    print('CONTENT_BOUNDS=none')
    print('Content: full frame')
"
