#!/usr/bin/env python3
"""Verify the copied research engine against its recorded baseline."""
import hashlib
import json
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
lock = json.loads((root / "upstream.lock.json").read_text())
failures = []
for name, record in lock["files"].items():
    path = root / record.get("preserved_path", name)
    if not path.is_file():
        failures.append(name + ": missing")
        continue
    data = path.read_bytes()
    if record["mode"] == "prefix":
        data = data[:record["bytes"]]
    if hashlib.sha256(data).hexdigest() != record["sha256"]:
        failures.append(name + ": recorded baseline changed")
print("\n".join(failures) if failures else f"PASS: {len(lock['files'])} research baseline records verified.")
sys.exit(bool(failures))
