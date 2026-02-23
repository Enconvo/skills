#!/usr/bin/env python3
"""List all installed skills from the Enconvo skills manager."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request


API_BASE = "http://localhost:54535/command/call/skills_manager/get_all_installed_skills"


class ListError(Exception):
    pass


class Args(argparse.Namespace):
    format: str


def _request(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "skill-installer"})
    with urllib.request.urlopen(req) as resp:
        return resp.read()


def _get_installed_skills() -> list[dict]:
    try:
        payload = _request(API_BASE)
    except urllib.error.HTTPError as exc:
        raise ListError(f"Failed to fetch installed skills: HTTP {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise ListError(
            f"Failed to connect to skills manager: {exc.reason}"
        ) from exc
    data = json.loads(payload.decode("utf-8"))
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return data.get("data", data.get("skills", []))
    return []


def _parse_args(argv: list[str]) -> Args:
    parser = argparse.ArgumentParser(description="List all installed skills.")
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
        skills = _get_installed_skills()
        if args.format == "json":
            print(json.dumps(skills, indent=2))
        else:
            if not skills:
                print("No skills installed.")
                return 0
            for idx, s in enumerate(skills, start=1):
                if isinstance(s, str):
                    print(f"{idx}. {s}")
                else:
                    name = s.get("name", "unknown")
                    desc = s.get("description", "")
                    if len(desc) > 80:
                        desc = desc[:77] + "..."
                    print(f"{idx}. {name}")
                    if desc:
                        print(f"   {desc}")
        return 0
    except ListError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
