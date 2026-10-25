"""Behavioral checks for complete, read-only, evidence-preserving exports."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from knowledge_map import (evidence_status, main, markdown_links, read_breadth, read_hops,
                           rebase_links, render_html, safe_url, state_to_graph, validate_graph)


def sample():
    return {"question": "Q?", "decomposition": {"concepts": [{"id": "S", "label": "S", "kind": "entity"}]},
            "history": [{"round": 1, "breadth": {"agent2": {"directions": [
                {"id": "d1", "question": "Selected?", "anchor_ids": ["S"]},
                {"id": "d2", "question": "Not selected?", "anchor_ids": ["S"], "finding": "Keep this finding", "evidence_refs": ["https://example.org/paper"]}]}},
                "selected": ["d1"], "depth": {"d1": {"hops": [
                    {"question": "h1?", "finding": "F", "status": "verified_direct", "relation": "observation", "evidence_refs": ["https://example.org/one"]},
                    {"question": "h2?", "finding": "Boundary", "status": "unresolved", "relation": "analogy", "evidence_refs": ["reference-id-not-a-url"]}],
                    "new_concepts": [{"id": "N", "label": "New concept"}],
                    "bridges": [{"source": "S", "target": "N", "kind": "analogy", "relation": "explicit analogy"}]}}}]}


class ExportTests(unittest.TestCase):
    def test_keeps_unselected_and_does_not_promote_evidence(self):
        graph = state_to_graph(sample())
        untouched = next(n for n in graph["nodes"] if "d2" in n["origin_ids"])
        self.assertEqual(untouched["summary"], "Keep this finding")
        self.assertEqual(untouched["status"], "frontier")
        self.assertEqual(untouched["evidence"], "unresolved")
        self.assertTrue(any(e["kind"] == "analogy" for e in graph["edges"]))
        self.assertEqual(graph["meta"]["counts"], {"directions": 2, "selected": 1, "hops": 2})
        validate_graph(graph)

    def test_evidence_status_and_missing_sources_stay_honest(self):
        self.assertEqual(evidence_status("verified_direct/inferred/unresolved"), "unresolved")
        graph = state_to_graph(sample())
        h2 = next(n for n in graph["nodes"] if n["label"] == "h2?")
        self.assertEqual(h2["status"], "blocked")
        self.assertIsNone(h2["links"][0]["url"])
        self.assertIn("reference-id-not-a-url", h2["links"][0]["note"])

    def test_no_input_mutation(self):
        data = sample(); before = copy.deepcopy(data)
        state_to_graph(data)
        self.assertEqual(data, before)

    def test_historical_rounds_and_markdown(self):
        data = {"question": "Q", "rounds": [{"round": 1, "anchors": [{"id": "F", "label": "Frontier anchor"}],
            "breadth": {"agent3_subject": {"direction_ids": ["R1-A3-1", "R1-A3-2"]}},
            "selection": {"selected_ids": ["R1-A3-1"]}, "depth": [{"direction_id": "R1-A3-1", "hops": 2}]}]}
        breadth = "| R1-A3-1 | First question? | Initial [paper](https://example.org/a) |\n| R1-A3-2 | Second question? | Retained knowledge |"
        depth = "## R1-A3-1 — The path\n1. **First.** Finding. [paper](https://example.org/a). **verified_direct**\n2. **Second.** Limits. Same source. **supported_with_limits/unresolved**"
        report = "| R1-A3-1 展示标题 | 摘要 | 限制 |"
        graph = state_to_graph(data, breadth, depth, {"运行状态": "state.json", "深度探索台账": "depth.md"}, report)
        self.assertEqual(graph["meta"]["counts"]["hops"], 2)
        self.assertEqual(next(n for n in graph["nodes"] if n["type"] == "direction")["label"], "展示标题")
        self.assertTrue(any(n["id"] == "concept:F" for n in graph["nodes"]))
        self.assertTrue(all(any(l["kind"] == "file" for l in n["links"]) for n in graph["nodes"]))
        self.assertEqual(next(n for n in graph["nodes"] if n["id"].endswith(":2"))["evidence"], "unresolved")

    def test_missing_hop_text_not_fabricated(self):
        data = {"question": "Q", "rounds": [{"round": 1, "breadth": {"agent2": {"direction_ids": ["R1-A2-1"]}},
            "selection": {"selected_ids": ["R1-A2-1"]}, "depth": [{"direction_id": "R1-A2-1", "hops": 3}]}]}
        graph = state_to_graph(data)
        self.assertFalse(any(n["type"] == "finding" for n in graph["nodes"]))
        self.assertTrue(graph["meta"]["warnings"])

    def test_hop_headings_and_breadth_sections(self):
        hops = read_hops("### Hop 1 — Read [verified_direct]\nA\n### Hop 2 — Question [inferred / unresolved]\nB")
        self.assertEqual(len(hops), 2)
        self.assertEqual(hops[1]["body"], "B")
        records = read_breadth("### R3-A2-1 — A question\n[Paper](https://example.org/a)\n# Round 3 selection record\nSCORE")
        self.assertNotIn("SCORE", records["R3-A2-1"]["body"])

    def test_links_allow_only_safe_protocols(self):
        for value in ["javascript:alert(1)", "data:text/html,x", "//example.org/x", "https://a/\nx", "\\\\host\\x"]:
            self.assertIsNone(safe_url(value))
        self.assertEqual(markdown_links("[Paper](https://example.org/paper)")[0]["url"], "https://example.org/paper")

    def test_dangling_and_cyclic_nodes_rejected(self):
        graph = state_to_graph(sample())
        graph["nodes"][0]["parent_id"] = graph["nodes"][1]["id"]
        with self.assertRaisesRegex(ValueError, "循环"):
            validate_graph(graph)
        graph = state_to_graph(sample()); graph["edges"][0]["target"] = "missing"
        with self.assertRaises(ValueError): validate_graph(graph)

    def test_export_is_offline_and_script_injection_safe(self):
        graph = state_to_graph(sample()); graph["nodes"][0]["label"] = '</script><script>alert("x")</script>'
        document = render_html(graph)
        self.assertNotIn('src="app.js"', document)
        self.assertNotIn('href="styles.css"', document)
        self.assertNotIn('</script><script>alert("x")', document)
        self.assertIn('\\u003c/script>', document)

    def test_rebases_local_files_without_touching_web_links(self):
        graph = state_to_graph(sample()); graph["nodes"][0]["links"] = [{"url": "notes/%E4%B8%AD.md#section"}]
        rebase_links(graph, Path('/project/run'), Path('/project/export'))
        self.assertEqual(graph["nodes"][0]["links"][0]["url"], "../run/notes/%E4%B8%AD.md#section")
        retained = next(n for n in graph["nodes"] if n["id"] == "direction:r1:d2")
        self.assertEqual(retained["links"][0]["url"], "https://example.org/paper")

    def test_cli_never_overwrites_input(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "map.graph.json"; original = json.dumps(sample()); path.write_text(original)
            self.assertEqual(main(["--input", str(path), "--output", str(path.with_name("map.html"))]), 2)
            self.assertEqual(path.read_text(), original)
            self.assertFalse(path.with_name("map.html").exists())

    def test_cli_complete_export_and_input_hash_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"; original = json.dumps(sample()); path.write_text(original)
            output = Path(directory) / "map.html"
            self.assertEqual(main(["--input", str(path), "--output", str(output)]), 0)
            self.assertEqual(path.read_text(), original)
            self.assertTrue(output.is_file())
            exported = json.loads(output.with_suffix('.graph.json').read_text())
            self.assertTrue(all(n["links"] for n in exported["nodes"]))


if __name__ == "__main__":
    unittest.main()
