---
name: nanobanana
description: "AI image generation via Google Nano Banana (Gemini image models) with native aspect ratio and resolution control. Use when: (1) Generating images with specific aspect ratios (16:9, 9:16, 1:1, etc.), (2) Generating images at specific resolutions (1K, 2K, 4K), (3) Other skills need image generation backend (pptx-design-agent, docx-design-agent, xlsx-design-agent), (4) User says 'generate image', 'nanobanana', 'nano banana', or needs AI image generation with precise dimension control."
---

# Nano Banana Image Generation

Generate images via Google's Nano Banana models with **native aspect ratio and resolution control** — no more prompt-only AR hacks.

## Models

| Model | ID | Speed | Quality | Use When |
|-------|----|-------|---------|----------|
| **Nano Banana Pro** (default) | `gemini-3-pro-image-preview` | ~16s | Professional, 4K capable | Default for all tasks |
| Nano Banana | `gemini-2.5-flash-image` | ~8s | Good, fast | User explicitly asks for speed/non-pro |

**Default: Nano Banana Pro.** Only use non-pro if user explicitly requests it (e.g., "use flash", "use non-pro", "faster model").

## Pricing

| Model | Resolution | Cost/Image | Batch (50% off) |
|-------|-----------|------------|------------------|
| **Nano Banana Pro** | 1K / 2K | **$0.134** | $0.067 |
| **Nano Banana Pro** | 4K | **$0.240** | $0.120 |
| **Nano Banana Flash** | All sizes | **$0.039** | $0.0195 |

**Cost examples:**
- Typical PPTX deck (10 slides, Pro 2K backgrounds): **~$1.34**
- Same deck with Flash: **~$0.39** (71% cheaper)
- Single 4K print-quality image (Pro): **$0.24**

Flash is ~3.4x cheaper than Pro. Use Flash for drafts, bulk generation, or when user is cost-conscious. Use Pro (default) for final/professional output.

## Aspect Ratios

| AR | Name | Pixel Dims (2K) | Best For |
|----|------|-----------------|----------|
| **16:9** (default) | Widescreen | 2048 × 1152 | PPTX backgrounds, YouTube, desktop wallpaper |
| 9:16 | Portrait | 1152 × 2048 | Mobile, Instagram Stories, PPTX side panels |
| 1:1 | Square | 2048 × 2048 | Social media, icons, profile pics |
| 3:2 | Classic landscape | 2048 × 1365 | Photography, print |
| 2:3 | Classic portrait | 1365 × 2048 | Book covers, posters |
| 4:3 | Standard | 2048 × 1536 | Presentations (4:3 format), iPad |
| 3:4 | Standard portrait | 1536 × 2048 | Print, documents |
| 5:4 | Near-square landscape | 2048 × 1638 | Large prints |
| 4:5 | Instagram | 1638 × 2048 | Instagram feed posts |
| 21:9 | Ultrawide | 2048 × 878 | Cinematic, panoramic strips |

**Default: 16:9.** Show the table above when user asks for "list of aspect ratios" or "AR options".

## Resolutions

| Size | Square (1:1) | Widescreen (16:9) | Portrait (9:16) | Gen Time | Best For |
|------|-------------|-------------------|-----------------|----------|----------|
| 1K | 1024 × 1024 | 1024 × 576 | 576 × 1024 | ~13s | Drafts, thumbnails, quick tests |
| **2K** (default) | 2048 × 2048 | 2048 × 1152 | 1152 × 2048 | ~16s | PPTX/DOCX backgrounds, web, screen use |
| 4K | 4096 × 4096 | 4096 × 2304 | 2304 × 4096 | ~22s | Print, high-DPI displays, large format |

**Default: 2K.** Rationale: 2K at 16:9 (2048×1152) is the sweet spot for PPTX slide backgrounds (13.33"×7.5" at ~150 DPI). Sharp on screen, good for print, fast generation.

Show the table above when user asks for "list of resolutions" or "resolution options".

## Usage

### Script Location

All scripts are in the `scripts/` subdirectory of this skill.

1. Determine this SKILL.md file's directory path as `SKILL_DIR`
2. Script path = `${SKILL_DIR}/scripts/generate.py`

### Prerequisites

```bash
python3 -m pip install google-genai Pillow --quiet
```

### Authentication

The script tries auth in this order:
1. `GEMINI_API_KEY` environment variable
2. `--api-key` flag
3. OAuth credentials from Gemini CLI (`~/.gemini/oauth_creds.json`)

If no auth found, the script prints setup instructions.

### Commands

```bash
# Basic image generation (defaults: pro model, 16:9, 2K)
python3 ${SKILL_DIR}/scripts/generate.py --prompt "A moody cityscape at night" --output city.png

# Specify aspect ratio and resolution
python3 ${SKILL_DIR}/scripts/generate.py --prompt "A cute cat" --output cat.png --ar 1:1 --size 4K

# Use non-pro (flash) model
python3 ${SKILL_DIR}/scripts/generate.py --prompt "Quick sketch" --output sketch.png --model flash

# Portrait for mobile / side panels
python3 ${SKILL_DIR}/scripts/generate.py --prompt "Forest scene" --output forest.png --ar 9:16

# With reference image (style transfer / variation)
python3 ${SKILL_DIR}/scripts/generate.py --prompt "Same style but in winter" --output winter.png --reference summer.png

# Low-res draft
python3 ${SKILL_DIR}/scripts/generate.py --prompt "Test concept" --output draft.png --size 1K

# Ultrawide panoramic strip
python3 ${SKILL_DIR}/scripts/generate.py --prompt "Mountain range" --output pano.png --ar 21:9
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--prompt`, `-p` | Image generation prompt (required) | — |
| `--output`, `-o` | Output file path | `generated.png` |
| `--ar` | Aspect ratio | `16:9` |
| `--size` | Resolution: `1K`, `2K`, `4K` | `2K` |
| `--model`, `-m` | `pro` or `flash` | `pro` |
| `--reference`, `--ref` | Reference image path(s) for vision input | — |
| `--api-key` | Gemini API key (overrides env var) | — |
| `--json` | Output result as JSON | `false` |

### Output

On success, the script prints:
```
OK: saved to city.png (2048x1152, AR=1.78, model=gemini-3-pro-image-preview)
```

With `--json`:
```json
{
  "status": "ok",
  "path": "city.png",
  "width": 2048,
  "height": 1152,
  "ar": 1.78,
  "model": "gemini-3-pro-image-preview",
  "aspect_ratio": "16:9",
  "image_size": "2K"
}
```

## Recommended AR by Use Case

| Use Case | AR | Size | Why |
|----------|-----|------|-----|
| **Headshot / portrait photo** | **3:4** | 2K | Classic portrait framing, natural phone-camera feel |
| **Selfie (Instagram feed)** | **4:5** | 2K | Instagram feed post standard |
| **Selfie (Stories / full mobile)** | **9:16** | 2K | Full vertical mobile screen |
| **Profile pic / avatar** | **1:1** | 2K | Square crop, universal across platforms |
| **PPTX background** | **16:9** | 2K | Matches widescreen slide ratio |
| **PPTX side panel** | **9:16** or **3:4** | 2K | Portrait crop for split layouts |
| **Panoramic / cinematic** | **21:9** | 2K | Ultrawide strip |
| **Photography / print** | **3:2** or **2:3** | 4K | Classic photo ratio, high-res for print |
| **Book cover / poster** | **2:3** | 2K | Tall portrait, standard print format |

When user asks for a "portrait", "selfie", or "headshot" without specifying AR, **default to 3:4 at 2K**.

## Integration with Design Skills

When called from pptx-design-agent, docx-design-agent, or xlsx-design-agent:

| Image Role | Recommended AR | Recommended Size |
|------------|---------------|-----------------|
| PPTX full-bleed background | 16:9 | 2K |
| PPTX side panel | 9:16 or 3:4 | 2K |
| PPTX content image | Match slot ratio | 2K |
| PPTX accent strip | 21:9 | 2K |
| DOCX cover banner | 16:9 or 3:1 (crop) | 2K |
| DOCX content illustration | 4:3 or 1:1 | 1K |
| XLSX cover image | 16:9 | 2K |

**Key advantage over baoyu-danger-gemini-web**: Native AR and resolution parameters mean the API returns images at the EXACT requested dimensions — no more prompt-only AR requests that Gemini ignores, no more post-generation cropping.

## Post-Generation Verification

The script automatically verifies dimensions after generation. If the output doesn't match the requested AR (>5% deviation), it warns:

```
WARNING: AR mismatch — requested 16:9 (1.78), got 1024x1024 (1.00). Consider regenerating.
```

This should be rare with native AR params but serves as a safety net.
