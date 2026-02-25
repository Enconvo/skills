---
name: video-prompt-enhancer
description: "Transform simple video prompts into cinematic, structured prompts for AI video generation (Veo 3, Seedance, Grok, Kling, Runway, etc). Adds real camera/lens specs, camera movement, and anti-AI directives without overriding creative intent. Use when: user says 'enhance video prompt', 'make video realistic', 'video prompt', or when a basic video prompt needs upgrading."
---

# Video Prompt Enhancer

A thin realism layer that wraps any video prompt with real cinematography specs, camera movement, and anti-AI artifact directives — without overriding the user's creative intent.

**Use when:** User provides a video prompt and wants the result to look like real footage instead of an obvious AI render.

**Trigger phrases:** "enhance video prompt", "make video realistic", "video prompt", "cinematic prompt", or when a basic video prompt needs upgrading for any AI video generator (Veo 3, Seedance, Grok, Kling, Runway, etc).

## Design Philosophy

Same approach as image-prompt-enhancer — intentionally minimal. It adds only three things:

1. **Real camera/lens specs** — anchors the model in cinematographic reality
2. **Camera movement** — a single, clear movement instruction (AI video models handle one movement well, multiple = chaos)
3. **Anti-AI directives** — fights smoothing, subtitles, fade transitions, plastic textures

It does **NOT** override lighting, environment, aesthetic, audio content, dialogue, mood, or any creative intent. The user's prompt is the sole creative authority.

## Usage

### Script Location

All scripts are in the `scripts/` subdirectory of this skill.

1. Determine this SKILL.md file's directory path as `SKILL_DIR`
2. Script path = `${SKILL_DIR}/scripts/enhance_video.py`

### Commands

```bash
# Basic enhancement (auto-selects cinematic camera, push-in movement, high realism)
python3 ${SKILL_DIR}/scripts/enhance_video.py --prompt "a woman walking through a Tokyo street market"

# Flat text output for piping
python3 ${SKILL_DIR}/scripts/enhance_video.py --prompt "a chef cooking ramen in a tiny kitchen" --flat

# Save as JSON file
python3 ${SKILL_DIR}/scripts/enhance_video.py --prompt "two friends laughing at a cafe" --output /tmp/enhanced.json

# Specify camera style
python3 ${SKILL_DIR}/scripts/enhance_video.py --prompt "selfie vlog in Tokyo" --style smartphone

# Specify camera movement
python3 ${SKILL_DIR}/scripts/enhance_video.py --prompt "a man sitting on a bench" --movement static

# Found-footage horror style
python3 ${SKILL_DIR}/scripts/enhance_video.py --prompt "exploring a dark abandoned hospital hallway" --style vhs --movement handheld

# Maximum realism
python3 ${SKILL_DIR}/scripts/enhance_video.py --prompt "a fisherman casting a net at dawn" --realism ultra

# Add custom negative directives
python3 ${SKILL_DIR}/scripts/enhance_video.py --prompt "a dancer performing" --negative "No slow motion." "No lens flare."
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--prompt`, `-p` | Video prompt to enhance (required) | -- |
| `--style`, `-s` | Camera style: `cinematic`, `documentary`, `handheld`, `smartphone`, `vhs` | auto-detect |
| `--movement`, `-m` | Camera movement: `static`, `push`, `pull`, `orbit`, `tracking`, `handheld` | auto-detect |
| `--realism`, `-r` | Realism level: `standard`, `high`, `ultra` | `high` |
| `--output`, `-o` | Save enhanced prompt as JSON file | stdout |
| `--flat` | Output flat text string only (for piping) | `false` |
| `--negative`, `-n` | Extra negative directives to append | -- |

### Auto-Detection

**Camera style** is auto-detected from keywords in the prompt:

| Keywords | Style |
|----------|-------|
| selfie, vlog, phone camera, tiktok, instagram | `smartphone` |
| vhs, found footage, camcorder, home video, tape | `vhs` |
| handheld, shaky, run, chase, follow | `handheld` |
| documentary, interview, news, behind the scenes | `documentary` |
| *(everything else)* | `cinematic` |

**Camera movement** is auto-detected from action words:

| Keywords | Movement |
|----------|----------|
| sits, standing, static, tripod, fixed | `static` |
| push in, dolly in, close in, zoom in | `push` |
| pull out, dolly out, reveal, pull back | `pull` |
| orbit, circle around, rotate around | `orbit` |
| tracking, follow, walking, running, moving through | `tracking` |
| handheld, shaky, vhs, found footage, pov | `handheld` |
| *(default)* | `push` (gentle push-in) |

### Output

Default JSON output:

```json
{
  "enhanced_prompt": "Shot on Arri Alexa LF with 50mm Cooke S7/i at f/2.8, ISO 800, 24fps, HDR10. Slow dolly push in toward the subject. a woman walking through a Tokyo street market. This must look like real footage, not an AI render. No subtitles, captions, or text overlays. ...",
  "meta": {
    "original_prompt": "a woman walking through a Tokyo street market",
    "camera": { "body": "Arri Alexa LF", "lens": "50mm Cooke S7/i", "settings": "f/2.8, ISO 800, 24fps, HDR10" },
    "camera_movement": "Slow dolly push in toward the subject.",
    "realism_level": "high",
    "anti_ai_directives": ["No subtitles, captions, or text overlays.", "..."]
  }
}
```

With `--flat`, outputs just the enhanced prompt text string.

### Realism Levels

| Level | Directives | Use When |
|-------|-----------|----------|
| `standard` | 3 (no subtitles, no watermarks, no smoothing) | Quick enhancement |
| `high` (default) | 8 (+ no fake bokeh, no HDR artifacts, no fade transitions, no unwanted music, real textures) | General use |
| `ultra` | 13 (+ indistinguishable from real, sensor noise, no beauty filter, no CGI, natural motion blur) | Maximum realism |

### Camera Style Presets

| Style | Bodies | Lenses | Best For |
|-------|--------|--------|----------|
| `cinematic` | Arri Alexa LF/Mini LF, RED V-Raptor, Sony Venice 2 | 35-85mm Cooke/Zeiss/Sigma Cine | Narrative, ads, polished content |
| `documentary` | Sony FX6, Canon C70, Blackmagic Pocket 6K | 18-70mm zoom/prime | Interviews, real-world coverage |
| `handheld` | Sony A7S III, Sony FX3, Canon R5 C | 24-35mm fast primes | Action, chase, immersive POV |
| `smartphone` | iPhone 15/16 Pro, Samsung Galaxy S24 Ultra | 23-24mm wide | Selfie, vlog, social media |
| `vhs` | Sony Handycam CCD-TRV, JVC GR-C1 | Built-in | Found footage, horror, retro |

### Camera Movement Presets

| Movement | Description | Works Well For |
|----------|-------------|----------------|
| `static` | Locked-off tripod, no movement | Dialogue, still subjects, tableaux |
| `push` | Slow dolly push toward subject | Building tension, focus on detail |
| `pull` | Slow dolly pull revealing scene | Reveals, establishing shots |
| `orbit` | Slow arc around subject | Product shots, hero moments |
| `tracking` | Lateral/following movement | Walking, running, movement scenes |
| `handheld` | Natural shake and micro-movement | Documentary, horror, POV, realism |

## Video Prompt Writing Tips

These best practices come from Reddit research (r/VEO3, r/PromptEngineering, r/ChatGPT, r/aivideo, r/comfyui). The enhancer handles camera specs + anti-AI; you handle the rest in your prompt:

### What to Include in YOUR Prompt

1. **One action per clip.** Most AI video models generate 4-16 seconds. Multiple actions = chaos. Focus each prompt on a single clear action or movement.

2. **Audio cues.** Audio descriptions dramatically improve realism in models that support it (Veo 3, etc). Always describe ambient sounds, sound effects, and whether music should be present or absent.
   - Good: `"ambient sounds of market chatter, sizzling food, distant traffic"`
   - Good: `"quiet room, only the ticking of a wall clock"`

3. **Dialogue formatting.** Use colon format to prevent subtitle generation:
   - Good: `She speaks (melancholic, trembling voice): "I tried everything."`
   - Bad: `She says "I tried everything."` (may trigger subtitles)
   - Specify accent, tone, emotion in parentheses

4. **Specific physical descriptions.** Concrete > abstract.
   - Good: `"shuffling with hunched shoulders"` (reads as real)
   - Bad: `"walking sadly"` (reads as AI)

5. **Lighting.** Unspecified lighting = flat AI look. Describe it:
   - `"warm afternoon sun creating long shadows between vendor stalls"`
   - `"single overhead fluorescent, harsh, no fill light"`
   - NOT: `"cinematic lighting"`, `"dramatic lighting"`

6. **Character details.** For consistency, describe characters with 10+ attributes:
   - `"SARAH (50s), short gray hair, weathered face, faded blue cardigan, reading glasses pushed up on her forehead"`

### What to Avoid

- Multiple actions in one prompt (one action per clip)
- Complex combined camera movements (pan + zoom + dolly = chaos)
- Close-ups of hands (common AI video distortion issue)
- More than 2-3 characters per scene (consistency breaks down)
- Vague/abstract descriptions ("beautiful", "amazing")
- Exact timestamp breakdowns (most models don't reliably follow precise timing)

## Example Prompts (from Reddit)

**Pharmaceutical ad** (3.7K upvotes, r/ChatGPT):
```
Muted colors, somber muted lighting. A woman, SARAH (50s), sits on a couch
in a cluttered living room. She speaks (melancholic, slightly trembling voice):
"I tried everything for my depression, nothing worked."
```

**Travel vlog selfie** (63 upvotes, r/GrowthHacking):
```
A selfie video of a travel blogger exploring a bustling Tokyo street market.
She's wearing a vintage denim jacket and has excitement in her eyes. The
afternoon sun creates beautiful shadows between the vendor stalls. She's
sampling street foods while talking, occasionally looking into the camera.
The image is slightly grainy, looks very film-like. She speaks in a British
accent: "Okay, you have to try this place when you visit Tokyo."
```

**Horror found footage** (r/AIVideo4all):
```
Shaky handheld domestic handycam footage. Continuous one shot walking in a
dark black narrow cavern. We keep walking through the narrow dark tunnel.
Suddenly there is a curve that turns left. After the curve, we look up to
discover ancient symbols carved on the stone. Shaky handheld, blurry, chaotic,
soft natural colors, ultra detailed.
```

## Integration with Image Prompt Enhancer

For image-to-video workflows (recommended by Reddit for best results):

```bash
# 1. Generate a starting frame with image-prompt-enhancer + nanobanana
IMG_PROMPT=$(python3 ~/.claude/skills/image-prompt-enhancer/scripts/enhance.py \
  -p "a fisherman casting a net at dawn, golden light on water" --flat)
python3 ~/.claude/skills/nanobanana/scripts/generate.py \
  --prompt "$IMG_PROMPT" --output /tmp/start_frame.png --ar 16:9

# 2. Enhance the video prompt
python3 ${SKILL_DIR}/scripts/enhance_video.py \
  -p "the fisherman pulls back and casts the net in a wide arc, water droplets catching the golden light, ambient sound of lapping waves and distant seabirds" --flat

# 3. Use the starting frame + enhanced prompt with your video generator (Veo 3, Seedance, Grok, etc)
```

## Recommended Workflow

1. User provides video prompt (any style, any intent)
2. Run enhance_video.py to wrap it with camera specs + movement + anti-AI directives
3. Include audio cues and dialogue formatting in your prompt (enhancer doesn't add these)
4. Feed enhanced prompt to your video generator (Veo 3, Seedance, Grok, Kling, Runway, etc)
   - **For Grok I2V specifically:** do not click `Make video` until BOTH are ready: (a) reference image upload is visibly complete (no upload/progress state), and (b) the submitted prompt/card is settled.
5. If result still looks AI-ish, increase realism level to `ultra`
6. For maximum control, generate a starting frame first (image-to-video workflow)
