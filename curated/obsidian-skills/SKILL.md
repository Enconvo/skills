---
name: obsidian-skills
description: "Obsidian vault toolkit: interact with vaults via Obsidian CLI (read, create, search, daily notes, properties, tasks, plugins); create/edit Markdown notes with wikilinks, callouts, embeds, and properties; build Bases (.base) views with filters and formulas; create JSON Canvas (.canvas) mind maps and flowcharts; extract clean markdown from web pages with Defuddle. Activates on: obsidian, vault, wikilink, callout, .base file, .canvas file, obsidian cli, obsidian note, obsidian markdown, daily note, defuddle, or any Obsidian-related request."
---

# Obsidian Skills

Comprehensive skill for working with Obsidian vaults — CLI interaction, Markdown, Bases, Canvas, and web content extraction.

## Prerequisites — Obsidian CLI

Before running any `obsidian` CLI command:

### 1. Ensure Obsidian is running

The CLI **requires** the Obsidian app to be open. Check and launch if needed:

```bash
pgrep -x Obsidian > /dev/null || open -a Obsidian
```

If Obsidian was just launched, wait a few seconds for it to initialize before running CLI commands.

### 2. Verify the CLI is available

```bash
obsidian version
```

If the command returns:
> `Command line interface is not enabled. Please turn it on in Settings > General > Advanced.`

Tell the user: **Please open Obsidian, go to Settings → General → Advanced, and enable "Command line interface". Then try again.**

Do NOT attempt to enable it programmatically — this must be done manually by the user in the Obsidian app.

If the command is not found, guide the user through setup:

1. **Requires Obsidian installer 1.12+** — update Obsidian to the latest version.
2. **Enable CLI in Obsidian**: Go to **Settings → General → Command line interface** and follow the prompt to register.
3. **Restart the terminal** after registration for PATH changes to take effect.

**macOS**: Ensure `~/.zprofile` contains:
```bash
export PATH="$PATH:/Applications/Obsidian.app/Contents/MacOS"
```

**Linux**: Check the symlink exists: `ls -l /usr/local/bin/obsidian`

If the user has not installed or enabled the CLI, inform them of these steps and wait for confirmation before proceeding with CLI commands.

---

## Other References

| Need | Reference |
|------|-----------|
| Create/edit `.md` notes with wikilinks, callouts, embeds, properties, tags | [Obsidian Markdown](references/obsidian-markdown.md) |
| Build `.base` files with views, filters, formulas, summaries | [Obsidian Bases](references/obsidian-bases.md) |
| Create `.canvas` files with nodes, edges, mind maps, flowcharts | [JSON Canvas](references/json-canvas.md) |
| Extract clean markdown from web pages (remove ads/clutter) | [Defuddle](references/defuddle.md) |

---

## Obsidian CLI Reference

Use the `obsidian` CLI to interact with a running Obsidian instance from the terminal for scripting, automation, and integration with external tools. Anything you can do in Obsidian you can do from the command line.

### Syntax

**Parameters** take a value with `=`. Quote values with spaces:

```bash
obsidian create name="My Note" content="Hello world"
```

**Flags** are boolean switches with no value:

```bash
obsidian create name="My Note" open overwrite
```

For multiline content use `\n` for newline and `\t` for tab:

```bash
obsidian create name="Note" content="# Title\n\nBody text"
```

### File Targeting

Many commands accept `file` or `path` to target a specific file. Without either, the active file is used.

- `file=<name>` — resolves like a wikilink (name only, no path or extension needed)
- `path=<path>` — exact path from vault root, e.g. `folder/note.md`

```bash
# These are equivalent if "Recipe.md" is the only file with that name
obsidian read file=Recipe
obsidian read path="Templates/Recipe.md"
```

### Vault Targeting

If your terminal's current working directory is a vault folder, that vault is used by default. Otherwise, the most recently focused vault is used.

Use `vault=<name>` or `vault=<id>` as the first parameter to target a specific vault:

```bash
obsidian vault=Notes daily
obsidian vault="My Vault" search query="test"
```

### Copy Output

Add `--copy` to any command to copy the output to the clipboard:

```bash
obsidian read --copy
obsidian search query="TODO" --copy
```

---

### Common Examples

#### Everyday Use

```bash
# Open today's daily note
obsidian daily

# Add a task to your daily note
obsidian daily:append content="- [ ] Buy groceries"

# Search your vault
obsidian search query="meeting notes"

# Read the active file
obsidian read

# List all tasks from your daily note
obsidian tasks daily

# Create a new note from a template
obsidian create name="Trip to Paris" template=Travel

# List all tags in your vault with counts
obsidian tags counts

# Compare two versions of a file
obsidian diff file=README from=1 to=3
```

#### For Developers

```bash
# Open developer tools
obsidian devtools

# Reload a community plugin you're developing
obsidian plugin:reload id=my-plugin

# Take a screenshot of the app
obsidian dev:screenshot path=screenshot.png

# Run JavaScript in the app console
obsidian eval code="app.vault.getFiles().length"
```

---

### General Commands

#### help

Show list of all available commands.

| Parameter | Description |
|-----------|-------------|
| `<command>` | Show help for a specific command |

#### version

Show Obsidian version.

#### reload

Reload the app window.

#### restart

Restart the app.

---

### Files and Folders

#### file

Show file info (default: active file).

| Parameter | Description |
|-----------|-------------|
| `file=<name>` | file name |
| `path=<path>` | file path |

#### files

List files in the vault.

| Parameter | Description |
|-----------|-------------|
| `folder=<path>` | filter by folder |
| `ext=<extension>` | filter by extension |
| `total` | return file count (flag) |

#### folder

Show folder info.

| Parameter | Description |
|-----------|-------------|
| `path=<path>` | **(required)** folder path |
| `info=files\|folders\|size` | return specific info only |

#### folders

List folders in the vault.

| Parameter | Description |
|-----------|-------------|
| `folder=<path>` | filter by parent folder |
| `total` | return folder count (flag) |

#### open

Open a file.

| Parameter | Description |
|-----------|-------------|
| `file=<name>` | file name |
| `path=<path>` | file path |
| `newtab` | open in new tab (flag) |

#### create

Create or overwrite a file.

| Parameter | Description |
|-----------|-------------|
| `name=<name>` | file name |
| `path=<path>` | file path |
| `content=<text>` | initial content |
| `template=<name>` | template to use |
| `overwrite` | overwrite if file exists (flag) |
| `open` | open file after creating (flag) |
| `newtab` | open in new tab (flag) |

#### read

Read file contents (default: active file).

| Parameter | Description |
|-----------|-------------|
| `file=<name>` | file name |
| `path=<path>` | file path |

#### append

Append content to a file (default: active file).

| Parameter | Description |
|-----------|-------------|
| `file=<name>` | file name |
| `path=<path>` | file path |
| `content=<text>` | **(required)** content to append |
| `inline` | append without newline (flag) |

#### prepend

Prepend content after frontmatter (default: active file).

| Parameter | Description |
|-----------|-------------|
| `file=<name>` | file name |
| `path=<path>` | file path |
| `content=<text>` | **(required)** content to prepend |
| `inline` | prepend without newline (flag) |

#### move

Move or rename a file (default: active file). Automatically updates internal links if enabled in vault settings.

| Parameter | Description |
|-----------|-------------|
| `file=<name>` | file name |
| `path=<path>` | file path |
| `to=<path>` | **(required)** destination folder or path |

#### rename

Rename a file (default: active file). File extension is preserved if omitted. Use `move` to rename and move simultaneously.

| Parameter | Description |
|-----------|-------------|
| `file=<name>` | file name |
| `path=<path>` | file path |
| `name=<name>` | **(required)** new file name |

#### delete

Delete a file (default: active file, trash by default).

| Parameter | Description |
|-----------|-------------|
| `file=<name>` | file name |
| `path=<path>` | file path |
| `permanent` | skip trash, delete permanently (flag) |

---

### Daily Notes

#### daily

Open daily note.

| Parameter | Description |
|-----------|-------------|
| `paneType=tab\|split\|window` | pane type to open in |

#### daily:path

Get daily note path. Returns the expected path even if the file hasn't been created yet.

#### daily:read

Read daily note contents.

#### daily:append

Append content to daily note.

| Parameter | Description |
|-----------|-------------|
| `content=<text>` | **(required)** content to append |
| `paneType=tab\|split\|window` | pane type to open in |
| `inline` | append without newline (flag) |
| `open` | open file after adding (flag) |

#### daily:prepend

Prepend content to daily note.

| Parameter | Description |
|-----------|-------------|
| `content=<text>` | **(required)** content to prepend |
| `paneType=tab\|split\|window` | pane type to open in |
| `inline` | prepend without newline (flag) |
| `open` | open file after adding (flag) |

---

### Search

#### search

Search vault for text. Returns matching file paths.

| Parameter | Description |
|-----------|-------------|
| `query=<text>` | **(required)** search query |
| `path=<folder>` | limit to folder |
| `limit=<n>` | max files |
| `format=text\|json` | output format (default: text) |
| `total` | return match count (flag) |
| `case` | case sensitive (flag) |

#### search:context

Search with matching line context. Returns grep-style `path:line: text` output.

| Parameter | Description |
|-----------|-------------|
| `query=<text>` | **(required)** search query |
| `path=<folder>` | limit to folder |
| `limit=<n>` | max files |
| `format=text\|json` | output format (default: text) |
| `case` | case sensitive (flag) |

#### search:open

Open search view.

| Parameter | Description |
|-----------|-------------|
| `query=<text>` | initial search query |

---

### Properties

#### properties

List properties in the vault. Use `active` or `file`/`path` to show properties for a specific file.

| Parameter | Description |
|-----------|-------------|
| `file=<name>` | show properties for file |
| `path=<path>` | show properties for path |
| `name=<name>` | get specific property count |
| `sort=count` | sort by count (default: name) |
| `format=yaml\|json\|tsv` | output format (default: yaml) |
| `total` | return property count (flag) |
| `counts` | include occurrence counts (flag) |
| `active` | show properties for active file (flag) |

#### property:set

Set a property on a file (default: active file).

| Parameter | Description |
|-----------|-------------|
| `name=<name>` | **(required)** property name |
| `value=<value>` | **(required)** property value |
| `type=text\|list\|number\|checkbox\|date\|datetime` | property type |
| `file=<name>` | file name |
| `path=<path>` | file path |

#### property:remove

Remove a property from a file (default: active file).

| Parameter | Description |
|-----------|-------------|
| `name=<name>` | **(required)** property name |
| `file=<name>` | file name |
| `path=<path>` | file path |

#### property:read

Read a property value from a file (default: active file).

| Parameter | Description |
|-----------|-------------|
| `name=<name>` | **(required)** property name |
| `file=<name>` | file name |
| `path=<path>` | file path |

---

### Tags

#### tags

List tags in the vault. Use `active` or `file`/`path` to show tags for a specific file.

| Parameter | Description |
|-----------|-------------|
| `file=<name>` | file name |
| `path=<path>` | file path |
| `sort=count` | sort by count (default: name) |
| `total` | return tag count (flag) |
| `counts` | include tag counts (flag) |
| `format=json\|tsv\|csv` | output format (default: tsv) |
| `active` | show tags for active file (flag) |

#### tag

Get tag info.

| Parameter | Description |
|-----------|-------------|
| `name=<tag>` | **(required)** tag name |
| `total` | return occurrence count (flag) |
| `verbose` | include file list and count (flag) |

---

### Tasks

#### tasks

List tasks in the vault. Use `active` or `file`/`path` to show tasks for a specific file.

| Parameter | Description |
|-----------|-------------|
| `file=<name>` | filter by file name |
| `path=<path>` | filter by file path |
| `status="<char>"` | filter by status character |
| `total` | return task count (flag) |
| `done` | show completed tasks (flag) |
| `todo` | show incomplete tasks (flag) |
| `verbose` | group by file with line numbers (flag) |
| `format=json\|tsv\|csv` | output format (default: text) |
| `active` | show tasks for active file (flag) |
| `daily` | show tasks from daily note (flag) |

Examples:

```bash
tasks                        # List all tasks
tasks todo                   # Incomplete tasks only
tasks file=Recipe done       # Completed tasks in Recipe
tasks daily                  # Tasks from daily note
tasks daily total            # Count tasks in daily note
tasks verbose                # Tasks with file paths and line numbers
tasks 'status=?'             # Filter by custom status
```

#### task

Show or update a task.

| Parameter | Description |
|-----------|-------------|
| `ref=<path:line>` | task reference (path:line) |
| `file=<name>` | file name |
| `path=<path>` | file path |
| `line=<n>` | line number |
| `status="<char>"` | set status character |
| `toggle` | toggle task status (flag) |
| `daily` | daily note (flag) |
| `done` | mark as done (flag) |
| `todo` | mark as todo (flag) |

Examples:

```bash
task file=Recipe line=8             # Show task info
task ref="Recipe.md:8"              # Show task by reference
task ref="Recipe.md:8" toggle       # Toggle completion
task daily line=3 toggle            # Toggle daily note task
task file=Recipe line=8 done        # Mark done → [x]
task file=Recipe line=8 status=-    # Set status → [-]
```

---

### Links

#### backlinks

List backlinks to a file (default: active file).

| Parameter | Description |
|-----------|-------------|
| `file=<name>` | target file name |
| `path=<path>` | target file path |
| `counts` | include link counts (flag) |
| `total` | return backlink count (flag) |
| `format=json\|tsv\|csv` | output format (default: tsv) |

#### links

List outgoing links from a file (default: active file).

| Parameter | Description |
|-----------|-------------|
| `file=<name>` | file name |
| `path=<path>` | file path |
| `total` | return link count (flag) |

#### unresolved

List unresolved links in vault.

| Parameter | Description |
|-----------|-------------|
| `total` | return unresolved link count (flag) |
| `counts` | include link counts (flag) |
| `verbose` | include source files (flag) |
| `format=json\|tsv\|csv` | output format (default: tsv) |

#### orphans

List files with no incoming links.

| Parameter | Description |
|-----------|-------------|
| `total` | return orphan count (flag) |

#### deadends

List files with no outgoing links.

| Parameter | Description |
|-----------|-------------|
| `total` | return dead-end count (flag) |

---

### Outline

#### outline

Show headings for the current file.

| Parameter | Description |
|-----------|-------------|
| `file=<name>` | file name |
| `path=<path>` | file path |
| `format=tree\|md\|json` | output format (default: tree) |
| `total` | return heading count (flag) |

---

### Bookmarks

#### bookmarks

List bookmarks.

| Parameter | Description |
|-----------|-------------|
| `total` | return bookmark count (flag) |
| `verbose` | include bookmark types (flag) |
| `format=json\|tsv\|csv` | output format (default: tsv) |

#### bookmark

Add a bookmark.

| Parameter | Description |
|-----------|-------------|
| `file=<path>` | file to bookmark |
| `subpath=<subpath>` | subpath (heading or block) within file |
| `folder=<path>` | folder to bookmark |
| `search=<query>` | search query to bookmark |
| `url=<url>` | URL to bookmark |
| `title=<title>` | bookmark title |

---

### Command Palette

#### commands

List available command IDs.

| Parameter | Description |
|-----------|-------------|
| `filter=<prefix>` | filter by ID prefix |

#### command

Execute an Obsidian command.

| Parameter | Description |
|-----------|-------------|
| `id=<command-id>` | **(required)** command ID to execute |

#### hotkeys

List hotkeys for all commands.

| Parameter | Description |
|-----------|-------------|
| `total` | return hotkey count (flag) |
| `verbose` | show if hotkey is custom (flag) |
| `format=json\|tsv\|csv` | output format (default: tsv) |

#### hotkey

Get hotkey for a command.

| Parameter | Description |
|-----------|-------------|
| `id=<command-id>` | **(required)** command ID |
| `verbose` | show if custom or default (flag) |

---

### Plugins

#### plugins

List installed plugins.

| Parameter | Description |
|-----------|-------------|
| `filter=core\|community` | filter by plugin type |
| `versions` | include version numbers (flag) |
| `format=json\|tsv\|csv` | output format (default: tsv) |

#### plugins:enabled

List enabled plugins.

| Parameter | Description |
|-----------|-------------|
| `filter=core\|community` | filter by plugin type |
| `versions` | include version numbers (flag) |
| `format=json\|tsv\|csv` | output format (default: tsv) |

#### plugin

Get plugin info.

| Parameter | Description |
|-----------|-------------|
| `id=<plugin-id>` | **(required)** plugin ID |

#### plugin:enable / plugin:disable

Enable or disable a plugin.

| Parameter | Description |
|-----------|-------------|
| `id=<id>` | **(required)** plugin ID |
| `filter=core\|community` | plugin type |

#### plugin:install

Install a community plugin.

| Parameter | Description |
|-----------|-------------|
| `id=<id>` | **(required)** plugin ID |
| `enable` | enable after install (flag) |

#### plugin:uninstall

Uninstall a community plugin.

| Parameter | Description |
|-----------|-------------|
| `id=<id>` | **(required)** plugin ID |

#### plugin:reload

Reload a plugin (for developers).

| Parameter | Description |
|-----------|-------------|
| `id=<id>` | **(required)** plugin ID |

#### plugins:restrict

Toggle or check restricted mode.

| Parameter | Description |
|-----------|-------------|
| `on` | enable restricted mode (flag) |
| `off` | disable restricted mode (flag) |

---

### Bases

#### bases

List all `.base` files in the vault.

#### base:views

List views in the current base file.

#### base:create

Create a new item in a base. Defaults to the active base view if no file is specified.

| Parameter | Description |
|-----------|-------------|
| `file=<name>` | base file name |
| `path=<path>` | base file path |
| `view=<name>` | view name |
| `name=<name>` | new file name |
| `content=<text>` | initial content |
| `open` | open file after creating (flag) |
| `newtab` | open in new tab (flag) |

#### base:query

Query a base and return results.

| Parameter | Description |
|-----------|-------------|
| `file=<name>` | base file name |
| `path=<path>` | base file path |
| `view=<name>` | view name to query |
| `format=json\|csv\|tsv\|md\|paths` | output format (default: json) |

---

### File History

#### diff

List or compare versions from local File recovery and Sync. Versions are numbered from newest to oldest.

| Parameter | Description |
|-----------|-------------|
| `file=<name>` | file name |
| `path=<path>` | file path |
| `from=<n>` | version number to diff from |
| `to=<n>` | version number to diff to |
| `filter=local\|sync` | filter by version source |

```bash
diff                              # List all versions of active file
diff file=Recipe                  # List versions of a specific file
diff file=Recipe from=1           # Compare latest version to current
diff file=Recipe from=2 to=1      # Compare two versions
diff filter=sync                  # Only show Sync versions
```

#### history

List versions from File recovery only.

| Parameter | Description |
|-----------|-------------|
| `file=<name>` | file name |
| `path=<path>` | file path |

#### history:list

List all files with local history.

#### history:read

Read a local history version.

| Parameter | Description |
|-----------|-------------|
| `file=<name>` | file name |
| `path=<path>` | file path |
| `version=<n>` | version number (default: 1) |

#### history:restore

Restore a local history version.

| Parameter | Description |
|-----------|-------------|
| `file=<name>` | file name |
| `path=<path>` | file path |
| `version=<n>` | **(required)** version number |

#### history:open

Open file recovery.

| Parameter | Description |
|-----------|-------------|
| `file=<name>` | file name |
| `path=<path>` | file path |

---

### Sync

#### sync

Pause or resume sync.

| Parameter | Description |
|-----------|-------------|
| `on` | resume sync (flag) |
| `off` | pause sync (flag) |

#### sync:status

Show sync status and usage.

#### sync:history

List sync version history for a file (default: active file).

| Parameter | Description |
|-----------|-------------|
| `file=<name>` | file name |
| `path=<path>` | file path |
| `total` | return version count (flag) |

#### sync:read

Read a sync version (default: active file).

| Parameter | Description |
|-----------|-------------|
| `file=<name>` | file name |
| `path=<path>` | file path |
| `version=<n>` | **(required)** version number |

#### sync:restore

Restore a sync version (default: active file).

| Parameter | Description |
|-----------|-------------|
| `file=<name>` | file name |
| `path=<path>` | file path |
| `version=<n>` | **(required)** version number |

#### sync:open

Open sync history (default: active file).

| Parameter | Description |
|-----------|-------------|
| `file=<name>` | file name |
| `path=<path>` | file path |

#### sync:deleted

List deleted files in sync.

| Parameter | Description |
|-----------|-------------|
| `total` | return deleted file count (flag) |

---

### Publish

#### publish:site

Show publish site info (slug, URL).

#### publish:list

List published files.

| Parameter | Description |
|-----------|-------------|
| `total` | return published file count (flag) |

#### publish:status

List publish changes.

| Parameter | Description |
|-----------|-------------|
| `total` | return change count (flag) |
| `new` | show new files only (flag) |
| `changed` | show changed files only (flag) |
| `deleted` | show deleted files only (flag) |

#### publish:add

Publish a file or all changed files (default: active file).

| Parameter | Description |
|-----------|-------------|
| `file=<name>` | file name |
| `path=<path>` | file path |
| `changed` | publish all changed files (flag) |

#### publish:remove

Unpublish a file (default: active file).

| Parameter | Description |
|-----------|-------------|
| `file=<name>` | file name |
| `path=<path>` | file path |

#### publish:open

Open file on published site (default: active file).

| Parameter | Description |
|-----------|-------------|
| `file=<name>` | file name |
| `path=<path>` | file path |

---

### Templates

#### templates

List templates.

| Parameter | Description |
|-----------|-------------|
| `total` | return template count (flag) |

#### template:read

Read template content.

| Parameter | Description |
|-----------|-------------|
| `name=<template>` | **(required)** template name |
| `title=<title>` | title for variable resolution |
| `resolve` | resolve template variables (flag) |

#### template:insert

Insert template into active file.

| Parameter | Description |
|-----------|-------------|
| `name=<template>` | **(required)** template name |

Note: `resolve` processes `{{date}}`, `{{time}}`, `{{title}}` variables. Use `create path=<path> template=<name>` to create a file with a template.

---

### Themes and Snippets

#### themes

List installed themes.

| Parameter | Description |
|-----------|-------------|
| `versions` | include version numbers (flag) |

#### theme

Show active theme or get info.

| Parameter | Description |
|-----------|-------------|
| `name=<name>` | theme name for details |

#### theme:set

Set active theme.

| Parameter | Description |
|-----------|-------------|
| `name=<name>` | **(required)** theme name (empty for default) |

#### theme:install / theme:uninstall

Install or uninstall a community theme.

| Parameter | Description |
|-----------|-------------|
| `name=<name>` | **(required)** theme name |
| `enable` | activate after install (flag, install only) |

#### snippets / snippets:enabled

List installed or enabled CSS snippets.

#### snippet:enable / snippet:disable

Enable or disable a CSS snippet.

| Parameter | Description |
|-----------|-------------|
| `name=<name>` | **(required)** snippet name |

---

### Aliases

#### aliases

List aliases in the vault. Use `active` or `file`/`path` to show aliases for a specific file.

| Parameter | Description |
|-----------|-------------|
| `file=<name>` | file name |
| `path=<path>` | file path |
| `total` | return alias count (flag) |
| `verbose` | include file paths (flag) |
| `active` | show aliases for active file (flag) |

---

### Random Notes

#### random

Open a random note.

| Parameter | Description |
|-----------|-------------|
| `folder=<path>` | limit to folder |
| `newtab` | open in new tab (flag) |

#### random:read

Read a random note (includes path).

| Parameter | Description |
|-----------|-------------|
| `folder=<path>` | limit to folder |

---

### Unique Notes

#### unique

Create unique note.

| Parameter | Description |
|-----------|-------------|
| `name=<text>` | note name |
| `content=<text>` | initial content |
| `paneType=tab\|split\|window` | pane type to open in |
| `open` | open file after creating (flag) |

---

### Vault

#### vault

Show vault info.

| Parameter | Description |
|-----------|-------------|
| `info=name\|path\|files\|folders\|size` | return specific info only |

#### vaults

List known vaults.

| Parameter | Description |
|-----------|-------------|
| `total` | return vault count (flag) |
| `verbose` | include vault paths (flag) |

#### vault:open

Switch to a different vault (TUI only).

| Parameter | Description |
|-----------|-------------|
| `name=<name>` | **(required)** vault name |

---

### Word Count

#### wordcount

Count words and characters (default: active file).

| Parameter | Description |
|-----------|-------------|
| `file=<name>` | file name |
| `path=<path>` | file path |
| `words` | return word count only (flag) |
| `characters` | return character count only (flag) |

---

### Workspace

#### workspace

Show workspace tree.

| Parameter | Description |
|-----------|-------------|
| `ids` | include workspace item IDs (flag) |

#### workspaces

List saved workspaces.

| Parameter | Description |
|-----------|-------------|
| `total` | return workspace count (flag) |

#### workspace:save / workspace:load / workspace:delete

Save, load, or delete a workspace.

| Parameter | Description |
|-----------|-------------|
| `name=<name>` | workspace name (**(required)** for load/delete) |

#### tabs

List open tabs.

| Parameter | Description |
|-----------|-------------|
| `ids` | include tab IDs (flag) |

#### tab:open

Open a new tab.

| Parameter | Description |
|-----------|-------------|
| `group=<id>` | tab group ID |
| `file=<path>` | file to open |
| `view=<type>` | view type to open |

#### recents

List recently opened files.

| Parameter | Description |
|-----------|-------------|
| `total` | return recent file count (flag) |

---

### Web Viewer

#### web

Open URL in web viewer.

| Parameter | Description |
|-----------|-------------|
| `url=<url>` | **(required)** URL to open |
| `newtab` | open in new tab (flag) |

---

### Developer Commands

Commands to help develop Community plugins and Themes.

#### devtools

Toggle Electron dev tools.

#### dev:debug

Attach/detach Chrome DevTools Protocol debugger.

| Parameter | Description |
|-----------|-------------|
| `on` | attach debugger (flag) |
| `off` | detach debugger (flag) |

#### dev:cdp

Run a Chrome DevTools Protocol command.

| Parameter | Description |
|-----------|-------------|
| `method=<CDP.method>` | **(required)** CDP method to call |
| `params=<json>` | method parameters as JSON |

#### dev:errors

Show captured JavaScript errors.

| Parameter | Description |
|-----------|-------------|
| `clear` | clear the error buffer (flag) |

#### dev:screenshot

Take a screenshot (returns base64 PNG).

| Parameter | Description |
|-----------|-------------|
| `path=<filename>` | output file path |

#### dev:console

Show captured console messages.

| Parameter | Description |
|-----------|-------------|
| `limit=<n>` | max messages to show (default 50) |
| `level=log\|warn\|error\|info\|debug` | filter by log level |
| `clear` | clear the console buffer (flag) |

#### dev:css

Inspect CSS with source locations.

| Parameter | Description |
|-----------|-------------|
| `selector=<css>` | **(required)** CSS selector |
| `prop=<name>` | filter by property name |

#### dev:dom

Query DOM elements.

| Parameter | Description |
|-----------|-------------|
| `selector=<css>` | **(required)** CSS selector |
| `attr=<name>` | get attribute value |
| `css=<prop>` | get CSS property value |
| `total` | return element count (flag) |
| `text` | return text content (flag) |
| `inner` | return innerHTML instead of outerHTML (flag) |
| `all` | return all matches instead of first (flag) |

#### dev:mobile

Toggle mobile emulation.

| Parameter | Description |
|-----------|-------------|
| `on` | enable mobile emulation (flag) |
| `off` | disable mobile emulation (flag) |

#### eval

Execute JavaScript and return result.

| Parameter | Description |
|-----------|-------------|
| `code=<javascript>` | **(required)** JavaScript code to execute |

---

## Obsidian Markdown Essentials

### Wikilinks & Embeds

```markdown
[[Note Name]]                    Wikilink
[[Note Name|Display Text]]      Wikilink with alias
[[Note Name#Heading]]            Link to heading
[[Note Name#^block-id]]          Link to block
![[Note Name]]                   Embed note
![[image.png|300]]               Embed image with width
```

### Frontmatter

```yaml
---
title: My Note
tags: [project, active]
aliases: [Alt Name]
cssclasses: [custom-class]
---
```

### Callouts

```markdown
> [!note] Title
> Content here.

> [!tip]- Foldable callout
> Hidden until expanded.
```

Types: `note`, `abstract`, `info`, `todo`, `tip`, `success`, `question`, `warning`, `failure`, `danger`, `bug`, `example`, `quote`

### Tasks

```markdown
- [ ] Incomplete task
- [x] Completed task
```

---

## Bases Quick Start

```yaml
# my-view.base
filters:
  and:
    - file.hasTag("project")
formulas:
  days_old: '(now() - file.ctime).days'
views:
  - type: table
    name: "Projects"
    order: [file.name, status, formula.days_old]
```

View types: `table`, `cards`, `list`, `map`

---

## Canvas Quick Start

```json
{
  "nodes": [
    {"id": "abc123def4567890", "type": "text", "x": 0, "y": 0, "width": 300, "height": 150, "text": "# Node"}
  ],
  "edges": []
}
```

Node types: `text`, `file`, `link`, `group`. IDs are 16-char hex strings.

---

## Defuddle Quick Start

```bash
defuddle parse <url> --md
defuddle parse <url> --md -o content.md
```

If not installed: `npm install -g defuddle-cli`
