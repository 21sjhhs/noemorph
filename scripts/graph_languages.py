"""Language variants are copies of one graph, with display text translated only."""
from __future__ import annotations

import copy
import hashlib
import json
import math
import re
import struct

LANGUAGE_TAG = re.compile(r"^[A-Za-z]{2,8}(?:-[A-Za-z0-9]{1,8})*$")
META_TEXT = {"title", "question", "description", "provenance"}
NODE_TEXT = {"label", "summary", "next_question", "evidence_note"}
PROTECTED_DETAIL_KEYS = {"id", "ids", "origin_ids", "anchor_ids", "typed_queries", "formal_logic",
                         "source", "target", "parent_id", "url", "direct_url", "doi", "href", "path", "evidence", "role", "type"}
LANGUAGE_META = {"language", "language_label", "translation"}


def language_tag(value):
    if not isinstance(value, str) or not LANGUAGE_TAG.fullmatch(value):
        raise ValueError("language 必须是 BCP 47 形式的语言标签，例如 zh-CN、en、ja 或 und")
    parts = value.split("-")
    return "-".join([parts[0].lower()] + [p.upper() if len(p) == 2 else p.title() if len(p) == 4 else p.lower() for p in parts[1:]])


def stripped(graph):
    result = copy.deepcopy(graph)
    result.pop("view", None)
    for key in LANGUAGE_META:
        result.get("meta", {}).pop(key, None)
    return result


def canonical(value):
    """Deterministic typed encoding: JSON containers, UTF-16 keys, IEEE-754 numbers."""
    if isinstance(value, dict):
        return "{" + ",".join(json.dumps(k, ensure_ascii=False) + ":" + canonical(value[k]) for k in sorted(value, key=lambda k: k.encode("utf-16-be"))) + "}"
    if isinstance(value, list):
        return "[" + ",".join(canonical(v) for v in value) + "]"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        number = float(value)
        if not math.isfinite(number) or isinstance(value, int) and int(number) != value:
            raise ValueError("图谱数值不能无损表示为浏览器数值；请把精确大整数记录为字符串")
        return 'n' + struct.pack('>d', number).hex()
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def fingerprint(graph):
    return hashlib.sha256(canonical(stripped(graph)).encode("utf-8")).hexdigest()


def is_display_text(path):
    if len(path) >= 2 and path[0] == "meta":
        return len(path) == 2 and path[1] in META_TEXT or len(path) == 3 and path[1] == "warnings"
    if len(path) >= 3 and path[0] == "nodes":
        if len(path) == 3 and path[2] in NODE_TEXT:
            return True
        if len(path) == 4 and path[2] == "tags":
            return True
        if len(path) == 5 and path[2] == "links" and path[4] in {"label", "note"}:
            return True
        if path[2] == "details":
            return not any(key in PROTECTED_DETAIL_KEYS for key in path[3:])
    if len(path) >= 3 and path[0] == "edges" and path[2] == "details":
        protected = (PROTECTED_DETAIL_KEYS - {"evidence"}) | {"status", "relation", "relation_type"}
        return not any(key in protected for key in path[3:])
    return len(path) == 3 and path[0] == "edges" and path[2] == "label"


def is_display_value(value, path):
    return (isinstance(value, str) and bool(value.strip()) and is_display_text(path)
            and not re.fullmatch(r"https?://\S+", value)
            and not (path[-1:] == ("evidence",) and value in {
                "verified_direct", "supported_with_limits", "inferred", "unresolved", "contradicted"}))


def locked_projection(graph):
    def walk(value, path=()):
        if is_display_value(value, path):
            return {"$display_text": True}
        if isinstance(value, dict):
            return {k: walk(v, path + (k,)) for k, v in value.items()}
        if isinstance(value, list):
            return [walk(v, path + (str(i),)) for i, v in enumerate(value)]
        return value
    return walk(stripped(graph))



def language_issues(graph):
    """Conservative script/sentence audit, not semantic language detection."""
    language = language_tag(graph.get("meta", {}).get("language", "und")).split("-")[0]
    issues = []
    def walk(value, path=()):
        if is_display_value(value, path):
            han = bool(re.search(r"[\u3400-\u9fff]", value))
            words = re.findall(r"[A-Za-z]+(?:['’-][A-Za-z]+)*", value)
            if language == "en" and han or language == "zh" and not han and len(words) >= 8:
                issues.append(".".join(path))
        elif isinstance(value, dict):
            for key, child in value.items(): walk(child, path + (key,))
        elif isinstance(value, list):
            for index, child in enumerate(value): walk(child, path + (str(index),))
    walk(graph)
    return issues


def require_complete_language(graph):
    issues = language_issues(graph)
    if issues:
        raise ValueError("图谱语言声明与展示文字不一致（" + graph["meta"]["language"] + "）：" + ", ".join(issues[:5]) + "；请完整翻译，混合原始记录请声明 und")


def missing_languages(requested, available):
    return [code for code in dict.fromkeys([*requested, "en"])
            if not any(code == actual or code == "en" and actual.startswith("en-") for actual in available)]

def validate_translation(source, translated, require_binding=True):
    target = language_tag(translated.get("meta", {}).get("language"))
    require_complete_language(translated)
    if target == "und":
        raise ValueError("翻译版本不能声明为未指定语言 und")
    if locked_projection(source) != locked_projection(translated):
        raise ValueError("语言版本改变了图结构、ID、URL、证据状态或其他非展示字段")
    info = translated.get("meta", {}).get("translation", {})
    if require_binding and info.get("source_fingerprint") != fingerprint(source):
        raise ValueError("语言版本的 source_fingerprint 与原图不匹配；请从当前原图重新翻译")
    if require_binding and (info.get("target_language") != target or not isinstance(info.get("translator"), str) or not info["translator"].strip()):
        raise ValueError("翻译记录需声明 target_language 和实际 translator 标识")
    return translated


def stamp_translation(source, translated, translator="unspecified"):
    """Call only on an actual translated artifact; never performs translation."""
    validate_translation(source, translated, require_binding=False)
    result = copy.deepcopy(translated)
    lang = language_tag(result["meta"]["language"])
    result["meta"]["language"] = lang
    result["meta"]["translation"] = {"source_fingerprint": fingerprint(source),
        "source_language": language_tag(source.get("meta", {}).get("language", "und")),
        "target_language": lang, "translator": translator}
    return result


def make_bundle(source, translations=(), default_language=None, require_binding=True):
    base = copy.deepcopy(source)
    base.setdefault("meta", {})["language"] = language_tag(base.get("meta", {}).get("language", "und"))
    graphs, languages = [base], {base["meta"]["language"]}
    for translated in translations:
        validate_translation(base, translated, require_binding=require_binding)
        lang = language_tag(translated["meta"]["language"])
        if lang in languages:
            raise ValueError(f"重复的图谱语言：{lang}")
        variant = copy.deepcopy(translated)
        variant["meta"]["language"] = lang
        graphs.append(variant)
        languages.add(lang)
    default = language_tag(default_language or base["meta"]["language"])
    if default not in languages:
        raise ValueError("default_language 没有对应的已生成图谱")
    return {"bundle_version": "1.0", "source_fingerprint": fingerprint(base),
            "default_language": default, "graphs": graphs}


def validate_bundle(bundle):
    if bundle.get("bundle_version") != "1.0" or not isinstance(bundle.get("graphs"), list) or not bundle["graphs"]:
        raise ValueError("需要 bundle_version=1.0 与非空 graphs 数组")
    checked = make_bundle(bundle["graphs"][0], bundle["graphs"][1:], bundle.get("default_language"))
    if bundle.get("source_fingerprint") != checked["source_fingerprint"]:
        raise ValueError("语言包的 source_fingerprint 与原图不匹配")
    return bundle


if __name__ == "__main__":
    import argparse
    from pathlib import Path
    parser = argparse.ArgumentParser(description="Bind and validate an actual translated graph. Does not translate text.")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--translation", type=Path, required=True)
    parser.add_argument("--translator", required=True, help="Actual delegated translation agent identity")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.resolve() == args.source.resolve():
        parser.error("翻译版本不得覆盖原图")
    try:
        result = stamp_translation(json.loads(args.source.read_text()), json.loads(args.translation.read_text()), args.translator)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"language": result["meta"]["language"], "source_fingerprint": result["meta"]["translation"]["source_fingerprint"], "output": str(args.output)}, ensure_ascii=False))
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
