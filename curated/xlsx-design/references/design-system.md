# Design System Reference

## Table of Contents

1. [Typography](#typography)
2. [Color Palettes](#color-palettes)
3. [Grid Layout Rules](#grid-layout-rules)
4. [Visual Hierarchy](#visual-hierarchy)
5. [Decorative Elements](#decorative-elements)
6. [Worksheet Structure Patterns](#worksheet-structure-patterns)
7. [Cover Sheet Patterns](#cover-sheet-patterns)
8. [Data Table Design](#data-table-design)
9. [Chart Design](#chart-design)
10. [Image Generation](#image-generation)
11. [Layout Type Catalog](#layout-type-catalog)
12. [Palette Template](#palette-template)

## Typography

- **Minimum data cell font size: 9pt.** Body text minimum 10pt. Headings: 14-18pt.
- Preferred body text: 10-11pt. Section headers: 13-16pt. Titles: 16-20pt.
- Always use a deliberate font pairing:
  - Georgia + Calibri (classic + modern)
  - Cambria + Calibri (warm serif + clean sans)
  - Rockwell + Georgia (editorial elegance)
  - Calibri throughout (safe, systematic)
  - Consolas + Calibri (technical + clean)
- Never use default Calibri for both headings and body without intentional size/weight differentiation.
- **Number formatting is typography.** Consistent decimal places, currency symbols, and percentage formats across all data of the same type.
- Right-align numeric data. Left-align text. Center headers.
- Use bold sparingly — headers, totals, and key metrics only.

## Color Palettes

Define a complete palette before building any workbook.

### Dark Premium (finance, executive reports, luxury)
- Sheet background: White (default)
- Heading color: `#0B1D3A` (deep navy)
- Body text: `#1A202C` (near-black)
- Muted text: `#64748B` (slate gray)
- Accent: `#C9A84C` (gold)
- Header fill: `#0B1D3A` | Header text: `#FFFFFF`
- Alt row: `#F1F5F9`
- KPI card bg: `#F8FAFC` | KPI border: `#C9A84C`
- Positive: `#16A34A` | Negative: `#DC2626`

### Light Clean (startups, tech, education)
- Heading color: `#1E293B`
- Body text: `#334155`
- Muted text: `#94A3B8`
- Accent: `#3B82F6` (blue)
- Header fill: `#3B82F6` | Header text: `#FFFFFF`
- Alt row: `#F0F9FF`
- Positive: `#16A34A` | Negative: `#DC2626`

### Warm Earth (sustainability, nature, lifestyle)
- Heading color: `#2D1B0E`
- Body text: `#44382C`
- Muted text: `#8B7355`
- Accent: `#C2704E` (terracotta)
- Accent 2: `#7C9A6E` (sage green)
- Header fill: `#C2704E` | Header text: `#FFFFFF`
- Alt row: `#FDF8F0`

### Bold Vibrant (creative, marketing, events)
- Heading color: `#0F0F1A`
- Body text: `#1A1A2E`
- Muted text: `#6B7280`
- Accents: `#FF6B6B` (coral) / `#4ECDC4` (teal) / `#FFE66D` (yellow)
- Header fill: `#0F0F1A` | Header text: `#FFFFFF`
- Alt row: `#FAFAFA`

### Corporate Blue (business reports, proposals)
- Heading color: `#1E3A5F`
- Body text: `#2D3748`
- Muted text: `#718096`
- Accent: `#2563EB` (royal blue)
- Accent 2: `#059669` (emerald)
- Header fill: `#1E3A5F` | Header text: `#FFFFFF`
- Alt row: `#F0F4F8`

## Grid Layout Rules

### Column Width Units
- openpyxl column width is measured in **character units** (approximate width of a character at default font)
- 1 character unit ≈ 7 pixels at Calibri 11pt
- 1 inch ≈ 10.3 character units
- **Always calculate column widths explicitly.** Never rely on Excel's auto-fit from openpyxl — it doesn't exist.

### Column Width Guidelines
| Column Type | Width (chars) | Example |
|-------------|--------------|---------|
| Narrow ID/index | 6-8 | Row #, ID |
| Short label | 10-12 | Status, Type |
| Standard data | 12-16 | Numbers, dates |
| Medium text | 16-22 | Names, categories |
| Wide text | 22-30 | Descriptions |
| Extra wide | 30-50 | Notes, comments |

### Row Height Guidelines
| Row Type | Height (points) | Usage |
|----------|----------------|-------|
| Compact data | 15-16 | Dense tables |
| Standard data | 18-20 | Comfortable reading |
| Header row | 24-30 | Column headers |
| Section header | 28-36 | Section breaks |
| KPI metric | 36-48 | Large numbers |
| Cover title | 40-60 | Workbook title |
| Spacer row | 6-10 | Visual separation |

### Content Width Calculation
Before placing ANY element, calculate:
1. **Total columns needed** — plan all columns before building
2. **Sum of column widths** — should fill the desired print width
3. **Print width** = paper width - left margin - right margin
   - Letter (8.5" - 0.5" - 0.5" = 7.5") ≈ 77 character units
   - A4 (8.27" - 0.5" - 0.5" = 7.27") ≈ 75 character units
4. **KPI card sections**: use merged cells spanning 2-4 columns each
5. **Chart placement**: charts span 8-12 columns, 15-25 rows typically

### Merged Cell Discipline
- **DO merge** for: section headers, KPI card areas, cover sheet titles, column group headers
- **NEVER merge** within data table body — it breaks sorting, filtering, and formulas
- **Always style the top-left cell** of a merge — only it retains formatting
- **Merge sparingly** — prefer column width adjustment over excessive merging

### Freeze Panes Strategy
| Scenario | Freeze Setting | Purpose |
|----------|---------------|---------|
| Simple data table | `A2` | Header row stays visible |
| Table with row labels | `B2` | Header row + label column |
| Dashboard with title area | `A4` or `A5` | Title area stays visible |
| Wide table | `C2` | Header + first 2 ID columns |
| Multi-section | None | Let user scroll freely |

## Visual Hierarchy

Layer order (most prominent to least):
1. **KPI metric values** — largest font, bold, accent color
2. **Section headers** — large bold heading font, accent underline
3. **Column headers** — bold, filled background, white text
4. **Data values** — standard body font, right-aligned numbers
5. **Labels and categories** — standard font, left-aligned
6. **Captions and notes** — smallest font, muted color
7. **Decorative elements** — borders, fills (support, don't compete)

## Decorative Elements

Every major section should have at least 2-3 of these:

- **Header row fill**: solid accent color with white bold text. The #1 visual anchor in any table.
- **Alternating row fills**: subtle tint on every other row for scanability. Use palette `alt_row_fill`.
- **Section separator**: merged row with heading font + bottom accent border. Creates visual breaks.
- **KPI card area**: merged cells with accent top border, large metric value, label above, note below.
- **Accent borders**: colored top/bottom borders on key rows (totals, section breaks, headers).
- **Conditional formatting**: color scales, data bars, icon sets — data-driven decoration.
- **Chart elements**: embedded charts with palette colors, clean axis styling.
- **Spacer rows**: empty rows with reduced height (6-10pt) between sections.
- **Column group headers**: merged cells spanning column groups, creating hierarchy.
- **Sheet tab colors**: accent-colored tabs for visual workbook navigation.

### Construction Patterns

**KPI Card (merged cells):**
```
Row N:   [Label          ] ← merged 3 cols, caption font, accent color
Row N+1: [  $14.8B       ] ← merged 3 cols, metric font (24pt bold)
Row N+2: [  +12.3% ▲     ] ← merged 3 cols, caption font, green/red
```

**Section Separator:**
```
Row N:   [   SECTION TITLE                    ] ← merged full width, heading font
Row N+1: [═══════════════════════════════════] ← accent bottom border on row N
```

**Data Table:**
```
Row N:   [HEADER | HEADER | HEADER | HEADER ] ← filled bg, white bold text
Row N+1: [data   | data   | data   | data   ] ← white bg
Row N+2: [data   | data   | data   | data   ] ← alt fill bg
Row N+3: [data   | data   | data   | data   ] ← white bg
...
Row M:   [TOTAL  | total  | total  | total  ] ← bold, double top border
```

## Worksheet Structure Patterns

### 1. Simple Data Table
```
Cover Sheet (title, subtitle, date, author)
─────────────────────────────
Data Sheet
  Header row (frozen)
  Data rows with auto-filter
  Totals row at bottom
```

### 2. KPI Dashboard
```
Dashboard Sheet
  Row 1-3:  Title area (merged)
  Row 4:    Spacer
  Row 5-7:  KPI cards (3-4 across)
  Row 8:    Spacer
  Row 9:    Section header "Revenue Breakdown"
  Row 10+:  Data table with chart alongside
─────────────────────────────
Data Sheet (raw data behind dashboard)
```

### 3. Financial Report
```
Cover Sheet
─────────────────────────────
Summary Sheet
  KPI cards (Revenue, Profit, Margin, Growth)
  Summary table
  Trend chart
─────────────────────────────
Detail Sheet
  Full data table with categories
  Pivot-style subtotals
─────────────────────────────
Charts Sheet (optional)
  Full-page charts
```

### 4. Project Tracker
```
Dashboard Sheet
  Status KPIs (On Track, At Risk, Overdue counts)
  Timeline/Gantt overview
─────────────────────────────
Tasks Sheet
  Full task table (ID, Name, Owner, Status, Start, End, Progress)
  Conditional formatting on Status column
  Auto-filter enabled
─────────────────────────────
Resources Sheet
  Team allocation table
```

### 5. Comparison Matrix
```
Comparison Sheet
  Header: items being compared across columns
  Rows: criteria/features
  Conditional formatting for best/worst values
  Summary row at bottom
─────────────────────────────
Notes Sheet (optional)
  Methodology, sources, definitions
```

## Cover Sheet Patterns

### 1. Classic Corporate
```
┌─────────────────────────────────┐
│                                  │
│                                  │
│     WORKBOOK TITLE               │  ← large, bold, heading font (merged A8:H8)
│     ════════════════             │  ← accent border (row 9)
│     Subtitle / Description       │  ← muted color (merged A10:H10)
│                                  │
│     Author: John Smith           │  ← caption font
│     Date: 2024-12-31             │
│     Version: 1.0                 │
│                                  │
└─────────────────────────────────┘
```

### 2. Bold Banner
```
┌─────────────────────────────────┐
│ ████████████████████████████████ │  ← merged rows with accent fill
│ ████  WORKBOOK TITLE       ████ │  ← white text on dark bg
│ ████████████████████████████████ │
├─────────────────────────────────┤
│                                  │
│     Subtitle                     │
│     Author  ·  Date              │
│                                  │
└─────────────────────────────────┘
```

### 3. Minimal Elegant
```
┌─────────────────────────────────┐
│                                  │
│                                  │
│         WORKBOOK                 │  ← center-aligned, large
│         TITLE                    │
│         ───────                  │  ← short accent border
│         Subtitle                 │
│                                  │
│     Author  ·  Date  ·  v1.0    │  ← bottom area, muted
└─────────────────────────────────┘
```

### 4. Side-Accent
```
┌────┬────────────────────────────┐
│    │                             │
│ A  │    WORKBOOK TITLE           │  ← Column A: accent fill
│ C  │    Subtitle                 │     (full height)
│ C  │                             │
│ E  │    ─────────────            │
│ N  │                             │
│ T  │    Author Name              │
│    │    Date                     │
└────┴────────────────────────────┘
```

## Data Table Design

### Pre-Calculation
Before building ANY table:
1. **Count columns** and decide proportional widths
2. **Sum of column widths** should fit the print width
3. **Minimum column width**: 6 chars for IDs, 12 chars for data
4. **Header row height**: 24-30pt (taller than data rows)
5. **Enable auto-filter** on header row
6. **Freeze the header row** for scrolling

### Table Style Patterns

#### Professional Banded
- Header: palette `header_fill` + white text + bold
- Alternating rows: white and `alt_row_fill`
- Thin borders: light gray (#E2E8F0)
- Totals row: bold + double top border

#### Accent-Top Minimal
- Thick accent-colored top border on header row
- No vertical borders
- Thin horizontal separators only
- Clean, modern look

#### KPI Card Row (as merged cells)
- Each card spans 2-4 columns
- Accent top border per card
- Label + big value + delta note
- Cards separated by empty column

#### Thick Borders (Retro)
- Heavy borders in dark color
- No fills — just strong lines
- Typewriter font in body cells

## Chart Design

### Chart Types by Data
| Data Type | Best Chart | Alternative |
|-----------|-----------|-------------|
| Comparison (categories) | Bar/Column | Table with conditional formatting |
| Trend over time | Line | Area |
| Composition (parts of whole) | Pie (≤6 slices) | Stacked bar |
| Distribution | Scatter | Histogram |
| Cumulative | Area (stacked) | Line |
| Ranking | Horizontal bar | Table with data bars |

### Chart Dimensions
- **Standard chart**: width=18cm, height=12cm (spans ~8 columns, ~20 rows)
- **Wide chart**: width=24cm, height=10cm (spans ~10 columns, ~17 rows)
- **Small chart**: width=12cm, height=8cm (spans ~5 columns, ~13 rows)
- **Dashboard mini**: width=10cm, height=7cm (spans ~4 columns, ~12 rows)

### Chart Styling Rules
1. **Use palette colors** for all series — apply from `chart_colors` list
2. **Title**: heading font, heading color. Keep short (under 40 chars).
3. **Axis labels**: body font, muted color. Include units.
4. **Gridlines**: light gray (#E0E0E0), thin. Horizontal only (remove vertical).
5. **Legend**: bottom or right, body font, muted color
6. **Data labels**: only when chart has few data points (≤6). Caption font size.
7. **No 3D effects**. Flat/2D only.
8. **Chart style**: use `chart.style = 10` as base, then customize colors

### Chart Placement
- Place charts to the RIGHT of data (same rows) or BELOW data (separate section)
- Anchor to a specific cell — charts don't move with data unless anchored properly
- Leave 1-2 empty columns between data and chart
- Never overlap charts with data cells

## Image Generation

### When to Generate Images
- **Cover sheets**: Decorative background or accent illustration
- **Dashboard headers**: Atmospheric images representing the data theme
- **Report branding**: Company logos, section illustrations

### Image Prompt Best Practices

**The image gen tool has NO native AR parameter — AR is requested via prompt text only.**

**Every cover sheet image prompt must include:**
1. **No text**: "No text, no words, no letters, no typography, no watermarks — purely visual."
2. **Landscape ratio**: "16:9 widescreen aspect ratio" (cover sheets are wide)
3. **Color harmony**: Name 2-3 hex colors from active style — image must look cohesive with workbook palette
4. **Visual style**: Match the workbook's design language (clean corporate for STYLE-01, hand-drawn for STYLE-03, pastel for STYLE-04, etc.)
5. **Composition for overlay**: If title cells will sit over the image: "Dark/quiet zone in [center/lower area] for text overlay"
6. **Quality**: "High resolution, clean edges, professional quality"

**Post-generation:** Check actual AR with PIL. If >15% off from 16:9, use `crop_to_aspect()` or regenerate.

### Image in Spreadsheets
- Images are placed as overlays — they float above cells
- Anchor images to specific cells for positioning
- Keep images small — spreadsheets are data-first
- Use `safe_add_image()` helper for aspect-ratio-safe insertion
- Rounded corners add professional polish — use `round_corners()` helper
- Save as PNG for transparency support

### Image Strategy for Spreadsheets
```
Data-heavy (dashboard, report)?
  -> Cover sheet image only. Data tables and charts ARE the visuals.
Presentation-style (executive summary)?
  -> Cover image + small section illustrations
Portfolio/catalog?
  -> Product images alongside data rows
Default:
  -> Skip images. Focus on data presentation.
```

## Layout Type Catalog

### 1. Cover Sheet
**Purpose:** Title page, branding, metadata.
**Structure:** Merged cells for title area, accent borders, metadata rows.
**When:** Every workbook should have one.

### 2. Dashboard
**Purpose:** At-a-glance KPI overview.
**Structure:** KPI cards (merged cells) at top, charts and summary tables below.
**When:** Executive summaries, status reports.

### 3. Data Table
**Purpose:** Structured data display with sorting/filtering.
**Structure:** Header row (frozen) + data rows + totals. Auto-filter enabled.
**When:** Any tabular data — the most common layout.

### 4. KPI Summary
**Purpose:** Key metrics highlighted.
**Structure:** 3-6 KPI cards in a row, each spanning 2-4 columns. Label + value + delta.
**When:** Dashboard top section, executive summary sheets.

### 5. Comparison Matrix
**Purpose:** Side-by-side comparison of items.
**Structure:** Items as columns, criteria as rows. Conditional formatting highlights best/worst.
**When:** Product comparisons, vendor evaluations, feature matrices.

### 6. Chart Sheet
**Purpose:** Full-page chart visualization.
**Structure:** Minimal text, large chart filling most of the sheet. Source data reference.
**When:** Trend analysis, distribution visualizations, presentation-ready charts.

### 7. Report Summary
**Purpose:** Narrative + data hybrid.
**Structure:** Section headers (merged), text in wide merged cells, small tables/KPIs inline.
**When:** Written reports that happen to live in a spreadsheet.

### 8. Timeline / Gantt
**Purpose:** Project timeline visualization.
**Structure:** Tasks as rows, time periods as columns. Conditional formatting creates bars.
**When:** Project tracking, milestone planning, resource scheduling.

## Palette Template

Copy and customize for each workbook:

```python
pal = {
    'heading':       '0B1D3A',
    'body':          '1A202C',
    'muted':         '64748B',
    'accent':        'C9A84C',
    'header_fill':   '0B1D3A',
    'header_font':   'FFFFFF',
    'alt_row_fill':  'F1F5F9',
    'kpi_card_bg':   'F8FAFC',
    'positive':      '16A34A',
    'negative':      'DC2626',
    'border':        'E2E8F0',
    'chart_colors':  ['C9A84C', '0B1D3A', '64748B', '16A34A', 'DC2626'],
}
```
