# i2v Pipeline

## Provider & Endpoint (HARDCODED to EnConvo default)

**Do NOT hardcode the provider name or route.** Always resolve at runtime by reading the agent's `<Video_Create>` ability block and using its `Route`, `Current provider`, `Current model`, and `Current credential` values verbatim.

At the time this skill was authored, the EnConvo default resolved to:
- Local API path: `video_create/features/x_ai/create` (xAI Grok Imagine Video)
- Model: `grok-imagine-video`
- Credential: `globaldefault`

If the user changes the EnConvo default later (e.g. to Veo, Sora, Seedance, Kling, Hailuo, Wan), the same skill flow still works — just call the new route shown in the runtime ability block. NO fallback to other providers if the configured default fails.

## Common Parameters (provider-agnostic)

- Mode: `image-to-video`
- Resolution: `720p` (1280x720) when supported, else closest equivalent
- Aspect ratio: `16:9`
- Duration: 6–10s per clip (10s preferred for steady cadence)
- Wall-clock per clip: provider-dependent, typically ~30–60s at 720p

## Sequential Pipeline (never parallel)

Clips MUST render in order because each clip's start frame is the previous clip's end frame.

```
S01.image = canonical_anchor_reference_url            # ACT anchor point #1
  render S01 → ffmpeg extract endframe → upload → endframe_url_01
S02.image = endframe_url_01                            # chain off clip 1
  render S02 → endframe → upload → endframe_url_02

# MID-ACT RE-ANCHOR at clip 3 — do NOT chain from clip 2's endframe.
S03.image = canonical_anchor_reference_url            # ACT anchor point #2 (drift reset)
  render S03 → endframe → upload → endframe_url_03
S04.image = endframe_url_03                            # chain off clip 3
  render S04 → endframe → upload → endframe_url_04
S05.image = endframe_url_04                            # ... chain S05/S06 off clip 3 line
  ... continue chaining within the SAME ACT ...

# ACT BOUNDARY — HARD RESET. Do NOT carry endframe from previous ACT.
S{first_of_next_ACT}.image = canonical_anchor_url     # original locked reference; clip-3 rule repeats
  render → endframe → upload → endframe_url_{next}
  ... resume within-act chaining (with clip-3 re-anchor) ...
...
```

**Anchor points per ACT = clip 1 and clip 3.** The longest unbroken endframe chain is therefore ≤2 clips (S01→S02, and S03→S04→S05/S06). Empirically, by clip 2's endframe the face has drifted enough that without the clip-3 reset the act's FINAL frame looks like a different woman. Skip the mid-act reset only for 2-clip acts (no clip 3 exists). The clip-3 reset is safe re: broadcaster-text burn-in because every prompt carries the mandatory BURN-IN LOCK block — it was the *every-clip* reset, not an occasional one, that triggered burn-in.

## Endframe Extraction

Use `scripts/extract_endframe.sh <clip.mp4> <out.jpg>`:

```bash
ffmpeg -hide_banner -loglevel error -sseof -0.1 -i "$1" -frames:v 1 -q:v 2 -y "$2"
```

Then upload via `enconvo/upload_file` to get a fresh hosted URL. The xAI i2v `image` field requires a URL, not a local path.

## Prompt Template (per clip)

Use `templates/anchor_i2v_prompt.txt` as the skeleton. Every prompt is composed of EIGHT blocks. The last three (SCALE LOCK, BURN-IN LOCK, SUBJECT FRAMING) are NON-NEGOTIABLE — omit SCALE/BURN-IN and you get slow-zoom drift and broadcaster-text burn-in (see War Story 2026-05-31 below); omit SUBJECT FRAMING and the body drifts off-center or gets clipped at the edges.

```
[VO LINE]
  Verbatim Mandarin monologue for this clip (50 字 for 10s, 30 字 for 6s).
  Delivered as the spoken audio, in a calm institutional broadcast tone.

[IDENTITY LOCK]
  Same female news anchor as reference: Eurasian, early-30s, heart-shaped
  face, almond hazel eyes, sleek dark blowout. Scarlet Saint Laurent
  Le Smoking peak-lapel blazer, ivory silk shell, pearl-drop gold
  earrings, slim gold Cartier Tank watch. Natural makeup, defined dark
  brow, neutral satin lip, real skin (visible pores, faint freckles).

[SET LOCK]
  Contemporary studio behind her: out-of-focus night-city skyline through
  angled glass, softly bokeh'd. STATIC plate, no drift, no pan, no zoom.
  Warm amber key from camera left, cool blue rim from right.
  News desk in foreground, forearms resting on desk surface, no gestures.

[CAMERA LOCK]
  Locked-off medium close-up, chest-up framing, eyeline slightly
  camera-right. No camera movement. 35mm equivalent, f/2.8 look.

[MOTION LOCK]
  Only anchor moves: natural lipsync to VO, blinks, slow eye shifts,
  subtle micro-nods. Hands stay locked on the desk. Right 40% of frame
  remains clean negative space — no objects, no gesture, nothing.
  Background stays absolutely still. Return to neutral resting pose
  by second 10 so the endframe is a clean handoff for the next clip.

[SCALE LOCK]
  Fixed 35mm equivalent throughout the full 10 seconds. NO zoom,
  NO dolly, NO pan, NO parallax, NO scale-to-frame. Anchor's head
  occupies the SAME frame fraction at second 0 and second 10.
  Background fully static.

[BURN-IN LOCK — ABSOLUTELY CRITICAL]
  Render a clean unadorned video plate. ZERO text of any kind
  anywhere in the frame. NO captions, subtitles, chyrons,
  lower-thirds, breaking-news banners, tickers, logos, watermarks,
  station IDs, show titles, speech bubbles, timecodes, frame
  counters. NO words such as CAPTAIN, BREAKING, LIVE, CNBC,
  BLOOMBERG, or any English or Chinese characters as on-air
  graphics. The studio set behind her has NO visible text on any
  monitor, NO scrolling text, NO labeled banners. All graphics added
  in post — render must be 100% text-free.

[SUBJECT FRAMING]
  Anchor fills the LEFT ~55% of frame, head near the top edge, whole
  body INSIDE frame — crown, shoulders, elbows, hands never cropped or
  touching an edge. RIGHT ~45% stays clean negative space for the post
  overlay. Do NOT zoom or scale the subject to reach the edges.
```

## War Story — 2026-05-31: canonical reset triggered broadcaster text burn-in

**Symptom.** With v3 doctrine (every clip starts from the canonical anchor photo, not the previous clip's endframe), xAI Grok Imagine started burning literal broadcaster text into the render — lower-third chyrons with the word "CAPTAIN", "BREAKING" banners, fake ticker crawls. Clip S01 was clean; S02 and S03 (rendered fresh from the still photo with identical prompts) had burn-in.

**Root cause.** Feeding a still photograph + "news anchor in studio" context primes the i2v model to interpret the prompt as "here is a new TV broadcast scene, please decorate it like real TV." The model fills in the missing video-time decoration it expects in a broadcast — chyrons, station IDs, breaking-news supers. Generic prompt-side "no text" suppression is insufficient.

**Fix.** Two-part lock:
1. **Endframe chain restoration.** Within an ACT, use clip N's actual last video frame as clip N+1's start image (not the canonical photo). The model reads the input as "continue this established clean shot" and does not redecorate.
2. **Named-token burn-in block.** Add the BURN-IN LOCK block above to every prompt — explicitly name the hallucinated tokens (CAPTAIN, BREAKING, LIVE, CNBC, BLOOMBERG), the structural elements, AND the background sources (monitors behind her show no text). Close with "all graphics added in post — render must be 100% text-free."

Both together killed the issue on the next attempt. The earlier v2 doctrine (chain within ACT, reset across ACTs) is now back as canonical — with the burn-in + scale locks bolted onto every prompt as mandatory blocks 6 and 7.

## Parameter Defaults

Use the runtime `<Video_Create>` ability block's schema for the exact parameter shape. The example below assumes xAI Grok is the current default; adapt the `model` and any provider-specific fields if the default has been swapped.

```json
{
  "prompt": "<five-block prompt>",
  "mode": "image-to-video",
  "model": "<runtime Video_Create current model>",
  "image": "<hosted reference URL>",
  "duration": 10,
  "aspect_ratio": "16:9",
  "resolution": "720p",
  "credentials": "globaldefault",
  "download": true,
  "output_dir": "<session>/v{N}_clips",
  "file_name": "v{N}_s{NN}.mp4"
}
```

## Continuity QA

After each clip downloads, before extracting endframe:

1. Spot check the clip's first frame against the input image — should be near-identical (no face shift, no wardrobe drift).
2. Spot check that hands stayed on desk and right-40 is clean.
3. If either fails, regenerate that clip BEFORE extracting endframe and continuing. A broken clip in position N corrupts all downstream clips.

## Failure Recovery

- **Identity drift:** anchor looks like a different woman → regenerate from the previous good endframe. If it keeps drifting, re-anchor from the canonical reference URL and accept a small visible cut.
- **Per-act reset + clip-3 re-anchor are both mandatory, not optional.** Drift compounds clip-by-clip and faster than expected. The first clip of every ACT MUST use the canonical locked anchor reference URL (not the previous ACT's endframe), AND the 3rd clip of every ACT MUST re-anchor to the same canonical reference (not clip 2's endframe). This caps the unbroken chain at ≤2 clips so even the act's final frame stays on-model. If an anchor still drifts inside a ≤2-clip chain, regenerate that clip from its anchor reference rather than extending the chain.
- **Gesture violation:** hand lifts off desk into right-40 → regenerate, strengthen the hands-locked clause.
- **Background drift:** LED plate pans → regenerate with "STATIC plate, frozen, no pan, no drift" repeated twice.
- **Audio missing/garbled:** the current provider sometimes drops VO → regenerate the SAME clip with the SAME provider. Do NOT switch providers. There is no rescue path.
- **Subject clipped at edge** (crown, elbow, or fingers cut off, or the body touching a frame edge) → REGENERATE the anchor at a LARGER scale / with more headroom. NEVER fix this with a centered zoom-crop in ffmpeg — that just re-crops the same overflow and pushes the head/hands further out of frame. The whole body must already sit comfortably inside the frame in the source render.

## Cost Discipline

Each 10s clip costs real money + wall-clock. Re-render only when defect is real. A 10-act 600s video = ~60 clips = ~30–60 min wall-clock + provider billing. Plan accordingly.
