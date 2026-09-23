# logbook-viewer

Stateless single-page viewer for one or more `LOGBOOK.md` files (written by the `logbook` skill).

```bash
python3 server.py            # uses ./config.json
python3 server.py my.json    # other config
```

`config.json`:

```json
{"port": 8765, "projects": [{"name": "unfolding-fnf", "path": "/path/to/LOGBOOK.md"}]}
```

- Server: Python stdlib only, binds `127.0.0.1`, re-reads the files on every request. No state.
- Page: vanilla JS, `marked` from a CDN for Markdown (falls back to plain text offline).
- Filters live in the URL hash. The page polls every 5 s and re-renders when a file changed.
- Search: all words must match; `"quoted phrase"` matches exactly. Results show closed entries with hit counts and snippet lines; open one for the full text. `/` focuses the search box.
- The activity strip collapses (click "Activity"); the browser remembers it.
- Left table of contents: entries in view and their bold sections. Click to scroll. Hidden while searching.
- Heatmap cell = one day. Click it for the day view. `‹ ›` step one day. "commands only" hides prose.
- Images with a relative path are served from the directory of that project's logbook.
- Check: `python3 test_parse.py`. Debug: `python3 server.py --parse LOGBOOK.md`.
