#!/usr/bin/env python3
"""List skills from the Enconvo curated skills store."""

from __future__ import annotations

import argparse
import json
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
                }
                for s in skills
            ]
            print(json.dumps(payload, indent=2))
        else:
            if not skills:
                print("No skills found.")
                return 0
            for idx, s in enumerate(skills, start=1):
                name = s.get("name", "unknown")
                installed = s.get("isInstalled", False)
                suffix = " (already installed)" if installed else ""
                desc = s.get("description", "")
                # Truncate long descriptions
                if len(desc) > 80:
                    desc = desc[:77] + "..."
                print(f"{idx}. {name}{suffix}")
                if desc:
                    print(f"   {desc}")
        return 0
    except ListError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
