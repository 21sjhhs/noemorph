#!/usr/bin/env python3
"""Workflow state audit for an unseeded conceptual discovery skill.

This utility checks structure and stage ordering. It neither performs research
nor verifies the truth of assertions, citation validity, or actual agent spawning.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys
import tempfile

STATUS_VALUES = {"verified_direct", "supported_with_limits", "inferred", "unresolved", "contradicted"}
REQUIRED_DIRECTION = (
    "id", "question", "anchor_ids", "logical_move", "discovery_target",
    "search_route", "bridge_test", "novelty_reason", "unknowns"
)
REQUIRED_HOP = ("question", "finding", "relation", "evidence_refs", "status")


def fail(msg: str) -> None:
    raise ValueError(msg)


def text_field(obj, name: str) -> str:
    value = obj.get(name)
    if not isinstance(value, str) or not value.strip():
        fail(f"missing or blank text field: {name}")
    return value.strip()


def list_field(obj, name: str, *, nonempty=False) -> list:
    value = obj.get(name)
    if not isinstance(value, list) or (nonempty and not value):
        fail(f"expected list for field: {name}")
    return value


def load(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        obj = json.load(f)
    if not isinstance(obj, dict):
        fail("top-level JSON value must be an object")
    return obj


def write(path: str, value: dict) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".noemorph-", suffix=".json", dir=p.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(value, f, ensure_ascii=False, indent=2)
            f.write("\n")
        os.replace(tmp, p)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def normalize(s: str) -> str:
    return re.sub(r"\W+", "", s, flags=re.UNICODE).casefold()


def current(s: dict) -> dict:
    return s["history"][-1]


def check_phase(s: dict, target: str) -> None:
    if s["phase"] != target:
        fail(f"expected phase={target}; actual phase={s['phase']}")


def init(a) -> dict:
    if Path(a.state).exists():
        fail("state file already exists; use an independent run directory")
    if a.rounds < 1 or a.agents < 1:
        fail("rounds and agents must be positive")
    if a.top_n is not None and not (1 <= a.top_n <= 5 * a.agents):
        fail("top-n must be between 1 and agents*5")
    s = {
        "version": "4.0", "question": a.question,
        "config": {"macro_rounds": a.rounds, "agents": a.agents,
                   "breadth_per_agent": 5, "top_n": a.top_n, "depth_hops": 3},
        "decomposition": None, "phase": "decomposition", "current_round": 1,
        "history": [{"round": 1, "breadth": {}, "selected": [], "depth": {}, "closed": False}],
        "frontier": [],
    }
    write(a.state, s)
    return s


def decomp(a) -> dict:
    s = load(a.state)
    check_phase(s, "decomposition")
    item = load(a.input)
    concepts = list_field(item, "concepts", nonempty=True)
    list_field(item, "relations")
    list_field(item, "open_questions")
    ids = set()
    for obj in concepts:
        if not isinstance(obj, dict):
            fail("concept must be an object")
        ident = text_field(obj, "id")
        text_field(obj, "label")
        text_field(obj, "kind")
        if ident in ids:
            fail(f"duplicate concept id: {ident}")
        ids.add(ident)
    s["decomposition"] = item
    s["phase"] = "breadth"
    write(a.state, s)
    return s


def breadth(a) -> dict:
    s = load(a.state)
    check_phase(s, "breadth")
    data = load(a.input)
    if data.get("round") != s["current_round"]:
        fail("wrong macro round in breadth submission")
    aid = text_field(data, "agent_id")
    round_data = current(s)
    if aid in round_data["breadth"]:
        fail(f"agent already submitted: {aid}")
    if len(round_data["breadth"]) >= s["config"]["agents"]:
        fail("all breadth agents already submitted")
    directions = list_field(data, "directions")
    if len(directions) != 5:
        fail("each independent breadth agent must submit exactly five directions")
    other_ids = {d["id"] for r in round_data["breadth"].values() for d in r["directions"]}
    other_questions = {normalize(d["question"]) for r in round_data["breadth"].values() for d in r["directions"]}
    ids, qs = set(), set()
    known_ids = {c["id"] for c in s["decomposition"]["concepts"]}
    known_ids.update(x.get("id") for x in s["frontier"] if isinstance(x, dict))
    for d in directions:
        if not isinstance(d, dict):
            fail("direction must be an object")
        for field in REQUIRED_DIRECTION:
            if field not in d:
                fail(f"missing direction field: {field}")
        did = text_field(d, "id")
        question = text_field(d, "question")
        for field in ("logical_move", "discovery_target", "search_route", "bridge_test", "novelty_reason"):
            text_field(d, field)
        anchors = list_field(d, "anchor_ids", nonempty=True)
        if not all(isinstance(x, str) and x in known_ids for x in anchors):
            fail(f"unrecognized anchor id for direction: {did}")
        if not isinstance(d["unknowns"], (list, str)):
            fail("unknowns must be a list or string")
        if did in ids or did in other_ids:
            fail(f"duplicate direction id: {did}")
        nq = normalize(question)
        if nq in qs or nq in other_questions:
            fail(f"duplicate direction question: {question}")
        ids.add(did)
        qs.add(nq)
    round_data["breadth"][aid] = data
    if len(round_data["breadth"]) == s["config"]["agents"]:
        s["phase"] = "selection"
    write(a.state, s)
    return s


def select(a) -> dict:
    s = load(a.state)
    check_phase(s, "selection")
    ids = [x.strip() for x in a.ids.split(",") if x.strip()]
    if len(ids) != len(set(ids)):
        fail("duplicate selected ids")
    if not ids:
        fail("selection cannot be empty")
    top_n = s["config"]["top_n"]
    if top_n is not None and len(ids) != top_n:
        fail(f"selection count must equal configured top-n={top_n}")
    available = {d["id"] for r in current(s)["breadth"].values() for d in r["directions"]}
    if not set(ids).issubset(available):
        fail("selected direction not among current breadth candidates")
    current(s)["selected"] = ids
    s["phase"] = "depth"
    write(a.state, s)
    return s


def depth(a) -> dict:
    s = load(a.state)
    check_phase(s, "depth")
    item = load(a.input)
    if item.get("round") != s["current_round"]:
        fail("wrong macro round in depth submission")
    direction_id = text_field(item, "direction_id")
    text_field(item, "agent_id")
    r = current(s)
    if direction_id not in r["selected"]:
        fail("depth direction was not selected")
    if direction_id in r["depth"]:
        fail("this selected direction already has a depth submission")
    hops = list_field(item, "hops", nonempty=True)
    if len(hops) < 3:
        fail("at least three deepening attempts are required (unresolved allowed)")
    for hop in hops:
        if not isinstance(hop, dict):
            fail("hop must be an object")
        for field in REQUIRED_HOP:
            if field not in hop:
                fail(f"missing hop field: {field}")
        for field in ("question", "finding", "relation"):
            text_field(hop, field)
        list_field(hop, "evidence_refs")
        if hop["status"] not in STATUS_VALUES:
            fail("invalid evidence status")
    for field in ("new_concepts", "bridges", "limits", "unresolved"):
        list_field(item, field)
    text_field(item, "boundary_change")
    r["depth"][direction_id] = item
    if len(r["depth"]) == len(r["selected"]):
        s["phase"] = "round_close"
    write(a.state, s)
    return s


def close(a) -> dict:
    s = load(a.state)
    check_phase(s, "round_close")
    r = current(s)
    r["closed"] = True
    old_frontier = {f.get("id"): f for f in s["frontier"] if isinstance(f, dict) and f.get("id")}
    for sub in r["depth"].values():
        for c in sub["new_concepts"]:
            if isinstance(c, dict) and isinstance(c.get("id"), str) and c["id"]:
                old_frontier[c["id"]] = c
    s["frontier"] = list(old_frontier.values())
    if s["current_round"] == s["config"]["macro_rounds"]:
        s["phase"] = "finished"
    else:
        s["current_round"] += 1
        s["history"].append({"round": s["current_round"], "breadth": {}, "selected": [], "depth": {}, "closed": False})
        s["phase"] = "breadth"
    write(a.state, s)
    return s


def status(a) -> dict:
    s = load(a.state)
    r = current(s)
    return {
        "phase": s["phase"], "current_round": s["current_round"],
        "macro_rounds": s["config"]["macro_rounds"],
        "expected_agents": s["config"]["agents"],
        "breadth_agents_submitted": len(r["breadth"]),
        "breadth_directions_submitted": sum(len(b["directions"]) for b in r["breadth"].values()),
        "selected_directions": len(r["selected"]),
        "depth_submissions": len(r["depth"]),
        "closed_rounds": sum(bool(x["closed"]) for x in s["history"]),
        "frontier_concepts": len(s["frontier"]),
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sp = p.add_subparsers(dest="command", required=True)
    q = sp.add_parser("init")
    q.add_argument("--state", required=True)
    q.add_argument("--question", required=True)
    q.add_argument("--rounds", type=int, required=True)
    q.add_argument("--agents", type=int, default=5)
    q.add_argument("--top-n", type=int, default=None)
    for name in ("decomp", "breadth", "depth"):
        q = sp.add_parser(name)
        q.add_argument("--state", required=True)
        q.add_argument("--input", required=True)
    q = sp.add_parser("select")
    q.add_argument("--state", required=True)
    q.add_argument("--ids", required=True)
    for name in ("close", "status"):
        q = sp.add_parser(name)
        q.add_argument("--state", required=True)
    a = p.parse_args()
    try:
        obj = globals()[a.command](a)
        if a.command != "status":
            obj = status(a)
        print(json.dumps(obj, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as e:
        print(f"state validation error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
