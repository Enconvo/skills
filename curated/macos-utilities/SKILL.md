---
name: macos-utilities
description: "macOS utility toolkit: screenshot capture (select area, current screen, frontmost app, select window). Activates on: screenshot, take screenshot, capture screen, screen capture, select area screenshot, frontmost app screenshot, select window screenshot, or any screenshot request."
---

# macOS Utilities Skill

macOS utility skill for screenshot capture. Uses Enconvo HTTP APIs for screenshot operations.

## API Base URL

All HTTP API calls use base URL: `http://localhost:54535`

All API calls are **POST** requests with `Content-Type: application/json`.

---

## Screenshot Capture

Take screenshots via Enconvo's screenshot API. All screenshot endpoints return the captured image path.

### Select Area Screenshot

Lets the user freely select an area on screen to capture.

**Endpoint:** `POST http://localhost:54535/command/call/screen_shot_action/screenshot`

**Parameters:** None required.

**Example:**

```bash
curl -X POST http://localhost:54535/command/call/screen_shot_action/screenshot \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Current Screen Screenshot

Captures a full screenshot of the currently active screen display.

**Endpoint:** `POST http://localhost:54535/command/call/screen_shot_action/screenshot_current_screen`

**Parameters:** None required.

**Example:**

```bash
curl -X POST http://localhost:54535/command/call/screen_shot_action/screenshot_current_screen \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Frontmost App Screenshot

Captures a screenshot of the currently active (frontmost) application window.

**Endpoint:** `POST http://localhost:54535/command/call/screen_shot_action/screenshot_frontmost_app`

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `capture_full_content` | `boolean` | No | Capture the entire scrollable area when the window supports scrolling (default: `false`) |

**Example:**

```bash
# Capture visible area only
curl -X POST http://localhost:54535/command/call/screen_shot_action/screenshot_frontmost_app \
  -H "Content-Type: application/json" \
  -d '{}'

# Capture full scrollable content
curl -X POST http://localhost:54535/command/call/screen_shot_action/screenshot_frontmost_app \
  -H "Content-Type: application/json" \
  -d '{"capture_full_content": true}'
```

### Select Window Screenshot

Lets the user click on a window to capture it.

**Endpoint:** `POST http://localhost:54535/command/call/screen_shot_action/user_select_window_screenshot`

**Parameters:** None required.

**Example:**

```bash
curl -X POST http://localhost:54535/command/call/screen_shot_action/user_select_window_screenshot \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Decision Matrix

| Need | Command |
|------|---------|
| Capture a specific region | `screenshot` (select area) |
| Capture the entire screen | `screenshot_current_screen` |
| Capture the active app window | `screenshot_frontmost_app` |
| Capture full scrollable content of active app | `screenshot_frontmost_app` with `capture_full_content: true` |
| Let user pick a window to capture | `user_select_window_screenshot` |

After capturing, use the **Read** tool (file read) to view the screenshot content.
