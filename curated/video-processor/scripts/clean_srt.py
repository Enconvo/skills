#!/usr/bin/env python3
"""
Clean filler words and verbal tics from SRT subtitles.
Runs between transcription and translation to prevent filler propagation.
Usage: clean_srt.py <srt_file> [--in-place]
"""
import sys
import os
import re


# Filler patterns (case-insensitive)
# Each tuple: (compiled regex, replacement)
FILLER_PATTERNS = [
    # === "you know" (aggressive — remove in all positions) ===
    # Repeated "you know" (2+ occurrences in same segment)
    (re.compile(r'(?:[,.]?\s*you know[,.]?\s*){2,}', re.IGNORECASE), ' '),
    # "you know" at start/end of segment
    (re.compile(r'^you know[,.]?\s*', re.IGNORECASE), ''),
    (re.compile(r'[,.]?\s*you know[.]?\s*$', re.IGNORECASE), ''),
    # "you know" between commas
    (re.compile(r',\s*you know,\s*', re.IGNORECASE), ', '),
    # "you know" after sentence-ending punctuation
    (re.compile(r'([.!?])\s*you know[,.]?\s*', re.IGNORECASE), r'\1 '),
    # "you know" mid-sentence without commas (raw Whisper output)
    (re.compile(r'(?<=\w)\s+you know\s+(?=\w)', re.IGNORECASE), ' '),
    # "And you know" transitions
    (re.compile(r'\band you know[,.]?\s*', re.IGNORECASE), 'and '),

    # === Standalone filler sounds ===
    (re.compile(r'\b(?:um|uh|uhm|umm|hmm|hm|er|erm|ah|ahh)\b[,.]?\s*', re.IGNORECASE), ''),

    # === Filler words/phrases at segment start ===
    # "Yeah," / "Yeah." / "Yeah yeah" at start — acknowledgment filler
    (re.compile(r'^(?:yeah[,.\s]*)+', re.IGNORECASE), ''),
    # "Well," at start — discourse marker
    (re.compile(r'^well[,.]?\s*', re.IGNORECASE), ''),
    # "Oh," at start — interjection
    (re.compile(r'^oh[,.]?\s*', re.IGNORECASE), ''),
    # "Okay," / "OK," at start
    (re.compile(r'^(?:okay|ok)[,.]?\s*', re.IGNORECASE), ''),
    # "Right," / "Right?" at start
    (re.compile(r'^right[,?.]?\s*', re.IGNORECASE), ''),
    # "So," at start (single, as discourse marker)
    (re.compile(r'^so,\s*', re.IGNORECASE), ''),
    # "Like," at start
    (re.compile(r'^like,\s*', re.IGNORECASE), ''),
    # "I mean" at start or mid-sentence between commas
    (re.compile(r'^I mean[,.]?\s*', re.IGNORECASE), ''),
    (re.compile(r',\s*I mean,\s*', re.IGNORECASE), ', '),
    # "Actually," at start
    (re.compile(r'^actually,\s*', re.IGNORECASE), ''),

    # === Filler phrases at end of segment ===
    # "right?" / "right." at end
    (re.compile(r'[,.]?\s*right[?.]\s*$', re.IGNORECASE), '.'),

    # === Mid-sentence fillers (between commas or in natural positions) ===
    # "like" as filler between commas
    (re.compile(r',\s*like,\s*', re.IGNORECASE), ', '),
    # "I would say" as hedging filler
    (re.compile(r',?\s*I would say,?\s*', re.IGNORECASE), ' '),
    # "basically" / "essentially" as filler
    (re.compile(r',?\s*basically,?\s*', re.IGNORECASE), ' '),
    (re.compile(r',?\s*essentially,?\s*', re.IGNORECASE), ' '),

    # === Repeated phrases (2+ in same segment) ===
    (re.compile(r'(?:,?\s*sort of[,.]?\s*){2,}', re.IGNORECASE), ' sort of '),
    (re.compile(r'(?:,?\s*kind of[,.]?\s*){2,}', re.IGNORECASE), ' kind of '),
    (re.compile(r'(?:,?\s*right[,?]?\s*){2,}', re.IGNORECASE), ' '),
    (re.compile(r'(?:^|\.\s*)(?:so,?\s*){2,}', re.IGNORECASE), 'So, '),

    # === Stutters: "I- I", "the- the", "we- we" etc. ===
    (re.compile(r'\b(\w+)-\s*\1\b', re.IGNORECASE), r'\1'),
    # Whisper triple repeats without hyphens: "in in in" → "in"
    (re.compile(r'\b(\w+)\s+\1\s+\1\b', re.IGNORECASE), r'\1'),
    # Double repeats: "was was" → "was" (but not intentional like "very very")
    (re.compile(r'\b(I|the|a|an|to|is|was|we|it|that|this|and|but|or|so|in|on|of)\s+\1\b', re.IGNORECASE), r'\1'),
]

# Post-cleanup patterns
CLEANUP_PATTERNS = [
    # Multiple spaces
    (re.compile(r'  +'), ' '),
    # Space before punctuation
    (re.compile(r'\s+([,.:;!?])'), r'\1'),
    # Leading/trailing whitespace
    (re.compile(r'^\s+|\s+$'), ''),
    # Leading comma
    (re.compile(r'^[,.\s]+'), ''),
    # Double commas
    (re.compile(r',\s*,'), ','),
    # Capitalize first letter
]


def clean_text(text):
    """Remove filler words and verbal tics from a subtitle text."""
    original = text

    for pattern, replacement in FILLER_PATTERNS:
        text = pattern.sub(replacement, text)

    for pattern, replacement in CLEANUP_PATTERNS:
        text = pattern.sub(replacement, text)

    # Capitalize first letter if lowered after cleanup
    if text and text[0].islower() and (not original or original[0].isupper()):
        text = text[0].upper() + text[1:]

    # If cleanup removed everything, keep original
    if not text.strip():
        text = original

    return text.strip()


def clean_srt_file(srt_path):
    """Clean an SRT file and return (cleaned_content, stats)."""
    with open(srt_path, 'r', encoding='utf-8') as f:
        content = f.read()

    blocks = content.strip().split('\n\n')
    cleaned_blocks = []
    changed_count = 0
    total_count = 0

    for block in blocks:
        lines = block.split('\n')
        if len(lines) >= 3:
            total_count += 1
            index = lines[0]
            timestamp = lines[1]
            text = '\n'.join(lines[2:])

            cleaned = clean_text(text)
            if cleaned != text:
                changed_count += 1

            cleaned_blocks.append(f"{index}\n{timestamp}\n{cleaned}")
        else:
            cleaned_blocks.append(block)

    cleaned_content = '\n\n'.join(cleaned_blocks) + '\n'
    return cleaned_content, total_count, changed_count


def main():
    if len(sys.argv) < 2:
        print("Usage: clean_srt.py <srt_file> [--in-place]")
        print("  Without --in-place: prints cleaned content to stdout")
        print("  With --in-place: overwrites the file")
        sys.exit(1)

    srt_file = sys.argv[1]
    in_place = '--in-place' in sys.argv

    if not os.path.exists(srt_file):
        print(f"Error: File not found: {srt_file}")
        sys.exit(1)

    cleaned_content, total, changed = clean_srt_file(srt_file)

    if in_place:
        with open(srt_file, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
        print(f"Cleaned {srt_file}: {changed}/{total} segments modified")
    else:
        # Print to stdout for piping
        sys.stdout.write(cleaned_content)
        # Stats to stderr so they don't mix with content
        print(f"Stats: {changed}/{total} segments modified", file=sys.stderr)


if __name__ == "__main__":
    main()
