#!/usr/bin/env python3
"""Publish this reviewed repository with the user's existing GitHub CLI identity.

Requires gh and a clean committed Git repository. No force push, token handling,
unrelated repository changes or implicit overwrite of an existing remote.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

from release_scan import scan
from validate_skill import validate

ROOT = Path(__file__).resolve().parents[1]


def run(*args):
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True)


def checked(*args):
    result = run(*args)
    if result.returncode:
        raise ValueError(result.stderr.strip() or "command failed: " + args[0])
    return result.stdout.strip()


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dry-run", action="store_true", help="Show planned steps only; does not check auth or publish")
    args = p.parse_args(argv)
    try:
        settings = json.loads((ROOT / ".github/repository.json").read_text())
        if settings["name"] != "noemorph" or settings["visibility"] != "public":
            raise ValueError("unexpected release identity")
        for result in (validate(ROOT), scan(ROOT)):
            if not result["ok"]:
                raise ValueError("release validation or scan failed")
        if "Apache License" not in (ROOT / "LICENSE").read_text():
            raise ValueError("reviewed LICENSE is required")
        if args.dry_run:
            print(json.dumps({"executed": False, "requires": ["gh auth login", "clean committed local Git repository"],
                "steps": ["read existing gh identity", "inspect same-name repository and origin", "create public noemorph only if absent", "apply description and topics", "push current HEAD without force"],
                "repository_settings": settings}, indent=2))
            return 0
        if not shutil.which("gh"):
            raise ValueError("GitHub CLI (gh) is not installed. Install it, run gh auth login, then retry.")
        checked("gh", "auth", "status")
        owner = checked("gh", "api", "user", "--jq", ".login")
        if owner.casefold() != settings["owner"].casefold():
            raise ValueError("authenticated account differs from the reviewed repository owner; inspect settings before publishing")
        if Path(checked("git", "rev-parse", "--show-toplevel")).resolve() != ROOT:
            raise ValueError("run from this project's own Git repository")
        checked("git", "rev-parse", "HEAD")
        if checked("git", "status", "--porcelain"):
            raise ValueError("commit the reviewed files before publishing")
        identity = owner + "/noemorph"
        remote = run("git", "remote", "get-url", "origin")
        expected = {f"https://github.com/{identity}", f"https://github.com/{identity}.git", f"git@github.com:{identity}.git"}
        if remote.returncode == 0 and remote.stdout.strip() not in expected:
            raise ValueError("origin belongs to another repository; refusing to modify it")
        view = run("gh", "repo", "view", identity, "--json", "nameWithOwner,isPrivate,url")
        if view.returncode == 0:
            info = json.loads(view.stdout)
            if remote.returncode != 0 or info["nameWithOwner"].casefold() != identity.casefold() or info["isPrivate"]:
                raise ValueError("existing repository is not an established public origin for this checkout; inspect it manually")
        elif "Could not resolve to a Repository" in view.stderr or "HTTP 404" in view.stderr:
            if remote.returncode == 0:
                raise ValueError("origin exists but repository lookup failed; inspect permissions before creating")
            checked("gh", "repo", "create", identity, "--public", "--description", settings["description"], "--source", str(ROOT), "--remote", "origin")
        else:
            raise ValueError("cannot establish repository absence: " + view.stderr.strip())
        checked("gh", "repo", "edit", identity, "--description", settings["description"], "--add-topic", ",".join(settings["topics"]))
        checked("git", "push", "--set-upstream", "origin", "HEAD:main")
        print(json.dumps({"repository": "https://github.com/" + identity, "pushed": True}, indent=2))
        return 0
    except (OSError, ValueError, KeyError) as exc:
        print(f"publish error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
