"""Smallest check that fails if the entry parser breaks: python3 test_parse.py"""
import os, tempfile
from server import parse

SAMPLE = """# Development logbook
intro text

---

## 2026-09-20 — First title

**Context:** a

```bash
## not a heading, inside a fence
echo hi
```

---

## 2026-09-20 — # entry 2: second
body two
---
"""
with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
    f.write(SAMPLE)
try:
    e = parse("p", f.name)
finally:
    os.unlink(f.name)
assert [x["title"] for x in e] == ["First title", "entry 2: second"], e
assert e[0]["date"] == "2026-09-20" and e[0]["id"] == "p:0" and e[1]["id"] == "p:1"
assert "echo hi" in e[0]["body"] and "not a heading" in e[0]["body"]
assert e[1]["body"] == "body two", repr(e[1]["body"])
assert not e[0]["body"].endswith("---")
assert parse("p", "/nonexistent")[0]["title"].startswith("cannot read")

# append through the handler's logic, then parse it back
import io, json as _json
from server import Handler
class Fake(Handler):
    def __init__(self, path, payload):
        self.projects = {"p": path}; self.path = "/api/entries"
        raw = _json.dumps(payload).encode(); self.headers = {"Content-Length": str(len(raw))}
        self.rfile = io.BytesIO(raw); self.wfile = io.BytesIO(); self.sent = []
    def send_response(self, code, *a): self.sent.append(code)
    def send_error(self, code, *a): self.sent.append(code)
    def send_header(self, *a): pass
    def end_headers(self): pass
with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
    f.write(SAMPLE)
try:
    h = Fake(f.name, {"project": "p", "date": "2026-09-24", "title": "Added by hand", "body": "**Context:** test\n"}); h.do_POST()
    assert h.sent == [204], h.sent
    e = parse("p", f.name)
    assert [x["title"] for x in e][-1] == "Added by hand" and e[-1]["body"] == "**Context:** test" and e[-1]["date"] == "2026-09-24", e[-1]
    assert e[1]["body"] == "body two", repr(e[1]["body"])  # previous entry untouched
    h = Fake(f.name, {"project": "p", "date": "bad", "title": "x"}); h.do_POST(); assert h.sent == [400]
    h = Fake(f.name, {"project": "nope", "date": "2026-09-24", "title": "x"}); h.do_POST(); assert h.sent == [400]
    assert len(parse("p", f.name)) == 3
finally:
    os.unlink(f.name)
print("ok")
