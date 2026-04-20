# Audio Playbook — TTS & Transcription

The canonical working paths for voice-over and word-synced captions on macOS with Enconvo. Every path below was verified against a real 77.5s narration.

## TTS (Text-to-Speech)

### Working path — Enconvo TTS endpoint

Enconvo's `tts/tts` endpoint works reliably for whole-script generation regardless of the configured TTS provider.

```
local_api tts/tts {
  "user_input_text": "<full narration script>",
  "audio_file_name": "narration",
  "output_dir": "<session_dir>/artemis2",
  "speed": "1",
  "description": "<short description of the narration for voice selection>"
}
```

Returns `{path: "...narration.wav"}`. Typical 150-word documentary script → ~77s WAV (slower than 150 wpm target; see AUDIO-1 learning).

### Voice selection by style

| Style preset | Recommended voice character |
|---|---|
| Mission Control Cinematic | Authoritative documentary, male or female, measured pace |
| Swiss Pulse | Neutral, clipped, slightly cold |
| Velvet Standard | Warm, slightly husky, unhurried |
| Data Drift | Neutral, precise, analytical |
| Maximalist Type | Brash, energetic (or skip narration entirely — let type do the work) |
| Soft Signal | Warm, intimate, unhurried |
| Neon Frequency | Young, ambient, sometimes robotic / processed |
| Folk Frequency | Warm, slight regional inflection, earnest |
| Shadow Cut | Low, measured, deliberate silences |
| Deconstructed | Optional; if used, slightly uncanny or layered |
| Broadcast Bulletin | Crisp, news-anchor, authoritative |

### Fallback chain

1. **Enconvo `tts/tts`** (primary) — works for most cases.
2. **`hyperframes tts "<script>" --voice af_nova --output narration.wav`** — Kokoro-82M, works offline.
3. **`edge_tts`** via `local_api tts/edge_tts/generate` — Microsoft Edge read-aloud, 300+ voices, free.

## Transcription (word-level for captions)

Captions require per-word `{word, start, end}` timestamps. The HyperFrames caption pipeline consumes this directly.

### Blocked path — don't use from agent context

`local_api transcribe/transcribe_audio_video {...}` **returns empty** when called from an agent session. The handler reads `runtime.preferences.stt` which is only populated by an Enconvo command launcher. This is the STT-1 learning.

### Working path — direct Groq Whisper-Large-V3

Your configured provider is `transcribe|enconvo_cloud_plan` → `groq/whisper-large-v3`. To call it from an agent session, bypass the cloud plan and go direct.

**Step 1 — fetch decrypted API key (the disk JSON is encrypted; STT-2):**

```
local_api credentials/load_credentials {"providerName": "groq"}
```

Returns `{apiKey: "gsk_...", ...}`. The `apiKey` is the real decrypted key.

**Step 2 — POST to Groq:**

```bash
curl -s -X POST https://api.groq.com/openai/v1/audio/transcriptions \
  -H "Authorization: Bearer $GROQ_KEY" \
  -F "file=@narration.wav" \
  -F "model=whisper-large-v3" \
  -F "response_format=verbose_json" \
  -F "timestamp_granularities[]=word" \
  --output transcript.json
```

**Step 3 — parse `words[]`:**

```python
import json
d = json.load(open('transcript.json'))
# d['words'] = [{'word': 'Artemis', 'start': 0.32, 'end': 0.86}, ...]
# d['duration'] = 77.52
# d['text'] = 'Artemis II, the first crewed lunar flyby...'
```

**Step 4 — group into caption groups** (3–5 words per group, break on sentence-ending punctuation or 0.3s+ pauses). Hand the resulting array to HyperFrames captions.

### Fallback — local Python whisper

If no Groq key is available, local Whisper is slower but self-contained:

```bash
whisper narration.wav --model small.en --language en \
  --word_timestamps True --output_format json --output_dir .
```

Produces `narration.json` with `segments[].words[]` — roughly the same shape but requires a small reshape to flatten.

`hyperframes transcribe` CLI is whisper.cpp-based and has been broken on this system (fails to invoke `/opt/homebrew/bin/whisper` which is Python-whisper, not whisper.cpp). Avoid it.

## Duration reconciliation

After TTS + transcription:

```bash
ffprobe -v error -show_entries format=duration \
  -of default=noprint_wrappers=1:nokey=1 narration.wav
```

Use the printed value (e.g. `77.52`) as:
- `data-duration` on the root composition
- scene timing anchor (last scene ends at ~this value)
- `data-duration` on the `<audio>` element

**Do not** use the target duration (e.g. "60s") — always use the actual measured WAV duration.

## Quick checklist before hyperframes handoff

- [ ] `narration.wav` exists, duration measured via ffprobe
- [ ] `transcript.json` with `words[]` array exists
- [ ] Caption groups generated (typical: 3–5 words per group, 30–50 groups for 60s video)
- [ ] Scene boundaries aligned to sentence-ending word start times + 0.2–0.4s buffer
- [ ] Root composition `data-duration` matches measured audio duration (not target)
