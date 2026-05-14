# Automation Patterns for the Live Classroom

How to actually drive the learning surface — browser, native apps, Obsidian. Don't make the student click around for you.

## Browser (Web Pages) — Primary Path

Use the Enconvo Companion extension via `browser-use/*` endpoints. The user keeps their existing logged-in sessions intact.

### First check: is the right browser connected?

```
local_api → browser-use/browsers → {}
```

If Chrome isn't in the list:
1. Tell the user in **one short message** to install Companion: `https://chromewebstore.google.com/detail/enconvo-companion/afaklbihknigbnjdkegbnenkheogejkd`
2. After install, ask them to **click the Companion toolbar icon on a real webpage** (not `chrome://` pages — extensions can't run there).
3. Recheck `browser-use/browsers` until Chrome shows up.

### Standard interaction loop

```
1. snapshot       → get accessibility tree with @e1, @e2... refs
2. click/fill/scroll using a @eN ref
3. wait_for       → wait for the change
4. snapshot AGAIN → confirm new state, get fresh refs
```

**Refs invalidate after every DOM change.** Re-snapshot after every action that navigates, opens a dialog, or fires AJAX.

### Useful one-liners

| Goal | Call |
|---|---|
| Verify which page is open | `browser-use/get_url { browser: "google_chrome" }` |
| Find the right tab | `browser-use/tab { action: "list" }` then `tab { action: "switch", index: N }` |
| Take a screenshot for reading | `browser-use/screenshot { browser: "google_chrome" }` → returns `filePath`, then use `file_system/read_file` to read it |
| Highlight what you're teaching about | `browser-use/highlight { selector: "@eN", color: "red", duration: 3000 }` |
| Quick custom JS extract | `browser-use/eval { script: "document.title" }` |

### Fallback: AppleScript when extension isn't available

```bash
osascript <<EOF
tell application "Google Chrome"
  activate
  repeat with w in windows
    set tIndex to 1
    repeat with t in tabs of w
      if (URL of t) contains "ibkr.com" then
        set active tab index of w to tIndex
        return
      end if
      set tIndex to tIndex + 1
    end repeat
  end repeat
end tell
EOF
```

This focuses the right tab. Combine with `screencapture -x output.png` and `Read` on the PNG to see what's on screen.

## Native macOS Apps

Use `computer-use/*` (Accessibility API). Works with Finder, System Settings, Notes, Xcode, Numbers, anything that exposes AX.

Pattern is identical to browser-use: snapshot → act on ref → re-snapshot.

For Electron apps that expose CDP (VS Code, Slack, Discord, Figma): see the `browser-use` skill's Electron section — launch with `--remote-debugging-port=9222` and connect via `agent-browser connect 9222`.

## Obsidian

Treat Obsidian as the **textbook**, not a live target you drive. You write the notes; the student reads them.

### Find the vault

```bash
cat ~/Library/Application\ Support/obsidian/obsidian.json
```

Known default: `/Users/zanearcher/Documents/Obsidian Vault`

### Create notes

Use the file system tools (`file_system/write_file`, `file_system/edit_file`). Don't use Obsidian's API — just write Markdown files to disk and Obsidian will pick them up.

### Open a specific note for the student

```bash
open "obsidian://open?vault=Obsidian%20Vault&file=Investing%2FOptions%20101%2F05%20-%20The%20Greeks"
```

URL-encode the file path. `%2F` for `/`, `%20` for spaces.

### Wikilink conventions

- Internal link: `[[Note Name]]`
- Display alias: `[[Note Name|click here]]`
- Section link: `[[Note Name#Heading]]`
- Back-to-index: `[[00 - Topic MOC|↩ Back to Map]]`

## Screenshots — When and How

Take a screenshot when:
- You just acted on the page and need to verify the change.
- The student asks "what should I be looking at?"
- You haven't seen the page recently and your reference might be stale.

**Don't** screenshot before every reply — wasteful and slow.

### Quick screenshot recipe

```bash
screencapture -x /path/to/output.png
```
Then `file_system/read_file` the PNG to see it.

Or for browser-only: `browser-use/screenshot { browser: "google_chrome" }` returns a path you can immediately read.

## Verifying State Before Teaching

Before referencing something on screen, **verify it's actually there**:
1. Snapshot the surface.
2. Confirm the element you're about to point at exists and is visible.
3. If the user said "I'm on page X" but the snapshot shows page Y — say so, then drive them (or yourself) to the right place.

Teaching against an imaginary screen state = the student loses trust instantly.

## When to Stop Driving

If the student says "let me look first" or "wait, I want to explore" — **stop interacting with the page**. They're learning by clicking. That's good. Let them. Resume when they ask.
