# Photo Dedup

Find and remove duplicate photos. Scans a folder, identifies duplicate groups using perceptual hashing, and generates an interactive HTML review page — no server needed.

## How It Works

1. **Perceptual Hashing** — Each image is converted to a pHash. Similar-looking images produce similar hashes.
2. **Clustering** — Images are grouped by similarity. The best image (largest file) is auto-selected.
3. **Interactive Review** — A self-contained HTML page lets you see all duplicate groups, pick which to keep, and download a save script.

## Quick Start

### Requirements

```bash
pip3 install Pillow imagehash pillow-heif
```

Python 3.10+ required.

### 1. Scan for duplicates

```bash
python3 scripts/dedup.py ~/Photos/event-folder/ --preview
```

This scans the folder, finds duplicates, generates a review HTML page, and opens it in the browser.

Options:
- `--preview` — Scan only, generate HTML review (recommended first step)
- `--threshold N` — Similarity sensitivity (default: 6, range 0-20)
- `--output DIR` — Custom output folder for unique photos
- `--no-html` — Skip HTML generation, just produce JSON report

### 2. Review & select

The HTML page opens automatically. You can:
- See all duplicate groups side by side
- Click to select which photos to keep
- **Auto-select best** — one-click pick of highest quality from each group
- Click 🔍 to preview photos in lightbox
- **Save selected** — downloads a `copy_photos.sh` script

### 3. Save

Run the downloaded script:

```bash
bash ~/Downloads/copy_photos.sh
```

Selected photos are copied to `~/Desktop/photo_picks/` (originals untouched).

### Supported Formats

JPG, JPEG, PNG, HEIC, WEBP, TIFF, BMP

### Safety

- Originals are **never** modified or deleted
- "Save" copies files to a new folder, leaving originals in place

## Claude Code Skill

This is a [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill. Install it and use natural language:

```
> dedup my photos in ~/Photos/school-event/
```

See `SKILL.md` for the skill definition.

## License

MIT
