#!/usr/bin/env python3
"""Stateless logbook viewer. Reads the LOGBOOK.md files listed in config.json on every request.

    python3 server.py [config.json]
    python3 server.py --parse LOGBOOK.md   # dump parsed entries as JSON (debug)
"""
import json, os, re, sys
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import unquote, urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
# "## 2026-09-20 — title" (also tolerates "-" / "–" and a stray "# " before the title)
HEAD = re.compile(r"^## (\d{4}-\d{2}-\d{2})\s*[—–-]+\s*(?:#\s*)?(.*)$")


def parse(name, path):
    """Split one logbook file into entries. Header text before the first entry is dropped."""
    try:
        lines = open(path, encoding="utf-8").read().splitlines()
    except OSError as e:
        return [{"id": f"{name}:err", "project": name, "date": "", "title": f"cannot read {path}: {e}", "body": ""}]
    entries, cur, fence = [], None, False
    for line in lines:
        if line.startswith("```"):
            fence = not fence
        m = None if fence else HEAD.match(line)
        if m:
            cur = {"id": f"{name}:{len(entries)}", "project": name, "date": m[1], "title": m[2].strip(), "lines": []}
            entries.append(cur)
        elif cur is not None:
            cur["lines"].append(line)
    for e in entries:
        e["body"] = re.sub(r"\n-{3,}\s*$", "", "\n".join(e.pop("lines")).strip())
    return entries


class Handler(SimpleHTTPRequestHandler):
    projects = {}  # name -> path, set in main()

    def do_GET(self):
        path = unquote(urlparse(self.path).path)
        if path == "/api/entries":
            mtimes = [os.path.getmtime(p) if os.path.exists(p) else 0 for p in self.projects.values()]
            body = json.dumps({
                "version": ",".join(f"{m:.0f}" for m in mtimes),
                "projects": list(self.projects),
                "entries": [e for n, p in self.projects.items() for e in parse(n, p)],
            }).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            return self.wfile.write(body)
        if path.startswith("/files/"):  # images referenced from an entry, relative to that logbook's directory
            name, _, rel = path[7:].partition("/")
            if name in self.projects:
                root = os.path.dirname(os.path.realpath(self.projects[name]))
                full = os.path.realpath(os.path.join(root, rel))
                if full.startswith(root + os.sep) and os.path.isfile(full):
                    self.send_response(200)
                    self.send_header("Content-Type", self.guess_type(full))
                    self.send_header("Content-Length", str(os.path.getsize(full)))
                    self.end_headers()
                    with open(full, "rb") as f:
                        return self.copyfile(f, self.wfile)
            return self.send_error(404)
        if path == "/":
            self.path = "/index.html"
        return super().do_GET()

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *a):  # quiet
        pass


def make_server(cfg_path=None):
    """Configure the handler from the config file and return a bound (not yet running) HTTPServer."""
    cfg = json.load(open(cfg_path or os.path.join(HERE, "config.json")))
    Handler.projects = {p["name"]: os.path.expanduser(p["path"]) for p in cfg["projects"]}
    return HTTPServer(("127.0.0.1", cfg.get("port", 8765)), partial(Handler, directory=HERE))


def main():
    if len(sys.argv) > 2 and sys.argv[1] == "--parse":
        return print(json.dumps(parse("x", sys.argv[2]), indent=1, ensure_ascii=False))
    srv = make_server(sys.argv[1] if len(sys.argv) > 1 else None)
    print(f"http://localhost:{srv.server_port}/  ({len(Handler.projects)} logbooks)")
    srv.serve_forever()


if __name__ == "__main__":
    main()
