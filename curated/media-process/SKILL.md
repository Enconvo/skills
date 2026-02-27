---
name: media-process
version: 1.0.0
category: media
description: "Media processing toolkit: image editing/compression, video compression/extraction/downloading, audio compression/transcription. Activates on: image resize, image compress, video compress, extract audio, download video, compress audio, transcribe audio/video, screenshot, or any media processing request."
---

# Media Process Skill

All-in-one media processing skill covering image, video, and audio operations. Uses macOS native tools for simple tasks and HTTP APIs for advanced processing.

## API Base URL

All HTTP API calls use base URL: `http://localhost:54535`

All API calls are **POST** requests with `Content-Type: application/json`.

---

## 1. Image Processing

### Simple Operations (macOS sips)

For basic image manipulation (resize, rotate, flip, format conversion, etc.), use the macOS built-in `sips` command directly:

```bash
# Resize image
sips -z <height> <width> <input_file>

# Resize to fit within max dimension (preserving aspect ratio)
sips --resampleWidth <width> <input_file>
sips --resampleHeight <height> <input_file>

# Convert format
sips -s format <png|jpeg|tiff|gif|bmp> <input_file> --out <output_file>

# Rotate
sips -r <degrees> <input_file>

# Flip
sips -f horizontal <input_file>
sips -f vertical <input_file>

# Get image properties
sips -g all <input_file>
```

### Screenshot

Use the `screencapture` command to capture screenshots:

```bash
# Capture full screen
screencapture <output_file>

# Capture interactive selection
screencapture -i <output_file>

# Capture specific window
screencapture -w <output_file>
```

After capturing, use the **Read** tool (file read) to view the image content.

### Image Compression

**Endpoint:** `POST http://localhost:54535/command/call/compress_image/image_compress`

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `image_files` | `string[]` | Yes | Array of image file paths to compress |
| `context_files` | `string[]` | No | Context files |
| `destinationFolderPath` | `string` | No | Destination folder path (default: `~/Downloads`) |
| `overwrite` | `boolean` | No | Whether to overwrite the original file (default: `false`) |
| `quality` | `number` | No | Quality 0-100, higher is better (default: `80`) |

**Example:**

```bash
curl -X POST http://localhost:54535/command/call/compress_image/image_compress \
  -H "Content-Type: application/json" \
  -d '{
    "image_files": ["/path/to/image.png"],
    "quality": 80,
    "destinationFolderPath": "~/Downloads",
    "overwrite": false
  }'
```

---

## 2. Video Processing

### Video Compress

**Endpoint:** `POST http://localhost:54535/command/call/video_utils/compress_video`

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `video_files` | `string[]` | Yes | Array of video file paths to compress |
| `context_files` | `string[]` | No | Context files |
| `destinationFolderPath` | `string` | No | Destination folder path (default: `~/Downloads`) |
| `overwrite` | `boolean` | No | Whether to overwrite the original video file (default: `false`) |
| `quality` | `number` | No | Quality 0-100, higher is better (default: `80`) |

**Example:**

```bash
curl -X POST http://localhost:54535/command/call/video_utils/compress_video \
  -H "Content-Type: application/json" \
  -d '{
    "video_files": ["/path/to/video.mp4"],
    "quality": 80,
    "destinationFolderPath": "~/Downloads",
    "overwrite": false
  }'
```

### Extract Audio from Video

**Endpoint:** `POST http://localhost:54535/command/call/video_utils/extract_audio`

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `video_files` | `string[]` | Yes | Array of video file paths to extract audio from |
| `context_files` | `string[]` | No | Context files |
| `destinationFolderPath` | `string` | No | Destination folder path (default: `~/Downloads`) |

**Example:**

```bash
curl -X POST http://localhost:54535/command/call/video_utils/extract_audio \
  -H "Content-Type: application/json" \
  -d '{
    "video_files": ["/path/to/video.mp4"],
    "destinationFolderPath": "~/Downloads"
  }'
```

### Online Video/Audio Downloader

Download videos or audio from YouTube, TikTok, Instagram, Reddit, Twitter, Vimeo, etc.

**Endpoint:** `POST http://localhost:54535/command/call/video_utils/online_video_or_audio_downloader`

This command delegates to `youtube|youtube_video_downloader` internally. Pass the URL as needed.

### Fallback: yt-dlp / ffmpeg

For operations not covered by the above APIs, use `yt-dlp` or `ffmpeg` directly:

```bash
# Download video with yt-dlp
yt-dlp <url>

# Download audio only
yt-dlp -x --audio-format mp3 <url>

# Convert video format with ffmpeg
ffmpeg -i input.mp4 output.avi

# Trim video
ffmpeg -i input.mp4 -ss 00:00:10 -to 00:00:30 -c copy output.mp4

# Extract frames
ffmpeg -i input.mp4 -vf "fps=1" frame_%04d.png

# Merge audio and video
ffmpeg -i video.mp4 -i audio.mp3 -c:v copy -c:a aac output.mp4
```

---

## 3. Audio Processing

### Audio Compress

**Endpoint:** `POST http://localhost:54535/command/call/audio_utils/compress_audio`

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `audio_files` | `string[]` | Yes | Array of audio file paths to compress |
| `context_files` | `string[]` | No | Context files |
| `destinationFolderPath` | `string` | No | Destination folder path (default: `~/Downloads`) |
| `overwrite` | `boolean` | No | Whether to overwrite the original audio file (default: `false`) |
| `quality` | `number` | No | Quality 0-100, higher is better (default: `80`) |

**Example:**

```bash
curl -X POST http://localhost:54535/command/call/audio_utils/compress_audio \
  -H "Content-Type: application/json" \
  -d '{
    "audio_files": ["/path/to/audio.mp3"],
    "quality": 80,
    "destinationFolderPath": "~/Downloads",
    "overwrite": false
  }'
```

### Fallback: ffmpeg

For other audio operations, use `ffmpeg`:

```bash
# Convert audio format
ffmpeg -i input.wav output.mp3

# Trim audio
ffmpeg -i input.mp3 -ss 00:00:10 -to 00:00:30 -c copy output.mp3

# Adjust volume
ffmpeg -i input.mp3 -filter:a "volume=1.5" output.mp3

# Merge audio files
ffmpeg -i "concat:file1.mp3|file2.mp3" -c copy output.mp3

# Change bitrate
ffmpeg -i input.mp3 -b:a 128k output.mp3
```

---

## 4. Audio/Video Transcription

Transcribe audio or video files to text.

**Endpoint:** `POST http://localhost:54535/command/call/transcribe/transcribe_audio_video`

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `audio_files` | `string[]` | Yes | Array of audio/video file paths to transcribe |
| `context_files` | `string[]` | No | Context files |
| `output_format` | `object` | No | Output format: `{"value": "plain_text"}` or `{"value": "file"}` (default: `plain_text`) |
| `output_dir` | `string` | No | Output directory (used when `output_format` is `file`) |

**Output format options:**
- `plain_text` — Returns transcription text directly
- `file` — Saves transcription to a TXT file in `output_dir`

**Example:**

```bash
# Transcribe to plain text
curl -X POST http://localhost:54535/command/call/transcribe/transcribe_audio_video \
  -H "Content-Type: application/json" \
  -d '{
    "audio_files": ["/path/to/audio.mp3"],
    "output_format": {"value": "plain_text"}
  }'

# Transcribe to file
curl -X POST http://localhost:54535/command/call/transcribe/transcribe_audio_video \
  -H "Content-Type: application/json" \
  -d '{
    "audio_files": ["/path/to/video.mp4"],
    "output_format": {"value": "file"},
    "output_dir": "~/Downloads"
  }'
```

---

## Decision Matrix

| Task | Tool |
|------|------|
| Image resize / rotate / flip / convert | `sips` (macOS native) |
| Screenshot capture | `screencapture` (macOS native) |
| View image content | **Read** tool (file read) |
| Image compression | API: `compress_image/image_compress` |
| Video compression | API: `video_utils/compress_video` |
| Extract audio from video | API: `video_utils/extract_audio` |
| Download online video/audio | API: `video_utils/online_video_or_audio_downloader` |
| Audio compression | API: `audio_utils/compress_audio` |
| Transcribe audio/video | API: `transcribe/transcribe_audio_video` |
| Other video operations | `ffmpeg` or `yt-dlp` |
| Other audio operations | `ffmpeg` |
