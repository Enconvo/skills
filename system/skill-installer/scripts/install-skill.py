#!/usr/bin/env python3
"""Install a skill from the Enconvo curated skills store."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request


API_BASE = "http://localhost:54535/command/call/skills_manager/api_install_skill"


class InstallError(Exception):
    pass


class Args(argparse.Namespace):
    name: str
    url: str


def _request(api_url: str) -> bytes:
    req = urllib.request.Request(api_url, headers={"User-Agent": "skill-installer"})
    with urllib.request.urlopen(req) as resp:
        return resp.read()


def _install_skill(skill_name: str, download_url: str) -> dict:
    params = {
        "skillName": skill_name,
        "downloadUrl": download_url,
    }
    url = API_BASE + "?" + urllib.parse.urlencode(params)
    try:
        payload = _request(url)
    except urllib.error.HTTPError as exc:
        raise InstallError(f"Install failed: HTTP {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise InstallError(
            f"Failed to connect to skills manager: {exc.reason}"
        ) from exc
    data = json.loads(payload.decode("utf-8"))
    return data


def _parse_args(argv: list[str]) -> Args:
    parser = argparse.ArgumentParser(description="Install a skill.")
    parser.add_argument(
        "--name",
        required=True,
        help="Skill name to install",
    )
    parser.add_argument(
        "--url",
        required=True,
        help="Download URL for the skill",
    )
    return parser.parse_args(argv, namespace=Args())


def main(argv: list[str]) -> int:
    args = _parse_args(argv)
    try:
        result = _install_skill(args.name, args.url)
        if result.get("success"):
            print(f"Installed {args.name} successfully.")
        else:
            msg = result.get("message", "Unknown error")
            print(f"Install response: {msg}", file=sys.stderr)
            return 1
        return 0
    except InstallError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
