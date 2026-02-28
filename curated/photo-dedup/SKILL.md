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
5. **User reviews in browser** — they see all duplicate groups, click to select photos to keep, then click "Keep Selected" button
6. **Browser confirms** — a confirmation dialog warns the user that unselected duplicates will be deleted
7. **Auto-delete** — the browser calls the Enconvo API (`http://localhost:54535/command/call/enconvo/delete_files`) to delete unselected duplicate files directly

No server needed for the review page. The HTML file is self-contained — works offline, opens instantly. File deletion is handled via the Enconvo local API.

## Output Structure

```
<source>/photo_dedup.html      ← Review page (open in browser)
/tmp/dedup_report_*.json       ← Scan report
```

## Important Notes

- **Destructive** — Unselected duplicate photos will be permanently deleted after user confirmation
- **Best quality auto-selected** — The largest file in each group is auto-selected for keeping
- **Supported formats** — JPG, JPEG, PNG, HEIC, WEBP, TIFF, BMP
- **Performance** — Handles 500+ photos in under a minute
- **No server** — Review page runs as static HTML, deletion via Enconvo local API
