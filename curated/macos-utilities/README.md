# macOS Utilities

macOS utility toolkit for Claude Code: screenshot capture.
macOS 实用工具合集，适用于 Claude Code：截屏捕获。

## Features / 功能

- **Select Area Screenshot** — Freely select any screen area to capture / 自由选择屏幕区域截图
- **Current Screen Screenshot** — Capture the full active screen display / 捕获当前活动屏幕全屏截图
- **Frontmost App Screenshot** — Capture the active app window, supports full scrollable content / 捕获当前活动应用窗口，支持滚动长截图
- **Select Window Screenshot** — Click to select a window to capture / 点击选择窗口截图

## Install

Copy this skill folder to your Claude Code skills directory:

```bash
cp -r macos-utilities ~/.claude/skills/macos-utilities
```

Or clone from the skills repo:

```bash
git clone https://github.com/Enconvo/skills.git /tmp/enconvo-skills
cp -r /tmp/enconvo-skills/curated/macos-utilities ~/.claude/skills/macos-utilities
```

## Requirements

- macOS
- [Claude Code](https://claude.com/claude-code)
- [Enconvo](https://enconvo.com) running locally (provides screenshot APIs on `localhost:54535`)

## Quick Start

```
# Take a screenshot of selected area
Ask: "take a screenshot of this area"

# Capture the current screen
Ask: "screenshot my current screen"

# Capture the frontmost app
Ask: "screenshot the frontmost app"

# Capture with full scrollable content
Ask: "screenshot the frontmost app with full scrollable content"

# Select a window to capture
Ask: "take a screenshot of a specific window"
```
