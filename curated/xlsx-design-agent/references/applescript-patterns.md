# AppleScript IPC — Complete Capability Reference for Microsoft Excel

## Table of Contents

1. [Dual-Engine Architecture](#dual-engine-architecture)
2. [Known Quirks](#known-quirks)
3. [Workbook Management](#workbook-management)
4. [Worksheet Navigation](#worksheet-navigation)
5. [Reading Cells](#reading-cells)
6. [Modifying Cells — LIVE](#modifying-cells--live)
7. [Font Properties — LIVE](#font-properties--live)
8. [Cell Formatting — LIVE](#cell-formatting--live)
9. [Recalculation](#recalculation)
10. [Find and Replace — LIVE](#find-and-replace--live)
11. [Range Operations](#range-operations)
12. [Selection Operations](#selection-operations)
13. [Print and Export](#print-and-export)
14. [View Settings](#view-settings)
15. [Comprehensive Workbook Reader](#comprehensive-workbook-reader)
16. [Known Limitations](#known-limitations)
17. [Unit System](#unit-system)
18. [Task Classification Matrix](#task-classification-matrix)
19. [Decision Matrix](#decision-matrix)

## Dual-Engine Architecture

You have **two engines** for manipulating Excel workbooks:

- **openpyxl** (file-based): Bulk creation, cell styling (Font, Fill, Border, Alignment), charts, conditional formatting, data validation, images, named styles, merged cells, formulas. Deterministic, headless, cross-platform.
- **AppleScript IPC** (live editing): Cell value edits, font changes, find/replace, recalculation, PDF export, print settings, view controls — all reflected instantly in the open workbook.

### The Golden Workflow
```
1. openpyxl    →  Create/rebuild workbook (heavy lifting, styles, charts, formatting)
2. AppleScript →  Close any open instance, then open the file in Excel
3. AppleScript →  Recalculate (formulas, pivots)
4. AppleScript →  Verify, make live tweaks
5. AppleScript →  Save (and optionally export PDF)
```

For **edit-only** tasks on an already-open workbook:
```
1. AppleScript →  Read current cell values
2. AppleScript →  Make targeted live edits
3. AppleScript →  Recalculate if formulas depend on edits
4. AppleScript →  Save
   (No openpyxl needed! No file reload!)
```

### Stale Display Warning

**Excel caches open files aggressively.** If openpyxl writes to a file while Excel has it open, Excel will NOT see the changes — it continues showing stale cached data. This is different from Word/PowerPoint which are more graceful about file reloads.

**Mandatory workflow after openpyxl writes:**
```applescript
-- Close WITHOUT saving (discard Excel's stale cache)
-- Then reopen (loads fresh openpyxl-written file from disk)
tell application "Microsoft Excel"
    close active workbook saving no
    delay 0.5
    open "/path/to/file.xlsx"
end tell
```

## Known Quirks

| Issue | Workaround |
|-------|------------|
| Stale display after openpyxl write | Close without saving + reopen (see above) |
| `calculate` can timeout on large workbooks | Set calculation to manual first, calculate specific range |
| `value of cell` returns display text, not underlying value | Use `formula of cell` for formulas, `value of cell` for data |
| Font color setting can be unreliable | Use openpyxl for color changes |
| Large workbook reads can timeout | Read sheet by sheet, range by range |
| Row height/column width units differ from openpyxl | AppleScript uses points; openpyxl uses character units/points |

## Workbook Management

```applescript
-- Open a file
tell application "Microsoft Excel"
    activate
    open "/path/to/file.xlsx"
end tell

-- Save
tell application "Microsoft Excel"
    save active workbook
end tell

-- Save As (new name)
tell application "Microsoft Excel"
    save active workbook in "/path/to/new_file.xlsx"
end tell

-- Close without saving
tell application "Microsoft Excel"
    close active workbook saving no
end tell

-- Close and reopen (MANDATORY after openpyxl edits)
tell application "Microsoft Excel"
    activate
    set filePath to "/path/to/file.xlsx"
    try
        close active workbook saving no
    end try
    delay 0.5
    open filePath
end tell

-- Get workbook info
tell application "Microsoft Excel"
    set wbName to name of active workbook
    set wbPath to full name of active workbook
    set sheetCount to count of worksheets of active workbook
end tell

-- Check if workbook is open
tell application "Microsoft Excel"
    set wbCount to count of workbooks
    if wbCount > 0 then
        set wbName to name of active workbook
    end if
end tell
```

## Worksheet Navigation

```applescript
-- Switch to a worksheet by name
tell application "Microsoft Excel"
    activate object worksheet "Dashboard" of active workbook
end tell

-- Switch to worksheet by index
tell application "Microsoft Excel"
    activate object worksheet 2 of active workbook
end tell

-- Get active sheet name
tell application "Microsoft Excel"
    set sheetName to name of active sheet
end tell

-- List all sheet names
tell application "Microsoft Excel"
    set output to ""
    set sheetCount to count of worksheets of active workbook
    repeat with i from 1 to sheetCount
        set sName to name of worksheet i of active workbook
        set output to output & i & ": " & sName & return
    end repeat
    return output
end tell

-- Add new worksheet
tell application "Microsoft Excel"
    make new worksheet at end of active workbook with properties {name:"New Sheet"}
end tell

-- Rename worksheet
tell application "Microsoft Excel"
    set name of active sheet to "Q4 Dashboard"
end tell

-- Delete worksheet
tell application "Microsoft Excel"
    set display alerts to false
    delete worksheet "Sheet2" of active workbook
    set display alerts to true
end tell
```

## Reading Cells

```applescript
-- Read a single cell value
tell application "Microsoft Excel"
    set cellVal to value of cell "A1" of active sheet
end tell

-- Read a range of cells
tell application "Microsoft Excel"
    set rangeVals to value of range "A1:D10" of active sheet
    -- Returns a list of lists
end tell

-- Read cell with row/column notation
tell application "Microsoft Excel"
    set cellVal to value of cell 3 of row 5 of active sheet
    -- cell 3 = column C, row 5
end tell

-- Read specific cell properties
tell application "Microsoft Excel"
    set c to cell "B2" of active sheet
    set cellVal to value of c
    set cellFormula to formula of c
    set cellFormat to number format of c
    return "Value: " & cellVal & ", Formula: " & cellFormula & ", Format: " & cellFormat
end tell

-- Read used range dimensions
tell application "Microsoft Excel"
    set ur to used range of active sheet
    set rowCount to count of rows of ur
    set colCount to count of columns of ur
    return "Used range: " & rowCount & " rows x " & colCount & " columns"
end tell
```

## Modifying Cells — LIVE

```applescript
-- Set cell value
tell application "Microsoft Excel"
    set value of cell "A1" of active sheet to "Revenue"
    set value of cell "B1" of active sheet to 14800000
end tell

-- Set formula
tell application "Microsoft Excel"
    set formula of cell "C1" of active sheet to "=SUM(B2:B100)"
end tell

-- Clear cell content
tell application "Microsoft Excel"
    clear contents cell "A1" of active sheet
end tell

-- Clear range
tell application "Microsoft Excel"
    clear contents range "A1:D100" of active sheet
end tell

-- Batch update (multiple cells)
tell application "Microsoft Excel"
    tell active sheet
        set value of cell "A1" to "Q4 2024"
        set value of cell "B1" to "Revenue"
        set value of cell "C1" to "Growth"
        set value of cell "A2" to "Product A"
        set value of cell "B2" to 5200000
        set value of cell "C2" to 0.15
    end tell
end tell
```

## Font Properties — LIVE

```applescript
-- Change font of a cell
tell application "Microsoft Excel"
    set c to cell "A1" of active sheet
    set name of font object of c to "Georgia"
    set font size of font object of c to 14
    set bold of font object of c to true
    set italic of font object of c to false
end tell

-- Change font of a range
tell application "Microsoft Excel"
    set r to range "A1:D1" of active sheet
    set name of font object of r to "Calibri"
    set font size of font object of r to 11
    set bold of font object of r to true
end tell

-- Read font properties
tell application "Microsoft Excel"
    set c to cell "A1" of active sheet
    set fName to name of font object of c
    set fSize to font size of font object of c
    set fBold to bold of font object of c
    return "Font: " & fName & " " & fSize & "pt, Bold=" & fBold
end tell

-- Note: font COLOR setting via AppleScript can be unreliable.
-- For reliable color changes, use openpyxl instead.
```

## Cell Formatting — LIVE

```applescript
-- Set number format
tell application "Microsoft Excel"
    set number format of cell "B2" of active sheet to "$#,##0.00"
    set number format of range "C2:C100" of active sheet to "0.0%"
end tell

-- Set alignment
tell application "Microsoft Excel"
    set horizontal alignment of cell "A1" of active sheet to horizontal align center
    set vertical alignment of cell "A1" of active sheet to vertical align center
    -- Options: horizontal align left, center, right, justify
    -- Options: vertical align top, center, bottom
end tell

-- Set wrap text
tell application "Microsoft Excel"
    set wrap text of cell "A1" of active sheet to true
end tell

-- Set row height
tell application "Microsoft Excel"
    set height of row 1 of active sheet to 30  -- points
end tell

-- Set column width
tell application "Microsoft Excel"
    set column width of column 1 of active sheet to 20  -- character units
end tell

-- Merge cells
tell application "Microsoft Excel"
    merge range "A1:D1" of active sheet
end tell

-- Unmerge cells
tell application "Microsoft Excel"
    unmerge range "A1:D1" of active sheet
end tell
```

## Recalculation

**This is a key xlsx-specific need. openpyxl writes formulas but DOES NOT calculate them. Excel must recalculate.**

```applescript
-- Recalculate active workbook (all formulas)
tell application "Microsoft Excel"
    calculate active workbook
end tell

-- Recalculate specific sheet
tell application "Microsoft Excel"
    calculate worksheet "Dashboard" of active workbook
end tell

-- Set calculation mode
tell application "Microsoft Excel"
    -- Automatic (default): formulas recalculate on every change
    set calculation to calculation automatic

    -- Manual: formulas only recalculate when triggered
    set calculation to calculation manual
end tell

-- Force full recalculation (when automatic doesn't catch everything)
tell application "Microsoft Excel"
    set calculation to calculation manual
    delay 0.3
    calculate active workbook
    delay 0.5
    set calculation to calculation automatic
end tell

-- Recalculate after openpyxl edits (full workflow)
tell application "Microsoft Excel"
    activate
    set filePath to full name of active workbook
    close active workbook saving no
    delay 0.5
    open filePath
    delay 1
    calculate active workbook
    delay 0.5
    save active workbook
end tell
```

## Find and Replace — LIVE

```applescript
-- Simple find and replace (all occurrences)
tell application "Microsoft Excel"
    tell active sheet
        replace what "Q3" replacement "Q4" look at part with replace scope replace all
    end tell
end tell

-- Find a value
tell application "Microsoft Excel"
    tell used range of active sheet
        set foundCell to find what "Revenue" look at whole
        if foundCell is not missing value then
            set cellAddr to get address foundCell
            return "Found at: " & cellAddr
        end if
    end tell
end tell
```

## Range Operations

```applescript
-- Copy range
tell application "Microsoft Excel"
    copy range range "A1:D10" of active sheet
end tell

-- Paste to destination
tell application "Microsoft Excel"
    select range "A1:D10" of worksheet "Sheet2" of active workbook
    paste special active sheet what paste values
end tell

-- Sort range
tell application "Microsoft Excel"
    sort range "A1:D100" of active sheet key1 range "B1" of active sheet order1 sort descending
end tell

-- Auto-fit column widths
tell application "Microsoft Excel"
    autofit column range "A:F" of active sheet
end tell

-- Auto-fit row heights
tell application "Microsoft Excel"
    autofit row range "1:100" of active sheet
end tell

-- Insert rows
tell application "Microsoft Excel"
    insert into range row 5 of active sheet
end tell

-- Delete rows
tell application "Microsoft Excel"
    delete range row 5 of active sheet
end tell
```

## Selection Operations

```applescript
-- Select a cell
tell application "Microsoft Excel"
    select cell "A1" of active sheet
end tell

-- Select a range
tell application "Microsoft Excel"
    select range "A1:D10" of active sheet
end tell

-- Get current selection
tell application "Microsoft Excel"
    set selAddr to get address selection
    return "Selection: " & selAddr
end tell

-- Select entire column
tell application "Microsoft Excel"
    select column 1 of active sheet
end tell

-- Go to specific cell (scroll to it)
tell application "Microsoft Excel"
    scroll area of active sheet to range "A1"
end tell
```

## Print and Export

```applescript
-- Export to PDF
tell application "Microsoft Excel"
    save active workbook in "/Users/me/Desktop/output.pdf" as PDF file format
end tell

-- Alternative PDF export via print
tell application "Microsoft Excel"
    -- Use System Events for PDF export via print dialog if direct save fails
end tell

-- Print workbook
tell application "Microsoft Excel"
    print out active workbook
end tell

-- Print specific sheets
tell application "Microsoft Excel"
    print out worksheet "Dashboard" of active workbook
end tell

-- Print settings
tell application "Microsoft Excel"
    tell page setup of active sheet
        set orientation to landscape
        set fit to pages wide to 1
        set fit to pages tall to 0  -- as many as needed
        set left margin to 0.5
        set right margin to 0.5
        set top margin to 0.75
        set bottom margin to 0.75
        set print title rows of active sheet to "$1:$1"  -- repeat header row
    end tell
end tell
```

## View Settings

```applescript
-- Set zoom level
tell application "Microsoft Excel"
    set zoom of active window to 125
end tell

-- Show/hide gridlines
tell application "Microsoft Excel"
    set display gridlines of active window to false
end tell

-- Show/hide row/column headings
tell application "Microsoft Excel"
    set display headings of active window to false
end tell

-- Freeze panes at current selection
tell application "Microsoft Excel"
    select cell "A2" of active sheet
    freeze panes active window
end tell

-- Unfreeze panes
tell application "Microsoft Excel"
    set freeze panes of active window to false
end tell

-- Set view to Page Break Preview
tell application "Microsoft Excel"
    set view of active window to page break preview
    -- Options: normal view, page break preview, page layout view
end tell
```

## Comprehensive Workbook Reader

Copy-paste ready script to audit a workbook:

```applescript
tell application "Microsoft Excel"
    set output to ""
    set wbName to name of active workbook
    set output to output & "Workbook: " & wbName & return

    -- Sheet count
    set sheetCount to count of worksheets of active workbook
    set output to output & "Sheets: " & sheetCount & return

    repeat with i from 1 to sheetCount
        set ws to worksheet i of active workbook
        set sName to name of ws
        set output to output & return & "=== Sheet " & i & ": " & sName & " ===" & return

        -- Used range info
        set ur to used range of ws
        set rowCount to count of rows of ur
        set colCount to count of columns of ur
        set output to output & "Used range: " & rowCount & " rows x " & colCount & " cols" & return

        -- First 15 rows
        set maxRows to rowCount
        if maxRows > 15 then set maxRows to 15
        set maxCols to colCount
        if maxCols > 8 then set maxCols to 8

        repeat with r from 1 to maxRows
            set rowText to ""
            repeat with c from 1 to maxCols
                set cellVal to value of cell c of row r of ws
                if cellVal is missing value then
                    set cellStr to ""
                else
                    set cellStr to cellVal as text
                    if length of cellStr > 20 then
                        set cellStr to text 1 thru 20 of cellStr & "..."
                    end if
                end if
                set rowText to rowText & cellStr & " | "
            end repeat
            set output to output & "  R" & r & ": " & rowText & return
        end repeat
    end repeat

    return output
end tell
```

## Known Limitations

| Capability | Status | Workaround |
|-----------|--------|------------|
| Insert image/chart | Not reliable | Use openpyxl `ws.add_image()` / chart API |
| Set cell fill color | Limited/unreliable | Use openpyxl `PatternFill` |
| Set cell borders | Limited | Use openpyxl `Border` + `Side` |
| Set conditional formatting | Not exposed | Use openpyxl `conditional_formatting` |
| Create charts | Not exposed | Use openpyxl chart API |
| Set named styles | Not exposed | Use openpyxl `NamedStyle` |
| Modify merged cells | Partial | Use openpyxl for merging |
| Set data validation | Not exposed | Use openpyxl `DataValidation` |
| **Recalculate formulas** | **Works well** | Primary use case |
| **Read cell values** | **Works well** | Quick inspection |
| **Edit cell values live** | **Works well** | Fast targeted changes |
| **Find and replace** | **Works well** | Efficient batch changes |
| **Auto-fit columns** | **Works well** | Better than openpyxl (no auto-fit) |
| **PDF export** | **Works well** | Primary use case |
| **Print settings** | **Works well** | Page setup and printing |
| **View controls** | **Works well** | Zoom, gridlines, freeze |

## Unit System

```
AppleScript for Excel uses POINTS for row heights and CHARACTER UNITS for column widths.
openpyxl uses the same units.

Row height:
  Default: 15 points
  1 point = 1/72 inch
  Typical header row: 24-30 points
  Typical data row: 16-20 points

Column width:
  Default: 8.43 character units
  1 character unit ≈ 7 pixels (at Calibri 11pt)
  Typical narrow column: 8-10 chars
  Typical data column: 12-16 chars
  Typical text column: 20-30 chars

Page margins (AppleScript page setup):
  In inches (0.5, 0.75, 1.0, etc.)
```

## Task Classification Matrix

| Task | Tool | Justification |
|------|------|---------------|
| Create new workbook from scratch | **openpyxl** | File-level, no Excel needed |
| Bulk cell formatting (fills, borders, fonts) | **openpyxl** | Better API, batch operations |
| Create charts | **openpyxl** | Chart API, precise control |
| Add conditional formatting | **openpyxl** | Full rule API |
| Add data validation | **openpyxl** | Full validation API |
| Set named styles | **openpyxl** | Style registration API |
| Merge cells | **openpyxl** | Reliable merge/unmerge |
| Add images | **openpyxl** | Image insertion API |
| Set page setup (margins, titles) | **openpyxl** | Full page setup API |
| Batch workbook generation | **openpyxl** | Headless, repeatable |
| **Recalculate formulas** | **AppleScript** | Requires Excel's calc engine |
| **Auto-fit column widths** | **AppleScript** | Excel measures actual text width |
| **Export to PDF** | **AppleScript** | Excel's rendering engine |
| Edit cell values in open workbook | **AppleScript** | Instant, no reload |
| Change font properties live | **AppleScript** | Instant feedback |
| Find and replace text | **AppleScript** | Efficient batch operation |
| Print workbook | **AppleScript** | Requires Excel |
| View/zoom settings | **AppleScript** | Application-level |
| Sort data | **AppleScript** | Live sort on open data |

## Decision Matrix

| User Request | Engine | Why |
|-------------|--------|-----|
| "Create a quarterly dashboard" | **openpyxl** | Full workbook creation |
| "Build a KPI report with charts" | **openpyxl** | Charts + formatting + layout |
| "Add conditional formatting for negative values" | **openpyxl** | Conditional formatting API |
| "Style the header row blue with white text" | **openpyxl** | Cell styling API |
| "Add a data table with auto-filter" | **openpyxl** | Table creation + auto-filter |
| "Generate 20 monthly reports" | **openpyxl** | Batch, headless |
| "Recalculate all formulas" | **AppleScript** | Excel's calculation engine |
| "Auto-fit all column widths" | **AppleScript** | Excel measures text width |
| "Export to PDF" | **AppleScript** | Excel rendering |
| "Change Q3 to Q4 everywhere" | **AppleScript** | Find/replace |
| "What's in cell B5?" | **AppleScript** | Quick read |
| "Update the revenue number" | **AppleScript** | Targeted cell edit |
| "Print 3 copies" | **AppleScript** | Print control |
| "Hide gridlines" | **AppleScript** | View settings |
| "Redesign the entire workbook" | **openpyxl** | Complex rebuild |
| "Create workbook then export PDF" | **Both** | openpyxl builds, AppleScript finalizes |
