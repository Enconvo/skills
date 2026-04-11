#!/usr/bin/env python3
"""Pre-translation SRT review gate.

Runs after clean_srt.py and before translate/dub. Prints a report with stats
and flags so the agent can decide whether to proceed or intervene (e.g. manual
splits for long compound sentences, or merges for micro-fragments when dubbing
from a dense language like Chinese to a wordier language like English).

Usage: review_srt.py <srt_file>

Exit code: always 0 (informational only — the agent interprets the verdict).
"""
import os
import re
import sys

# Length thresholds. Mirror clean_srt.py's caps so the review aligns with
# what the splitter considers "over the limit".
# Netflix/BBC/EBU subtitle standard: 42 chars/line for Latin, ~16 for CJK.
LONG_LATIN_CHARS = 42
LONG_CJK_CHARS = 16

# Hard threshold — if any entry exceeds this, it's almost certainly a problem.
HARD_LATIN_CHARS = 60
HARD_CJK_CHARS = 24

# Duration thresholds for the dub-side check.
SHORT_DURATION_S = 1.0     # flag if many entries are under this
CRITICAL_SHORT_S = 0.6     # always flag entries under this

CJK_RANGE = re.compile(r'[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]')
SRT_TS = re.compile(
    r'(\d{2}:\d{2}:\d{2}[,.]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[,.]\d{3})'
)


def parse_ts(ts):
    h, m, rest = ts.split(':')
    s, ms = rest.replace(',', '.').split('.')
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def is_cjk(text):
    return bool(CJK_RANGE.search(text))


def unit_count(text):
    """Characters. For CJK: only CJK chars. For Latin: full length."""
    if is_cjk(text):
        return sum(1 for c in text if CJK_RANGE.match(c))
    return len(text)


def parse_srt(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    entries = []
    for block in re.split(r'\n\n+', content.strip()):
        lines = block.strip().split('\n')
        if len(lines) < 3:
            continue
        m = SRT_TS.search(lines[1])
        if not m:
            continue
        start, end = parse_ts(m.group(1)), parse_ts(m.group(2))
        text = ' '.join(lines[2:]).strip()
        entries.append({
            'index': int(lines[0]) if lines[0].isdigit() else len(entries) + 1,
            'start': start,
            'end': end,
            'duration': max(0.0, end - start),
            'text': text,
            'units': unit_count(text),
            'is_cjk': is_cjk(text),
        })
    return entries


def fmt_time(seconds):
    m, s = divmod(int(seconds), 60)
    return f'{m}:{s:02d}'


def review(path):
    entries = parse_srt(path)
    if not entries:
        print(f'ERROR: no valid entries in {path}')
        return 'CRITICAL', {}

    total = len(entries)
    total_dur = entries[-1]['end'] - entries[0]['start']
    units = [e['units'] for e in entries]
    durs = [e['duration'] for e in entries]

    # Flags
    soft_long = [e for e in entries
                 if (e['is_cjk'] and e['units'] > LONG_CJK_CHARS)
                 or (not e['is_cjk'] and e['units'] > LONG_LATIN_CHARS)]
    hard_long = [e for e in entries
                 if (e['is_cjk'] and e['units'] > HARD_CJK_CHARS)
                 or (not e['is_cjk'] and e['units'] > HARD_LATIN_CHARS)]
    short_dur = [e for e in entries if e['duration'] < SHORT_DURATION_S]
    critical_short = [e for e in entries if e['duration'] < CRITICAL_SHORT_S]

    short_ratio = len(short_dur) / total
    long_ratio = len(soft_long) / total

    # Verdict
    verdict = 'OK'
    reasons = []
    if hard_long:
        verdict = 'CRITICAL'
        reasons.append(f'{len(hard_long)} entries over hard length threshold')
    if long_ratio > 0.1:
        verdict = 'CRITICAL' if verdict == 'CRITICAL' else 'WARN'
        reasons.append(f'{len(soft_long)} entries ({long_ratio:.0%}) over soft length cap')
    if short_ratio > 0.3:
        verdict = 'CRITICAL'
        reasons.append(f'{len(short_dur)} entries ({short_ratio:.0%}) under {SHORT_DURATION_S}s — TTS overrun risk')
    elif short_ratio > 0.1:
        verdict = 'WARN' if verdict == 'OK' else verdict
        reasons.append(f'{len(short_dur)} entries ({short_ratio:.0%}) under {SHORT_DURATION_S}s')
    if len(critical_short) > 0 and verdict == 'OK':
        verdict = 'WARN'
        reasons.append(f'{len(critical_short)} entries under {CRITICAL_SHORT_S}s (hard short)')

    # Report
    max_entry = max(entries, key=lambda e: e['units'])
    shortest_entry = min(entries, key=lambda e: e['duration'])
    unit_label = 'chars'

    print(f'SRT Review: {os.path.basename(path)}')
    print('─' * 60)
    print(f'Total entries:  {total}           Duration: {fmt_time(total_dur)}')
    print(f'Avg entry:      ~{sum(units)/total:.0f} {unit_label} / {sum(durs)/total:.1f}s')
    print(f'Max entry:      #{max_entry["index"]} — {max_entry["units"]} {unit_label}, '
          f'{max_entry["duration"]:.1f}s — "{max_entry["text"][:60]}{"..." if len(max_entry["text"]) > 60 else ""}"')
    print(f'Shortest dur:   #{shortest_entry["index"]} — {shortest_entry["duration"]:.2f}s — '
          f'"{shortest_entry["text"][:50]}{"..." if len(shortest_entry["text"]) > 50 else ""}"')
    print()

    # Flags section
    marker = {'OK': '✓', 'WARN': '⚠', 'CRITICAL': '✗'}[verdict]
    print(f'Flags:')
    if not reasons:
        print(f'  {marker} OK — no anomalies detected')
    else:
        for r in reasons:
            print(f'  {marker} {r}')
    print()
    print(f'Verdict: {verdict}')
    if verdict != 'OK':
        print()
        print('Recommended action:')
        if hard_long or long_ratio > 0.1:
            print('  - Long entries: consider manual comma/semicolon splits, or')
            print('    reject and re-run clean_srt.py if splitter was bypassed.')
        if short_ratio > 0.1:
            print('  - Short entries: when dubbing to a wordier target language')
            print('    (CJK→English especially), consider merging adjacent fragments')
            print('    within the same utterance before running TTS.')

    return verdict, {
        'total': total, 'soft_long': len(soft_long), 'hard_long': len(hard_long),
        'short_dur': len(short_dur), 'critical_short': len(critical_short),
    }


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help'):
        print(__doc__)
        sys.exit(0)
    path = sys.argv[1]
    if not os.path.exists(path):
        print(f'Error: file not found: {path}')
        sys.exit(1)
    review(path)
    sys.exit(0)


if __name__ == '__main__':
    main()
