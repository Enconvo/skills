# openpyxl Complete Reference

## Table of Contents

1. [Standard Imports](#standard-imports)
2. [Opening and Saving](#opening-and-saving)
3. [Worksheet Operations](#worksheet-operations)
4. [Cell Values & Types](#cell-values--types)
5. [Cell Styling](#cell-styling)
6. [Number Formats](#number-formats)
7. [Named Styles](#named-styles)
8. [Merged Cells](#merged-cells)
9. [Column & Row Dimensions](#column--row-dimensions)
10. [Freeze Panes](#freeze-panes)
11. [Auto-Filter](#auto-filter)
12. [Data Validation](#data-validation)
13. [Conditional Formatting](#conditional-formatting)
14. [Charts](#charts)
15. [Images](#images)
16. [Page Setup & Print](#page-setup--print)
17. [Worksheet Protection](#worksheet-protection)
18. [Reading Workbook Content (Audit)](#reading-workbook-content-audit)
19. [Embedded Helper Functions](#embedded-helper-functions)
20. [Unit Quick Reference](#unit-quick-reference)

---

## Standard Imports

```python
import os
from openpyxl import Workbook, load_workbook
from openpyxl.styles import (
    Font, PatternFill, Border, Side, Alignment, NamedStyle,
    numbers, Protection
)
from openpyxl.styles.differential import DifferentialStyle
from openpyxl.formatting.rule import (
    ColorScaleRule, CellIsRule, DataBarRule, IconSetRule, FormulaRule
)
from openpyxl.chart import (
    BarChart, LineChart, PieChart, AreaChart, ScatterChart, Reference
)
from openpyxl.chart.series import DataPoint
from openpyxl.chart.label import DataLabelList
from openpyxl.utils import get_column_letter, column_index_from_string
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.drawing.image import Image as XlImage
from copy import copy
```

## Opening and Saving

```python
xlsx_path = os.environ['XLSX_PATH']

# Open existing workbook
wb = load_workbook(xlsx_path)
ws = wb.active

# OR create new blank workbook
wb = Workbook()
ws = wb.active
ws.title = "Dashboard"

# ALWAYS save at end:
wb.save(xlsx_path)
```

**Stale Display Warning:** Excel caches open files. If Excel has the file open while openpyxl writes to it, Excel will show stale data. You MUST close and reopen the file in Excel after openpyxl saves. Use AppleScript to automate this:
```
close → save with openpyxl → reopen
```

## Worksheet Operations

```python
# Create new worksheet
ws2 = wb.create_sheet("Data")           # append at end
ws3 = wb.create_sheet("Summary", 0)     # insert at position 0

# Access worksheet by name
ws = wb["Dashboard"]

# List all sheet names
print(wb.sheetnames)  # ['Dashboard', 'Data', 'Summary']

# Rename worksheet
ws.title = "Q4 Dashboard"

# Copy worksheet
ws_copy = wb.copy_worksheet(ws)

# Remove worksheet
wb.remove(ws2)
# OR: del wb["Data"]

# Set active sheet
wb.active = wb["Summary"]

# Set tab color (hex without #)
ws.sheet_properties.tabColor = "0071E3"
```

## Cell Values & Types

```python
# String
ws['A1'] = "Revenue"

# Number
ws['B1'] = 14800000

# Date
from datetime import date, datetime
ws['C1'] = date(2024, 12, 31)
ws['D1'] = datetime.now()

# Formula
ws['E1'] = '=SUM(B2:B100)'
ws['F1'] = '=IF(B1>0,"Positive","Negative")'
ws['G1'] = '=VLOOKUP(A2,Data!A:B,2,FALSE)'

# Boolean
ws['H1'] = True

# None (empty)
ws['I1'] = None

# Access by row, column
ws.cell(row=1, column=1, value="Revenue")

# Iterate rows
for row in ws.iter_rows(min_row=2, max_row=100, min_col=1, max_col=5, values_only=True):
    print(row)  # tuple of values

# Append a row
ws.append(["Product A", 1500, 0.23, "Active"])
```

## Cell Styling

```python
# Font
cell = ws['A1']
cell.font = Font(
    name='Calibri',
    size=11,
    bold=True,
    italic=False,
    color='0B1D3A',       # hex without #
    underline='single',   # 'single', 'double', 'singleAccounting', 'doubleAccounting'
    strike=False,
)

# Fill (background color)
cell.fill = PatternFill(
    start_color='003DA5',  # hex without #
    end_color='003DA5',
    fill_type='solid',
)

# Border
thin_border = Border(
    left=Side(style='thin', color='CCCCCC'),
    right=Side(style='thin', color='CCCCCC'),
    top=Side(style='thin', color='CCCCCC'),
    bottom=Side(style='thin', color='CCCCCC'),
)
cell.border = thin_border
# Border styles: 'thin', 'medium', 'thick', 'double', 'dotted', 'dashed',
#                'dashDot', 'dashDotDot', 'hair', 'mediumDashed',
#                'mediumDashDot', 'mediumDashDotDot', 'slantDashDot'

# Alignment
cell.alignment = Alignment(
    horizontal='center',    # 'left', 'center', 'right', 'justify', 'fill'
    vertical='center',      # 'top', 'center', 'bottom'
    wrap_text=True,
    shrink_to_fit=False,
    indent=0,
    text_rotation=0,        # 0-180 degrees
)

# Copy style to another cell
target = ws['B1']
target.font = copy(cell.font)
target.fill = copy(cell.fill)
target.border = copy(cell.border)
target.alignment = copy(cell.alignment)
target.number_format = cell.number_format
```

## Number Formats

```python
# Integer with comma separator
ws['A1'].number_format = '#,##0'

# Currency
ws['B1'].number_format = '$#,##0.00'
ws['C1'].number_format = '"$"#,##0'           # no decimals

# Percentage
ws['D1'].number_format = '0.0%'
ws['E1'].number_format = '0%'

# Date
ws['F1'].number_format = 'YYYY-MM-DD'
ws['G1'].number_format = 'MMM D, YYYY'
ws['H1'].number_format = 'MM/DD/YYYY'

# Accounting (with alignment)
ws['I1'].number_format = '_($* #,##0.00_);_($* (#,##0.00);_($* "-"??_);_(@_)'

# Custom
ws['J1'].number_format = '#,##0.0"x"'         # e.g., "2.5x"
ws['K1'].number_format = '0.00"M"'            # e.g., "14.80M"
ws['L1'].number_format = '+#,##0;-#,##0;0'    # +/- prefix

# Conditional number format (positive green, negative red)
ws['M1'].number_format = '[Green]+#,##0.0%;[Red]-#,##0.0%;0.0%'
```

## Named Styles

```python
# Create a named style
header_style = NamedStyle(name='header')
header_style.font = Font(name='Calibri', size=11, bold=True, color='FFFFFF')
header_style.fill = PatternFill(start_color='003DA5', end_color='003DA5', fill_type='solid')
header_style.alignment = Alignment(horizontal='center', vertical='center')
header_style.border = Border(
    bottom=Side(style='thin', color='002080')
)

# Register the style with the workbook
wb.add_named_style(header_style)

# Apply to cells
ws['A1'].style = 'header'
ws['B1'].style = 'header'

# Create multiple styles at once
styles = {
    'body': NamedStyle(
        name='body',
        font=Font(name='Calibri', size=11, color='1A1A1A'),
        alignment=Alignment(vertical='center'),
    ),
    'metric': NamedStyle(
        name='metric',
        font=Font(name='Calibri', size=24, bold=True, color='003DA5'),
        alignment=Alignment(horizontal='center', vertical='center'),
    ),
    'caption': NamedStyle(
        name='caption',
        font=Font(name='Calibri', size=9, color='999999'),
    ),
}
for style in styles.values():
    wb.add_named_style(style)

# Apply
ws['A5'].style = 'metric'
ws['A6'].style = 'caption'
```

## Merged Cells

```python
# Merge cells
ws.merge_cells('A1:D1')        # merge A1 through D1
ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=4)

# IMPORTANT: Only the top-left cell of a merged range retains data and style.
# Set value and style on the top-left cell:
ws['A1'] = 'Quarterly Report'
ws['A1'].font = Font(name='Georgia', size=16, bold=True, color='0B1D3A')
ws['A1'].alignment = Alignment(horizontal='center', vertical='center')

# Unmerge
ws.unmerge_cells('A1:D1')

# WARNING: Never merge cells that contain data in non-top-left positions.
# Data in merged-away cells is silently lost.

# Pattern: Use merged cells for section headers, KPI cards, cover sheet titles.
# Never merge within data table body — it breaks sorting and filtering.
```

## Column & Row Dimensions

```python
# Set column width (in character units — approximately 1 char = 7 pixels at default font)
ws.column_dimensions['A'].width = 20
ws.column_dimensions['B'].width = 15

# Set by column number
col_letter = get_column_letter(3)  # 'C'
ws.column_dimensions[col_letter].width = 12

# Set row height (in points — 1 point = 1/72 inch)
ws.row_dimensions[1].height = 30    # header row
ws.row_dimensions[2].height = 20    # data row

# Default dimensions for entire sheet
ws.sheet_format.defaultColWidth = 14
ws.sheet_format.defaultRowHeight = 18

# Hide columns/rows
ws.column_dimensions['F'].hidden = True
ws.row_dimensions[50].hidden = True

# Auto-width calculation helper (see Embedded Helper Functions)
# openpyxl does NOT have auto-fit — you must calculate manually.
```

**Width Unit Quick Reference:**
- Character width unit ≈ 7 pixels (at Calibri 11pt)
- 1 inch ≈ 10.3 character units
- Minimum readable column: 8 chars
- Comfortable data column: 12-16 chars
- Wide text column: 20-30 chars
- Narrow ID column: 6-8 chars

## Freeze Panes

```python
# Freeze top row (header row stays visible while scrolling)
ws.freeze_panes = 'A2'

# Freeze first column
ws.freeze_panes = 'B1'

# Freeze top row AND first column
ws.freeze_panes = 'B2'

# Freeze top 3 rows + first 2 columns
ws.freeze_panes = 'C4'

# Remove freeze
ws.freeze_panes = None
```

## Auto-Filter

```python
# Enable auto-filter on header row
ws.auto_filter.ref = 'A1:F100'

# Auto-detect range from data
from openpyxl.utils import get_column_letter
max_col = ws.max_column
max_row = ws.max_row
ws.auto_filter.ref = f'A1:{get_column_letter(max_col)}{max_row}'

# Add filter criteria (programmatic)
ws.auto_filter.add_filter_column(0, ['Active', 'Pending'])  # column A
ws.auto_filter.add_sort_condition(f'B2:B{max_row}')         # sort by column B
```

## Data Validation

```python
# Dropdown list validation
dv = DataValidation(
    type='list',
    formula1='"Active,Pending,Closed,Archived"',
    allow_blank=True,
)
dv.error = 'Invalid status'
dv.errorTitle = 'Status Error'
dv.prompt = 'Select a status'
dv.promptTitle = 'Status'
ws.add_data_validation(dv)
dv.add('D2:D100')

# Number range validation
dv_num = DataValidation(type='whole', operator='between', formula1=0, formula2=100)
dv_num.error = 'Value must be 0-100'
ws.add_data_validation(dv_num)
dv_num.add('E2:E100')

# Date validation
dv_date = DataValidation(type='date', operator='greaterThan', formula1='2024-01-01')
ws.add_data_validation(dv_date)
dv_date.add('F2:F100')
```

## Conditional Formatting

```python
# Color Scale (green-yellow-red)
ws.conditional_formatting.add(
    'B2:B100',
    ColorScaleRule(
        start_type='min', start_color='DC2626',    # red
        mid_type='percentile', mid_value=50, mid_color='FFEB3B',  # yellow
        end_type='max', end_color='16A34A',         # green
    )
)

# Two-color scale (white to blue)
ws.conditional_formatting.add(
    'C2:C100',
    ColorScaleRule(
        start_type='min', start_color='FFFFFF',
        end_type='max', end_color='003DA5',
    )
)

# Cell value rules (highlight cells)
red_fill = PatternFill(start_color='FFEBEE', end_color='FFEBEE', fill_type='solid')
red_font = Font(color='DC2626', bold=True)
ws.conditional_formatting.add(
    'D2:D100',
    CellIsRule(
        operator='lessThan',
        formula=['0'],
        fill=red_fill,
        font=red_font,
    )
)

green_fill = PatternFill(start_color='E8F5E9', end_color='E8F5E9', fill_type='solid')
green_font = Font(color='16A34A', bold=True)
ws.conditional_formatting.add(
    'D2:D100',
    CellIsRule(
        operator='greaterThan',
        formula=['0'],
        fill=green_fill,
        font=green_font,
    )
)

# Data Bars
ws.conditional_formatting.add(
    'E2:E100',
    DataBarRule(
        start_type='min', end_type='max',
        color='003DA5',
        showValue=True,
    )
)

# Icon Sets (arrows, traffic lights)
ws.conditional_formatting.add(
    'F2:F100',
    IconSetRule(
        icon_style='3Arrows',  # '3Arrows', '3TrafficLights1', '4Arrows', '5Arrows'
        type='percent',
        values=[0, 33, 67],
    )
)

# Formula-based rule
ws.conditional_formatting.add(
    'A2:F100',
    FormulaRule(
        formula=['$G2="Overdue"'],
        fill=PatternFill(start_color='FFEBEE', end_color='FFEBEE', fill_type='solid'),
        font=Font(color='DC2626'),
    )
)
```

## Charts

```python
# Bar Chart
chart = BarChart()
chart.type = 'col'           # 'col' (vertical) or 'bar' (horizontal)
chart.grouping = 'clustered'  # 'clustered', 'stacked', 'percentStacked'
chart.title = 'Revenue by Quarter'
chart.y_axis.title = 'Revenue ($M)'
chart.x_axis.title = 'Quarter'
chart.style = 10              # built-in style number

# Data references
data = Reference(ws, min_col=2, min_row=1, max_col=4, max_row=5)
cats = Reference(ws, min_col=1, min_row=2, max_row=5)
chart.add_data(data, titles_from_data=True)
chart.set_categories(cats)

# Size and position
chart.width = 18   # cm
chart.height = 12  # cm
ws.add_chart(chart, 'H2')  # anchor cell

# Line Chart
line = LineChart()
line.title = 'Trend'
line.y_axis.title = 'Value'
line_data = Reference(ws, min_col=2, min_row=1, max_col=3, max_row=13)
line_cats = Reference(ws, min_col=1, min_row=2, max_row=13)
line.add_data(line_data, titles_from_data=True)
line.set_categories(line_cats)
line.style = 10
ws.add_chart(line, 'H15')

# Pie Chart
pie = PieChart()
pie.title = 'Distribution'
pie_data = Reference(ws, min_col=2, min_row=1, max_row=5)
pie_cats = Reference(ws, min_col=1, min_row=2, max_row=5)
pie.add_data(pie_data, titles_from_data=True)
pie.set_categories(pie_cats)
ws.add_chart(pie, 'H28')

# Area Chart
area = AreaChart()
area.title = 'Cumulative'
area.grouping = 'stacked'
area_data = Reference(ws, min_col=2, min_row=1, max_col=4, max_row=13)
area_cats = Reference(ws, min_col=1, min_row=2, max_row=13)
area.add_data(area_data, titles_from_data=True)
area.set_categories(area_cats)
ws.add_chart(area, 'H41')

# Scatter Chart
scatter = ScatterChart()
scatter.title = 'Correlation'
scatter.x_axis.title = 'Variable X'
scatter.y_axis.title = 'Variable Y'
x_values = Reference(ws, min_col=1, min_row=2, max_row=20)
y_values = Reference(ws, min_col=2, min_row=2, max_row=20)
from openpyxl.chart import Series
series = Series(y_values, x_values, title='Data Points')
scatter.series.append(series)
ws.add_chart(scatter, 'H54')

# Chart styling (palette colors)
from openpyxl.chart.series import DataPoint
from openpyxl.drawing.fill import PatternFillProperties, ColorChoice
# Set series colors programmatically via chart series fill properties
for i, s in enumerate(chart.series):
    s.graphicalProperties.solidFill = palette_colors[i % len(palette_colors)]
```

## Images

```python
from openpyxl.drawing.image import Image as XlImage
from PIL import Image as PILImage

def safe_add_image(ws, img_path, anchor_cell, max_width_cm=18, max_height_cm=12):
    """Insert image preserving aspect ratio.
    max_width_cm/max_height_cm: maximum dimensions in centimeters."""
    pil_img = PILImage.open(img_path)
    w_px, h_px = pil_img.size
    ratio = w_px / h_px

    # Convert max dimensions to pixels (96 DPI)
    max_w_px = max_width_cm * 96 / 2.54
    max_h_px = max_height_cm * 96 / 2.54

    if w_px > max_w_px:
        w_px = max_w_px
        h_px = w_px / ratio
    if h_px > max_h_px:
        h_px = max_h_px
        w_px = h_px * ratio

    img = XlImage(img_path)
    img.width = w_px
    img.height = h_px
    ws.add_image(img, anchor_cell)
    return img


def round_corners(img_path, radius=25, output_path=None):
    """Add rounded corners to image. Returns path to rounded PNG."""
    from PIL import ImageDraw
    img = PILImage.open(img_path).convert('RGBA')
    w, h = img.size
    mask = PILImage.new('L', (w, h), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), (w, h)], radius=radius, fill=255)
    result = PILImage.new('RGBA', (w, h), (255, 255, 255, 0))
    result.paste(img, mask=mask)
    if output_path is None:
        base, _ = os.path.splitext(img_path)
        output_path = f"{base}_rounded.png"
    result.save(output_path, 'PNG')
    return output_path


def crop_to_aspect(img_path, target_w, target_h, output_path=None):
    """Center-crop image to target aspect ratio."""
    img = PILImage.open(img_path)
    src_w, src_h = img.size
    target_ratio = target_w / target_h
    src_ratio = src_w / src_h
    if src_ratio > target_ratio:
        new_w = int(src_h * target_ratio)
        offset = (src_w - new_w) // 2
        crop_box = (offset, 0, offset + new_w, src_h)
    else:
        new_h = int(src_w / target_ratio)
        offset = (src_h - new_h) // 2
        crop_box = (0, offset, src_w, offset + new_h)
    cropped = img.crop(crop_box)
    if output_path is None:
        base, ext = os.path.splitext(img_path)
        output_path = f"{base}_cropped{ext}"
    cropped.save(output_path, quality=95)
    return output_path
```

## Page Setup & Print

```python
# Paper size
ws.page_setup.paperSize = ws.PAPERSIZE_LETTER    # or PAPERSIZE_A4
ws.page_setup.orientation = ws.ORIENTATION_LANDSCAPE  # or ORIENTATION_PORTRAIT

# Margins (in inches)
ws.page_margins.left = 0.5
ws.page_margins.right = 0.5
ws.page_margins.top = 0.75
ws.page_margins.bottom = 0.75
ws.page_margins.header = 0.3
ws.page_margins.footer = 0.3

# Print titles (repeat rows/columns on every printed page)
ws.print_title_rows = '1:1'    # repeat row 1
ws.print_title_cols = 'A:A'    # repeat column A

# Print area
ws.print_area = 'A1:F50'

# Fit to page
ws.page_setup.fitToWidth = 1
ws.page_setup.fitToHeight = 0    # 0 = as many pages as needed vertically
ws.sheet_properties.pageSetUpPr.fitToPage = True

# Header/Footer
ws.oddHeader.center.text = 'Quarterly Report'
ws.oddHeader.center.size = 10
ws.oddFooter.center.text = 'Page &P of &N'
ws.oddFooter.center.size = 9

# Gridlines
ws.sheet_properties.outlinePr = None
ws.page_setup.horizontalCentered = True
```

## Worksheet Protection

```python
# Protect sheet (prevent edits)
ws.protection.sheet = True
ws.protection.password = 'optional_password'

# Allow specific actions on protected sheet
ws.protection.enable()
ws.protection.formatCells = True      # allow cell formatting
ws.protection.formatColumns = True    # allow column resizing
ws.protection.formatRows = True       # allow row resizing
ws.protection.sort = True             # allow sorting
ws.protection.autoFilter = True       # allow filtering

# Unlock specific cells (on a protected sheet)
ws['A1'].protection = Protection(locked=False)
```

## Reading Workbook Content (Audit)

```python
def audit_workbook(wb):
    """Print structured audit of entire workbook."""
    print(f"Sheets: {wb.sheetnames}")
    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        print(f"\n--- Sheet: {sheet_name} ---")
        print(f"  Dimensions: {ws.dimensions}")
        print(f"  Max row: {ws.max_row}, Max col: {ws.max_column}")
        print(f"  Freeze: {ws.freeze_panes}")
        print(f"  Auto-filter: {ws.auto_filter.ref}")

        # Merged cells
        if ws.merged_cells.ranges:
            print(f"  Merged: {list(ws.merged_cells.ranges)}")

        # Sample first 20 rows
        print(f"  Content (first 20 rows):")
        for row in ws.iter_rows(min_row=1, max_row=min(20, ws.max_row),
                                max_col=min(10, ws.max_column), values_only=False):
            cells_info = []
            for cell in row:
                val = str(cell.value)[:30] if cell.value is not None else ''
                font_name = cell.font.name if cell.font.name else 'inherit'
                font_size = cell.font.size if cell.font.size else 'inherit'
                cells_info.append(f"{val} ({font_name}/{font_size})")
            print(f"    Row {row[0].row}: {' | '.join(cells_info)}")

        # Column widths
        print(f"  Column widths:")
        for col_letter in [get_column_letter(i) for i in range(1, min(11, ws.max_column + 1))]:
            w = ws.column_dimensions[col_letter].width
            print(f"    {col_letter}: {w}")
```

## Embedded Helper Functions

Copy-paste these at the top of every Python script. They cover 90% of common operations:

```python
import os
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment, NamedStyle
from openpyxl.utils import get_column_letter
from copy import copy


def hex_to_font_color(hex_str):
    """Convert hex color string to openpyxl font color.
    Accepts '#RRGGBB' or 'RRGGBB'."""
    return hex_str.lstrip('#')


def setup_styles(wb, style_dict):
    """Register NamedStyles from a style dict (from style-xlsx-mapping.md).
    Creates: 'heading', 'subheading', 'body', 'metric', 'caption' named styles."""
    for style_name, font_spec in style_dict['fonts'].items():
        ns = NamedStyle(name=style_name)
        ns.font = Font(
            name=font_spec['name'],
            size=font_spec['size'],
            bold=font_spec.get('bold', False),
            italic=font_spec.get('italic', False),
            color=font_spec['color'],
        )
        if style_name == 'metric':
            ns.alignment = Alignment(horizontal='center', vertical='center')
        elif style_name in ('heading', 'subheading'):
            ns.alignment = Alignment(vertical='center')
        try:
            wb.add_named_style(ns)
        except ValueError:
            pass  # style already registered


def auto_width(ws, min_width=8, max_width=50, padding=2):
    """Calculate and set column widths based on content.
    openpyxl has no auto-fit — this approximates it."""
    for col_cells in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col_cells[0].column)
        for cell in col_cells:
            if cell.value is not None:
                cell_len = len(str(cell.value))
                # Account for bold (wider chars)
                if cell.font and cell.font.bold:
                    cell_len = int(cell_len * 1.1)
                max_len = max(max_len, cell_len)
        width = max(min_width, min(max_len + padding, max_width))
        ws.column_dimensions[col_letter].width = width


def make_header_row(ws, row_num, headers, style_dict):
    """Create a styled header row."""
    pal = style_dict['palette']
    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(row=row_num, column=col_idx, value=header)
        cell.font = Font(
            name=style_dict['fonts'].get('body', {}).get('name', 'Calibri'),
            size=11, bold=True, color=pal['header_font'],
        )
        cell.fill = PatternFill(
            start_color=pal['header_fill'],
            end_color=pal['header_fill'],
            fill_type='solid',
        )
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = Border(
            bottom=Side(style='thin', color=pal.get('accent', '000000'))
        )
    ws.row_dimensions[row_num].height = style_dict['sheet_setup']['header_row_height']


def make_data_rows(ws, start_row, data, style_dict, number_formats=None):
    """Populate data rows with alternating fills.
    data: list of lists. number_formats: dict of {col_idx: format_string}."""
    pal = style_dict['palette']
    body_font = Font(
        name=style_dict['fonts']['body']['name'],
        size=style_dict['fonts']['body']['size'],
        color=pal['body'],
    )
    alt_fill = PatternFill(
        start_color=pal['alt_row_fill'],
        end_color=pal['alt_row_fill'],
        fill_type='solid',
    )
    for row_offset, row_data in enumerate(data):
        row_num = start_row + row_offset
        for col_idx, value in enumerate(row_data, 1):
            cell = ws.cell(row=row_num, column=col_idx, value=value)
            cell.font = copy(body_font)
            cell.alignment = Alignment(vertical='center')
            if row_offset % 2 == 0:
                cell.fill = copy(alt_fill)
            if number_formats and col_idx in number_formats:
                cell.number_format = number_formats[col_idx]
        ws.row_dimensions[row_num].height = style_dict['sheet_setup']['default_row_height']


def make_totals_row(ws, row_num, col_range, style_dict, label="Total"):
    """Add a totals row with SUM formulas."""
    pal = style_dict['palette']
    ws.cell(row=row_num, column=1, value=label).font = Font(
        name=style_dict['fonts']['body']['name'],
        size=style_dict['fonts']['body']['size'],
        bold=True, color=pal['heading'],
    )
    top_border = Border(top=Side(style='double', color=pal.get('accent', '000000')))
    for col_idx in col_range:
        col_letter = get_column_letter(col_idx)
        cell = ws.cell(row=row_num, column=col_idx)
        cell.value = f'=SUM({col_letter}2:{col_letter}{row_num - 1})'
        cell.font = Font(
            name=style_dict['fonts']['body']['name'],
            size=style_dict['fonts']['body']['size'],
            bold=True, color=pal['heading'],
        )
        cell.border = copy(top_border)


def make_kpi_card(ws, start_row, start_col, label, value, note, style_dict, width=3):
    """Create a KPI card using merged cells.
    width: number of columns to merge."""
    pal = style_dict['palette']
    end_col = start_col + width - 1
    end_col_letter = get_column_letter(end_col)
    start_col_letter = get_column_letter(start_col)

    # Top accent border on first row
    for c in range(start_col, end_col + 1):
        cell = ws.cell(row=start_row, column=c)
        cell.border = Border(top=Side(style='medium', color=pal.get('accent', '003DA5')))

    # Label row
    ws.merge_cells(start_row=start_row, start_column=start_col,
                   end_row=start_row, end_column=end_col)
    label_cell = ws.cell(row=start_row, column=start_col, value=label)
    label_cell.font = Font(
        name=style_dict['fonts']['caption']['name'],
        size=style_dict['fonts']['caption']['size'],
        bold=True, color=pal.get('accent', pal['heading']),
    )
    label_cell.alignment = Alignment(horizontal='center', vertical='center')
    if 'kpi_card_bg' in pal:
        label_cell.fill = PatternFill(
            start_color=pal['kpi_card_bg'], end_color=pal['kpi_card_bg'], fill_type='solid')

    # Value row
    ws.merge_cells(start_row=start_row + 1, start_column=start_col,
                   end_row=start_row + 1, end_column=end_col)
    value_cell = ws.cell(row=start_row + 1, column=start_col, value=value)
    value_cell.font = Font(
        name=style_dict['fonts']['metric']['name'],
        size=style_dict['fonts']['metric']['size'],
        bold=True, color=style_dict['fonts']['metric']['color'],
    )
    value_cell.alignment = Alignment(horizontal='center', vertical='center')
    if 'kpi_card_bg' in pal:
        value_cell.fill = PatternFill(
            start_color=pal['kpi_card_bg'], end_color=pal['kpi_card_bg'], fill_type='solid')
    ws.row_dimensions[start_row + 1].height = 36

    # Note row
    ws.merge_cells(start_row=start_row + 2, start_column=start_col,
                   end_row=start_row + 2, end_column=end_col)
    note_cell = ws.cell(row=start_row + 2, column=start_col, value=note)
    note_color = pal['positive'] if '+' in str(note) or '▲' in str(note) else (
        pal['negative'] if '-' in str(note) or '▼' in str(note) else pal['muted'])
    note_cell.font = Font(
        name=style_dict['fonts']['caption']['name'],
        size=style_dict['fonts']['caption']['size'],
        color=note_color,
    )
    note_cell.alignment = Alignment(horizontal='center', vertical='center')
    if 'kpi_card_bg' in pal:
        note_cell.fill = PatternFill(
            start_color=pal['kpi_card_bg'], end_color=pal['kpi_card_bg'], fill_type='solid')


def make_chart(ws, chart_type, data_ref, cat_ref, title, anchor, palette_colors,
               width=18, height=12):
    """Create a styled chart. chart_type: 'bar', 'line', 'pie', 'area', 'scatter'."""
    from openpyxl.chart import BarChart, LineChart, PieChart, AreaChart, ScatterChart
    chart_classes = {
        'bar': BarChart, 'line': LineChart, 'pie': PieChart,
        'area': AreaChart, 'scatter': ScatterChart,
    }
    chart = chart_classes[chart_type]()
    chart.title = title
    chart.width = width
    chart.height = height
    chart.style = 10
    chart.add_data(data_ref, titles_from_data=True)
    if cat_ref:
        chart.set_categories(cat_ref)
    # Apply palette colors to series
    for i, s in enumerate(chart.series):
        if i < len(palette_colors):
            s.graphicalProperties.solidFill = palette_colors[i]
    ws.add_chart(chart, anchor)
    return chart


def make_cover_sheet(ws, title, subtitle, metadata, style_dict):
    """Create a styled cover sheet.
    metadata: dict with keys like 'author', 'date', 'version'."""
    pal = style_dict['palette']

    # Title in merged area (row 8-9, columns A-H)
    ws.merge_cells('A8:H8')
    title_cell = ws['A8']
    title_cell.value = title
    title_cell.font = Font(
        name=style_dict['fonts']['heading']['name'],
        size=style_dict['fonts']['heading']['size'] + 4,
        bold=True, color=pal['heading'],
    )
    title_cell.alignment = Alignment(horizontal='center', vertical='center')
    ws.row_dimensions[8].height = 40

    # Accent border below title
    for col in range(1, 9):
        ws.cell(row=9, column=col).border = Border(
            top=Side(style='medium', color=pal.get('accent', pal['heading']))
        )
    ws.row_dimensions[9].height = 6  # thin accent line

    # Subtitle
    ws.merge_cells('A10:H10')
    sub_cell = ws['A10']
    sub_cell.value = subtitle
    sub_cell.font = Font(
        name=style_dict['fonts'].get('subheading', style_dict['fonts']['body'])['name'],
        size=13, color=pal.get('muted', pal['body']),
    )
    sub_cell.alignment = Alignment(horizontal='center', vertical='center')
    ws.row_dimensions[10].height = 30

    # Metadata
    row = 13
    for key, value in metadata.items():
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=8)
        meta_cell = ws.cell(row=row, column=1, value=f"{key}: {value}")
        meta_cell.font = Font(
            name=style_dict['fonts']['body']['name'],
            size=10, color=pal.get('muted', pal['body']),
        )
        meta_cell.alignment = Alignment(horizontal='center')
        row += 1


def add_conditional_format(ws, cell_range, style_dict):
    """Apply standard positive/negative conditional formatting."""
    cf = style_dict['conditional_format']
    green_fill = PatternFill(start_color='E8F5E9', end_color='E8F5E9', fill_type='solid')
    green_font = Font(color=cf['positive'], bold=True)
    red_fill = PatternFill(start_color='FFEBEE', end_color='FFEBEE', fill_type='solid')
    red_font = Font(color=cf['negative'], bold=True)

    ws.conditional_formatting.add(
        cell_range,
        CellIsRule(operator='greaterThan', formula=['0'],
                   fill=green_fill, font=green_font)
    )
    ws.conditional_formatting.add(
        cell_range,
        CellIsRule(operator='lessThan', formula=['0'],
                   fill=red_fill, font=red_font)
    )


def make_section_separator(ws, row_num, label, style_dict, col_span=8):
    """Add a section separator row with accent styling."""
    pal = style_dict['palette']
    ws.merge_cells(start_row=row_num, start_column=1,
                   end_row=row_num, end_column=col_span)
    cell = ws.cell(row=row_num, column=1, value=label)
    cell.font = Font(
        name=style_dict['fonts']['heading']['name'],
        size=style_dict['fonts']['heading']['size'],
        bold=True, color=pal['heading'],
    )
    cell.alignment = Alignment(vertical='center')
    cell.border = Border(
        bottom=Side(style='medium', color=pal.get('accent', pal['heading']))
    )
    ws.row_dimensions[row_num].height = style_dict['sheet_setup']['header_row_height'] + 4
```

## Unit Quick Reference

| Measurement | Character Units | Points | Pixels (96 DPI) | Centimeters |
|-------------|----------------|--------|-----------------|-------------|
| Default column width | 8.43 | — | 64 | 1.7 |
| Default row height | — | 15 | 20 | 0.53 |
| 1 inch | ~10.3 | 72 | 96 | 2.54 |
| 1 cm | ~4.1 | 28.35 | 37.8 | 1 |
| A4 width | — | 595 | 794 | 21.0 |
| A4 height | — | 842 | 1123 | 29.7 |
| Letter width | — | 612 | 816 | 21.59 |
| Letter height | — | 792 | 1056 | 27.94 |

**openpyxl units:**
- Column width: character units (1 char ≈ 7px at Calibri 11pt)
- Row height: points (1pt = 1/72 inch)
- Chart dimensions: centimeters
- Image dimensions: pixels (display at 96 DPI)
- Page margins: inches

**Key conversions:**
- `width_chars = pixels / 7` (approximate)
- `height_points = pixels * 72 / 96`
- `cm = inches * 2.54`
