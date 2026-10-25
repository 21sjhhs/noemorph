#!/usr/bin/env python3
"""Scan the candidate release for common secrets and personal paths; redact matches.

This is a bounded pattern scan, not proof that arbitrary credentials are absent.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

EXCLUDED = {".git", "__pycache__", ".venv", "node_modules", "dist", "runs", "local-runs", "test-results", ".secrets"}
PATTERNS = {
    "github_token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b|\bgithub_pat_[A-Za-z0-9_]{30,}\b"),
    "api_key": re.compile(r"\bsk-(?:proj-|ant-)?[A-Za-z0-9_-]{20,}\b"),
    "aws_access_key": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "private_key": re.compile(r"-----BEGIN " + r"(?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "credential_in_url": re.compile(r"https?://[^\s/:@]+:[^\s/@]+@"),
    "personal_absolute_path": re.compile(r"/(?:Users|Volumes)/[^\s\"'<>]+|" + r"/" + r"home/(?!runner(?:/|\b))[^\s\"'<>]+"),
}
FORBIDDEN_NAMES = {".env", "credentials.json", "id_rsa", "id_ed25519"}


def release_files(root):
    root = Path(root).resolve()
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if any(part in EXCLUDED for part in relative.parts) or relative.name == ".DS_Store" or relative.parts[:2] == ("audit", "private"):
            continue
        if path.is_symlink():
            raise ValueError("release cannot include symlink: " + relative.as_posix())
        if path.is_file() and path.suffix not in {".pyc", ".log"}:
            yield path


def scan(root):
    root = Path(root).resolve()
    findings, count = [], 0
    for path in release_files(root):
        count += 1
        name = path.relative_to(root).as_posix()
        if path.name in FORBIDDEN_NAMES or path.name.startswith('.env.') and path.name != '.env.example' or path.suffix in {'.pem', '.key'}:
            findings.append({"file": name, "line": 0, "kind": "sensitive_filename", "match": "[REDACTED]"})
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # Binary assets need separate human inspection; filenames are still checked.
            continue
        for line_number, line in enumerate(text.splitlines(), 1):
            for kind, pattern in PATTERNS.items():
                if pattern.search(line):
                    findings.append({"file": name, "line": line_number, "kind": kind, "match": "[REDACTED]"})
    return {"ok": not findings, "files_scanned": count, "findings": findings,
            "limits": "Common token formats, key headers, credential URLs and personal paths only; no arbitrary-secret or legal clearance guarantee."}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("path", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    args = p.parse_args(argv)
    try:
        result = scan(args.path)
        print(json.dumps(result, indent=2))
        return 0 if result["ok"] else 1
    except (OSError, ValueError) as exc:
        print(f"release scan error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
