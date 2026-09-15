#!/usr/bin/env python3
"""Regenerate this skill directory's cli-reference.md exhaustively.

Walks every Hermes subparser recursively (depth 4) and dumps each --help.

Why the careful subcommand parser:
  argparse prints flag value enums (e.g. `--type {oauth,api-key}`) with the same
  `{a,b,c}` shape as real subparser choice lists. A naive regex matches both,
  and walking into a flag enum hits an infinite loop because argparse silently
  ignores unknown positionals and re-prints the same help.

Fix: only treat `{a,b,c}` as subcommands when it appears inside the
`positional arguments:` block AND is followed by an indented `name   description`
listing. Cap depth at 4. Track visited paths.

Expected output size: 300 KB–2 MB. Abort before replacing the reference if
help capture fails or output exceeds 5 MB.
"""
import re
import subprocess
import datetime
import pathlib
import shutil
from concurrent.futures import ThreadPoolExecutor

MAX_DEPTH = 4
TIMEOUT = 20
MAX_BYTES = 5_000_000
OUT_PATH = pathlib.Path(__file__).resolve().parents[1] / 'cli-reference.md'


def run(path):
    hermes = shutil.which('hermes')
    if hermes is None:
        raise SystemExit('hermes executable not found on PATH; existing reference preserved')
    r = subprocess.run([hermes, *path, '--help'], capture_output=True, text=True,
                       timeout=TIMEOUT, check=True)
    return (r.stdout or '') + (r.stderr or '')


def subcommands(help_text):
    """Read only positional subparser listings, including aliases/metavars."""
    lines = help_text.splitlines()
    try:
        start = lines.index('positional arguments:') + 1
    except ValueError:
        return []
    for i in range(start, len(lines)):
        line = lines[i]
        if line and not line[0].isspace():
            break
        header = re.fullmatch(r'  (?:\{([a-zA-Z0-9_,\-]+)\}|<subcommand>|COMMAND)(?:\s*\.\.\.)?\s*', line)
        if not header:
            continue
        declared = header.group(1).split(',') if header.group(1) else None
        listed = []
        j = i + 1
        while j < len(lines):
            row = lines[j]
            if not row.strip() or re.match(r'^ {8,}\S', row):
                j += 1
                continue
            match = re.fullmatch(r' {4}([a-zA-Z0-9_-]+)(?: \(([a-zA-Z0-9_, -]+)\))?(?: {2,}(\S.*))?\s*', row)
            if not match:
                break
            # A bare name is a command row only with a wrapped description.
            if not match.group(3) and not (j + 1 < len(lines) and re.match(r'^ {8,}\S', lines[j + 1])):
                break
            listed.append(match.group(1))
            if match.group(2):
                listed.extend(alias.strip() for alias in match.group(2).split(','))
            j += 1
        if listed and (declared is None or all(name in declared for name in listed)):
            return declared if declared is not None else listed
    return []


def main():
    hermes = shutil.which('hermes')
    if hermes is None:
        raise SystemExit('hermes executable not found on PATH; existing reference preserved')
    ver = subprocess.check_output([hermes, '--version'], text=True, timeout=TIMEOUT).strip()
    root_help = run([])
    root_commands = subcommands(root_help)
    if not root_commands:
        raise SystemExit('No top-level subcommands parsed; existing reference preserved')
    help_cache = {(): root_help}
    pending = [(cmd,) for cmd in root_commands]
    queued = set(pending)
    captured_bytes = len(root_help.encode('utf-8'))
    # Help calls at the same depth are independent. Capture concurrently,
    # then render in stable depth-first order below.
    with ThreadPoolExecutor(max_workers=4) as pool:
        while pending:
            next_paths = []
            for path, help_text in zip(pending, pool.map(run, pending)):
                help_cache[path] = help_text
                captured_bytes += len(help_text.encode('utf-8'))
                if captured_bytes > MAX_BYTES:
                    raise SystemExit('Help capture exceeded 5 MB; existing reference preserved. Inspect parser.')
                if len(path) < MAX_DEPTH:
                    for cmd in subcommands(help_text):
                        child = (*path, cmd)
                        if child not in queued:
                            queued.add(child)
                            next_paths.append(child)
            print(f"Fetched {len(help_cache)} command nodes...", flush=True)
            pending = next_paths
    out = [
        "# Hermes CLI Full Reference",
        f"_Auto-generated {datetime.date.today()} for {ver}_",
        "",
        "## hermes (top-level)",
        "```",
        root_help.rstrip(),
        "```",
    ]

    visited = set()
    command_paths = []
    stats = {'nodes': 1, 'max_depth': 0}
    output_bytes = len('\n'.join(out).encode('utf-8'))

    def walk(path, depth):
        nonlocal output_bytes
        key = ' '.join(path)
        if key in visited or depth > MAX_DEPTH:
            return
        visited.add(key)
        command_paths.append(key)
        stats['nodes'] += 1
        stats['max_depth'] = max(stats['max_depth'], depth)
        help_text = help_cache[tuple(path)]
        hashes = '#' * (depth + 1)
        section = [f"\n{hashes} hermes {' '.join(path)}", "```", help_text.rstrip(), "```"]
        output_bytes += len(('\n' + '\n'.join(section)).encode('utf-8'))
        if output_bytes > MAX_BYTES:
            raise SystemExit('Help capture exceeded 5 MB; existing reference preserved. Inspect parser.')
        out.extend(section)
        for sub in subcommands(help_text):
            walk(path + [sub], depth + 1)

    for cmd in root_commands:
        walk([cmd], 1)

    # A navigable index makes the complete reference useful without searching
    # hundreds of help blocks; aliases receive their own captured help links.
    index = ["## Command index", "", "- [hermes (top-level)](#hermes-top-level)"]
    index.extend(f"- [hermes {path}](#hermes-{path.replace(' ', '-')})" for path in command_paths)
    index.append("")
    out[3:3] = index
    content = '\n'.join(out)
    if not 300_000 <= len(content.encode('utf-8')) <= MAX_BYTES:
        raise SystemExit(f"Unexpected reference size ({len(content.encode('utf-8'))} bytes, {stats['nodes']} nodes); existing reference preserved. Inspect parser.")
    temp_path = OUT_PATH.with_suffix('.md.tmp')
    temp_path.write_text(content, encoding='utf-8')
    temp_path.replace(OUT_PATH)
    size_kb = OUT_PATH.stat().st_size / 1024
    print(f"Wrote {OUT_PATH} ({size_kb:.1f} KB) -- {stats['nodes']} nodes, max depth {stats['max_depth']}")
    if size_kb > 2000:
        print("WARNING: output > 2 MB. Runaway suspected -- inspect subcommands() regex.")


if __name__ == '__main__':
    main()
