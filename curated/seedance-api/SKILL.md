---
version: 1.0.0
name: seedance-api
description: "Seedance 1.5 Pro video generation via Volcengine Ark API. Supports T2V (text-to-video) and I2V (image-to-video). Use when user says 'seedance api', 'seedance 1.5', 'volcengine video', 'ark video', or '/seedance-api'."
---

# Seedance 1.5 Pro Video Generation

Generate videos using Seedance 1.5 Pro via the Volcengine Ark API. Supports text-to-video (T2V) and image-to-video (I2V) modes.

## Prerequisites

1. Install the SDK:
   ```bash
   pip install 'volcengine-python-sdk[ark]'
   ```

2. Set the `ARK_API_KEY` environment variable with your Volcengine Ark API key.

## Script

```
~/.claude/skills/seedance-api/scripts/seedance_worker.py
```

## Parameters

| Parameter | Description | Default |
|---|---|---|
| `--prompt` | Text prompt describing the video (required) | — |
| `--ref-image` | Reference image for I2V — local path or URL. Omit for T2V. | — |
| `--duration` | Video duration in seconds: `5` or `10` | `5` |
| `--output-dir` | Directory to save the output MP4 | `~/Downloads` |
| `--camera-fixed` | Lock camera position (`true`/`false`) | `false` |
| `--watermark` | Include watermark (`true`/`false`) | `true` |
| `--model` | Model endpoint ID | `doubao-seedance-1-5-pro-251215` |

## Usage

### Text-to-Video (T2V)

```bash
python3 ~/.claude/skills/seedance-api/scripts/seedance_worker.py \
  --prompt "A cat walking through a field of flowers at sunset" \
  --duration 5
```

### Image-to-Video (I2V) with URL

```bash
python3 ~/.claude/skills/seedance-api/scripts/seedance_worker.py \
  --prompt "The person turns and smiles" \
  --ref-image "https://example.com/photo.png" \
  --duration 10
```

### Image-to-Video (I2V) with local file

```bash
python3 ~/.claude/skills/seedance-api/scripts/seedance_worker.py \
  --prompt "Gentle wind blowing through hair" \
  --ref-image ~/Pictures/portrait.jpg
```

## How to invoke from Claude Code

Run the script in the background so it does not block the conversation:

```bash
python3 ~/.claude/skills/seedance-api/scripts/seedance_worker.py \
  --prompt "..." [--ref-image ...] [--duration 5|10] &
```

## Notes

- Generation typically takes 1-4 minutes depending on duration and server load.
- The script polls every 5 seconds and prints status updates.
- On success the MP4 is downloaded to `--output-dir` and the final path + file size are printed.
- For I2V with a local image, the script converts it to a base64 data URL before sending.
