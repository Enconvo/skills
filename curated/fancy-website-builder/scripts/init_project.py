#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Initialize a new fancy-website-builder project from a chosen shell.

Steps:
1. Copy assets/shells/<shell>/ into <output_dir>/.
2. Apply palette.json (if provided) — rewrites --brand-1..5 in inline <style>.
3. Set up i18n/<lang>.json files for every requested language (zh/ja/etc. start as copies of en.json — translate later with i18n_translate.py).
4. Update window.__I18N_LANGS__ in index.html.

Usage:
  uv run init_project.py <output_dir> --shell editorial-nightscape \\
      [--palette palette.json] [--langs en,zh,ja] [--hero A]
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parent.parent


def apply_palette(html_path: Path, palette: dict[str, str]) -> None:
    text = html_path.read_text()
    for k, v in palette.items():
        # palette.json keys look like "brand_1", CSS uses --brand-1
        css_var = '--' + k.replace('_', '-')
        text = re.sub(
            rf'({re.escape(css_var)}\s*:\s*)[^;]+;',
            rf'\1{v};',
            text,
            count=1,
        )
    html_path.write_text(text)


def set_supported_langs(html_path: Path, langs: list[str]) -> None:
    arr = '[' + ', '.join(f"'{l}'" for l in langs) + ']'
    text = html_path.read_text()
    text = re.sub(
        r"window\.__I18N_LANGS__\s*=\s*window\.__I18N_LANGS__\s*\|\|\s*\[[^\]]*\];",
        f"window.__I18N_LANGS__ = {arr};",
        text,
    )
    html_path.write_text(text)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('output_dir', type=Path)
    p.add_argument('--shell', required=True, help='Shell name (folder under assets/shells/)')
    p.add_argument('--palette', type=Path, help='palette.json from extract_palette.py')
    p.add_argument('--langs', default='en', help='Comma-separated language codes, e.g. en,zh,ja')
    p.add_argument('--hero', help='Hero variant id (A/B/C/D/E/F). If omitted, shell default is kept.')
    args = p.parse_args()

    shell_src = SKILL_DIR / 'assets' / 'shells' / args.shell
    if not shell_src.exists():
        print(f'Shell not found: {shell_src}', file=sys.stderr)
        print(f'Available shells: {[p.name for p in (SKILL_DIR / "assets/shells").iterdir() if p.is_dir()]}', file=sys.stderr)
        return 1

    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Copy shell
    for item in shell_src.iterdir():
        dst = args.output_dir / item.name
        if item.is_dir():
            shutil.copytree(item, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(item, dst)
    print(f'✓ Copied shell "{args.shell}" → {args.output_dir}')

    html_path = args.output_dir / 'index.html'

    # Apply palette
    if args.palette and args.palette.exists():
        palette = json.loads(args.palette.read_text())
        apply_palette(html_path, palette)
        print(f'✓ Applied palette from {args.palette}')

    # Set up i18n
    langs = [l.strip() for l in args.langs.split(',') if l.strip()]
    if 'en' not in langs:
        langs.insert(0, 'en')
    i18n_dir = args.output_dir / 'i18n'
    i18n_dir.mkdir(exist_ok=True)
    en_json = i18n_dir / 'en.json'
    if not en_json.exists():
        # shell didn't ship one — create empty
        en_json.write_text('{}\n')
    en_data = en_json.read_text()
    for lang in langs:
        if lang == 'en':
            continue
        target = i18n_dir / f'{lang}.json'
        if not target.exists():
            target.write_text(en_data)
            print(f'  · Created {target.name} (copied from en.json — translate before shipping)')
    set_supported_langs(html_path, langs)
    print(f'✓ i18n langs: {", ".join(langs)}')

    if args.hero:
        print(f'  · Hero variant: {args.hero} — replace <script id="hero-technique"> manually from references/hero-shaders.md')

    print(f'\nNext steps:')
    print(f'  1. cd {args.output_dir} && python3 -m http.server 7531')
    print(f'  2. open http://127.0.0.1:7531/')
    if len(langs) > 1:
        print(f'  3. uv run {SKILL_DIR}/scripts/i18n_translate.py {args.output_dir}/i18n/en.json --langs {",".join(l for l in langs if l != "en")}')

    return 0


if __name__ == '__main__':
    sys.exit(main())
