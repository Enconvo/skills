#!/usr/bin/env python3
"""Install a skill from the Enconvo store, Skills.sh, ClawHub, or GitHub URL."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

CLAWDHUB_INSTALL_DIR = os.path.expanduser("~/.agents")

# npm package names for CLI dependencies
_CLI_PACKAGES = {
    "skills": "skills",
    "clawdhub": "clawdhub",
}

API_INSTALL = "http://localhost:54535/command/call/skills_manager/api_install_skill"
API_LIST = "http://localhost:54535/command/call/skills_manager/api_skills_list"


class InstallError(Exception):
    pass


def _ensure_cli(cmd: str) -> None:
    """Ensure a CLI tool is installed, auto-install via npm if missing."""
    if shutil.which(cmd):
        return
    pkg = _CLI_PACKAGES.get(cmd, cmd)
    print(f"'{cmd}' CLI not found. Installing via: npm i -g {pkg} ...")
    try:
        result = subprocess.run(
            ["npm", "i", "-g", pkg],
            capture_output=True,
            text=True,
            timeout=120,
        )
    except FileNotFoundError:
        raise InstallError(
            f"npm not found. Please install Node.js first, then run: npm i -g {pkg}"
        )
    except subprocess.TimeoutExpired:
        raise InstallError(f"Timed out installing {pkg}.")
    if result.returncode != 0:
        raise InstallError(f"Failed to install {pkg}: {result.stderr.strip()}")
    if not shutil.which(cmd):
        raise InstallError(f"Installed {pkg} but '{cmd}' command still not found.")
    print(f"'{cmd}' installed successfully.")


class Args(argparse.Namespace):
    name: str | None
    url: str | None
    slug: str | None
    skills_slug: str | None


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


def _search_skills_sh(query: str) -> list[dict]:
    """Search Skills.sh for skills. Returns list of dicts with slug, name, installs, url."""
    _ensure_cli("skills")
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
                    "slug": slug,
                    "name": display_name,
                    "installs": installs,
                    "url": url,
                })
    return skills


def _install_from_skills_sh(slug: str) -> None:
    """Install a skill from Skills.sh via the skills CLI."""
    _ensure_cli("skills")
    cmd = ["skills", "add", slug, "--agent", "universal", "-g", "-y"]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired as exc:
        raise InstallError("Skills.sh install timed out.") from exc
    if result.returncode != 0:
        raise InstallError(
            f"Skills.sh install failed: {result.stderr.strip() or result.stdout.strip()}"
        )
    print(result.stdout.strip())


def _search_clawdhub(query: str) -> list[dict]:
    """Search ClawHub for skills. Returns list of dicts with slug, version, title, score."""
    _ensure_cli("clawdhub")
    try:
        result = subprocess.run(
            ["clawdhub", "search", query],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except subprocess.TimeoutExpired as exc:
        raise InstallError("ClawHub search timed out.") from exc
    if result.returncode != 0:
        raise InstallError(f"ClawHub search failed: {result.stderr.strip()}")
    skills = []
    for line in result.stdout.strip().splitlines():
        m = re.match(r"^(\S+)\s+v([\d.]+)\s{2,}(.+?)\s{2,}\(([\d.]+)\)\s*$", line)
        if m:
            skills.append({
                "slug": m.group(1),
                "version": m.group(2),
                "title": m.group(3),
                "score": m.group(4),
            })
    return skills


def _install_from_clawdhub(slug: str, version: str | None = None) -> None:
    """Install a skill from ClawHub via the clawdhub CLI into ~/.agents/skills/."""
    _ensure_cli("clawdhub")
    os.makedirs(CLAWDHUB_INSTALL_DIR, exist_ok=True)
    cmd = ["clawdhub", "install", slug]
    if version:
        cmd += ["--version", version]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=CLAWDHUB_INSTALL_DIR,
        )
    except subprocess.TimeoutExpired as exc:
        raise InstallError("ClawHub install timed out.") from exc
    if result.returncode != 0:
        raise InstallError(
            f"ClawHub install failed: {result.stderr.strip() or result.stdout.strip()}"
        )
    print(result.stdout.strip())


def _parse_args(argv: list[str]) -> Args:
    parser = argparse.ArgumentParser(
        description="Install a skill from the Enconvo store, Skills.sh, ClawHub, or GitHub URL.",
        epilog=(
            "Examples:\n"
            "  %(prog)s --name pdf                              # install from store (falls back to Skills.sh, then ClawHub)\n"
            "  %(prog)s --url https://github.com/...            # install from GitHub URL\n"
            "  %(prog)s --skills-slug anthropics/skills@pdf     # install directly from Skills.sh\n"
            "  %(prog)s --slug nano-pdf                         # install directly from ClawHub\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--name",
        default=None,
        help="Skill name to install (Enconvo store -> Skills.sh -> ClawHub fallback)",
    )
    group.add_argument(
        "--url",
        default=None,
        help="GitHub URL to install from (supports repo and subdirectory URLs)",
    )
    group.add_argument(
        "--skills-slug",
        default=None,
        dest="skills_slug",
        help="Skills.sh slug to install directly (e.g. anthropics/skills@pdf)",
    )
    group.add_argument(
        "--slug",
        default=None,
        help="ClawHub skill slug to install directly from ClawHub",
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

        # Mode 2: --skills-slug -> install directly from Skills.sh
        if args.skills_slug:
            _install_from_skills_sh(args.skills_slug)
            print(f"Installed {args.skills_slug} successfully from Skills.sh.")
            return 0

        # Mode 3: --slug -> install directly from ClawHub
        if args.slug:
            _install_from_clawdhub(args.slug)
            print(f"Installed {args.slug} successfully from ClawHub.")
            return 0

        # Mode 4: --name -> Enconvo store -> Skills.sh -> ClawHub fallback chain
        if args.name:
            # 1) Try Enconvo store
            store_info = _find_skill_in_store(args.name)
            if store_info:
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

            # 2) Fallback: search Skills.sh
            print(f"Skill '{args.name}' not found in Enconvo store. Searching Skills.sh...")
            skills_sh_results = _search_skills_sh(args.name)
            if skills_sh_results:
                best = skills_sh_results[0]
                slug = best["slug"]
                print(f"Found '{slug}' on Skills.sh ({best['installs']} installs). Installing...")
                _install_from_skills_sh(slug)
                print(f"Installed {slug} successfully from Skills.sh.")
                return 0

            # 3) Fallback: search ClawHub
            print(f"Not found on Skills.sh either. Searching ClawHub...")
            clawdhub_results = _search_clawdhub(args.name)
            if clawdhub_results:
                best = clawdhub_results[0]
                slug = best["slug"]
                print(f"Found '{slug}' v{best['version']} on ClawHub ({best['title']}). Installing...")
                _install_from_clawdhub(slug)
                print(f"Installed {slug} successfully from ClawHub.")
                return 0

            raise InstallError(
                f"Skill '{args.name}' not found in Enconvo store, Skills.sh, or ClawHub."
            )

        print(
            "Error: provide --name, --url, --skills-slug, or --slug.",
            file=sys.stderr,
        )
        return 1

    except InstallError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
