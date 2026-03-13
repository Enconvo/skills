# pptx-design-agent

A Claude Code skill for creating and editing professional PowerPoint presentations on macOS with premium design quality.
macOS 上的专业 PowerPoint 演示文稿创建与编辑技能，具备高品质视觉设计。

## Demo Gallery

All demos are generated entirely by this skill — no manual editing. Download any `.pptx` from the [`demo/`](demo/) folder and open in PowerPoint to see the full design.

### Text & Shape Only (No Background Images)

Pure python-pptx output — gradients, cards, shapes, and typography only. Tiny file sizes (~36KB each).

| Style | File | Description |
|-------|------|-------------|
| **STYLE-01** Strategy Consulting | [Demo](demo/PPTX_Demo_Style01_Strategy_Consulting.pptx) | Clean consulting deck with structured layouts and KPI panels |
| **STYLE-02** Executive Editorial | [Demo](demo/PPTX_Demo_Style02_Executive_Editorial.pptx) | Sophisticated serif typography with editorial spacing |
| **STYLE-03** Sketch Hand-Drawn | [Demo](demo/PPTX_Demo_Style03_Sketch_Hand_Drawn.pptx) | Playful hand-drawn aesthetic with organic shapes |
| **STYLE-04** Kawaii Cute | [Demo](demo/PPTX_Demo_Style04_Kawaii_Cute.pptx) | Pastel colors with rounded, friendly design elements |
| **STYLE-05** Corporate Modern | [Demo](demo/PPTX_Demo_Style05_Corporate_Modern.pptx) | Professional and clean with modern grid layouts |
| **STYLE-06** Anime Manga | [Demo](demo/PPTX_Demo_Style06_Anime_Manga.pptx) | Bold, dynamic panels inspired by manga aesthetics |
| **STYLE-08** Editorial Magazine | [Demo](demo/PPTX_Demo_Style08_Editorial_Magazine.pptx) | Magazine-style spreads with editorial typography |
| **STYLE-09** Storyboard Sequential | [Demo](demo/PPTX_Demo_Style09_Storyboard_Sequential.pptx) | Comic/storyboard panel flow with sequential narrative |
| **STYLE-10** Bento Grid | [Demo](demo/PPTX_Demo_Style10_Bento_Grid.pptx) | Japanese bento-box inspired grid layouts |
| **STYLE-11** Bricks Masonry | [Demo](demo/PPTX_Demo_Style11_Bricks_Masonry.pptx) | Pinterest-style masonry card layouts |
| **STYLE-12** Retro Risograph | [Demo](demo/PPTX_Demo_Style12_Retro_Risograph.pptx) | Vintage risograph print aesthetic with halftone textures |

### With AI-Generated Background Images

Full composition design — AI-generated backgrounds with semi-transparent overlay cards, text scrims, and intentional negative space for content placement.

| Style | File | Description |
|-------|------|-------------|
| **Coffee 3D Clay** | [Demo](demo/Coffee_Style07_3D_Clay_BG.pptx) | 3D clay render backgrounds with warm earth tones and transparent cards — "The World of Coffee" |
| **Coffee Fashion Editorial** | [Demo](demo/With%20Back_Ground_IMG-Coffee_Fashion_Editorial.pptx) | Fashion editorial photography backgrounds with coffee theme |
| **K-Beauty BG (Fixed)** | [Demo](demo/With_Background_Img-PPTX_Demo_BG_Fixed.pptx) | Bold anime-style backgrounds with K-Beauty content |
| **Executive Editorial BG** | [Demo](demo/With_Background_Img-PPTX_Demo_Style02_Executive_Editorial_BG.pptx) | Sophisticated editorial backgrounds with light overlay |
| **Executive Editorial BG Dark** | [Demo](demo/With_Background_Img-PPTX_Demo_Style02_Executive_Editorial_BG_Dark.pptx) | Same editorial style with dark mood variant |
| **Editorial Magazine BG** | [Demo](demo/With_Background_Img-PPTX_Demo_Style08_Editorial_Magazine_BG.pptx) | Magazine-style backgrounds with editorial composition |

### Background Images Used

The `coffee_style07_images/` folder contains the 5 AI-generated background images used in the Coffee 3D Clay demo:
- `slide1_title_bg.png` — Title slide background
- `slide2_origin_bg.png` — Origin story background
- `slide3_beans_bg.png` — Bean varieties background
- `slide4_brewing_bg.png` — Brewing methods background
- `slide5_closing_bg.png` — Closing slide background

---

## Architecture

**Dual-engine approach** for macOS PowerPoint automation:

| Engine | Technology | Role |
|--------|-----------|------|
| **python-pptx** | python-pptx + lxml (file-based) | Bulk creation, gradients, corner radius, letter spacing, images, charts, tables |
| **AppleScript IPC** | osascript (live editing) | Text edits, font properties, positions, fills, z-order, visibility, rotation, shadows, speaker notes, slide management |

**Golden Rule:** Build with python-pptx, tweak with AppleScript. For edit-only tasks on an open presentation, use AppleScript alone (no python-pptx, no file reload).

**No stale display issue:** Unlike the xlsx skill, python-pptx writes files without PowerPoint open, so AppleScript's `open POSIX file` always loads a fresh copy from disk.

## Features / 功能

- **Create presentations from scratch** — Premium design with gradients, cards, KPI panels, charts, tables / 从零创建演示文稿，含渐变、卡片、KPI 面板、图表等高品质设计
- **Live-edit open presentations** — AppleScript IPC for text, fonts, positions, fills, z-order, shadows, speaker notes / 通过 AppleScript 实时编辑已打开的演示文稿
- **Composition-first design** — Plan image + overlay as one design with intentional negative space / 构图优先设计，图片与叠加层统一规划留白区域
- **AI image generation** — Slide backgrounds and content illustrations / AI 生成幻灯片背景与内容插图
- **5 built-in color palettes** — Dark Premium, Light Clean, Warm Earth, Bold Vibrant, Tropical Dark / 五套内置配色方案
- **10 creative layout patterns** — Layout rhythm across slides / ���种创意版式，幻灯片间节奏变化
- **26 critical rules** — Including width-first text box sizing to prevent wrapping cascades / 26 条核心规则，含宽度优先文本框计算，防止换行溢出级联问题
- **12 curated design styles** — Strategy Consulting to Retro Risograph / 12 种精选设计风格
- **3-phase pre-build workflow** — Content analysis → style selection → image strategy / 三阶段预构建流程

## Requirements

- **macOS** (AppleScript IPC requires Microsoft PowerPoint for Mac)
- **Python 3** with `python-pptx` and `lxml`
- **Microsoft PowerPoint** installed

## Installation

1. Copy the `pptx-design-agent/` folder into your Claude Code skills directory:

```bash
cp -r pptx-design-agent ~/.claude/skills/
```

2. Install Python dependencies:

```bash
python3 -m pip install python-pptx lxml
```

## Skill Structure

```
pptx-design-agent/
├── README.md                              # This file
├── SKILL.md                               # Main skill configuration & 26 critical rules
├── demo/                                  # 18 demo presentations (downloadable)
│   ├── PPTX_Demo_Style01-12_*.pptx       # Text/shape-only demos (12 styles)
│   ├── With_Background_Img-*.pptx         # AI background image demos
│   ├── Coffee_Style07_3D_Clay_BG.pptx    # 3D clay render demo
│   └── coffee_style07_images/             # AI-generated background PNGs
└── references/
    ├── python-pptx-reference.md           # python-pptx API reference, helpers, overlap checker
    ├── applescript-patterns.md            # Full live IPC capability reference & decision matrix
    ├── design-system.md                   # Palettes, layouts, composition planning, image generation
    ├── design-styles-catalog.md           # 12 curated design styles (STYLE-01 to STYLE-12)
    ├── style-pptx-mapping.md             # Concrete RGBColor values, font configs per style
    └── audit-system.md                    # 12 mandatory post-build audit checks
```

## Workflows

### New Presentation (Full Build)

```
1. Plan:        Palette, fonts, composition strategy, layout rhythm
2. Generate:    AI images with intentional negative space for content zones
3. python-pptx: Build slides one at a time (one per tool call)
4. AppleScript: Open file in PowerPoint
5. AppleScript: Navigate & verify each slide visually
6. AppleScript: Make live tweaks (text, positions)
7. AppleScript: Save
```

### Edit Existing (Live IPC)

```
1. AppleScript: Read all slides/shapes/text (enumerate)
2. AppleScript: Make targeted live edits
3. AppleScript: Save
   (No python-pptx needed!)
```

### Redesign

```
1. AppleScript: Catalog everything (read all shapes/text)
2. Plan:        New design, palette, image strategy
3. Generate:    New images
4. python-pptx: Rebuild each slide
5. AppleScript: Close and reopen the file
6. AppleScript: Verify, tweak, save
```

### Quick Fix

```
AppleScript: Read -> edit -> save (no python-pptx needed)
```

## Usage

Once installed, Claude Code will automatically use this skill when you ask it to create or edit PowerPoint presentations. Examples:

- "Create a 10-slide pitch deck for my startup"
- "Build a quarterly business review presentation"
- "Redesign this presentation with a dark premium theme"
- "Change the title on slide 3 to 'Q4 Results'"
- "Add a background image to the title slide"

## License

MIT
