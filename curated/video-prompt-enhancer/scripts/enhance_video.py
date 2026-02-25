#!/usr/bin/env python3
"""Video Prompt Enhancer — thin realism layer for AI video generation.

Works with any AI video generator: Veo 3, Seedance, Grok, Kling, Runway, etc.
Adds real cinematography specs, camera movement, and anti-AI artifact
directives to ANY video prompt without overriding creative intent.

Usage:
    python3 enhance_video.py --prompt "a woman walking through a market"
    python3 enhance_video.py --prompt "a chef cooking ramen" --flat
    python3 enhance_video.py --prompt "horror scene in a forest" --style handheld
"""

import argparse
import json
import random
import sys

# ---------------------------------------------------------------------------
# Camera Presets — real gear from top Reddit Veo 3 posts
# ---------------------------------------------------------------------------

CAMERAS = {
    "cinematic": [
        {"body": "Arri Alexa LF", "lens": "50mm Cooke S7/i", "settings": "f/2.8, ISO 800, 24fps, HDR10"},
        {"body": "Arri Alexa Mini LF", "lens": "35mm Zeiss Supreme Prime", "settings": "f/2.0, ISO 800, 24fps"},
        {"body": "RED V-Raptor", "lens": "85mm Sigma Cine FF", "settings": "f/2.0, ISO 400, 24fps, 8K downscaled"},
        {"body": "Sony Venice 2", "lens": "40mm Zeiss Supreme Prime", "settings": "f/2.8, ISO 500, 24fps"},
    ],
    "documentary": [
        {"body": "Sony FX6", "lens": "24-70mm f/2.8 GM", "settings": "f/4, ISO 1600, 24fps"},
        {"body": "Canon C70", "lens": "35mm f/1.4L", "settings": "f/2.8, ISO 800, 24fps"},
        {"body": "Blackmagic Pocket 6K", "lens": "18-35mm Sigma Art", "settings": "f/2.8, ISO 1000, 24fps"},
    ],
    "handheld": [
        {"body": "Sony A7S III", "lens": "24mm f/1.4 GM", "settings": "f/2.0, ISO 3200, 24fps, handheld stabilization"},
        {"body": "Sony FX3", "lens": "35mm f/1.4 GM", "settings": "f/2.0, ISO 1600, 24fps, handheld"},
        {"body": "Canon R5 C", "lens": "28mm f/1.4L", "settings": "f/2.0, ISO 2000, 24fps, handheld"},
    ],
    "smartphone": [
        {"body": "iPhone 16 Pro", "lens": "24mm Fusion", "settings": "4K 24fps, ProRes, auto exposure"},
        {"body": "iPhone 15 Pro", "lens": "24mm wide", "settings": "4K 30fps, Cinematic mode, f/1.78"},
        {"body": "Samsung Galaxy S24 Ultra", "lens": "23mm wide", "settings": "4K 30fps, auto, f/1.7"},
    ],
    "vhs": [
        {"body": "Sony Handycam CCD-TRV", "lens": "built-in zoom", "settings": "480i, auto exposure, VHS-C"},
        {"body": "JVC GR-C1", "lens": "built-in", "settings": "VHS, auto, analog video"},
    ],
}

# ---------------------------------------------------------------------------
# Camera movement presets — what Veo 3 actually responds to well
# ---------------------------------------------------------------------------

CAMERA_MOVEMENTS = {
    "static": [
        "Static locked-off tripod shot.",
        "Fixed camera position on tripod, no movement.",
        "Steady tripod shot, camera does not move.",
    ],
    "push": [
        "Slow dolly push in toward the subject.",
        "Gentle push in, narrowing on the subject.",
        "Slow steady push-in on a dolly.",
    ],
    "pull": [
        "Slow dolly pull-out revealing the scene.",
        "Gentle pull back, widening to reveal the environment.",
    ],
    "orbit": [
        "Slow orbit around the subject.",
        "Camera slowly orbits the subject, 45-degree arc.",
    ],
    "tracking": [
        "Smooth tracking shot following the subject's movement.",
        "Lateral tracking shot, keeping pace with the subject.",
    ],
    "handheld": [
        "Handheld follow, slight natural shake.",
        "Handheld camera with natural micro-movements and breathing.",
        "Shaky handheld footage, unstable, organic movement.",
    ],
}

# ---------------------------------------------------------------------------
# Anti-AI directives — fight video-specific artifacts
# ---------------------------------------------------------------------------

ANTI_AI_STANDARD = [
    "No subtitles, captions, or text overlays.",
    "No watermarks or logos.",
    "No AI smoothing or plastic skin texture.",
]

ANTI_AI_HIGH = ANTI_AI_STANDARD + [
    "No artificial bokeh or simulated depth of field.",
    "No post-processing filters or HDR artifacts.",
    "No fade transitions at start or end.",
    "No background music unless specified.",
    "All textures must be photographically real.",
]

ANTI_AI_ULTRA = ANTI_AI_HIGH + [
    "The final result must be indistinguishable from real footage.",
    "Mild sensor noise consistent with the camera and ISO setting.",
    "No beauty filter applied to any subject.",
    "No CGI or compositing artifacts.",
    "Natural motion blur consistent with 24fps shutter angle.",
]

# ---------------------------------------------------------------------------
# Auto-detection heuristics
# ---------------------------------------------------------------------------

SMARTPHONE_KEYWORDS = ["selfie", "vlog", "phone camera", "front camera", "instagram", "tiktok", "pov selfie"]
VHS_KEYWORDS = ["vhs", "found footage", "camcorder", "home video", "tape", "retro video"]
HANDHELD_KEYWORDS = ["handheld", "shaky", "run", "chase", "follow", "documentary"]
DOCUMENTARY_KEYWORDS = ["documentary", "interview", "news", "behind the scenes", "bts"]

STATIC_KEYWORDS = ["sits", "standing", "static", "locked", "tripod", "fixed"]
PUSH_KEYWORDS = ["push in", "dolly in", "close in", "zoom in"]
PULL_KEYWORDS = ["pull out", "dolly out", "reveal", "pull back", "zoom out"]
ORBIT_KEYWORDS = ["orbit", "circle around", "rotate around", "360"]
TRACKING_KEYWORDS = ["tracking", "follow", "walking", "running", "moving through"]
HANDHELD_MOVE_KEYWORDS = ["handheld", "shaky", "vhs", "found footage", "pov"]


def pick_camera_style(prompt: str, override: str | None) -> str:
    if override:
        return override
    prompt_lower = prompt.lower()
    if any(kw in prompt_lower for kw in SMARTPHONE_KEYWORDS):
        return "smartphone"
    if any(kw in prompt_lower for kw in VHS_KEYWORDS):
        return "vhs"
    if any(kw in prompt_lower for kw in HANDHELD_KEYWORDS):
        return "handheld"
    if any(kw in prompt_lower for kw in DOCUMENTARY_KEYWORDS):
        return "documentary"
    return "cinematic"


def pick_camera(camera_style: str) -> dict:
    options = CAMERAS.get(camera_style, CAMERAS["cinematic"])
    return random.choice(options)


def pick_movement(prompt: str, override: str | None) -> str:
    if override:
        options = CAMERA_MOVEMENTS.get(override, CAMERA_MOVEMENTS["static"])
        return random.choice(options)
    prompt_lower = prompt.lower()
    if any(kw in prompt_lower for kw in PUSH_KEYWORDS):
        return random.choice(CAMERA_MOVEMENTS["push"])
    if any(kw in prompt_lower for kw in PULL_KEYWORDS):
        return random.choice(CAMERA_MOVEMENTS["pull"])
    if any(kw in prompt_lower for kw in ORBIT_KEYWORDS):
        return random.choice(CAMERA_MOVEMENTS["orbit"])
    if any(kw in prompt_lower for kw in TRACKING_KEYWORDS):
        return random.choice(CAMERA_MOVEMENTS["tracking"])
    if any(kw in prompt_lower for kw in HANDHELD_MOVE_KEYWORDS):
        return random.choice(CAMERA_MOVEMENTS["handheld"])
    if any(kw in prompt_lower for kw in STATIC_KEYWORDS):
        return random.choice(CAMERA_MOVEMENTS["static"])
    # Default: gentle push-in (most cinematic, least distracting)
    return random.choice(CAMERA_MOVEMENTS["push"])


def get_anti_ai(realism: str) -> list:
    if realism == "ultra":
        return list(ANTI_AI_ULTRA)
    elif realism == "high":
        return list(ANTI_AI_HIGH)
    return list(ANTI_AI_STANDARD)


def build_enhanced_prompt(
    prompt: str,
    camera_style: str,
    movement_override: str | None,
    realism: str,
    extra_negatives: list | None = None,
) -> dict:
    """Wrap the user's video prompt with cinematography specs + anti-AI directives.

    Does NOT override lighting, environment, aesthetic, audio content,
    dialogue, or creative intent. The user's prompt is the source of truth.
    """

    camera = pick_camera(camera_style)
    movement = pick_movement(prompt, movement_override)
    anti_ai = get_anti_ai(realism)
    if extra_negatives:
        anti_ai = anti_ai + extra_negatives

    parts = [
        f"Shot on {camera['body']} with {camera['lens']} at {camera['settings']}.",
        f"{movement}",
        f"{prompt}.",
        f"This must look like real footage, not an AI render.",
        " ".join(anti_ai),
    ]

    enhanced_text = " ".join(parts)

    result = {
        "enhanced_prompt": enhanced_text,
        "meta": {
            "original_prompt": prompt,
            "camera": camera,
            "camera_movement": movement,
            "realism_level": realism,
            "anti_ai_directives": anti_ai,
        },
    }

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Add realism layer to any video prompt (Veo 3, Seedance, Grok, Kling, Runway, etc)"
    )
    parser.add_argument("--prompt", "-p", required=True, help="Your video prompt (any style, any intent)")
    parser.add_argument(
        "--style", "-s",
        choices=["cinematic", "documentary", "handheld", "smartphone", "vhs"],
        default=None,
        help="Camera style (auto-detected from prompt if not specified)",
    )
    parser.add_argument(
        "--movement", "-m",
        choices=["static", "push", "pull", "orbit", "tracking", "handheld"],
        default=None,
        help="Camera movement (auto-detected from prompt if not specified)",
    )
    parser.add_argument("--output", "-o", default=None, help="Save enhanced prompt as JSON file")
    parser.add_argument("--flat", action="store_true", help="Output flat text string only")
    parser.add_argument(
        "--realism", "-r",
        choices=["standard", "high", "ultra"],
        default="high",
        help="Realism level (how many anti-AI directives to add)",
    )
    parser.add_argument("--negative", "-n", nargs="*", help="Extra negative directives to append")

    args = parser.parse_args()

    camera_style = pick_camera_style(args.prompt, args.style)

    result = build_enhanced_prompt(
        prompt=args.prompt,
        camera_style=camera_style,
        movement_override=args.movement,
        realism=args.realism,
        extra_negatives=args.negative,
    )

    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2)
        print(f"OK: saved to {args.output}", file=sys.stderr)

    if args.flat:
        print(result["enhanced_prompt"])
    elif not args.output:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
