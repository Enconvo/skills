#!/usr/bin/env python3
"""List skills from the Enconvo curated skills store, with Skills.sh and ClawHub fallback."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request


API_BASE = "http://localhost:54535/command/call/skills_manager/api_skills_list"


class ListError(Exception):
    pass


class Args(argparse.Namespace):
    search: str | None
    format: str


def _request(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "skill-installer"})
    with urllib.request.urlopen(req) as resp:
        return resp.read()


def _list_skills(search: str | None) -> list[dict]:
    params = {}
    if search:
        params["search"] = search
    url = API_BASE
    if params:
        url += "?" + urllib.parse.urlencode(params)
    try:
        payload = _request(url)
    except urllib.error.HTTPError as exc:
        raise ListError(f"Failed to fetch skills: HTTP {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise ListError(f"Failed to connect to skills manager: {exc.reason}") from exc
    data = json.loads(payload.decode("utf-8"))
    if not data.get("success"):
        raise ListError("Skills API returned an error.")
    skills_list = data.get("data", {}).get("list", [])
    return skills_list


def _search_skills_sh(query: str) -> list[dict]:
    """Search Skills.sh for skills. Returns list of dicts with slug, name, installs, url."""
    if not shutil.which("skills"):
        return []
    try:
        result = subprocess.run(
            ["skills", "find", query],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []
    if result.returncode != 0:
        return []
    skills = []
    lines = result.stdout.splitlines()
    for i, line in enumerate(lines):
        stripped = line.strip()
        url_m = re.match(r"^└\s+https://skills\.sh/(\S+/\S+/\S+)\s*$", stripped)
        if url_m:
            path = url_m.group(1)
            parts = path.split("/", 2)
            if len(parts) == 3:
                slug = f"{parts[0]}/{parts[1]}@{parts[2]}"
                url = f"https://skills.sh/{path}"
                installs = ""
                display_name = slug
                for j in range(i - 1, max(i - 3, -1), -1):
                    prev = lines[j].strip()
                    inst_m = re.match(r"^(.+?)\s+([\d,.]+[KkMm]?)\s+installs\s*$", prev)
                    if inst_m:
                        display_name = inst_m.group(1).strip()
                        installs = inst_m.group(2)
                        break
                skills.append({
                    "name": display_name,
                    "slug": slug,
                    "installs": installs,
                    "url": url,
                    "source": "skills_sh",
                })
    return skills


def _search_clawdhub(query: str) -> list[dict]:
    """Search ClawHub for skills. Returns a list of dicts with slug, version, title, score."""
    if not shutil.which("clawdhub"):
        return []
    try:
        result = subprocess.run(
            ["clawdhub", "search", query],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []
    if result.returncode != 0:
        return []
    skills = []
    for line in result.stdout.strip().splitlines():
        m = re.match(r"^(\S+)\s+v([\d.]+)\s{2,}(.+?)\s{2,}\(([\d.]+)\)\s*$", line)
        if m:
            skills.append({
                "name": m.group(1),
                "version": m.group(2),
                "title": m.group(3),
                "score": m.group(4),
                "source": "clawdhub",
            })
    return skills


def _parse_args(argv: list[str]) -> Args:
    parser = argparse.ArgumentParser(description="List skills.")
    parser.add_argument(
        "--search",
        default=None,
        help="Search keyword to filter skills",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format",
    )
    return parser.parse_args(argv, namespace=Args())


def main(argv: list[str]) -> int:
    args = _parse_args(argv)
    try:
        skills = _list_skills(args.search)
        skills_sh_skills: list[dict] = []
        clawdhub_skills: list[dict] = []

        # Fallback chain: Enconvo -> Skills.sh -> ClawHub
        if not skills and args.search:
            skills_sh_skills = _search_skills_sh(args.search)
            if not skills_sh_skills:
                clawdhub_skills = _search_clawdhub(args.search)

        if args.format == "json":
            payload = [
                {
                    "name": s.get("name", ""),
                    "title": s.get("title", ""),
                    "description": s.get("description", ""),
                    "download_url": s.get("download_url", ""),
                    "installed": s.get("isInstalled", False),
                    "author": s.get("author", {}).get("name", ""),
                    "version": s.get("version", ""),
                    "source": "enconvo",
                }
                for s in skills
            ]
            payload += [
                {
                    "name": s["name"],
                    "slug": s["slug"],
                    "description": "",
                    "installed": False,
                    "installs": s["installs"],
                    "url": s["url"],
                    "source": "skills_sh",
                }
                for s in skills_sh_skills
            ]
            payload += [
                {
                    "name": s["name"],
                    "title": s["title"],
                    "description": "",
                    "download_url": "",
                    "installed": False,
                    "author": "",
                    "version": s["version"],
                    "source": "clawdhub",
                    "score": s["score"],
                }
                for s in clawdhub_skills
            ]
            print(json.dumps(payload, indent=2))
        else:
            if not skills and not skills_sh_skills and not clawdhub_skills:
                print("No skills found.")
                return 0
            idx = 1
            if skills:
                for s in skills:
                    name = s.get("name", "unknown")
                    installed = s.get("isInstalled", False)
                    suffix = " (already installed)" if installed else ""
                    desc = s.get("description", "")
                    if len(desc) > 80:
                        desc = desc[:77] + "..."
                    print(f"{idx}. {name}{suffix}")
                    if desc:
                        print(f"   {desc}")
                    idx += 1
            if skills_sh_skills:
                print(f"\nFrom Skills.sh:")
                for s in skills_sh_skills:
                    installs = s["installs"]
                    print(f"{idx}. {s['slug']} ({installs} installs)")
                    idx += 1
            if clawdhub_skills:
                print(f"\nFrom ClawHub:")
                for s in clawdhub_skills:
                    title = s["title"]
                    version = s["version"]
                    score = s["score"]
                    print(f"{idx}. {s['name']} v{version} - {title} (score: {score})")
                    idx += 1
        return 0
    except ListError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
