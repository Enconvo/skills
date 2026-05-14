# Obsidian Textbook Template

How to structure the deep-dive notes that back your live teaching. The chat is light; the vault is heavy. The student switches between them.

## Folder Structure

```
<Vault>/<Parent Category>/<Topic Name>/
├── 00 - <Topic> Tutor MOC.md
├── 01 - <Step 1 Name>.md
├── 02 - <Step 2 Name>.md
├── ...
└── NN - <Step N Name>.md
```

Parent category examples: `Investing/`, `Programming/`, `Health/`, `Languages/`. Match what's already in the vault.

Topic name: short, descriptive, title-case. e.g. `Options 101`, `Python Decorators`, `Regex Basics`.

## MOC (Map of Content) Template

`00 - <Topic> Tutor MOC.md`

```markdown
---
tags: [<topic>, tutorial, moc]
created: YYYY-MM-DD
tutor: <agent name>
classroom: <surface used, e.g. "IBKR Portal (ibkr.com)">
---

# <Topic> — Map of Content

One-sentence framing of what this curriculum covers and why.

## Reading Order

1. [[01 - Step Name]]
2. [[02 - Step Name]]
3. [[03 - Step Name]]
...

## Live Classroom Snapshot

- **Example used:** <e.g. AAPL stock at $185>
- **Surface:** <URL or app name>
- **Screenshot:** <optional path>

## Big-Picture Mental Model

> One memorable line — the single sentence that, if the student forgets everything else, still captures the topic.
```

## Step Note Template

`NN - <Step Name>.md`

```markdown
---
tags: [<topic>, <subtopic>]
---

# NN — <Step Name>

## Definition

Plain-English definition. 2–3 lines max.

## Why It Matters

What this concept lets the student *do* or *avoid*. One short paragraph.

## Worked Example

A concrete example using the same numbers / context from the live classroom. This is where formulas, tables, and the math live — *not in chat*.

## Memory Hook / Mental Model

One memorable line or analogy.

## Common Trap

The most common newbie mistake about this concept and how to spot it.

[[00 - <Topic> Tutor MOC|↩ Back to Map]]
```

## Style Rules for Notes

These notes are **reference material the student reads at their own pace**, so they CAN be longer and denser than chat. But:

- Use **tables for data**, **code blocks for code**, **callouts for warnings**.
- Keep each note focused on ONE step's concept. Don't merge.
- Cross-link liberally with `[[wikilinks]]` — concepts in options/programming/etc. are interconnected.
- Include the worked example from the live classroom whenever possible — the student remembers the IBKR-stock-at-$85 example better than abstract X and Y.
- End every note with the back-to-MOC link.

## What Goes In a Note vs. What Goes In Chat

| Content | Chat | Note |
|---|---|---|
| Plain English intuition | ✅ | ✅ |
| One-sentence mental model | ✅ | ✅ |
| Pointer to the screen | ✅ | — |
| One eye-exercise question | ✅ | — |
| Definition (2–3 lines) | ✅ | ✅ |
| Tables of values | ❌ | ✅ |
| Formulas with √ and Σ | ❌ | ✅ |
| Worked example with multiple steps | ❌ | ✅ |
| Cheat-sheet of edge cases | ❌ | ✅ |
| Common-trap warning | brief | full |

## File Naming

- Always two-digit prefix for ordering: `01`, `02`, ..., `10`, `11`.
- Title-case the step name. Use hyphens or spaces consistently with the vault.
- Avoid special characters that need URL encoding except `-` and spaces.

## When the Curriculum Changes

If the user reroutes the lesson (skips ahead, asks a side question that becomes a new step), it's fine to:
- Insert a new note (e.g. `04b - Side Topic.md`)
- Or renumber if the curriculum gets a real restructure (rare; only worth it for major rewrites)

The MOC's reading order is the source of truth — update it when you change the structure.

## Tag Conventions

Always include:
- The topic tag: `options`, `python`, `regex`, etc.
- A type tag: `tutorial`, `definition`, `worked-example`
- Optional subtopic tags

This lets the student later search/filter the vault by `tag:options tag:tutorial` to retrieve the whole curriculum.
