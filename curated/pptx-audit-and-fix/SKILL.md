---
name: pptx-audit-and-fix
description: "Audit and fix PowerPoint (.pptx) layout issues directly on files using python-pptx. No PowerPoint app needed. 5-phase audit: (1) structural scan for overlaps and out-of-bounds shapes, (2) text truth check for hidden overflow via font metrics, (3) visual/readability audit for font size and contrast, (4) layout consistency for margins and spacing, (5) composition coverage detection — flags overlay shapes blocking full-bleed background images (>30% single shape = WARNING, >50% combined = CRITICAL). Auto-fixes text box sizing, font sizes, empty placeholders, and vertical reflow. Use when: (1) User wants to check a .pptx for layout problems, (2) User asks to fix or clean up a PowerPoint file, (3) After creating/editing a presentation to validate quality, (4) User says 'audit pptx', 'fix pptx', 'check my slides', or similar."
---

# PPTX Audit & Fix Skill

Standalone Python tool for auditing and fixing PowerPoint layout issues directly on `.pptx` files. No PowerPoint application needed.

## Dependencies

```bash
pip install python-pptx Pillow lxml
```

## How to Use

The complete audit tool is at `references/pptx_audit.py` in this skill directory. Use it as follows:

### Option 1: As a Python module (recommended for Claude Code)

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

### Option 2: As a CLI tool

```bash
# Audit only (report)
python ~/.claude/skills/pptx-audit-and-fix/references/pptx_audit.py deck.pptx

# Audit + fix
python ~/.claude/skills/pptx-audit-and-fix/references/pptx_audit.py deck.pptx --fix

# Audit + fix with custom output
python ~/.claude/skills/pptx-audit-and-fix/references/pptx_audit.py deck.pptx --fix --output deck_fixed.pptx
```

## What It Detects (5 Phases)

### Phase 1 — Structural Scan
- Shape-on-shape overlaps (using stored bounding boxes)
- Shapes extending beyond slide boundaries
- Decorative lines cutting through text

### Phase 2 — Text Truth Check (Key Innovation)
- Estimates TRUE rendered text height using font metrics
- Finds HIDDEN overlaps where text overflows its box but the box dimensions haven't updated
- This catches the #1 most common layout bug in PowerPoint

### Phase 3 — Visual & Readability Audit
- Font sizes below 14pt threshold
- Low contrast text (WCAG luminance calculation)
- Red text on dark backgrounds (low luminance warning)

### Phase 4 — Layout Consistency
- Shapes too close to slide edges (< 36pt margin)
- Uneven vertical spacing rhythm
- Empty/unused text placeholders

### Phase 5 — Composition Coverage
- Detects overlay shapes that block too much of a full-bleed background image
- Single shape covering >30% of slide area: WARNING
- Combined overlays covering >50% of slide area: CRITICAL
- Helps catch design issues where cards/scrims hide the BG image's focal content

## What It Fixes Automatically
- Text boxes resized to fit content (only significant overflows >8pt — small ones PowerPoint handles)
- **Iterative vertical reflow** after resizing: all shapes below a resized box cascade down to prevent new overlaps
- Font sizes increased to minimum 14pt
- Empty placeholders deleted

## Fix Engine Architecture
The fix runs in 4 ordered passes:
1. **Font size fixes** (no layout side effects)
2. **Empty placeholder deletion** (no layout side effects)
3. **Text box resizing** (only overflows > `MIN_OVERFLOW_FIX_PT` = 8pt)
4. **Vertical reflow** per affected slide — iteratively resolves all overlaps by nudging shapes down, checking horizontal overlap to avoid moving unrelated shapes. Max 20 iterations.

## What Requires Manual Review
- Contrast fixes (scrim overlays / color changes need design decisions)
- Cross-slide alignment (needs context about intentional vs accidental)

## Severity Levels
- **CRITICAL** — Will be visible to audience (overlaps, overflow, tiny fonts, very low contrast)
- **WARNING** — Likely problematic (text overflow, borderline font sizes, moderate contrast)
- **INFO** — Style suggestions (margins, spacing, unused shapes)

## Known Issues & Workarounds (Session Learnings)

### 1. `fix_all()` cascading reflow can push content off-slide
The auto-fix engine nudges shapes down to resolve overlaps, but on dense slides this cascade can push the bottom card/content past the 540pt slide boundary. **Workaround:** For dense slides, do NOT use `fix_all()`. Instead, manually reflow using python-pptx:
- Keep original box heights (PowerPoint renders text more compactly than the estimator predicts)
- Only fix positions/spacing, not heights
- Widen text boxes to reduce line wrapping instead of increasing height

### 2. Text height estimator overestimates by ~30%
The `estimate_text_height()` function adds +8pt padding and uses LINE_HEIGHT_RATIO=1.25, which consistently overestimates. For a 14pt font with 2 lines, it estimates ~43pt but PowerPoint renders in ~32pt. For 40pt font (2 lines), it estimates ~108pt but PowerPoint renders in ~96pt. **Impact:** The audit flags many "hidden overlaps" that don't actually exist visually. When manually fixing, trust PowerPoint's stored heights more than the estimates — only add 5-10pt gap between elements, not the full estimate.

### 3. Multi-line title boxes need special attention
A 40pt font title wrapping to 2 lines needs ~96pt height, but the stored box is often only ~58pt. PowerPoint still renders the text visually beyond the box edge. **Fix:** Manually expand the title box height to accommodate 2 lines at the font size (`font_pt * 2.4` is a good rule of thumb), then reflow everything below.

### 4. Color/opacity issues not detected by audit
The audit tool checks contrast ratios but misses:
- **Alpha transparency on text** — `<a:alpha val="55000"/>` makes text 55% transparent, invisible on dark backgrounds
- **Gray text on dark overlay backgrounds** — `#757575` on `#0A0A0A` at 80% opacity is nearly invisible
- **Card background opacity** — Cards filled with `#0A0A0A` at 80%+ opacity block background photos

**Manual fixes needed:**
- Remove alpha elements from text: `shape._element.findall('.//a:alpha', ns)` → remove
- Change gray `#757575` description text to white `#FFFFFF` for dark backgrounds
- Adjust card background opacity via `fill_alpha.set('val', '50000')` for better photo visibility
- Update both run-level color AND `defRPr` color (paragraph default) for consistency

### 5. Recommended manual fix workflow for dense slides
```python
# 1. Read from ORIGINAL file (not accumulated fixes)
prs = Presentation("original.pptx")

# 2. Keep original box heights — they work in PowerPoint
# 3. Widen narrow text boxes to prevent wrapping (saves vertical space)
shape.width = Pt(500)  # was 396

# 4. Reflow top-down with zero or minimal gaps
y = Pt(28)  # start position
for shape in shapes_top_to_bottom:
    shape.top = int(y)
    y = shape.top + shape.height + Pt(1)  # 1pt gap

# 5. Fix colors/opacity separately
for run in shape.text_frame.paragraphs[0].runs:
    run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
```

## Integration with pptx-design-agent

When using this skill after creating/editing slides with the `pptx-design-agent` skill:
1. Run the audit on the output file
2. Review the report for CRITICAL and WARNING issues
3. **For sparse slides (< 8 text shapes):** Apply auto-fixes with `fix_all()`
4. **For dense slides (8+ text shapes):** Use manual reflow (see Known Issues #5)
5. Manually address color/opacity issues (see Known Issues #4)
6. Save the fixed version

## Limitations vs PowerPoint Add-in
- **Text height**: Estimated via font metrics (~70% accurate — overestimates by ~30%) vs exact from PowerPoint renderer
- **Visual verification**: No screenshot/AI review available — user screenshot feedback is essential for validating fixes
- **Scrim overlays**: Injected as raw OOXML via lxml
- **Color/opacity**: Audit detects contrast issues but doesn't fix alpha transparency or card overlay opacity
- **Dense slides**: Auto-fix reflow can cascade content off-slide; manual reflow recommended
