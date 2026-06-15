# Visible Surface Control

Use this reference when a walkthrough depends on the user seeing the same browser/app surface as the tutor, or when the tutor needs to point at a visible element.

## Foreground Rule

Before the first teaching beat, and after any navigation, tab switch, app switch, file picker, or native Settings action, make the target surface frontmost. Do not assume `background:false`, a selected tab, or a successful navigation means the user can see it.

Preferred browser command:

```bash
scripts/foreground_browser.sh "Google Chrome" "optioncharts.io"
```

- Arg 1: browser app name, default `Google Chrome`; also supports `Microsoft Edge`, `Brave Browser`, `Arc`, `Safari`, `Google Chrome Canary`, and `Chromium`.
- Arg 2: optional URL substring used to select the matching tab before raising the window.
- The script activates the browser, selects the matching tab when possible, un-minimizes windows via `AXMinimized`, makes the process frontmost, and prints `STATUS: OK` or `STATUS: WARN`.

After running it, verify with a screenshot or current app/browser state. Start teaching only when the target page/app is visibly frontmost.

Manual fallback if the script is unavailable:

```bash
osascript -e 'tell application "Google Chrome" to activate' \
  -e 'tell application "Google Chrome" to set index of window 1 to 1' \
  -e 'tell application "System Events" to tell process "Google Chrome" to set frontmost to true'
```

If the foreground check fails, retry once. If it still fails, tell the user briefly that visibility control is blocked and continue only with a clearly labeled fallback.

## Cursor Pointing

In live tutoring, point at the exact visible thing being explained. The sequence is:

1. Name the element.
2. Move the cursor to it.
3. Give the takeaway.

For web pages/canvas charts, prefer browser-page coordinates when browser automation provides mouse movement. Re-capture after every scroll, zoom, or layout change because coordinates become stale.

For native apps or non-DOM targets, use:

```bash
scripts/point_cursor.sh point X Y
scripts/point_cursor.sh circle CX CY [R] [LOOPS]
scripts/point_cursor.sh underline X1 Y X2
```

`point_cursor.sh` uses macOS logical points through `cliclick`. If coordinates came from a 2x Retina screenshot, divide raw pixels by 2. Keep gestures short so the cursor helps the user rather than distracting them.

## EnConvo Frontmost Path

For EnConvo setup walkthroughs:

1. Press `Cmd+Shift+D` to bring Smart Bar forward.
2. Press `Cmd+,` while Smart Bar or EnConvo is active to open global Settings.
3. Verify the Settings window is frontmost before teaching or changing anything.

Use the menu bar path `EnConvo -> Settings` only as a fallback.
