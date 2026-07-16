#!/usr/bin/env bash
# build_audio.sh — assemble the EnConvo VO+bed+SFX mix and mux it onto a silent render.
#
#   Usage:  scripts/build_audio.sh <silent_render.mp4> <final_output.mp4>
#   Run from the scaffold root (asset paths are relative to it).
#
# The scene VO markers and the tick·tick·tock keycap SFX times are LOCKED to the
# stable 50.5s timeline — the same mix muxes onto BOTH the 16:9 and 9:16 renders,
# and onto ANY theme (Minimal / Line Art), because they share that timeline.
# Swap assets/vo/vo2..vo8.wav for your product; keep vo8 (the fixed EnConvo outro).
#
#   Env overrides:  FFMPEG=/path/to/ffmpeg   MIX=/path/to/mix.wav   FORCE=1 (rebuild mix)
set -euo pipefail

FFMPEG="${FFMPEG:-ffmpeg}"
SILENT="${1:?need <silent_render.mp4>}"
OUT="${2:?need <final_output.mp4>}"
A=assets/audio; VO=assets/vo; SFX="$A/sfx"
MIX="${MIX:-enconvo_mix.wav}"
DUR=50.5

# ---- build the audio bed once (cached; FORCE=1 to rebuild) --------------------
if [[ ! -f "$MIX" || -n "${FORCE:-}" ]]; then
  echo "[build_audio] assembling mix -> $MIX"
  "$FFMPEG" -y -hide_banner -loglevel error \
    -i "$A/ambient.wav" \
    -i "$VO/vo2.wav" -i "$VO/vo3.wav" -i "$VO/vo4.wav" -i "$VO/vo5.wav" \
    -i "$VO/vo6.wav" -i "$VO/vo7.wav" -i "$VO/vo8.wav" \
    -i "$SFX/tick.wav" -i "$SFX/tick.wav" -i "$SFX/tock.wav" \
    -filter_complex "\
[1]aresample=48000,aformat=channel_layouts=stereo,adelay=4900|4900[v2];\
[2]aresample=48000,aformat=channel_layouts=stereo,adelay=10100|10100[v3];\
[3]aresample=48000,aformat=channel_layouts=stereo,adelay=17900|17900[v4];\
[4]aresample=48000,aformat=channel_layouts=stereo,adelay=25300|25300[v5];\
[5]aresample=48000,aformat=channel_layouts=stereo,adelay=32600|32600[v6];\
[6]aresample=48000,aformat=channel_layouts=stereo,adelay=38900|38900[v7];\
[7]aresample=48000,aformat=channel_layouts=stereo,adelay=43900|43900[v8];\
[v2][v3][v4][v5][v6][v7][v8]amix=inputs=7:normalize=0[voall];\
[voall]asplit=2[vokey][vomix];\
[0]aresample=48000,aformat=channel_layouts=stereo,volume=0.42[bed];\
[bed][vokey]sidechaincompress=threshold=0.02:ratio=8:attack=15:release=350[bd];\
[8]aresample=48000,aformat=channel_layouts=stereo,volume=5.0,adelay=47500|47500[k1];\
[9]aresample=48000,aformat=channel_layouts=stereo,volume=5.0,adelay=47780|47780[k2];\
[10]aresample=48000,aformat=channel_layouts=stereo,volume=5.5,adelay=48060|48060[k3];\
[k1][k2][k3]amix=inputs=3:normalize=0[sfx];\
[vomix]volume=1.3[vol];\
[bd][vol][sfx]amix=inputs=3:normalize=0,alimiter=limit=0.97[a]" \
    -map "[a]" -t "$DUR" -ac 2 -ar 48000 "$MIX"
fi

# ---- mux onto the silent render ----------------------------------------------
echo "[build_audio] muxing -> $OUT"
"$FFMPEG" -y -hide_banner -loglevel error -i "$SILENT" -i "$MIX" \
  -filter_complex "[1:a]afade=t=in:st=0:d=0.2,afade=t=out:st=49.9:d=0.4[a]" \
  -map 0:v:0 -map "[a]" -c:v copy -c:a aac -b:a 192k -movflags +faststart -t "$DUR" "$OUT"
echo "[build_audio] done: $OUT"
