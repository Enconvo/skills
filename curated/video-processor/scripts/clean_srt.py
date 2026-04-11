#!/usr/bin/env python3
"""
Clean filler words and verbal tics from SRT subtitles, then split long
multi-sentence segments into one-sentence-per-entry.

Runs between transcription and translation so downstream gets clean, short,
sentence-sized entries. Eliminates the class of bugs caused by Whisper
segment mode returning 5-15 second multi-sentence chunks.

Usage: clean_srt.py <srt_file> [--in-place] [--no-split]
"""
import sys
import os
import re


# Max lengths before splitting. Chosen so one SRT entry renders as one
# single-line caption at auto-sized fonts without wrapping.
MAX_WORDS_LATIN = 15
MAX_CHARS_CJK = 22

# Sentence-ending punctuation — Latin + CJK.
# No trailing-whitespace requirement: CJK text concatenates sentences without
# spaces (e.g. "A。B。C。"), so requiring \s after the punct would only match
# the final sentence. We match each "up-to-terminator" run independently.
SENTENCE_END_RE = re.compile(r'([^.!?。！？]*[.!?。！？]+)', re.UNICODE)
# Comma fallback — splits clauses when no sentence punctuation is present.
CLAUSE_END_RE = re.compile(r'([^,，；;]*[,，；;]+)', re.UNICODE)

CJK_RANGE_RE = re.compile(r'[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]')


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


def is_cjk_text(text):
    """True if the text contains CJK characters (heuristic: any CJK char)."""
    return bool(CJK_RANGE_RE.search(text))


def count_units(text):
    """Word count for Latin text, character count for CJK (excluding spaces/punct)."""
    if is_cjk_text(text):
        return sum(1 for c in text if CJK_RANGE_RE.match(c))
    return len(text.split())


def over_limit(text):
    """True if text exceeds the per-caption-line length limit."""
    if is_cjk_text(text):
        return count_units(text) > MAX_CHARS_CJK
    return count_units(text) > MAX_WORDS_LATIN


def split_by_regex(text, regex):
    """Split text using regex that captures each unit (including its trailing punct).
    Returns list of non-empty trimmed chunks. Any trailing remainder without
    matched punctuation is appended as its own chunk.
    """
    chunks = []
    pos = 0
    for m in regex.finditer(text):
        chunks.append(m.group(1).strip())
        pos = m.end()
    tail = text[pos:].strip()
    if tail:
        chunks.append(tail)
    return [c for c in chunks if c]


def hard_split(text, max_units):
    """Last-resort split at word/char boundaries."""
    if is_cjk_text(text):
        # Walk through characters, chunking at max_units CJK chars.
        out, buf, count = [], [], 0
        for c in text:
            buf.append(c)
            if CJK_RANGE_RE.match(c):
                count += 1
                if count >= max_units:
                    out.append(''.join(buf).strip())
                    buf, count = [], 0
        if buf:
            out.append(''.join(buf).strip())
        return [c for c in out if c]
    # Latin: word-based
    words = text.split()
    return [' '.join(words[i:i + max_units]).strip()
            for i in range(0, len(words), max_units)]


def _ends_with_sentence_punct(text):
    """True if text ends in sentence-ending punctuation (one complete sentence)."""
    return bool(text) and text.rstrip()[-1:] in '.!?。！？'


INTERNAL_COMMA_RE = re.compile(r'[,，；;]')


def split_sentence_text(text):
    """Split a single SRT entry's text into one-sentence-per-entry chunks.

    Strategy (three tiers):
      1. Always split on sentence-ending punctuation ([.!?。！？]).
      2. For each resulting chunk, decide whether to preserve it whole or
         split further on clause punctuation (commas, semicolons):
           - If the chunk is a complete sentence AND (under length cap OR has
             no internal commas) → preserve whole.
           - If the chunk is a non-sentence fragment under the length cap →
             preserve as-is.
           - Otherwise → comma-split. This catches two cases:
             (a) ASR-produced CJK compound sentences where Whisper joined
                 multiple clauses with `,` and only put one `。` at the end.
             (b) Long English compound sentences that run over the length cap.
      3. Any clause still over the length cap gets hard-split by word/char count.

    This rule preserves short sentences intact regardless of commas (so an
    English sentence like "I went home, had dinner." stays whole), preserves
    long sentences with no internal commas (so a dense single-clause statement
    stays whole), but splits long comma-joined compounds — which is exactly
    the pattern Whisper produces for Chinese multi-clause run-ons.

    Returns list of chunks.
    """
    text = text.strip()
    if not text:
        return []

    chunks = split_by_regex(text, SENTENCE_END_RE)
    if not chunks:
        chunks = [text]

    out = []
    for c in chunks:
        ends_sentence = _ends_with_sentence_punct(c)
        has_internal_comma = bool(INTERNAL_COMMA_RE.search(c))
        # Whole sentence: preserve if short, or if there's no comma to split on.
        if ends_sentence and (not over_limit(c) or not has_internal_comma):
            out.append(c)
            continue
        # Non-sentence fragment under the limit: pass through.
        if not ends_sentence and not over_limit(c):
            out.append(c)
            continue
        # Long chunk: comma split, then hard cap for anything still too long.
        subs = split_by_regex(c, CLAUSE_END_RE) or [c]
        for s in subs:
            if over_limit(s):
                max_u = MAX_CHARS_CJK if is_cjk_text(s) else MAX_WORDS_LATIN
                out.extend(hard_split(s, max_u))
            else:
                out.append(s)
    return [c for c in out if c]


def _parse_ts(ts):
    """SRT timestamp 'HH:MM:SS,mmm' → seconds (float)."""
    h, m, rest = ts.split(':')
    s, ms = rest.replace('.', ',').split(',')
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0


def _format_ts(t):
    """Seconds → SRT timestamp 'HH:MM:SS,mmm'."""
    if t < 0:
        t = 0
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = int(t % 60)
    ms = int(round((t - int(t)) * 1000))
    if ms >= 1000:
        s += 1
        ms -= 1000
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def split_long_segments(srt_content):
    """Walk SRT blocks and split any multi-sentence entry into per-sentence entries.

    Time redistribution: proportional to character count of each sub-sentence.
    Indices are renumbered sequentially. Blocks that fit the length limit
    pass through unchanged.
    """
    blocks = srt_content.strip().split('\n\n')
    new_entries = []  # list of (start_sec, end_sec, text)

    for block in blocks:
        lines = block.split('\n')
        if len(lines) < 3:
            continue
        ts_line = lines[1]
        m = re.match(r'(\d{2}:\d{2}:\d{2}[,.]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[,.]\d{3})', ts_line)
        if not m:
            continue
        start = _parse_ts(m.group(1).replace('.', ','))
        end = _parse_ts(m.group(2).replace('.', ','))
        text = '\n'.join(lines[2:]).strip()
        if not text:
            continue

        chunks = split_sentence_text(text)
        if len(chunks) <= 1:
            new_entries.append((start, end, text))
            continue

        # Distribute time proportionally by char count.
        total_chars = sum(max(1, len(c)) for c in chunks) or 1
        dur = max(0.0, end - start)
        cursor = start
        for i, chunk in enumerate(chunks):
            share = max(1, len(chunk)) / total_chars
            if i == len(chunks) - 1:
                sub_end = end
            else:
                sub_end = cursor + dur * share
            new_entries.append((cursor, sub_end, chunk))
            cursor = sub_end

    out_blocks = []
    for i, (s, e, t) in enumerate(new_entries, start=1):
        out_blocks.append(f"{i}\n{_format_ts(s)} --> {_format_ts(e)}\n{t}")
    return '\n\n'.join(out_blocks) + '\n'


def clean_srt_file(srt_path, do_split=True):
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

    split_count_before = total_count
    split_count_after = total_count
    if do_split:
        split_content = split_long_segments(cleaned_content)
        # Count new entries after split.
        split_count_after = sum(
            1 for b in split_content.strip().split('\n\n')
            if len(b.split('\n')) >= 3
        )
        cleaned_content = split_content

    return cleaned_content, total_count, changed_count, split_count_before, split_count_after


def main():
    if len(sys.argv) < 2:
        print("Usage: clean_srt.py <srt_file> [--in-place] [--no-split]")
        print("  Without --in-place: prints cleaned content to stdout")
        print("  With --in-place: overwrites the file")
        print("  With --no-split: skip sentence splitting (only filler cleanup)")
        sys.exit(1)

    srt_file = sys.argv[1]
    in_place = '--in-place' in sys.argv
    do_split = '--no-split' not in sys.argv

    if not os.path.exists(srt_file):
        print(f"Error: File not found: {srt_file}")
        sys.exit(1)

    cleaned_content, total, changed, before, after = clean_srt_file(srt_file, do_split=do_split)

    split_note = f", split {before} -> {after}" if do_split else ""
    if in_place:
        with open(srt_file, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
        print(f"Cleaned {srt_file}: {changed}/{total} segments modified{split_note}")
    else:
        sys.stdout.write(cleaned_content)
        print(f"Stats: {changed}/{total} segments modified{split_note}", file=sys.stderr)


if __name__ == "__main__":
    main()
