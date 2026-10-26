#!/usr/bin/env python3
"""Portable settings cards for any local agent with file or shell access.

render: offline HTML + JSON download. serve: loopback card saves the user's
choices, exits, and returns the configuration to the calling agent. No research
or translation is started by this utility.
"""
from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import secrets
import sys
import tempfile
from urllib.parse import urlsplit

from graph_languages import language_tag

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "plugins/knowledge-map"
DEFAULTS = {"schema_version": "noemorph-run-config/1.0", "question": "", "scope": "", "macro_rounds": 3,
            "max_parallel_agents": None, "top_n": None, "depth_hops": 3,
            "presentation_languages": ["zh-CN", "en"], "ui_language": "zh-CN",
            "research_language_policy": "unconstrained", "logical_roles": 5, "breadth_per_role": 5}


def validate_config(value):
    if not isinstance(value, dict) or set(value) - set(DEFAULTS):
        raise ValueError("配置必须是对象，且只能包含已声明的运行参数")
    c = {**DEFAULTS, **value}
    if not isinstance(c["question"], str) or not c["question"].strip():
        raise ValueError("请填写研究问题。")
    c["question"] = c["question"].strip()
    if not isinstance(c["scope"], str):
        raise ValueError("scope must be text")
    c["scope"] = c["scope"].strip()
    def integer(name, low, high, nullable=False):
        v = c[name]
        if nullable and v is None:
            return
        if isinstance(v, bool) or not isinstance(v, int) or not low <= v <= high:
            raise ValueError(f"{name} 必须为 {low}–{high} 的整数" + ("或 null（自动）" if nullable else ""))
    integer("macro_rounds", 1, 1000)
    integer("max_parallel_agents", 1, 5, True)
    integer("top_n", 1, 20, True)
    integer("depth_hops", 3, 20)
    languages = c["presentation_languages"]
    if not isinstance(languages, list) or not languages:
        raise ValueError("请至少选择一种最终呈现语言。")
    c["presentation_languages"] = list(dict.fromkeys([*(language_tag(v) for v in languages), "en"]))
    if "und" in c["presentation_languages"]:
        raise ValueError("最终呈现语言不能是未标注的 und")
    if c["schema_version"] != DEFAULTS["schema_version"] or c["ui_language"] not in {"zh-CN", "en"} or c["research_language_policy"] != "unconstrained" or c["logical_roles"] != 5 or c["breadth_per_role"] != 5:
        raise ValueError("固定研究骨架或界面语言配置无效")
    return c


def render_card(config=None, endpoint=None, token=None):
    template = (ASSETS / "run-card.html").read_text(encoding="utf-8")
    boot = {"config": {**DEFAULTS, **(config or {})}}
    if endpoint:
        boot.update(endpoint=endpoint, token=token)
    data = json.dumps(boot, ensure_ascii=False, allow_nan=False).replace("<", "\\u003c")
    template = template.replace('<script id="run-card-data" type="application/json">{}</script>', '<script id="run-card-data" type="application/json">' + data + '</script>')
    template = template.replace('<link rel="stylesheet" href="styles.css">', '<style>' + (ASSETS / "styles.css").read_text() + '</style>')
    for name in ("i18n.js", "settings.js"):
        source = (ASSETS / name).read_text().replace("</script", "<\\/script")
        template = template.replace(f'<script src="{name}"></script>', '<script>' + source + '</script>')
    return template


def save_config(path, config):
    validated = validate_config(config)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=".noemorph-config-", suffix=".json", dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(validated, f, ensure_ascii=False, indent=2)
            f.write('\n')
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)
    return validated


def portable_prompt(question, ui_language="zh-CN"):
    return {"card_version": "noemorph-selection-card/1.0", "question": question, "ui_language": ui_language,
        "fields": [
            {"id": "scope", "label": "研究范围与排除项 / Scope and exclusions", "type": "string", "default": ""},
            {"id": "macro_rounds", "label": "思考轮数 / Research rounds", "type": "integer", "min": 1, "max": 1000, "suggestions": [1,3,5]},
            {"id": "max_parallel_agents", "label": "并行子代理上限 / Maximum parallel subagents", "type": "integer_or_null", "options": [None,1,2,3,4,5]},
            {"id": "top_n", "label": "每轮深入路径数 / Deep paths per round", "type": "integer_or_null", "min": 1, "max": 20, "default": None},
            {"id": "depth_hops", "label": "每条路径最少推进次数 / Minimum depth attempts", "type": "integer", "min": 3, "max": 20, "default": 3},
            {"id": "presentation_languages", "label": "最终内容呈现语言 / Final content languages", "type": "language_tag_array", "options": [["zh-CN","en"],["en"]], "required_languages": ["en"], "allow_custom": True}],
        "fixed": {"logical_roles": 5, "breadth_per_role": 5, "research_language_policy": "unconstrained"},
        "fallback": "Use the bundled HTML settings card or a numbered text card when native selection UI is unavailable. Wait for actual user choices."}


class CardHandler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def respond(self, status, body, content_type='application/json; charset=utf-8'):
        encoded = body.encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(encoded)))
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self):
        if self.headers.get('Host') != urlsplit(self.server.expected_origin).netloc:
            return self.respond(403, '{"error":"loopback host required"}')
        if urlsplit(self.path).path != '/':
            return self.respond(404, '{"error":"not found"}')
        self.respond(200, self.server.card_html, 'text/html; charset=utf-8')

    def do_POST(self):
        token = self.headers.get('X-Noemorph-Token')
        if self.headers.get('Host') != urlsplit(self.server.expected_origin).netloc or self.path != '/api/config' or self.headers.get('Origin') != self.server.expected_origin or token != self.server.card_token:
            return self.respond(403, '{"error":"same-origin card token required"}')
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 262144:
                raise ValueError('invalid payload size')
            config = validate_config(json.loads(self.rfile.read(length)))
            save_config(self.server.config_path, config)
            self.server.saved_config = config
            self.respond(200, '{"saved":true}')
            # Requests run in separate threads; shutdown safely releases the CLI.
            self.server.shutdown()
        except (ValueError, OSError) as exc:
            self.respond(400, json.dumps({'error': str(exc)}, ensure_ascii=False))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    for command in ('render', 'serve', 'prompt'):
        q = sub.add_parser(command)
        q.add_argument('--question', default='')
        q.add_argument('--ui-language', choices=['zh-CN','en'], default='zh-CN')
        if command == 'render':
            q.add_argument('--output', type=Path, required=True)
        if command == 'serve':
            q.add_argument('--directory', type=Path, required=True)
            q.add_argument('--port', type=int, default=0)
    q = sub.add_parser('validate')
    q.add_argument('--input', type=Path, required=True)
    q.add_argument('--output', type=Path)
    args = p.parse_args(argv)
    try:
        if args.command == 'validate':
            config = validate_config(json.loads(args.input.read_text(encoding='utf-8')))
            if args.output:
                save_config(args.output, config)
            print(json.dumps(config, ensure_ascii=False, indent=2))
        elif args.command == 'prompt':
            print(json.dumps(portable_prompt(args.question, args.ui_language), ensure_ascii=False, indent=2))
        elif args.command == 'render':
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(render_card({'question': args.question, 'ui_language': args.ui_language}), encoding='utf-8')
            print(args.output.resolve())
        else:
            directory = args.directory.resolve()
            config_path = directory / 'run-config.json'
            if config_path.exists():
                raise ValueError('run-config.json 已存在；为新研究使用独立目录')
            directory.mkdir(parents=True, exist_ok=True)
            server = ThreadingHTTPServer(('127.0.0.1', args.port), CardHandler)
            server.expected_origin = f'http://127.0.0.1:{server.server_port}'
            server.card_token = secrets.token_urlsafe(24)
            server.config_path = config_path
            server.saved_config = None
            server.card_html = render_card({'question': args.question, 'ui_language': args.ui_language}, '/api/config', server.card_token)
            card_file = directory / 'run-card.html'
            card_file.write_text(render_card({'question': args.question, 'ui_language': args.ui_language}), encoding='utf-8')
            print(json.dumps({'card_url': server.expected_origin + '/', 'config_path': str(config_path), 'offline_card': str(card_file)}, ensure_ascii=False), flush=True)
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                pass
            finally:
                server.server_close()
            if server.saved_config is None:
                return 130
            print(json.dumps({'saved': str(config_path), 'config': server.saved_config}, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError) as exc:
        print(f'run settings error: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
