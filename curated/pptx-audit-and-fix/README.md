# pptx-audit-and-fix

A Claude Code skill for auditing and fixing PowerPoint (.pptx) layout issues directly on files using python-pptx. No PowerPoint application needed.

## What It Does

4-phase audit that detects common layout bugs, plus an auto-fix engine that resolves what it can:

| Phase | Focus | Detects |
|-------|-------|---------|
| **1. Structural Scan** | Shape geometry | Overlaps, boundary violations, decorative lines cutting through text |
| **2. Text Truth Check** | Hidden overflows | Text that overflows its box but PowerPoint hasn't updated the box dimensions |
| **3. Visual & Readability** | Contrast & fonts | Font sizes below 14pt, low contrast text (WCAG), red-on-dark warnings |
| **4. Layout Consistency** | Margins & spacing | Shapes too close to edges, uneven vertical spacing, empty placeholders |

### Auto-Fix Engine

Runs in 4 ordered passes:

1. **Font size fixes** — increase to minimum 14pt
2. **Empty placeholder deletion**
3. **Text box resizing** — only significant overflows (>8pt)
4. **Vertical reflow** — iteratively cascades shapes down to prevent new overlaps (max 20 iterations)

Issues requiring design decisions (contrast fixes, cross-slide alignment) are flagged for manual review.

## Requirements

- **Python 3** with `python-pptx`, `Pillow`, and `lxml`

```bash
pip install python-pptx Pillow lxml
```

## Installation

Copy the `pptx-audit-and-fix/` folder into your Claude Code skills directory:

```bash
cp -r pptx-audit-and-fix ~/.claude/skills/
```

## Usage

### As a Python module

```python
from pptx_audit import PptxAuditor

auditor = PptxAuditor("presentation.pptx")
report = auditor.run_full_audit()
print(report)

# Apply automatic fixes
auditor.fix_all(report)
auditor.save("presentation_fixed.pptx")
```

### As a CLI tool

```bash
# Audit only
python pptx_audit.py deck.pptx

# Audit + fix
python pptx_audit.py deck.pptx --fix

# Audit + fix with custom output
python pptx_audit.py deck.pptx --fix --output deck_fixed.pptx
```

## Severity Levels

- **CRITICAL** — Visible to audience (overlaps, overflow, tiny fonts, very low contrast)
- **WARNING** — Likely problematic (borderline font sizes, moderate contrast)
- **INFO** — Style suggestions (margins, spacing, unused shapes)

## Known Limitations

- **Text height estimation** overestimates by ~30% (font metrics vs PowerPoint renderer) — trust PowerPoint's stored heights for manual fixes
- **Dense slides (8+ shapes)** — auto-fix reflow can cascade content off-slide; use manual reflow instead
- **Color/opacity** — detects contrast issues but doesn't fix alpha transparency or card overlay opacity
- **No visual verification** — operates on XML structure only, no screenshot/AI review

## Integration with pptx-design-agent

Use after creating slides with the [pptx-design-agent](../pptx-design-agent/) skill:

1. Run audit on the output file
2. Review CRITICAL and WARNING issues
3. Sparse slides (< 8 shapes): apply `fix_all()`
4. Dense slides (8+ shapes): use manual reflow
5. Address color/opacity issues manually
