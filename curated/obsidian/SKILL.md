---
name: obsidian
description: "Obsidian vault toolkit: create/edit Markdown notes with wikilinks, callouts, embeds, and properties; build Bases (.base) views with filters and formulas; create JSON Canvas (.canvas) mind maps and flowcharts; interact with vaults via the Obsidian CLI; extract clean markdown from web pages with Defuddle. Activates on: obsidian, vault, wikilink, callout, .base file, .canvas file, obsidian cli, obsidian note, obsidian markdown, daily note, defuddle, or any Obsidian-related request."
---

# Obsidian Skills

Comprehensive skill for working with Obsidian vaults — Markdown, Bases, Canvas, CLI, and web content extraction.

## Decision Matrix

| Need | Reference |
|------|-----------|
| Create/edit `.md` notes with wikilinks, callouts, embeds, properties, tags | [Obsidian Markdown](references/obsidian-markdown.md) |
| Build `.base` files with views, filters, formulas, summaries | [Obsidian Bases](references/obsidian-bases.md) |
| Create `.canvas` files with nodes, edges, mind maps, flowcharts | [JSON Canvas](references/json-canvas.md) |
| Read, create, search notes via CLI; plugin development; debugging | [Obsidian CLI](references/obsidian-cli.md) |
| Extract clean markdown from web pages (remove ads/clutter) | [Defuddle](references/defuddle.md) |

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

## CLI Quick Start

```bash
obsidian read file="My Note"
obsidian create name="New Note" content="# Hello"
obsidian search query="search term"
obsidian daily:append content="- [ ] New task"
obsidian property:set name="status" value="done" file="My Note"
obsidian plugin:reload id=my-plugin
```

Run `obsidian help` for all commands. Use `silent` to prevent files from opening.

---

## Defuddle Quick Start

```bash
defuddle parse <url> --md
defuddle parse <url> --md -o content.md
```

If not installed: `npm install -g defuddle-cli`
