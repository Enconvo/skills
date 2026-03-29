#!/usr/bin/env python3
"""Seedance 1.5 Pro video generation via Volcengine Ark API.

Supports text-to-video (T2V) and image-to-video (I2V) modes.
"""

import argparse
import base64
import mimetypes
import os
import re
import sys
import time
import urllib.request
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate video with Seedance 1.5 Pro (Volcengine Ark API)"
    )
    parser.add_argument(
        "--prompt", required=True, help="Text prompt describing the video"
    )
    parser.add_argument(
        "--ref-image",
        default=None,
        help="Reference image for I2V: local file path or URL. Omit for T2V.",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=5,
        choices=[5, 10],
        help="Video duration in seconds (default: 5)",
    )
    parser.add_argument(
        "--output-dir",
        default=os.path.expanduser("~/Downloads"),
        help="Directory to save the output MP4 (default: ~/Downloads)",
    )
    parser.add_argument(
        "--camera-fixed",
        default="false",
        choices=["true", "false"],
        help="Lock camera position (default: false)",
    )
    parser.add_argument(
        "--watermark",
        default="true",
        choices=["true", "false"],
        help="Include watermark (default: true)",
    )
    parser.add_argument(
        "--model",
        default="doubao-seedance-1-5-pro-251215",
        help="Model endpoint ID (default: doubao-seedance-1-5-pro-251215)",
    )
    return parser.parse_args()


def local_image_to_data_url(path: str) -> str:
    """Convert a local image file to a base64 data URL."""
    resolved = Path(path).expanduser().resolve()
    if not resolved.is_file():
        print(f"Error: image file not found: {resolved}", file=sys.stderr)
        sys.exit(1)

    mime_type, _ = mimetypes.guess_type(str(resolved))
    if mime_type is None:
        # Fall back based on suffix
        suffix = resolved.suffix.lower()
        mime_map = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp",
            ".gif": "image/gif",
            ".bmp": "image/bmp",
        }
        mime_type = mime_map.get(suffix, "image/png")

    data = resolved.read_bytes()
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:{mime_type};base64,{b64}"


def is_url(s: str) -> bool:
    return s.startswith("http://") or s.startswith("https://") or s.startswith("data:")


def sanitize_filename(text: str, max_len: int = 20) -> str:
    """Create a filesystem-safe prefix from prompt text."""
    cleaned = re.sub(r"[^\w\s-]", "", text).strip()
    cleaned = re.sub(r"[\s_]+", "_", cleaned)
    return cleaned[:max_len]


def download_video(url: str, dest: Path) -> None:
    """Download a video file from a URL."""
    print(f"Downloading video to {dest} ...")
    try:
        urllib.request.urlretrieve(url, str(dest))
    except Exception as e:
        print(f"urllib download failed ({e}), trying requests ...", file=sys.stderr)
        try:
            import requests

            resp = requests.get(url, stream=True, timeout=120)
            resp.raise_for_status()
            with open(dest, "wb") as f:
                for chunk in resp.iter_content(chunk_size=1024 * 1024):
                    f.write(chunk)
        except Exception as e2:
            print(f"Error: failed to download video: {e2}", file=sys.stderr)
            sys.exit(1)


def main():
    args = parse_args()

    # Load .env file if present (co-located with script or skill root)
    script_dir = Path(__file__).resolve().parent
    for env_path in [script_dir / ".env", script_dir.parent / ".env"]:
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        os.environ.setdefault(k.strip(), v.strip())

    # Check API key
    api_key = os.environ.get("ARK_API_KEY")
    if not api_key:
        print(
            "Error: ARK_API_KEY not found.\n"
            "Either set the env var or edit ~/.claude/skills/seedance-api/.env",
            file=sys.stderr,
        )
        sys.exit(1)

    # Import SDK (fail early with helpful message)
    try:
        from volcenginesdkarkruntime import Ark
    except ImportError:
        print(
            "Error: volcengine-python-sdk[ark] is not installed.\n"
            "Install it with:\n"
            "  pip install 'volcengine-python-sdk[ark]'",
            file=sys.stderr,
        )
        sys.exit(1)

    # Build prompt text with parameters
    prompt_text = (
        f"{args.prompt} "
        f"--duration {args.duration} "
        f"--camerafixed {args.camera_fixed} "
        f"--watermark {args.watermark}"
    )

    # Build content list
    content = [{"type": "text", "text": prompt_text}]

    # Handle reference image (I2V mode)
    if args.ref_image:
        if is_url(args.ref_image):
            image_url = args.ref_image
        else:
            image_url = local_image_to_data_url(args.ref_image)
        content.append({"type": "image_url", "image_url": {"url": image_url}})
        mode = "I2V"
    else:
        mode = "T2V"

    print(f"Mode: {mode}")
    print(f"Model: {args.model}")
    print(f"Prompt: {args.prompt}")
    print(f"Duration: {args.duration}s | Camera fixed: {args.camera_fixed} | Watermark: {args.watermark}")

    # Create task
    client = Ark(
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        api_key=api_key,
    )

    try:
        create_result = client.content_generation.tasks.create(
            model=args.model,
            content=content,
        )
    except Exception as e:
        print(f"Error creating task: {e}", file=sys.stderr)
        sys.exit(1)

    task_id = create_result.id
    print(f"Task created: {task_id}")
    print("Polling for completion ...")

    # Poll for result
    start_time = time.time()
    last_status = None
    while True:
        try:
            result = client.content_generation.tasks.get(task_id=task_id)
        except Exception as e:
            print(f"Warning: poll error ({e}), retrying ...", file=sys.stderr)
            time.sleep(5)
            continue

        status = result.status
        elapsed = int(time.time() - start_time)

        if status != last_status:
            print(f"  [{elapsed}s] Status: {status}")
            last_status = status

        if status == "succeeded":
            break
        elif status == "failed":
            error_msg = getattr(result, "error", "unknown error")
            print(f"Error: task failed — {error_msg}", file=sys.stderr)
            sys.exit(1)
        else:
            time.sleep(5)

    elapsed = int(time.time() - start_time)
    print(f"Generation completed in {elapsed}s.")

    # Extract video URL from result
    video_url = None
    if hasattr(result, "content") and result.content:
        for item in result.content:
            # Handle both dict and object forms
            if isinstance(item, dict):
                if item.get("type") == "video_url":
                    video_url = item.get("video_url", {}).get("url")
                elif item.get("type") == "url":
                    video_url = item.get("url")
            else:
                item_type = getattr(item, "type", None)
                if item_type == "video_url":
                    vu = getattr(item, "video_url", None)
                    if vu:
                        video_url = getattr(vu, "url", None) or (vu.get("url") if isinstance(vu, dict) else None)
                elif item_type == "url":
                    video_url = getattr(item, "url", None)

    if not video_url:
        # Try to find any URL-like string in the result
        result_str = str(result)
        url_match = re.search(r'https?://[^\s\'"]+\.mp4[^\s\'"]*', result_str)
        if url_match:
            video_url = url_match.group(0)
        else:
            print("Warning: could not extract video URL from result.", file=sys.stderr)
            print(f"Raw result:\n{result}", file=sys.stderr)
            sys.exit(1)

    # Prepare output directory and filename
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    prefix = sanitize_filename(args.prompt)
    filename = f"{prefix}_seedance.mp4"
    dest = output_dir / filename

    # Avoid overwriting
    if dest.exists():
        ts = int(time.time())
        filename = f"{prefix}_{ts}_seedance.mp4"
        dest = output_dir / filename

    download_video(video_url, dest)

    size_bytes = dest.stat().st_size
    if size_bytes >= 1024 * 1024:
        size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        size_str = f"{size_bytes / 1024:.1f} KB"

    print(f"Saved: {dest}")
    print(f"Size: {size_str}")


if __name__ == "__main__":
    main()
