---
name: skill-installer
description: Install or uninstall skills from the Enconvo curated skills store or from a GitHub URL. Use when a user asks to list, install, or uninstall skills.
metadata:
  short-description: Browse, install, and uninstall curated skills from Enconvo
---

# Skill Installer

Helps browse and install skills from the Enconvo curated skills store or directly from GitHub. Skills are installed into `.agents/skills`.

Use the helper scripts based on the task:
- List/search skills when the user asks what is available, or if the user uses this skill without specifying what to do.
- List installed skills when the user asks what skills are currently installed.
- Install a skill by name from the Enconvo store, or by GitHub URL (supports repo and subdirectory URLs).
- Uninstall a skill when the user wants to remove an installed skill.

## Two Install Methods

1. **From Enconvo store** (by skill name): Look up the skill in the store and install it.
   - Example: `scripts/install-skill.py --name pdf`
2. **From GitHub URL** (supports full repo or subdirectory): Install directly from a GitHub URL.
   - Repo: `scripts/install-skill.py --url https://github.com/tivojn/xlsx-design-agent`
   - Subdir: `scripts/install-skill.py --url https://github.com/anthropics/skills/tree/main/skills/pptx`

## Communication

When listing skills, output approximately as follows:
"""
Available skills from Enconvo:
1. skill-name - Short description
2. skill-name (already installed) - Short description
3. ...
Which ones would you like installed?
"""

After installing a skill, tell the user: "Use / to select and use the installed skill."

## Scripts

All of these scripts use network, so when running in the sandbox, request escalation when running them.

- `scripts/list-skills.py` (prints skills list with installed annotations)
- `scripts/list-skills.py --search <keyword>` (search/filter skills by keyword)
- `scripts/list-skills.py --format json` (JSON output with name, title, description, download_url, installed, author, version)
- `scripts/installed-skills.py` (prints all installed skills)
- `scripts/installed-skills.py --format json` (JSON output of installed skills)
- `scripts/install-skill.py --name <skill-name>` (install from Enconvo store)
- `scripts/install-skill.py --url <github-url>` (install from GitHub, name derived from URL)
- `scripts/uninstall-skill.py --name <skill-name>`

## API Details

The scripts use the Enconvo skills manager API:
- List skills: `http://localhost:54535/command/call/skills_manager/api_skills_list?search=<keyword>`
- Install skill from store: `http://localhost:54535/command/call/skills_manager/api_install_skill?skillName=<name>&downloadUrl=<url>`
- Install skill from github: `http://localhost:54535/command/call/skills_manager/api_install_skill&githubUrl=<url>`
- Installed skills: `http://localhost:54535/command/call/skills_manager/get_all_installed_skills`
- Uninstall skill: `http://localhost:54535/command/call/skills_manager/api_uninstall_skill?skillName=<name>`

## Behavior and Options

- Lists all Enconvo curated skills by default; use `--search` to filter.
- Each skill in the list shows its installed status.
- When installing by name only (`--name`), the script automatically looks up the download URL from the store.
- When installing by URL (`--url`), the skill name is derived automatically from the URL.
- GitHub URLs support both full repo (`https://github.com/owner/repo`) and subdirectory (`https://github.com/owner/repo/tree/branch/path/to/skill`).
- Skills are installed into `.agents/skills` via the Enconvo skills manager service.

## Notes

- The Enconvo skills manager API must be running on `localhost:54535` for the scripts to work.
- When the user provides a skill name without a URL, search the store first to find and install it.
- When the user provides a GitHub URL, install directly from that URL.
