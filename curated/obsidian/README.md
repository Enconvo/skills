Agent Skills for use with Obsidian.

These skills follow the [Agent Skills specification](https://agentskills.io/specification) so they can be used by any skills-compatible agent, including Claude Code and Codex CLI.

## Installation

### Marketplace

```
/plugin marketplace add kepano/obsidian-skills
/plugin install obsidian@obsidian-skills
```

### Manually

#### Claude Code

Add the contents of this repo to a `/.claude` folder in the root of your Obsidian vault (or whichever folder you're using with Claude Code). See more in the [official Claude Skills documentation](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview).

#### Codex CLI

Copy the `skills/` directory into your Codex skills path (typically `~/.codex/skills`). See the [Agent Skills specification](https://agentskills.io/specification) for the standard skill format.

## Skill

| Skill | Description |
|-------|-------------|
| [obsidian](skills/obsidian) | Work with Obsidian vaults — Markdown, Bases, Canvas, CLI, and web content extraction |

### References

The obsidian skill includes detailed references for each area:

| Reference | Description |
|-----------|-------------|
| [obsidian-markdown](skills/obsidian/references/obsidian-markdown.md) | [Obsidian Flavored Markdown](https://help.obsidian.md/obsidian-flavored-markdown) (`.md`) — wikilinks, embeds, callouts, properties, and Obsidian-specific syntax |
| [obsidian-bases](skills/obsidian/references/obsidian-bases.md) | [Obsidian Bases](https://help.obsidian.md/bases/syntax) (`.base`) — views, filters, formulas, and summaries |
| [json-canvas](skills/obsidian/references/json-canvas.md) | [JSON Canvas](https://jsoncanvas.org/) files (`.canvas`) — nodes, edges, groups, and connections |
| [obsidian-cli](skills/obsidian/references/obsidian-cli.md) | [Obsidian CLI](https://help.obsidian.md/cli) — vault interaction, plugin and theme development |
| [defuddle](skills/obsidian/references/defuddle.md) | [Defuddle](https://github.com/kepano/defuddle-cli) — extract clean markdown from web pages |
