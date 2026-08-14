---
name: context7-docs
description: Use before writing or modifying any code that uses a third-party library, package, or framework — fetches current docs via the Context7 MCP server instead of relying on training data.
---

Before writing or modifying any code that uses a third-party library, package,
or framework, fetch its current docs via the Context7 MCP server — do not rely
on training data for external APIs.

- Call `resolve-library-id` with the library name to get its Context7 ID, then
  `query-docs` with that ID and a specific `topic` (e.g. "middleware",
  "query invalidation").
- If you already know the exact ID (e.g. `/vercel/next.js`), skip resolving and
  call `query-docs` directly. Match the version in our manifest
  (package.json / requirements.txt / go.mod) when the library moves fast.
- Verify the library ID and version reported in the tool output before trusting
  the result; Context7 falls back to "latest" if a pinned version isn't indexed.
- Prefer a focused `topic` query to keep the pull small (~5k tokens/call).

If Context7 has no entry for a library, say so and fall back to your best
knowledge — do not block. You can also trigger a lookup manually by adding
"use context7" to a request.
