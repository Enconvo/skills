#!/usr/bin/env python3
"""Regenerate ~/.claude/skills/hermes-configure/cli-reference.md exhaustively.

Walks every Hermes subparser recursively (depth 4) and dumps each --help.

Why the careful subcommand parser:
  argparse prints flag value enums (e.g. `--type {oauth,api-key}`) with the same
  `{a,b,c}` shape as real subparser choice lists. A naive regex matches both,
  and walking into a flag enum hits an infinite loop because argparse silently
  ignores unknown positionals and re-prints the same help.

Fix: only treat `{a,b,c}` as subcommands when it appears inside the
`positional arguments:` block AND is followed by an indented `name   description`
listing. Cap depth at 4. Track visited paths.

Expected output size: 300–900 KB. Anything tens-of-MB means the runaway is back.
"""
import re
import subprocess
import datetime
import pathlib

HERMES = subprocess.check_output(['which', 'hermes'], text=True).strip()
MAX_DEPTH = 4
TIMEOUT = 20
OUT_PATH = pathlib.Path.home() / '.claude/skills/hermes-configure/cli-reference.md'


def run(path):
    try:
        r = subprocess.run([HERMES, *path, '--help'], capture_output=True, text=True, timeout=TIMEOUT)
        return (r.stdout or '') + (r.stderr or '')
    except Exception as e:
        return f"<help fetch failed: {e}>"


def subcommands(help_text):
    """Extract real subparser choices, ignoring flag enums."""
    lines = help_text.splitlines()
    in_pos = False
    i = 0
    while i < len(lines):
        if re.match(r'^positional arguments:', lines[i]):
            in_pos = True
            i += 1
            continue
        if in_pos:
            m = re.match(r'^\s+\{([a-zA-Z0-9_,\-]+)\}\s*\.{0,3}\s*$', lines[i])
            if m:
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1
                if j < len(lines) and re.match(r'^\s{4,}\S+\s', lines[j]):
                    return [s.strip() for s in m.group(1).split(',') if s.strip()]
                return []
            if re.match(r'^[A-Za-z][A-Za-z ]*:\s*$', lines[i]):
                break
        i += 1
    return []


def main():
    ver = subprocess.check_output([HERMES, '--version'], text=True).strip()
    out = [
        "# Hermes CLI Full Reference",
        f"_Auto-generated {datetime.date.today()} for {ver}_",
        "",
        "## hermes (top-level)",
        "```",
        run([]).rstrip(),
        "```",
    ]

    visited = set()
    stats = {'nodes': 1, 'max_depth': 0}

    def walk(path, depth):
        key = ' '.join(path)
        if key in visited or depth > MAX_DEPTH:
            return
        visited.add(key)
        stats['nodes'] += 1
        stats['max_depth'] = max(stats['max_depth'], depth)
        help_text = run(path)
        hashes = '#' * (depth + 1)
        out.append(f"\n{hashes} hermes {' '.join(path)}")
        out.append("```")
        out.append(help_text.rstrip())
        out.append("```")
        for sub in subcommands(help_text):
            walk(path + [sub], depth + 1)

    for cmd in subcommands(run([])):
        walk([cmd], 1)

    OUT_PATH.write_text('\n'.join(out))
    size_kb = OUT_PATH.stat().st_size / 1024
    print(f"Wrote {OUT_PATH} ({size_kb:.1f} KB) -- {stats['nodes']} nodes, max depth {stats['max_depth']}")
    if size_kb > 2000:
        print("WARNING: output > 2 MB. Runaway suspected -- inspect subcommands() regex.")


if __name__ == '__main__':
    main()
