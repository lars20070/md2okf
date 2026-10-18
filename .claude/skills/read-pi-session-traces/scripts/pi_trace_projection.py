"""Allowlisted Pi trace projections, searchable fields, and rendering."""

from __future__ import annotations

import json

from pi_trace_core import ID_CHARS, clip, field_names, is_number, shape, text_value

KNOWN_TYPES = {
    "message",
    "model_change",
    "thinking_level_change",
    "session_info",
    "compaction",
    "branch_summary",
    "custom",
    "custom_message",
    "label",
}
KNOWN_ROLES = {"user", "assistant", "toolResult", "bashExecution", "custom"}
KNOWN_BLOCKS = {"text", "thinking", "toolCall", "image"}
TOKEN_FIELDS = (
    "input",
    "output",
    "cacheRead",
    "cacheWrite",
    "reasoning",
    "totalTokens",
)
COST_FIELDS = ("input", "output", "cacheRead", "cacheWrite", "total")


def scalar(value, limit):
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, str):
        return clip(value, limit)
    return shape(value)


def project_usage(usage):
    if not isinstance(usage, dict):
        return None
    result = {key: usage[key] for key in TOKEN_FIELDS if is_number(usage.get(key))}
    cost = usage.get("cost")
    if isinstance(cost, dict):
        result["cost"] = {
            key: cost[key] for key in COST_FIELDS if is_number(cost.get(key))
        }
    return result


def _blocks(content):
    return content if isinstance(content, list) else []


def _block(block, chars, thinking, tools):
    if not isinstance(block, dict):
        return {"type": None, "value": type(block).__name__}
    block_type = block.get("type")
    if block_type == "text":
        return {"type": "text", "text": clip(text_value(block.get("text")), chars)}
    if block_type == "image":
        data = block.get("data")
        length = len(data) if isinstance(data, str) else 0
        return {
            "type": "image",
            "mimeType": scalar(block.get("mimeType"), 100),
            "base64Chars": length,
            "approxBytes": length * 3 // 4,
        }
    if block_type == "thinking":
        value = block.get("thinking")
        value = value if isinstance(value, str) else ""
        if block.get("redacted") is True:
            return {"type": "thinking", "redacted": True}
        if thinking:
            return {"type": "thinking", "thinking": clip(value, chars)}
        return {"type": "thinking", "chars": len(value), "hidden": True}
    if block_type == "toolCall":
        result = {
            "type": "toolCall",
            "id": scalar(block.get("id"), ID_CHARS),
            "name": scalar(block.get("name"), 200),
        }
        if tools:
            result["arguments"] = clip(
                json.dumps(block.get("arguments"), ensure_ascii=False), chars
            )
        return result
    return {"type": scalar(block_type, 100), "fields": field_names(block)}


def _content(content, chars, thinking, tools):
    if isinstance(content, str):
        return [{"type": "text", "text": clip(content, chars)}]
    return [_block(block, chars, thinking, tools) for block in _blocks(content)]


def _details(value, chars):
    result = shape(value)
    if isinstance(value, dict):
        truncation = value.get("truncation")
        if isinstance(truncation, dict) and isinstance(
            truncation.get("truncated"), bool
        ):
            result["truncated"] = truncation["truncated"]
        path = value.get("fullOutputPath")
        if isinstance(path, str):
            result["fullOutputPath"] = clip(path, chars)
    return result


def project_entry(record, chars, thinking=False, tools=True):
    """Project only known-safe fields; unknown structures become metadata."""
    obj = record.obj
    entry_type = obj.get("type")
    result = {
        "kind": "entry",
        "id": scalar(obj.get("id"), ID_CHARS),
        "parentId": scalar(obj.get("parentId"), ID_CHARS),
        "line": record.line,
        "timestamp": scalar(obj.get("timestamp"), 100),
        "type": scalar(entry_type, 100),
    }
    if entry_type == "message" and isinstance(obj.get("message"), dict):
        msg = obj["message"]
        role = msg.get("role")
        result["role"] = scalar(role, 100)
        if role == "user":
            result["content"] = _content(msg.get("content"), chars, thinking, tools)
        elif role == "assistant":
            result["provider"] = scalar(msg.get("provider"), 200)
            result["model"] = scalar(msg.get("model"), 200)
            result["stopReason"] = scalar(msg.get("stopReason"), 100)
            if isinstance(msg.get("errorMessage"), str):
                result["errorMessage"] = clip(msg["errorMessage"], chars)
            result["content"] = [
                _block(block, chars, thinking, tools)
                for block in _blocks(msg.get("content"))
            ]
            usage = project_usage(msg.get("usage"))
            if usage is not None:
                result["usage"] = usage
        elif role == "toolResult":
            result["toolName"] = scalar(msg.get("toolName"), 200)
            result["toolCallId"] = scalar(msg.get("toolCallId"), ID_CHARS)
            result["isError"] = msg.get("isError") is True
            if tools:
                result["content"] = _content(msg.get("content"), chars, thinking, tools)
                if msg.get("details") is not None:
                    result["details"] = _details(msg["details"], chars)
                usage = project_usage(msg.get("usage"))
                if usage is not None:
                    result["usage"] = usage
        elif role == "bashExecution":
            result["command"] = clip(text_value(msg.get("command")), chars)
            for key in ("exitCode", "cancelled", "truncated", "excludeFromContext"):
                if key in msg:
                    result[key] = scalar(msg[key], 100)
            if isinstance(msg.get("fullOutputPath"), str):
                result["fullOutputPath"] = clip(msg["fullOutputPath"], chars)
            if tools:
                result["output"] = clip(text_value(msg.get("output")), chars)
        elif role == "custom":
            result["customType"] = scalar(msg.get("customType"), 200)
            result["display"] = scalar(msg.get("display"), 100)
            result["content"] = _content(msg.get("content"), chars, thinking, tools)
            if msg.get("details") is not None:
                result["details"] = shape(msg["details"])
        else:
            result["fields"] = field_names(msg)
            result["size"] = record.size
    elif entry_type == "message":
        result["fields"] = field_names(obj)
        result["size"] = record.size
    elif entry_type == "model_change":
        result["provider"] = scalar(obj.get("provider"), 200)
        result["modelId"] = scalar(obj.get("modelId"), 200)
    elif entry_type == "thinking_level_change":
        result["thinkingLevel"] = scalar(obj.get("thinkingLevel"), 100)
    elif entry_type == "session_info":
        result["name"] = scalar(obj.get("name"), chars)
    elif entry_type in ("compaction", "branch_summary"):
        result["summary"] = clip(text_value(obj.get("summary")), chars)
        key = "firstKeptEntryId" if entry_type == "compaction" else "fromId"
        result[key] = scalar(obj.get(key), ID_CHARS)
        if entry_type == "compaction":
            result["tokensBefore"] = scalar(obj.get("tokensBefore"), 100)
        usage = project_usage(obj.get("usage"))
        if usage is not None:
            result["usage"] = usage
        if obj.get("details") is not None:
            result["details"] = shape(obj["details"])
    elif entry_type == "custom":
        result["customType"] = scalar(obj.get("customType"), 200)
        if obj.get("data") is not None:
            result["data"] = shape(obj["data"])
    elif entry_type == "custom_message":
        result["customType"] = scalar(obj.get("customType"), 200)
        result["display"] = scalar(obj.get("display"), 100)
        result["content"] = _content(obj.get("content"), chars, thinking, tools)
        if obj.get("details") is not None:
            result["details"] = shape(obj["details"])
    elif entry_type == "label":
        result["targetId"] = scalar(obj.get("targetId"), ID_CHARS)
        result["label"] = scalar(obj.get("label"), chars)
    else:
        result["fields"] = field_names(obj)
        result["size"] = record.size
    return result


def searchable_fields(record, include_thinking=False):
    """Yield (field, text) pairs from the same safe allowlist used for output."""
    obj = record.obj
    entry_type = obj.get("type")
    if entry_type == "message" and isinstance(obj.get("message"), dict):
        msg = obj["message"]
        role = msg.get("role")
        for key in ("provider", "model", "responseModel", "toolName"):
            if isinstance(msg.get(key), str):
                yield key, msg[key]
        if isinstance(msg.get("errorMessage"), str):
            yield "errorMessage", msg["errorMessage"]
        if role == "bashExecution":
            for key in ("command", "output"):
                if isinstance(msg.get(key), str):
                    yield key, msg[key]
        content = msg.get("content")
    elif entry_type == "custom_message":
        content = obj.get("content")
    else:
        content = None
    if isinstance(content, str):
        yield "content", content
    for block in _blocks(content):
        if not isinstance(block, dict):
            continue
        block_type = block.get("type")
        if block_type == "text" and isinstance(block.get("text"), str):
            yield "text", block["text"]
        elif (
            block_type == "thinking"
            and include_thinking
            and isinstance(block.get("thinking"), str)
        ):
            yield "thinking", block["thinking"]
        elif block_type == "toolCall":
            if isinstance(block.get("name"), str):
                yield "toolName", block["name"]
            yield "arguments", json.dumps(block.get("arguments"), ensure_ascii=False)
    for key in (
        "provider",
        "modelId",
        "thinkingLevel",
        "name",
        "summary",
        "customType",
        "label",
    ):
        if isinstance(obj.get(key), str):
            yield key, obj[key]


def excerpt(value, start, end, limit=200):
    left = max(0, start - limit // 2)
    right = min(len(value), max(end, start + 1) + limit // 2)
    text = " ".join(value[left:right].split())
    return clip(text, limit)


def _usage_text(usage):
    bits = []
    if is_number(usage.get("totalTokens")):
        bits.append(f"{usage['totalTokens']:,} tokens")
    cost = usage.get("cost") or {}
    if is_number(cost.get("total")):
        bits.append(f"${cost['total']:.6f}")
    return ", ".join(bits) or "recorded usage"


def render_entry(record):
    role = record.get("role")
    label = role or record.get("type")
    if role == "assistant":
        label += f" {record.get('provider')}/{record.get('model')}"
    elif role == "toolResult":
        label += f" {record.get('toolName')} [{record.get('toolCallId')}]"
    lines = [
        f"L{record.get('line')}  {record.get('id')}  {record.get('timestamp') or '-'}  {label}"
    ]
    if "errorMessage" in record:
        lines.append(f"    error: {record['errorMessage']}")
    if "command" in record:
        lines.append(f"    $ {record['command']}")
    for block in record.get("content", []):
        block_type = block.get("type")
        if block_type == "text":
            lines.extend(f"    {line}" for line in block.get("text", "").splitlines())
        elif block_type == "thinking":
            value = block.get("thinking")
            lines.append(
                f"    [thinking] {value}"
                if value is not None
                else f"    [thinking hidden: {block.get('chars', 0)} chars]"
            )
        elif block_type == "toolCall":
            tail = f" {block['arguments']}" if "arguments" in block else ""
            lines.append(f"    -> {block.get('name')} [{block.get('id')}]{tail}")
        elif block_type == "image":
            lines.append(
                f"    [image {block.get('mimeType')}, ~{block.get('approxBytes')} bytes]"
            )
        else:
            lines.append(f"    [{block_type} block; fields: {block.get('fields', [])}]")
    if "output" in record:
        lines.extend(f"    {line}" for line in record["output"].splitlines())
    if "summary" in record:
        lines.append(f"    summary: {record['summary']}")
    if "usage" in record:
        lines.append(f"    usage: {_usage_text(record['usage'])}")
    if "fields" in record:
        lines.append(f"    fields: {', '.join(record['fields'])} (values not shown)")
    if "branchPoint" in record:
        point = record["branchPoint"]
        lines.append(f"    branch point: other children {', '.join(point['others'])}")
    if "context" in record:
        lines.append(f"    context: {record['context']}")
    return "\n".join(lines) + "\n"


def render_text(record):
    kind = record.get("kind")
    if kind == "entry":
        return render_entry(record)
    if kind == "session":
        if "counts" in record:
            return (
                f"{record.get('id')}  {record.get('entries')} entries  {record.get('path')}\n"
                f"    prompts={record.get('prompts')} leaves={record.get('tree', {}).get('leafCount')}"
                f" models={record.get('models')}\n"
            )
        fork = (
            f" fork of {record['parentSession']}" if record.get("parentSession") else ""
        )
        return f"{record.get('id')}  {record.get('created') or '-'}  {record.get('cwd') or '-'}{fork}\n    {record.get('path')}\n"
    if kind == "hit":
        return (
            f"{record.get('session')} L{record.get('line')} {record.get('entryId')}"
            f" {record.get('field')}: {record.get('excerpt')}\n"
        )
    if kind == "warning":
        where = f"{record.get('path')}"
        if record.get("line") is not None:
            where += f":{record['line']}"
        return f"warning: {where}: {record.get('message')}\n"
    if kind == "summary":
        fields = [f"{key}={value}" for key, value in record.items() if key != "kind"]
        return "-- " + " ".join(fields) + "\n"
    return json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n"


def render_json(record):
    return json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n"
