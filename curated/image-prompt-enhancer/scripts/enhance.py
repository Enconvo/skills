#!/usr/bin/env python3
"""Image Prompt Enhancer — thin realism layer for AI image generation.

Adds real camera specs + anti-AI artifact directives to ANY prompt
without overriding the user's creative intent.

Usage:
    python3 enhance.py --prompt "a woman in a coffee shop"
    python3 enhance.py --prompt "a homeless man sleeping under a bridge" --flat
    python3 enhance.py --prompt "glamorous office lady in a studio" --flat
"""

import argparse
import json
import random
import sys

# ---------------------------------------------------------------------------
# Camera Presets — real gear from top Reddit posts
# ---------------------------------------------------------------------------

CAMERAS = {
    "mirrorless": [
        {"body": "Sony A7R V", "lens": "35mm f/1.4 GM", "settings": "f/2.8, ISO 200, 1/250s"},
        {"body": "Sony A7R V", "lens": "50mm f/1.4 GM", "settings": "f/2.0, ISO 160, 1/200s"},
        {"body": "Fujifilm X-T5", "lens": "23mm f/1.4 R", "settings": "f/2.8, ISO 400, 1/125s"},
        {"body": "Fujifilm X-T5", "lens": "56mm f/1.2 R", "settings": "f/1.8, ISO 200, 1/200s"},
    ],
    "dslr": [
        {"body": "Canon EOS R5", "lens": "85mm f/1.4L IS USM", "settings": "f/2.0, ISO 100, 1/200s"},
        {"body": "Canon EOS R5", "lens": "50mm f/1.2L RF", "settings": "f/1.8, ISO 200, 1/160s"},
        {"body": "Nikon Z9", "lens": "50mm f/1.2 S", "settings": "f/1.8, ISO 200, 1/200s"},
        {"body": "Nikon Z8", "lens": "85mm f/1.2 S", "settings": "f/2.0, ISO 100, 1/250s"},
    ],
    "smartphone": [
        {"body": "iPhone 15 Pro", "lens": "24mm wide", "settings": "auto exposure, f/1.78"},
        {"body": "iPhone 16 Pro", "lens": "24mm Fusion", "settings": "auto exposure, ProRAW"},
        {"body": "Samsung Galaxy S24 Ultra", "lens": "23mm wide", "settings": "auto, f/1.7"},
    ],
    "film": [
        {"body": "Leica M6", "lens": "35mm Summicron f/2", "settings": "f/4, Portra 400"},
        {"body": "Contax T2", "lens": "38mm Sonnar f/2.8", "settings": "f/5.6, Kodak Gold 200"},
    ],
}

# ---------------------------------------------------------------------------
# Anti-AI directives — these fight artifacts, not style
# ---------------------------------------------------------------------------

ANTI_AI_STANDARD = [
    "No AI smoothing or plastic skin texture.",
    "No simulated depth of field with unrealistic bokeh.",
    "No post-processing filters.",
]

ANTI_AI_HIGH = ANTI_AI_STANDARD + [
    "Without 'AI gloss' or waxy rendering on any surface.",
    "No HDR artifacts or tone mapping.",
    "No sharpening halos at contrast edges.",
    "All textures must be photographically real — skin, fabric, metal, wood, concrete.",
]

ANTI_AI_ULTRA = ANTI_AI_HIGH + [
    "The final result must be indistinguishable from a real photograph.",
    "Mild digital noise consistent with the camera sensor and ISO setting.",
    "No beauty filter applied to any subject.",
]

# ---------------------------------------------------------------------------
# Camera auto-selection heuristics
# ---------------------------------------------------------------------------

SMARTPHONE_KEYWORDS = ["selfie", "mirror selfie", "phone camera", "front camera", "instagram"]
FILM_KEYWORDS = ["film look", "analog", "vintage", "35mm film", "grain", "retro"]


def pick_camera_type(prompt: str, override: str | None) -> str:
    if override:
        return override
    prompt_lower = prompt.lower()
    if any(kw in prompt_lower for kw in SMARTPHONE_KEYWORDS):
        return "smartphone"
    if any(kw in prompt_lower for kw in FILM_KEYWORDS):
        return "film"
    # Default: mirrorless (versatile, modern, realistic)
    return "mirrorless"


def pick_camera(camera_type: str) -> dict:
    options = CAMERAS.get(camera_type, CAMERAS["mirrorless"])
    return random.choice(options)


def get_anti_ai(realism: str) -> list:
    if realism == "ultra":
        return list(ANTI_AI_ULTRA)
    elif realism == "high":
        return list(ANTI_AI_HIGH)
    return list(ANTI_AI_STANDARD)


def build_enhanced_prompt(
    prompt: str,
    camera_type: str,
    realism: str,
    extra_negatives: list | None = None,
) -> dict:
    """Wrap the user's prompt with camera specs + anti-AI directives.

    Does NOT override lighting, environment, aesthetic, or creative intent.
    The user's prompt is the source of truth for all creative decisions.
    """

    camera = pick_camera(camera_type)
    anti_ai = get_anti_ai(realism)
    if extra_negatives:
        anti_ai = anti_ai + extra_negatives

    # Build enhanced prompt — camera bracket + user prompt + anti-AI bracket
    parts = [
        f"Captured with a {camera['body']} and {camera['lens']} at {camera['settings']}.",
        f"{prompt}.",
        f"This must look like a real photograph, not an AI render.",
        " ".join(anti_ai),
    ]

    enhanced_text = " ".join(parts)

    result = {
        "enhanced_prompt": enhanced_text,
        "meta": {
            "original_prompt": prompt,
            "camera": camera,
            "realism_level": realism,
            "anti_ai_directives": anti_ai,
        },
    }

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Add realism layer to any image prompt"
    )
    parser.add_argument("--prompt", "-p", required=True, help="Your image prompt (any style, any intent)")
    parser.add_argument(
        "--camera", "-c",
        choices=["dslr", "mirrorless", "smartphone", "film"],
        default=None,
        help="Camera style (auto-detected from prompt if not specified)",
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

    camera_type = pick_camera_type(args.prompt, args.camera)

    result = build_enhanced_prompt(
        prompt=args.prompt,
        camera_type=camera_type,
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
