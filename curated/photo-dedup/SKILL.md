---
name: photo-dedup
description: "Find & remove duplicate photos using perceptual hashing. Interactive browser review page — no server needed. Use when user says: dedup photos, find duplicate photos, remove duplicate images, photo dedup, /photo-dedup."
user_invocable: true
---

# Photo Dedup — Find & Remove Duplicate Photos

Use this skill when the user wants to deduplicate photos, find unique images, remove similar/duplicate photos. Trigger phrases: "dedup photos", "find duplicate photos", "remove duplicate images", "photo dedup", "/photo-dedup".

## Overview

Processes a folder of photos, identifies duplicates and near-duplicates using perceptual hashing, and generates an interactive HTML review page. The user reviews duplicate groups and picks which to keep — no server required.

## How It Works

1. **Perceptual Hashing** — Each image is converted to a perceptual hash (pHash). Similar-looking images produce similar hashes, even if they differ in resolution, compression, or minor edits.

2. **Clustering** — Images are grouped by hash similarity. Each cluster = one "scene". The best image (largest file = highest quality) is auto-selected.

3. **Interactive Review** — A self-contained HTML page opens in the browser. The user reviews duplicate groups, picks which to keep, and downloads a save script.

## Usage

### Basic:
```
/photo-dedup ~/Photos/school-event/
```

### With custom threshold:
```
/photo-dedup ~/Photos/school-event/ --threshold 8
```
Threshold controls similarity sensitivity (default: 6, range 0-20). Lower = stricter, higher = more aggressive grouping.

## Workflow

When the user invokes this skill:

1. **Validate input** — Confirm the source folder exists and contains images
2. **Install dependencies if needed** — `pip3 install Pillow imagehash pillow-heif`
3. **Run the scan** (generates report + HTML review page, opens browser automatically):
   ```bash
   python3 ~/.claude/skills/photo-dedup/scripts/dedup.py <source_folder> --preview [--threshold N]
   ```
4. **Report results** to the user (total, unique, duplicates)
5. **User reviews in browser** — they see all duplicate groups, click to select photos, then click "Save selected" to download a `copy_photos.sh` script
6. **Run the save script** for the user:
   ```bash
   bash ~/Downloads/copy_photos.sh
   ```
7. **Tell the user** where the selected photos are saved (default: `~/Desktop/photo_picks/`)

No server needed. The HTML file is self-contained — works offline, opens instantly.

## Output Structure

```
~/Desktop/photo_picks/         ← Selected photos (copies, originals untouched)
<source>/photo_dedup.html      ← Review page (open in browser)
/tmp/dedup_report_*.json       ← Scan report
```

## Important Notes

- **Non-destructive** — Original photos are NEVER moved or deleted
- **Supported formats** — JPG, JPEG, PNG, HEIC, WEBP, TIFF, BMP
- **Performance** — Handles 500+ photos in under a minute
- **No server** — Everything runs locally as static HTML
