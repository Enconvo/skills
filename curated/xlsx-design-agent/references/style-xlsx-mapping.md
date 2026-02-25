# Style → openpyxl Implementation Mapping

Concrete openpyxl values for each spreadsheet design style. Read `references/design-styles-catalog.md` for full style descriptions — this file provides code-level implementation.

## Common Imports

```python
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment, NamedStyle
from openpyxl.utils import get_column_letter
```

---

## STYLE-01 — Strategy Consulting

```python
STYLE_01 = {
    "name": "Strategy Consulting",
    "fonts": {
        "heading": {"name": "Georgia", "size": 16, "bold": True, "color": "0B1D3A"},
        "subheading": {"name": "Georgia", "size": 13, "bold": True, "color": "0B1D3A"},
        "body": {"name": "Calibri", "size": 11, "bold": False, "color": "1A1A1A"},
        "metric": {"name": "Calibri", "size": 24, "bold": True, "color": "003DA5"},
        "caption": {"name": "Calibri", "size": 9, "bold": False, "color": "999999"},
    },
    "palette": {
        "heading": "0B1D3A",
        "body": "1A1A1A",
        "muted": "999999",
        "accent": "003DA5",
        "header_fill": "003DA5",
        "header_font": "FFFFFF",
        "alt_row_fill": "F5F5F5",
        "kpi_card_bg": "F8F9FA",
        "positive": "16A34A",
        "negative": "DC2626",
        "chart_colors": ["003DA5", "0B1D3A", "999999", "16A34A", "DC2626"],
    },
    "sheet_setup": {
        "default_row_height": 18,
        "header_row_height": 24,
        "default_col_width": 14,
        "freeze_row": 1,
    },
    "cover_pattern": "classic_corporate",
    "table_style": "banded",
    "accent_border": {"color": "003DA5", "style": "thin"},
    "conditional_format": {"positive": "16A34A", "negative": "DC2626", "bar_color": "003DA5"},
    "design_notes": "No shadows, no 3D. Hairline borders. Max 2 accent colors. Data-first. Precise number formatting.",
}
```

---

## STYLE-02 — Executive Editorial

```python
STYLE_02 = {
    "name": "Executive Editorial",
    "fonts": {
        "heading": {"name": "Rockwell", "size": 16, "bold": True, "color": "C8102E"},
        "subheading": {"name": "Georgia", "size": 13, "bold": True, "color": "333333"},
        "body": {"name": "Georgia", "size": 11, "bold": False, "color": "333333"},
        "metric": {"name": "Georgia", "size": 22, "bold": True, "color": "C8102E"},
        "caption": {"name": "Georgia", "size": 9, "bold": False, "color": "8C8279"},
    },
    "palette": {
        "heading": "C8102E",
        "body": "333333",
        "muted": "8C8279",
        "accent": "C8102E",
        "header_fill": "C8102E",
        "header_font": "FFFFFF",
        "alt_row_fill": "FAF7F2",
        "kpi_card_bg": "FAF7F2",
        "positive": "16A34A",
        "negative": "DC2626",
        "chart_colors": ["C8102E", "333333", "8C8279", "16A34A", "DC2626"],
    },
    "sheet_setup": {
        "default_row_height": 20,
        "header_row_height": 26,
        "default_col_width": 16,
        "freeze_row": 1,
    },
    "cover_pattern": "minimal_elegant",
    "table_style": "accent_top",
    "accent_border": {"color": "C8102E", "style": "thin"},
    "conditional_format": {"positive": "16A34A", "negative": "DC2626", "bar_color": "C8102E"},
    "design_notes": "Generous whitespace via row heights. Crimson accents sparingly. Section separators via thick borders.",
}
```

---

## STYLE-03 — Creative Brief

```python
STYLE_03 = {
    "name": "Creative Brief",
    "fonts": {
        "heading": {"name": "Comic Sans MS", "size": 16, "bold": True, "color": "3C3C3C"},
        "subheading": {"name": "Calibri", "size": 13, "bold": True, "color": "3C3C3C"},
        "body": {"name": "Calibri", "size": 11, "bold": False, "color": "3C3C3C"},
        "metric": {"name": "Calibri", "size": 20, "bold": True, "color": "D46A3C"},
        "caption": {"name": "Calibri", "size": 9, "bold": False, "italic": True, "color": "A0A0A0"},
    },
    "palette": {
        "heading": "3C3C3C",
        "body": "3C3C3C",
        "muted": "A0A0A0",
        "accent": "D46A3C",
        "accent2": "2B4570",
        "header_fill": "3C3C3C",
        "header_font": "FFFFFF",
        "alt_row_fill": "F5F0E1",
        "kpi_card_bg": "F5F0E1",
        "positive": "5A8C46",
        "negative": "C44E3B",
        "chart_colors": ["D46A3C", "2B4570", "3C3C3C", "5A8C46", "C44E3B"],
    },
    "sheet_setup": {
        "default_row_height": 18,
        "header_row_height": 22,
        "default_col_width": 14,
        "freeze_row": 1,
    },
    "cover_pattern": "side_accent",
    "table_style": "thin_borders",
    "accent_border": {"color": "D46A3C", "style": "dashed"},
    "conditional_format": {"positive": "5A8C46", "negative": "C44E3B", "bar_color": "D46A3C"},
    "design_notes": "Loose layout. Intentionally varied column widths. Annotation-style italic notes. Dashed borders.",
}
```

---

## STYLE-04 — Playful / Kawaii

```python
STYLE_04 = {
    "name": "Playful / Kawaii",
    "fonts": {
        "heading": {"name": "Calibri", "size": 16, "bold": True, "color": "4A2040"},
        "subheading": {"name": "Calibri", "size": 13, "bold": True, "color": "4A2040"},
        "body": {"name": "Calibri", "size": 12, "bold": False, "color": "4A2040"},
        "metric": {"name": "Calibri", "size": 22, "bold": True, "color": "4A2040"},
        "caption": {"name": "Calibri", "size": 9, "bold": False, "color": "A0A0A0"},
    },
    "palette": {
        "heading": "4A2040",
        "body": "4A2040",
        "muted": "A0A0A0",
        "accent": "FFAB91",
        "accent2": "81D4FA",
        "bg_pink": "FFD6E0",
        "bg_lavender": "E8D5F5",
        "bg_mint": "D5F5E3",
        "header_fill": "FFD6E0",
        "header_font": "4A2040",
        "alt_row_fill": "FFF0F5",
        "kpi_card_bg": "E8D5F5",
        "positive": "66BB6A",
        "negative": "EF5350",
        "chart_colors": ["FFAB91", "81D4FA", "FFD6E0", "E8D5F5", "D5F5E3"],
    },
    "sheet_setup": {
        "default_row_height": 22,
        "header_row_height": 28,
        "default_col_width": 15,
        "freeze_row": 1,
    },
    "cover_pattern": "bold_banner",
    "table_style": "pastel_banded",
    "accent_border": {"color": "FFAB91", "style": "thin"},
    "conditional_format": {"positive": "66BB6A", "negative": "EF5350", "bar_color": "FFAB91"},
    "design_notes": "Generous row heights. Soft colors. Rotate pastel fills across sections. Extra cell padding.",
}
```

---

## STYLE-05 — Corporate Modern

```python
STYLE_05 = {
    "name": "Corporate Modern",
    "fonts": {
        "heading": {"name": "Calibri", "size": 16, "bold": True, "color": "1D1D1F"},
        "subheading": {"name": "Calibri", "size": 13, "bold": False, "color": "6E6E73"},
        "body": {"name": "Calibri", "size": 11, "bold": False, "color": "1D1D1F"},
        "metric": {"name": "Calibri", "size": 24, "bold": True, "color": "0071E3"},
        "caption": {"name": "Calibri", "size": 9, "bold": False, "color": "6E6E73"},
    },
    "palette": {
        "heading": "1D1D1F",
        "body": "1D1D1F",
        "muted": "6E6E73",
        "accent": "0071E3",
        "header_fill": "0071E3",
        "header_font": "FFFFFF",
        "alt_row_fill": "F8F9FA",
        "kpi_card_bg": "FFFFFF",
        "kpi_card_border": "D1D1D6",
        "positive": "16A34A",
        "negative": "DC2626",
        "chart_colors": ["0071E3", "6E6E73", "1D1D1F", "16A34A", "DC2626"],
    },
    "sheet_setup": {
        "default_row_height": 18,
        "header_row_height": 24,
        "default_col_width": 14,
        "freeze_row": 1,
    },
    "cover_pattern": "classic_corporate",
    "table_style": "banded",
    "accent_border": {"color": "0071E3", "style": "thin"},
    "conditional_format": {"positive": "16A34A", "negative": "DC2626", "bar_color": "0071E3"},
    "design_notes": "Card-style sections via bordered ranges. Systematic spacing. Blue accent underlines. KPI cards prominent.",
}
```

---

## STYLE-06 — Bold Narrative

```python
STYLE_06 = {
    "name": "Bold Narrative",
    "fonts": {
        "heading": {"name": "Arial Black", "size": 18, "bold": True, "color": "1A1A40"},
        "subheading": {"name": "Calibri", "size": 13, "bold": True, "color": "1A1A40"},
        "body": {"name": "Calibri", "size": 11, "bold": False, "color": "1A1A40"},
        "metric": {"name": "Calibri", "size": 28, "bold": True, "color": "FFB300"},
        "caption": {"name": "Calibri", "size": 9, "bold": False, "color": "6E6E73"},
    },
    "palette": {
        "heading": "1A1A40",
        "body": "1A1A40",
        "muted": "6E6E73",
        "accent": "FFB300",
        "accent2": "1E88E5",
        "accent3": "E91E63",
        "header_fill": "1A1A40",
        "header_font": "FFFFFF",
        "alt_row_fill": "F5F5F5",
        "kpi_card_bg": "1A1A40",
        "kpi_card_font": "FFFFFF",
        "positive": "66BB6A",
        "negative": "EF5350",
        "chart_colors": ["FFB300", "1E88E5", "E91E63", "1A1A40", "66BB6A"],
    },
    "sheet_setup": {
        "default_row_height": 20,
        "header_row_height": 28,
        "default_col_width": 16,
        "freeze_row": 1,
    },
    "cover_pattern": "bold_banner",
    "table_style": "accent_top",
    "accent_border": {"color": "FFB300", "style": "thick"},
    "conditional_format": {"positive": "66BB6A", "negative": "EF5350", "bar_color": "FFB300"},
    "design_notes": "Large dramatic titles. Dark inverted KPI cards. Thick accent borders. Cinematic whitespace via row heights.",
}
```

---

## STYLE-07 — Warm Organic

```python
STYLE_07 = {
    "name": "Warm Organic",
    "fonts": {
        "heading": {"name": "Cambria", "size": 16, "bold": True, "color": "2D1B0E"},
        "subheading": {"name": "Cambria", "size": 13, "bold": True, "color": "2D1B0E"},
        "body": {"name": "Calibri", "size": 11, "bold": False, "color": "44382C"},
        "metric": {"name": "Cambria", "size": 22, "bold": True, "color": "C2704E"},
        "caption": {"name": "Calibri", "size": 9, "bold": False, "color": "8B7355"},
    },
    "palette": {
        "heading": "2D1B0E",
        "body": "44382C",
        "muted": "8B7355",
        "accent": "C2704E",
        "accent2": "7C9A6E",
        "header_fill": "C2704E",
        "header_font": "FFFFFF",
        "alt_row_fill": "FDF8F0",
        "kpi_card_bg": "FEF7ED",
        "positive": "7C9A6E",
        "negative": "C2704E",
        "chart_colors": ["C2704E", "7C9A6E", "8B7355", "2D1B0E", "D4C5B0"],
    },
    "sheet_setup": {
        "default_row_height": 20,
        "header_row_height": 26,
        "default_col_width": 15,
        "freeze_row": 1,
    },
    "cover_pattern": "minimal_elegant",
    "table_style": "accent_top",
    "accent_border": {"color": "C2704E", "style": "thin"},
    "conditional_format": {"positive": "7C9A6E", "negative": "C2704E", "bar_color": "C2704E"},
    "design_notes": "Generous whitespace. Warm tones. Two-color accent (terracotta + sage). Nothing harsh.",
}
```

---

## STYLE-08 — Magazine Editorial

```python
STYLE_08 = {
    "name": "Magazine Editorial",
    "fonts": {
        "heading": {"name": "Georgia", "size": 18, "bold": True, "color": "0A0A0A"},
        "subheading": {"name": "Georgia", "size": 14, "bold": True, "color": "0A0A0A"},
        "body": {"name": "Georgia", "size": 10, "bold": False, "color": "0A0A0A"},
        "metric": {"name": "Georgia", "size": 24, "bold": True, "color": "0A0A0A"},
        "caption": {"name": "Calibri", "size": 9, "bold": False, "color": "757575"},
    },
    "palette": {
        "heading": "0A0A0A",
        "body": "0A0A0A",
        "muted": "757575",
        "accent": "FFD600",
        "accent2": "E91E63",
        "accent3": "1A237E",
        "header_fill": "0A0A0A",
        "header_font": "FFFFFF",
        "alt_row_fill": "F5F5F5",
        "kpi_card_bg": "0A0A0A",
        "kpi_card_font": "FFFFFF",
        "positive": "16A34A",
        "negative": "DC2626",
        "chart_colors": ["0A0A0A", "FFD600", "E91E63", "1A237E", "757575"],
    },
    "sheet_setup": {
        "default_row_height": 18,
        "header_row_height": 26,
        "default_col_width": 15,
        "freeze_row": 1,
    },
    "cover_pattern": "bold_banner",
    "table_style": "minimal_rules",
    "accent_border": {"color": "0A0A0A", "style": "thick"},
    "conditional_format": {"positive": "16A34A", "negative": "DC2626", "bar_color": "FFD600"},
    "design_notes": "Asymmetric column widths. Massive headings. Thick divider borders. One bold accent per sheet. High contrast.",
}
```

---

## STYLE-09 — Technical Documentation

```python
STYLE_09 = {
    "name": "Technical Documentation",
    "fonts": {
        "heading": {"name": "Calibri", "size": 14, "bold": True, "color": "2C2C2C"},
        "subheading": {"name": "Calibri", "size": 12, "bold": True, "color": "2C2C2C"},
        "body": {"name": "Calibri", "size": 11, "bold": False, "color": "2C2C2C"},
        "code": {"name": "Consolas", "size": 10, "bold": False, "color": "2C2C2C"},
        "metric": {"name": "Calibri", "size": 18, "bold": True, "color": "E53935"},
        "caption": {"name": "Calibri", "size": 9, "bold": False, "color": "757575"},
    },
    "palette": {
        "heading": "2C2C2C",
        "body": "2C2C2C",
        "muted": "757575",
        "accent": "E53935",
        "accent2": "FFEB3B",
        "code_bg": "F0EDE8",
        "header_fill": "2C2C2C",
        "header_font": "FFFFFF",
        "alt_row_fill": "F8F8F8",
        "kpi_card_bg": "EBF5FF",
        "warning_bg": "FFFDE7",
        "error_bg": "FFEBEE",
        "positive": "16A34A",
        "negative": "E53935",
        "chart_colors": ["2C2C2C", "E53935", "FFEB3B", "16A34A", "757575"],
    },
    "sheet_setup": {
        "default_row_height": 16,
        "header_row_height": 22,
        "default_col_width": 14,
        "freeze_row": 1,
    },
    "cover_pattern": "classic_corporate",
    "table_style": "banded",
    "accent_border": {"color": "E0E0E0", "style": "thin"},
    "conditional_format": {"positive": "16A34A", "negative": "E53935", "bar_color": "2C2C2C"},
    "design_notes": "Scannable. Code columns in Consolas + warm-white bg. Numbered sections. Note/Warning/Error callout fills.",
}
```

---

## STYLE-10 — Dashboard Report

```python
STYLE_10 = {
    "name": "Dashboard Report",
    "fonts": {
        "heading": {"name": "Calibri", "size": 14, "bold": True, "color": "1C1C1E"},
        "subheading": {"name": "Calibri", "size": 11, "bold": True, "color": "1C1C1E"},
        "body": {"name": "Calibri", "size": 10, "bold": False, "color": "1C1C1E"},
        "metric": {"name": "Calibri", "size": 28, "bold": True, "color": "0071E3"},
        "metric_label": {"name": "Calibri", "size": 9, "bold": False, "color": "A0A0A0"},
        "caption": {"name": "Calibri", "size": 9, "bold": False, "color": "A0A0A0"},
    },
    "palette": {
        "heading": "1C1C1E",
        "body": "1C1C1E",
        "muted": "A0A0A0",
        "accent_blue": "0071E3",
        "accent_green": "34C759",
        "accent_purple": "AF52DE",
        "accent_orange": "FF9F0A",
        "header_fill": "1C1C1E",
        "header_font": "FFFFFF",
        "alt_row_fill": "F5F5F7",
        "kpi_card_bg": "F5F5F7",
        "positive": "34C759",
        "negative": "FF3B30",
        "chart_colors": ["0071E3", "34C759", "AF52DE", "FF9F0A", "1C1C1E"],
    },
    "sheet_setup": {
        "default_row_height": 16,
        "header_row_height": 22,
        "default_col_width": 12,
        "freeze_row": 1,
    },
    "cover_pattern": "minimal_elegant",
    "table_style": "kpi_cards",
    "accent_border": {"color": "D1D1D6", "style": "thin"},
    "conditional_format": {"positive": "34C759", "negative": "FF3B30", "bar_color": "0071E3"},
    "design_notes": "Metric-forward. KPI cards prominent. Color-coded metrics. Dense but organized. Narrow default widths.",
}
```

---

## STYLE-11 — Portfolio / Gallery

```python
STYLE_11 = {
    "name": "Portfolio / Gallery",
    "fonts": {
        "heading": {"name": "Calibri", "size": 14, "bold": False, "color": "1A1A1A"},
        "body": {"name": "Calibri", "size": 10, "bold": False, "color": "757575"},
        "caption": {"name": "Calibri", "size": 9, "bold": False, "color": "757575"},
    },
    "palette": {
        "heading": "1A1A1A",
        "body": "757575",
        "muted": "A0A0A0",
        "accent": "E60023",
        "header_fill": "1A1A1A",
        "header_font": "FFFFFF",
        "alt_row_fill": "FAFAFA",
        "kpi_card_bg": "FFFFFF",
        "kpi_card_border": "EAEAEA",
        "positive": "16A34A",
        "negative": "DC2626",
        "chart_colors": ["1A1A1A", "E60023", "757575", "EAEAEA", "16A34A"],
    },
    "sheet_setup": {
        "default_row_height": 20,
        "header_row_height": 24,
        "default_col_width": 18,
        "freeze_row": 1,
    },
    "cover_pattern": "bold_banner",
    "table_style": "invisible",
    "accent_border": {"color": "EAEAEA", "style": "thin"},
    "conditional_format": {"positive": "16A34A", "negative": "DC2626", "bar_color": "1A1A1A"},
    "design_notes": "Minimal borders. Wide columns. Small elegant captions. Generous row heights. Clean gallery presentation.",
}
```

---

## STYLE-12 — Retro / Vintage

```python
STYLE_12 = {
    "name": "Retro / Vintage",
    "fonts": {
        "heading": {"name": "Rockwell", "size": 16, "bold": True, "color": "1B2838"},
        "subheading": {"name": "Rockwell", "size": 13, "bold": True, "color": "1B2838"},
        "body": {"name": "Consolas", "size": 10, "bold": False, "color": "1B2838"},
        "metric": {"name": "Rockwell", "size": 22, "bold": True, "color": "0078BF"},
        "caption": {"name": "Consolas", "size": 9, "bold": False, "color": "5A6A7A"},
    },
    "palette": {
        "heading": "1B2838",
        "body": "1B2838",
        "muted": "5A6A7A",
        "accent": "0078BF",
        "accent2": "FF665E",
        "accent3": "00A95C",
        "bg_paper": "F2E8D5",
        "header_fill": "1B2838",
        "header_font": "F2E8D5",
        "alt_row_fill": "F2E8D5",
        "kpi_card_bg": "F2E8D5",
        "positive": "00A95C",
        "negative": "FF665E",
        "chart_colors": ["0078BF", "FF665E", "00A95C", "1B2838", "5A6A7A"],
    },
    "sheet_setup": {
        "default_row_height": 20,
        "header_row_height": 26,
        "default_col_width": 14,
        "freeze_row": 1,
    },
    "cover_pattern": "side_accent",
    "table_style": "thick_borders",
    "accent_border": {"color": "1B2838", "style": "medium"},
    "conditional_format": {"positive": "00A95C", "negative": "FF665E", "bar_color": "0078BF"},
    "design_notes": "Max 2-3 colors. No pure black — use dark navy #1B2838. Typewriter body. Paper bg tint fills.",
}
```

---

## Style Application Workflow

When applying a style, follow this order:

1. **Set sheet defaults** — default row height, column widths from style `sheet_setup`
2. **Register NamedStyles** — create heading, body, metric styles from style fonts + palette
3. **Apply palette colors** — all fills, borders, font colors from style palette
4. **Build cover sheet** — using the style's `cover_pattern`
5. **Style data tables** — using the style's `table_style` pattern
6. **Apply conditional formatting** — using style's `conditional_format` colors
7. **Follow design notes** — style-specific layout decisions
8. **Run the mandatory audit** — style changes don't exempt from quality checks
