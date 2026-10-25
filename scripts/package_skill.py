#!/usr/bin/env python3
"""Build a scanned, reproducible noemorph/ ZIP; never publish or install it."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile

from release_scan import scan, release_files
from validate_skill import validate


def package(root, output):
    root, output = Path(root).resolve(), Path(output).resolve()
    if output.suffix.lower() != ".zip":
        raise ValueError("output must end with .zip")
    for check in (validate(root), scan(root)):
        if not check["ok"]:
            raise ValueError("release checks failed: " + json.dumps(check))
    if not (root / "LICENSE").is_file() or "Apache License" not in (root / "LICENSE").read_text():
        raise ValueError("reviewed Apache-2.0 LICENSE is required")
    files = list(release_files(root))
    if output in files:
        raise ValueError("output must not replace a source file")
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            info = zipfile.ZipInfo("noemorph/" + path.relative_to(root).as_posix(), (2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, path.read_bytes())
    return {"archive": str(output), "files": len(files), "sha256": hashlib.sha256(output.read_bytes()).hexdigest()}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, default=Path("dist/noemorph.zip"))
    args = p.parse_args(argv)
    try:
        print(json.dumps(package(Path(__file__).resolve().parents[1], args.output), indent=2))
        return 0
    except (OSError, ValueError) as exc:
        print(f"package error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
