# pptx-audit

Deterministic structural audit for PowerPoint `.pptx` files. The verification half of the `pptx-design` skill set — `pptx-design` builds, `pptx-audit` verifies.

## Why this exists

Instructions alone don't make weaker LLMs run the audit thoroughly. This skill replaces the agent-driven "MUST audit before delivery" prompt rule with a **deterministic Python script** that the agent invokes and whose JSON output it must paste before delivery. The script does the work; the agent only has to call it.

## What it checks

14 structural checks, each documented in `references/audit-checks.md`:

| # | Check | Severity | Catches |
|---|---|---|---|
| 1 | BOUNDS | CRITICAL | shapes off-slide |
| 2 | TEXT CLIPPING | WARNING | vertical text overflow |
| 3 | WORD-WRAP QUALITY | CRITICAL | long words wider than frame |
| 4 | CONTAINER-TEXT SYNC | CRITICAL | text overflows its parent card |
| 5 | BULLET ALIGNMENT | WARNING | misaligned bullet dots |
| 6 | OVERLAP | WARNING | independent text shapes colliding |
| 7 | Z-ORDER | CRITICAL | opaque shape covering text |
| 8 | FONT COMPLIANCE | CRITICAL/WARNING | sub-14pt fonts, missing font.name |
| 9 | SPACING CONSISTENCY | INFO | cross-slide left-margin variance |
| 10 | COLOR/FILL INTEGRITY | WARNING | orphan accent1 theme fills |
| 11 | STYLE COMPLIANCE | WARNING | off-style fonts/colors (when --style passed) |
| 12 | IMAGE AR DISTORTION | CRITICAL | stretched/squished images |
| 13 | BROKEN GRADIENTS | CRITICAL | "blue rectangle" theme fallback bug |
| 14 | TEXT ZONE LUMINANCE | CRITICAL | unreadable text over BG image |

## Usage

```bash
# Basic
python3 ./scripts/audit.py /abs/path/to/deck.pptx

# With active style (enables CHECK 11)
python3 ./scripts/audit.py /abs/path/to/deck.pptx --style STYLE-02

# Stricter (treat WARNINGs as fails too)
python3 ./scripts/audit.py /abs/path/to/deck.pptx --fail-on warning
```

**Exit codes:**
- `0` — no CRITICAL issues
- `1` — CRITICAL issues present
- `2` — script error (bad path, missing deps, malformed pptx)

## Output (always JSON to stdout)

```json
{
  "path": "/abs/path/to/deck.pptx",
  "style": "STYLE-02" or null,
  "summary": {"critical": 0, "warning": 2, "info": 1, "passed": true},
  "critical": [],
  "warning": [{"check": 2, "slide": 1, "shape": "TextBox 2", "msg": "..."}],
  "info": [...]
}
```

## How `pptx-design` uses it

`pptx-design`'s SKILL.md has a front-loaded "DELIVERY GATE" block that instructs the building agent to:

1. Run this script before reporting completion.
2. Paste the JSON `summary` block verbatim.
3. If `passed: false`, fix CRITICALs using `python-pptx` and re-run, looping up to 5 times.
4. After 5 failed passes, escalate to user — never silently deliver.

## Dependencies

```bash
python3 -m pip install python-pptx lxml Pillow
```

Pillow is required for CHECK 12 (image AR) and CHECK 14 (luminance). The script gracefully degrades if Pillow is missing — those checks return INFO with the install hint.

## Limitations

- **Detection only, no auto-fix.** v1 reports issues; the building agent applies fixes via `python-pptx`. v2 may add `--fix` for trivial cases.
- **No visual rendering.** Some bugs only show in the rendered slide (text on a busy photo, color collisions on multi-tone backgrounds). Pair with `pdftoppm` PNG inspection per `pptx-design`'s visual-verification workflow.
- **CHECK 11 only knows 3 styles** (STYLE-01, 02, 03). Add entries to `_STYLE_DICTS` in `audit.py` to enforce others.
- **CHECK 5 is conservative** — strict bullet line-count layout validation is too noisy without a reliable bullet detector; left to the agent.
- **Conservative on false positives.** Some checks ("~" coverage in `SKILL.md`) flag only high-confidence cases to avoid the audit-credibility-killing false positives the original `audit-system.md` warned about.

## See also

- `SKILL.md` — full usage docs, triage rules, coverage map
- `references/audit-checks.md` — full check definitions, fix strategies, false-positive guidance, key lessons learned
- `../pptx-design/` — the build half of the pair
