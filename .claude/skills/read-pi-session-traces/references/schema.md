# Pi 1.4.0 session fields used by this skill

This reference covers only saved-session behavior consumed by `pi-trace.py`.
It is pinned to `@earendil-works/pi-coding-agent` `1.4.0`, the version in
`kits/pi/spec.yaml`. The trace format is still version 3; releases from
0.86.0 on added carriers inside it, 1.4.0 itself none, and older traces read
the same way. Treat every field as optional and unknown types as metadata.

## File and header

Sessions normally live below:

```text
${XDG_STATE_HOME:-~/.local/state}/md2okf/pi/sessions/
└── --<escaped-cwd>--/
    └── <created>_<session-id>.jsonl
```

The first parseable line in the first 1 MiB decides whether a file is a Pi
session. Blank and malformed lines before it are skipped. It must be an object
with `type: "session"` and a string `id`:

```json
{"type":"session","version":3,"id":"...","timestamp":"...","cwd":"/work","parentSession":"..."}
```

`parentSession` marks a fork. The header is not an entry and has no
`parentId`.

## Entry envelope and tree

Every subsequent entry is an object with the following structural fields:

```json
{"type":"message","id":"00000001","parentId":null,"timestamp":"2026-09-29T08:19:08.000Z"}
```

`id` and `parentId` form a tree. The last written entry is the default leaf;
other leaves are abandoned or alternate branches. Malformed traces may contain
missing parents, cycles, duplicate ids, non-string ids, or very large ids.
Traversal retains full ids internally, but output clips ids to 200 characters.

Pi 1.4.0 entry types consumed by the skill:

| Type | Allowlisted fields |
| --- | --- |
| `message` | `message`, described below |
| `model_change` | `provider`, `modelId` |
| `thinking_level_change` | `thinkingLevel` |
| `session_info` | `name` |
| `compaction` | `summary`, `firstKeptEntryId`, `tokensBefore`, `usage`, metadata-shaped `details` |
| `branch_summary` | `summary`, `fromId`, `usage`, metadata-shaped `details` |
| `custom` | `customType`; `data` shape only |
| `custom_message` | `customType`, `display`, content, `details` shape only |
| `label` | `targetId`, `label` |
| `usage` | `kind` (projected as `usageKind`), `provider`, `model`, `usage` |
| `context_edit` | `targetId`; `hidden: true` when `replacement` is `null`, else `replaced: true`. The replacement is never shown or searched |

Unknown entry types expose only type, structural metadata, field names, and
record size. Their values and any apparent usage are ignored.

## Messages

`message.role` selects the allowlist:

- `system`: the prompt and tool loadout. The first one declares every prompt
  section and tool; later ones patch `sections` by name (`null` removes one)
  and list `toolsAdded`/`toolsRemoved`. Only names are projected: `sections`,
  `sectionsRemoved`, `toolsAdded`, and `toolsRemoved`. Section text, content,
  and tool descriptions or parameters are never printed or searched.
- `user`: `content`, as a string or block list.
- `assistant`: `provider`, `model`, `stopReason`, `thinkingLevel` (the level
  requested for that response, when recorded), `errorMessage`, content, and
  `usage`.
- `toolResult`: `toolCallId`, `toolName`, `isError`, content, usage, the
  shape of `details`, and `nestedCalls` as `{count, complete}`. Truncation
  flags and `fullOutputPath` inside details are reported, but the path is never
  opened. Nested call arguments and errors are never shown.
- `bashExecution`: `command`, `output`, `exitCode`, `cancelled`, `truncated`,
  `excludeFromContext`, and `fullOutputPath`.
- `custom`: `customType`, `display`, content, and the shape of `details`.

Unknown roles expose field names and record size only.

Entry timestamps are ISO 8601. Nested message timestamps are epoch
milliseconds; tool elapsed time correlates those message timestamps.

## Content blocks

| Type | Behavior |
| --- | --- |
| `text` | Print and search `text`, clipped by the field limit. |
| `thinking` | Count characters by default; print/search text only with `--thinking`. |
| `toolCall` | Print/search `name` and serialized `arguments`; retain `id` for result correlation. |
| `image` | Report MIME type, base64 character count, and approximate bytes; never expose or search `data`. |

Unknown blocks expose type and field names only. Signatures and opaque details
are never printed or searched.

## Context annotations

A `compaction` summary replaces older context. Its `firstKeptEntryId` identifies
where retained raw entries begin. Only the latest compaction on a selected path
governs the current reconstructed context.

A `branch_summary` adds a summary of an abandoned branch to the selected
branch's context; it does not remove its ancestors. `fromId` identifies the
summarized branch endpoint.

A `context_edit` changes only later model context for one earlier entry,
named by `targetId`; raw history, UI, exports, and usage are unchanged. When
the target and a later edit of it are both on the selected path, `show` marks
the target "hidden from later context" (`replacement: null`) or "replaced in
later context". The latest edit of a target on the path wins; `show` marks
earlier ones superseded, and marks an edit whose target is not earlier on the
path as having no effect there. Edits are branch-relative: a path that ends
before the edit shows the target unedited.

`show` presents raw path entries and annotates these effects; it does not claim
to reconstruct the exact model request.

## Usage and tools

Only Pi 1.4.0 carriers are counted:

| Source | Carrier | Model attribution |
| --- | --- | --- |
| `conversation` | assistant `message.usage` | `provider/model` |
| `toolExecution` | tool-result `message.usage` | `unattributed` |
| `summarization` | `compaction.usage`, `branch_summary.usage` | `unattributed` |
| `auxiliary` | standalone `usage` entry, any `kind` (e.g. `cache_warm`) | `provider/model` |

`usage.total` sums every source. Pi counts `usage` entries in session totals
and treats unknown `kind` values as normal usage, so the skill does too.

Token fields are `input`, `output`, `cacheRead`, `cacheWrite`, `reasoning`, and
`totalTokens`. Cost fields below `cost` are `input`, `output`, `cacheRead`,
`cacheWrite`, and `total`. Values are summed exactly as recorded; absent fields
contribute nothing.

Assistant `toolCall` blocks correlate to `toolResult` messages by
`id`/`toolCallId`. Inspection reports calls, errors, calls without results,
results without calls, and elapsed milliseconds when both message timestamps
are usable.

A tool result's `nestedCalls` is a bounded record of the calls that tool made
to other tools, such as a codemode script's `tools.*` calls: `calls[]` with
`name`, `status` (`ok`, `error`, `unfinished`), `durationMs`, and `error`, plus
`complete`. Inspection counts them under `nestedTools`, keyed by nested tool
name, with `calls`, `errors` (status `error` or a recorded `error`), and
`durationMs {total, max}`. They never take part in direct call/result matching
and never change the direct `tools` numbers. `complete: false` means Pi
dropped some records, and `inspect` warns that `nestedTools` undercounts.

A fork copies existing entries into a new file. Summing parent and child, or
interpreting all child usage as new spend, double-counts copied history.
