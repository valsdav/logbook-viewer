---
name: logbook
description: Appends a dated entry to a running LOGBOOK.md in the repository, recording the history of development done with Claude — what was worked on, what changed, implementation decisions, dead ends and open questions — so the user can later remember what was developed and why. Use ONLY when the user explicitly asks, e.g. "/dev-logbook", "update the logbook", "log this session", "add a logbook entry". Do not run it on your own initiative.
---

# Development logbook

The logbook is the user's memory of the project: a narrative history, not technical documentation. Months from now the user should be able to read it and recall what was built, in what order, and why things ended up the way they are. It lives in the repository and grows by one entry each time it is invoked.

## File

- Path: `LOGBOOK.md` at the repository root (find it with `git rev-parse --show-toplevel`). If the user already has a logbook at another path, use that one.
- One running file, entries in chronological order, newest at the bottom. Appending keeps edits cheap and git diffs clean.
- If the file does not exist, create it with this header, then add the first entry:

```markdown
# Development logbook

History of development work on this repository, done with Claude.
Each entry records what was done, what changed, and the decisions behind it.
```

- Never rewrite or reorder past entries. If something recorded earlier turned out wrong, say so in the new entry ("Correction to 2026-09-10: ...").

## Keep it cheap

Build the entry from the conversation. If `change-digest` summaries were produced in this session, condense them rather than reconstructing the work. For the factual footprint use only `git diff --stat`, `git status --short` and `git log --oneline` for recent commits. To append, do not read the whole logbook: at most look at its last entry (`tail -n 40 LOGBOOK.md`) for continuity, then append with a shell heredoc or an append-style edit.

## Entry template

```markdown
---

## <YYYY-MM-DD> — <short title of the session or step>

**Context:** why this work was done and what it builds on (link to the previous entry's open questions when relevant).

**What was done**
- The main pieces of work, at the level of "added X to do Y", not line-by-line.

**What changed**
- Touched areas/files, grouped sensibly. Commit hashes if commits were made.

**Decisions**
- Decision — reason. Include rejected alternatives when they matter.

**Dead ends**
- What was tried and abandoned, and why. (Omit if none.)

**Results**
- Outcomes of tests or studies, with key numbers. (Omit if none.)

**Commands**
```bash
# one comment line per step, then the command exactly as it was run
python submit_job.py -c $CFG/config.yaml -s fnf --version v1
```

**Open questions / next steps**
- What remains, as stated by the user or evident from unfinished work.
```

Within one day, a second invocation adds a new entry with its own title (e.g. "2026-09-16 — entry 2: ..."), rather than editing the earlier one. The heading is always `## YYYY-MM-DD — title` on one line: it is what the viewer parses.

## Commands

Commands are copied from the logbook later, so keep them machine-clean:

- Every command the user may re-run goes in a fenced ```` ```bash ```` block, never inline in prose and never inside a list item. Top-level blocks only.
- One block per logical chain (e.g. "the v8b chain"); inside it, a `# ` comment line before each step. No prose inside the block, no `$ ` prompts, no `...` placeholders: the block must run as pasted.
- Variables the commands depend on (`BASE=`, `CFG=`) are defined at the top of the block, not assumed from an earlier entry.
- Inline code (`` `name` ``) is for file names, config keys and function names only, never for a command.
- If a command was later corrected, repeat the full corrected block in the new entry ("Correction to ..."), do not describe the edit in words.
- Images: `![caption](docs/logbook_img/<date>-<slug>.png)`, path relative to the repository root.

## Style

- Write for the user's future self: brief, concrete, readable in a minute per entry.
- Record reasons, since the code already records the what. "Switched to unbinned fit" is weak; "Switched to unbinned fit because binned SFs were unstable in low-stat eta bins" is useful.
- Use exact names (functions, files, config keys) so entries are greppable.
- Mark intermediate states honestly ("work in progress", "tests not yet run").
- Do not commit the logbook unless the user asks; mention that it was updated and show the new entry in the chat.
