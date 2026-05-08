#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Translate i18n/en.json into other languages via the configured LLM (gog).

Reads each key/value, ships them in a single LLM call per language with a
brand-tone-preserving prompt, writes <lang>.json.

Usage:
  uv run i18n_translate.py <i18n/en.json> --langs zh,ja,es,fr,ko,ru
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


LANG_NAMES = {
    'zh': '简体中文 (Simplified Chinese)',
    'ja': '日本語 (Japanese)',
    'ko': '한국어 (Korean)',
    'es': 'Español (Spanish)',
    'fr': 'Français (French)',
    'ru': 'Русский (Russian)',
    'de': 'Deutsch (German)',
    'pt': 'Português (Portuguese)',
    'it': 'Italiano (Italian)',
    'ar': 'العربية (Arabic)',
    'he': 'עברית (Hebrew)',
}


PROMPT_TMPL = """You are translating UI strings from English to {target_name}.

Critical rules:
- Preserve brand voice (intimate, editorial, after-hours — not corporate).
- Keep first-person singular if the original uses it (I/my, not we/our).
- Translate idioms culturally, not literally ("after hours" is the *feeling* of off-the-clock intimacy).
- Keep proper nouns untranslated unless they have a canonical localised form.
- Preserve punctuation rhythm (em dashes, ellipses, line breaks) where they carry weight.
- Output ONLY a JSON object with the same keys, translated values. No markdown, no commentary.

English JSON:
{src_json}

Output the {target_name} JSON now:"""


def translate_via_gog(en_data: dict, lang: str) -> dict:
    target_name = LANG_NAMES.get(lang, lang)
    prompt = PROMPT_TMPL.format(target_name=target_name, src_json=json.dumps(en_data, ensure_ascii=False, indent=2))
    # Use `gog` if available; otherwise emit error so caller can paste prompt into another LLM.
    if shutil.which('gog'):
        # gog has no built-in "ask LLM" — fall back to a generic LLM CLI.
        pass
    if shutil.which('llm'):
        result = subprocess.run(['llm', '-m', 'gpt-4o-mini', prompt], capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            text = result.stdout.strip()
            # Strip code fences if present
            if text.startswith('```'):
                text = '\n'.join(text.splitlines()[1:-1])
            return json.loads(text)
        print(f'llm CLI failed: {result.stderr}', file=sys.stderr)
    raise SystemExit(
        'No LLM CLI available. Install `llm` (https://llm.datasette.io/) or '
        'run translation manually: paste the prompt below into your LLM, save '
        f'output as <lang>.json:\n\n---\n{prompt}\n---'
    )


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('en_json', type=Path)
    p.add_argument('--langs', required=True, help='Comma-separated language codes, e.g. zh,ja,es')
    p.add_argument('--out-dir', type=Path, help='Defaults to en_json.parent')
    args = p.parse_args()

    en_data = json.loads(args.en_json.read_text())
    out_dir = args.out_dir or args.en_json.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    for lang in [l.strip() for l in args.langs.split(',') if l.strip()]:
        if lang == 'en':
            continue
        print(f'Translating to {LANG_NAMES.get(lang, lang)}…')
        try:
            translated = translate_via_gog(en_data, lang)
        except SystemExit as e:
            print(e, file=sys.stderr)
            return 1
        target = out_dir / f'{lang}.json'
        target.write_text(json.dumps(translated, ensure_ascii=False, indent=2) + '\n')
        print(f'  ✓ {target}')

    return 0


if __name__ == '__main__':
    sys.exit(main())
