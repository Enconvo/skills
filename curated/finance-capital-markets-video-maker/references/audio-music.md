# Audio & Music

The finance video has two audio layers:

1. **Anchor speech** — baked into i2v render. NEVER use TTS for anchor voice. See `i2v-pipeline.md`.
2. **BGM bed** — generated below.

There are exactly TWO sanctioned BGM paths, in priority order. Pick ONE per video. No fallback chain, no hybrid mixing.

## Loudness, Ducking & Seamless Looping (broadcast standard — applies to BOTH paths)

This is the validated mix recipe. Use it regardless of whether the bed came from acestep or Suno.

**Targets (EBU R128 / social-broadcast):**
- Program integrated: ~ −13.7 to −14 LUFS.
- Anchor VO: −14 to −16 LUFS.
- Music bed: −18 to −23 LUFS — i.e. **6–10 dB under the voice**.
- Duck during speech: bed pulled −3 to −6 dB under the VO via sidechain (not a flat blanket cut).
- True-peak ceiling: ≤ −1 dBTP (limiter at 0.97).

**Validated duck-mix** (video+VO is input `0`, looped bed wav is input `1`):
```bash
ffmpeg -y -i {slug}_final_novo.mp4 -i bgm_loop.wav -filter_complex \
  "[1:a]volume=0.46[bgmv];\
   [0:a]asplit=2[vo][vokey];\
   [bgmv][vokey]sidechaincompress=threshold=0.06:ratio=3:attack=20:release=300[bgmduck];\
   [vo][bgmduck]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.97[aout]" \
  -map 0:v -map "[aout]" -c:v copy -c:a aac -b:a 192k {slug}_final.mp4
```
- `volume` on the bed is the master trim. Start ~`0.46` (bed ~−19 LUFS under a −14 VO). Users often want it quieter — drop in **~2 dB steps** (`0.58 → 0.46 → 0.36`; each ×0.79 ≈ −2 dB).
- `sidechaincompress` keyed off the VO ducks the bed during speech ONLY. `ratio=3` (3:1) is gentle; `release=300` recovers smoothly between sentences. Heavier (8:1) pumps — avoid.
- `normalize=0` stops amix auto-attenuation; `alimiter=limit=0.97` caps true peak under −1 dBTP.
- `-c:v copy` — NEVER re-encode video for an audio-only change.
- Verify: `ffmpeg -i out.mp4 -af ebur128=framelog=quiet -f null - 2>&1 | grep 'I:'`.
- **Fades:** default to NO hard fade in/out (continuous broadcast feel; users have explicitly asked to remove them). Add a 1–2s top/tail fade only on request.

**Seamless looping** (bed shorter than video — the common case; Suno clips are often ~35–100s). Crossfade copies with a TRIANGULAR acrossfade so seams are inaudible — do NOT concat-demux (clicks at every join):
```bash
# N = ceil(target_sec / src_sec) + 1 copies; d=3 tri crossfade eats 3s per join.
ffmpeg -y -i src.wav -i src.wav -i src.wav -i src.wav -i src.wav -i src.wav -filter_complex \
  "[0][1]acrossfade=d=3:c1=tri:c2=tri[a1];[a1][2]acrossfade=d=3:c1=tri:c2=tri[a2];\
   [a2][3]acrossfade=d=3:c1=tri:c2=tri[a3];[a3][4]acrossfade=d=3:c1=tri:c2=tri[a4];\
   [a4][5]acrossfade=d=3:c1=tri:c2=tri[aout]" -map "[aout]" -c:a pcm_s16le bgm_loop.wav
```
Total ≈ N×src − 3×(N−1). Make it exceed the video; `amix duration=first` trims the tail.

**Under-50MB social/TG export:** after the mix, two-pass re-encode `-c:v libx264 -b:v 1300k -pass 1/2 -g 60 -preset medium` + `-c:a aac -b:a 128k`. A 4:09 1280×720 cut lands ~45 MB.

## Path A (PRIMARY) — acestep skill, local generation

Use this whenever the local acestep installation is available and the desired track length is ≤ 240s.

### When to choose

- Default for every video.
- Faster (local M-series), no auth, no rate limits, no credit cost.
- Full control over BPM, key, instrumentation, structure.
- Stems available if needed for finer mixing.

### How to invoke

Load the `acestep` skill at `/Users/zanearcher/.agents/skills/acestep/SKILL.md` and follow its prompt-engineering rules (see also the sibling `acestep-songwriting` skill for caption / BPM / key choice).

### Canonical BGM brief for finance-anchor videos

Use these as the default knobs unless the user specifies otherwise:

- **Style:** cinematic financial broadcast underscore, late-night business news
- **Reference vibe:** Bloomberg Open Interest, CNBC Fast Money cold open, slow-build pulse
- **Mood:** tense, calm authority, not aggressive, not celebratory
- **BPM:** 88–96 (slow enough that VO sits above it cleanly)
- **Key:** A minor or D minor (broody but not maudlin)
- **Instrumentation:** sub-bass pulse, sparse piano motif, occasional analog synth pad, light percussive ticks; NO drums front-and-center, NO vocals
- **Structure:** sustained bed, no dramatic drops, no buildups, no swells under VO
- **Duration:** 1.05× the final video length (gives ffmpeg 5% trim margin)
- **Output:** WAV or 320kbps MP3, mono OK if final mix is mono

### Mixing instructions

```bash
ffmpeg -i {slug}_final_novo.mp4 -i bgm_{slug}.mp3 \
  -filter_complex "[1:a]volume=-18dB,afade=t=in:st=0:d=2,afade=t=out:st=END-2:d=2[bgm];\
                   [0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -y {slug}_final.mp4
```

Replace `END` with the actual duration in seconds. This flat `volume=-18dB` + linear `amix` is the QUICK path. **For the broadcast-grade result, use the sidechain-duck mix in the “Loudness, Ducking & Seamless Looping” section above** — it keeps the bed audible between phrases but ducks it under speech, instead of a flat blanket cut. Verify integrated loudness with `ffmpeg -i out.mp4 -af ebur128=framelog=quiet -f null -`.

## Path B (SECONDARY) — suno.ai via browser automation + computer use

Use this ONLY when the user explicitly asks for Suno's signature sound, or when acestep is unavailable, or when the user wants lyrics + vocals on top of the bed (rare for finance videos).

### When to choose

- User says: "use Suno", "suno.ai", "with vocals", "signature Suno track"
- acestep installation is broken or missing on the host
- Track length needs to exceed 240s and acestep can't continue cleanly

### How to invoke

Drive the user's logged-in Chrome session through the `browser` skill at `/Users/zanearcher/.config/enconvo/extension/computer-use/skills/browser`. Use the real browser session (cookies + Suno login already established) — do NOT use isolated `browser-use` for this; Suno gates anonymous access.

If the real-browser path is unavailable for some reason, fall back to driving Chrome via the broader `computer-use` skill at `/Users/zanearcher/.config/enconvo/extension/computer-use/skills/computer-use`.

### Suno workflow

1. Open `https://suno.com/create` in a grouped background tab.
2. Click "Custom Mode" toggle to ON.
3. Fill the **Style of Music** field with the canonical brief (BPM, instrumentation, vibe — same content as Path A's brief, condensed to ~200 chars).
4. Fill **Title** with `{slug}_bgm`.
5. Leave **Lyrics** blank, toggle **Instrumental** to ON (finance videos have no vocal bed).
6. Click **Create**. Wait ~30–60s for generation. Suno produces 2 variants per generation.
7. Listen to both, pick the better one (the one with less harmonic interference against speech mid-frequency range).
8. **Download — preferred: pull straight from Suno's CDN (bypasses the flaky ⋮ dropdown).** The download dropdown renders in a portal that gets truncated past the page-snapshot's ~200-element cap once the workspace holds many clips, so the **Download** item is often unreachable. Instead, read the clip's title-link href with `computer-use/browser/get_attribute` (attribute `href`) → it's `/song/<uuid>` → download directly: `curl -sL -o bgm_src.mp3 https://cdn1.suno.ai/<uuid>.mp3` (full-quality MP3; only use the ⋮→Download→WAV path when you truly need lossless). Fast, deterministic, ref-staleness-proof.
   - Element refs go stale after every fill/scroll/playback re-render. **Pause playback first** (the playbar re-renders every second and shifts handles), then re-snapshot immediately before reading the href.
   - The clip title collides across re-rolls ("Market Pulse" appears many times); identify the right clip by newest-at-top position or by a unique title, and confirm the downloaded file's duration with `ffprobe`.
9. **Gacha discipline.** Suno output is random — send the user a SHORT preview (the raw ~35–60s clip is itself a fine preview) via the IM channel and get a 👍 BEFORE committing to the full loop + duck-mix + export. Re-roll the same brief rather than over-editing a weak take. The instrumental toggle PERSISTS between generations in one session — set it ON once and don't blindly re-toggle.
10. Save into the session workspace as `bgm_{slug}_suno.{mp3,wav}`. If shorter than the video (usual), seamless-loop it per the Looping recipe above; use Suno **Extend** only when the user wants genuinely evolving music, not a loop.

### Suno cost discipline

Suno credits are limited. ONE Suno generation per video unless the user explicitly asks for variants. If the first generation is unusable, regenerate with a refined Style prompt rather than burning credits on the same prompt.

### Suno failure recovery

- **Login expired:** prompt the user to log in, then resume. Do NOT attempt to scrape headlessly.
- **Rate limit hit:** stop and report. Do NOT silently swap to acestep — that's a provider switch and breaks the user's explicit request.
- **Suno UI redesign breaks the click path:** capture a screenshot of the current page state, surface to the user, ask which button to click. Resume after they tell you.

## Path Selection Matrix

| Situation                                  | Use     |
| ------------------------------------------ | ------- |
| Default — no user preference stated        | Path A  |
| User says "local", "acestep", "on-device"  | Path A  |
| User says "suno", "with vocals", "sing"    | Path B  |
| acestep broken on host                     | Path B  |
| Need stems for finer mixing                | Path A  |
| User wants signature Suno acoustic vibe    | Path B  |

## What NOT To Do

- Do NOT mix paths within a single video (don't generate Path A bed + Path B overlay).
- Do NOT use cloud TTS services for BGM — wrong tool.
- Do NOT layer multiple BGM tracks at once — one bed only.
- Do NOT auto-fallback from Path B to Path A if Suno fails — stop and tell the user, let them decide.
- Do NOT generate BGM with vocal stems on a finance video unless the user explicitly asked. The anchor's Mandarin VO is the only voice the audience should hear.
