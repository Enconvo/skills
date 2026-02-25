# Post-Generation Audit System for Excel Workbooks

## Table of Contents

1. [Cascading Fix Problem](#cascading-fix-problem)
2. [Checks 1-10](#check-1-sheet-setup)
3. [Iterative Fix Loop](#iterative-fix-loop)
4. [Fix Strategies](#fix-strategies)
5. [False Positive Avoidance](#false-positive-avoidance)
6. [Output Format](#output-format)
7. [Key Lessons Learned](#key-lessons-learned)

---

## Cascading Fix Problem

Fixing one issue often creates another. This is the #1 reason audits fail:
- Widening a column to fit text → may push total table width beyond print margins (CHECK 3)
- Increasing font size to fix minimum → changes row height needs (CHECK 8)
- Adding merged cells for style compliance → may break auto-filter (CHECK 4)
- Fixing column widths → may affect chart anchor positions (CHECK 6)

**The iterative loop is NON-NEGOTIABLE. A single-pass audit is useless.**

---

## CHECK 1: SHEET SETUP
```
For every worksheet in the workbook:
  - Page margins are set (not default 0.75" all around unless intentional)
  - Print area is defined for sheets with data
  - Orientation matches data layout (landscape for wide tables, portrait for narrow)
  - Paper size is set (Letter or A4)
  - Fit-to-page is configured (fit to 1 page wide, auto height)
  - Print title rows set (header row repeats on every printed page)

STYLE-AWARE: If a style is active, verify sheet_setup matches style spec.
```

## CHECK 2: FONT COMPLIANCE
```
For every cell with content in every worksheet:
  - cell.font.size >= 9 for data cells (minimum readable in print)
  - cell.font.size >= 10 for body text cells
  - cell.font.name is explicitly set (not None / inherited from theme default)
  - cell.font.size is explicitly set (not None / inherited)

STYLE-AWARE: If a style is active, also verify:
  - Heading cells use the style's heading font name
  - Body cells use the style's body font name
  - Font sizes match the style's hierarchy
  - FLAG WARNING if a cell uses a font not in the active style
```

## CHECK 3: COLUMN & DATA INTEGRITY
```
For every data table region:
  - Column widths are explicitly set (not default 8.43)
  - No column is narrower than its header text requires (min_width check)
  - No data is truncated — column width accommodates longest value + padding
  - Numeric columns are right-aligned
  - Text columns are left-aligned
  - Number formats are consistent within each column (no mixed formats)
  - Total table width fits within print margins

Width verification:
  For each column with data:
    max_content_len = max(len(str(cell.value)) for cell in column if cell.value)
    min_required_width = max_content_len + 2  (padding)
    FLAG CRITICAL if column_width < min_required_width * 0.8
    FLAG WARNING if column_width < min_required_width
```

## CHECK 4: DATA TABLE STRUCTURE
```
For every identifiable data table (contiguous data region):
  - Header row exists and is visually distinct (fill, bold, or border)
  - Auto-filter is enabled on the header row
  - Freeze panes is set (header row stays visible)
  - No merged cells within the data body (breaks sorting/filtering)
  - Totals row (if present) is visually distinct (bold, border above)
  - Column order is logical (IDs first, then data, then calculated)

FLAG CRITICAL if:
  - Data table has no header row styling
  - Merged cells exist within data rows
  - Auto-filter is missing on tables with > 10 rows
```

## CHECK 5: PRINT FLOW & PAGINATION
```
For print-oriented sheets:
  - No orphaned headers: column headers are not the last row on a printed page
    (use print_title_rows to repeat headers on every page)
  - Section headers don't appear as the last element on a page
  - Tables are not split awkwardly (keep small tables together)
  - Page breaks are intentional, not random
  - Print area covers all intended content

Detection approach: Estimate page breaks from row heights.
  - Sum row heights from top; when sum exceeds page_height - margins, that's a break
  - Check if a header/separator row falls right at a break boundary
```

## CHECK 6: MERGE & STRUCTURE INTEGRITY
```
For every merged cell range:
  - Only the top-left cell has a value (data in other cells would be lost)
  - Merged cells are not inside data table bodies (breaks sort/filter)
  - Merged cells used for KPI cards have proper accent borders
  - Chart anchors are not inside merged ranges (can cause positioning bugs)
  - No overlapping merged ranges

For chart placements:
  - Charts don't overlap data cells
  - Charts are anchored to appropriate cells
  - Chart dimensions are reasonable (not tiny, not full-sheet unless chart sheet)
```

## CHECK 7: COLOR/FILL INTEGRITY
```
Collect all unique colors from:
  - cell.font.color (text colors)
  - cell.fill.start_color (background fills)
  - cell.border side colors

For each color:
  - Not accidentally default theme blue (#4472C4)
  - Not accidentally default black when style specifies a different dark color

STYLE-AWARE: If a style is active:
  - Every color must match a value in the style's palette dict
    Tolerance: ±15 per RGB channel
  - Exception: pure white (#FFFFFF) and pure black (#000000) always allowed
  - FLAG WARNING for off-palette colors
```

## CHECK 8: SPACING & ALIGNMENT CONSISTENCY
```
For data rows:
  - Row heights are consistent within each table (within ±2pt)
  - Numeric columns are consistently right-aligned
  - Text columns are consistently left-aligned
  - Header row alignment is consistent (typically center)

For KPI card sections:
  - Cards have uniform height
  - Cards have uniform width (column spans)
  - Spacing between cards is consistent (empty column width)

For the entire workbook:
  - Default row height is set (not Excel default 15pt unless intentional)
  - Default column width is set
```

## CHECK 9: STYLE COMPLIANCE (only when a design style is active)

```
Skip this check entirely if no design style was specified.

Load the active style dict from references/style-xlsx-mapping.md.

9a — SHEET SETUP:
  Default row height matches style sheet_setup.default_row_height
  Header row height matches style sheet_setup.header_row_height
  Freeze panes set per style sheet_setup.freeze_row

9b — COVER SHEET:
  Cover sheet pattern matches style's cover_pattern
  Accent colors on cover match style palette
  Cover fonts match style heading font

9c — FONT FAMILIES:
  Collect all unique font names across the workbook:
    Every font must appear in the active style's fonts dict values
    FLAG WARNING for each font not in the style

9d — COLOR PALETTE:
  Collect all unique colors from text, fills, borders:
    Each color must match a style palette value (tolerance: ±15 per RGB channel)
    FLAG WARNING for off-palette colors
    Exception: white, black always allowed

9e — TABLE STYLING:
  All data tables follow the style's table_style pattern
  Header fill matches style palette header_fill
  Header font color matches style palette header_font
  Alt-row fill matches style palette alt_row_fill

9f — CONDITIONAL FORMATTING:
  Positive color matches style conditional_format.positive
  Negative color matches style conditional_format.negative
  Data bar color matches style conditional_format.bar_color

9g — STYLE-SPECIFIC RULES:
  STYLE-01 (Strategy): Max 2 accent colors per sheet, no decorative images
  STYLE-03 (Creative): Dashed accent borders, irregular column widths
  STYLE-04 (Kawaii): Rotating pastel fills across sections, generous row heights
  STYLE-06 (Bold Narrative): Dark inverted KPI cards, thick accent borders
  STYLE-08 (Magazine): Asymmetric column widths, at least one heading >= 16pt
  STYLE-09 (Technical): Code columns in Consolas with warm-white bg fill
  STYLE-11 (Portfolio): Minimal borders, wide columns, generous whitespace
  STYLE-12 (Retro): No pure black — must use dark navy #1B2838
```

## CHECK 10: WORKBOOK STRUCTURE
```
  - Workbook has at least one data sheet with content
  - Sheet names are descriptive (not "Sheet1", "Sheet2", "Sheet3")
  - Sheet tab order is logical (Cover → Dashboard/Summary → Detail → Data)
  - Cover sheet exists (for workbooks with 2+ data sheets)
  - No empty sheets (unless intentionally reserved)
  - Sheet tab colors are set (accent-colored for visual navigation)
```

---

## Iterative Fix Loop

```python
MAX_PASSES = 5

for pass_num in range(1, MAX_PASSES + 1):
    issues = run_all_checks(wb)  # Checks 1-10 (9 only if style active)
    critical = [i for i in issues if i.severity == 'CRITICAL']

    if not critical:
        print(f"Clean after {pass_num - 1} fix passes")
        break

    for issue in issues:
        apply_fix(issue)

    wb.save(path)
    wb = load_workbook(path)  # Reload to get clean state

    print(f"Pass {pass_num}: fixed {len(issues)} issues, re-auditing...")
else:
    print(f"WARNING: {len(critical)} critical issues remain after {MAX_PASSES} passes")
```

---

## Fix Strategies

**FONT COMPLIANCE (CHECK 2):**
1. Set missing font.name to style's body font (or "Calibri" if no style)
2. Set missing font.size to style's body size (or 11 if no style)
3. If font size < minimum, increase to minimum
4. **After font fix → re-run CHECK 3 (column widths may need adjustment)**

**COLUMN WIDTH (CHECK 3):**
1. Recalculate width from max content length + padding
2. Use auto_width() helper to scan all cells in column
3. If total table width exceeds print margins, proportionally reduce widest columns
4. **After width fix → re-run CHECK 5 (print flow) and CHECK 6 (chart positions)**

**TABLE STRUCTURE (CHECK 4):**
1. If no header styling, apply style's header_fill + header_font
2. If auto-filter missing, add auto-filter on header row range
3. If freeze panes missing, set freeze on row below headers
4. If merged cells in data body, unmerge them
5. **After structural changes → re-run CHECK 3 (widths) and CHECK 6 (merges)**

**PRINT FLOW (CHECK 5):**
1. Orphaned header: set print_title_rows to repeat header on every page
2. Awkward table split: adjust page breaks manually
3. **After page break changes → re-run CHECK 10 (structure)**

**COLOR COMPLIANCE (CHECK 7 / CHECK 9d):**
1. Map off-palette colors to nearest palette color by Euclidean RGB distance
2. Replace in-place via cell.font or cell.fill
3. **After color fix → no cascading checks needed**

**SPACING (CHECK 8):**
1. Set consistent row heights within each table
2. Fix inconsistent alignment (right-align all numerics, left-align all text)
3. **After spacing fix → re-run CHECK 5 (print flow)**

---

## False Positive Avoidance

1. **Empty cells with inherited styles:** Only flag cells that contain actual data. Empty cells may inherit font from column/row defaults — this is OK.
2. **Theme-inherited fonts:** Some cells inherit font from the workbook theme. Only flag if the style explicitly requires a different font.
3. **Cover sheet merged cells:** Cover sheet is expected to have merged cells — don't flag these under CHECK 4.
4. **Default column widths:** If a column has no data, default width is fine — don't flag.
5. **Chart sheet structure:** Chart-only sheets don't need headers, auto-filter, or freeze panes.
6. **Conditional formatting colors:** Colors applied by conditional formatting rules are dynamic — don't flag individual cell colors if they come from a CF rule.
7. **Number format inheritance:** Number format "General" on empty cells is OK — only flag when data exists with wrong format.

---

## Output Format

Per-sheet report:
```
[Sheet] [SEVERITY] [CHECK#] — Description → Fix applied / Remaining
```

Final summary:
```
CRITICAL: N (must be 0 before delivery)
WARNING: N (should be 0, acceptable if minor)
INFO: N (advisory)

STYLE: STYLE-XX (Name) or "Default (no style)"
STYLE COMPLIANCE: All checks passed / N issues
PASSES: X until clean
TOTAL FIXES: N applied
```

---

## Key Lessons Learned

1. **openpyxl has NO auto-fit for column widths** — you must calculate widths manually by scanning cell content. Use the `auto_width()` helper function.

2. **Fixing one issue often creates another** — the iterative loop is essential. Column width changes affect print flow. Font size changes affect row heights.

3. **Merged cells are the #1 source of structural bugs** — they break sorting, filtering, and formulas. Use them only for decoration (headers, KPI cards, cover sheets), never in data tables.

4. **Number format consistency is critical** — mixed formats in the same column (e.g., some cells with "$#,##0" and others with "0.00") look unprofessional. Audit all cells in each column.

5. **Excel caches open files** — after openpyxl writes, you MUST close and reopen the file in Excel. AppleScript handles this: close saving no → reopen.

6. **Freeze panes and auto-filter are table essentials** — every data table should have both. Missing freeze panes means users lose sight of headers; missing auto-filter means no sorting/filtering.

7. **Print setup is often forgotten** — always set print_title_rows, fit-to-page-wide, and paper size. Test with AppleScript PDF export.

8. **The audit must be generic** — discover tables dynamically by finding contiguous data regions. Don't hardcode sheet names or cell ranges.

9. **Color drift is subtle** — off-palette colors creep in when styles are applied inconsistently. Always audit all colors against the active palette.

10. **Chart positioning is fragile** — charts anchor to cells. If rows/columns are inserted/deleted, charts shift. Always verify chart positions after structural changes.
