# Pi 0.84.4 session fields used by this skill

This reference covers only saved-session behavior consumed by `pi-trace.py`.
It is pinned to `@earendil-works/pi-coding-agent` `0.84.4`, the version in
`kits/sbxpi/spec.yaml`. Treat every field as optional and unknown types as
metadata.

## File and header

Sessions normally live below:

```text
<state>/sbxagent/traces/<project>/sbxpi/sessions/
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

Pi 0.84.4 entry types consumed by the skill:

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

Unknown entry types expose only type, structural metadata, field names, and
record size. Their values and any apparent usage are ignored.

## Messages

`message.role` selects the allowlist:

- `user`: `content`, as a string or block list.
- `assistant`: `provider`, `model`, `stopReason`, `errorMessage`, content, and
  `usage`.
- `toolResult`: `toolCallId`, `toolName`, `isError`, content, usage, and the
  shape of `details`. Truncation flags and `fullOutputPath` inside details are
  reported, but the path is never opened.
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

`show` presents raw path entries and annotates these effects; it does not claim
to reconstruct the exact model request.

## Usage and tools

Only Pi 0.84.4 carriers are counted:

| Source | Carrier | Model attribution |
| --- | --- | --- |
| `conversation` | assistant `message.usage` | `provider/model` |
| `toolExecution` | tool-result `message.usage` | `unattributed` |
| `summarization` | `compaction.usage`, `branch_summary.usage` | `unattributed` |

Token fields are `input`, `output`, `cacheRead`, `cacheWrite`, `reasoning`, and
`totalTokens`. Cost fields below `cost` are `input`, `output`, `cacheRead`,
`cacheWrite`, and `total`. Values are summed exactly as recorded; absent fields
contribute nothing.

Assistant `toolCall` blocks correlate to `toolResult` messages by
`id`/`toolCallId`. Inspection reports calls, errors, calls without results,
results without calls, and elapsed milliseconds when both message timestamps
are usable.

A fork copies existing entries into a new file. Summing parent and child, or
interpreting all child usage as new spend, double-counts copied history.
