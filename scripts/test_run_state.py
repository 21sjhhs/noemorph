#!/usr/bin/env python3
"""Structural tests using only abstract identifiers, with no research scenarios."""
import json
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

SCRIPT = Path(__file__).resolve().with_name("run_state.py")


def direction(i: int, anchor="C0"):
    return {
        "id": f"D{i}", "question": f"Q{i}?", "anchor_ids": [anchor],
        "logical_move": f"M{i}", "discovery_target": "Unknown category",
        "search_route": "Independent concept search", "bridge_test": "Compare defining properties",
        "novelty_reason": "Different target", "unknowns": [],
    }


def depth_record(round_id, direction_id):
    return {"round": round_id, "agent_id": "X1", "direction_id": direction_id,
            "hops": [{"question": f"Q{k}?", "finding": "Unresolved branch",
                      "relation": "Hypothetical extension", "evidence_refs": [],
                      "status": "unresolved"} for k in range(3)],
            "new_concepts": [{"id": f"F_{round_id}_{direction_id}", "label": "Unknown"}],
            "bridges": [], "boundary_change": "Candidate frontier extended",
            "limits": [], "unresolved": ["Needs verification"]}


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.state = self.root / "state.json"
        self.counter = 0

    def call(self, *args, success=True):
        result = subprocess.run([sys.executable, str(SCRIPT), *map(str, args)],
                                capture_output=True, text=True)
        if success and result.returncode:
            self.fail(result.stderr)
        if not success:
            self.assertNotEqual(result.returncode, 0)
        return result

    def save(self, data):
        self.counter += 1
        path = self.root / f"input_{self.counter}.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def initialize(self, rounds=1, agents=2, top_n=2):
        self.call("init", "--state", self.state, "--question", "Q?", "--rounds", rounds,
                  "--agents", agents, "--top-n", top_n)
        x = {"concepts": [{"id":"C0","label":"X","kind":"entity"},
                          {"id":"C1","label":"Y","kind":"property"}],
             "relations": [], "open_questions": []}
        self.call("decomp", "--state", self.state, "--input", self.save(x))

    def test_full_one_round(self):
        self.initialize()
        self.call("breadth", "--state", self.state, "--input", self.save({
            "round": 1, "agent_id": "A1", "directions": [direction(i) for i in range(5)]}))
        self.call("breadth", "--state", self.state, "--input", self.save({
            "round": 1, "agent_id": "A2", "directions": [direction(i) for i in range(5,10)]}))
        self.call("select", "--state", self.state, "--ids", "D0,D5")
        for ident in ("D0", "D5"):
            self.call("depth", "--state", self.state, "--input", self.save(depth_record(1, ident)))
        result = self.call("close", "--state", self.state)
        self.assertEqual(json.loads(result.stdout)["phase"], "finished")
        self.assertEqual(json.loads(result.stdout)["frontier_concepts"], 2)

    def test_reject_early_selection(self):
        self.initialize()
        self.call("select", "--state", self.state, "--ids", "D0,D1", success=False)

    def test_exact_five_directions(self):
        self.initialize()
        self.call("breadth", "--state", self.state, "--input", self.save({
            "round": 1, "agent_id": "A1", "directions": [direction(i) for i in range(4)]}), success=False)

    def test_no_reused_state(self):
        self.initialize()
        self.call("init", "--state", self.state, "--question", "Q?", "--rounds", 1,
                  "--agents", 2, success=False)

    def test_reject_depth_without_selection(self):
        self.initialize()
        self.call("depth", "--state", self.state, "--input", self.save(depth_record(1, "D0")), success=False)

    def test_round_transition(self):
        self.initialize(rounds=2, agents=1, top_n=1)
        self.call("breadth", "--state", self.state, "--input", self.save({
            "round":1, "agent_id":"A1", "directions":[direction(i) for i in range(5)]}))
        self.call("select", "--state", self.state, "--ids", "D0")
        self.call("depth", "--state", self.state, "--input", self.save(depth_record(1,"D0")))
        output = self.call("close", "--state", self.state)
        data = json.loads(output.stdout)
        self.assertEqual(data["phase"], "breadth")
        self.assertEqual(data["current_round"], 2)
        self.assertEqual(data["closed_rounds"], 1)


if __name__ == "__main__":
    unittest.main()
