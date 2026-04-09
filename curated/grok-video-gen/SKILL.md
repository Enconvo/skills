---
name: grok-video-gen
description: Generate videos using Grok AI via Chrome browser automation. Supports T2V (text-to-video) and I2V (image-to-video) with reference image uploads. Uses grok.com/imagine. Use when user says "Grok video", "create video with Grok", or wants AI video generation through Grok.
---

# Grok Video Generator

Generate videos using Grok AI via real Chrome browser automation (CDP) on grok.com/imagine.

## Script Directory

**Agent Execution Instructions**:
1. Determine this SKILL.md file's directory path as `SKILL_DIR`
2. Script path = `${SKILL_DIR}/scripts/<script-name>.ts`
3. Replace all `${SKILL_DIR}` in this document with the actual path

**Script Reference**:
| Script | Purpose |
|--------|---------|
| `scripts/main.ts` | CLI entry point for Grok image & video generation |
| `scripts/grok-utils.ts` | Chrome CDP utilities (based on baoyu-post-to-x patterns) |

## Prerequisites

- Google Chrome or Chromium
- `bun` runtime
- Logged in to x.com (session saved in Chrome profile)

## Usage

### Video Generation (uses grok.com/imagine)

```bash
# Text-to-video (T2V)
npx -y bun ${SKILL_DIR}/scripts/main.ts --video "A cat playing piano" --output cat.mp4

# Video with specific aspect ratio
npx -y bun ${SKILL_DIR}/scripts/main.ts --video --aspect 9:16 "Ocean waves crashing" --output waves.mp4

# Image-to-video (I2V) — animate a photo
npx -y bun ${SKILL_DIR}/scripts/main.ts --video \
  -r /path/to/selfie.png \
  --aspect 9:16 \
  "Animate this photo. The woman turns toward camera with a confident smile and says hello." \
  --output animated.mp4 \
  --timeout 600
```

### I2V Best Practices

| Aspect | Recommendation |
|--------|---------------|
| **Aspect ratio** | Always specify `--aspect 9:16` for portrait, `--aspect 16:9` for landscape |
| **Timeout** | Use `--timeout 600` for video (generation takes 1-3 minutes) |
| **Prompt style** | Describe the motion/action you want, not just the scene |
| **Reference image** | Higher resolution = better quality output |
| **Output resolution** | Grok outputs ~416x752 for 9:16 — this is normal |
| **Speech** | Grok I2V does NOT generate real speech audio — for talking head videos with actual voice, use Seedance (`--agent` mode) instead |

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `<text>` | Generation prompt (positional) | — |
| `--prompt`, `-p` | Prompt text (alternative to positional) | — |
| `--reference`, `-r` | Reference image path (repeatable for multiple) | — |
| `--output`, `-o` | Output file path | `grok-image.png` |
| `--all` | Save all generated images (numbered: name-1.png, name-2.png) | `false` |
| `--imagine` | Use `grok.com/imagine` for image gen (clicks 📷 Image mode) | `false` |
| `--video` | Generate video (clicks 🎬 Video mode on `grok.com/imagine`) | `false` |
| `--aspect <ratio>` | Aspect ratio: `2:3`, `3:2`, `1:1`, `9:16`, `16:9` | — |
| `--timeout` | Max wait time in seconds | 120 (image) / 300 (video) |
| `--profile <dir>` | Custom Chrome profile directory | auto |
| `--json` | Output JSON with URLs and paths | `false` |

## How It Works

### Video Mode (`--video`)
1. Launches Chrome with CDP (reuses login session)
2. Navigates to `grok.com/imagine`
3. **Clicks 🎬 "Video" mode button** (explicit mode selection)
4. Sets aspect ratio if `--aspect` specified
5. Uploads reference images if provided (`-r`)
6. **Snapshots existing video URLs** (to skip stale results from previous runs)
7. Types prompt into the input
8. **Submits the generation** — uses multi-strategy approach:
   - First tries: `button[aria-label="Make video"]` on the reference image card (React onClick)
   - Fallback 1: `button[type="submit"]` or `button[aria-label*="send/submit/generate"]`
   - Fallback 2: Dark circular send button with SVG near input area
   - Fallback 3: Last button inside form/input/compose container
   - Last resort: Press Enter
9. Polls DOM for NEW `<video>` element (ignores pre-existing URLs)
10. Downloads video URL and saves as .mp4

## Authentication

Uses the same Chrome profile as `baoyu-post-to-x`. First run: log in to x.com manually. Session persists across runs.

Profile location: `~/.local/share/x-browser-profile/`

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GROK_CHROME_PATH` | Chrome executable path override |
| `GROK_PROFILE_DIR` | Chrome profile directory override |

## Troubleshooting

| Issue | Fix |
|-------|-----|
| **Video stuck after submit** | Fixed in v2 (2026-03-21) — multi-strategy submit fallback. If still stuck, check Chrome profile login. |
| **"Make video" button not found** | Normal — Grok UI changes frequently. Script auto-falls back to submit button. |
| **Low resolution video** | Expected — Grok outputs ~416x752 for 9:16. Upscale with ffmpeg if needed. |
| **Chrome won't launch** | Check `GROK_CHROME_PATH` or ensure Chrome is installed at default path. |
| **Session expired** | Open Chrome manually, log in to x.com, close. Session persists in profile. |

## Changelog

- **v4 (2026-03-21):** Silent failure detection:
  1. **Pre-existing image snapshot** — captures all image URLs before submit, only counts NEW ones. Prevents returning avatars/sidebar thumbnails when generation silently fails.
  2. **Error detection** — detects rate limits, captcha, "try again" messages from Grok and throws instead of returning garbage.
  3. **Avatar/sidebar filtering** — skips images inside avatar, profile, sidebar, history, nav, header containers.
  4. **File input verification** — after upload, verifies the filename in the input matches what was intended. Retries if mismatched.
  5. **Stale upload clearing** — removes previous upload thumbnails before new upload.
- **v3 (2026-03-21):** Three critical fixes:
  1. **`--imagine` flag** — image gen via `grok.com/imagine` (clicks 📷 Image mode, multi-strategy submit, reference dedup)
  2. **Explicit mode switching** — `--imagine` clicks Image, `--video` clicks Video. Prevents mode bleed between runs.
  3. **Stale video dedup** — snapshots existing video URLs before submit, ignores them when polling. Fixes bug where previous generation's video was returned instead of new one.
- **v2 (2026-03-21):** Fixed I2V submit flow — added 3-strategy fallback when "Make video" button isn't found. Previously required manual click; now fully autonomous.
- **v1:** Initial release — image gen via x.com/i/grok, video gen via grok.com/imagine.
