#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow", "numpy", "scikit-learn"]
# ///
"""Extract 5 dominant OKLCH colors from a subject image.

Output: JSON of the form
{
  "brand_1": "oklch(16% 0.04 270)",  # darkest, usually background
  "brand_2": "oklch(72% 0.17 55)",   # mid accent
  ...
  "brand_5": "oklch(94% 0.025 80)"   # lightest, usually ink/cream
}

The shells reference these as `--brand-1` through `--brand-5` CSS custom properties.

Usage:
  uv run extract_palette.py <image> --out palette.json
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path


def srgb_to_linear(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def rgb_to_oklab(r: float, g: float, b: float) -> tuple[float, float, float]:
    r, g, b = srgb_to_linear(r), srgb_to_linear(g), srgb_to_linear(b)
    L = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    M = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    S = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    L, M, S = L ** (1/3), M ** (1/3), S ** (1/3)
    return (
        0.2104542553*L + 0.7936177850*M - 0.0040720468*S,
        1.9779984951*L - 2.4285922050*M + 0.4505937099*S,
        0.0259040371*L + 0.7827717662*M - 0.8086757660*S,
    )


def oklab_to_oklch(lab: tuple[float, float, float]) -> tuple[float, float, float]:
    L, a, b = lab
    C = math.sqrt(a*a + b*b)
    H = math.degrees(math.atan2(b, a)) % 360
    return L, C, H


def fmt_oklch(lch: tuple[float, float, float]) -> str:
    L, C, H = lch
    return f'oklch({L*100:.1f}% {C:.3f} {H:.0f})'


def extract(img_path: Path, n_colors: int = 5) -> dict[str, str]:
    from PIL import Image
    import numpy as np
    from sklearn.cluster import KMeans

    img = Image.open(img_path).convert('RGB')
    if img.width > 320:
        ratio = 320 / img.width
        img = img.resize((320, int(img.height * ratio)), Image.LANCZOS)
    arr = np.array(img).reshape(-1, 3) / 255.0

    km = KMeans(n_clusters=n_colors, n_init=10, random_state=42)
    km.fit(arr)
    centroids = km.cluster_centers_

    # Sort by lightness (L of OKLab)
    lches = []
    for r, g, b in centroids:
        lch = oklab_to_oklch(rgb_to_oklab(float(r), float(g), float(b)))
        lches.append(lch)
    lches.sort(key=lambda x: x[0])  # darkest first

    return {f'brand_{i+1}': fmt_oklch(lch) for i, lch in enumerate(lches)}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('image', type=Path)
    p.add_argument('--out', type=Path, default=Path('palette.json'))
    p.add_argument('--n', type=int, default=5)
    args = p.parse_args()

    palette = extract(args.image, args.n)
    args.out.write_text(json.dumps(palette, indent=2, ensure_ascii=False))
    print(json.dumps(palette, indent=2, ensure_ascii=False))
    print(f'\nWrote {args.out}', file=sys.stderr)
    return 0


if __name__ == '__main__':
    sys.exit(main())
