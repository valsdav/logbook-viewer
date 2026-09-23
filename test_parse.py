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
print("ok")
