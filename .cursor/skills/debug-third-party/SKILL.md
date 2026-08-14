---
name: debug-third-party
description: Use when an error, crash, or unexpected behavior appears to come from an external dependency rather than our own code — checks for a known upstream bug via the GitHub MCP server before building a workaround.
---

When you hit an error, crash, or unexpected behavior that appears to come from
an external dependency (not our own code), check whether it's a known bug
BEFORE building a workaround.

1. Identify the upstream repo (`owner/repo`) from the manifest — the
   `repository` field in package.json, project URL in PyPI/pyproject.toml,
   the Go module path, or Cargo.toml. Do not guess the repo.
2. Use the GitHub MCP server (issues toolset) to search that repo:
   - `search_issues` with a distinctive substring of the error message plus
     `is:issue is:open` (or `state:open`). Search the key symbol/message, not
     the whole stack trace.
   - Open the best matches with `issue_read` (`method: "get"` for the issue
     body, then `method: "get_comments"` — a separate call — for maintainer
     replies and any linked fix or workaround; `get` alone won't surface
     comments).
3. Also skim recently closed issues / merged PRs with `search_pull_requests`.
   A fix may exist in a newer release.
4. Report back: whether it's a known issue, the issue number + status, the full
   URL (`https://github.com/<owner>/<repo>/issues/<number>`), and any suggested
   workaround. Only then implement a local fix, and reference the issue number
   in a code comment.
