#!/usr/bin/env python3
"""Install a skill from the Enconvo store or a GitHub URL."""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request


API_INSTALL = "http://localhost:54535/command/call/skills_manager/api_install_skill"
API_LIST = "http://localhost:54535/command/call/skills_manager/api_skills_list"


class InstallError(Exception):
    pass


class Args(argparse.Namespace):
    name: str | None
    url: str | None


def _request(api_url: str) -> bytes:
    req = urllib.request.Request(api_url, headers={"User-Agent": "skill-installer"})
    with urllib.request.urlopen(req) as resp:
        return resp.read()


def _is_github_url(s: str) -> bool:
    return bool(re.match(r"https?://github\.com/", s))


def _find_skill_in_store(skill_name: str) -> dict | None:
    """Search the store for a skill by name and return its info."""
    params = {"search": skill_name}
    url = API_LIST + "?" + urllib.parse.urlencode(params)
    try:
        payload = _request(url)
    except (urllib.error.HTTPError, urllib.error.URLError):
        return None
    data = json.loads(payload.decode("utf-8"))
    skills = data.get("data", {}).get("list", [])
    for s in skills:
        if s.get("name") == skill_name:
            return s
    return None


def _install_from_store(skill_name: str, download_url: str) -> dict:
    """Install via skillName + downloadUrl."""
    params = {
        "skillName": skill_name,
        "downloadUrl": download_url,
    }
    url = API_INSTALL + "?" + urllib.parse.urlencode(params)
    try:
        payload = _request(url)
    except urllib.error.HTTPError as exc:
        raise InstallError(f"Install failed: HTTP {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise InstallError(
            f"Failed to connect to skills manager: {exc.reason}"
        ) from exc
    return json.loads(payload.decode("utf-8"))


def _install_from_github(github_url: str) -> dict:
    """Install via githubUrl."""
    params = {"githubUrl": github_url}
    url = API_INSTALL + "?" + urllib.parse.urlencode(params)
    try:
        payload = _request(url)
    except urllib.error.HTTPError as exc:
        raise InstallError(f"Install failed: HTTP {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise InstallError(
            f"Failed to connect to skills manager: {exc.reason}"
        ) from exc
    return json.loads(payload.decode("utf-8"))


def _parse_args(argv: list[str]) -> Args:
    parser = argparse.ArgumentParser(
        description="Install a skill from the Enconvo store or a GitHub URL.",
        epilog=(
            "Examples:\n"
            "  %(prog)s --name pdf                    # install from store\n"
            "  %(prog)s --url https://github.com/...  # install from GitHub URL\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--name",
        default=None,
        help="Skill name to install from the Enconvo store",
    )
    group.add_argument(
        "--url",
        default=None,
        help="GitHub URL to install from (supports repo and subdirectory URLs)",
    )
    return parser.parse_args(argv, namespace=Args())


def main(argv: list[str]) -> int:
    args = _parse_args(argv)

    try:
        # Mode 1: --url (GitHub URL) -> install via githubUrl
        if args.url:
            result = _install_from_github(args.url)
            if result.get("success"):
                print(f"Installed skill from {args.url} successfully.")
            else:
                msg = result.get("error", result.get("message", "Unknown error"))
                print(f"Install failed: {msg}", file=sys.stderr)
                return 1
            return 0

        # Mode 2: --name -> look up in store, then install via skillName & downloadUrl
        if args.name:
            store_info = _find_skill_in_store(args.name)
            if not store_info:
                raise InstallError(
                    f"Skill '{args.name}' not found in the Enconvo store."
                )
            download_url = store_info.get("download_url", "")
            if not download_url:
                raise InstallError(
                    f"No download URL found for skill '{args.name}'."
                )
            result = _install_from_store(args.name, download_url)
            if result.get("success"):
                print(f"Installed {args.name} successfully from Enconvo store.")
            else:
                msg = result.get("error", result.get("message", "Unknown error"))
                print(f"Install failed: {msg}", file=sys.stderr)
                return 1
            return 0

        print("Error: provide --name (store install) or --url (GitHub install).",
              file=sys.stderr)
        return 1

    except InstallError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
