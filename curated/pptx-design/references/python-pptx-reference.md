# python-pptx Complete Reference

## Table of Contents

1. [Standard Imports](#standard-imports)
2. [Opening and Saving](#opening-and-saving)
3. [Adding Slides](#adding-slides)
4. [Slide Background — Gradient (lxml)](#slide-background--gradient-lxml)
5. [Slide Background — Solid](#slide-background--solid)
6. [Clearing All Shapes](#clearing-all-shapes)
7. [Adding Shapes](#adding-shapes)
8. [Common Shape Types](#common-shape-types)
9. [Adding Text Boxes](#adding-text-boxes)
10. [Multiple Paragraphs](#multiple-paragraphs)
11. [Mixed Formatting in One Paragraph](#mixed-formatting-in-one-paragraph)
12. [Letter Spacing (lxml)](#letter-spacing-lxml)
13. [Transparency (lxml)](#transparency-lxml)
14. [Rounded Rectangle Corner Radius (lxml)](#rounded-rectangle-corner-radius-lxml)
15. [Remove Shape Outline (lxml)](#remove-shape-outline-lxml)
16. [Adding Tables](#adding-tables)
17. [Adding Charts](#adding-charts)
18. [Adding Images](#adding-images)
19. [Reading All Slide Content (Audit)](#reading-all-slide-content-audit)
20. [Overlap and Bounds Checker](#overlap-and-bounds-checker)
21. [Text Frame Sizing](#text-frame-sizing)
22. [Embedded Helper Functions](#embedded-helper-functions)
23. [EMU Quick Reference](#emu-quick-reference)

---

## Standard Imports

```python
import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor  # ⚠ See "Common Pitfalls" — no .red/.green/.blue attrs
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from lxml import etree
from PIL import Image as PILImage  # for image AR detection
```

## Opening and Saving

```python
pptx_path = os.environ['PPTX_PATH']

# Open existing
prs = Presentation(pptx_path)

# OR create new blank
prs = Presentation()
prs.slide_width = Emu(12192000)
prs.slide_height = Emu(6858000)

# ALWAYS save at end:
prs.save(pptx_path)
```

## Adding Slides

```python
layout = prs.slide_layouts[6]  # 6 = Blank (fully custom)
slide = prs.slides.add_slide(layout)
```

## Slide Background — Gradient (lxml)

Most reliable method for gradients:

```python
bg_elem = slide.background._element
bgPr = bg_elem.find(qn('p:bgPr'))
if bgPr is None:
    bgPr = etree.SubElement(bg_elem, qn('p:bgPr'))

for child in list(bgPr):
    if child.tag != qn('a:effectLst'):
        bgPr.remove(child)

gradFill = etree.SubElement(bgPr, qn('a:gradFill'))
gsLst = etree.SubElement(gradFill, qn('a:gsLst'))

gs1 = etree.SubElement(gsLst, qn('a:gs')); gs1.set('pos', '0')
srgb1 = etree.SubElement(gs1, qn('a:srgbClr')); srgb1.set('val', '0B1D3A')

gs2 = etree.SubElement(gsLst, qn('a:gs')); gs2.set('pos', '100000')
srgb2 = etree.SubElement(gs2, qn('a:srgbClr')); srgb2.set('val', '162D50')

lin = etree.SubElement(gradFill, qn('a:lin'))
lin.set('ang', '5400000')  # top-to-bottom
lin.set('scaled', '1')

if bgPr.find(qn('a:effectLst')) is None:
    etree.SubElement(bgPr, qn('a:effectLst'))
```

## Slide Background — Solid

```python
bg = slide.background; fill = bg.fill; fill.solid()
fill.fore_color.rgb = RGBColor(0xF7, 0xF8, 0xFA)
```

## Clearing All Shapes

```python
for sp in list(slide.shapes):
    slide.shapes._spTree.remove(sp._element)
```

## Adding Shapes

```python
shape = slide.shapes.add_shape(
    MSO_SHAPE.ROUNDED_RECTANGLE,
    Emu(457200), Emu(1500000), Emu(5400000), Emu(4800000)
)
shape.fill.solid()
shape.fill.fore_color.rgb = RGBColor(0x1A, 0x33, 0x58)
shape.line.color.rgb = RGBColor(0x2A, 0x4A, 0x78)
shape.line.width = Pt(0.75)

# Remove outline:
shape.line.fill.background()
```

## Common Shape Types

```python
MSO_SHAPE.RECTANGLE           MSO_SHAPE.ROUNDED_RECTANGLE
MSO_SHAPE.OVAL                MSO_SHAPE.DIAMOND
MSO_SHAPE.RIGHT_TRIANGLE      MSO_SHAPE.ISOSCELES_TRIANGLE
MSO_SHAPE.RIGHT_ARROW         MSO_SHAPE.CHEVRON
MSO_SHAPE.STAR_5_POINT        MSO_SHAPE.HEART
MSO_SHAPE.LIGHTNING_BOLT      MSO_SHAPE.CROSS
MSO_SHAPE.DONUT
```

## Adding Text Boxes

```python
txBox = slide.shapes.add_textbox(
    Emu(457200), Emu(228600), Emu(10000000), Emu(600000)
)
tf = txBox.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.alignment = PP_ALIGN.LEFT
run = p.add_run()
run.text = "EXECUTIVE SUMMARY"
run.font.size = Pt(28)
run.font.bold = True
run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
run.font.name = "Georgia"
```

## Multiple Paragraphs

```python
p1 = tf.paragraphs[0]
run1 = p1.add_run(); run1.text = "Title Line"
run1.font.size = Pt(20); run1.font.bold = True
run1.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
run1.font.name = "Georgia"

p2 = tf.add_paragraph(); p2.space_before = Pt(6)
run2 = p2.add_run(); run2.text = "Body text here"
run2.font.size = Pt(16)
run2.font.color.rgb = RGBColor(0x88, 0x99, 0xAA)
run2.font.name = "Georgia"
```

## Mixed Formatting in One Paragraph

```python
run1 = p.add_run(); run1.text = "Revenue: "
run1.font.size = Pt(18)
run1.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

run2 = p.add_run(); run2.text = "$14.8B"
run2.font.size = Pt(18); run2.font.bold = True
run2.font.color.rgb = RGBColor(0xC9, 0xA8, 0x4C)
```

## Letter Spacing (lxml)

```python
rPr = run._r.get_or_add_rPr()
rPr.set('spc', '300')  # 300 = 3pt tracking
```

## Transparency (lxml)

```python
spPr = shape._element.spPr
solidFill = spPr.find(qn('a:solidFill'))
srgbClr = solidFill.find(qn('a:srgbClr'))
alpha = etree.SubElement(srgbClr, qn('a:alpha'))
alpha.set('val', '15000')  # 15% opacity (15000/1000)
```

### ⛔ CRITICAL PITFALL: Gradient fills on shapes — NEVER write custom code

**THIS IS THE #1 CAUSE OF "MYSTERY BLUE RECTANGLES" IN PRESENTATIONS.**

**DO NOT** write your own lxml code to add `<a:gradFill>` to shapes. **DO NOT** use `etree.SubElement(spPr, qn('a:gradFill'))` or any variant. **ALWAYS** use the `add_gradient_shape()` helper from the Embedded Helper Functions section below.

**What goes wrong when you write custom gradient code:**
1. `add_shape()` creates shapes with theme style fills (`<p:style>` referencing `accent1`), not explicit `spPr` fills. Adding `gradFill` to `spPr` doesn't override the theme — the theme fill (BLUE) shows through.
2. `etree.SubElement` can silently attach to the wrong XML parent — `<p:sp>` (shape root) instead of `<p:spPr>` (shape properties). PowerPoint ignores fill elements outside `<p:spPr>` and falls back to the blue theme.
3. Even if correctly placed in `spPr`, appending puts `gradFill` AFTER `<a:ln>`, violating OOXML schema order. PowerPoint silently ignores out-of-order elements.

**The ONLY correct approach:** Use `add_gradient_shape()` (see Embedded Helper Functions below). It:
1. Calls `shape.fill.solid()` first — creates an explicit fill that overrides the theme `<p:style>`
2. Removes that `solidFill` and replaces with `gradFill` via lxml
3. Inserts `gradFill` BEFORE `<a:ln>` to respect OOXML schema order

**If you find yourself writing ANY of these, STOP and use `add_gradient_shape()` instead:**
```python
# ❌ ALL OF THESE ARE WRONG:
etree.SubElement(spPr, qn('a:gradFill'))  # Wrong insertion point
etree.SubElement(sp, '{...}gradFill')     # Wrong parent (sp not spPr)
spPr.append(gradFill)                     # Wrong order (after ln)

# ✅ THE ONLY CORRECT WAY:
shape = add_gradient_shape(slide, left, top, w, h, '#0A1628', '#000000',
                            alpha_start=40, alpha_end=75)
```

## Rounded Rectangle Corner Radius (lxml)

```python
spPr = shape._element.spPr
prstGeom = spPr.find(qn('a:prstGeom'))
avLst = prstGeom.find(qn('a:avLst'))
if avLst is None:
    avLst = etree.SubElement(prstGeom, qn('a:avLst'))
else:
    for child in list(avLst):
        avLst.remove(child)
gd = etree.SubElement(avLst, qn('a:gd'))
gd.set('name', 'adj')
gd.set('fmla', 'val 5000')  # lower = less rounded
```

## Remove Shape Outline (lxml)

```python
spPr = shape._element.spPr
ln = spPr.find(qn('a:ln'))
if ln is None:
    ln = etree.SubElement(spPr, qn('a:ln'))
noFill = etree.SubElement(ln, qn('a:noFill'))
```

## Adding Tables

```python
rows, cols = 4, 5
table_shape = slide.shapes.add_table(
    rows, cols, Emu(457200), Emu(1500000), Emu(11200000), Emu(2000000)
)
table = table_shape.table
table.columns[0].width = Emu(3000000)

# Style header row
for col_idx in range(cols):
    cell = table.cell(0, col_idx)
    cell.text = ["Metric", "2022", "2023", "2024", "Change"][col_idx]
    for paragraph in cell.text_frame.paragraphs:
        paragraph.alignment = PP_ALIGN.CENTER
        for run in paragraph.runs:
            run.font.size = Pt(14); run.font.bold = True
            run.font.color.rgb = RGBColor(0x0B, 0x1D, 0x3A)
            run.font.name = "Georgia"
    cell.fill.solid()
    cell.fill.fore_color.rgb = RGBColor(0xC9, 0xA8, 0x4C)

# Alternating row colors
for row_idx in range(1, rows):
    for col_idx in range(cols):
        cell = table.cell(row_idx, col_idx)
        cell.text = "..."
        for paragraph in cell.text_frame.paragraphs:
            for run in paragraph.runs:
                run.font.size = Pt(14)
                run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                run.font.name = "Georgia"
        cell.fill.solid()
        if row_idx % 2 == 0:
            cell.fill.fore_color.rgb = RGBColor(0x15, 0x2C, 0x4D)
        else:
            cell.fill.fore_color.rgb = RGBColor(0x1A, 0x33, 0x58)
```

## Adding Charts

```python
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE

chart_data = CategoryChartData()
chart_data.categories = ['Q1', 'Q2', 'Q3', 'Q4']
chart_data.add_series('Revenue', (100, 150, 120, 180))

chart_frame = slide.shapes.add_chart(
    XL_CHART_TYPE.COLUMN_CLUSTERED,
    Emu(1270000), Emu(1500000), Emu(9600000), Emu(4800000),
    chart_data
)
chart = chart_frame.chart
chart.has_legend = True
chart.legend.include_in_layout = False
```

## Adding Images

### WARNING: Aspect Ratio Distortion

**`slide.shapes.add_picture(path, left, top, width, height)` STRETCHES the image to fit the given width × height. If the image's native aspect ratio doesn't match, the image will be distorted.** This is the #1 source of ugly image placement.

**Rules:**
- For **full-bleed backgrounds** (16:9 image → 16:9 slide): safe to specify both width and height — they match.
- For **ALL other placements**: **DEFAULT to native-AR-by-construction** (see below). Use `add_picture_fit()` only when both slot dimensions are immutable. **AVOID `add_picture_cover()`** for portraits/faces — see warning below.
- **NEVER** call `add_picture(path, left, top, width, height)` with both width and height when the image AR doesn't match the target area AR.

**⭐ RECOMMENDED PATTERN — Native AR by construction:**

When at least ONE slot dimension is flexible (you control the layout), derive the other dimension from the image's native AR. This eliminates stretching by construction — no crop, no srcRect, no renderer quirks.

```python
from PIL import Image as PILImage

def add_picture_native_ar(slide, image_path, left, top,
                           fixed_dim, axis='height',
                           slide_w=12192000, slide_h=6858000):
    """Place image preserving native AR. ONE dimension is fixed; other is derived.

    This is the SAFEST helper for portrait/face images on landscape slides.
    No crop, no srcRect — just native AR placement. No stretch is possible.

    Args:
        fixed_dim: the fixed dimension in EMU (e.g., slide height for full-height panel)
        axis: 'height' (fix h, derive w) or 'width' (fix w, derive h)
    Returns: (pic_shape, actual_w, actual_h)
    """
    img = PILImage.open(image_path)
    iw, ih = img.size
    img.close()
    native_ar = iw / ih
    if axis == 'height':
        h = fixed_dim
        w = int(h * native_ar)
    else:
        w = fixed_dim
        h = int(w / native_ar)
    pic = slide.shapes.add_picture(image_path, Emu(left), Emu(top), Emu(w), Emu(h))
    return pic, w, h
```

Usage:
```python
# Full-height portrait panel on right side of slide — width derived from height
pic, panel_w, _ = add_picture_native_ar(slide, 'portrait.png',
                                         left=0, top=0, fixed_dim=SH, axis='height')
# panel_w is now exactly SH * native_ar — image displays at native AR, no stretch
```

**Choosing the right helper:**

| Helper | Behavior | Use when |
|--------|----------|----------|
| **`add_picture_native_ar()`** ⭐ | One dim fixed, other derived. No crop, no stretch. | **DEFAULT for portrait/face images.** When you control at least one slot dimension. |
| `add_picture_fit()` | Letterbox inside the box. May leave blank edges. Never crops. | Both slot dims fixed AND you accept letterbox; product/diagram images where full frame matters. |
| ~~`add_picture_cover()`~~ | Fill-and-crop via srcRect+xfrm. | **⚠️ AVOID for faces/portraits.** Math-correct but renders inconsistently in macOS PowerPoint — cropped portion can be stretched to display rect, distorting face proportions. Only use when both slot dims are immutable AND you've side-by-side-verified the rendered output against the source image. |

**⚠️ Empirical lesson on `add_picture_cover()`:** The srcRect-based crop+resize XML is mathematically equivalent to a CSS-cover layout, but macOS PowerPoint's renderer applies srcRect inconsistently when the cropped visible AR == box AR. Faces in portrait images come out visibly horizontally stretched. **The XML can pass `visible_AR == box_AR` checks while still rendering stretched.** If you must use cover, mandatorily render-and-side-by-side-verify before delivering. Better default: redesign the slot to use native AR via `add_picture_native_ar()`.

If neither feels right, the AR of the image doesn't match the slot — regenerate the image at the slot's AR instead of forcing a fit.

```python
from pptx.util import Emu

# Full-slide background image (16:9) — safe, AR matches
pic = slide.shapes.add_picture(
    'path/to/background.png',
    Emu(0), Emu(0), Emu(12192000), Emu(6858000)
)

# ⚠️ WRONG — forces 16:9 image into a portrait box, causing distortion:
# pic = slide.shapes.add_picture('bg.png', Emu(8000000), Emu(500000), Emu(3500000), Emu(5500000))

# ✅ RIGHT — use add_picture_fit() for non-background placements:
# pic = add_picture_fit(slide, 'photo.png', 8000000, 500000, 3500000, 5500000)
```

### Aspect-Ratio-Safe Image Placement

The canonical implementations of **`add_picture_fit()`**, **`add_picture_cover()`**, **`check_image_ar()`**, and **`verify_generated_image()`** live in [Embedded Helper Functions § Helper Functions](#helper-functions) — they are part of the standard helper library you import alongside `pal`, `make_*_page`, etc. Don't redefine them here.

Quick API surface (full docstrings at the canonical defs):

| Function | Signature | Returns |
|---|---|---|
| `add_picture_fit(slide, path, left, top, max_w, max_h, align='center')` | letterbox inside box | `(pic, l, t, w, h)` |
| `add_picture_cover(slide, path, left, top, w, h)` | fill-and-crop | `pic` |
| `check_image_ar(path, target_w_emu, target_h_emu, tolerance=0.08)` | pre-placement AR check | `(ok, native_ar, target_ar)` |
| `verify_generated_image(path, role, intended_ar=None, text_zone=None, text_color=None)` | post-generation AR + text-zone luminance check (CHECK 14) | `(ok, actual_ar, message)` |

**Post-generation workflow:**
```python
# After generating image with AI image generation tool:
ok, ar, msg = verify_generated_image('/path/to/generated.png', 'side-panel', intended_ar=0.75)
if not ok:
    print(f"⚠️ {msg}")
    # Option 1: Regenerate with stronger AR directive
    # Option 2: Change the image role to match actual AR
    # Option 3: Use add_picture_fit() to place without distortion (last resort)
else:
    print(f"✅ {msg}")
    # Proceed with placement using add_picture_fit()
```

### Usage Patterns

```python
# Full-bleed background — direct add_picture is safe (16:9 → 16:9)
slide.shapes.add_picture(bg_path, Emu(0), Emu(0), Emu(12192000), Emu(6858000))

# Side panel image — MUST use add_picture_fit()
pic, *_ = add_picture_fit(slide, photo_path,
                           8000000, 500000,   # left, top
                           3500000, 5500000)  # max W, max H

# Content image inside a card — MUST use add_picture_fit()
pic, *_ = add_picture_fit(slide, icon_path,
                           card_left + 100000, card_top + 100000,
                           card_width - 200000, 2000000)

# Pre-check before placing (optional but recommended)
ok, native_ar, target_ar = check_image_ar(photo_path, 3500000, 5500000)
if not ok:
    print(f"⚠️ AR mismatch: image is {native_ar:.2f}, target is {target_ar:.2f}")
    # Either: use add_picture_fit() to fit without distortion
    # Or: regenerate the image at the correct AR
```

## Reading All Slide Content (Audit)

```python
for slide_idx, slide in enumerate(prs.slides):
    print(f"\n{'='*60}")
    print(f"--- Slide {slide_idx + 1} ---")
    for shape in slide.shapes:
        print(f"  Shape: type={shape.shape_type}, Name='{shape.name}'")
        print(f"    Pos: L={shape.left}, T={shape.top}, W={shape.width}, H={shape.height}")
        if shape.has_text_frame:
            for para in shape.text_frame.paragraphs:
                txt = para.text.strip()
                if txt:
                    print(f"    Text: '{txt[:120]}'")
                    for run in para.runs:
                        fn = run.font.name
                        fs = run.font.size
                        fb = run.font.bold
                        try:
                            fc = str(run.font.color.rgb) if run.font.color and run.font.color.rgb else 'inherit'
                        except:
                            fc = 'inherit'
                        print(f"      Font: {fn}, Size: {fs}, Bold: {fb}, Color: {fc}")
        if hasattr(shape, 'image'):
            try:
                print(f"    [IMAGE] type={shape.image.content_type}, size={len(shape.image.blob)} bytes")
            except:
                pass
```

## Overlap and Bounds Checker

Detects unintentional overlaps using **geometry, not shape names** (audit Lesson 9).
Decorative shapes are identified by size — full-slide backgrounds, thin accent strips,
and images are skipped automatically. Parent-child containment pairs (text inside a
card) are also skipped.

```python
def check_overlaps(slide, slide_width=12192000, slide_height=6858000):
    """Report unintentional overlaps and out-of-bounds shapes on a slide.

    Skipped (not flagged as unintentional overlap):
      - Full-slide or near-full-slide shapes (backgrounds, overlays).
      - Thin accent strips (either dimension <= 0.1" / 91440 EMU).
      - Image shapes (they often sit behind decorative content by design).
      - Parent-child pairs where one shape's bbox fully contains the other.

    Args:
        slide: pptx slide object.
        slide_width, slide_height: in EMU. Defaults to 16:9 widescreen.
    """
    SW, SH = slide_width, slide_height
    THIN = 91440            # 0.1 inch
    FULL_TOL = 50000        # EMU tolerance for "full-slide"

    shapes_info = []
    for s in slide.shapes:
        is_image = hasattr(s, 'image')
        w, h = s.width, s.height
        is_full_slide = (abs(w - SW) < FULL_TOL and abs(h - SH) < FULL_TOL
                         and abs(s.left) < FULL_TOL and abs(s.top) < FULL_TOL)
        is_thin = (w <= THIN or h <= THIN)
        shapes_info.append({
            'name': s.name,
            'left': s.left, 'top': s.top,
            'right': s.left + w, 'bottom': s.top + h,
            'w': w, 'h': h,
            'decorative': is_full_slide or is_thin or is_image,
        })

    def contains(a, b):
        return (a['left'] <= b['left'] and a['top'] <= b['top']
                and a['right'] >= b['right'] and a['bottom'] >= b['bottom'])

    for i, a in enumerate(shapes_info):
        for j, b in enumerate(shapes_info):
            if i >= j: continue
            if a['decorative'] or b['decorative']: continue
            if contains(a, b) or contains(b, a): continue  # parent-child
            if (a['left'] < b['right'] and a['right'] > b['left'] and
                a['top'] < b['bottom'] and a['bottom'] > b['top']):
                print(f"  OVERLAP: {a['name']} <-> {b['name']}")

    for s in shapes_info:
        if s['right'] > SW or s['bottom'] > SH:
            print(f"  OUT OF BOUNDS: {s['name']}")
```

## Text Frame Sizing

**CRITICAL: Never guess text frame dimensions.** Always calculate width per-paragraph (sum ALL runs), compute wrapped line count against frame width, then derive height.

**The bug this prevents:** A paragraph with multiple runs (e.g., bold + normal text on the same line) has a rendered width equal to the SUM of all runs. Calculating per-run width makes each look fine, but the combined width exceeds the frame — causing wrapping the height doesn't account for, leading to text overflow.

### Sizing Helper Functions

```python
import math

PT = 12700  # 1 point in EMU

def run_width_emu(text, font_size, bold=False, spacing_hundredths=0):
    """Width of a single text run in EMU.
    Georgia avg char width: bold ~0.60*fs, regular ~0.55*fs.
    spacing_hundredths: letter spacing in hundredths of a point (e.g., 300 = 3pt)."""
    factor = 0.60 if bold else 0.55
    sp_pt = spacing_hundredths / 100.0
    return len(text) * (factor * font_size + sp_pt) * PT * 1.12  # 12% safety


def para_width_emu(runs):
    """Total width of a paragraph = SUM of all run widths.
    runs: list of (text, font_size, bold, spacing_hundredths) tuples.
    THIS IS THE KEY INSIGHT — always sum all runs, never measure individually."""
    return sum(run_width_emu(t, fs, b, sp) for t, fs, b, sp in runs)


def frame_dims(paragraphs, max_width):
    """Calculate text frame (width, height) accounting for line wrapping.
    paragraphs: list of dicts:
        {'runs': [(text, fs, bold, sp), ...],
         'max_fs': int,  # largest font size in this paragraph
         'space_before_pt': float,  # optional, default 0
         'space_after_pt': float}   # optional, default 0
    max_width: maximum allowed frame width in EMU.
    Returns (width_emu, height_emu)."""
    total_h_pt = 0
    for para in paragraphs:
        pw = para_width_emu(para['runs'])
        n_lines = max(1, math.ceil(pw / max_width))
        line_h_pt = para['max_fs'] * 1.35
        para_h_pt = (n_lines * line_h_pt
                     + para.get('space_before_pt', 0)
                     + para.get('space_after_pt', 0))
        total_h_pt += para_h_pt
    h = int(total_h_pt * PT * 1.18)  # 18% height safety
    return max_width, h


def single_line_dims(text, font_size, bold=False, spacing=0):
    """For text that must NOT wrap — returns (width, height) sized exactly.
    Use with word_wrap=False on the text frame."""
    w = int(run_width_emu(text, font_size, bold, spacing))
    h = int(font_size * 1.35 * PT * 1.18)
    return w, h
```

### Usage Rules

1. **Per-paragraph, not per-run**: A paragraph's width = sum of ALL its runs.
2. **Wrapped lines = `ceil(para_width / frame_width)`**: Always compute this.
3. **Single-line elements**: Use `word_wrap=False` and `single_line_dims()`.
4. **Multi-run paragraphs**: Use `frame_dims()` with all runs listed per paragraph.
5. **Safety margins**: 12% on width, 18% on height (Georgia renders slightly wider than calculated).

### Example

```python
# WRONG — measures runs separately, misses that they share one line:
w1 = run_width_emu("Bold part", 16, True)   # looks fine alone
w2 = run_width_emu(" — normal part", 15)     # looks fine alone
# But paragraph renders as w1+w2 on ONE line — may exceed frame!

# RIGHT — measure the full paragraph:
paras = [
    {'runs': [("Bold part", 16, True, 0), (" — normal part", 15, False, 0)],
     'max_fs': 16, 'space_after_pt': 8},
    {'runs': [("Second paragraph here.", 15, False, 0)],
     'max_fs': 15, 'space_before_pt': 8},
]
frame_w, frame_h = frame_dims(paras, max_width=5300000)
# frame_h now correctly accounts for any wrapping
```

---

## Embedded Helper Functions

Copy-paste these at the top of every Python script. They cover 90% of common operations.

### Palette (`pal`) Dict Contract

All layout helpers (`add_slide_header`, `make_kpi_card`, `make_narrative_page`, etc.)
accept a `pal` dict with **hex string** values (NOT `RGBColor` objects). Required keys:

```python
pal = {
    'accent':        '#C8A96E',  # primary accent color (bars, highlights)
    'text_primary':  '#FFFFFF',  # main text color
    'text_muted':    '#8899AA',  # subtitle / secondary text
    'card_fill':     '#1A3358',  # card/panel background
    'card_border':   '#2A4A78',  # card/panel border (or same as card_fill for no border)
    'footer_bg':     '#0A1628',  # optional — footer strip color
}
```

The `STYLE_XX` dicts in `style-pptx-mapping.md` use a DIFFERENT format (RGBColor values,
different key names). Convert with `style_to_pal()` before passing to layout helpers:

```python
pal = style_to_pal(STYLE_02)  # returns the hex-string dict helpers expect
make_kpi_card(slide, L, T, W, H, 'REVENUE', '$14.8B', 'YoY +22%', pal)
```

### Helper Functions

```python
import os
from pptx import Presentation
from pptx.util import Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from lxml import etree
from PIL import Image as PILImage


def hex_to_rgb(hex_str):
    """Convert '#RRGGBB' or 'RRGGBB' to RGBColor."""
    h = hex_str.lstrip('#')
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def rgb_to_hex(rgb_color):
    """Convert RGBColor (or int-like color) to '#RRGGBB' string."""
    s = str(rgb_color)
    return '#' + s if not s.startswith('#') else s


def style_to_pal(style_dict):
    """Adapter: convert a STYLE_XX dict (RGBColor values, style-specific keys) into
    the hex-string `pal` dict that layout helpers expect.

    Handles missing optional keys by filling sensible defaults so helpers never
    crash on KeyError. See the `pal` dict contract above the helpers section.
    """
    palette = style_dict.get('palette', {})
    def h(key, fallback):
        val = palette.get(key)
        if val is None:
            return fallback
        return rgb_to_hex(val)

    bg = h('bg', '#FFFFFF')
    return {
        'accent':       h('primary', h('accent', '#C8A96E')),
        'text_primary': h('text', '#1A1A1A'),
        'text_muted':   h('secondary', h('tertiary', '#8899AA')),
        'card_fill':    h('bg_white', bg),
        'card_border':  h('border', h('tertiary', '#CCCCCC')),
        'footer_bg':    h('footer', bg),
    }


def set_gradient_bg(slide, hex_start, hex_end, angle=5400000):
    """Set slide gradient background via lxml."""
    bg_elem = slide.background._element
    bgPr = bg_elem.find(qn('p:bgPr'))
    if bgPr is None:
        bgPr = etree.SubElement(bg_elem, qn('p:bgPr'))
    for child in list(bgPr):
        if child.tag != qn('a:effectLst'):
            bgPr.remove(child)
    gradFill = etree.SubElement(bgPr, qn('a:gradFill'))
    gsLst = etree.SubElement(gradFill, qn('a:gsLst'))
    gs1 = etree.SubElement(gsLst, qn('a:gs')); gs1.set('pos', '0')
    srgb1 = etree.SubElement(gs1, qn('a:srgbClr')); srgb1.set('val', hex_start.lstrip('#'))
    gs2 = etree.SubElement(gsLst, qn('a:gs')); gs2.set('pos', '100000')
    srgb2 = etree.SubElement(gs2, qn('a:srgbClr')); srgb2.set('val', hex_end.lstrip('#'))
    lin = etree.SubElement(gradFill, qn('a:lin'))
    lin.set('ang', str(angle)); lin.set('scaled', '1')
    if bgPr.find(qn('a:effectLst')) is None:
        etree.SubElement(bgPr, qn('a:effectLst'))


def add_rect(slide, left, top, width, height, fill_hex, border_hex=None):
    """Add a rectangle shape with optional border."""
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                                   Emu(left), Emu(top), Emu(width), Emu(height))
    shape.fill.solid()
    shape.fill.fore_color.rgb = hex_to_rgb(fill_hex)
    if border_hex:
        shape.line.color.rgb = hex_to_rgb(border_hex)
        shape.line.width = Pt(0.75)
    else:
        shape.line.fill.background()
    return shape


def add_rounded_rect(slide, left, top, width, height, fill_hex,
                     border_hex=None, radius=10000):
    """Add a rounded rectangle with configurable corner radius.

    Default `radius=10000` ("moderate/pleasant") per Rule 18.
    Scale: 3000=barely visible, 10000=moderate, 16667=PowerPoint default,
    50000=pill shape (avoid on content cards)."""
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                   Emu(left), Emu(top), Emu(width), Emu(height))
    shape.fill.solid()
    shape.fill.fore_color.rgb = hex_to_rgb(fill_hex)
    if border_hex:
        shape.line.color.rgb = hex_to_rgb(border_hex)
        shape.line.width = Pt(0.75)
    else:
        shape.line.fill.background()
    spPr = shape._element.spPr
    prstGeom = spPr.find(qn('a:prstGeom'))
    avLst = prstGeom.find(qn('a:avLst'))
    if avLst is None:
        avLst = etree.SubElement(prstGeom, qn('a:avLst'))
    else:
        for child in list(avLst):
            avLst.remove(child)
    gd = etree.SubElement(avLst, qn('a:gd'))
    gd.set('name', 'adj')
    gd.set('fmla', f'val {radius}')
    return shape


def add_textbox(slide, left, top, width, height, text,
                font_name="Georgia", font_size=16, bold=False,
                color_hex="FFFFFF", alignment=PP_ALIGN.LEFT, spacing=0):
    """Add a text box with formatted text."""
    txBox = slide.shapes.add_textbox(Emu(left), Emu(top), Emu(width), Emu(height))
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = alignment
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.color.rgb = hex_to_rgb(color_hex)
    run.font.name = font_name
    if spacing > 0:
        rPr = run._r.get_or_add_rPr()
        rPr.set('spc', str(spacing))
    return txBox


def set_transparency(shape, alpha_percent):
    """Set shape fill transparency. alpha_percent: 0=invisible, 100=opaque.

    Requires a shape with solidFill. For gradient-filled shapes produced by
    add_gradient_shape(), pass alpha_start/alpha_end to that helper instead —
    per-stop alpha lives on the gradient stops, not the shape.
    """
    spPr = shape._element.spPr
    solidFill = spPr.find(qn('a:solidFill'))
    if solidFill is None:
        raise ValueError(
            "set_transparency requires a shape with solidFill. Got a shape with "
            "gradFill or no fill — pass alpha_start/alpha_end to add_gradient_shape() "
            "instead, or call shape.fill.solid() first if you meant to replace the fill."
        )
    srgbClr = solidFill.find(qn('a:srgbClr'))
    if srgbClr is None:
        raise ValueError(
            "set_transparency: solidFill has no srgbClr child. The shape may be "
            "using a theme color reference — call shape.fill.solid() + assign "
            "shape.fill.fore_color.rgb before setting transparency."
        )
    for existing in srgbClr.findall(qn('a:alpha')):
        srgbClr.remove(existing)
    alpha = etree.SubElement(srgbClr, qn('a:alpha'))
    alpha.set('val', str(int(alpha_percent * 1000)))


def clear_slide(slide):
    """Remove all shapes from a slide.

    Does NOT modify the slide background or layout — only the shape tree.
    Use when rebuilding a slide's contents in place (e.g., during a redesign).
    """
    for sp in list(slide.shapes):
        slide.shapes._spTree.remove(sp._element)


def add_slide_header(slide, title_text, pal, subtitle_text=None, font_name="Georgia"):
    """Standard slide header: left accent bar + title + underline + optional subtitle.
    Returns Y position where content should start below the header."""
    add_rect(slide, 0, 0, 57150, 6858000, pal['accent'])
    add_textbox(slide, 457200, 200000, 10000000, 550000, title_text,
                font_name=font_name, font_size=30, bold=True,
                color_hex=pal['text_primary'], spacing=350)
    add_rect(slide, 457200, 750000, 2200000, 32000, pal['accent'])
    y = 900000
    if subtitle_text:
        add_textbox(slide, 457200, 830000, 10000000, 350000, subtitle_text,
                    font_name=font_name, font_size=16, color_hex=pal['text_muted'])
        y = 1250000
    return y


def add_slide_footer(slide, text, pal, font_name="Georgia"):
    """Standard slide footer bar."""
    add_rect(slide, 0, 6500000, 12192000, 358000, pal.get('footer_bg', '#0A1628'))
    add_textbox(slide, 457200, 6530000, 11280000, 300000, text,
                font_name=font_name, font_size=14,
                color_hex=pal['text_muted'], spacing=150)


def make_kpi_card(slide, left, top, width, height, label, value, note, pal,
                  font_name="Georgia"):
    """Create a KPI metric card with label, big value, and note.
    Use ONLY for actual metric/data content (revenue, growth rates, counts,
    percentages, scores). For narrative, story, or quote content, use the
    appropriate layout helper: make_narrative_page(), make_quote_page(),
    make_comparison_page(), make_title_page(), or make_chapter_divider()."""
    add_rounded_rect(slide, left, top, width, height,
                     pal['card_fill'], pal['card_border'])  # default radius=10000 (Rule 18)
    # Top accent bar INSET within card (Rule 23 — bar must be inside card boundary).
    # Offset by card corner radius so the bar doesn't poke past the rounded corners.
    bar_inset = 180000  # ~0.2" — clears the 10000 adj rounded corner
    add_rect(slide, left + bar_inset, top + 80000,
             width - 2 * bar_inset, 28000, pal['accent'])

    tb = slide.shapes.add_textbox(
        Emu(left + 180000), Emu(top + 180000),
        Emu(width - 360000), Emu(height - 280000)
    )
    tf = tb.text_frame; tf.word_wrap = True

    p = tf.paragraphs[0]; p.space_after = Pt(4)
    r = p.add_run(); r.text = label
    r.font.size = Pt(14); r.font.bold = True
    r.font.color.rgb = hex_to_rgb(pal['accent'])
    r.font.name = font_name
    rPr = r._r.get_or_add_rPr(); rPr.set('spc', '200')

    p2 = tf.add_paragraph(); p2.space_before = Pt(8); p2.space_after = Pt(4)
    r2 = p2.add_run(); r2.text = value
    r2.font.size = Pt(28); r2.font.bold = True
    r2.font.color.rgb = hex_to_rgb(pal['text_primary'])
    r2.font.name = font_name

    p3 = tf.add_paragraph(); p3.space_before = Pt(2)
    r3 = p3.add_run(); r3.text = note
    r3.font.size = Pt(14)
    r3.font.color.rgb = hex_to_rgb(pal['text_muted'])
    r3.font.name = font_name
    return tb


def add_picture_cover(slide, image_path, left, top, width, height):
    """Add image filling bounding box with fill-and-crop (CSS cover mode).

    Unlike add_picture_fit() which fits INSIDE the box (may leave blank space),
    this fills the ENTIRE box by scaling to the larger dimension and cropping
    the overflow via a:srcRect — no blank space, no distortion.

    USE THIS for portrait photo panels, side-panel images, and anywhere you
    want the image to fully fill a defined area without letterboxing.

    LESSON LEARNED (2026-04-07): add_picture(path, l, t, w, h) with both
    dimensions set silently stretches the image, destroying aspect ratio.
    This helper is the correct fill-and-crop solution.
    """
    from PIL import Image as PILImage
    from lxml import etree
    from pptx.oxml.ns import qn

    img = PILImage.open(image_path)
    iw, ih = img.size
    img.close()
    img_ar = iw / ih
    box_ar = width / height

    # Scale to fill: fit the larger dimension, overflow the other
    if img_ar > box_ar:
        # image is wider than box — fit by height, crop sides
        fit_h = height
        fit_w = int(height * img_ar)
    else:
        # image is taller than box — fit by width, crop top/bottom
        fit_w = width
        fit_h = int(width / img_ar)

    # Place oversized image centered over the box
    offset_l = left - (fit_w - width) // 2
    offset_t = top - (fit_h - height) // 2
    pic = slide.shapes.add_picture(image_path, Emu(offset_l), Emu(offset_t),
                                   Emu(fit_w), Emu(fit_h))

    # Apply srcRect crop to trim overflow
    crop_l = max(0, (left - offset_l) / fit_w)
    crop_t = max(0, (top - offset_t) / fit_h)
    crop_r = max(0, (offset_l + fit_w - (left + width)) / fit_w)
    crop_b = max(0, (offset_t + fit_h - (top + height)) / fit_h)

    spTree = pic._element
    blipFill = (spTree.find('.//' + qn('p:blipFill')) or
                spTree.find('.//' + qn('pic:blipFill')))
    if blipFill is not None:
        srcRect = blipFill.find(qn('a:srcRect'))
        if srcRect is None:
            srcRect = etree.SubElement(blipFill, qn('a:srcRect'))
        srcRect.set('l', str(int(crop_l * 100000)))
        srcRect.set('t', str(int(crop_t * 100000)))
        srcRect.set('r', str(int(crop_r * 100000)))
        srcRect.set('b', str(int(crop_b * 100000)))

    # Reposition shape to exact bounding box
    spPr = (spTree.find('.//' + qn('p:spPr')) or
            spTree.find('.//' + qn('pic:spPr')))
    if spPr is not None:
        xfrm = spPr.find(qn('a:xfrm'))
        if xfrm is not None:
            off = xfrm.find(qn('a:off'))
            ext = xfrm.find(qn('a:ext'))
            if off is not None:
                off.set('x', str(int(left)))
                off.set('y', str(int(top)))
            if ext is not None:
                ext.set('cx', str(int(width)))
                ext.set('cy', str(int(height)))
    return pic


def add_picture_fit(slide, image_path, left, top, max_width, max_height,
                    align='center'):
    """Add image preserving native aspect ratio within a bounding box (fit/letterbox mode).

    Fits INSIDE the box — may leave blank space at edges. Use add_picture_cover()
    instead when you need the image to fill the entire box with no blank space.
    ALWAYS use one of these for non-full-bleed images. Never call add_picture()
    with both W and H unless the image AR matches the target box AR.

    Args:
        slide: pptx slide object
        image_path: path to image file
        left, top: top-left corner of bounding box (EMU)
        max_width, max_height: maximum dimensions (EMU)
        align: 'center' (default), 'top-left', 'top', 'bottom'

    Returns:
        (pic_shape, actual_left, actual_top, actual_width, actual_height)
    """
    img = PILImage.open(image_path)
    native_w, native_h = img.size
    img.close()
    native_ar = native_w / native_h
    box_ar = max_width / max_height
    if native_ar > box_ar:
        w = max_width
        h = int(w / native_ar)
    else:
        h = max_height
        w = int(h * native_ar)
    if align == 'top-left':
        al, at = left, top
    elif align == 'top':
        al = left + (max_width - w) // 2
        at = top
    elif align == 'bottom':
        al = left + (max_width - w) // 2
        at = top + max_height - h
    else:  # 'center' (default)
        al = left + (max_width - w) // 2
        at = top + (max_height - h) // 2
    pic = slide.shapes.add_picture(image_path, Emu(al), Emu(at), Emu(w), Emu(h))
    return pic, al, at, w, h


def check_image_ar(image_path, target_w_emu, target_h_emu, tolerance=0.08):
    """Check if image native AR matches target placement AR.
    Returns (ok, native_ar, target_ar). Use BEFORE placing."""
    img = PILImage.open(image_path)
    native_w, native_h = img.size
    img.close()
    native_ar = native_w / native_h
    target_ar = target_w_emu / target_h_emu
    diff = abs(native_ar - target_ar) / native_ar
    return diff <= tolerance, round(native_ar, 2), round(target_ar, 2)


def _crop_text_zone(img, text_zone):
    """Crop the declared text zone from an image. Returns a PIL.Image.

    text_zone: dict {'zone': 'bottom'|'top'|'left'|'right'|'center-band', 'size': 0.0-1.0}
    """
    W, H = img.size
    zone = text_zone.get('zone', 'bottom')
    size = float(text_zone.get('size', 0.35))
    if zone == 'bottom':
        return img.crop((0, int(H * (1 - size)), W, H))
    if zone == 'top':
        return img.crop((0, 0, W, int(H * size)))
    if zone == 'left':
        return img.crop((0, 0, int(W * size), H))
    if zone == 'right':
        return img.crop((int(W * (1 - size)), 0, W, H))
    if zone == 'center-band':
        h = int(H * size)
        y = (H - h) // 2
        return img.crop((0, y, W, y + h))
    raise ValueError(f"text_zone['zone'] must be 'bottom'|'top'|'left'|'right'|'center-band', got {zone!r}")


def verify_text_zone_luminance(image_path, text_zone,
                                text_color='white', max_lum=140, min_lum=115):
    """Check if the declared text zone is dark/light enough to host overlay text.

    Args:
        image_path: path to the generated image.
        text_zone: dict {'zone': ..., 'size': ...} — matches add_bg_image()'s arg.
        text_color: 'white' | 'cream' | 'dark' | 'black'. Governs which direction to check.
        max_lum: when text_color is light (white/cream), zone mean luminance must be <= this (0-255).
                 Default 140 leaves headroom for comfortable white-on-dark contrast.
        min_lum: when text_color is dark (black/dark), zone mean luminance must be >= this.

    Returns:
        (ok: bool, mean_lum: float, message: str)
    """
    img = PILImage.open(image_path).convert('L')  # grayscale
    crop = _crop_text_zone(img, text_zone)
    pixels = list(crop.getdata())
    img.close()
    crop.close()
    if not pixels:
        return False, 0.0, "Text zone crop is empty — check text_zone dimensions."

    mean = sum(pixels) / len(pixels)
    light_text = text_color.lower() in ('white', 'cream', 'gold', 'light')
    dark_text  = text_color.lower() in ('black', 'dark')

    if light_text:
        if mean > max_lum:
            return False, mean, (
                f"TEXT ZONE TOO BRIGHT for {text_color} text: mean luminance "
                f"{mean:.0f}/255 (max allowed {max_lum}). REGENERATE with stronger "
                f"dark-zone directive, OR add a targeted gradient shape to darken this zone."
            )
        return True, mean, f"OK: text zone mean luminance {mean:.0f} ≤ {max_lum} for {text_color} text"

    if dark_text:
        if mean < min_lum:
            return False, mean, (
                f"TEXT ZONE TOO DARK for {text_color} text: mean luminance "
                f"{mean:.0f}/255 (min required {min_lum}). REGENERATE with lighter directive."
            )
        return True, mean, f"OK: text zone mean luminance {mean:.0f} ≥ {min_lum} for {text_color} text"

    return True, mean, f"OK: text zone mean luminance {mean:.0f} (no direction check for text_color={text_color!r})"


def verify_generated_image(image_path, intended_role, intended_ar=None,
                            text_zone=None, text_color='white'):
    """MANDATORY post-generation check. Run after EVERY image generation.

    Two-stage verification:
      1. AR check — does the image's pixel AR match the intended role's expected AR?
      2. Text zone luminance check (if text_zone provided) — is the declared text zone
         dark/light enough to host overlay text?

    Args:
        image_path: path to generated image.
        intended_role: 'full-bleed', 'side-panel', 'content', 'accent-strip'.
        intended_ar: expected AR float (e.g. 1.78 for 16:9). If None, uses role defaults.
        text_zone: dict {'zone': ..., 'size': ...} matching add_bg_image(). If provided,
                   runs the luminance check. Omit for images that don't host text.
        text_color: 'white' (default) | 'cream' | 'dark' | 'black'. Governs luminance direction.

    Returns:
        (ok: bool, details: dict, message: str)

        details = {
            'actual_ar': float,
            'ar_ok': bool,
            'zone_lum': float or None,
            'zone_ok': bool or None,
        }
    """
    ROLE_AR = {
        'full-bleed':   (1.5, 2.0),
        'side-panel':   (0.5, 1.0),
        'content':      (0.6, 1.8),
        'accent-strip': (2.0, 5.0),
    }
    img = PILImage.open(image_path)
    w, h = img.size
    img.close()
    actual_ar = round(w / h, 2)

    # Stage 1: AR check
    if intended_ar:
        diff = abs(actual_ar - intended_ar) / intended_ar
        if diff > 0.15:
            return False, {'actual_ar': actual_ar, 'ar_ok': False, 'zone_lum': None, 'zone_ok': None}, (
                f"AR MISMATCH: {w}x{h} (AR={actual_ar}), intended={intended_ar} "
                f"for {intended_role}. Deviation={diff:.0%}. REGENERATE.")
        ar_ok = True
    else:
        lo, hi = ROLE_AR.get(intended_role, (0.5, 2.0))
        if actual_ar < lo or actual_ar > hi:
            return False, {'actual_ar': actual_ar, 'ar_ok': False, 'zone_lum': None, 'zone_ok': None}, (
                f"AR MISMATCH: {w}x{h} (AR={actual_ar}), {intended_role} expects [{lo}-{hi}]. REGENERATE.")
        ar_ok = True

    # Stage 2: Text zone luminance check (optional)
    if text_zone is not None:
        zone_ok, zone_lum, zone_msg = verify_text_zone_luminance(
            image_path, text_zone, text_color=text_color
        )
        if not zone_ok:
            return False, {
                'actual_ar': actual_ar, 'ar_ok': True,
                'zone_lum': zone_lum, 'zone_ok': False,
            }, f"AR ok ({actual_ar}) but {zone_msg}"
        return True, {
            'actual_ar': actual_ar, 'ar_ok': True,
            'zone_lum': zone_lum, 'zone_ok': True,
        }, f"OK: {w}x{h} AR={actual_ar}, {zone_msg}"

    return True, {
        'actual_ar': actual_ar, 'ar_ok': True,
        'zone_lum': None, 'zone_ok': None,
    }, f"OK: {w}x{h} AR={actual_ar} matches {intended_role} (no text_zone check requested)"


def add_bg_image(slide, image_path, text_zone=None,
                 gradient_hex='#000000', gradient_alpha=(80, 0),
                 slide_width=12192000, slide_height=6858000):
    """Add full-bleed background image with OPTIONAL targeted gradient per Rule 25/28.

    Strategy: dark BG image + targeted gradient shape ONLY where text sits.
    NEVER adds a full-slide overlay (that violates Rule 25 — it washes out the
    whole image uniformly and defeats the point of using a BG image).

    Args:
        image_path: path to the BG image. Must be dark/moody (Rule 28).
        text_zone: dict describing where text will sit — determines the
            gradient shape. Shape of the dict:
                {'zone': 'bottom'|'top'|'left'|'right'|'center-band',
                 'size': float in (0, 1)}  # fraction of slide in that axis
            If None, no gradient is added. Use None for card-based slides
            where opaque cards handle contrast (Rule 28, opaque-card exception).
        gradient_hex: color for the gradient shape (default black).
        gradient_alpha: (alpha_at_text_end, alpha_at_image_end). 0=transparent,
            100=opaque. Default (80, 0) = 80% opaque where text sits, fading
            to transparent toward image focal point.
        slide_width, slide_height: slide dimensions in EMU (default 16:9).

    Returns:
        (picture_shape, gradient_shape_or_None)
    """
    SW, SH = slide_width, slide_height
    pic = slide.shapes.add_picture(image_path, Emu(0), Emu(0), Emu(SW), Emu(SH))

    if text_zone is None:
        return pic, None

    zone = text_zone.get('zone', 'bottom')
    size = float(text_zone.get('size', 0.35))
    a_text, a_image = gradient_alpha

    # angle encoding (OOXML): 0 = left-to-right, 5400000 = top-to-bottom,
    # 10800000 = right-to-left, 16200000 = bottom-to-top.
    if zone == 'bottom':
        h = int(SH * size)
        # bottom zone: alpha starts transparent at top, opaque at bottom
        g = add_gradient_shape(slide, 0, SH - h, SW, h, gradient_hex, gradient_hex,
                               angle='5400000',
                               alpha_start=a_image, alpha_end=a_text)
    elif zone == 'top':
        h = int(SH * size)
        g = add_gradient_shape(slide, 0, 0, SW, h, gradient_hex, gradient_hex,
                               angle='5400000',
                               alpha_start=a_text, alpha_end=a_image)
    elif zone == 'left':
        w = int(SW * size)
        g = add_gradient_shape(slide, 0, 0, w, SH, gradient_hex, gradient_hex,
                               angle='0',
                               alpha_start=a_text, alpha_end=a_image)
    elif zone == 'right':
        w = int(SW * size)
        g = add_gradient_shape(slide, SW - w, 0, w, SH, gradient_hex, gradient_hex,
                               angle='0',
                               alpha_start=a_image, alpha_end=a_text)
    elif zone == 'center-band':
        h = int(SH * size)
        y = (SH - h) // 2
        # two-stop vertical fade: edges transparent, middle opaque. Use a
        # symmetric approximation with a single shape biased toward center.
        g = add_gradient_shape(slide, 0, y, SW, h, gradient_hex, gradient_hex,
                               angle='5400000',
                               alpha_start=a_image, alpha_end=a_text)
    else:
        raise ValueError(
            f"text_zone['zone'] must be one of "
            f"'bottom'|'top'|'left'|'right'|'center-band', got {zone!r}"
        )
    return pic, g


def make_title_page(slide, title_text, subtitle_text, pal,
                    font_name="Georgia", title_size=36, subtitle_size=18):
    """Create a centered title page with accent line.
    Use for: opening slide, section title cards.
    Layout: centered title + horizontal accent line + subtitle below."""
    SW, SH = 12192000, 6858000
    # Title — centered
    t_w, t_h = single_line_dims(title_text, title_size, bold=True, spacing=400)
    t_w = min(t_w, SW - 914400)
    t_left = (SW - t_w) // 2
    add_textbox(slide, t_left, 2400000, t_w, t_h, title_text,
                font_name=font_name, font_size=title_size, bold=True,
                color_hex=pal['text_primary'], alignment=PP_ALIGN.CENTER, spacing=400)
    # Accent line — centered below title
    line_w = min(2400000, t_w)
    add_rect(slide, (SW - line_w) // 2, 3100000, line_w, 32000, pal['accent'])
    # Subtitle — centered
    s_w, s_h = single_line_dims(subtitle_text, subtitle_size)
    s_w = min(s_w, SW - 914400)
    add_textbox(slide, (SW - s_w) // 2, 3300000, s_w, s_h, subtitle_text,
                font_name=font_name, font_size=subtitle_size,
                color_hex=pal['text_muted'], alignment=PP_ALIGN.CENTER)


def make_chapter_divider(slide, chapter_num, chapter_title, pal,
                         font_name="Georgia", num_size=72, title_size=28):
    """Create a chapter divider with large number + accent line + title.
    Use for: section transitions, story act breaks, topic changes."""
    SW = 12192000
    # Large chapter number
    num_text = str(chapter_num).zfill(2)
    n_w, n_h = single_line_dims(num_text, num_size, bold=True)
    add_textbox(slide, (SW - n_w) // 2, 1800000, n_w, n_h, num_text,
                font_name=font_name, font_size=num_size, bold=True,
                color_hex=pal['accent'], alignment=PP_ALIGN.CENTER)
    # Accent line
    add_rect(slide, (SW - 1800000) // 2, 2800000, 1800000, 32000, pal['accent'])
    # Chapter title
    t_w, t_h = single_line_dims(chapter_title, title_size, bold=True, spacing=300)
    t_w = min(t_w, SW - 914400)
    add_textbox(slide, (SW - t_w) // 2, 3000000, t_w, t_h, chapter_title,
                font_name=font_name, font_size=title_size, bold=True,
                color_hex=pal['text_primary'], alignment=PP_ALIGN.CENTER, spacing=300)


def make_narrative_page(slide, title_text, body_text, pal,
                        font_name="Georgia", title_size=28, body_size=16,
                        image_path=None):
    """Create a narrative/story page with flowing body text, NOT cards.
    Use for: story content, explanations, educational text, descriptions.
    If image_path is provided, text takes left 60%, image takes right 40%.
    Image is placed with PRESERVED ASPECT RATIO — never distorted."""
    SW, SH = 12192000, 6858000
    margin = 457200
    content_top = add_slide_header(slide, title_text, pal, font_name=font_name)
    if image_path:
        text_w = int((SW - margin * 2) * 0.58)
        img_left = margin + text_w + 200000
        img_max_w = SW - img_left - margin
        img_top = content_top + 100000
        img_max_h = SH - img_top - 500000
        # CRITICAL: Use add_picture_fit() to preserve aspect ratio
        add_picture_fit(slide, image_path,
                        img_left, img_top, img_max_w, img_max_h,
                        align='center')
    else:
        text_w = SW - margin * 2
    # Body text
    body_h = SH - content_top - 600000
    txBox = slide.shapes.add_textbox(
        Emu(margin), Emu(content_top + 100000),
        Emu(text_w), Emu(body_h)
    )
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    p.line_spacing = Pt(body_size * 1.5)
    run = p.add_run()
    run.text = body_text
    run.font.size = Pt(body_size)
    run.font.color.rgb = hex_to_rgb(pal['text_primary'])
    run.font.name = font_name
    return txBox


def make_quote_page(slide, quote_text, attribution, pal,
                    font_name="Georgia", quote_size=26, attr_size=16):
    """Create a centered quote page with decorative quotation mark.
    Use for: famous quotes, character dialogue, testimonials, key takeaways."""
    SW, SH = 12192000, 6858000
    # Decorative opening quote mark (large, faded)
    q_mark = slide.shapes.add_textbox(
        Emu((SW - 1200000) // 2), Emu(1200000), Emu(1200000), Emu(900000)
    )
    tf_q = q_mark.text_frame
    p_q = tf_q.paragraphs[0]
    p_q.alignment = PP_ALIGN.CENTER
    r_q = p_q.add_run()
    r_q.text = "\u201C"
    r_q.font.size = Pt(120)
    r_q.font.color.rgb = hex_to_rgb(pal['accent'])
    r_q.font.name = font_name
    set_transparency(q_mark, 20)
    # Quote text — centered, italic
    q_w = int(SW * 0.7)
    q_left = (SW - q_w) // 2
    paras = [{'runs': [(quote_text, quote_size, False, 0)],
              'max_fs': quote_size}]
    _, q_h = frame_dims(paras, q_w)
    txBox = slide.shapes.add_textbox(
        Emu(q_left), Emu(2400000), Emu(q_w), Emu(q_h)
    )
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.line_spacing = Pt(quote_size * 1.6)
    run = p.add_run()
    run.text = quote_text
    run.font.size = Pt(quote_size)
    run.font.italic = True
    run.font.color.rgb = hex_to_rgb(pal['text_primary'])
    run.font.name = font_name
    # Attribution — right-aligned below quote
    attr_top = 2400000 + q_h + 300000
    a_w, a_h = single_line_dims(f"— {attribution}", attr_size)
    a_w = min(a_w, q_w)
    add_textbox(slide, q_left, attr_top, q_w, a_h, f"— {attribution}",
                font_name=font_name, font_size=attr_size,
                color_hex=pal['text_muted'], alignment=PP_ALIGN.RIGHT)
    return txBox


def make_comparison_page(slide, title_text, left_title, left_items,
                         right_title, right_items, pal,
                         font_name="Georgia", title_size=28, body_size=16):
    """Create a side-by-side comparison page with two columns.
    Use for: pros vs cons, before vs after, two characters, two options.
    left_items/right_items: list of strings (bullet points)."""
    SW, SH = 12192000, 6858000
    margin = 457200
    content_top = add_slide_header(slide, title_text, pal, font_name=font_name)
    col_w = 5200000
    gap = 400000
    col1_left = margin
    col2_left = margin + col_w + gap
    col_top = content_top + 100000
    col_h = SH - col_top - 600000
    # Divider line (thin accent)
    div_x = margin + col_w + gap // 2 - 16000
    add_rect(slide, div_x, col_top, 32000, col_h, pal['accent'])
    for col_idx, (col_title, items, c_left) in enumerate([
        (left_title, left_items, col1_left),
        (right_title, right_items, col2_left)
    ]):
        # Column header
        add_textbox(slide, c_left, col_top, col_w, 450000, col_title,
                    font_name=font_name, font_size=20, bold=True,
                    color_hex=pal['accent'])
        # Bullet items
        txBox = slide.shapes.add_textbox(
            Emu(c_left), Emu(col_top + 500000),
            Emu(col_w), Emu(col_h - 500000)
        )
        tf = txBox.text_frame
        tf.word_wrap = True
        for i, item in enumerate(items):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.space_before = Pt(8)
            p.alignment = PP_ALIGN.LEFT
            run = p.add_run()
            run.text = f"\u2022  {item}"
            run.font.size = Pt(body_size)
            run.font.color.rgb = hex_to_rgb(pal['text_primary'])
            run.font.name = font_name


def add_gradient_shape(slide, left, top, width, height, hex_start, hex_end,
                       angle='5400000', alpha_start=None, alpha_end=None):
    """Add a rectangle with gradient fill, properly overriding theme defaults.

    CRITICAL: Do NOT use etree.SubElement to add gradFill directly to spPr
    after add_shape(). This causes two bugs:
    1. add_shape() applies a theme fill via <p:style>, not an explicit spPr fill.
       Simply adding gradFill to spPr won't override the theme — both render,
       and the theme fill (often light blue) shows through transparent areas.
    2. SubElement appends gradFill AFTER <a:ln>, violating OOXML schema order
       (fill must come before ln). PowerPoint ignores out-of-order elements.

    The fix:
    1. Call shape.fill.solid() first — this creates an explicit fill in spPr
       that properly overrides the theme style.
    2. Remove that solidFill and replace with gradFill via lxml.
    3. Insert gradFill BEFORE <a:ln> to respect OOXML schema order.

    Args:
        alpha_start/alpha_end: 0=invisible, 100=fully opaque (maps to OOXML val*1000)
    """
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                                    Emu(left), Emu(top), Emu(width), Emu(height))
    shape.line.fill.background()

    # Step 1: Override theme fill with explicit solid fill
    shape.fill.solid()
    shape.fill.fore_color.rgb = RGBColor(0, 0, 0)

    # Step 2: Remove solidFill, replace with gradFill
    spPr = shape._element.spPr
    solidFill = spPr.find(qn('a:solidFill'))
    if solidFill is not None:
        spPr.remove(solidFill)

    # Step 3: Insert gradFill BEFORE <a:ln> (OOXML schema order)
    ln = spPr.find(qn('a:ln'))
    gradFill = etree.Element(qn('a:gradFill'))
    if ln is not None:
        spPr.insert(list(spPr).index(ln), gradFill)
    else:
        spPr.append(gradFill)

    gsLst = etree.SubElement(gradFill, qn('a:gsLst'))
    gs1 = etree.SubElement(gsLst, qn('a:gs')); gs1.set('pos', '0')
    srgb1 = etree.SubElement(gs1, qn('a:srgbClr'))
    srgb1.set('val', hex_start.lstrip('#'))
    if alpha_start is not None:
        a = etree.SubElement(srgb1, qn('a:alpha'))
        a.set('val', str(int(alpha_start * 1000)))

    gs2 = etree.SubElement(gsLst, qn('a:gs')); gs2.set('pos', '100000')
    srgb2 = etree.SubElement(gs2, qn('a:srgbClr'))
    srgb2.set('val', hex_end.lstrip('#'))
    if alpha_end is not None:
        a = etree.SubElement(srgb2, qn('a:alpha'))
        a.set('val', str(int(alpha_end * 1000)))

    lin = etree.SubElement(gradFill, qn('a:lin'))
    lin.set('ang', str(angle)); lin.set('scaled', '1')
    return shape
```

## Common Pitfalls

### 1. RGBColor has NO `.red`, `.green`, `.blue` attributes

`pptx.dml.color.RGBColor` inherits from `int`, NOT a named-tuple. Accessing `.red` raises `AttributeError` and crashes the build script.

```python
color = RGBColor(0xFA, 0xF7, 0xF2)

# ❌ WRONG — crashes with AttributeError
srgb.set('val', f'{color.red:02X}{color.green:02X}{color.blue:02X}')

# ✅ RIGHT — str() returns 'FAF7F2'
srgb.set('val', str(color))

# ✅ RIGHT — indexing works for int components
r, g, b = color[0], color[1], color[2]
```

**Rule for lxml helpers:** Any function that builds XML elements needing a hex color string (gradients, transparency, glow, shadow) should accept `hex_color: str` as the parameter type, NOT `RGBColor`. Convert at the call site with `str(my_rgb_color)` if needed.

### 2. Gradient fills via python-pptx API can fail silently

Always use the lxml approach for gradient fills (see `set_gradient_bg()` and shape gradient examples). The `fill.gradient()` API can produce empty/broken fills that render as solid opaque shapes in PowerPoint.

### 3. `add_picture()` silently distorts images

`slide.shapes.add_picture(path, left, top, width, height)` stretches the image to fit W×H regardless of native AR. Use `add_picture_fit()` for all non-full-bleed placements. See Rule #22.

---

## EMU Quick Reference

| Measurement | EMU Value |
|-------------|-----------|
| 1 inch | 914400 |
| 0.5 inch | 457200 |
| Slide width (10") | 12192000 |
| Slide height (7.5") | 6858000 |
| 1 point | 12700 |
| 1 cm | 360000 |
