#!/usr/bin/env python3
"""Read-only protocol checks; never research, semantic scoring or citation verification."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from run_card import validate_config
from run_state import normalize, STATUS_VALUES


def audit(state, config=None, require_complete=False):
    errors, warnings = [], []
    def error(code, path):
        errors.append({"code": code, "path": path})
    if not isinstance(state, dict) or state.get("version") != "4.0":
        return {"ok": False, "errors": [{"code": "unsupported_state", "path": "$"}], "warnings": []}
    cfg = validate_config(config) if config is not None else None
    settings = state.get("config", {})
    if not isinstance(settings, dict) or settings.get("agents") != 4:
        error("maintained_protocol_requires_four_breadth_submitters", "config.agents")
        settings = settings if isinstance(settings, dict) else {}
    total = settings.get("macro_rounds")
    if isinstance(total, bool) or not isinstance(total, int) or total < 1:
        error("invalid_round_limit", "config.macro_rounds")
    if cfg:
        for key in ("macro_rounds", "top_n"):
            if cfg[key] is not None and cfg[key] != settings.get(key):
                error("run_configuration_mismatch", "config." + key)
        if cfg["question"] != state.get("question"):
            error("run_question_mismatch", "question")
    minimum = cfg["depth_hops"] if cfg else 3
    history = state.get("history")
    if not isinstance(history, list) or not history:
        error("missing_history", "history")
        history = []
    seen_questions, seen_ids = {}, set()
    counts = {"rounds": len(history), "directions": 0, "selected": 0, "attempts": 0}
    for index, row in enumerate(history):
        path = f"history[{index}]"
        if not isinstance(row, dict):
            error("round_must_be_object", path)
            continue
        if row.get("round") != index + 1:
            error("nonconsecutive_round", path + ".round")
        breadth = row.get("breadth", {})
        if not isinstance(breadth, dict):
            error("breadth_must_be_object", path + ".breadth")
            continue
        completed = row.get("closed") or state.get("phase") == "finished"
        if completed and len(breadth) != 4:
            error("incomplete_breadth", path + ".breadth")
        current_ids, current_questions = set(), set()
        for submission in breadth.values():
            if not isinstance(submission, dict) or not isinstance(submission.get("directions"), list):
                error("invalid_submission", path + ".breadth")
                continue
            directions = submission["directions"]
            if len(directions) != 5:
                error("five_directions_per_submitter_required", path + ".breadth")
            for direction in directions:
                if not isinstance(direction, dict) or not isinstance(direction.get("id"), str) or not isinstance(direction.get("question"), str):
                    error("invalid_direction", path + ".breadth")
                    continue
                ident, question = direction["id"], normalize(direction["question"])
                if ident in current_ids:
                    error("duplicate_direction_id", path + ".breadth")
                if question in current_questions or not question:
                    error("duplicate_or_empty_normalized_question", path + ".breadth")
                if question in seen_questions and seen_questions[question] < index:
                    warnings.append({"code": "cross_round_question_repeated_review_conditions_and_novelty", "path": path + ".breadth"})
                if ident in seen_ids:
                    warnings.append({"code": "direction_id_reused_across_rounds", "path": path + ".breadth"})
                seen_questions[question] = index
                current_ids.add(ident)
                current_questions.add(question)
                counts["directions"] += 1
        seen_ids.update(current_ids)
        selected = row.get("selected", [])
        if not isinstance(selected, list) or any(not isinstance(v, str) for v in selected):
            error("invalid_selected_ids", path + ".selected")
            continue
        if len(set(selected)) != len(selected) or not set(selected).issubset(current_ids):
            error("invalid_selection", path + ".selected")
        if completed and settings.get("top_n") is not None and len(selected) != settings["top_n"]:
            error("selection_count_mismatch", path + ".selected")
        counts["selected"] += len(selected)
        depth = row.get("depth", {})
        if not isinstance(depth, dict):
            error("depth_must_be_object", path + ".depth")
            continue
        if completed and set(depth) != set(selected):
            error("missing_or_unselected_depth", path + ".depth")
        for ident, result in depth.items():
            target = path + ".depth[" + ident + "]"
            if ident not in selected:
                error("unselected_depth", target)
            hops = result.get("hops") if isinstance(result, dict) else None
            if not isinstance(hops, list):
                error("missing_hops", target)
                continue
            if len(hops) < minimum:
                error("configured_depth_not_reached", target)
            counts["attempts"] += len(hops)
            for hop in hops:
                if not isinstance(hop, dict) or hop.get("status") not in STATUS_VALUES:
                    error("invalid_evidence_status", target)
                    continue
                refs = hop.get("evidence_refs")
                if not isinstance(refs, list):
                    error("invalid_evidence_refs", target)
                elif hop["status"] in {"verified_direct", "supported_with_limits"} and not any(ref for ref in refs):
                    error("supported_claim_without_recorded_source", target)
    if isinstance(total, int) and not isinstance(total, bool):
        if len(history) > total:
            error("round_limit_exceeded", "history")
        if state.get("phase") == "finished" and (len(history) != total or any(not isinstance(r, dict) or not r.get("closed") for r in history)):
            error("premature_completion", "phase")
    if require_complete and state.get("phase") != "finished":
        error("run_not_finished", "phase")
    warnings.append({"code": "not_verified_semantic_novelty_role_identity_source_support_scope_or_actual_delegation", "path": "$"})
    return {"ok": not errors, "errors": errors, "warnings": warnings, "counts": counts}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = audit(json.loads(args.state.read_text(encoding="utf-8")),
                       json.loads(args.config.read_text(encoding="utf-8")) if args.config else None,
                       args.require_complete)
        print(json.dumps(result, indent=2))
        return 0 if result["ok"] else 1
    except (OSError, ValueError, TypeError) as exc:
        print(f"run audit error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
