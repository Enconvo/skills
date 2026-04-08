#!/bin/bash
# Generate TTS audio with perfect subtitle sync and create dubbed video
# Usage: generate_tts_and_dub.sh <video_file> <original_srt> <translated_srt> <target_lang> [voice_profile] [voice_name]
#
# Uses numpy timeline assembly (scales to 1500+ segments).
# edge-tts runs async parallel (batches of 10) for speed.
# Timing analysis identifies overlong segments for agent-driven condensation.
#
# Set WORK_DIR env var to reuse a previous work directory (for condensation re-runs).

set -e

VIDEO_FILE="$1"
ORIGINAL_SRT="$2"
TRANSLATED_SRT="$3"
TARGET_LANG="$4"
VOICE_PROFILE="$5"  # Optional: voicebox profile name OR "none" to skip
VOICE_NAME="$6"     # Optional: specific voice ID override (e.g. en-US-BrianNeural)

# Audio mix mode: "mix" (default) = original audio lowered + dub overlay; "replace" = dub only
MIX_MODE="${MIX_MODE:-mix}"
# Original audio volume when mixing (0.0-1.0, default 0.15 = 15%)
MIX_ORIGINAL_VOLUME="${MIX_ORIGINAL_VOLUME:-0.15}"
# Subtitle burning: "yes" = burn dual subs; "no" (default) = no burned subs
BURN_SUBS="${BURN_SUBS:-no}"

if [ -z "$VIDEO_FILE" ] || [ -z "$ORIGINAL_SRT" ] || [ -z "$TRANSLATED_SRT" ] || [ -z "$TARGET_LANG" ]; then
    echo "Usage: generate_tts_and_dub.sh <video_file> <original_srt> <translated_srt> <target_lang> [voice_profile] [voice_name]"
    echo "  voice_profile: voicebox profile name, or omit for auto-select"
    echo "  voice_name: specific voice ID (e.g. en-US-BrianNeural, am_michael)"
    echo ""
    echo "  Set WORK_DIR env var to reuse a previous work directory (for re-runs after condensation)"
    exit 1
fi

BASE_NAME=$(basename "$VIDEO_FILE" | sed 's/\.[^.]*$//')
WORK_DIR="${WORK_DIR:-/tmp/tts_work_$$}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "========================================"
echo "  Generating Synced TTS Audio"
echo "========================================"
echo ""
echo "Video: $VIDEO_FILE"
echo "Target: $TARGET_LANG"
echo "Work dir: $WORK_DIR"
echo ""

# Create working directory
mkdir -p "$WORK_DIR"

# Determine TTS engine (with availability checks)
if [ -n "$VOICE_PROFILE" ] && [ "$VOICE_PROFILE" != "none" ]; then
    VOICEBOX_SCRIPT="$HOME/.claude/skills/voicebox/scripts/voicebox.py"
    if [ -f "$VOICEBOX_SCRIPT" ]; then
        TTS_ENGINE="voicebox"
        echo "Using: Voicebox voice cloning (profile: $VOICE_PROFILE)"
        # Warn about long videos
        VIDEO_DUR_CHECK=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$VIDEO_FILE" 2>/dev/null || echo "0")
        VIDEO_MINS=$(echo "$VIDEO_DUR_CHECK / 60" | bc 2>/dev/null || echo "0")
        if [ "$VIDEO_MINS" -gt 5 ] 2>/dev/null; then
            echo ""
            echo "Video is ~${VIDEO_MINS} min long."
            echo "   Voicebox generates sequentially — best for short videos (1-5 min)."
            echo "   For long videos, edge-tts is much faster (parallel generation)."
        fi
    else
        echo "Voicebox skill not installed. Voice profile '$VOICE_PROFILE' cannot be used."
        echo "   Install from: https://github.com/EnConvo/skill/tree/main/curated/voicebox"
        echo "   Voicebox supports: Qwen-TTS Clone, Designed voices, Custom_Voice presets."
        echo "   Note: Best for short videos (1-5 min). Long videos take too long."
        echo ""
        echo "   Falling back to edge-tts..."
        TTS_ENGINE="edge-tts"
        VOICE_PROFILE="none"
    fi
else
    TTS_ENGINE="edge-tts"
    echo "Using: edge-tts (cloud, parallel)"
fi
echo ""

# Build sync_tts.py arguments
SYNC_ARGS=("$TRANSLATED_SRT" "$WORK_DIR" "$TTS_ENGINE" "$TARGET_LANG")
if [ -n "$VOICE_PROFILE" ] && [ "$VOICE_PROFILE" != "none" ]; then
    SYNC_ARGS+=("$VOICE_PROFILE")
fi
if [ -n "$VOICE_NAME" ]; then
    # If no voice_profile but we have voice_name, add placeholder
    if [ -z "$VOICE_PROFILE" ] || [ "$VOICE_PROFILE" = "none" ]; then
        SYNC_ARGS+=("none")
    fi
    SYNC_ARGS+=("$VOICE_NAME")
fi

# Generate and sync TTS (parallel edge-tts + numpy timeline)
python3 "$SCRIPT_DIR/sync_tts.py" "${SYNC_ARGS[@]}"

echo ""

# Copy timing report to CWD if it exists
if [ -f "$WORK_DIR/timing_report.json" ]; then
    cp "$WORK_DIR/timing_report.json" "${BASE_NAME}_timing_report.json"
    echo "Timing report: ${BASE_NAME}_timing_report.json"
fi

# The combined WAV is already built by sync_tts.py using numpy timeline
COMBINED_WAV="$WORK_DIR/combined.wav"

if [ ! -f "$COMBINED_WAV" ]; then
    echo "ERROR: Combined audio not found at $COMBINED_WAV"
    exit 1
fi

# Get video duration and trim/normalize
VIDEO_DUR=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$VIDEO_FILE")

echo "Trimming to video duration and normalizing..."
ffmpeg -y -i "$COMBINED_WAV" -t "$VIDEO_DUR" -af "volume=1.5" -ar 24000 -ac 1 "${BASE_NAME}_${TARGET_LANG}_audio.wav" 2>/dev/null

echo "Synced audio: ${BASE_NAME}_${TARGET_LANG}_audio.wav"
echo ""

# Create dubbed video
echo "========================================"
if [ "$BURN_SUBS" = "yes" ]; then
    echo "  Creating Dubbed Video (Burned-In Subs)"
else
    echo "  Creating Dubbed Video"
fi
echo "  Audio: $MIX_MODE mode$([ "$MIX_MODE" = "mix" ] && echo " (original at ${MIX_ORIGINAL_VOLUME})")"
echo "========================================"
echo ""

MUX_LOG="$WORK_DIR/mux.log"
MUX_OK=false
DUB_AUDIO="${BASE_NAME}_${TARGET_LANG}_audio.wav"

# Step A: Prepare the final audio track
if [ "$MIX_MODE" = "mix" ]; then
    echo "Mixing: original audio at ${MIX_ORIGINAL_VOLUME} volume + dubbed voice overlay..."
    MIXED_AUDIO="$WORK_DIR/mixed_audio.wav"
    ffmpeg -y \
        -i "$VIDEO_FILE" \
        -i "$DUB_AUDIO" \
        -filter_complex "[0:a]volume=${MIX_ORIGINAL_VOLUME}[orig];[1:a]volume=1.0[dub];[orig][dub]amix=inputs=2:duration=first:dropout_transition=0[mixed]" \
        -map "[mixed]" \
        "$MIXED_AUDIO" > "$MUX_LOG" 2>&1
    FINAL_AUDIO="$MIXED_AUDIO"
    echo "  Mixed audio ready."
else
    echo "Replace mode: using dubbed audio only (no original audio)."
    FINAL_AUDIO="$DUB_AUDIO"
fi
echo ""

# Step B: Mux video + audio, optionally burn subtitles

# Escape SRT paths for ffmpeg filter (colons, backslashes, single quotes, brackets)
escape_srt_path() {
    echo "$1" | sed "s/\\\\/\\\\\\\\\\\\\\\\/g; s/:/\\\\\\\\:/g; s/'/\\\\\\\\'/g; s/\\[/\\\\\\\\[/g; s/\\]/\\\\\\\\]/g"
}

if [ "$BURN_SUBS" = "yes" ]; then
    # Verify SRT files exist
    HAVE_ORIG_SRT=false
    HAVE_TRANS_SRT=false
    [ -f "$ORIGINAL_SRT" ] && HAVE_ORIG_SRT=true && echo "Original SRT: $ORIGINAL_SRT ($(wc -l < "$ORIGINAL_SRT") lines)"
    [ -f "$TRANSLATED_SRT" ] && HAVE_TRANS_SRT=true && echo "Translated SRT: $TRANSLATED_SRT ($(wc -l < "$TRANSLATED_SRT") lines)"
    echo ""

    # Try burning in dual subtitles (original on top, translated on bottom)
    if $HAVE_ORIG_SRT && $HAVE_TRANS_SRT; then
        echo "Burning in dual subtitles (original top + translated bottom)..."
        ORIG_ESC=$(escape_srt_path "$ORIGINAL_SRT")
        TRANS_ESC=$(escape_srt_path "$TRANSLATED_SRT")
        FILTER="subtitles='${TRANS_ESC}':force_style='FontSize=20,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2,Shadow=1,MarginV=30',subtitles='${ORIG_ESC}':force_style='FontSize=16,PrimaryColour=&H0080FFFF,OutlineColour=&H00000000,Outline=2,Shadow=1,Alignment=6,MarginV=30'"
        if ffmpeg -y \
            -i "$VIDEO_FILE" \
            -i "$FINAL_AUDIO" \
            -map 0:v:0 -map 1:a:0 \
            -vf "$FILTER" \
            -c:v libx264 -crf 20 -preset fast \
            -c:a aac -b:a 192k \
            -shortest \
            "${BASE_NAME}_dubbed.mp4" > "$MUX_LOG" 2>&1; then
            MUX_OK=true
            echo "  Dual burned-in subtitles succeeded."
        else
            echo "  Dual burn-in failed, trying single..."
            tail -3 "$MUX_LOG"
        fi
    fi

    # Fallback: burn in translated subtitle only
    if ! $MUX_OK && $HAVE_TRANS_SRT; then
        echo "Burning in translated subtitles only..."
        TRANS_ESC=$(escape_srt_path "$TRANSLATED_SRT")
        FILTER="subtitles='${TRANS_ESC}':force_style='FontSize=20,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2,Shadow=1,MarginV=30'"
        if ffmpeg -y \
            -i "$VIDEO_FILE" \
            -i "$FINAL_AUDIO" \
            -map 0:v:0 -map 1:a:0 \
            -vf "$FILTER" \
            -c:v libx264 -crf 20 -preset fast \
            -c:a aac -b:a 192k \
            -shortest \
            "${BASE_NAME}_dubbed.mp4" > "$MUX_LOG" 2>&1; then
            MUX_OK=true
            echo "  Single burned-in subtitle succeeded."
        else
            echo "  Single burn-in failed:"
            tail -3 "$MUX_LOG"
        fi
    fi
fi

# No subs or sub burning failed/skipped: mux video + audio directly
if ! $MUX_OK; then
    if [ "$BURN_SUBS" = "yes" ]; then
        echo "WARNING: Subtitle burning failed — creating video WITHOUT subtitles."
        echo "   SRT files are still available separately."
    fi
    ffmpeg -y \
        -i "$VIDEO_FILE" \
        -i "$FINAL_AUDIO" \
        -map 0:v:0 -map 1:a:0 \
        -c:v copy \
        -c:a aac -b:a 192k \
        -shortest \
        "${BASE_NAME}_dubbed.mp4" > "$MUX_LOG" 2>&1
fi

echo ""

# Conditional cleanup: if overlong segments exist, keep work dir for potential re-run
if [ -f "${BASE_NAME}_timing_report.json" ]; then
    OVERLONG_COUNT=$(python3 -c "import json; print(len(json.load(open('${BASE_NAME}_timing_report.json'))))" 2>/dev/null || echo "0")
    if [ "$OVERLONG_COUNT" -gt 0 ]; then
        echo "Keeping work dir for potential condensation re-run: $WORK_DIR"
        echo "(${OVERLONG_COUNT} overlong segments detected — agent may condense and re-run)"
        rm -f "${BASE_NAME}_${TARGET_LANG}_audio.wav"
    else
        echo "Cleaning up temporary files..."
        rm -rf "$WORK_DIR"
        rm -f "${BASE_NAME}_${TARGET_LANG}_audio.wav"
    fi
else
    echo "Cleaning up temporary files..."
    rm -rf "$WORK_DIR"
    rm -f "${BASE_NAME}_${TARGET_LANG}_audio.wav"
fi

echo ""
echo "========================================"
echo "  DONE!"
echo "========================================"
echo ""
echo "Output files:"
echo "  - ${BASE_NAME}_original.srt"
echo "  - ${BASE_NAME}_${TARGET_LANG}.srt"
echo "  - ${BASE_NAME}_dubbed.mp4"
echo ""
echo "Audio: $MIX_MODE mode$([ "$MIX_MODE" = "mix" ] && echo " (original at ${MIX_ORIGINAL_VOLUME}, dub overlay at full volume)")"
if [ "$BURN_SUBS" = "yes" ]; then
    echo "Subtitles: burned into video (original top/yellow + translated bottom/white)"
else
    echo "Subtitles: not burned in (SRT files available separately)"
fi
echo ""
