#!/usr/bin/env python3
"""
Photo Dedup — Deduplication Scanner
Finds unique photos from duplicates/near-duplicates using perceptual hashing.
Generates a JSON report and optionally an interactive HTML review page.
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

try:
    from PIL import Image
    import imagehash
except ImportError:
    print("ERROR: Required packages not installed. Run:")
    print("  pip3 install Pillow imagehash pillow-heif")
    sys.exit(1)

# Register HEIC/HEIF support if available
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass  # HEIC files will be skipped

SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.heic', '.webp', '.tiff', '.tif', '.bmp'}


def get_image_files(folder: Path) -> list[Path]:
    """Get all supported image files from folder."""
    files = []
    for f in sorted(folder.rglob('*')):
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS:
            files.append(f)
    return files


def compute_hash(filepath: Path) -> "imagehash.ImageHash | None":
    """Compute perceptual hash for an image."""
    try:
        with Image.open(filepath) as img:
            return imagehash.phash(img)
    except Exception as e:
        print(f"  WARNING: Could not process {filepath.name}: {e}")
        return None


def cluster_images(image_hashes: dict, threshold: int) -> list[list[Path]]:
    """Group images into clusters based on hash similarity."""
    files = list(image_hashes.keys())
    visited = set()
    clusters = []

    for i, file_a in enumerate(files):
        if file_a in visited:
            continue
        cluster = [file_a]
        visited.add(file_a)

        for j in range(i + 1, len(files)):
            file_b = files[j]
            if file_b in visited:
                continue
            distance = image_hashes[file_a] - image_hashes[file_b]
            if distance <= threshold:
                cluster.append(file_b)
                visited.add(file_b)

        clusters.append(cluster)

    return clusters


def pick_best(cluster: list[Path]) -> Path:
    """Pick the best image from a cluster (largest file = highest quality)."""
    return max(cluster, key=lambda f: f.stat().st_size)


def format_size(size_bytes: int) -> str:
    """Format bytes to human readable."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def main():
    parser = argparse.ArgumentParser(description="Photo Dedup — find unique photos from duplicates")
    parser.add_argument("source", help="Source folder containing photos")
    parser.add_argument("--threshold", type=int, default=6,
                        help="Similarity threshold (0-20, default: 6). Lower = stricter.")
    parser.add_argument("--preview", action="store_true",
                        help="Preview mode — scan only, then generate review HTML")
    parser.add_argument("--output", help="Custom output folder (default: source/unique/)")
    parser.add_argument("--no-html", action="store_true",
                        help="Skip HTML generation (just produce JSON report)")
    args = parser.parse_args()

    source = Path(args.source).resolve()
    if not source.is_dir():
        print(f"ERROR: '{source}' is not a directory")
        sys.exit(1)

    output = Path(args.output) if args.output else source / "unique"

    # Find images
    print(f"Scanning: {source}")
    images = get_image_files(source)
    if not images:
        print("No supported image files found.")
        sys.exit(0)

    print(f"Found {len(images)} images. Computing hashes...")

    # Compute hashes
    hashes = {}
    for i, img in enumerate(images, 1):
        h = compute_hash(img)
        if h is not None:
            hashes[img] = h
        if i % 50 == 0 or i == len(images):
            print(f"  Processed {i}/{len(images)}")

    # Cluster
    print(f"\nClustering with threshold={args.threshold}...")
    clusters = cluster_images(hashes, args.threshold)

    # Pick best from each cluster
    unique_picks = []
    duplicate_count = 0
    report_clusters = []

    for cluster in clusters:
        best = pick_best(cluster)
        unique_picks.append(best)
        dupes = [f for f in cluster if f != best]
        duplicate_count += len(dupes)

        # Include full paths for the HTML generator
        paths = {best.name: str(best)}
        for d in dupes:
            paths[d.name] = str(d)

        report_clusters.append({
            "selected": best.name,
            "selected_size": format_size(best.stat().st_size),
            "duplicates": [f.name for f in dupes],
            "paths": paths,
            "count": len(cluster)
        })

    # Sort clusters by size (most duplicates first)
    report_clusters.sort(key=lambda c: c["count"], reverse=True)

    # Print summary
    print(f"\n{'='*60}")
    print(f"RESULTS")
    print(f"{'='*60}")
    print(f"  Total photos scanned:  {len(hashes)}")
    print(f"  Unique photos found:   {len(unique_picks)}")
    print(f"  Duplicates identified: {duplicate_count}")
    print(f"  Dedup ratio:           {len(hashes)}:{len(unique_picks)} ({100*len(unique_picks)/len(hashes):.0f}% unique)")

    # Show top clusters with most duplicates
    multi_clusters = [c for c in report_clusters if c["count"] > 1]
    if multi_clusters:
        print(f"\n  Top duplicate groups:")
        for c in multi_clusters[:10]:
            print(f"    - {c['selected']} ({c['selected_size']}) + {len(c['duplicates'])} duplicate(s)")

    if args.preview:
        print(f"\n  PREVIEW MODE — no files were copied.")
    else:
        # Copy unique photos
        output.mkdir(parents=True, exist_ok=True)
        print(f"\n  Copying {len(unique_picks)} unique photos to: {output}")
        for img in unique_picks:
            dest = output / img.name
            if dest.exists():
                stem = img.stem
                suffix = img.suffix
                counter = 1
                while dest.exists():
                    dest = output / f"{stem}_{counter}{suffix}"
                    counter += 1
            shutil.copy2(img, dest)
        print(f"  Done! Unique photos saved to: {output}")

    # Save report
    report = {
        "source": str(source),
        "total_scanned": len(hashes),
        "unique_count": len(unique_picks),
        "duplicate_count": duplicate_count,
        "threshold": args.threshold,
        "clusters": report_clusters
    }
    report_path = Path("/tmp") / f"dedup_report_{source.name}.json"
    if not args.preview:
        report_path = output / "dedup_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"  Report saved to: {report_path}")

    # Auto-generate HTML review page
    if not args.no_html and multi_clusters:
        print(f"\nGenerating review page...")
        script_dir = Path(__file__).resolve().parent
        gen_script = script_dir / "generate_review.py"
        if gen_script.exists():
            cmd = [sys.executable, str(gen_script), str(report_path)]
            if not args.preview:
                cmd += ["--no-open"]
            subprocess.run(cmd)
        else:
            print(f"  WARNING: generate_review.py not found at {gen_script}")


if __name__ == "__main__":
    main()
