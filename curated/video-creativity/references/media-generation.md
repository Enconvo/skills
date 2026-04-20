# Rich Media Generation

HyperFrames compositions can embed images (`<img>`) and videos (`<video muted playsinline>`). Use this reference to add generated assets — still images or motion clips — to enrich scenes beyond SVG/CSS decoratives.

## The 4 generation capabilities

| Capability | Input | Output | Use for |
|---|---|---|---|
| **T2I** (text → image) | Prompt | Still image | Scene backgrounds, hero shots, mission patches, product concepts, abstract textures |
| **I2I** (image → image) | Prompt + reference images | Still image | Brand-consistent variants, portrait placement in scenes (agent selfie on billboard), editing existing assets |
| **T2V** (text → video) | Prompt | Short video clip | Animated backgrounds (stars, ocean, particles), cinematic b-roll, abstract motion loops |
| **I2V** (image → video) | Prompt + source image | Short video clip | Animate a T2I result, bring a still product shot to life, portrait-to-motion |

## Available tools in this environment

### T2I — Text-to-Image

**Primary tool:** `text_to_image` (directly available as a top-level tool).
- Params: `prompt`, `name`, `output_dir`, `modelParams.aspectRatio` (1:1 / 2:3 / 3:2 / 3:4 / 4:3 / 4:5 / 5:4 / 9:16 / 16:9 / 21:9), `modelParams.imageSize` (1K / 2K / 4K).
- Default: 1:1 @ 1K.
- For video backgrounds, always match the composition's aspect ratio (`16:9` landscape, `9:16` portrait, `1:1` square).
- For hero elements that will be placed against a dark canvas, prompt with "isolated on pure black background" to get clean compositing.

**Alternative:** `nanobanana` skill — Gemini image generation with precise dimension control. Use when you need specific resolutions (1K/2K/4K) that the default tool can't hit.

**Alternative:** `image_create` extension (`local_api image_create/...`) — routed through Enconvo's configured image provider.

### I2I — Image-to-Image

**Primary tool:** `image_to_image` (directly available as a top-level tool).
- Params: `prompt`, `images` (array of absolute paths or URLs), `name`, `output_dir`, `modelParams.aspectRatio`, `modelParams.imageSize`.
- Main use in videos: **putting the user's portrait into a scene** (agent selfie on a stadium big-screen, user's face on a magazine cover, etc.) — pass their portrait file as the reference and describe the scene.

### T2V — Text-to-Video

**Primary skill:** `veo` (Google Veo 3.1, Gemini family).
- Native aspect ratio control (9:16 default for mobile, 16:9 for landscape).
- Native resolution (720p / 1080p / 4K).
- Native duration control (4s / 6s / 8s).
- Best for cinematic quality, realistic motion.

**Alternative:** `seedance-api` (Seedance 1.5 Pro via Volcengine) — good for stylized motion.
**Alternative:** `grok-video-gen` — Grok AI via browser automation.
**Alternative:** `video_create` extension — routed through Enconvo's configured video provider.

### I2V — Image-to-Video

**Primary skill:** `veo` also supports I2V (image + prompt → animated video).
**Alternative:** `seedance-api` also supports I2V.

## When to reach for generated media

### Pick T2I (still image) when:

- A scene needs a **rich background** that SVG can't paint (a real photograph of a launch pad, a painterly illustration, a textured hero image).
- The visual is **held mostly static** (parallax/slow zoom only) — still images compress better in H.264 than motion.
- You need **exact framing** that's easier to compose than film.
- A **product shot / logo / icon** needs to appear authentically (prompt "an isolated photorealistic X on pure black").

### Pick T2V or I2V (video) when:

- The scene **needs motion that GSAP can't fake** (flowing water, drifting clouds, real fire plume, organic particles).
- A **hero moment** benefits from live footage (rocket liftoff, ocean splashdown, product spin).
- The composition's primary energy is **ambient/environmental**, not data/type-driven.

### Pick I2I when:

- **Brand consistency** matters across a series — generate variants from a reference image.
- **Portrait placement** — user's face appears in the video (on a billboard, as a character, as a poster).
- **Editing a prior generation** — swap a background, change lighting, fix a detail.

### Pick NOTHING (pure SVG/CSS) when:

- The style demands it (Swiss Pulse, Data Drift, Broadcast Bulletin — these are synthetic by design).
- **Deterministic reproducibility** matters (generated media shifts across runs).
- Render time and file size are constrained.

## Style preset × generation capability compatibility

| Style preset | T2I (bg/hero) | T2V/I2V (ambient) | I2I (portrait in scene) |
|---|---|---|---|
| Mission Control Cinematic | ✓ (launch pad, Moon surface, Earth-from-space) | ✓ (plume, starfield, clouds) | Rare |
| Swiss Pulse | ✗ (stay synthetic) | ✗ | ✗ |
| Velvet Standard | ✓✓ (editorial imagery is the point) | ✓ (slow drifts) | ✓ (portrait on magazine spread) |
| Data Drift | ✗ (analytical, no photography) | ✗ | ✗ |
| Maximalist Type | Rare (type is the visual) | Rare | Sometimes |
| Soft Signal | ✓✓ (documentary imagery) | ✓✓ (warm motion, nature) | ✓ (human subjects) |
| Neon Frequency | ✓ (duotone-processed) | ✓ (synth motion, glitch) | ✓ (portrait duotoned) |
| Folk Frequency | ✓✓ (organic imagery) | ✓ (gentle nature motion) | Rare |
| Shadow Cut | ✓ (monochrome stills) | ✓ (b-roll) | Sometimes |
| Deconstructed | ✓ (raw stills to collage) | ✓ | ✓ |
| Broadcast Bulletin | ✓ (news stills, maps) | ✓ (live ops footage) | ✓ (anchor portrait) |

## Adding generated media to a spec

Add a **Media Assets** block to the spec (after Visual Identity, before Scene Breakdown). Example:

```markdown
## Media Assets

### Generated stills (T2I)
| ID | Type | Aspect | Description / prompt | Used in scene |
|---|---|---|---|---|
| `bg-launchpad.png` | T2I | 16:9 | "Photorealistic launch pad at dawn, SLS rocket silhouetted, dramatic backlighting, shot on Sony A7R V, cinematic, no AI gloss" | Scene 2 background (parallax) |
| `moon-surface.png` | T2I | 16:9 | "Close-up of lunar far-side surface, crater texture, cold light, photorealistic, National Geographic aesthetic" | Scene 5 full-frame |

### Generated motion (T2V)
| ID | Type | Duration | Aspect | Description / prompt | Used in scene |
|---|---|---|---|---|---|
| `plume-loop.mp4` | T2V (Veo) | 6s | 16:9 | "Slow-motion rocket exhaust plume, orange-to-yellow, against pure black, seamless loop" | Scene 2 over SVG rocket |
| `ocean-dawn.mp4` | T2V (Veo) | 8s | 16:9 | "Calm Pacific dawn, gentle waves, warm horizon glow, static camera, cinematic" | Scene 7 ambient background |

### Reference-driven (I2I)
| ID | Type | Source | Prompt | Used in scene |
|---|---|---|---|---|
| `crew-portrait-composite.png` | I2I | `crew.jpg` | "Same four astronauts, moved to mission control room background, warm broadcast lighting" | Scene 5 nameplate area |
```

Generate each asset **before** the hyperframes build, save to the project root, and reference by filename in the scenes.

## Wiring generated media into HyperFrames

### Still images as background

```html
<div id="bg-scene2" class="scene-bg" style="
  position: absolute; inset: 0;
  background-image: url('bg-launchpad.png');
  background-size: cover;
  background-position: center;
  opacity: 0;
">
</div>

<script>
  tl.fromTo('#bg-scene2',
    { opacity: 0, scale: 1.05 },
    { opacity: 1, scale: 1.0, duration: 1.0, ease: 'power2.out' }, 0.1);
</script>
```

**Gotcha:** Always pair a generated photo background on a dark-canvas style with a dark overlay (`background: linear-gradient(rgba(5,7,13,0.55), rgba(5,7,13,0.75))`) so text stays legible. WCAG contrast still applies.

### Video as background

```html
<video id="vid-plume"
       data-start="5.6" data-duration="14.8" data-track-index="2"
       src="plume-loop.mp4"
       muted playsinline loop
       style="position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; z-index: 1;">
</video>
```

**Gotcha:** Video must be `muted playsinline`. Never use a `<video>` element for audio — use a separate `<audio>` tag.

### Portrait in scene (I2I composite)

Useful when the user wants to appear in the video. Pass the agent's portrait (`avatars/portrait.jpg`) as the reference to `image_to_image`, describe the scene context, save output, embed as a still in the scene.

## Prompt discipline

All generated media prompts in a spec must follow these rules:

1. **Style-match the preset.** A Mission Control video's generated assets should read like NASA press kit photos, not stock-footage-style polish.
2. **Anti-AI-gloss directive.** Every realistic-image prompt ends with: *"shot on Sony A7R V and 50mm f/1.4, real photograph aesthetic, no AI smoothing, no plastic skin, natural imperfections, editorial quality."* See `image-prompt-enhancer` skill for the full realism framework.
3. **Isolated backgrounds for hero elements.** Prompt "isolated on pure black background" or "isolated on transparent background" for objects that will be composited into a scene.
4. **Aspect ratio matches composition.** Never generate 1:1 for a 16:9 scene unless it's a side element.
5. **Seed where possible.** If the generator supports seeds, write the seed into the spec for reproducibility.

## Cost / time awareness

| Capability | Typical time | Rough cost |
|---|---|---|
| T2I | 5–15s | Cheap |
| I2I | 10–20s | Cheap |
| T2V (Veo, 8s clip) | 60–120s | Medium-high |
| I2V (Veo, 8s clip) | 60–120s | Medium-high |

For a 60s explainer: 3–5 T2I assets ≈ 1 minute total. 1–2 T2V clips ≈ 2–4 minutes. Budget accordingly — don't generate 10 videos when 2 clips + 4 stills will do.

## Quick checklist before handoff

- [ ] Every generated asset is listed in the spec's Media Assets block with prompt, aspect ratio, and target scene.
- [ ] Every photo background on a dark-canvas style has a planned dark overlay (for contrast).
- [ ] Every T2V/I2V clip has `muted playsinline` in the spec's scene description.
- [ ] All asset filenames are relative to the project root.
- [ ] The WCAG contrast audit will still pass after the photo background is composited (verify by eye, then `hyperframes validate`).
