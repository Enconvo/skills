#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pillow",
#     "numpy",
#     "transformers>=4.40",
#     "torch",
#     "rembg ; extra == 'matte'",
# ]
# ///
"""Prepare a subject image for use as a hero asset.

Branches on subject type:
- human / scene: downscale to 900px wide; depth map via Depth Anything V2.
- product: downscale + depth + alpha matte (rembg).
- brand-mark: keep PNG/SVG transparency; skip depth.
- abstract: just downscale.

Outputs `hero.jpg` (always) and `hero_depth.jpg` / `hero_alpha.png` as appropriate.

Usage:
  uv run prep_subject.py <input_image> <output_dir> --type <human|product|brand-mark|abstract|scene>
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def downscale(img_path: Path, out_path: Path, target_w: int = 900) -> tuple[int, int]:
    from PIL import Image
    img = Image.open(img_path).convert('RGB')
    if img.width > target_w:
        ratio = target_w / img.width
        img = img.resize((target_w, int(img.height * ratio)), Image.LANCZOS)
    img.save(out_path, quality=90)
    return img.size


def generate_depth_map(img_path: Path, out_path: Path) -> None:
    from transformers import pipeline
    from PIL import Image, ImageFilter
    import torch

    device = 'mps' if torch.backends.mps.is_available() else ('cuda' if torch.cuda.is_available() else 'cpu')
    print(f'Running Depth Anything V2 on {device}…')
    pipe = pipeline(
        task='depth-estimation',
        model='depth-anything/Depth-Anything-V2-Small-hf',
        device=device,
    )
    img = Image.open(img_path).convert('RGB')
    out = pipe(img)
    depth = out['depth']
    # soften high-frequency edges so the displaced mesh doesn't tear
    depth = depth.filter(ImageFilter.GaussianBlur(radius=2))
    depth.save(out_path, quality=92)


def generate_alpha_matte(img_path: Path, out_path: Path) -> None:
    try:
        from rembg import remove
    except ImportError:
        print('rembg not installed; skipping alpha matte. Install via: pip install rembg', file=sys.stderr)
        return
    with open(img_path, 'rb') as f:
        in_bytes = f.read()
    out_bytes = remove(in_bytes)
    out_path.write_bytes(out_bytes)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('input', type=Path, help='Source image path')
    p.add_argument('output_dir', type=Path, help='Where to write hero.jpg etc.')
    p.add_argument('--type', choices=['human', 'product', 'brand-mark', 'abstract', 'scene'], required=True)
    p.add_argument('--target-width', type=int, default=900)
    args = p.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    if args.type == 'brand-mark':
        # Keep transparency; just copy
        from shutil import copy
        ext = args.input.suffix.lower()
        if ext in ('.svg',):
            copy(args.input, args.output_dir / 'hero.svg')
            print(f'Saved {args.output_dir / "hero.svg"} (vector, untouched)')
        else:
            from PIL import Image
            img = Image.open(args.input).convert('RGBA')
            if img.width > args.target_width:
                ratio = args.target_width / img.width
                img = img.resize((args.target_width, int(img.height * ratio)), Image.LANCZOS)
            img.save(args.output_dir / 'hero.png')
            print(f'Saved {args.output_dir / "hero.png"} (RGBA, {img.size})')
        return 0

    # All other subject types: downscale to JPG
    hero_path = args.output_dir / 'hero.jpg'
    size = downscale(args.input, hero_path, args.target_width)
    print(f'Saved {hero_path} ({size[0]}x{size[1]})')

    if args.type == 'abstract':
        return 0  # done

    # Depth map for human / product / scene
    depth_path = args.output_dir / 'hero_depth.jpg'
    generate_depth_map(args.input, depth_path)
    print(f'Saved {depth_path}')

    if args.type == 'product':
        alpha_path = args.output_dir / 'hero_alpha.png'
        generate_alpha_matte(args.input, alpha_path)
        if alpha_path.exists():
            print(f'Saved {alpha_path}')

    return 0


if __name__ == '__main__':
    sys.exit(main())
