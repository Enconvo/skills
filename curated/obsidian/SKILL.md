---
name: obsidian
description: Work with Obsidian vaults — create and edit Obsidian Flavored Markdown (.md) with wikilinks, embeds, callouts, and properties; build Bases (.base) with views, filters, and formulas; create JSON Canvas (.canvas) files with nodes and edges; interact with vaults via the Obsidian CLI; and extract clean markdown from web pages using Defuddle. Use when working with Obsidian notes, .base files, .canvas files, vault operations, or web content extraction.
---

# Obsidian Skills

A comprehensive skill for working with Obsidian vaults. This skill covers Obsidian Flavored Markdown, Bases, JSON Canvas, the Obsidian CLI, and Defuddle for web content extraction.

## When to use

Activate this skill when:
- Creating or editing `.md` files with Obsidian-specific syntax (wikilinks, callouts, embeds, properties, tags)
- Working with `.base` files (database views, filters, formulas, summaries)
- Creating or editing `.canvas` files (visual canvases, mind maps, flowcharts)
- Interacting with an Obsidian vault via the CLI (reading, creating, searching notes, plugin development)
- Extracting clean content from web pages for use in Obsidian

## Reference guides

Each area has a dedicated reference with full syntax and examples:

- [Obsidian Flavored Markdown](references/obsidian-markdown.md) — Wikilinks, embeds, callouts, properties, tags, math, diagrams, and all Obsidian-specific Markdown syntax
- [Obsidian Bases](references/obsidian-bases.md) — `.base` file format, views (table/cards/list/map), filters, formulas, functions, summaries
- [JSON Canvas](references/json-canvas.md) — `.canvas` file format, nodes (text/file/link/group), edges, colors, layout
- [Obsidian CLI](references/obsidian-cli.md) — CLI commands for vault interaction, note management, plugin development, and debugging
- [Defuddle](references/defuddle.md) — Extract clean markdown from web pages, reducing clutter and saving tokens

## Quick reference

### Obsidian Markdown essentials

```markdown
[[Note Name]]                    Wikilink
[[Note Name|Display Text]]      Wikilink with alias
[[Note Name#Heading]]            Link to heading
![[Note Name]]                   Embed note
![[image.png|300]]               Embed image with width

> [!note] Title                  Callout
> Content here.

- [ ] Task item                  Task list
- [x] Completed task

%%hidden comment%%               Comment
```

### Frontmatter

```yaml
---
title: My Note
tags: [project, active]
aliases: [Alt Name]
---
```

### Bases quick start

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

### Canvas quick start

```json
{
  "nodes": [
    {"id": "abc123", "type": "text", "x": 0, "y": 0, "width": 300, "height": 150, "text": "# Node"}
  ],
  "edges": []
}
```

### CLI quick start

```bash
obsidian read file="My Note"
obsidian create name="New Note" content="# Hello"
obsidian search query="search term"
obsidian daily:append content="- [ ] New task"
```

### Defuddle quick start

```bash
defuddle parse <url> --md
```
