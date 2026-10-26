#!/usr/bin/env python3
"""Build the visualization-only demo bundle; never used as research input."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from knowledge_map import rebase_links, validate_graph, render_html
from graph_languages import make_bundle, stamp_translation
from run_card import render_card

root = Path(__file__).resolve().parents[1]
graph = json.loads((root / "examples/demo.graph.json").read_text())
graph["meta"]["language"] = "zh-CN"
graph["meta"]["language_label"] = "简体中文"
validate_graph(graph)
translated = json.loads((root / "examples/demo.en.graph.json").read_text())
translated = stamp_translation(graph, translated, "independent-translation-agent (demo)")
(root / "examples/demo.en.graph.json").write_text(json.dumps(translated, ensure_ascii=False, indent=2) + '\n', encoding="utf-8")
bundle = make_bundle(graph, [translated], 'zh-CN')
(root / "examples/knowledge-map.html").write_text(render_html(bundle), encoding="utf-8")
for variant in (graph, translated):
    rebase_links(variant, root / "examples", root / "plugins/knowledge-map")
translated = stamp_translation(graph, translated, translated["meta"]["translation"]["translator"])
bundle = make_bundle(graph, [translated], 'zh-CN')
data = json.dumps(bundle, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
(root / "plugins/knowledge-map/demo.js").write_text("/* UI demonstration only; never research context. */\nwindow.NOEMORPH_DEMO = " + data + ";\n")
(root / "examples/run-card.html").write_text(render_card(), encoding="utf-8")
print("Built offline demo bundle, examples/knowledge-map.html and examples/run-card.html.")
