---
name: image-prompt-enhancer
description: "Transform simple image prompts into hyper-realistic, structured prompts that produce photorealistic AI images. Applies 7 realism pillars (real camera specs, anti-AI gloss, physical imperfections, situational lighting, documentary aesthetic). Use when: user says 'enhance prompt', 'make it realistic', 'photorealistic prompt', or when a basic image prompt needs upgrading for Nano Banana / Gemini generation."
---

# Image Prompt Enhancer

A thin realism layer that wraps any image prompt with real camera specs and anti-AI artifact directives — without overriding the user's creative intent.

**Use when:** User provides an image prompt and wants the result to look like a real photograph instead of an obvious AI render.

**Trigger phrases:** "enhance prompt", "make it realistic", "improve this prompt", "photorealistic prompt", or when a basic image prompt needs upgrading for Nano Banana / Gemini generation.

## Design Philosophy

This enhancer is intentionally minimal. It adds only two things:

1. **Real camera/lens specs** — anchors the model in photographic reality
2. **Anti-AI directives** — fights smoothing, plastic skin, HDR artifacts

It does **NOT** override lighting, environment, aesthetic, mood, or any creative intent. The user's prompt is the sole creative authority. This means it works equally well for:
- Glamorous professional portraits
- Gritty street photography
- Cozy candid scenes
- Raw documentary shots

## Usage

### Script Location

All scripts are in the `scripts/` subdirectory of this skill.

1. Determine this SKILL.md file's directory path as `SKILL_DIR`
2. Script path = `${SKILL_DIR}/scripts/enhance.py`

### Commands

```bash
# Basic enhancement (auto-selects mirrorless camera, high realism)
python3 ${SKILL_DIR}/scripts/enhance.py --prompt "a woman in a coffee shop"

# Flat text output for piping
python3 ${SKILL_DIR}/scripts/enhance.py --prompt "a homeless man sleeping under a bridge" --flat

# Save as JSON file
python3 ${SKILL_DIR}/scripts/enhance.py --prompt "two friends at a park" --output /tmp/enhanced.json

# Specify camera style
python3 ${SKILL_DIR}/scripts/enhance.py --prompt "street scene in Tokyo" --camera smartphone

# Maximum realism (more anti-AI directives)
python3 ${SKILL_DIR}/scripts/enhance.py --prompt "portrait of an elderly fisherman" --realism ultra

# Add custom negative directives
python3 ${SKILL_DIR}/scripts/enhance.py --prompt "a chef cooking" --negative "No motion blur." "No lens flare."

# Pipe directly to nanobanana
PROMPT=$(python3 ${SKILL_DIR}/scripts/enhance.py -p "a barista making coffee" --flat)
python3 ~/.claude/skills/nanobanana/scripts/generate.py --prompt "$PROMPT" --output /tmp/barista.png --ar 3:4 --size 2K
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--prompt`, `-p` | Image prompt to enhance (required) | -- |
| `--camera`, `-c` | Camera style: `dslr`, `mirrorless`, `smartphone`, `film` | auto-detect from prompt |
| `--realism`, `-r` | Realism level: `standard`, `high`, `ultra` | `high` |
| `--output`, `-o` | Save enhanced prompt as JSON file | stdout |
| `--flat` | Output flat text string only (for piping) | `false` |
| `--negative`, `-n` | Extra negative directives to append | -- |

### Camera Auto-Detection

The script auto-selects camera type based on keywords in the prompt:

| Keywords | Camera Type |
|----------|-------------|
| selfie, mirror selfie, phone camera, front camera, instagram | `smartphone` |
| film look, analog, vintage, 35mm film, grain, retro | `film` |
| *(everything else)* | `mirrorless` |

Override with `--camera` if the auto-detection doesn't match your intent.

### Output

Default JSON output:

```json
{
  "enhanced_prompt": "Captured with a Sony A7R V and 35mm f/1.4 GM at f/2.8, ISO 200, 1/250s. a woman in a coffee shop. This must look like a real photograph, not an AI render. No AI smoothing or plastic skin texture. No simulated depth of field with unrealistic bokeh. ...",
  "meta": {
    "original_prompt": "a woman in a coffee shop",
    "camera": { "body": "Sony A7R V", "lens": "35mm f/1.4 GM", "settings": "f/2.8, ISO 200, 1/250s" },
    "realism_level": "high",
    "anti_ai_directives": ["No AI smoothing or plastic skin texture.", "..."]
  }
}
```

With `--flat`, outputs just the enhanced prompt text string.

### Realism Levels

| Level | Directives | Use When |
|-------|-----------|----------|
| `standard` | 3 directives (no smoothing, no fake bokeh, no filters) | Quick enhancement, less restrictive |
| `high` (default) | 7 directives (+ no AI gloss, no HDR artifacts, no halos, real textures) | General use |
| `ultra` | 10 directives (+ indistinguishable from photo, sensor noise, no beauty filter) | Maximum realism, people close-ups |

### Camera Presets

| Type | Bodies | Lenses |
|------|--------|--------|
| `mirrorless` | Sony A7R V, Fujifilm X-T5 | 23mm f/1.4, 35mm f/1.4, 50mm f/1.4, 56mm f/1.2 |
| `dslr` | Canon EOS R5, Nikon Z9, Nikon Z8 | 50mm f/1.2, 85mm f/1.2, 85mm f/1.4L |
| `smartphone` | iPhone 15/16 Pro, Samsung Galaxy S24 Ultra | 23-24mm wide |
| `film` | Leica M6, Contax T2 | 35mm Summicron, 38mm Sonnar |

A random camera+lens combo is selected from the chosen type on each run.

## Integration with Nano Banana

```bash
# Enhance then generate
PROMPT=$(python3 ${SKILL_DIR}/scripts/enhance.py -p "a barista making coffee" --flat)
python3 ~/.claude/skills/nanobanana/scripts/generate.py --prompt "$PROMPT" --output /tmp/barista.png --ar 3:4 --size 2K
```

## Recommended Workflow

1. User provides prompt (any style, any intent)
2. Run enhance.py to wrap it with camera specs + anti-AI directives
3. Feed enhanced prompt to nanobanana
4. If result still looks AI-ish, increase realism level to `ultra`

## Background: The 7 Realism Pillars

These techniques were discovered from the highest-voted Reddit posts (r/scintai, r/GoogleGeminiAI, r/StableDiffusion, r/midjourney) that make AI images look real. The enhancer applies pillars #2 and #3 automatically. The others are best handled in the user's own prompt:

1. **Structured JSON Format** — JSON prompts get 7/10 usable images vs 2-3/10 with flat text
2. **Real Camera + Lens + Settings** — anchors the model in photographic reality *(applied by enhancer)*
3. **Anti-AI Gloss Directives** — negative instructions that break the "AI look" *(applied by enhancer)*
4. **Physical Imperfections** — describe in your prompt if needed (skin texture, fabric wrinkles, dust motes)
5. **Situational Lighting** — describe in your prompt (e.g., "warm overhead fluorescent" not "cinematic lighting")
6. **Documentary / Candid Aesthetic** — describe in your prompt if that's the intent
7. **Neutral Descriptive Language** — avoid "beautiful", "stunning", "perfect" in your prompt
