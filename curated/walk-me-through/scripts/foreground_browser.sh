#!/usr/bin/env bash
# foreground_browser.sh — reliably bring a browser window to the FRONT so the
# user can actually watch the live walkthrough. Fixes the recurring bug where
# browser-use/navigate with background:false only switches the tab but leaves
# the window minimized, behind other apps, or on another macOS Space — so the
# user stares at an empty desktop while the lesson is driven invisibly.
#
# Usage:
#   foreground_browser.sh [APP_NAME] [URL_SUBSTRING]
#
#   APP_NAME        Browser app name. Default: "Google Chrome".
#                   Supports: "Google Chrome", "Microsoft Edge", "Brave Browser",
#                   "Arc", "Safari", "Google Chrome Canary", "Chromium".
#   URL_SUBSTRING   Optional. If given, the matching tab is made active in its
#                   window before that window is raised (Chromium/Safari only).
#
# Exit code 0 = app is frontmost. Prints a one-line STATUS for the caller to
# verify; ALWAYS follow this with a screenshot to confirm the chart is visible.

set -uo pipefail

APP_NAME="${1:-Google Chrome}"
URL_SUBSTRING="${2:-}"

is_chromium() {
  case "$1" in
    "Google Chrome"|"Microsoft Edge"|"Brave Browser"|"Arc"|"Google Chrome Canary"|"Chromium") return 0 ;;
    *) return 1 ;;
  esac
}

# 1) Activate the app. This also pulls the user across to the Space that holds
#    the app's active window, and launches it if it is not running.
osascript -e "tell application \"$APP_NAME\" to activate" >/dev/null 2>&1

# 2) Optionally select the tab whose URL contains URL_SUBSTRING, then raise that
#    window to the front of the app's window stack.
if [ -n "$URL_SUBSTRING" ]; then
  if is_chromium "$APP_NAME"; then
    osascript >/dev/null 2>&1 <<OSA
tell application "$APP_NAME"
  set winList to every window
  repeat with w in winList
    set tabIdx to 0
    repeat with t in (every tab of w)
      set tabIdx to tabIdx + 1
      if (URL of t) contains "$URL_SUBSTRING" then
        set active tab index of w to tabIdx
        set index of w to 1
        return
      end if
    end repeat
  end repeat
end tell
OSA
  elif [ "$APP_NAME" = "Safari" ]; then
    osascript >/dev/null 2>&1 <<OSA
tell application "Safari"
  repeat with w in (every window)
    repeat with t in (every tab of w)
      if (URL of t) contains "$URL_SUBSTRING" then
        set current tab of w to t
        set index of w to 1
        return
      end if
    end repeat
  end repeat
end tell
OSA
  fi
else
  # No URL filter: just raise window 1 to the front.
  osascript -e "tell application \"$APP_NAME\" to set index of window 1 to 1" >/dev/null 2>&1
fi

# 3) Un-minimize EVERY window of the app and force the process frontmost via
#    System Events (handles the minimized-into-Dock and behind-other-apps cases
#    that `activate` alone does not always fix).
osascript >/dev/null 2>&1 <<OSA
tell application "System Events"
  tell process "$APP_NAME"
    set frontmost to true
    try
      repeat with w in (every window)
        if value of attribute "AXMinimized" of w is true then
          set value of attribute "AXMinimized" of w to false
        end if
      end repeat
    end try
  end tell
end tell
OSA

# 4) Re-activate after un-minimizing so the restored window takes focus.
osascript -e "tell application \"$APP_NAME\" to activate" >/dev/null 2>&1

# 5) Verify and report.
FRONT_APP=$(osascript -e 'tell application "System Events" to get name of first process whose frontmost is true' 2>/dev/null)
if [ "$FRONT_APP" = "$APP_NAME" ]; then
  echo "STATUS: OK — $APP_NAME is frontmost. Confirm with a screenshot before teaching."
  exit 0
else
  echo "STATUS: WARN — frontmost app is '$FRONT_APP', expected '$APP_NAME'. Retry or check Screen Recording / Accessibility permissions, then screenshot."
  exit 1
fi
