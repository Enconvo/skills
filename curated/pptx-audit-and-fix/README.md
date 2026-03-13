# pptx-audit-and-fix

Standalone Python tool for auditing and fixing PowerPoint (.pptx) layout issues directly on files. No PowerPoint application needed.

## Features

- **5-phase audit** covering structural, text, visual, layout, and composition issues
- **Auto-fix engine** with iterative vertical reflow to prevent cascading overlaps
- **No PowerPoint required** — works entirely with python-pptx and lxml
- **CLI and Python API** — use from command line or import as a module

## 5 Audit Phases

| Phase | What it checks |
|-------|---------------|
| **1. Structural Scan** | Shape-on-shape overlaps, out-of-bounds shapes, decorative lines cutting through text |
| **2. Text Truth Check** | Estimates true rendered text height via font metrics — catches hidden overflow where text spills beyond its box |
| **3. Visual & Readability** | Font sizes below 14pt, low contrast text (WCAG luminance), red-on-dark warnings |
| **4. Layout Consistency** | Shapes too close to edges (<36pt margin), uneven vertical spacing, empty placeholders |
| **5. Composition Coverage** | Overlay shapes blocking full-bleed BG images — single shape >30% = WARNING, combined >50% = CRITICAL |

## Auto-Fix Capabilities

- Text boxes resized to fit content (overflows >8pt)
- Iterative vertical reflow after resizing — cascades shapes down to prevent new overlaps
- Font sizes increased to minimum 14pt
- Empty placeholders deleted

## Requirements

```bash
pip install python-pptx Pillow lxml
```

## Usage

### CLI

```bash
# Audit only (report)
python ~/.claude/skills/pptx-audit-and-fix/references/pptx_audit.py deck.pptx

# Audit + fix
python ~/.claude/skills/pptx-audit-and-fix/references/pptx_audit.py deck.pptx --fix

# Audit + fix with custom output
python ~/.claude/skills/pptx-audit-and-fix/references/pptx_audit.py deck.pptx --fix --output deck_fixed.pptx
```

### Python API

```python
import sys
sys.path.insert(0, "~/.claude/skills/pptx-audit-and-fix/references")
from pptx_audit import PptxAuditor

auditor = PptxAuditor("presentation.pptx")
report = auditor.run_full_audit()
print(report)

# Apply automatic fixes
auditor.fix_all(report)
auditor.save("presentation_fixed.pptx")
```

## Severity Levels

- **CRITICAL** — Visible to audience (overlaps, overflow, tiny fonts, BG image mostly hidden)
- **WARNING** — Likely problematic (text overflow, borderline fonts, single overlay >30%)
- **INFO** — Style suggestions (margins, spacing, unused shapes)

## Skill Structure

```
pptx-audit-and-fix/
├── README.md            # This file
├── skill.md             # Skill configuration and documentation
└── references/
    └── pptx_audit.py    # Complete audit + fix tool (CLI + Python API)
```

## Limitations

- **Text height**: Estimated via font metrics (~90% accurate) vs exact from PowerPoint renderer
- **Visual verification**: No screenshot/AI review — structural analysis only
- **Composition coverage**: Detects overlay area ratios but cannot assess whether the BG image focal point is blocked

## License

MIT
