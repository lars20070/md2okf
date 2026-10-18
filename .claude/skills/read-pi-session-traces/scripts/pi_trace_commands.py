"""Command handlers, fixed output budgeting, and Pi 0.84.4 statistics."""

from __future__ import annotations

import argparse
import collections
import datetime
import re
import sys

from pi_trace_core import (
    ID_CHARS,
    MAX_LISTED,
    UsageError,
    Warnings,
    build_tree,
    clip,
    is_number,
    iter_records,
    read_at,
    select_one,
    select_sessions,
    warn_problem,
)
from pi_trace_projection import (
    COST_FIELDS,
    KNOWN_BLOCKS,
    KNOWN_ROLES,
    KNOWN_TYPES,
    TOKEN_FIELDS,
    excerpt,
    project_entry,
    render_json,
    render_text,
    scalar,
    searchable_fields,
)

DEFAULT_FIELD_CHARS = 2000
DEFAULT_OUTPUT_CHARS = 20000
SUMMARY_RESERVE = 1000
EXIT_OK = 0
EXIT_NO_HITS = 1
EXIT_USAGE = 2


class Output:
    """Write each record once while reserving room for the fixed summary."""

    def __init__(self, as_json, unlimited):
        self.render = render_json if as_json else render_text
        self.cap = 0 if unlimited else DEFAULT_OUTPUT_CHARS
        self.used = 0
        self.shown = 0
        self.stopped_by = None

    def room(self):
        """Characters still free for items, or None when output is uncapped."""
        if not self.cap:
            return None
        return self.cap - SUMMARY_RESERVE - self.used

    def add(self, record):
        return self.add_rendered(self.render(record))

    def add_rendered(self, rendered):
        room = self.room()
        if room is not None and len(rendered) > room:
            self.stopped_by = "item-too-large" if self.shown == 0 else "output-limit"
            return False
        sys.stdout.write(rendered)
        self.used += len(rendered)
        self.shown += 1
        return True

    def warnings(self, warnings):
        shown = 0
        for warning in warnings.items:
            if not self.add(warning):
                break
            shown += 1
        return shown

    def summary(self, record):
        rendered = self.render(record)
        # Summary records contain counts only and fit the fixed reserve.
        if self.cap and self.used + len(rendered) > self.cap:
            raise RuntimeError("summary exceeded its fixed output reserve")
        sys.stdout.write(rendered)
        self.used += len(rendered)


def _summary(command, complete, stopped_by, warnings, warnings_shown, **counts):
    return {
        "kind": "summary",
        "command": command,
        **counts,
        "complete": complete,
        "stoppedBy": stopped_by,
        "warnings": warnings,
        "warningsShown": warnings_shown,
    }


def _session_record(session, chars):
    return {
        "kind": "session",
        "id": clip(session.id, ID_CHARS),
        "path": session.path,
        "cwd": scalar(session.cwd, chars),
        "created": scalar(session.created, 100),
        "parentSession": scalar(session.parent_session, ID_CHARS),
        "size": session.size,
        "partialTail": session.partial_tail,
    }


def cmd_sessions(args):
    sessions, found = select_sessions(args.path)
    out = Output(args.json, args.unlimited)
    page = (
        sessions[args.skip :]
        if not args.limit
        else sessions[args.skip : args.skip + args.limit]
    )
    shown = 0
    for session in page:
        if not out.add(_session_record(session, args.max_field_chars)):
            break
        shown += 1
    consumed = args.skip + shown
    remaining = max(0, len(sessions) - consumed)
    stopped = out.stopped_by
    if stopped is None and remaining:
        stopped = "limit"
    summary = _summary(
        "sessions",
        remaining == 0,
        stopped,
        0,
        0,
        total=len(sessions),
        shown=shown,
        skip=args.skip,
        remaining=remaining,
        notPi=found.not_pi,
        ignored=found.ignored,
    )
    out.summary(summary)
    return EXIT_OK


def _matcher(pattern, regex, ignore_case):
    if regex:
        flags = re.IGNORECASE if ignore_case else 0
        try:
            compiled = re.compile(pattern, flags)
        except re.error as error:
            raise UsageError(f"invalid regular expression: {error}") from None

        def match(value):
            found = compiled.search(value)
            return None if found is None else found.span()

        return match
    needle = pattern.casefold() if ignore_case else pattern

    def match(value):
        haystack = value.casefold() if ignore_case else value
        start = haystack.find(needle)
        return None if start < 0 else (start, start + len(needle))

    return match


def cmd_search(args):
    sessions, _ = select_sessions(args.path, args.session)
    match = _matcher(args.pattern, args.regex, args.ignore_case)
    warnings = Warnings()
    out = Output(args.json, args.unlimited)
    skipped = 0
    hits = 0
    matches_seen = 0
    decoded = 0
    sessions_searched = 0
    stopped = None
    for session in sessions:
        sessions_searched += 1
        for record in iter_records(session, warn_problem(warnings, session)):
            decoded += 1
            found = None
            for field, value in searchable_fields(record, args.thinking):
                span = match(value)
                if span is not None:
                    found = (field, value, span)
                    break
            if found is None:
                continue
            matches_seen += 1
            if skipped < args.skip:
                skipped += 1
                continue
            if args.limit and hits >= args.limit:
                stopped = "limit"
                break
            field, value, span = found
            hit = {
                "kind": "hit",
                "session": clip(session.id, ID_CHARS),
                "path": session.path,
                "line": record.line,
                "entryId": scalar(record.obj.get("id"), ID_CHARS),
                "type": scalar(record.obj.get("type"), 100),
                "field": field,
                "excerpt": excerpt(value, *span),
            }
            if not out.add(hit):
                stopped = out.stopped_by
                break
            hits += 1
        if stopped:
            break
    warnings_shown = out.warnings(warnings)
    if out.stopped_by and stopped is None:
        stopped = out.stopped_by
    complete = stopped is None
    out.summary(
        _summary(
            "search",
            complete,
            stopped,
            warnings.count,
            warnings_shown,
            hits=hits,
            skipped=skipped,
            recordsDecoded=decoded,
            sessionsSearched=sessions_searched,
            sessionsTotal=len(sessions),
        )
    )
    return EXIT_NO_HITS if matches_seen == 0 and complete else EXIT_OK


def _compaction_note(obj, node, path, latest):
    kept = obj.get("firstKeptEntryId")
    note = "replaces older model context"
    if node is not latest:
        note += "; superseded by a later compaction on this path"
    elif isinstance(kept, str) and kept not in {item.id for item in path}:
        note += "; firstKeptEntryId is not on this path"
    return note


def _branch_note(obj, tree):
    source = obj.get("fromId")
    if isinstance(source, str) and source not in tree.nodes:
        return "adds an abandoned-branch summary; fromId is not in this file"
    return "adds an abandoned-branch summary to model context"


def _show_entry(stream, session, tree, path, index, latest_compaction, args, warnings):
    """Project path[index] with its path annotations, or None if unreadable."""
    node = path[index]
    record = read_at(stream, node.line, node.offset)
    if record is None:
        warnings.add(
            session.path,
            node.line,
            "entry no longer parses; did the file change?",
        )
        return None
    projected = project_entry(
        record,
        args.max_field_chars,
        thinking=args.thinking,
        tools=not args.no_tools,
    )
    children = tree.children.get(node.id, [])
    if len(children) > 1:
        on_path = path[index + 1].id if index + 1 < len(path) else None
        projected["branchPoint"] = {
            "children": len(children),
            "others": [clip(child, ID_CHARS) for child in children if child != on_path][
                :MAX_LISTED
            ],
        }
    if node.type == "compaction":
        projected["context"] = _compaction_note(
            record.obj, node, path, latest_compaction
        )
    elif node.type == "branch_summary":
        projected["context"] = _branch_note(record.obj, tree)
    return projected


def _fit_window(size, anchor, low, high, room):
    """Grow a contiguous [start, end) slice outward from anchor while it fits.

    Nearest entries win, alternating sides and starting before the anchor. A
    side stops at the first entry that does not fit, so the slice stays
    contiguous. Returns None when the anchor alone does not fit.
    """
    used = size(anchor)
    if used > room:
        return None
    start, end = anchor, anchor + 1
    grow_before, grow_after = start > low, end < high
    before_turn = True
    while grow_before or grow_after:
        take_before = grow_before and (before_turn or not grow_after)
        cost = size(start - 1 if take_before else end)
        fits = used + cost <= room
        if fits:
            used += cost
            if take_before:
                start -= 1
            else:
                end += 1
        if take_before:
            grow_before = fits and start > low
        else:
            grow_after = fits and end < high
        before_turn = not take_before
    return start, end


def cmd_show(args):
    session = select_one(args.path, args.session)
    warnings = Warnings()
    tree = build_tree(session, warnings)
    out = Output(args.json, args.unlimited)
    if not tree.order:
        warnings_shown = out.warnings(warnings)
        out.summary(
            _summary(
                "show",
                True,
                None,
                warnings.count,
                warnings_shown,
                pathLength=0,
                selected=0,
                shown=0,
                omitted=0,
                entriesBefore=0,
                entriesAfter=0,
                anchor=None,
                anchorShown=False,
            )
        )
        return EXIT_OK

    leaf = tree.resolve(args.leaf, "leaf") if args.leaf else None
    target = tree.resolve(args.entry, "entry") if args.entry else None
    if args.line is not None:
        if args.line == session.header_line:
            raise UsageError(f"line {args.line} is the session header, not an entry")
        target = tree.by_line.get(args.line)
        if target is None:
            raise UsageError(f"no entry starts at line {args.line}")
    # The anchor is the entry the caller cares about most; it is the first to
    # claim the output budget, and context is added around it while it fits.
    if target is None:
        leaf = leaf or tree.order[-1]
        path = tree.ancestry(leaf.id)
        low = 0 if args.all else max(0, len(path) - (args.tail or 20))
        high = len(path)
        anchor = low if args.all else high - 1
    else:
        if leaf:
            path = tree.ancestry(leaf.id)
            if target.id not in {node.id for node in path}:
                raise UsageError("the selected entry is not on the path to --leaf")
        else:
            leaf = tree.order[-1]
            path = tree.ancestry(leaf.id)
            if target.id not in {node.id for node in path}:
                leaf = tree.latest_leaf_below(target.id)
                path = tree.ancestry(leaf.id)
        anchor = [node.id for node in path].index(target.id)
        low = max(0, anchor - args.before)
        high = min(len(path), anchor + args.after + 1)

    latest_compaction = next(
        (node for node in reversed(path) if node.type == "compaction"), None
    )
    stopped = None
    shown = 0
    anchor_shown = False
    with open(session.path, "rb") as stream:

        def render(index):
            projected = _show_entry(
                stream, session, tree, path, index, latest_compaction, args, warnings
            )
            return None if projected is None else out.render(projected)

        rendered = {}
        room = out.room()
        if room is None:
            start, end = low, high
        else:
            # Render lazily while growing, so memory stays within the cap.
            def size(index):
                if index not in rendered:
                    rendered[index] = render(index)
                return len(rendered[index] or "")

            window = _fit_window(size, anchor, low, high, room)
            if window is None:
                stopped = "item-too-large"
                start = end = anchor
            else:
                start, end = window
                if (start, end) != (low, high):
                    stopped = "output-limit"
        for index in range(start, end):
            text = rendered[index] if index in rendered else render(index)
            if text is None:
                continue
            if not out.add_rendered(text):
                break
            shown += 1
            anchor_shown = anchor_shown or index == anchor
    omitted = (high - low) - shown
    warnings_shown = out.warnings(warnings)
    stopped = stopped or out.stopped_by
    out.summary(
        _summary(
            "show",
            omitted == 0,
            stopped,
            warnings.count,
            warnings_shown,
            pathLength=len(path),
            selected=high - low,
            shown=shown,
            omitted=omitted,
            entriesBefore=start,
            entriesAfter=len(path) - end,
            anchor=clip(path[anchor].id, ID_CHARS),
            anchorShown=anchor_shown,
        )
    )
    return EXIT_OK


def _iso_ms(value):
    if not isinstance(value, str):
        return None
    value = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        return datetime.datetime.fromisoformat(value).timestamp() * 1000
    except (ValueError, OverflowError, OSError):
        return None


class UsageSum:
    def __init__(self):
        self.records = 0
        self.tokens = {key: 0 for key in TOKEN_FIELDS}
        self.cost = {key: 0 for key in COST_FIELDS}

    def add(self, usage):
        if not isinstance(usage, dict):
            return False
        self.records += 1
        for key in TOKEN_FIELDS:
            if is_number(usage.get(key)):
                self.tokens[key] += usage[key]
        cost = usage.get("cost")
        if isinstance(cost, dict):
            for key in COST_FIELDS:
                if is_number(cost.get(key)):
                    self.cost[key] += cost[key]
        return True

    def as_dict(self):
        return {"records": self.records, **self.tokens, "cost": self.cost}


class ToolStats:
    def __init__(self):
        self.calls = 0
        self.errors = 0
        self.without_result = 0
        self.results_without_call = 0
        self.elapsed_total = 0
        self.elapsed_max = 0

    def as_dict(self):
        return {
            "calls": self.calls,
            "errors": self.errors,
            "withoutResult": self.without_result,
            "resultsWithoutCall": self.results_without_call,
            "elapsedMs": {"total": self.elapsed_total, "max": self.elapsed_max},
        }


class SessionStats:
    def __init__(self, chars):
        self.chars = chars
        self.types = collections.Counter()
        self.roles = collections.Counter()
        self.blocks = collections.Counter()
        self.unknown_types = collections.Counter()
        self.unknown_roles = collections.Counter()
        self.unknown_blocks = collections.Counter()
        self.prompts = 0
        self.models = collections.Counter()
        self.model_changes = collections.Counter()
        self.tools = {}
        self.pending = {}
        self.by_source = {
            "conversation": UsageSum(),
            "toolExecution": UsageSum(),
            "summarization": UsageSum(),
        }
        self.by_model = {}
        self.summaries_without_usage = 0

    def name(self, value):
        return (
            clip(value, min(200, self.chars) if self.chars else 200)
            if isinstance(value, str)
            else "?"
        )

    def tool(self, value):
        name = self.name(value)
        return self.tools.setdefault(name, ToolStats())

    def usage(self, source, model, value):
        if self.by_source[source].add(value):
            self.by_model.setdefault(model, UsageSum()).add(value)

    def count_blocks(self, content):
        if not isinstance(content, list):
            return
        for block in content:
            block_type = block.get("type") if isinstance(block, dict) else None
            name = self.name(block_type)
            self.blocks[name] += 1
            if block_type not in KNOWN_BLOCKS:
                self.unknown_blocks[name] += 1

    def visit(self, record):
        obj = record.obj
        entry_type = obj.get("type")
        name = self.name(entry_type)
        self.types[name] += 1
        if entry_type == "message":
            self.message(record, obj.get("message"), _iso_ms(obj.get("timestamp")))
        elif entry_type == "model_change":
            key = f"{self.name(obj.get('provider'))}/{self.name(obj.get('modelId'))}"
            self.model_changes[key] += 1
        elif entry_type == "custom_message":
            self.count_blocks(obj.get("content"))
        elif entry_type in ("compaction", "branch_summary"):
            if not self.by_source["summarization"].add(obj.get("usage")):
                self.summaries_without_usage += 1
            else:
                self.by_model.setdefault("unattributed", UsageSum()).add(
                    obj.get("usage")
                )
        elif entry_type not in KNOWN_TYPES:
            # Future entries are metadata only, including any future usage carrier.
            self.unknown_types[name] += 1

    def message(self, record, msg, when):
        if not isinstance(msg, dict):
            self.roles["?"] += 1
            return
        role = msg.get("role")
        name = self.name(role)
        self.roles[name] += 1
        self.count_blocks(msg.get("content"))
        if role == "user":
            self.prompts += 1
        elif role == "assistant":
            model = f"{self.name(msg.get('provider'))}/{self.name(msg.get('model'))}"
            self.models[model] += 1
            self.usage("conversation", model, msg.get("usage"))
            for block in (
                msg.get("content", []) if isinstance(msg.get("content"), list) else []
            ):
                if isinstance(block, dict) and block.get("type") == "toolCall":
                    self.tool(block.get("name")).calls += 1
                    call_id = block.get("id")
                    if isinstance(call_id, str):
                        self.pending[call_id] = (block.get("name"), when)
        elif role == "toolResult":
            self.usage("toolExecution", "unattributed", msg.get("usage"))
            call_id = msg.get("toolCallId")
            pending = (
                self.pending.pop(call_id, None) if isinstance(call_id, str) else None
            )
            stats = self.tool(pending[0] if pending else msg.get("toolName"))
            if pending is None:
                stats.results_without_call += 1
            elif pending[1] is not None and when is not None:
                elapsed = max(0, round(when - pending[1]))
                stats.elapsed_total += elapsed
                stats.elapsed_max = max(stats.elapsed_max, elapsed)
            if msg.get("isError") is True:
                stats.errors += 1
        elif role not in KNOWN_ROLES:
            self.unknown_roles[name] += 1

    def finish(self):
        for name, _ in self.pending.values():
            self.tool(name).without_result += 1


def _inspect_record(session, chars, warnings):
    stats = SessionStats(chars)
    tree = build_tree(session, warnings, stats.visit)
    stats.finish()
    leaves = tree.leaves()
    orphans = tree.orphans()
    cycles = tree.cycles()
    default_path = tree.ancestry(tree.order[-1].id) if tree.order else []
    messages = []
    for label, values in (
        ("entry types", stats.unknown_types),
        ("message roles", stats.unknown_roles),
        ("content blocks", stats.unknown_blocks),
    ):
        if values:
            messages.append(
                f"unknown {label} (newer Pi?): "
                + ", ".join(f"{key} x{count}" for key, count in values.most_common(10))
                + "; metadata only"
            )
    if session.parent_session:
        messages.append(
            "forked session: recorded usage includes history copied from its parent"
        )
    if orphans:
        messages.append(f"{len(orphans)} orphan entry/entries have missing parents")
    if cycles:
        messages.append(
            f"{len(cycles)} parent cycle(s), including {clip(cycles[0], 80)}"
        )
    for message in messages:
        warnings.add(session.path, None, message)
    return {
        "kind": "session",
        "id": clip(session.id, ID_CHARS),
        "path": session.path,
        "cwd": scalar(session.cwd, chars),
        "created": scalar(session.created, 100),
        "parentSession": scalar(session.parent_session, ID_CHARS),
        "size": session.size,
        "partialTail": session.partial_tail,
        "entries": len(tree.order) + tree.without_id,
        "counts": {
            "types": dict(stats.types),
            "roles": dict(stats.roles),
            "blocks": dict(stats.blocks),
        },
        "tree": {
            "rootCount": len(tree.roots),
            "leafCount": len(leaves),
            "leaves": [
                {"id": clip(node.id, ID_CHARS), "line": node.line}
                for node in leaves[-MAX_LISTED:]
            ],
            "orphanCount": len(orphans),
            "orphans": [
                {
                    "id": clip(node.id, ID_CHARS),
                    "parentId": clip(node.parent, ID_CHARS),
                    "line": node.line,
                }
                for node in orphans[:MAX_LISTED]
            ],
            "cycleCount": len(cycles),
            "pathLength": len(default_path),
        },
        "prompts": stats.prompts,
        "models": {
            "assistant": dict(stats.models),
            "changes": dict(stats.model_changes),
        },
        "tools": {key: value.as_dict() for key, value in sorted(stats.tools.items())},
        "usage": {
            "note": "sum of usage recorded by Pi 0.84.4 carriers",
            "bySource": {
                key: value.as_dict() for key, value in stats.by_source.items()
            },
            "byModel": {key: value.as_dict() for key, value in stats.by_model.items()},
            "summariesWithoutUsage": stats.summaries_without_usage,
        },
    }


def cmd_inspect(args):
    sessions, _ = select_sessions(args.path, args.session)
    page = (
        sessions[args.skip :]
        if not args.limit
        else sessions[args.skip : args.skip + args.limit]
    )
    warnings = Warnings()
    out = Output(args.json, args.unlimited)
    shown = 0
    for session in page:
        report = _inspect_record(session, args.max_field_chars, warnings)
        if not out.add(report):
            break
        shown += 1
    remaining = max(0, len(sessions) - args.skip - shown)
    warnings_shown = out.warnings(warnings)
    stopped = out.stopped_by
    if stopped is None and remaining:
        stopped = "limit"
    out.summary(
        _summary(
            "inspect",
            remaining == 0,
            stopped,
            warnings.count,
            warnings_shown,
            total=len(sessions),
            shown=shown,
            skip=args.skip,
            remaining=remaining,
        )
    )
    return EXIT_OK


def count(value):
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"not a whole number: {value!r}") from None
    if number < 0:
        raise argparse.ArgumentTypeError(f"must be 0 or more: {value!r}")
    return number


def positive(value):
    number = count(value)
    if not number:
        raise argparse.ArgumentTypeError("must be 1 or more")
    return number


PATH_HELP = (
    "the sessions root, one escaped-cwd folder, or one .jsonl file; "
    "directories are searched recursively"
)


def build_parser(prog):
    output = argparse.ArgumentParser(add_help=False)
    output.add_argument(
        "--max-field-chars",
        type=count,
        default=DEFAULT_FIELD_CHARS,
        metavar="N",
        help="clip each text field (0 = unlimited; default 2000)",
    )
    output.add_argument(
        "--unlimited",
        action="store_true",
        help="disable the fixed 20,000-character output cap",
    )
    parser = argparse.ArgumentParser(prog=prog)
    sub = parser.add_subparsers(dest="command", required=True)

    command = sub.add_parser("sessions", parents=[output], help="list session headers")
    command.add_argument("path", metavar="PATH", help=PATH_HELP)
    command.add_argument("--limit", type=count, default=50, metavar="N")
    command.add_argument("--skip", type=count, default=0, metavar="N")
    command.add_argument("--json", action="store_true", help="emit JSON Lines")
    command.set_defaults(func=cmd_sessions)

    command = sub.add_parser("search", parents=[output], help="search decoded fields")
    command.add_argument("path", metavar="PATH", help=PATH_HELP)
    command.add_argument("pattern", metavar="PATTERN")
    command.add_argument("--session", metavar="ID")
    command.add_argument("-e", "--regex", action="store_true")
    command.add_argument("-i", "--ignore-case", action="store_true")
    command.add_argument("--thinking", action="store_true")
    command.add_argument("--limit", type=count, default=20, metavar="N")
    command.add_argument("--skip", type=count, default=0, metavar="N")
    command.add_argument("--json", action="store_true", help="emit JSON Lines")
    command.set_defaults(func=cmd_search)

    command = sub.add_parser("show", parents=[output], help="show one branch slice")
    command.add_argument("path", metavar="PATH", help=PATH_HELP)
    command.add_argument("--session", metavar="ID")
    where = command.add_mutually_exclusive_group()
    where.add_argument("--entry", metavar="ID")
    where.add_argument("--line", type=positive, metavar="N")
    command.add_argument("--leaf", metavar="ID")
    command.add_argument("--before", type=count, default=3, metavar="N")
    command.add_argument("--after", type=count, default=5, metavar="N")
    command.add_argument("--tail", type=positive, metavar="N")
    command.add_argument("--all", action="store_true")
    command.add_argument("--thinking", action="store_true")
    command.add_argument("--no-tools", action="store_true")
    command.add_argument("--json", action="store_true", help="emit JSON Lines")
    command.set_defaults(func=cmd_show)

    command = sub.add_parser(
        "inspect", parents=[output], help="summarize structure and recorded usage"
    )
    command.add_argument("path", metavar="PATH", help=PATH_HELP)
    command.add_argument("--session", metavar="ID")
    command.add_argument("--limit", type=count, default=50, metavar="N")
    command.add_argument("--skip", type=count, default=0, metavar="N")
    command.add_argument("--json", action="store_true", help="emit JSON Lines")
    command.set_defaults(func=cmd_inspect)
    return parser


def main(argv=None, prog="pi-trace.py"):
    args = build_parser(prog).parse_args(argv)
    try:
        return args.func(args)
    except UsageError as error:
        sys.stdout.flush()
        print(f"{prog}: error: {error}", file=sys.stderr)
        for candidate in error.candidates:
            print(f"  {candidate}", file=sys.stderr)
        return EXIT_USAGE
