#!/usr/bin/env python3
"""Dependency-free checks equivalent to the applicable Agent Skills constraints.

The repository intentionally uses only flat, single-line YAML scalar frontmatter.
This is not a general YAML parser or a replacement for skills-ref on other skills.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

ALLOWED = {"name", "description", "license", "compatibility", "allowed-tools"}


def validate(root):
    root = Path(root).resolve()
    errors, warnings = [], []
    source = root / "SKILL.md"
    if not source.is_file():
        return {"ok": False, "errors": ["missing SKILL.md"], "warnings": []}
    content = source.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n(.+)\Z", content, re.S)
    if not match:
        return {"ok": False, "errors": ["invalid YAML frontmatter boundary or missing body"], "warnings": []}
    fields = {}
    for line in match[1].splitlines():
        item = re.fullmatch(r"([a-z][a-z-]*): ([^\n]+)", line)
        if not item or item[1] not in ALLOWED or item[1] in fields:
            errors.append("unsupported, duplicate or malformed flat frontmatter field")
            continue
        value = item[2]
        # These forms would be ambiguous YAML; this project does not use them.
        if value[0] in "|>{[&*!\"'" or ": " in value or " #" in value or value.lower() in {"true","false","null","~"}:
            errors.append("frontmatter must use an unambiguous plain string scalar")
        fields[item[1]] = value
    name = fields.get("name", "")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 64:
        errors.append("name violates Agent Skills naming constraints")
    if name != root.name:
        errors.append("name must match the skill directory")
    description = fields.get("description", "")
    if not 1 <= len(description) <= 1024:
        errors.append("description length must be 1–1024 characters")
    if "compatibility" in fields and not 1 <= len(fields["compatibility"]) <= 500:
        errors.append("compatibility length must be 1–500 characters")
    if len(content.splitlines()) >= 500:
        warnings.append("entrypoint reaches the recommended 500-line limit")
    references = re.findall(r"\[[^\]]+\]\(([^)]+)\)", match[2])
    references += re.findall(r"`((?:scripts|references|docs)/[^`\s]+\.(?:py|md|json|html))`", match[2])
    for ref in sorted(set(references)):
        if re.match(r"https?://", ref) or ref.startswith("#"):
            continue
        target = (root / ref.split("#")[0]).resolve()
        if not target.is_relative_to(root) or not target.is_file():
            errors.append("unresolved or escaping entrypoint reference: " + ref)
    return {"ok": not errors, "errors": errors, "warnings": warnings,
            "name": name, "description_characters": len(description),
            "compatibility_characters": len(fields.get("compatibility", "")),
            "entrypoint_lines": len(content.splitlines()), "references_checked": len(set(references)),
            "specification": "https://agentskills.io/specification", "method": "equivalent checks for this repository's flat YAML subset"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    result = validate(args.path)
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
