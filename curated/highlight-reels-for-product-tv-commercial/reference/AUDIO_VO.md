# AUDIO_VO.md — VO-narrated variant (extends the music-only default)

The default kit is **music-only**. The shipped **EnConvo launch cut** is a longer **50.5s VO-narrated** version: one clean narrator over a *ducked* music bed, with keypress SFX on the outro. Same composition / layout / themes — only longer, plus a voice track. Both orientations (16:9 + 9:16) share the **identical timeline**, so you build **one** audio mix and mux it onto **both** silent renders.

---

## Timeline (VO cut — keep these scene starts · 50.5s @ 30fps)

| Scene | data-start | VO marker (adelay ms) | Line (EnConvo example) |
|---|---|---|---|
| S1 logo | 0 | — | *(no VO — logo bloom)* |
| S2 thesis | 4.4 | 4900 | "Your Mac just got a command center." |
| S3 SmartBar | 9.4 | 10100 | "One launcher, every AI tool, and any model you choose." |
| S4 PopBar | 17.1 | 17900 | "Select text anywhere, and get an answer on the spot." |
| S5 Agents | 24.5 | 25300 | "Ask for a real app, and watch an agent build it." |
| S6 Quant | 31.9 | 32600 | "Describe a strategy in one line. Get a backtested result out." |
| S7 montage | 38.5 | 38900 | "Vision, memory, workflows, and everything in between." |
| S8 close/CTA | 43.8 | 43900 | "EnConvo. Your Mac's command center. Press Command, Shift, D to begin." |

VO lands ~0.5s **after** each scene start (let the visual establish first). Screen clips start ~0.2s after the scene. If you re-time scenes, move the markers with them.

---

## VO generation

- **One voice for the whole film** (consistency). Gemini TTS via `tts/features/gemini/create` (`text`, `voice`, `format:wav`, `output_dir`, `audio_file_name`); the EnConvo cut uses voice **Charon**.
- One wav per scene (n2…n8). Typical durations 2.9–6.4s. If you change the voice, **regenerate the whole set** — never mix voices across scenes.
- **ASR note:** the brand "EnConvo" transcribes back as "nConvo" — ASR drops the unstressed leading "En." That is a transcription artifact, **not** a VO defect; don't try to "fix" the read.

---

## The mix (ffmpeg, AFTER the silent render)

Build once, reuse for both orientations. `scripts/build_audio.sh` wires the whole chain (and takes a `BED=` override). Structure:

1. **VO bus** — place each scene wav with `adelay=<marker>|<marker>` (stereo), then `amix` them (`normalize=0`).
2. **Music bed** — a clean, VO-free score bed the length of the film (`assets/audio/ambient.wav`), `volume≈0.42`, **double-ducked**: sidechain-compressed under the VO *and* under the keypress SFX, so narration stays intelligible **and** the outro keycaps always cut through no matter what the bed is doing:
   `[bed][vobus]sidechaincompress=threshold=0.02:ratio=8:attack=15:release=350[bd0];`
   `[bd0][sfxbus]sidechaincompress=threshold=0.05:ratio=6:attack=4:release=260`
   The shipped bed is a **Suno-generated cinematic underscore** (warm analog pads + felt piano + glassy bells, **no rhythmic clicking**) whose final ~3s **decrescendo to near-silence** — keep any replacement bed's tail soft/resolved so the tick·tick·tock lands clean.
3. **Keypress SFX** (outro) — see below.
4. `amix` VO(vol ~1.3) + double-ducked bed + SFX (`normalize=0`), then `alimiter=limit=0.95–0.98`.
5. **Mux** onto the silent render: `-map 0:v:0 -map "[a]" -c:v copy -c:a aac -b:a 192k -movflags +faststart`, with `afade=t=in:st=0:d=0.2` and `afade=t=out:st=<dur-0.6>:d=0.4`.

> Keep the **music-only bed** (`ambient.wav`) as its own file, separate from any earlier VO+music mixes. Re-using a mix that already contains VO as the "bed" double-tracks the voice (a real bug hit this kit — `final_mix.wav` was a VO+music mix, `ambient.wav` is the clean bed).

### Regenerating the music bed (Suno)

The shipped `ambient.wav` was generated on **suno.com/create** (Advanced mode, **Instrumental** on) and trimmed to the 50.5s timeline:

- **Style prompt:** *Minimal cinematic tech underscore for a premium product launch film. Warm analog synth pads, soft felt piano motif, glassy bell tones, mellow sub bass, airy ambient shimmer, gentle uplifting swells. Elegant, restrained, sophisticated, Apple and Notion aesthetic. Smooth flowing legato, no rhythmic clicking. Slow graceful build that resolves into a soft calm sustained ending. Around 90 BPM.*
- **Exclude styles:** *ticking, tick-tock, clock, metronome, clicky percussion, staccato pulse, arpeggiated pluck, drums, snare, hi-hat, aggressive bass, vocals, lyrics, choir, loud final hit, sudden climax, distortion.* This exclude list is what keeps the bed from fighting the tick·tick·tock keycaps — **do not drop it.**
- **Fit to the timeline:** pick a take **longer** than the film, then trim the window whose **natural decrescendo lands on the film's end** (align the resolve to the outro so the bed is already soft when the keycaps hit). Add a ~1.2s fade-in and level-match to the old bed (~−13 LUFS) so the `volume=0.42` balance still holds:
  `ffmpeg -ss <start> -t 50.5 -i take.mp3 -af "afade=t=in:st=0:d=1.2,aresample=48000,aformat=channel_layouts=stereo,loudnorm=I=-13:TP=-1.5:LRA=11" -ac 2 -ar 48000 -c:a pcm_s16le assets/audio/ambient.wav`

---

## Keyboard-shortcut outro SFX — tick · tick · tock

The close presses the app's launch chord (⌘⇧D). Sound it as **a tick on each modifier, a tock on the action key** — three keys, three hits. **NOT** a tick per key plus a trailing tock (that reads as four).

- **Read the exact keycap press times from the composition's GSAP timeline** — `tl.to("#kCmd"…)`, `"#kShift"`, `"#kD"`. In the EnConvo cut they are **47.5 / 47.78 / 48.06s**.
- **Samples:** `tick.wav` + `tock.wav` from the **screen-to-promo** skill's SFX library (`~/.claude/skills/screen-to-promo/assets/sfx/`). Place each with `adelay` at its press time (resample to 48k stereo first).
- **Levels:** ticks (⌘, ⇧) ~`volume=5.0`; the **action tock (D) ~`volume=5.5`** — loudest, it is the money hit as the shortcut fires and the key-glow blooms. The tock coincides with the spoken key name ("D") and can get **masked** — bring it up until it clearly punctuates.
- These are **transients**: they cut through the VO even a few dB under it, and the bed **sidechain-ducks under them** (step 2) so they stay clean. The final master should still peak ≤ −0.3 dBFS (the `alimiter` holds it).
- The keycaps ship with unused `*_lit.png` variants (`key_cmd_lit`, `key_shift_lit`, `key_d_lit`) — a future enhancement is to swap to the lit art on each press.

---

## You can't audition — verify by measurement

- **SFX landed:** `ffmpeg -ss <t0> -to <t1> -i mix.wav -af volumedetect -f null -` on the outro window and confirm the region max rises where the hits are (the tick·tick·tock window should out-peak the surrounding bed).
- **No unwanted ticking in the bed:** render a spectrogram (`ffmpeg -i ambient.wav -lavfi showspectrumpic=s=1500x460 spec.png`) and read it — a clock-like tick shows as evenly-spaced full-height vertical stripes. Bell/piano note attacks are transients too, so also confirm the bed's **tail is soft** under the keycap window (a waveform image makes the decrescendo obvious).
- **VO intelligible over the bed:** transcribe the final mix (`transcribe/features/groq/transcribe`) and confirm the lines come back cleanly.
- **No clip:** whole-file `volumedetect` max ≤ −0.3 dBFS.
- **A/V + both cuts:** `ffprobe` shows `aac` 48k stereo + `h264`, `duration=50.5`; the one mix muxes onto **both** the landscape and vertical silent renders (they share the timeline).
