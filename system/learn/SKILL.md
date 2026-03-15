---
name: learn
description: Review the current conversation history and extract valuable knowledge. Use when the user asks to "learn from this conversation", "summarize what to remember", "extract skills from chat history", or "what should we remember from this session". The skill analyzes the dialogue, identifies reusable knowledge worth storing as memories or skills, and persists them using the memory system.
---

# Learn — Extract & Persist Knowledge from Conversation

Analyze the current conversation history and extract knowledge worth keeping long-term.

## Workflow

### 1. Scan the Conversation

Review the full conversation history in context. Look for:

- **Facts learned** — new tools, APIs, configs, domain knowledge discovered during the session
- **Decisions made** — architectural choices, trade-offs, approaches chosen and why
- **Problems solved** — bugs fixed, errors resolved, workarounds found
- **Preferences revealed** — how the user likes things done, their workflow habits
- **Reusable procedures** — multi-step workflows that will likely recur

### 2. Classify Each Item

For each piece of knowledge, decide:

| Type | Use when | Tool |
|------|----------|------|
| Simple fact / preference | One-liner, no procedure | `add_to_memory` |
| Person / contact | Someone the user knows | `add_to_memory` (category: person) |
| Reusable procedure / technique | Multi-step, tool-specific, likely to recur | Create a skill via `skill-creator`, then `add_to_memory` linking the skill |
| Project decision | Architectural or design choice | `add_to_memory` (category: decision) |

### 3. Check for Duplicates First

Before adding anything, run `search_memory` on relevant keywords. If a memory already exists:
- Update it with `update_memory` if new info adds value
- Skip it if it's already accurate and complete

### 4. Write Memories

For each item worth keeping:

**Simple memory:**
```
add_to_memory({
  content: "<informative summary with key details, not just a title>",
  category: "fact" | "experience" | "preference" | "decision" | "person",
  importance: 0.4–1.0,
  tags: ["relevant", "tags"]
})
```

**Skill-worthy knowledge** (use `skill-creator` skill first to create the skill file, then):
```
add_to_memory({
  content: "<summary of what the skill covers and when to use it>",
  category: "skill",
  importance: 0.7–0.9,
  tags: ["skill", "topic"],
  references: [{ type: "skill", name: "<skill-name>" }]
})
```

### 5. Report to User

After persisting, give the user a brief summary:

- How many memories were added / updated
- Which skills were created (if any)
- What was skipped and why (already known, too trivial, etc.)

Keep the report concise — bullet list, no fluff.

## Importance Scoring Guide

- **0.9–1.0** — Critical: workflow-changing, frequently needed, hard to rediscover
- **0.7–0.8** — High: project-specific decisions, reusable techniques
- **0.5–0.6** — Medium: useful context, preferences, tool configs
- **0.3–0.4** — Low: minor facts, one-off observations

## What NOT to Save

- Trivial small talk or greetings
- Temporary context that won't apply again
- Information the user can easily find elsewhere
- Sensitive credentials or secrets
- Exact conversation quotes (summarize instead)
