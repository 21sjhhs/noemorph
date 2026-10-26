#!/usr/bin/env python3
"""Read-only adapters and offline HTML export for the Noemorph knowledge map.

No models, searches, scientific inference, or writes to the input run occur here.
Python standard library only. See references/09-visualization.md.
"""
from __future__ import annotations

import argparse
import copy
import json
import math
import os
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit, unquote, quote
from graph_languages import (language_tag, make_bundle, validate_bundle, validate_translation,
                             stamp_translation, require_complete_language, missing_languages)

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "knowledge-map"
ROLES = {"anchor", "predicate", "subject", "predicate_abstraction", "subject_abstraction"}
STATUSES = {"discovered", "explored", "frontier", "blocked", "contradicted"}
EVIDENCE = {"verified_direct", "supported_with_limits", "inferred", "unresolved", "contradicted"}
LINK = re.compile(r"\[([^\]]+)\]\(([^\s)]+)\)")
DIRECTION_ID = r"R\d+-A[2-5]-\d+"


def plain(value):
    if value is None:
        return ""
    if not isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    value = LINK.sub(lambda m: m[1], value)
    return re.sub(r"[*`#]", "", value).strip()


def evidence_status(value):
    """Mixed/unknown assessments stay conservative; the original text is retained."""
    tokens = set(re.findall(r"[a-z_]+", str(value).lower()))
    for status in ("contradicted", "unresolved", "inferred", "supported_with_limits", "verified_direct"):
        if status in tokens:
            return status
    return "unresolved"


def safe_url(value):
    if not isinstance(value, str) or not value.strip():
        return None
    value = value.strip()
    if re.search(r"[\x00-\x20\x7f\\]", value) or value.startswith("//"):
        return None
    parsed = urlsplit(value)
    if parsed.scheme and parsed.scheme.lower() not in {"http", "https", "file"}:
        return None
    if parsed.scheme in {"http", "https"} and not parsed.netloc:
        return None
    return value


def source_links(refs):
    links = []
    for ref in refs or []:
        if isinstance(ref, dict):
            url = ref.get("url") or ref.get("href") or ref.get("path")
            label = ref.get("label") or ref.get("title") or "参考资料"
        else:
            url, label = str(ref), "参考资料"
            if re.match(r"^(?:doi:)?10\.\d{4,9}/", url, re.I):
                url = "https://doi.org/" + re.sub(r"^doi:", "", url, flags=re.I)
        # Bare bibliographic IDs are not invented into working hyperlinks.
        valid = safe_url(url)
        if valid and not urlsplit(valid).scheme and not re.search(r"[/#]|\.(?:md|pdf|html?|txt|json)(?:$|#)", valid):
            valid = None
        entry = {"label": plain(label), "url": valid, "kind": "source"}
        if not valid:
            entry["note"] = f"来源标识尚未解析：{url}"
        if entry not in links:
            links.append(entry)
    return links


def markdown_links(text):
    return source_links([{"label": label, "url": url} for label, url in LINK.findall(text)])


def role_of(agent, ident=""):
    text = f"{agent} {ident}".lower()
    match = re.search(r"(?:agent|a)[_-]?([2-5])", text)
    if match:
        return {"2": "predicate", "3": "subject", "4": "predicate_abstraction", "5": "subject_abstraction"}[match[1]]
    if "predicate" in text:
        return "predicate_abstraction" if "abstract" in text else "predicate"
    if "subject" in text:
        return "subject_abstraction" if "abstract" in text else "subject"
    return "anchor"


def node(ident, label, **extra):
    return {"id": ident, "label": plain(label) or ident, "summary": "", "type": "concept",
            "role": "anchor", "status": "discovered", "evidence": "unresolved",
            "importance": 2, "depth": 0, "round": 0, "parent_id": None,
            "origin_ids": [], "links": [], **extra}


def edge(source, target, **extra):
    return {"id": f"{source}→{target}", "source": source, "target": target,
            "label": "探索路径", "kind": "path", **extra}


def ledger_sections(text):
    matches = list(re.finditer(rf"^#{{2,3}}\s+({DIRECTION_ID})\s*[—–-]\s*(.*)$", text, re.M))
    result = {}
    for i, match in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        # A new round/selection section must not leak into this direction.
        block = text[match.end():end]
        stop = re.search(r"^#\s|^##\s+(?!R\d+-A)", block, re.M)
        if stop:
            block = block[:stop.start()]
        result[match[1]] = {"label": plain(match[2]), "body": block.strip()}
    return result


def read_breadth(text):
    result = ledger_sections(text)
    for line in text.splitlines():
        cols = re.split(r"(?<!\\)\|", line.strip().strip("|"))
        if len(cols) >= 3 and re.fullmatch(DIRECTION_ID, cols[0].strip()):
            ident = cols[0].strip()
            # First full direction table wins over later score-only tables.
            result.setdefault(ident, {"label": plain(cols[1]), "body": " | ".join(cols[2:]).strip()})
    return result


def read_hops(body):
    headings = list(re.finditer(r"^###\s+Hop\s+(\d+)\s*[—–-]\s*(.*)$", body, re.M | re.I))
    if headings:
        return [{"label": plain(m[2].split("[")[0]),
                 "body": body[m.end():headings[i + 1].start() if i + 1 < len(headings) else len(body)].strip(),
                 "assessment": m[2]}
                for i, m in enumerate(headings)]
    numbered = list(re.finditer(r"^(\d+)\.\s+", body, re.M))
    hops = []
    for i, m in enumerate(numbered):
        content = body[m.end():numbered[i + 1].start() if i + 1 < len(numbered) else len(body)].strip()
        content = re.split(r"\n\*\*(?:Bridge|Open|New concepts)", content)[0].strip()
        title = re.match(r"\*\*([^*]+)\*\*", content)
        hops.append({"label": plain(title[1]) if title else f"知识推进 {m[1]}", "body": content,
                     "assessment": content})
    return hops


def state_to_graph(state, breadth_text="", depth_text="", file_urls=None, report_text=""):
    """Supports run_state v4 and the historical rounds/direction_ids ledger format."""
    file_urls = file_urls or {}
    rounds = state.get("history", state.get("rounds"))
    if not isinstance(rounds, list) or not isinstance(state.get("question"), str):
        raise ValueError("不是受支持的 Noemorph 运行状态；需要 question 与 history / rounds 数组")
    nodes = [node("question", state["question"], type="question", importance=5,
                  summary="研究起点。图谱呈现已有记录；线条表示记录中的探索路径，不自动代表因果或等价。",
                  details=state.get("decomposition") or {},
                  links=[{"label": k, "url": v, "kind": "file"} for k, v in file_urls.items()])]
    edges, warnings = [], []
    concepts = (state.get("decomposition") or {}).get("concepts", [])[:]
    decomp = state.get("decomposition") or {}
    if not concepts:
        for key in ("whole_concept", "subject_candidates", "predicate_candidates", "relation_candidates", "conditions"):
            value = decomp.get(key, [])
            concepts.extend([value] if isinstance(value, dict) else value if isinstance(value, list) else [])
    known = {}
    for c in concepts:
        if not isinstance(c, dict) or not c.get("id"):
            continue
        ident = "concept:" + c["id"]
        known[c["id"]] = ident
        nodes.append(node(ident, c.get("label", c["id"]), parent_id="question", depth=1,
                          summary=c.get("kind", "原始概念拆解"), origin_ids=[c["id"]]))
        edges.append(edge("question", ident, label="概念拆解"))
    breadth = read_breadth(breadth_text)
    depths = ledger_sections(depth_text)
    report_labels = {}
    for line in report_text.splitlines():
        match = re.match(rf"^\|\s*({DIRECTION_ID})\s+([^|]+)\|", line)
        if match:
            report_labels[match[1]] = plain(match[2])
    counts = {"directions": 0, "selected": 0, "hops": 0}
    for r in rounds:
        rn = r.get("round", 1)
        for anchor in r.get("anchors", []):
            if not isinstance(anchor, dict) or not anchor.get("id") or anchor["id"] in known:
                continue
            cid = "concept:" + anchor["id"]
            known[anchor["id"]] = cid
            nodes.append(node(cid, anchor.get("label", anchor["id"]), parent_id="question", depth=1,
                              round=rn, importance=3, summary=plain(anchor.get("status", "本轮共享锚点")),
                              origin_ids=[anchor["id"]], details={"anchor_record": anchor}))
            edges.append(edge("question", cid, label=f"第 {rn} 轮锚点"))
        selected = r.get("selected", r.get("selection", {}).get("selected_ids", []))
        depth_rows = r.get("depth", {})
        depth_rows = {d["direction_id"]: d for d in depth_rows} if isinstance(depth_rows, list) else depth_rows
        for aid, submission in r.get("breadth", {}).items():
            directions = submission.get("directions", [{"id": v} for v in submission.get("direction_ids", [])])
            role = role_of(aid)
            for d in directions:
                did = d["id"]
                ident = f"direction:r{rn}:{did}"
                counts["directions"] += 1
                counts["selected"] += int(did in selected)
                record = breadth.get(did, {})
                detail = depth_rows.get(did, {})
                section = depths.get(did, {})
                content = record.get("body") or d.get("finding") or d.get("discovery_target", "")
                label = report_labels.get(did) or section.get("label") or d.get("label") or d.get("question") or record.get("label") or did
                references = markdown_links(content) + source_links(d.get("evidence_refs", []))
                if "广度探索台账" in file_urls:
                    references.append({"label": "原始方向与筛选记录", "url": file_urls["广度探索台账"], "kind": "file"})
                assessment = d.get("status", "unresolved")
                status = "explored" if detail else "frontier"
                parent = next((known[a] for a in d.get("anchor_ids", []) if a in known), "question")
                nodes.append(node(ident, label, type="direction", role=role, parent_id=parent, depth=1,
                                  importance=4 if did in selected else 2, status=status,
                                  evidence=evidence_status(assessment), evidence_note=str(assessment), round=rn,
                                  summary=plain(content) or "状态仅保留方向 ID；需查看原始探索文件。",
                                  origin_ids=[did], links=references,
                                  next_question=plain(d.get("unknowns", "")), selected=did in selected,
                                  details={"original_question": d.get("question") or record.get("label", ""),
                                           **{k: d[k] for k in ("logical_move", "bridge_test", "novelty_reason", "unknowns") if k in d}}))
                edges.append(edge(parent, ident, label="广度方向"))
                if not record and not d.get("question"):
                    warnings.append(f"{did} 只有 ID，未提供方向正文")
                hops = detail.get("hops", [])
                parsed = read_hops(section.get("body", ""))
                if isinstance(hops, int):
                    if parsed and len(parsed) != hops:
                        warnings.append(f"{did} 状态记录 {hops} 跳，台账解析 {len(parsed)} 跳；保留全部可读内容")
                    hops = [{"question": item["label"], "finding": plain(item["body"]),
                             "status": evidence_status(item["assessment"]),
                             "evidence_note": item["assessment"], "evidence_refs": markdown_links(item["body"])}
                            for item in parsed]
                    if not parsed:
                        warnings.append(f"{did} 仅有深度计数，没有逐跳正文；未虚构知识节点")
                previous = ident
                for i, h in enumerate(hops):
                    hid = f"hop:r{rn}:{did}:{i + 1}"
                    counts["hops"] += 1
                    ev = evidence_status(h.get("status"))
                    body = parsed[i]["body"] if i < len(parsed) else ""
                    refs = source_links(h.get("evidence_refs", []))
                    # "Same source" is kept explicit, not silently invented as an independent citation.
                    if body and not refs and re.search(r"same source", body, re.I):
                        refs = [{"label": "沿用上一跳来源", "url": None, "note": "原文写作 Same source；请打开深度台账核对具体文献。", "kind": "source"}]
                    if "深度探索台账" in file_urls:
                        refs.append({"label": "深度路径原始记录", "url": file_urls["深度探索台账"], "kind": "file"})
                    nodes.append(node(hid, h.get("label") or h.get("question") or f"知识推进 {i + 1}",
                                      summary=plain(h.get("finding", "")), type="finding", role=role,
                                      parent_id=previous, depth=i + 2, round=rn, importance=3,
                                      status="contradicted" if ev == "contradicted" else "blocked" if ev == "unresolved" else "explored",
                                      evidence=ev, evidence_note=h.get("evidence_note", str(h.get("status", ""))),
                                      origin_ids=[did], links=refs))
                    edges.append(edge(previous, hid, label=plain(h.get("relation")) or "逐级推进"))
                    previous = hid
                # New concepts and explicitly recorded cross-branch bridges are retained.
                for c in detail.get("new_concepts", []):
                    if not isinstance(c, dict) or not c.get("id"):
                        warnings.append(f"{did} 的 new_concepts 存在无结构条目；请查看原始状态")
                        continue
                    cid = "concept:" + c["id"]
                    if c["id"] not in known:
                        known[c["id"]] = cid
                        nodes.append(node(cid, c.get("label", c["id"]), parent_id=ident,
                                          summary=plain(c.get("finding", c.get("kind", ""))), role=role,
                                          depth=2, round=rn, evidence=evidence_status(c.get("status")),
                                          links=source_links(c.get("evidence_refs", [])), origin_ids=[c["id"], did]))
                        edges.append(edge(ident, cid, label="记录中的新概念"))
    # Only explicit structured bridges become graph edges. No semantic guessing.
    all_ids = {n["id"] for n in nodes}
    for r in rounds:
        ds = r.get("depth", {})
        ds = ds.values() if isinstance(ds, dict) else ds
        for d in ds:
            for b in d.get("bridges", []):
                if isinstance(b, dict):
                    s, t = b.get("source"), b.get("target")
                    s, t = known.get(s, s), known.get(t, t)
                    if s in all_ids and t in all_ids:
                        edges.append(edge(s, t, id=f"bridge:{len(edges)}", kind=b.get("kind", "related"), label=plain(b.get("relation", "记录中的联系"))))
                    else:
                        warnings.append("有一条结构化桥接的端点无法解析，未绘制；请查看原始状态")
                else:
                    warnings.append("有一条非结构化桥接未转为连线；请查看原始状态")
    if file_urls.get("运行状态"):
        for n in nodes:
            if not any(link.get("kind") == "file" for link in n["links"]):
                n["links"].append({"label": "原始运行记录", "url": file_urls["运行状态"], "kind": "file"})
    return {"schema_version": "1.0", "meta": {"title": "Noemorph · 知识探索地图",
            "question": state["question"], "description": "从已有研究记录生成 · 重要性与证据强度分别呈现",
            "rounds": len(rounds), "demo": False, "counts": counts, "warnings": list(dict.fromkeys(warnings)),
            "provenance": "Imported research records; citations and claims have not been re-verified by the viewer."},
            "nodes": nodes, "edges": edges}


def validate_graph(graph):
    if not isinstance(graph, dict) or graph.get("schema_version") != "1.0":
        raise ValueError("graph.schema_version 必须为 1.0")
    if not isinstance(graph.get("meta"), dict):
        raise ValueError("graph.meta 必须是对象")
    warnings = graph["meta"].get("warnings", [])
    if not isinstance(warnings, list) or not all(isinstance(w, str) for w in warnings):
        raise ValueError("meta.warnings 必须是文字数组")
    nodes, edges = graph.get("nodes"), graph.get("edges")
    if not isinstance(nodes, list) or not nodes or not isinstance(edges, list):
        raise ValueError("需要非空 nodes 数组与 edges 数组")
    ids = set()
    for n in nodes:
        if not isinstance(n, dict) or not isinstance(n.get("id"), str) or not n["id"].strip() or n["id"] in ids:
            raise ValueError("节点 ID 为空或重复")
        ids.add(n["id"])
        if not isinstance(n.get("label"), str) or not n["label"].strip():
            raise ValueError(f"{n['id']}: label 不能为空")
        if n.get("role", "anchor") not in ROLES or n.get("status", "discovered") not in STATUSES or n.get("evidence", "unresolved") not in EVIDENCE:
            raise ValueError(f"{n['id']}: 未知角色、探索状态或证据等级")
        importance = n.get("importance", 2)
        if isinstance(importance, bool) or not isinstance(importance, (int, float)) or not math.isfinite(importance) or not 1 <= importance <= 5:
            raise ValueError(f"{n['id']}: importance 必须在 1–5 之间")
        if not isinstance(n.get("links", []), list):
            raise ValueError(f"{n['id']}: links 必须是数组")
        for field in ("origin_ids", "tags"):
            value = n.get(field, [])
            if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
                raise ValueError(f"{n['id']}: {field} 必须是文字数组")
        if n.get("parent_id") is not None and (not isinstance(n["parent_id"], str) or not n["parent_id"].strip()):
            raise ValueError(f"{n['id']}: parent_id 必须是非空 ID 或 null")
        for link in n.get("links", []):
            if not isinstance(link, dict) or (link.get("url") is not None and not safe_url(link["url"])):
                raise ValueError(f"{n['id']}: 不安全或无效的链接")
    parents = {n["id"]: n.get("parent_id") for n in nodes}
    for ident, parent in parents.items():
        seen = {ident}
        while parent:
            if parent not in ids:
                raise ValueError(f"{ident}: 父节点不存在")
            if parent in seen:
                raise ValueError(f"{ident}: parent_id 存在循环")
            seen.add(parent)
            parent = parents[parent]
    eids = set()
    for e in edges:
        if not isinstance(e, dict) or e.get("source") not in ids or e.get("target") not in ids:
            raise ValueError("存在端点缺失的连线")
        if not isinstance(e.get("id"), str) or not e["id"].strip() or e["id"] in eids:
            raise ValueError("连线 ID 为空或重复")
        eids.add(e["id"])
    return graph


def rebase_links(graph, source_dir, output_dir):
    for n in graph["nodes"]:
        for link in n.get("links", []):
            url = link.get("url")
            if not url or urlsplit(url).scheme or url.startswith("#"):
                continue
            parts = urlsplit(url)
            path = (source_dir / unquote(parts.path)).resolve()
            relative = os.path.relpath(path, output_dir)
            link["url"] = quote(relative, safe="/.") + ("?" + parts.query if parts.query else "") + ("#" + parts.fragment if parts.fragment else "")


def render_html(graph):
    if graph.get("bundle_version"):
        validate_bundle(graph)
        for variant in graph["graphs"]:
            validate_graph(variant)
    else:
        validate_graph(graph)
    template = (PLUGIN / "index.html").read_text(encoding="utf-8")
    data = json.dumps(graph, ensure_ascii=False, separators=(",", ":"), allow_nan=False).replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    template = template.replace('<link rel="stylesheet" href="styles.css">', "<style>" + (PLUGIN / "styles.css").read_text() + "</style>")
    template = template.replace('<script src="demo.js"></script>', "")
    template = template.replace('<script id="graph-data" type="application/json">null</script>', '<script id="graph-data" type="application/json">' + data + '</script>')
    for name in ("graph-core.js", "languages.js", "i18n.js", "settings.js", "app.js"):
        source = (PLUGIN / name).read_text().replace("</script", "<\\/script")
        template = template.replace(f'<script src="{name}"></script>', "<script>" + source + "</script>")
    return template


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="研究状态 JSON 或标准 graph JSON")
    parser.add_argument("--output", required=True, type=Path, help="独立 HTML；与 .graph.json 同目录输出")
    parser.add_argument("--breadth-ledger", type=Path)
    parser.add_argument("--depth-ledger", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--annotations", type=Path, help="仅补充 label / importance / links / role / next_question")
    parser.add_argument("--translation", action="append", type=Path, default=[], help="已由翻译子 Agent 生成并绑定原图的语言版本，可重复")
    parser.add_argument("--language", help="原图的语言声明；混合或未知语言使用 und")
    parser.add_argument("--default-language", help="默认图谱内容语言（必须已经存在）")
    parser.add_argument("--config", type=Path, help="选择卡保存的 run-config.json；只读取呈现偏好")
    parser.add_argument("--allow-incomplete-languages", action="store_true", help="仅预览原始记录；允许缺失英文或其他请求版本，不代表最终交付")
    parser.add_argument("--json-output", type=Path, help="单独指定图谱 JSON 输出，避免覆盖原图")
    args = parser.parse_args(argv)
    try:
        json_path = args.json_output or args.output.with_suffix(".graph.json")
        if json_path.suffix != ".json" or json_path.resolve() == args.output.resolve() or json_path.resolve().parent != args.output.resolve().parent:
            raise ValueError("JSON 输出须与 HTML 在同一目录，并使用独立的 .json 文件名")
        inputs = [p.resolve() for p in (args.input, args.report, args.breadth_ledger, args.depth_ledger, args.annotations, args.config, *args.translation) if p]
        if args.output.resolve() in inputs or json_path.resolve() in inputs:
            raise ValueError("输出不得覆盖输入文件")
        if args.output.suffix.lower() != ".html":
            raise ValueError("--output 必须以 .html 结尾")
        original = json.loads(args.input.read_text(encoding="utf-8"))
        files = {}
        for label, path in (("综合研究报告", args.report), ("广度探索台账", args.breadth_ledger), ("深度探索台账", args.depth_ledger), ("运行状态", args.input)):
            if path:
                if not path.is_file():
                    raise ValueError(f"文件不存在：{path}")
                files[label] = quote(os.path.relpath(path.resolve(), args.input.resolve().parent), safe="/.")
        initial_bundle = None
        if original.get("bundle_version"):
            validate_bundle(original)
            initial_bundle = original
            graph = copy.deepcopy(original["graphs"][0])
        elif "nodes" in original:
            graph = copy.deepcopy(original)
        else:
            graph = state_to_graph(original,
                args.breadth_ledger.read_text() if args.breadth_ledger else "",
                args.depth_ledger.read_text() if args.depth_ledger else "", files,
                args.report.read_text() if args.report else "")
        if args.annotations:
            annotations = json.loads(args.annotations.read_text())
            known = {n["id"]: n for n in graph["nodes"]}
            for ident, patch in annotations.get("nodes", {}).items():
                if ident not in known:
                    raise ValueError(f"标注节点不存在：{ident}")
                if set(patch) - {"label", "importance", "links", "role", "next_question"}:
                    raise ValueError("标注只允许改变展示字段，不能改变研究状态或证据等级")
                known[ident].update(patch)
        graph["meta"]["language"] = language_tag(args.language or graph["meta"].get("language", "und"))
        translations = copy.deepcopy(initial_bundle["graphs"][1:]) if initial_bundle else []
        translations.extend(json.loads(path.read_text(encoding="utf-8")) for path in args.translation)
        for translated in translations:
            validate_graph(translated)
            validate_translation(graph, translated)
        config = None
        config_value = json.loads(args.config.read_text(encoding="utf-8")) if args.config else original.get("run_config")
        if config_value is not None:
            from run_card import validate_config
            config = validate_config(config_value)
        require_complete_language(graph)
        available = {graph["meta"]["language"]} | {v["meta"]["language"] for v in translations}
        missing = missing_languages(config["presentation_languages"] if config else [], available)
        if missing and not args.allow_incomplete_languages:
            raise ValueError("请求的内容语言版本尚未生成：" + ", ".join(missing) + "；英文为必备交付。仅预览可使用 --allow-incomplete-languages")
        for variant in [graph, *translations]:
            rebase_links(variant, args.input.resolve().parent, args.output.resolve().parent)
        translations = [stamp_translation(graph, v, v["meta"]["translation"]["translator"]) for v in translations]
        validate_graph(graph)
        payload = graph
        if translations or initial_bundle:
            default_language = args.default_language or (config["presentation_languages"][0] if config else None) or (initial_bundle["default_language"] if initial_bundle else None)
            payload = make_bundle(graph, translations, default_language)
            if initial_bundle and initial_bundle.get("view"):
                payload["view"] = initial_bundle["view"]
            elif graph.get("view"):
                payload["view"] = copy.deepcopy(graph["view"])
            if config:
                payload["run_config"] = config
                payload.setdefault("view", {})["ui_language"] = config["ui_language"]
        elif args.default_language and language_tag(args.default_language) != graph["meta"]["language"]:
            raise ValueError("默认语言没有对应的已生成图谱")
        if config:
            payload["run_config"] = config
            payload.setdefault("view", {})["ui_language"] = config["ui_language"]
        rendered = render_html(payload)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        print(json.dumps({"html": str(args.output.resolve()), "json": str(json_path.resolve()),
                          "nodes": len(graph["nodes"]), "edges": len(graph["edges"]),
                          "languages": [v["meta"]["language"] for v in [graph, *translations]],
                          "warnings": graph["meta"].get("warnings", [])}, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"knowledge map error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
