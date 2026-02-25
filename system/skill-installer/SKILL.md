---
name: skill-installer
description: Install or uninstall skills from the Enconvo curated skills store, Skills.sh, ClawHub, or a GitHub URL. Use when a user asks to list, install, or uninstall skills.
metadata:
  short-description: Browse, install, and uninstall skills from Enconvo, Skills.sh, and ClawHub
---

# Skill Installer

Helps browse and install skills from the Enconvo curated skills store, Skills.sh, ClawHub, or directly from GitHub. Skills are installed into `.agents/skills`.

Use the helper scripts based on the task:
- List/search skills when the user asks what is available, or if the user uses this skill without specifying what to do.
- List installed skills when the user asks what skills are currently installed.
- Install a skill by name from the Enconvo store (auto-falls back to Skills.sh, then ClawHub), by Skills.sh slug, by ClawHub slug, or by GitHub URL.
- Uninstall a skill when the user wants to remove an installed skill.

## Four Install Methods

1. **From Enconvo store** (by skill name, with fallback chain): Look up the skill in the Enconvo store. If not found, search Skills.sh. If still not found, search ClawHub.
   - Example: `scripts/install-skill.py --name pdf`
2. **From GitHub URL** (supports full repo or subdirectory): Install directly from a GitHub URL.
   - Repo: `scripts/install-skill.py --url https://github.com/tivojn/xlsx-design-agent`
   - Subdir: `scripts/install-skill.py --url https://github.com/anthropics/skills/tree/main/skills/pptx`
3. **From Skills.sh** (by slug): Install directly from Skills.sh by owner/repo@skill slug.
   - Example: `scripts/install-skill.py --skills-slug anthropics/skills@pdf`
4. **From ClawHub** (by slug): Install directly from ClawHub by skill slug.
   - Example: `scripts/install-skill.py --slug nano-pdf`

## Search Fallback Chain

When searching for skills (`list-skills.py --search <keyword>`):
1. **Enconvo store** is searched first.
2. If no results, **Skills.sh** (`skills find`) is searched.
3. If still no results, **ClawHub** (`clawdhub search`) is searched.

Results from each source are displayed under separate sections.

## Communication

When listing skills, output approximately as follows:
"""
Available skills from Enconvo:
1. skill-name - Short description
2. skill-name (already installed) - Short description

From Skills.sh:
3. owner/repo@skill (21K installs)
4. ...

From ClawHub:
5. skill-slug v1.0.0 - Title (score: 3.5)
6. ...

Which ones would you like installed?
"""

When installing from a fallback source, tell the user which source it came from.

After installing a skill, tell the user: "Use / to select and use the installed skill."

## Scripts

All of these scripts use network, so when running in the sandbox, request escalation when running them.

- `scripts/list-skills.py` (prints skills list with installed annotations)
- `scripts/list-skills.py --search <keyword>` (search/filter skills; falls back to Skills.sh then ClawHub)
- `scripts/list-skills.py --format json` (JSON output with name, title, description, source, etc.)
- `scripts/installed-skills.py` (prints all installed skills)
- `scripts/installed-skills.py --format json` (JSON output of installed skills)
- `scripts/install-skill.py --name <skill-name>` (install from Enconvo store -> Skills.sh -> ClawHub)
- `scripts/install-skill.py --url <github-url>` (install from GitHub, name derived from URL)
- `scripts/install-skill.py --skills-slug <owner/repo@skill>` (install directly from Skills.sh)
- `scripts/install-skill.py --slug <clawdhub-slug>` (install directly from ClawHub)
- `scripts/uninstall-skill.py --name <skill-name>`

## API Details

The scripts use the Enconvo skills manager API:
- List skills: `http://localhost:54535/command/call/skills_manager/api_skills_list?search=<keyword>`
- Install skill from store: `http://localhost:54535/command/call/skills_manager/api_install_skill?skillName=<name>&downloadUrl=<url>`
- Install skill from github: `http://localhost:54535/command/call/skills_manager/api_install_skill&githubUrl=<url>`
- Installed skills: `http://localhost:54535/command/call/skills_manager/get_all_installed_skills`
- Uninstall skill: `http://localhost:54535/command/call/skills_manager/api_uninstall_skill?skillName=<name>`

Skills.sh CLI (second fallback):
- Search: `skills find <query>`
- Install: `skills add <owner/repo@skill> --agent universal -g -y`

ClawHub CLI (third fallback):
- Search: `clawdhub search <query>`
- Install: `clawdhub install <slug> [--version <version>]`
- Prerequisite: `npm i -g clawdhub`

## Behavior and Options

- Lists all Enconvo curated skills by default; use `--search` to filter.
- Each skill in the list shows its installed status.
- When installing by name only (`--name`), the script follows the fallback chain: Enconvo store -> Skills.sh -> ClawHub.
- When installing by Skills.sh slug (`--skills-slug`), the skill is installed directly from Skills.sh.
- When installing by ClawHub slug (`--slug`), the skill is installed directly from ClawHub.
- When installing by URL (`--url`), the skill name is derived automatically from the URL.
- GitHub URLs support both full repo (`https://github.com/owner/repo`) and subdirectory (`https://github.com/owner/repo/tree/branch/path/to/skill`).
- Skills are installed into `.agents/skills` via the Enconvo skills manager service, Skills.sh CLI, or ClawHub CLI.

## Notes

- The Enconvo skills manager API must be running on `localhost:54535` for store-based operations.
- Skills.sh CLI (`skills`) is used as the second fallback source.
- ClawHub CLI (`clawdhub`) must be installed globally (`npm i -g clawdhub`) for ClawHub fallback to work.
- When the user provides a skill name without a URL, search Enconvo store first, then Skills.sh, then ClawHub.
- When the user provides a GitHub URL, install directly from that URL.
