---
name: pptx-audit
description: "Deterministic structural audit for PowerPoint .pptx files via a Python script. Runs 14 checks (bounds, text overflow, word-wrap, container-text sync, overlap, z-order, font compliance, image AR distortion, blue-rectangle gradient bug, text-zone luminance, etc.), returns JSON, and exits non-zero on CRITICAL issues. Use when: (1) pptx-design hands off a freshly built deck for delivery gating, (2) auditing a .pptx received from someone else, (3) verifying a .pptx after manual fixes. Trigger words: 'audit pptx', 'check pptx', 'verify pptx', 'lint pptx', 'pptx-audit'."
---

# pptx-audit — Deterministic Audit Gate for PowerPoint Decks

The verification half of the `pptx-design` skill set. **`pptx-design` builds; `pptx-audit` verifies.**

This skill exists because instructions alone don't make weaker LLMs run the audit thoroughly. The script does the work; the agent only has to call it and paste the result.

## When to use

- **Mandatory after any `pptx-design` build, redesign, or multi-slide edit.** No exceptions.
- Auditing a third-party .pptx (client deck, handover) — same script, same output.
- Re-running after an agent fix to confirm CRITICAL count went down.

## When NOT to use

- Single-property tweaks (one font change, one color swap on one slide). The script is fast (~1–3s per deck), so running it anyway is cheap, but `pptx-design` doesn't gate on it.
- Decks that aren't on disk yet — the script reads a saved `.pptx`. Save first.

## Usage

```bash
python3 ~/.claude/skills/pptx-audit/scripts/audit.py /abs/path/to/deck.pptx
```

With an active design style (enables CHECK 11 — STYLE COMPLIANCE):

```bash
python3 ~/.claude/skills/pptx-audit/scripts/audit.py /abs/path/to/deck.pptx --style STYLE-02
```

Stricter mode (treat WARNINGs as fails too):

```bash
python3 ~/.claude/skills/pptx-audit/scripts/audit.py /abs/path/to/deck.pptx --fail-on warning
```

Exit codes:
- `0` — no CRITICAL issues (or no CRITICAL/WARNING with `--fail-on warning`)
- `1` — CRITICAL issues present
- `2` — script error (bad path, missing deps, malformed pptx)

## Output (always JSON to stdout)

```json
{
  "path": "/abs/path/to/deck.pptx",
  "style": "STYLE-02" or null,
  "summary": {"critical": 0, "warning": 2, "info": 1, "passed": true},
  "critical": [],
  "warning": [
    {"check": 2, "slide": 1, "shape": "TextBox 2", "severity": "WARNING",
     "msg": "Estimated text height 113.4pt > frame height 78.7pt (lines=2, font=42pt)..."}
  ],
  "info": [...]
}
```

## How the calling agent should use this

**Required workflow when invoked from `pptx-design` for delivery gating:**

1. Run the script. Capture the full JSON.
2. **Paste the JSON `summary` block verbatim** in the response. No paraphrasing.
3. Decide based on the script's exit code:
   - **Exit 0** → audit passed. Proceed to visual verification (PDF render + PNG inspection — see `pptx-design`'s "Visual verification" workflow). Then deliver.
   - **Exit 1** → CRITICAL present. **Do not deliver.** Triage each CRITICAL using `references/audit-checks.md`. Apply fixes via `python-pptx`. Re-run `audit.py`. Loop up to 5 times.
4. After 5 failed passes, escalate: report the remaining CRITICALs to the user and ask for guidance. Do not silently deliver.

**Required workflow when invoked standalone** (e.g., user says "audit this deck"):

1. Run the script.
2. Print the `summary` line.
3. List each CRITICAL with slide + check number + message.
4. List WARNINGs in a collapsed/short form.
5. Offer: "Want me to fix the CRITICALs?" — only apply fixes after the user agrees.

## Triage before fixing

The script is **deterministic but conservative** — most flagged CRITICALs are real, but a few false-positive patterns persist. Before applying fixes:

- **CHECK 2 (text clipping)** is an estimate, not ground truth. The line-height ratio overshoots ~30% in practice. If a CHECK 2 issue says "estimated 113pt > 78pt" with only 2 lines at 42pt, render the slide to PNG (via `pdftoppm` per `pptx-design`'s `applescript-patterns.md`) and look before fixing.
- **CHECK 7 (z-order)** uses bbox math; transparency-aware fill checking is not yet implemented. A "covered by 100%" warning on a transparent fill is a false positive.
- **CHECK 9 (spacing)** is INFO only. Apply judgement — staggered/masonry layouts are intentional.

For known false-positive patterns and triage rules, see `references/audit-checks.md`.

## Coverage map

| Check | What it catches | Severity | Coverage |
|---|---|---|---|
| 1 BOUNDS | Shapes off-slide | CRITICAL | full |
| 2 TEXT CLIPPING | Vertical text overflow | WARNING | full (estimator) |
| 3 WORD-WRAP | Long words wider than frame | CRITICAL/WARNING | full |
| 4 CONTAINER SYNC | Text overflows its parent card | CRITICAL | full |
| 5 BULLET ALIGNMENT | Misaligned bullet dots | WARNING | minimal (column variance only) |
| 6 OVERLAP | Independent text shapes colliding | WARNING | full |
| 7 Z-ORDER | Opaque shape covers text | CRITICAL | minimal (bbox + opacity-naive) |
| 8 FONT COMPLIANCE | Sub-14pt fonts, missing font.name/size | CRITICAL/WARNING | full |
| 9 SPACING | Cross-slide left-margin variance | INFO | minimal |
| 10 COLOR INTEGRITY | Orphan accent1 theme fills | WARNING | minimal |
| 11 STYLE COMPLIANCE | Off-style fonts/colors (when --style passed) | WARNING | minimal (3 styles encoded) |
| 12 IMAGE AR DISTORTION | Stretched/squished images | CRITICAL/WARNING | full |
| 13 BROKEN GRADIENTS | "Blue rectangle" theme fallback bug | CRITICAL | full |
| 14 TEXT ZONE LUMINANCE | Unreadable text over BG image | CRITICAL | full (when shape annotated) |

"Minimal" coverage flags only high-confidence cases to avoid false-positive noise. The full check spec lives in `references/audit-checks.md`.

## Dependencies

```bash
python3 -m pip install python-pptx lxml Pillow
```

Pillow is required for CHECK 12 (image AR) and CHECK 14 (luminance). The script gracefully degrades if Pillow is missing — those checks return INFO with the install hint.

## Limitations

- **Detection only, no auto-fix.** The script reports issues; the agent applies fixes via `python-pptx`. Future v2 may add `--fix` for trivial cases.
- **No visual rendering.** Some bugs only show up in the rendered slide (text on a busy photo, color collisions on a multi-tone background). Always pair with `pdftoppm` PNG inspection per `pptx-design`'s visual-verification workflow.
- **CHECK 11 only knows 3 styles** (STYLE-01, 02, 03). Add entries to `_STYLE_DICTS` in `audit.py` to enforce others.
- **CHECK 5 is conservative.** Strict bullet line-count layout validation is too noisy without a reliable bullet detector — left to the agent.

## See also

- `~/.claude/skills/pptx-design/SKILL.md` — the build half of the pair; calls this skill before delivery.
- `references/audit-checks.md` — full check definitions, fix strategies, false-positive guidance, key lessons learned.
