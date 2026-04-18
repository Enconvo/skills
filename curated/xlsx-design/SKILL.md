---
name: xlsx-design
description: "Expert Excel workbook design agent for macOS using openpyxl and AppleScript. Creates and edits stunning, professional spreadsheets with premium design quality. Use when: (1) Creating new Excel workbooks from scratch with openpyxl, (2) Editing or redesigning existing .xlsx files, (3) Building workbooks with custom design (KPI dashboards, styled data tables, charts, conditional formatting, cover sheets), (4) Live editing workbooks via AppleScript IPC (cell values, fonts, recalculation, PDF export), (5) Refreshing/recalculating workbooks live in Excel on macOS, (6) Generating AI images for cover sheets and section headers, (7) Any task requiring openpyxl code generation with design best practices."
---

# Excel Workbook Design Agent

Expert Excel workbook design agent on macOS. openpyxl + lxml is the sole editing engine for workbook content; AppleScript is used for **app lifecycle + finalization** (open, close, recalculate, auto-fit, PDF export). AI images are optional for cover sheets only.

**Core doctrine:** openpyxl edits the file. AppleScript moves the window and recalculates. Grid-first — cells, rows, columns, widths, freezes — not freeform graphics.

## Workflow Gate (decide before you touch anything)

Sort the request into ONE of three lanes and follow that lane's rules. Do NOT force every request through the full plan.

| Lane | Trigger | Plan phase | Task tracking | Audit |
|---|---|---|---|---|
| **Trivial tweak** | Single-cell edit, one format change, a one-line formula fix on an existing workbook | Skip — just do it | None | Skip (not a new build) |
| **Small build** (1–4 sheets) | Small workbook, known style, clear content | Short inline plan (3–5 bullets). Confirm style + images in 1 turn. | Lightweight: 1 task per sheet | Mandatory |
| **Full build** (5+ sheets, dashboards, redesign) | Multi-sheet report, KPI dashboard, workbook redesign, anything with >1 chart | Full Pre-Build Workflow below (Phase 1 → 2 → 3) with explicit approval gates | Canonical template below (mandatory) | Mandatory |

**If uncertain, ask the user which lane fits.** Do not default to the heaviest lane "just in case" — it wastes the user's time.

## Task Tracking (Small build and Full build)

For any build lane, open a task list up front and keep it fresh as you go — it is your memory across long contexts.

### Canonical template (Full build — copy and adapt)

```
[ ] Phase 1: Content analysis & sheet structure (wait for approval)
[ ] Phase 2: Style selection (wait for approval)
[ ] Phase 3: Image strategy — cover only, yes/no (wait for approval)
[ ] Generate cover image (if yes) + verify AR with PIL
[ ] Build Sheet 1: <name>
[ ] Build Sheet 2: <name>
[ ] ... (one task per sheet)
[ ] Snapshot file, run audit Pass 1
[ ] Apply audit fixes, Pass 2 (repeat up to 5)
[ ] AppleScript: close+reopen, recalculate, auto-fit
[ ] AppleScript: visual verification screenshot/read
[ ] Deliver audit summary + file path
```

### Lightweight template (Small build)

```
[ ] Confirm style + image choice (single turn)
[ ] Build <N> sheets
[ ] Audit + fix loop
[ ] Recalculate + auto-fit in Excel
[ ] Deliver
```

Mark tasks completed as soon as they're done. Never batch completions.

## Pre-Build Workflow (Full build lane only)

### Phase 1: Content Analysis & Structure Planning (MANDATORY)

Analyze the content BEFORE touching style.

1. Classify content: Financial / KPI Dashboard / Project Tracker / Comparison / Report / Inventory.
2. Propose a worksheet structure table:

```
| # | Sheet Name | Purpose | Layout Type | Key Content |
|---|-----------|---------|-------------|-------------|
| 1 | Cover | Title page | Cover Sheet | Title, subtitle, metadata |
| 2 | Dashboard | KPI overview | Dashboard | 4 KPI cards, summary chart |
| 3 | Revenue | Detailed data | Data Table | Monthly revenue by product |
```

3. **Wait for user approval.**

Content type → layout mix:

| Content Type | Typical Layout Mix |
|---|---|
| Financial | Cover, KPI Summary, Data Tables, Charts |
| KPI Dashboard | Cover, Dashboard, KPI Summary, Chart Sheets |
| Project Tracker | Cover, Dashboard, Data Tables, Timeline/Gantt |
| Comparison | Cover, Comparison Matrix, Data Tables |
| Report | Cover, Report Summary, Data Tables, Charts |
| Inventory / Catalog | Cover, Data Tables (primary), KPI Summary |

### Phase 2: Style Selection

If user specifies a style → confirm and proceed.
If not → recommend one based on content type:

| Content Type | Recommended Style |
|---|---|
| Financial (P&L, forecasts) | STYLE-01 (Strategy Consulting) |
| Executive summary | STYLE-02 (Executive Editorial) |
| Creative planning | STYLE-03 (Creative Brief) |
| Fun brand, lifestyle | STYLE-04 (Playful / Kawaii) |
| SaaS metrics, product | STYLE-05 (Corporate Modern) |
| Brand story, annual | STYLE-06 (Bold Narrative) |
| Sustainability, wellness | STYLE-07 (Warm Organic) |
| Editorial annual report | STYLE-08 (Magazine Editorial) |
| API data, engineering | STYLE-09 (Technical Documentation) |
| KPI dashboard, analytics | STYLE-10 (Dashboard Report) |
| Portfolio catalog | STYLE-11 (Portfolio / Gallery) |
| Indie/retro brand | STYLE-12 (Retro / Vintage) |
| Generic / unclear | STYLE-02 (default) |

**If NONE of the 12 fit**, generate a **custom style** using the exact dict schema in [Style → openpyxl Mapping](references/style-xlsx-mapping.md). The audit (CHECK 9) validates custom styles identically — missing required keys will fail.

### Phase 3: Image Enhancement (cover sheet only)

Spreadsheets don't need per-sheet images. Ask once:

```
Would you like an AI-generated cover image?
  • Yes — HD 16:9 image tailored to content + style palette.
  • No — Typography-only cover with styled cells.
```

**Wait for response.** If yes:

1. Prompt must include: `No text/letters/words/watermarks`, `16:9 widescreen`, 2–3 palette hex colors, visual style matching the active style, a quiet text zone declaration.
2. After generation, verify with PIL — if AR deviates >15% from 16:9 (~1.78), regenerate or use `crop_to_aspect()`. Never insert an unverified image.
3. Browser-based image tools (e.g. grok-image-gen) run **sequentially**, never in parallel. API tools may run in parallel.

## Environment & Dependencies

Workbook file path lives in `XLSX_PATH`. Every Python script reads `os.environ['XLSX_PATH']`.

```bash
python3 -m pip install openpyxl lxml Pillow --quiet
```

## Dual-Engine Architecture

- **openpyxl** (file-based): all content, styling (Font/Fill/Border/Alignment), charts, conditional formatting, data validation, images, named styles, merges, formulas.
- **AppleScript IPC**: app lifecycle (open/close/quit), recalculate, auto-fit columns, find/replace, PDF export. No design work.

**Golden Rule:** Build with openpyxl, finalize with AppleScript.

**Stale Display Warning:** Excel caches open files. After openpyxl writes, you MUST close and reopen in Excel via AppleScript, or changes stay invisible.

**App-presence check (mandatory before AppleScript calls):**

```bash
osascript -e 'id of app "Microsoft Excel"' 2>/dev/null
```

If this fails (Excel not installed), skip all AppleScript steps and deliver the .xlsx with a note: "Excel not detected — open manually to recalculate formulas."

See [AppleScript Patterns](references/applescript-patterns.md) for the full live IPC matrix.

## Workflows

### New Workbook (Full Build)
1. Phase 1 → 2 → 3 (approval gates).
2. Generate cover image (if yes) + PIL verify.
3. openpyxl: build sheets one at a time, style each from the active style dict.
4. Snapshot + **mandatory audit loop** (CHECKs 1–10, up to 5 passes) per [Audit System](references/audit-system.md).
5. AppleScript (if Excel present): close+reopen, recalculate, auto-fit, visual verify.
6. Save / export PDF.
7. Report audit summary and file path.

### Edit Existing (Live IPC)
1. AppleScript: read cell values + sheet structure.
2. Minor edits → AppleScript. Major redesign → openpyxl.
3. Recalculate, save.

### Redesign
1. Read everything (sheets, cells, charts, styles) via openpyxl.
2. Phase 1–3 for new design.
3. openpyxl: rebuild preserving data, restyle everything.
4. Close+reopen, recalculate, auto-fit, verify, save.

### Quick Fix (Trivial tweak lane)
AppleScript: read → edit → recalc → save. No openpyxl, no audit.

## Priority Zero: Grid Integrity

**These rules override everything else.**

### Column Widths — MANDATORY
openpyxl has NO auto-fit. Calculate every width. Use `auto_width()` (min_width=6 to match design-system.md). Add 2-char padding. Verify total width fits print margins.

### Number Formats — MANDATORY
Same data type → same format, applied to the whole column. Pick ONE currency format, ONE percent format, ONE date format per workbook.

### Merge Cell Discipline — MANDATORY
Merges break sorting/filtering/formulas. Merge only for: cover titles, section headers, KPI cards, column group headers. **Never merge inside data table bodies.** Style only the top-left cell of a merge.

## Mandatory Audit — NON-NEGOTIABLE

Every new or redesigned workbook runs the audit before delivery. Details: [Audit System](references/audit-system.md).

- Runs 10 CHECKs + iterative fix loop with **snapshot-and-rollback** (regressions revert automatically).
- Never deliver a workbook with unresolved CRITICAL issues — surface them in the final report.
- Always report: CRITICAL count, WARNING count, fixes applied, passes needed.

## Palette Contract (read before any helper call)

All layout helpers (`make_header_row`, `make_kpi_card`, `add_accent_border`, etc.) consume a **flat `pal` dict of hex strings**, not a rich style dict. The mapping module exposes:

- `_REQUIRED_PAL_KEYS` — the minimum set every helper expects (`heading`, `body`, `muted`, `accent`, `header_fill`, `header_font`, `alt_row_fill`, `positive`, `negative`).
- `_validate_pal(pal, caller="...")` — raises ValueError on missing keys.
- `style_to_pal(style_dict)` — adapts a style dict (preset or custom) into the flat pal dict with sensible fallbacks.

**Never pass a raw style dict** into a helper expecting `pal`. Always adapt via `style_to_pal()` first. This is the #1 silent-bug trap in this skill.

## 5 Rule Clusters

### Cluster 1 — Grid & Format Discipline
1. Never set any font below 9pt (body ≥ 10pt, data ≥ 9pt).
2. Always set explicit column widths; calculate from content via `auto_width()`.
3. Always set number formats explicitly, per column, consistent across the workbook.
4. Right-align numbers, left-align text, center headers.
5. Never merge cells in data table body rows.

### Cluster 2 — Structure & Navigation
6. Always freeze the header row in data tables.
7. Always enable auto-filter on data tables with >10 rows.
8. Prefer more sheets over dense sheets.
9. Set print titles so header rows repeat on every printed page.
10. Use alternating row fills for readability.

### Cluster 3 — Style & Consistency
11. Use NamedStyles (heading, body, metric, caption) and apply everywhere — don't re-register on every build.
12. Adapt style dicts to `pal` via `style_to_pal()` before any helper call.
13. Match every color, font, and fill to the active style dict (preset or custom).
14. Never use emoji in cells — use labels or conditional-format icons.
15. Surgical edits only: preserve existing design when fixing a bug.

### Cluster 4 — Build Process
16. Build incrementally: one sheet per tool call for Full builds; announce before each.
17. Always save at the end of every Python script (`wb.save(xlsx_path)`).
18. Always reload (`load_workbook(path)`) after saving before auditing.
19. Snapshot the file before each audit pass; revert on regression (see audit-system.md).
20. Use the task tracker — mark tasks done as they finish, not in bulk at the end.

### Cluster 5 — Finalization & Delivery
21. Check Excel presence before AppleScript calls; skip AppleScript gracefully if absent.
22. After openpyxl writes, close and reopen in Excel (stale display).
23. Recalculate formulas via AppleScript before declaring done.
24. Auto-fit columns via AppleScript where appropriate (after recalc).
25. Never deliver an unaudited workbook. Always report the audit summary.
26. Honestly surface remaining CRITICAL issues in the final report — never silently deliver.

## References

- **[openpyxl Reference](references/python-openpyxl-reference.md)**: full API, helper functions (`auto_width`, `make_header_row`, `make_kpi_card`, charts, etc.), `pal` contract + `style_to_pal()` adapter. Read before writing any openpyxl code.
- **[AppleScript Patterns](references/applescript-patterns.md)**: live IPC reference, Excel presence check, decision matrix, known limits (stale display). Read before any Excel automation.
- **[Design System](references/design-system.md)**: typography, palettes, grid layout, chart design, 8 layout types. Read before designing a workbook.
- **[Design Styles Catalog](references/design-styles-catalog.md)**: 12 curated styles (STYLE-01 … STYLE-12). Read when selecting or recommending a style.
- **[Style → openpyxl Mapping](references/style-xlsx-mapping.md)**: exact dict schema for presets + custom styles, palette values, cover patterns. Read alongside the catalog.
- **[Audit System](references/audit-system.md)**: 10 CHECKs, snapshot-and-rollback iterative fix loop, cascading fix strategies, custom-style validation. Read before running the audit.
