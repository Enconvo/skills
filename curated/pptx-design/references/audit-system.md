# Post-Generation Audit System

## Table of Contents

1. [Cascading Fix Problem](#cascading-fix-problem)
2. [Checks 1-13](#check-1-bounds)
3. [Word-Wrap Simulation](#word-wrap-simulation)
4. [Iterative Fix Loop](#iterative-fix-loop)
5. [Fix Strategies](#fix-strategies)
6. [Bullet List Layout Algorithm](#bullet-list-layout-algorithm)
7. [False Positive Avoidance](#false-positive-avoidance)
8. [Output Format](#output-format)
9. [Key Lessons Learned](#key-lessons-learned)

---

## Cascading Fix Problem

Fixing one issue often creates another. This is the #1 reason audits fail:
- Widening a text box to fix word-wrap → breaks container alignment (CHECK 4)
- Widening a container → may push it off-slide (CHECK 1)
- Resizing containers → may cause overlap with adjacent elements (CHECK 6)
- Fixing bullet text height → changes spacing for all items below (CHECK 5)

**The iterative loop is NON-NEGOTIABLE. A single-pass audit is useless.**

---

## CHECK 1: BOUNDS
```
For every shape on every slide:
  - shape.left >= 0
  - shape.top >= 0
  - shape.left + shape.width <= slide_width  (tolerance: 15000 EMU / ~0.016")
  - shape.top + shape.height <= slide_height  (tolerance: 15000 EMU / ~0.016")
```

## CHECK 2: TEXT CLIPPING (vertical overflow)
```
For every text frame:
  - Simulate word-wrap to get actual line count (see WRAP SIMULATION below)
  - Estimated height = num_lines × font_size_emu × 1.35
  - FLAG if estimated_height > text_frame.height × 1.1
```

## CHECK 3: WORD-WRAP QUALITY (horizontal — #1 cause of ugly slides)
```
For every text frame:
  - Find the longest single word in the text
  - Estimate its rendered width: len(word) × font_size_emu × char_width_factor × safety_margin
  - char_width_factor (EMU-based, multiply by font_size_emu):
      - 0.62 for bold slab-serif/bold (Rockwell Bold, Georgia Bold)
      - 0.57 for regular serif (Georgia, Times New Roman)
      - 0.58 for sans-serif (Arial, Calibri)
      - 0.60 for monospaced (Consolas) — fixed-width, wider average
      - 0.63 for heavy sans (Arial Black, Comic Sans MS Bold)
      - 0.59 for casual/hand (Comic Sans MS Regular)
      - 0.50 for condensed fonts
  - safety_margin: 1.12
  - FLAG CRITICAL if word_width > text_frame.width
  - FLAG WARNING if word_width > text_frame.width × 0.96 and len(word) > 5
```

**Common long-word offenders**: "Optimization", "Development", "Infrastructure", "Transformation", "Implementation", "Organization", "Acceleration", "Sustainability", "Self-optimizing", "cross-functional"

## CHECK 4: CONTAINER-TEXT SYNC ⚠️ CRITICAL FOR DIAGRAMS

The **#1 bug after applying fixes**: a text box gets resized but its parent container stays the same size, causing text to visually overflow its card/node.

```
For every parent-child pair (container shape + text box inside it):
  - Identify pairs: text_box center is inside container bounds
  - text_box.left >= container.left + padding (min 0.04")
  - text_box.top >= container.top + padding
  - text_box.left + text_box.width <= container.left + container.width - padding
  - text_box.top + text_box.height <= container.top + container.height - padding

Fix strategy (in order):
  1. Grow container to wrap text box + padding
  2. If container would go off-slide → shrink text box font (min 14pt)
  3. If font at minimum → re-center text box inside container, accept slight text reduction
```

## CHECK 5: BULLET/LIST ALIGNMENT ⚠️ CRITICAL FOR SIDE PANELS

Bullet lists implemented as dot-shape + text-box pairs have THREE common bugs:
1. **Dot not aligned with first line of text** — dot should center on first line's vertical center
2. **Text boxes oversized** — height set for 3 lines when text only wraps to 2, creating invisible overlap
3. **Spacing is "cramped"** — gaps between items are tiny because text box height includes unused space

```
Detection:
  - Find groups of small shapes (W < 0.15" and H < 0.15") near text boxes
  - Filter to only shapes within the SAME container/panel

For each bullet item (dot + text pair):
  1. Simulate wrap to get TRUE line count
  2. text_box.height = lines × font_size × 1.35  (EXACT, no padding)
  3. Stack items sequentially:
     item[n+1].top = item[n].top + item[n].height + gap
     gap = 0.14" to 0.20" (MUST be consistent)
  4. Dot positioning:
     dot.center_y = text.top + (font_size × 1.35 × 0.42)
     dot.left = consistent across all bullets (within 5000 EMU)
  5. Text box left = consistent across all bullets (within 5000 EMU)
  6. Resize parent container to fit: last_item.bottom + bottom_padding
```

## CHECK 6: OVERLAP CLASSIFICATION
```
For overlapping shape pairs, classify:
  - INTENTIONAL parent-child: text inside container shape → SKIP
  - INTENTIONAL layered UI: footer bar + footer text, accent bar → SKIP
  - INTENTIONAL image-bg stack: full-slide image + overlay + text → SKIP
  - UNINTENTIONAL: two independent text shapes colliding → FLAG

Detection: for each pair of shapes, check if bounding boxes overlap by >10%.
Skip pairs where one is clearly inside the other (parent-child).
Skip full-slide-sized shapes (image backgrounds) and their overlay shapes.
```

## CHECK 7: Z-ORDER
```
Verify no opaque fill shape is layered above a text shape it covers by >30% area.
```

## CHECK 8: FONT COMPLIANCE
```
  - All runs must have font.size >= Pt(14) (captions/labels may be Pt(10)+ in styled decks)
  - All runs must have explicit font.name set (theme defaults are unreliable)
  - All runs must have explicit font.size set

  STYLE-AWARE: If a style is active, also verify:
  - Title runs use the style's title font name
  - Body runs use the style's body font name
  - Font sizes match the style's hierarchy (load from style-pptx-mapping.md)
  - FLAG WARNING if a run uses a font name not in the active style's font dict
```

## CHECK 9: SPACING CONSISTENCY
```
  - Primary left margins should be consistent across slides (within ~100000 EMU)
  - Card gaps should be uniform where cards are in a row/column
  - Bullet item gaps should be uniform within each list
```

## CHECK 10: COLOR/FILL INTEGRITY
```
  - Verify all shape fills use the deck's intended palette
  - Check transparent overlays aren't accidentally 0% or 100% opacity

  STYLE-AWARE: If a style is active, also verify:
  - All shape fill colors exist in the active style's palette dict
  - FLAG WARNING for any RGBColor not in the style's palette (tolerance: ±10 per channel)
```

## CHECK 11: STYLE COMPLIANCE (only when a design style is active)

```
Skip this check entirely if no design style was specified.

Load the active style dict from references/style-pptx-mapping.md.

11a — BACKGROUND:
  For every slide:
    - slide.background.fill.fore_color.rgb must match style["slide_bg"]
    - Exception: title/section slides may use an alternate bg from the palette
    - FLAG CRITICAL if background is default white when style specifies a colored bg

11b — ACCENT ELEMENTS:
  If style defines accent_bar:
    - Verify accent bar shapes exist on content slides
    - accent_bar color matches style["accent_bar"]["color"]
    - accent_bar height ≈ style["accent_bar"]["height"] (tolerance: ±5000 EMU)
  If style has NO accent_bar defined:
    - No stray accent bars should be present

11c — FONT FAMILY CONSISTENCY:
  Collect all unique font.name values across the deck:
    - Every font name must appear in the active style's fonts dict values
    - FLAG WARNING for each font name NOT in the style

11d — COLOR PALETTE COHERENCE:
  Collect all unique RGBColor values from shape fills, font colors, and line colors:
    - Each color must match a value in the style's palette dict (tolerance: ±10 per RGB channel)
    - FLAG WARNING for off-palette colors
    - Exception: pure white (#FFFFFF) and pure black (#000000) are always allowed
    - Exception: semi-transparent overlays and shadows are excluded

11e — STYLE-SPECIFIC LAYOUT RULES:
  STYLE-09 (Storyboard): Verify panel grid exists
  STYLE-10 (Bento): Verify tile layout with uniform gaps and rounded corners
  STYLE-04 (Kawaii): Verify all shape corners are rounded
  STYLE-07 (Clay): Verify rounded corners on all container shapes
  STYLE-01 (Strategy): Verify no drop shadows or 3D effects
  STYLE-08 (Editorial): Verify at least one headline >= Pt(48) on non-title slides
  STYLE-12 (Retro): Verify no pure black (#000000) — must use dark navy (#1B2838)

11f — IMAGE BACKGROUND COMPLIANCE (only when images are used):
  For every slide with an image background:
    1. Image shape at (0,0) with size = slide dimensions
       FLAG CRITICAL if image doesn't cover full slide
    2. Overlay shape exists between image and text (z-order)
       FLAG CRITICAL if text sits directly on image with no overlay
    3. All text shapes within overlay bounds
       FLAG WARNING if text extends beyond overlay edges
    4. Text contrast against overlay color
       FLAG WARNING if low contrast detected
    5. Z-order: image (bottom) → overlay (middle) → text/shapes (top)
       FLAG CRITICAL if image or overlay is above any text shape
    6. Minimum font sizes on image backgrounds: Titles >= Pt(24), Body >= Pt(16)
       FLAG WARNING if below thresholds
```

### Fix Strategies for CHECK 11

```
11a fix: Set slide.background.fill.solid() and .fore_color.rgb = style["slide_bg"]
11b fix: Add/recolor accent bars per style spec; remove if style doesn't define them
11c fix: Replace non-style fonts with nearest style-equivalent
11d fix: Map off-palette colors to nearest palette color by Euclidean RGB distance
11e fix: Apply style-specific corrections (add rounded corners, remove shadows, etc.)
11f fix: Resize image to cover slide, add/fix overlay, fix z-order, bump font sizes

After any CHECK 11 fix → re-run CHECK 1 (bounds), CHECK 4 (container sync), CHECK 8 (font)
```

## CHECK 12: IMAGE ASPECT RATIO DISTORTION ⚠️ CRITICAL

**This is the #1 image placement bug.** When an image's native aspect ratio doesn't match its placement dimensions, it gets stretched/squeezed — visually obvious and unprofessional.

**Root cause:** `slide.shapes.add_picture(path, left, top, width, height)` FORCES the image to fit the given width × height, regardless of the image's native AR. If a 16:9 landscape image (1920×1080) is placed into a 3:5 portrait box (3.5"×5.5"), it gets horizontally compressed.

```
For every image shape on every slide:
  1. Read native pixel dimensions: shape.image.size → (native_w, native_h)
  2. Compute native AR: native_ar = native_w / native_h
  3. Compute placed AR: placed_ar = shape.width / shape.height
  4. Compute distortion: distortion = abs(native_ar - placed_ar) / native_ar

  EXCEPTIONS (skip these):
    - Full-bleed images at (left=0, top=0) covering entire slide
      (shape.width ≈ 12192000 ± 50000 AND shape.height ≈ 6858000 ± 50000)
      → These always match 16:9, safe to skip

  FLAG CRITICAL if distortion > 0.10 (10%)
  FLAG WARNING if distortion > 0.05 (5%) and distortion <= 0.10

  Report: "Image '{shape.name}' on slide {n}: native AR={native_ar:.2f},
           placed AR={placed_ar:.2f}, distortion={distortion:.0%}"
```

### Detection Code

```python
from PIL import Image as PILImage
import io

def check_image_ar_distortion(prs):
    """CHECK 12: Detect images placed with distorted aspect ratios."""
    SW, SH = 12192000, 6858000
    issues = []
    for slide_idx, slide in enumerate(prs.slides):
        for shape in slide.shapes:
            if not hasattr(shape, 'image'):
                continue
            try:
                blob = shape.image.blob
                img = PILImage.open(io.BytesIO(blob))
                native_w, native_h = img.size
                img.close()
            except Exception:
                continue

            native_ar = native_w / native_h
            placed_ar = shape.width / shape.height

            # Skip full-bleed backgrounds (always 16:9 → 16:9)
            if (abs(shape.left) < 50000 and abs(shape.top) < 50000
                and abs(shape.width - SW) < 50000
                and abs(shape.height - SH) < 50000):
                continue

            distortion = abs(native_ar - placed_ar) / native_ar

            if distortion > 0.10:
                issues.append({
                    'slide': slide_idx + 1,
                    'severity': 'CRITICAL',
                    'check': 12,
                    'shape': shape.name,
                    'native_ar': round(native_ar, 2),
                    'placed_ar': round(placed_ar, 2),
                    'distortion': round(distortion * 100, 1),
                    'msg': f"Image '{shape.name}' on slide {slide_idx+1}: "
                           f"native AR={native_ar:.2f}, placed AR={placed_ar:.2f}, "
                           f"distortion={distortion:.0%}"
                })
            elif distortion > 0.05:
                issues.append({
                    'slide': slide_idx + 1,
                    'severity': 'WARNING',
                    'check': 12,
                    'shape': shape.name,
                    'native_ar': round(native_ar, 2),
                    'placed_ar': round(placed_ar, 2),
                    'distortion': round(distortion * 100, 1),
                    'msg': f"Image '{shape.name}' on slide {slide_idx+1}: "
                           f"minor AR distortion {distortion:.0%}"
                })
    return issues
```

### Fix Strategies for CHECK 12

```
1. Recompute placement using add_picture_fit() from python-pptx-reference.md:
   - Read native AR from image blob
   - Fit within the SAME bounding box but preserve AR
   - Center the image within the box

2. If fixing causes the image to be much smaller than intended:
   - The image was generated at the WRONG ratio for its role
   - Flag: "Image should be regenerated at [target_ar] ratio for this placement"
   - As interim fix: use add_picture_fit() and accept the reduced coverage

3. If a 16:9 image was placed as a side panel (common mistake):
   - Option A: Move it to full-bleed background (if that's what was intended)
   - Option B: Regenerate the image at portrait ratio for the panel
   - Option C (interim): Use add_picture_fit() — image will shrink but won't distort

After CHECK 12 fix → re-run CHECK 1 (bounds), CHECK 6 (overlap)
```

## CHECK 13: BROKEN GRADIENT FILLS ("BLUE RECTANGLE" BUG) ⚠️ CRITICAL

**This is the #1 shape fill bug.** When gradient fill XML is attached to the wrong parent element or the theme style isn't overridden, PowerPoint ignores the gradient and falls back to the theme's `accent1` color — typically blue. The result is an opaque blue rectangle where a semi-transparent gradient overlay should be.

**Root cause:** Custom gradient code uses `etree.SubElement` to add `<a:gradFill>` but attaches it to `<p:sp>` (shape root) instead of `<p:spPr>` (shape properties), or doesn't remove the `<p:style>` theme reference.

```
For every non-image, non-textbox shape on every slide:
  sp = shape.element
  ns_a = 'http://schemas.openxmlformats.org/drawingml/2006/main'
  ns_p = 'http://schemas.openxmlformats.org/presentationml/2006/main'

  13a — STRAY GRADIENT ON WRONG PARENT:
    stray_grads = sp.findall(f'{{{ns_a}}}gradFill')
    If any found:
      FLAG CRITICAL: "gradFill attached to <p:sp> instead of <p:spPr> — 
                      PowerPoint ignores this and shows blue theme fill"

  13b — THEME FILL WITHOUT EXPLICIT OVERRIDE:
    spPr = sp.find(f'{{{ns_p}}}spPr')
    p_style = sp.find(f'{{{ns_p}}}style')
    has_explicit_fill = spPr is not None and (
        spPr.find(f'{{{ns_a}}}solidFill') is not None or
        spPr.find(f'{{{ns_a}}}gradFill') is not None or
        spPr.find(f'{{{ns_a}}}noFill') is not None
    )
    has_theme_fill = p_style is not None and 'accent1' in etree.tostring(p_style).decode()
    If has_theme_fill and not has_explicit_fill:
      # Shape has theme fill (likely blue) with no explicit override
      # This is only CRITICAL for large shapes (overlays) — small accent bars are OK
      If shape.width > slide_width * 0.5 or shape.height > slide_height * 0.3:
        FLAG CRITICAL: "Large shape with theme accent1 fill and no explicit 
                        spPr fill — likely a broken gradient overlay (blue rectangle)"

  EXCEPTIONS (skip these):
    - Image shapes (have shape.image)
    - TextBox shapes (shape_type == TEXT_BOX)
    - Shapes smaller than 1" × 0.1" (accent bars, thin decorative elements)
```

### Detection Code

```python
def check_broken_gradients(prs):
    """CHECK 13: Detect broken gradient fills (blue rectangle bug)."""
    from lxml import etree
    ns_a = 'http://schemas.openxmlformats.org/drawingml/2006/main'
    ns_p = 'http://schemas.openxmlformats.org/presentationml/2006/main'
    SW, SH = prs.slide_width, prs.slide_height
    issues = []

    for si, slide in enumerate(prs.slides):
        for shape in slide.shapes:
            # Skip images and textboxes
            if hasattr(shape, 'image'):
                continue
            if shape.shape_type == 17:  # TEXT_BOX
                continue

            sp = shape.element

            # 13a: Stray gradFill on <p:sp> (wrong parent)
            stray_grads = sp.findall(f'{{{ns_a}}}gradFill')
            if stray_grads:
                issues.append({
                    'slide': si + 1,
                    'severity': 'CRITICAL',
                    'check': 13,
                    'shape': shape.name,
                    'msg': f"'{shape.name}' on slide {si+1}: gradFill attached to "
                           f"<p:sp> instead of <p:spPr> — blue rectangle bug"
                })
                continue

            # 13b: Theme fill with no explicit override on large shapes
            spPr = sp.find(f'{{{ns_p}}}spPr')
            p_style = sp.find(f'{{{ns_p}}}style')
            if spPr is None or p_style is None:
                continue

            has_explicit = (
                spPr.find(f'{{{ns_a}}}solidFill') is not None or
                spPr.find(f'{{{ns_a}}}gradFill') is not None or
                spPr.find(f'{{{ns_a}}}noFill') is not None or
                spPr.find(f'{{{ns_a}}}pattFill') is not None
            )
            style_xml = etree.tostring(p_style).decode()
            has_accent = 'accent1' in style_xml

            if has_accent and not has_explicit:
                # Only flag large shapes (overlays, panels)
                is_large = (shape.width > SW * 0.5 or shape.height > SH * 0.3)
                if is_large:
                    issues.append({
                        'slide': si + 1,
                        'severity': 'CRITICAL',
                        'check': 13,
                        'shape': shape.name,
                        'msg': f"'{shape.name}' on slide {si+1}: large shape with "
                               f"theme accent1 fill, no explicit spPr fill — "
                               f"likely broken gradient (blue rectangle)"
                    })

    return issues
```

### Fix Strategies for CHECK 13

```
13a fix (stray gradFill on wrong parent):
  1. Remove the stray gradFill from <p:sp>
  2. Find <p:spPr> inside the shape
  3. Call shape.fill.solid() to create an explicit fill that overrides the theme
  4. Remove the solidFill from spPr
  5. Insert the gradFill into spPr BEFORE <a:ln>
  6. Remove <p:style> to prevent theme fallback
  7. Add alpha values to gradFill stops if this was meant to be a semi-transparent overlay

13b fix (theme fill with no explicit override):
  1. Determine the intended fill from context (gradient overlay? solid dark panel?)
  2. Call shape.fill.solid() to override the theme
  3. Set the correct fill color/gradient
  4. Optionally remove <p:style> if it's not needed

After CHECK 13 fix → re-run CHECK 7 (z-order), CHECK 10 (color integrity)
```

---

## Word-Wrap Simulation

python-pptx has **NO rendering engine**. Simulate PowerPoint's word-wrap to calculate line counts.

```python
def simulate_wrap(text, box_w_emu, font_size_pt, font='Georgia', bold=False):
    """Simulate PowerPoint word-wrap. Returns line count."""
    CHAR_WIDTHS = {
        ('Georgia', False): 6800,    ('Georgia', True): 7200,
        ('Rockwell', False): 7100,   ('Rockwell', True): 7500,
        ('Calibri', False): 6400,    ('Calibri', True): 6800,
        ('Consolas', False): 7000,   ('Consolas', True): 7000,
        ('Arial Black', False): 7600,('Arial Black', True): 7600,
        ('Comic Sans MS', False): 7200, ('Comic Sans MS', True): 7600,
    }
    avg_char_w = CHAR_WIDTHS.get((font, bold), 6800 if not bold else 7200)

    words = text.split()
    lines = 1
    current_w = 0
    space_w = avg_char_w * font_size_pt * 0.35
    usable_w = box_w_emu * 0.95

    for word in words:
        word_w = len(word) * avg_char_w * font_size_pt
        test_w = current_w + (space_w if current_w > 0 else 0) + word_w
        if current_w > 0 and test_w > usable_w:
            lines += 1
            current_w = word_w
        else:
            current_w = test_w
    return lines
```

---

## Iterative Fix Loop (with snapshot-and-rollback)

A fix pass that MAKES THINGS WORSE (e.g., widening a text box breaks container sync → breaks bounds → breaks overlap) is a real failure mode. The loop snapshots the file before each pass and reverts if the critical count goes UP.

```python
import shutil

MAX_PASSES = 5

def count_critical(issues):
    return sum(1 for i in issues if i.severity == 'CRITICAL')

# Baseline audit
issues = run_all_checks(prs)  # Checks 1-14 (11 only if style active, 13-14 always)
prev_critical = count_critical(issues)
print(f"Baseline: {prev_critical} CRITICAL, {len(issues) - prev_critical} WARNING")

for pass_num in range(1, MAX_PASSES + 1):
    if prev_critical == 0:
        print(f"✅ Clean after {pass_num - 1} fix passes")
        break

    # Snapshot BEFORE applying fixes in this pass
    snapshot_path = f"{path}.pass{pass_num - 1}.bak"
    shutil.copy2(path, snapshot_path)

    # Apply all fixes for this pass
    for issue in issues:
        apply_fix(issue)

    prs.save(path)
    prs = Presentation(path)  # Reload to get clean state
    issues = run_all_checks(prs)
    new_critical = count_critical(issues)

    if new_critical > prev_critical:
        # Regression — revert and try a different strategy next pass
        shutil.copy2(snapshot_path, path)
        prs = Presentation(path)
        issues = run_all_checks(prs)  # Refresh after revert
        print(f"⚠️ Pass {pass_num} REGRESSED: "
              f"{prev_critical} → {new_critical} critical. Reverted. "
              f"Will try a different fix strategy next pass.")
        # Mark the fix strategies that were tried, so the next pass picks different ones.
        # (The exact mechanism depends on apply_fix — e.g., a global set of
        # attempted (issue_id, strategy) pairs.)
    else:
        print(f"Pass {pass_num}: {prev_critical} → {new_critical} critical, "
              f"fixed {prev_critical - new_critical}. Re-auditing...")
        prev_critical = new_critical

else:
    print(f"⚠️ {prev_critical} critical issues remain after {MAX_PASSES} passes")

# Clean up backup files after the loop completes
import glob
for bak in glob.glob(f"{path}.pass*.bak"):
    os.remove(bak)
```

**Why rollback matters:** without it, a bad fix on pass 3 can multiply issues that persist through passes 4 and 5, and the final deck is worse than the baseline. With rollback, the worst-case outcome is "no improvement" — never "regression."

**Fix strategy diversity:** when a pass reverts, the next pass must try a different strategy for the offending issue. For example, if widening a text box caused regression, the next pass should reduce font size instead. Track attempted (issue, strategy) pairs so the loop doesn't re-apply the same bad fix.

---

## Fix Strategies

**BAD-WORD-WRAP (CHECK 3):**
1. WIDEN text frame AND parent container (cascade to CHECK 4)
2. If would go off-slide → REDUCE font size (min 14pt)
3. If font at minimum → USE shorter synonym
4. **After any width change → re-run CHECK 4**

**TEXT-CLIP / VERTICAL OVERFLOW (CHECK 2):**
1. INCREASE text frame height AND parent container
2. If would push below slide bottom → REDUCE font size
3. If font at minimum → SPLIT content across shapes
4. **After any height change → re-run CHECK 5 if in a list**

**CONTAINER-TEXT DESYNC (CHECK 4):**
1. Grow container to wrap text box + padding (0.04" each side)
2. Re-center text box inside container
3. If container would go off-slide → shrink both proportionally
4. **After container resize → re-run CHECK 1 and CHECK 6**

**BULLET MISALIGNMENT (CHECK 5):**
1. Recalculate TRUE height using simulate_wrap()
2. Set text_box.height = exact needed height
3. Stack items sequentially with consistent gap (0.14"–0.20")
4. Align dots: dot.center_y = text.top + line_height × 0.42
5. Resize parent panel to fit
6. **After re-stacking → re-run CHECK 1, CHECK 4**

**BOUNDS OVERFLOW (CHECK 1):**
1. Reduce width/height to fit
2. Reposition shape inward
3. **After repositioning → re-run CHECK 4, CHECK 5, CHECK 6**

**OVERLAP — UNINTENTIONAL (CHECK 6):**
1. Move lower-priority shape to create gap
2. Reduce width of one shape
3. **After moving → re-run CHECK 1**

---

## Bullet List Layout Algorithm

```python
DOT_SIZE = Inches(0.055)
DOT_LEFT = panel.left + Inches(0.16)
TEXT_LEFT = DOT_LEFT + DOT_SIZE + Inches(0.10)
TEXT_W = (panel.left + panel.width) - TEXT_LEFT - Inches(0.12)
LINE_H = font_size_emu * 1.35
ITEM_GAP = Inches(0.16)

current_top = content_start_y

for each (dot, text_box, text_content):
    lines = simulate_wrap(text_content, TEXT_W, font_size_pt)
    text_h = lines * LINE_H

    text_box.left = TEXT_LEFT
    text_box.top = current_top
    text_box.width = TEXT_W
    text_box.height = text_h

    dot.left = DOT_LEFT
    dot.top = current_top + LINE_H * 0.42 - DOT_SIZE / 2
    dot.width = DOT_SIZE
    dot.height = DOT_SIZE

    current_top += text_h + ITEM_GAP

panel.height = current_top - ITEM_GAP + bottom_padding - panel.top
```

---

## False Positive Avoidance

1. **Bullet dot misalignment detecting wrong shapes**: Filter small shapes to same container/panel only.
2. **Title left margin inconsistency**: Exclude page numbers and footer text near slide edges.
3. **Intentional overlaps**: Accent bars, background rectangles, container-child pairs. Use center-point containment test.
4. **Tight word warnings at 95-96%**: Only flag CRITICAL at >100%, WARNING at >96%.

---

## Output Format

Per-slide report:
```
[S#] [SEVERITY] [CHECK#] — Description → Fix applied / Remaining
```

Final summary:
```
🔴 CRITICAL: N (must be 0 before delivery)
🟡 WARNING: N (should be 0, acceptable if tight-word at >96%)
🔵 INFO: N (advisory)

STYLE: STYLE-XX (Name) or "Default (no style)"
STYLE COMPLIANCE: ✅ All checks passed / ⚠️ N issues
PASSES: X until clean
TOTAL FIXES: N applied
```

---

## CHECK 14: TEXT ZONE LUMINANCE ⚠️ CRITICAL FOR BG IMAGE SLIDES

**This catches "the generated image looked fine, but text is unreadable on it."** CHECK 12 verified the image's aspect ratio. CHECK 14 verifies the image's **content** cooperates with the declared text zone — i.e., that the pixels where text will sit are actually dark enough for white/cream overlay text (or light enough for dark text).

This is the contract verification the image-gen `verify_generated_image()` post-gen check skips when `text_zone` isn't passed. Run CHECK 14 post-build to catch cases where the pilot/batch verification was skipped.

```
For every image shape on every slide:
  1. Skip unless the shape has a declared text_zone (annotated during build).
  2. Crop the text zone region from the image bytes.
  3. Compute mean grayscale luminance.
  4. Compare against the text color on that slide.

  FLAG CRITICAL:
    - white/cream text declared but zone mean luminance > 140 (too bright)
    - dark/black text declared but zone mean luminance < 115 (too dark)

  FLAG WARNING:
    - mean luminance within 20 of threshold (marginal contrast).
```

**How the slide's text_zone is known at audit time:** annotate it when the BG image is placed. Either:

- Store in the shape's `.name` attribute: `"BG_full_bleed__text_zone=bottom:0.35:white"`
- Store in a sidecar dict during build and persist to a hidden speaker-notes marker

The audit reads the annotation and calls `verify_text_zone_luminance()` from [python-pptx-reference.md](python-pptx-reference.md#embedded-helper-functions).

### Detection Code

```python
from pptx_helpers import verify_text_zone_luminance
import re

def check_text_zone_luminance(prs):
    """CHECK 14: Verify declared text zones have adequate contrast for overlay text."""
    issues = []
    ANNOT = re.compile(r'text_zone=(?P<zone>\w+):(?P<size>[0-9.]+):(?P<color>\w+)')

    for si, slide in enumerate(prs.slides):
        for shape in slide.shapes:
            if not hasattr(shape, 'image'):
                continue
            m = ANNOT.search(shape.name or '')
            if not m:
                continue
            text_zone = {'zone': m['zone'], 'size': float(m['size'])}
            text_color = m['color']

            # Extract image to a tempfile for PIL
            import tempfile, os as _os
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                f.write(shape.image.blob)
                tmp_path = f.name
            try:
                ok, lum, msg = verify_text_zone_luminance(
                    tmp_path, text_zone, text_color=text_color
                )
            finally:
                _os.unlink(tmp_path)

            if not ok:
                issues.append({
                    'slide': si + 1, 'severity': 'CRITICAL', 'check': 14,
                    'shape': shape.name,
                    'zone': text_zone, 'text_color': text_color,
                    'mean_luminance': round(lum, 1),
                    'msg': msg,
                })
    return issues
```

### Fix Strategies for CHECK 14

```
Option A (fastest): Add a targeted gradient shape to the text zone.
  - Use add_gradient_shape() covering only the text zone.
  - Dark end (alpha ~80) at text-edge, transparent (alpha 0) toward image focal point.
  - This converts a "too-bright image zone" into a dark-enough zone for white text.

Option B (better long-term): Regenerate the image with a stronger dark-zone directive.
  - Add to prompt: "bottom 35% MUST be dark, deep shadow, low luminance."
  - Run verify_generated_image(text_zone=...) before accepting.

Option C (last resort): Flip text color.
  - If the zone is BRIGHT but the whole deck's text is white, can't easily flip.
  - Only viable if the deck supports dark-text-on-light-zone elsewhere.

Option D (layout change): Move the text zone to a darker part of the image.
  - If zone was 'bottom' but the image's top is darker, swap to 'top'.
  - Requires also moving the overlay shape and text placement.

After CHECK 14 fix → re-run CHECK 1 (bounds), CHECK 6 (overlap), CHECK 7 (z-order)
```

## Pass B: pptx-audit-and-fix tool (optional)

If the `pptx-audit-and-fix` skill is installed at `~/.claude/skills/pptx-audit-and-fix/`, run it as a second pass AFTER Pass A is clean. Pass B adds WCAG contrast validation, composition coverage (overlay shapes blocking BG images), and text truth estimation. Skip if the skill is not installed — Pass A alone is sufficient.

```python
import os, importlib.util

audit_path = os.path.expanduser("~/.claude/skills/pptx-audit-and-fix/references/pptx_audit.py")
if os.path.exists(audit_path):
    spec = importlib.util.spec_from_file_location("pptx_audit", audit_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    auditor = mod.PptxAuditor(pptx_path)
    report = auditor.run_full_audit()
    print(report)
    # Fix auto-fixable issues
    if any(i.severity.name == 'CRITICAL' for i in report.issues):
        auditor.fix_all(report)
        auditor.save(pptx_path)
else:
    print("ℹ️ pptx-audit-and-fix skill not installed — skipping Pass B.")
```

## Key Lessons Learned

1. **python-pptx has NO rendering engine** — estimate using char-count × char-width-factor × font-size. Use `simulate_wrap()` for line counting and the more conservative char_width_factor × safety_margin for single-word overflow.

2. **Fixing one issue often creates another** — the iterative loop is essential; each fix must trigger re-checks on related checks.

3. **Text box height is the most common source of visual bugs** — oversized text boxes create invisible overlap. Always calculate TRUE height from simulated wrap.

4. **Bullet lists should NOT use python-pptx bullet properties** — use explicit dot shapes + text boxes for pixel-level control. Audit with CHECK 5.

5. **Always re-audit after applying fixes** — detect→fix→re-verify is the ONLY reliable approach.

6. **Container-text sync is the #1 missed bug** — when a text box is widened, the parent container MUST grow to match.

7. **False positives kill audit credibility** — filter bullet detection to same-container, exclude page numbers, use center-point containment.

8. **python-pptx auto-shapes have `has_text_frame=True` even when empty** — detect dots by SIZE (`< Inches(0.15)`) AND empty text, never by `has_text_frame`.

9. **The audit must be GENERIC, not hardcoded to shape names** — discover bullet panels dynamically.

10. **Accent bars on dark backgrounds are visual artifacts** — detect thin decorative bars on dark slides and remove/flag them.

11. **Image aspect ratio distortion is invisible to text-based checks** — `add_picture()` silently stretches images. The ONLY way to catch distortion is to compare native pixel AR against placed EMU AR (CHECK 12). Always use `add_picture_fit()` for non-full-bleed images.

12. **The most common AR distortion: 16:9 image placed as side panel** — An image generated as a background (16:9) but used as a portrait side panel gets horizontally compressed. This happens when the composition plan says "Full-bleed BG" but the build code places it as a side panel. The audit (CHECK 12) catches this, but prevention is better: always verify the image's planned role matches its actual placement before writing `add_picture()` code.

13. **Custom gradient code is the #1 cause of "blue rectangle" bugs** — Writing `etree.SubElement(spPr, ...)` to add gradFill silently attaches to the wrong parent (`<p:sp>` instead of `<p:spPr>`), and the shape's `<p:style>` theme reference (`accent1` = blue) takes over. CHECK 13 detects this post-build, but prevention is better: ALWAYS use `add_gradient_shape()` from the reference. Never write custom gradient XML.
