---
name: codex-image-gen
description: "Generate AI images via Codex CLI using ChatGPT Pro OAuth — no API key needed, covered by Pro subscription. Supports text-to-image (T2I) AND image-to-image (i2i) with reference images for likeness/style transfer. Use when: (1) User wants to generate an image and has Codex CLI / ChatGPT Pro, (2) Avoiding paid Gemini/OpenAI/fal API tokens, (3) Other skills need a free image-gen backend, (4) Selfie / portrait generation with face/likeness preservation from a reference photo. Trigger words: 'codex image', 'gpt image', 'pro image gen', 'free image gen', 'generate image with codex', 'selfie from portrait'."
---

# Codex Image Generation

Generate images via the Codex CLI's built-in `imagegen` skill, routed through ChatGPT Pro OAuth. **No API key needed — covered by Pro subscription.** Supports both text-to-image (T2I) and image-to-image (i2i) with reference photos.

## When to use

- User has ChatGPT Pro and `codex` CLI installed
- Want to avoid burning paid API tokens (Gemini, OpenAI direct, fal, etc.)
- Need quick image gen without configuring a paid provider

## When NOT to use

- Need a specific aspect ratio / resolution other than 1024x1536 portrait → use `nanobanana` instead
- Batch / high-volume generation → use `nanobanana` (parallel + faster per call)
- User lacks `codex` CLI or ChatGPT Pro

## Usage

**Text-to-image (T2I):**
```bash
~/.claude/skills/codex-image-gen/scripts/generate.sh "your prompt" /path/to/output.png
```

**Image-to-image (i2i)** — pass one or more reference images after the output path:
```bash
~/.claude/skills/codex-image-gen/scripts/generate.sh "your prompt" /path/to/output.png /path/to/ref1.png [/path/to/ref2.png ...]
```

On success, prints the absolute path of the saved file and exits 0. On failure, prints diagnostics and exits 1.

### Examples

```bash
# T2I — Generate to Desktop
~/.claude/skills/codex-image-gen/scripts/generate.sh "a fox in a snowy forest, watercolor" ~/Desktop/fox.png

# i2i — Selfie with face/likeness from a portrait
~/.claude/skills/codex-image-gen/scripts/generate.sh \
  "casual selfie, same face and likeness from the reference, warm natural lighting, weekend-luxe outfit, candid expression" \
  ~/Desktop/me-selfie.png \
  ~/portraits/avatar.png

# i2i — Style transfer with multiple references
~/.claude/skills/codex-image-gen/scripts/generate.sh \
  "the subject from ref1 in the painting style of ref2" \
  /tmp/styled.png \
  /path/subject.jpg /path/style-ref.jpg

# Use in another skill / pipeline
IMG=$(~/.claude/skills/codex-image-gen/scripts/generate.sh "promo banner: clean apple keynote style" /tmp/banner.png)
echo "Saved to: $IMG"
```

### When to use i2i

- **Selfie / portrait generation** with face preservation (pass user's portrait as reference)
- **Style transfer** (pass a style reference)
- **Character consistency** across multiple generations (re-use same reference)
- **Outfit / pose variations** of a given person

## How it works

1. Calls `codex exec` with the prompt + an explicit save instruction
2. Codex's built-in `imagegen` skill generates the image (saved to `~/.codex/generated_images/<session>/`)
3. Codex copies it to the requested path
4. The script verifies the file exists and returns the path

The script grants `codex` write access only to the output directory via `--add-dir`.

## Output specs

- **Format:** PNG
- **Size:** 1024x1536 (portrait) — Codex default, not currently user-controllable
- **Time:** ~30-60s per image (sequential)

## Cost

**Free.** Covered by ChatGPT Pro subscription. No API tokens consumed.

## Limitations

- Single image per call (no batching)
- Fixed 1024x1536 dimensions
- Requires active Codex OAuth (`codex login` if not authenticated)
- Synchronous — blocks until complete

## Troubleshooting

| Symptom | Fix |
|---|---|
| `command not found: codex` | Install: `npm i -g @openai/codex` |
| `codex login required` | Run `codex login` and sign in with ChatGPT Pro account |
| File not produced after success log | Check `/tmp/codex-image-gen.log` — look for sandbox path errors. Make sure output path is in a directory `codex` can write to. |
| Want a different size | Use `nanobanana` skill instead — supports 1K/2K/4K and all aspect ratios |
