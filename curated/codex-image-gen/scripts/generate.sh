#!/bin/bash
# codex-image-gen: Generate an image via Codex CLI using ChatGPT Pro OAuth.
#
# Usage:
#   T2I:  generate.sh "prompt" /path/to/output.png
#   I2I:  generate.sh "prompt" /path/to/output.png /path/to/ref1.png [/path/to/ref2.png ...]
#
# Image-to-image: pass one or more reference image paths after the output path.
# Codex will attach them to the prompt and the imagegen skill will use them as
# likeness/style references.

set -euo pipefail

PROMPT="${1:-}"
OUTPUT_PATH="${2:-}"

if [[ -z "$PROMPT" || -z "$OUTPUT_PATH" ]]; then
  cat >&2 <<EOF
Usage:
  T2I: $0 "prompt" /path/to/output.png
  I2I: $0 "prompt" /path/to/output.png /path/to/ref1.png [/path/to/ref2.png ...]
EOF
  exit 2
fi

if ! command -v codex >/dev/null 2>&1; then
  echo "ERROR: codex CLI not found. Install with: npm i -g @openai/codex" >&2
  exit 3
fi

# Shift off prompt + output; the rest are reference images.
shift 2
REF_IMAGES=("$@")

# Validate reference images exist.
for ref in "${REF_IMAGES[@]}"; do
  if [[ ! -f "$ref" ]]; then
    echo "ERROR: reference image not found: $ref" >&2
    exit 4
  fi
done

# Resolve output path to absolute (portable across macOS/Linux).
OUTPUT_PATH="$(python3 -c 'import os,sys; print(os.path.abspath(sys.argv[1]))' "$OUTPUT_PATH")"
OUTPUT_DIR="$(dirname "$OUTPUT_PATH")"
mkdir -p "$OUTPUT_DIR"

# Build codex args: --image flag for each reference image.
# `--image <FILE>...` is variadic in codex; use `--` later to delimit the prompt.
CODEX_ARGS=(
  exec
  --skip-git-repo-check
  --add-dir "$OUTPUT_DIR"
)
for ref in "${REF_IMAGES[@]}"; do
  CODEX_ARGS+=(--image "$ref")
done

# Build instruction. If references are provided, frame as i2i.
if [[ ${#REF_IMAGES[@]} -gt 0 ]]; then
  INSTRUCTION="Generate an image using the attached reference image(s) for likeness/style guidance.

Prompt: ${PROMPT}

After generation, save (or copy) the resulting PNG to exactly this absolute path, overwriting if it exists:
${OUTPUT_PATH}

Then confirm with one line: SAVED: ${OUTPUT_PATH}"
else
  INSTRUCTION="Generate an image: ${PROMPT}

After generation, save (or copy) the resulting PNG to exactly this absolute path, overwriting if it exists:
${OUTPUT_PATH}

Then confirm with one line: SAVED: ${OUTPUT_PATH}"
fi

# `--` delimits end of options so the prompt isn't consumed by --image's variadic FILE list.
CODEX_ARGS+=(-- "$INSTRUCTION")

LOG=/tmp/codex-image-gen.log
codex "${CODEX_ARGS[@]}" >"$LOG" 2>&1

if [[ -f "$OUTPUT_PATH" ]]; then
  echo "$OUTPUT_PATH"
  exit 0
fi

echo "ERROR: codex did not produce $OUTPUT_PATH" >&2
echo "--- last 30 lines of $LOG ---" >&2
tail -30 "$LOG" >&2
exit 1
