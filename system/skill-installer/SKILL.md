---
name: skill-installer
description: Install skills from the Enconvo curated skills store. Use when a user asks to list installable skills, search for skills, or install a skill.
metadata:
  short-description: Browse and install curated skills from Enconvo
---

# Skill Installer

Helps browse and install skills from the Enconvo curated skills store via the local skills manager API. Skills are installed into `.agents/skills`.

Use the helper scripts based on the task:
- List/search skills when the user asks what is available, or if the user uses this skill without specifying what to do.
- Install a skill when the user provides a skill name or selects one from the list.

Install skills with the helper scripts.

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
- `scripts/install-skill.py --name <skill-name> --url <download-url>`

## API Details

The scripts use the Enconvo skills manager API:
- List skills: `http://localhost:54535/command/call/skills_manager/api_skills_list?search=<keyword>`
- Install skill: `http://localhost:54535/command/call/skills_manager/api_install_skill?skillName=<name>&downloadUrl=<url>`

## Behavior and Options

- Lists all Enconvo curated skills by default; use `--search` to filter.
- Each skill in the list shows its installed status.
- Installation requires both `--name` (skill name) and `--url` (download URL), both available from the list output.
- Skills are installed into `.agents/skills` via the Enconvo skills manager service.

## Notes

- The Enconvo skills manager API must be running on `localhost:54535` for the scripts to work.
- Skill names and download URLs come from the list API response.
- When the user wants to install a skill, first list skills to get the correct name and download URL, then install.
