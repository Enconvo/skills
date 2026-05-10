# Keypress + Motion SFX Library

Production-tested SFX for screen-recording demo videos. Battle-tested on the Enconvo dub pipeline (v7–v9, May 2026). Use these as the canonical sounds for keypress overlays and CTA card motion in screen-to-promo videos.

## Files

| File | Spec | Use |
|------|------|-----|
| `tick.wav` | 44.1k mono · 0.08s · ~7KB | Sharp finger-strike attack — key DOWN. The "click" of contact. |
| `tock.wav` | 44.1k mono · 0.18s · ~16KB | Slightly deeper resonance — key BOTTOM-OUT or release. The "thunk" after the click. |
| `whoosh.wav` | 48k mono · 0.6s · ~56KB | Smooth motion sweep for transitions, logo reveals, scene changes. |

## Canonical Cue Patterns

### A single keypress (any modifier or letter)

Layer **tick + tock**, with tock delayed 100–150ms:

```
0ms:   tick   (vol 0.85)  ← finger contact
120ms: tock   (vol 0.95)  ← key bottoms out
```

This sounds like a real mechanical key press. Single tick = thin / cheap. Single tock = mushy / soft. Layered = satisfying, premium.

### A multi-key shortcut (e.g. ⌘⇧D)

Stack 2–3 ticks with 80–180ms spacing for the modifiers, then a tock for the triggering letter:

```
100ms: tick   (⌘ Cmd)
280ms: tick   (⇧ Shift)
460ms: tick   (D pressed — onset)
1450ms: tock  (D bottom-out / action fires)
```

This was the exact CTA card pattern that landed cleanly on screen capture — the spacing matches how a human actually rolls through a chord.

### Scene transition / logo reveal

`whoosh.wav` — single hit, no layering. Volume 0.6–0.8 depending on whether VO is overlapping.

```
2.10s: whoosh (Phase-1 outgoing)
2.50s: whoosh (logo settling in, softer at 0.6)
```

## Mixing Recipe (ffmpeg)

Build an SFX overlay track at the same length as the source video, then `amix` it onto the original audio:

```bash
ffmpeg -y \
  -i sfx/tick.wav -i sfx/tock.wav \
  -filter_complex "
    [0:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo,volume=0.85,adelay=18400|18400[c1];
    [1:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo,volume=0.95,adelay=18520|18520[c2];
    [c1][c2]amix=inputs=2:duration=longest:dropout_transition=0:normalize=0[mix];
    [mix]apad=whole_dur=DURATION,atrim=0:DURATION,asetpts=N/SR/TB[out]
  " -map "[out]" -ar 48000 -ac 2 -c:a pcm_s16le \
  keypress_track.wav
```

Then mix into source (preserves video stream as copy):

```bash
ffmpeg -y -i source.mp4 -i keypress_track.wav \
  -filter_complex "[0:a]volume=1.0[a0];[1:a]volume=1.0[a1];\
    [a0][a1]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[aout]" \
  -map 0:v:0 -map "[aout]" -c:v copy \
  -c:a aac -b:a 192k -ar 48000 -ac 2 -movflags +faststart \
  source_with_sfx.mp4
```

## Cue-Timing Discipline

**The hard-won rule from the Enconvo dub:** the SFX must land on the FRAME the key animation reveals, not the moment the keystroke happens off-screen.

Verify by extracting frames at 0.2s intervals around your intended cue point:

```bash
for t in 36.5 37.0 37.3 37.5 37.7 38.0 38.3; do
  ffmpeg -y -ss $t -i source.mp4 -frames:v 1 -loglevel error frame_${t}.png
done
```

Read each frame, find where the reveal animation actually starts (e.g. command bar emerging, menu unfurling), and align the tick to THAT frame. A 1s misalignment is immediately audible as "the sound came before the picture."

## Volume Targets

After mixing, verify each cue with `volumedetect`:

```bash
ffmpeg -y -ss 18.4 -t 0.4 -i out.mp4 -af "volumedetect" -f null - 2>&1 | grep max_volume
```

Healthy peaks: **−6 to −10 dB** at the cue moment. Below −15 dB the SFX disappears under VO; above −3 dB it overpowers the narration.

## Source / Provenance

Generated 2026-05-08 during the Enconvo dub pipeline build (`sessions/IE0h0u8KCbhh6aYJuOSo`). Validated across three production runs (v7, v8, v9). Reuse freely — these are the canonical screen-to-promo SFX.
