# xlsx-design-agent

A Claude Code skill for creating and editing professional Excel workbooks on macOS with premium design quality.
macOS 上的专业 Excel 工作簿创建与编辑技能，具备高品质表格设计。

## Architecture

**Dual-engine approach** for macOS Excel automation:

| Engine | Technology | Role |
|--------|-----------|------|
| **openpyxl** | openpyxl + lxml (file-based) | Bulk creation, styles, tables, charts, images, conditional formatting, data validation, named styles |
| **AppleScript IPC** | osascript (live editing) | Cell edits, font properties, recalculation, auto-fit columns, find/replace, PDF export |

**Golden Rule:** Build with openpyxl, finalize with AppleScript. For edit-only tasks on an open workbook, use AppleScript alone (no openpyxl, no file reload).

**Stale Display Warning:** Excel caches open files. After openpyxl writes, you must close and reopen the workbook via AppleScript to see changes — Excel will NOT auto-refresh from disk.

## Features / 功能

- **Create workbooks from scratch** — Premium design with cover sheets, KPI cards, data tables, charts, conditional formatting / 从零创建工作簿，含封面、KPI 卡片、数据表、图表、条件格式等高品质设计
- **Live-edit open workbooks** — AppleScript IPC for cells, fonts, recalculation, find/replace / 通过 AppleScript 实时编辑已打开的工作簿
- **Grid-first design philosophy** — Column widths, row heights, merged cells, freeze panes as primary layout tools / 网格优先设计，以列宽、行高、合并单元格和冻结窗格为核心布局手段
- **AI image generation** — Cover sheet art and dashboard illustrations / AI 生成封面图与仪表盘插图
- **12 curated design styles** — From Strategy Consulting to Retro Vintage / 12 种精选设计风格，从战略咨询到复古风
- **5 built-in color palettes** — Dark Premium, Light Clean, Warm Earth, Bold Vibrant, Corporate Blue / 五套内置配色方案
- **Dual-engine architecture** — openpyxl for building, AppleScript for live tweaks and finalization / 双引擎架构：openpyxl 构建 + AppleScript 实时调整

## Requirements

- **macOS** (AppleScript IPC requires Microsoft Excel for Mac)
- **Python 3** with `openpyxl`, `lxml`, and `Pillow`
- **Microsoft Excel** installed

## Installation

1. Copy the `xlsx-design-agent/` folder into your Claude Code skills directory:

```bash
cp -r xlsx-design-agent ~/.claude/skills/
```

2. Install Python dependencies:

```bash
python3 -m pip install openpyxl lxml Pillow
```

## Skill Structure

```
xlsx-design-agent/
├── README.md                              # This file
├── SKILL.md                               # Main skill configuration & 19 critical rules
└── references/
    ├── python-openpyxl-reference.md       # openpyxl API reference & helper functions
    ├── applescript-patterns.md            # AppleScript live IPC patterns & decision matrix
    ├── design-system.md                   # Typography, palettes, grid layout, chart design
    ├── design-styles-catalog.md           # 12 curated design styles with full specs
    ├── style-xlsx-mapping.md              # Concrete openpyxl values for all 12 styles
    └── audit-system.md                    # 10-check mandatory quality audit system
```

## Workflows

### New Workbook (Full Build)

```
1. Analyze:    Content structure, worksheet plan, column layout
2. Style:      Choose design style, palette, fonts
3. Generate:   AI images for cover sheet (if requested)
4. openpyxl:   Build worksheets section by section
5. Audit:      Run mandatory 10-check audit, fix issues iteratively
6. AppleScript: Open in Excel, recalculate, auto-fit
7. AppleScript: Verify visually, make live tweaks
8. AppleScript: Save / Export PDF
```

### Edit Existing (Live IPC)

```
1. AppleScript: Read content from open workbook
2. AppleScript: Make targeted live edits (cells, fonts, find/replace)
3. AppleScript: Recalculate if needed
4. AppleScript: Save
   (No openpyxl needed!)
```

### Redesign

```
1. openpyxl:   Catalog all content (sheets, cells, styles, charts)
2. Plan:       New design, palette, structure
3. openpyxl:   Rebuild the workbook
4. AppleScript: Close and reopen the file
5. AppleScript: Verify, tweak, save
```

### Quick Fix

```
AppleScript: Read -> edit -> save (no openpyxl needed)
```

## Usage

Once installed, Claude Code will automatically use this skill when you ask it to create or edit Excel workbooks. Examples:

- "Create a professional quarterly financial report spreadsheet"
- "Build a KPI dashboard with charts and conditional formatting"
- "Redesign this workbook with a dark premium theme"
- "Add a summary sheet with totals and sparklines"
- "Create a project tracker with status indicators"

## License

MIT
