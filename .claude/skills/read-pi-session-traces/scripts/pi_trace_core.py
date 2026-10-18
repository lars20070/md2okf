"""Discovery, streaming reads, warnings, selection, and Pi entry trees."""

from __future__ import annotations

import json
import os

HEADER_SCAN_BYTES = 1024 * 1024
ID_CHARS = 200
MAX_LISTED = 10
MAX_WARNINGS = 20


class UsageError(Exception):
    """Bad arguments or a path that cannot select the requested session."""

    def __init__(self, message, candidates=None):
        super().__init__(message)
        self.candidates = candidates or []


def clip(value, limit):
    text = value if isinstance(value, str) else str(value)
    if limit and len(text) > limit:
        return f"{text[:limit]}…[clipped {len(text) - limit} chars]"
    return text


def field_names(obj):
    names = [clip(str(key), 100) for key in sorted(obj, key=str)[:50]]
    if len(obj) > 50:
        names.append(f"…{len(obj) - 50} more")
    return names


def is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def shape(value):
    if isinstance(value, dict):
        return {
            "fields": field_names(value),
            "size": len(json.dumps(value, ensure_ascii=False)),
        }
    if isinstance(value, list):
        return {
            "items": len(value),
            "size": len(json.dumps(value, ensure_ascii=False)),
        }
    return {"type": type(value).__name__}


def text_value(value):
    if isinstance(value, str):
        return value
    if value is None:
        return ""
    if isinstance(value, (bool, int, float)):
        return json.dumps(value)
    return f"[{type(value).__name__}]"


_MALFORMED = object()


def _reject_constant(name):
    raise ValueError(f"non-standard JSON constant {name}")


def parse_json(raw):
    try:
        return json.loads(
            raw.decode("utf-8", "replace"), parse_constant=_reject_constant
        )
    except (ValueError, RecursionError):
        return _MALFORMED


class Session:
    def __init__(self, path, header, header_line, size, mtime, partial_tail):
        self.path = path
        self.header = header
        self.header_line = header_line
        self.size = size
        self.mtime = mtime
        self.partial_tail = partial_tail

    @property
    def id(self):
        return self.header["id"]

    @property
    def cwd(self):
        value = self.header.get("cwd")
        return value if isinstance(value, str) else None

    @property
    def created(self):
        value = self.header.get("timestamp")
        return value if isinstance(value, str) else None

    @property
    def parent_session(self):
        value = self.header.get("parentSession")
        return value if isinstance(value, str) and value else None


def read_header(path):
    """Return Pi's first parseable header in the first MiB, and its line."""
    try:
        with open(path, "rb") as stream:
            scanned = 0
            line = 0
            while True:
                raw = stream.readline(HEADER_SCAN_BYTES - scanned + 1)
                if not raw:
                    return None
                scanned += len(raw)
                line += 1
                if scanned > HEADER_SCAN_BYTES:
                    return None
                if not raw.strip():
                    continue
                obj = parse_json(raw)
                if obj is _MALFORMED or (not isinstance(obj, (dict, list)) and not obj):
                    continue
                if (
                    isinstance(obj, dict)
                    and obj.get("type") == "session"
                    and isinstance(obj.get("id"), str)
                ):
                    return obj, line
                return None
    except OSError:
        return None


def _partial_tail(path, size):
    if not size:
        return False
    try:
        with open(path, "rb") as stream:
            stream.seek(-1, os.SEEK_END)
            return stream.read(1) != b"\n"
    except OSError:
        return False


def open_session(path):
    found = read_header(path)
    if found is None:
        return None
    try:
        stat = os.stat(path)
    except OSError:
        return None
    header, line = found
    return Session(
        path,
        header,
        line,
        stat.st_size,
        stat.st_mtime,
        _partial_tail(path, stat.st_size),
    )


class Discovery:
    def __init__(self):
        self.sessions = []
        self.not_pi = 0
        self.ignored = 0


def discover(path):
    found = Discovery()
    if not os.path.exists(path):
        raise UsageError(f"{path}: no such file or directory")
    if os.path.isfile(path):
        session = open_session(path)
        if session is None:
            found.not_pi += 1
        else:
            found.sessions.append(session)
        return found
    for directory, dirnames, filenames in os.walk(path):
        dirnames[:] = sorted(name for name in dirnames if not name.startswith("."))
        for name in sorted(filenames):
            if name.startswith(".") or not name.endswith(".jsonl"):
                found.ignored += 1
                continue
            session = open_session(os.path.join(directory, name))
            if session is None:
                found.not_pi += 1
            else:
                found.sessions.append(session)
    found.sessions.sort(key=lambda session: (-session.mtime, session.path))
    return found


def _candidates(sessions):
    rows = [
        f"{clip(session.id, ID_CHARS)}  {session.path}" for session in sessions[:10]
    ]
    if len(sessions) > 10:
        rows.append(f"… and {len(sessions) - 10} more")
    return rows


def select_sessions(path, session_id=None):
    found = discover(path)
    sessions = found.sessions
    if not sessions:
        extra = (
            f" ({found.not_pi} .jsonl file(s) without a Pi header skipped)"
            if found.not_pi
            else ""
        )
        raise UsageError(f"no Pi session found at {path}{extra}")
    if session_id:
        matches = [session for session in sessions if session.id == session_id]
        if not matches:
            matches = [
                session for session in sessions if session.id.startswith(session_id)
            ]
        if not matches:
            raise UsageError(
                f"no session id starts with {clip(session_id, ID_CHARS)!r}"
            )
        if len(matches) > 1:
            raise UsageError(
                f"session id {session_id!r} is ambiguous: {len(matches)} match",
                _candidates(matches),
            )
        sessions = matches
    return sessions, found


def select_one(path, session_id=None):
    sessions, _ = select_sessions(path, session_id)
    if len(sessions) != 1:
        raise UsageError(
            f"{path} holds {len(sessions)} sessions; pass --session ID or one file",
            _candidates(sessions),
        )
    return sessions[0]


class Record:
    __slots__ = ("line", "obj", "offset", "size")

    def __init__(self, line, offset, size, obj):
        self.line = line
        self.offset = offset
        self.size = size
        self.obj = obj


class Warnings:
    def __init__(self):
        self.items = []
        self.count = 0
        self._seen = set()

    def add(self, path, line, message):
        key = (path, line, message)
        if key in self._seen:
            return
        self._seen.add(key)
        self.count += 1
        if len(self.items) < MAX_WARNINGS:
            self.items.append(
                {"kind": "warning", "path": path, "line": line, "message": message}
            )


PROBLEM_TEXT = {
    "malformed": "unparseable line skipped",
    "not-object": "line is JSON but not an object; skipped",
    "extra-header": "a second session header; skipped",
    "partial-tail": "last line has no newline (a write in progress?); skipped",
}


def iter_records(session, on_problem):
    """Stream valid entry objects after the header."""
    with open(session.path, "rb") as stream:
        offset = 0
        for line, raw in enumerate(stream, 1):
            start = offset
            offset += len(raw)
            if not raw.endswith(b"\n"):
                on_problem("partial-tail", line)
                break
            if not raw.strip():
                continue
            obj = parse_json(raw)
            if obj is _MALFORMED:
                on_problem("malformed", line)
                continue
            if line == session.header_line:
                continue
            if not isinstance(obj, dict):
                on_problem("not-object", line)
                continue
            if obj.get("type") == "session":
                on_problem("extra-header", line)
                continue
            yield Record(line, start, len(raw), obj)


def warn_problem(warnings, session):
    def add(kind, line):
        warnings.add(session.path, line, PROBLEM_TEXT[kind])

    return add


def read_at(stream, line, offset):
    stream.seek(offset)
    raw = stream.readline()
    if not raw.endswith(b"\n"):
        return None
    obj = parse_json(raw)
    if not isinstance(obj, dict):
        return None
    return Record(line, offset, len(raw), obj)


class Node:
    __slots__ = ("id", "line", "offset", "parent", "timestamp", "type")

    def __init__(self, entry_id, parent, line, offset, entry_type, timestamp):
        self.id = entry_id
        self.parent = parent
        self.line = line
        self.offset = offset
        self.type = entry_type
        self.timestamp = timestamp


class Tree:
    def __init__(self, session, warnings):
        self.session = session
        self.warnings = warnings
        self.nodes = {}
        self.order = []
        self.children = {}
        self.by_line = {}
        self.without_id = 0
        self.duplicates = 0

    def add(self, record):
        obj = record.obj
        entry_id = obj.get("id")
        if not isinstance(entry_id, str):
            self.without_id += 1
            self.warnings.add(
                self.session.path,
                record.line,
                "entry has no string id; left out of the tree",
            )
            return
        if len(entry_id) > ID_CHARS:
            self.warnings.add(
                self.session.path,
                record.line,
                "structural id exceeds 200 characters; navigation is not guaranteed",
            )
        parent = obj.get("parentId")
        if parent is not None and not isinstance(parent, str):
            self.warnings.add(
                self.session.path,
                record.line,
                "parentId is not a string; treated as a root",
            )
            parent = None
        if isinstance(parent, str) and len(parent) > ID_CHARS:
            self.warnings.add(
                self.session.path,
                record.line,
                "structural parentId exceeds 200 characters; navigation is not guaranteed",
            )
        if entry_id in self.nodes:
            self.duplicates += 1
            self.warnings.add(
                self.session.path,
                record.line,
                f"duplicate id {clip(entry_id, 80)}; the later entry wins",
            )
        entry_type = obj.get("type")
        timestamp = obj.get("timestamp")
        node = Node(
            entry_id,
            parent,
            record.line,
            record.offset,
            entry_type if isinstance(entry_type, str) else None,
            timestamp if isinstance(timestamp, str) else None,
        )
        self.nodes[entry_id] = node
        self.order.append(node)
        self.by_line[record.line] = node
        self.children.setdefault(parent, []).append(entry_id)

    @property
    def roots(self):
        return self.children.get(None, [])

    def leaves(self):
        return [node for node in self.order if node.id not in self.children]

    def orphans(self):
        return [
            node
            for node in self.order
            if node.parent is not None and node.parent not in self.nodes
        ]

    def cycles(self):
        """Return one representative id per parent cycle in linear time."""
        done = set()
        cycles = []
        for start in self.nodes:
            if start in done:
                continue
            path = []
            positions = {}
            current = start
            while current in self.nodes and current not in done:
                if current in positions:
                    cycles.append(current)
                    break
                positions[current] = len(path)
                path.append(current)
                current = self.nodes[current].parent
            done.update(path)
        return cycles

    def ancestry(self, entry_id):
        chain = []
        seen = set()
        current = entry_id
        while current is not None:
            node = self.nodes.get(current)
            if node is None:
                line = chain[-1].line if chain else None
                self.warnings.add(
                    self.session.path,
                    line,
                    f"parent {clip(current, 80)} is not in this file; walk stopped",
                )
                break
            if current in seen:
                self.warnings.add(
                    self.session.path,
                    node.line,
                    f"parent cycle at {clip(current, 80)}; walk stopped",
                )
                break
            seen.add(current)
            chain.append(node)
            current = node.parent
        chain.reverse()
        return chain

    def latest_leaf_below(self, entry_id):
        best = self.nodes[entry_id]
        stack = [entry_id]
        seen = set()
        while stack:
            current = stack.pop()
            if current in seen:
                continue
            seen.add(current)
            children = self.children.get(current, [])
            if not children and self.nodes[current].line > best.line:
                best = self.nodes[current]
            stack.extend(child for child in children if child in self.nodes)
        return best

    def resolve(self, prefix, label):
        if prefix in self.nodes:
            return self.nodes[prefix]
        matches = {node.id: node for node in self.order if node.id.startswith(prefix)}
        if not matches:
            raise UsageError(f"no {label} id starts with {clip(prefix, ID_CHARS)!r}")
        if len(matches) > 1:
            rows = [
                f"{clip(node.id, ID_CHARS)}  line {node.line}  {node.type}"
                for node in list(matches.values())[:MAX_LISTED]
            ]
            raise UsageError(
                f"{label} id {prefix!r} is ambiguous: {len(matches)} entries match",
                rows,
            )
        return next(iter(matches.values()))


def build_tree(session, warnings, visit=None):
    tree = Tree(session, warnings)
    for record in iter_records(session, warn_problem(warnings, session)):
        tree.add(record)
        if visit:
            visit(record)
    return tree
