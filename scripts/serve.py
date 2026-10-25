#!/usr/bin/env python3
"""Serve an explicitly chosen local directory on loopback. No dependencies."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class LocalHandler(SimpleHTTPRequestHandler):
    extensions_map = {**SimpleHTTPRequestHandler.extensions_map, ".md": "text/plain; charset=utf-8", ".json": "application/json; charset=utf-8", ".js": "text/javascript; charset=utf-8"}

    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        super().end_headers()

    def send_head(self):
        # Do not let symlinks expose files outside the selected directory.
        target = Path(self.translate_path(self.path)).resolve()
        if not target.is_relative_to(Path(self.directory).resolve()):
            self.send_error(403, "Outside the selected directory")
            return None
        return super().send_head()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--directory", type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument("--port", type=int, default=8765)
    args = p.parse_args()
    directory = args.directory.resolve()
    if not directory.is_dir():
        p.error("--directory must exist")
    try:
        server = ThreadingHTTPServer(("127.0.0.1", args.port), partial(LocalHandler, directory=str(directory)))
    except OSError as exc:
        p.error(f"无法监听端口 {args.port}：{exc}。可使用 --port 指定其他端口。")
    print(f"Noemorph: http://127.0.0.1:{server.server_port}/plugins/knowledge-map/", flush=True)
    print(f"Serving only: {directory} · Ctrl+C to stop", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
