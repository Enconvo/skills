# codex-image-gen

Generate AI images via the Codex CLI using ChatGPT Pro OAuth — **no API key needed, covered by Pro subscription**. Supports both text-to-image (T2I) and image-to-image (i2i) with reference photos for likeness/style transfer.

## Why this exists

ChatGPT Plus/Pro OAuth tokens grant image generation access *only* through the Codex CLI's internal endpoint — public OpenAI API endpoints (e.g. `openai/gpt-image-2` via `/v1/images/generations`) reject subscription-token auth with HTTP 404. This skill bridges that gap, letting agents call image gen for free if the user already pays for ChatGPT Pro.

## Requirements

- `codex` CLI installed: `npm i -g @openai/codex`
- Active Codex OAuth: `codex login` (sign in with ChatGPT Plus/Pro account)
- macOS or Linux with `bash`, `python3`, `chmod`

## Usage

```bash
# T2I
./scripts/generate.sh "your prompt" /path/to/output.png

# I2I — pass reference image(s) after the output path
./scripts/generate.sh "selfie of person, same face/likeness" /path/to/output.png /path/to/portrait.png
```

On success: prints absolute path of the saved file, exits 0.
On failure: prints diagnostics + tail of `/tmp/codex-image-gen.log`, exits non-zero.

## Output specs

- PNG, 1024x1536 (portrait), Codex default
- ~30–60s per image (sequential)
- Single image per call

For specific aspect ratios / 1K-4K control, use `nanobanana` instead.

## See also

- `SKILL.md` — full usage docs, examples, troubleshooting
