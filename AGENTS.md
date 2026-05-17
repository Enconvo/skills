# AGENTS.md
This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## What This Repo Is

This is the **Enconvo skills store** (`github.com/Enconvo/skills`) — a content repository of model-invocable Skills (Anthropic-style `SKILL.md` directories), not an application. There is no build, no test runner, no lint. Each skill is a self-contained folder of Markdown + bundled scripts/assets that ships to end-user agent runtimes.

The parent path `/Users/ysnows/Documents/Enconvo-AI/` is a multi-repo workspace; **this skills repo is independent** and its parent `AGENTS.md` is for the broader Enconvo product, not for skills authoring.

## Repository Layout

```
curated/                  # User-installable skills (the public catalog)
  {skill-name}/
    SKILL.md              # required — YAML frontmatter + Markdown body
    scripts/              # optional — uv/python/shell helpers; invoked via $SKILL_DIR/scripts/...
    references/           # optional — long-form docs the agent loads on demand
    assets/ | data/       # optional — icons, prompt templates, fixtures
    examples/             # optional — reference outputs / sample inputs
    README.md             # optional — human-facing notes (NOT loaded by the agent)
system/                   # Built-in skills shipped with the runtime
  skill-creator/          # Authoritative guide for writing/editing skills — read first
  skill-installer/        # Install pipeline: Enconvo store → Skills.sh → ClawHub → GitHub URL
  enconvo-skills/         # Reference for the Enconvo local HTTP API (port 54535)
  learn/                  # Extracts knowledge from a conversation into memory
```

Two `.gitignore`s exist (root and `curated/`) — both ignore `.DS_Store` and `.env`. Don't commit those.

## Skill Anatomy

Every `SKILL.md` starts with YAML frontmatter. `name` and `description` are required; everything else is optional:

```yaml
---
name: skill-name                 # must match the directory name
description: "..."               # the trigger text the model reads — be specific & action-oriented
version: 1.0.0                   # optional
author: ...                      # optional
category: audio | tools | ...    # optional
user_invocable: true             # optional — appears as a `/skill-name` slash command
metadata:                        # optional — e.g. short-description for menus
  short-description: ...
---
```

The `description` field is **how the model decides whether to invoke the skill** — it must be discoverable. Lead with concrete trigger phrases ("Use when…", "DEFAULT ACTION:…", "Activates on:…"). Examples in `curated/voicebox/SKILL.md`, `curated/video-creativity/SKILL.md`, `curated/pptx-design/SKILL.md` show the pattern.

## Path Convention: $SKILL_DIR

When a skill is installed and loaded, the harness exposes its base directory as `$SKILL_DIR`. **Always reference bundled scripts/assets via `$SKILL_DIR`** (e.g. `uv run $SKILL_DIR/scripts/foo.py`) — never hardcode the install path, which varies (`~/.agents/skills/...` vs `~/.config/enconvo/extension/...`).

## Authoring Workflow

Before creating or significantly editing a skill, read `system/skill-creator/SKILL.md`. Key principles enforced there:
- **Concise is key** — context window is shared; only add what the model doesn't already know.
- **Match degrees of freedom to fragility** — narrow scripts for fragile ops, prose for judgment-heavy ones.
- Bundled resources (`scripts/`, `references/`) keep the SKILL.md itself short.

For an established pattern, copy a sibling in `curated/` whose shape matches what you're building (e.g. `pptx-design` for design-heavy doc generation, `voicebox` for script-driven media tools, `botfather` for chat-bot management).

## Commits

This repo commits directly to `main`. Convention seen across history: `<skill-name>: <short imperative summary>` — e.g. `pptx-design: scope AppleScript to app lifecycle`, `video-processor: aspect-aware caption re-split`. Bulk additions use `add: <skill-name> ...`.

There is no CI; reviewers rely on the diff. Do not introduce build/test infrastructure unless the user asks for it.

## When the User Asks About Installing or Browsing Skills

Defer to `system/skill-installer/SKILL.md` — it documents the four install paths (Enconvo store, Skills.sh slug, ClawHub slug, GitHub URL) and the search fallback chain. Do not invent install commands.

## When the User Asks About Calling Enconvo Commands

Defer to `system/enconvo-skills/SKILL.md` — Enconvo exposes every command as `POST http://localhost:54535/{extensionName}/{commandName}` with a JSON body. Use that as the canonical reference; do not duplicate it elsewhere.
