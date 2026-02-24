#!/usr/bin/env python3
"""Nano Banana image generation via Google Gemini API.

Supports native aspect ratio and resolution control.
Default: Nano Banana Pro (gemini-3-pro-image-preview), 16:9, 2K.
"""

import argparse
import base64
import json
import os
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Auto-load .env from skill directory
# ---------------------------------------------------------------------------
_env_path = Path(__file__).resolve().parent.parent / ".env"
if _env_path.exists():
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                _k, _v = _k.strip(), _v.strip()
                if _v and _v != "YOUR_KEY_HERE" and _k not in os.environ:
                    os.environ[_k] = _v

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MODELS = {
    "pro": "gemini-3-pro-image-preview",
    "flash": "gemini-2.5-flash-image",
}

ASPECT_RATIOS = [
    "1:1", "2:3", "3:2", "3:4", "4:3",
    "4:5", "5:4", "9:16", "16:9", "21:9",
]

IMAGE_SIZES = ["1K", "2K", "4K"]

# Expected AR float values for verification
AR_FLOATS = {
    "1:1": 1.0, "2:3": 0.667, "3:2": 1.5, "3:4": 0.75, "4:3": 1.333,
    "4:5": 0.8, "5:4": 1.25, "9:16": 0.5625, "16:9": 1.778, "21:9": 2.333,
}

# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

def get_api_key(cli_key: str | None) -> str | None:
    """Try to get API key from CLI flag, env var, or None."""
    if cli_key:
        return cli_key
    return os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")


def get_oauth_access_token() -> str | None:
    """Try to get OAuth access token from Gemini CLI credentials."""
    creds_path = Path.home() / ".gemini" / "oauth_creds.json"
    if not creds_path.exists():
        return None
    try:
        with open(creds_path) as f:
            creds = json.load(f)
        expiry = creds.get("expiry_date", 0)
        # Token expired — try to refresh
        if expiry and time.time() * 1000 > expiry - 60000:
            refreshed = refresh_oauth_token(creds)
            if refreshed:
                return refreshed
            return None
        return creds.get("access_token")
    except Exception:
        return None


def refresh_oauth_token(creds: dict) -> str | None:
    """Refresh OAuth token using refresh_token."""
    import urllib.request
    import urllib.parse

    refresh_token = creds.get("refresh_token")
    if not refresh_token:
        return None

    # Gemini CLI OAuth credentials (public, embedded in @google/gemini-cli source)
    client_id = os.environ.get("GEMINI_CLIENT_ID", "REDACTED")
    client_secret = os.environ.get("GEMINI_CLIENT_SECRET", "REDACTED")

    data = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
    }).encode()

    req = urllib.request.Request(
        "https://oauth2.googleapis.com/token",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())
        new_token = result.get("access_token")
        if new_token:
            # Update cached creds
            creds["access_token"] = new_token
            if "expires_in" in result:
                creds["expiry_date"] = int(time.time() * 1000) + result["expires_in"] * 1000
            creds_path = Path.home() / ".gemini" / "oauth_creds.json"
            with open(creds_path, "w") as f:
                json.dump(creds, f, indent=2)
            return new_token
    except Exception as e:
        print(f"WARNING: OAuth refresh failed: {e}", file=sys.stderr)
    return None


# ---------------------------------------------------------------------------
# Image generation
# ---------------------------------------------------------------------------

def generate_image(
    prompt: str,
    model_id: str,
    aspect_ratio: str,
    image_size: str,
    output_path: str,
    reference_paths: list[str] | None = None,
    api_key: str | None = None,
    oauth_token: str | None = None,
) -> dict:
    """Generate image via Gemini REST API."""
    import urllib.request

    # Build request
    parts = []

    # Add reference images if provided
    if reference_paths:
        for ref_path in reference_paths:
            with open(ref_path, "rb") as f:
                img_data = base64.b64encode(f.read()).decode()
            ext = Path(ref_path).suffix.lower()
            mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
                    "webp": "image/webp", "gif": "image/gif"}.get(ext.lstrip("."), "image/png")
            parts.append({"inline_data": {"mime_type": mime, "data": img_data}})

    parts.append({"text": prompt})

    body = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "imageConfig": {
                "aspectRatio": aspect_ratio,
                "imageSize": image_size,
            },
        },
    }

    payload = json.dumps(body).encode()

    # Build URL and headers
    if api_key:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
    elif oauth_token:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {oauth_token}",
        }
    else:
        return {"status": "error", "message": "No authentication available"}

    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.readable() else str(e)
        return {"status": "error", "message": f"API error {e.code}: {error_body}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

    # Extract image from response
    candidates = result.get("candidates", [])
    if not candidates:
        return {"status": "error", "message": "No candidates in response", "raw": result}

    parts = candidates[0].get("content", {}).get("parts", [])
    image_data = None
    text_response = ""

    for part in parts:
        if "inlineData" in part:
            image_data = part["inlineData"].get("data")
        elif "text" in part:
            text_response = part["text"]

    if not image_data:
        return {"status": "error", "message": f"No image in response. Text: {text_response}", "raw": result}

    # Save image
    img_bytes = base64.b64decode(image_data)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "wb") as f:
        f.write(img_bytes)

    # Verify dimensions
    try:
        from PIL import Image as PILImage
        img = PILImage.open(output)
        w, h = img.size
        img.close()
        actual_ar = round(w / h, 3)
    except ImportError:
        w, h, actual_ar = 0, 0, 0.0

    expected_ar = AR_FLOATS.get(aspect_ratio, 1.0)
    ar_deviation = abs(actual_ar - expected_ar) / expected_ar if expected_ar and actual_ar else 0

    return {
        "status": "ok",
        "path": str(output),
        "width": w,
        "height": h,
        "ar": actual_ar,
        "expected_ar": round(expected_ar, 3),
        "ar_deviation": round(ar_deviation, 3),
        "model": model_id,
        "aspect_ratio": aspect_ratio,
        "image_size": image_size,
        "text": text_response,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Nano Banana image generation")
    parser.add_argument("--prompt", "-p", help="Image generation prompt")
    parser.add_argument("--output", "-o", default="generated.png", help="Output file path (default: generated.png)")
    parser.add_argument("--ar", default="16:9", choices=ASPECT_RATIOS, help="Aspect ratio (default: 16:9)")
    parser.add_argument("--size", default="2K", choices=IMAGE_SIZES, help="Resolution: 1K, 2K, 4K (default: 2K)")
    parser.add_argument("--model", "-m", default="pro", choices=["pro", "flash"], help="Model: pro (default) or flash")
    parser.add_argument("--reference", "--ref", nargs="+", help="Reference image path(s)")
    parser.add_argument("--api-key", help="Gemini API key (overrides env var)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--list-ar", action="store_true", help="List available aspect ratios and exit")
    parser.add_argument("--list-sizes", action="store_true", help="List available resolutions and exit")

    args = parser.parse_args()

    # List commands (no prompt needed)
    if args.list_ar:
        print("Available aspect ratios:")
        for ar in ASPECT_RATIOS:
            expected = AR_FLOATS.get(ar, 0)
            print(f"  {ar:>5}  (float: {expected:.3f})")
        return

    if args.list_sizes:
        print("Available resolutions:")
        print("  1K  — ~1024px long edge  (fast, drafts)")
        print("  2K  — ~2048px long edge  (default, PPTX/web)")
        print("  4K  — ~4096px long edge  (print, high-DPI)")
        return

    if not args.prompt:
        parser.error("--prompt/-p is required for image generation")

    # Auth
    api_key = get_api_key(args.api_key)
    oauth_token = None
    if not api_key:
        oauth_token = get_oauth_access_token()

    if not api_key and not oauth_token:
        print("ERROR: No authentication found.", file=sys.stderr)
        print("Set GEMINI_API_KEY env var, pass --api-key, or install Gemini CLI (npm i -g @google/gemini-cli) and authenticate.", file=sys.stderr)
        sys.exit(1)

    model_id = MODELS[args.model]

    # Generate
    t0 = time.time()
    result = generate_image(
        prompt=args.prompt,
        model_id=model_id,
        aspect_ratio=args.ar,
        image_size=args.size,
        output_path=args.output,
        reference_paths=args.reference,
        api_key=api_key,
        oauth_token=oauth_token,
    )
    elapsed = round(time.time() - t0, 1)
    result["elapsed_seconds"] = elapsed

    if args.json:
        print(json.dumps(result, indent=2))
    elif result["status"] == "ok":
        print(f"OK: saved to {result['path']} ({result['width']}x{result['height']}, AR={result['ar']}, model={result['model']}, {elapsed}s)")
        if result.get("ar_deviation", 0) > 0.05:
            print(f"WARNING: AR mismatch — requested {args.ar} ({result['expected_ar']}), got {result['ar']}. Deviation: {result['ar_deviation']:.0%}")
    else:
        print(f"ERROR: {result.get('message', 'Unknown error')}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
