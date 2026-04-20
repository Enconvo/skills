# Music & BGM — Soundtrack Design

Music is not optional polish. It's a second narrative channel. Done well, the soundtrack tells the viewer how to feel before the visuals have a chance to.

Every tier-1 video either **has a deliberately composed score** or makes **a conscious choice to have silence + voice-over only**. "No thought given to music" is the amateur tell.

## Decision tree: score / BGM / silent?

Answer these in order:

1. **Is there voice-over?**
   - Yes → BGM must duck under VO (-18 to -24 dB). See "Mixing with VO" below.
   - No → Music is the primary audio channel and can sit at full level (-3 to -6 dB peak).

2. **Does the narrative have an emotional arc?**
   - Flat/uniform → instrumental loop or silence + ambient is fine.
   - Rising/falling/climax → score it properly (separate stems for intro/build/climax/outro, matched to scene transitions).

3. **Does the style preset call for music?** See the style × music table below.

4. **Is this silent-by-design?** Some styles are stronger without music:
   - Mission Control Cinematic (mission brief format) often works best with VO + subtle ambient noise (servers humming, radio chatter) and NO score.
   - Shadow Cut (noir) uses silence as a weapon — a single tension cue at the 60% mark, nothing else.
   - Data Drift (analytical) usually no music at all.

## Style × Music compatibility

| Style | Default music approach | Genre/mood | BPM range |
|---|---|---|---|
| Mission Control Cinematic | Optional low ambient pad + timpani hit on hero reveal | Cinematic orchestral, ambient drones | 60–80 |
| Swiss Pulse | Minimal tonal pulse, sidechained to editing rhythm | Minimal techno, ambient electronic | 110–128 |
| Velvet Standard | Solo piano or chamber strings, restrained | Neoclassical, chamber, ambient piano | 60–90 |
| Data Drift | **No music** (or subtle hum/sine wave bed) | — | — |
| Maximalist Type | **Music IS the visual.** Full track, hard drops, type syncs to beat | Hip-hop, electronic, rock, pop | 120–180 |
| Soft Signal | Acoustic guitar / warm piano / ambient folk | Indie folk, ambient acoustic | 70–100 |
| Neon Frequency | Synthwave, darksynth, electro | Synthwave, retrowave, electro | 100–140 |
| Folk Frequency | Live acoustic, fingerpicked guitar, light percussion | Indie folk, acoustic, alt-country | 80–110 |
| Shadow Cut | **Silence**, with one tension cue at 60–70% | Tense ambient, single cue | 50–70 |
| Deconstructed | Fragmented, abrupt cuts between cues, intentional dead air | Experimental electronic, IDM | varies |
| Broadcast Bulletin | Subtle news-room bed loop + sting on chyron | Broadcast stings, tension bed | 110–130 |

## Tooling

**Primary: `acestep` skill** — ACE-Step V1.5, local or cloud.
- Text-to-music with caption (e.g., "ambient cinematic piano, slow, restrained, strings swell at 45s") + optional lyrics for vocal tracks.
- Duration control (1–240s).
- BPM and key-scale control.
- Returns `.mp3` ready to drop into a HyperFrames `<audio>` clip.

**Workflow check before generating:**
1. `bash ~/.claude/skills/acestep/scripts/acestep.sh config --check-key` — confirms cloud vs local.
2. `bash ~/.claude/skills/acestep/scripts/acestep.sh health` — confirms server is up if local.
3. If not installed, the acestep SKILL.md explains setup. Default to cloud API if the user has a key; otherwise run `setup`.

**Companion skills (if a proper music workflow is needed):**
- `acestep-songwriting` — for vocal tracks, structure, BPM/key selection.
- `acestep-lyrics-transcription` — if the music has vocals and you need synced lyrics (Groq Whisper → LRC).
- `acestep-simplemv` — standalone music-video renderer (we generally don't need it because HyperFrames renders the video; acestep provides just the audio).
- `acestep-thumbnail` — cover art via Gemini.

**Lighter alternative: library/curated stock music.** If the user has their own track or specifies a named reference (and a path), skip generation and use the file as-is.

## Generating music — the acestep brief

When invoking acestep, write the caption like a music director's brief, not a keyword list. Bad: `"sad piano"`. Good:

> `"Solo upright piano, slow 68 BPM, key of D minor, sparse left-hand intervals, right-hand melody emerges at 0:18 — felt-hammer timbre, room reverb, no percussion, no pads. Builds emotionally from 0:45 onward with subtle cello drone underneath. Ends on a held note at 1:30."`

That's the level of brief ACE-Step actually responds to.

### Rule: match the video's structural beats

A 78-second video with 7 scenes should NOT get a 78-second homogeneous loop. Commission:

- **Intro cue** (0–10s): sparse, establishes tonality.
- **Build** (10–45s): layers add gradually.
- **Climax / hero moment** (45–60s): full texture, aligned with the visual hero scene.
- **Return/wind-down** (60–75s): instruments drop out.
- **Outro** (75–78s): resolve + clean tail.

You can generate as one track with the brief describing the arc, OR commission 2–3 separate cues and crossfade them in the composition (better precision, more work).

## Mixing with VO

If there's voice-over:

- **BGM level:** -18 to -24 dB peak (side-chained under VO).
- **Caption font still legible?** Music shouldn't fight the text either — avoid tracks with dense vocal/lyrical content if captions are on screen.
- **Duck automation:** In HyperFrames, set two volume stages on the music `<audio>` element using `data-volume="0.25"` while VO is playing and `data-volume="0.6"` in VO-gap moments. (Currently the framework doesn't support automated ducking; either bake ducking into the generated file OR split the music into two clips with different `data-volume` values.)
- **Tail trim:** Music must end cleanly — never cut mid-phrase. Trim the generated file in ffmpeg if needed.

## Wiring music into HyperFrames

```html
<!-- Narration (primary) -->
<audio id="voiceover"
       data-start="0" data-duration="77.52" data-track-index="9"
       src="narration.wav" data-volume="1"></audio>

<!-- BGM (ducked under VO) -->
<audio id="bgm"
       data-start="0" data-duration="78" data-track-index="10"
       src="score.mp3" data-volume="0.22"></audio>
```

If music has a pronounced build/drop that should hit a specific scene, shift its `data-start` so the drop aligns with the target transition.

## What NOT to do

1. **No music just because "it needs music."** Silence is a valid aesthetic choice.
2. **No library-stock corporate piano** under a Mission Control cinematic piece. It reads instantly as cheap.
3. **No music fighting the VO** — if the viewer can't hear the narration, the music is too loud. Always mix music *under* voice, never parallel.
4. **No full-chorus vocal tracks behind a voiced explainer.** Lyrics and narration compete for the same mental channel.
5. **No hard cuts mid-phrase at the video end.** Trim or fade properly.
6. **Don't ship without listening.** Generate, play back, verify the emotional arc actually tracks the visual arc. If the climax cue hits the wrong scene, regenerate with a tightened brief.

## Checklist before handoff

- [ ] Music approach decided (score / BGM / silent) and justified against the chosen style.
- [ ] If music is generated, the ACE-Step brief is in the spec (not just "generate some music").
- [ ] BPM, key, duration specified.
- [ ] Mix level for music specified (VO-ducking plan if narration exists).
- [ ] Structural alignment to scenes documented ("build at 10s, climax at 45s aligned to scene 5 hero moment").
