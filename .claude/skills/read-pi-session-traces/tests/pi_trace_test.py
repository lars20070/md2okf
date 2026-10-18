"""Manual end-to-end tests for the read-pi-session-traces CLI."""

import json
import os
import subprocess
import sys
import tempfile
import time
import unittest

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(SKILL, "scripts", "pi-trace.py")
EPOCH = 1_788_000_000


def timestamp(number):
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(EPOCH + number)) + ".000Z"


def usage(tokens, cost):
    return {
        "input": tokens - 1,
        "output": 1,
        "cacheRead": 0,
        "cacheWrite": 0,
        "reasoning": 0,
        "totalTokens": tokens,
        "cost": {
            "input": cost / 2,
            "output": cost / 2,
            "cacheRead": 0,
            "cacheWrite": 0,
            "total": cost,
        },
    }


def text(value):
    return {"type": "text", "text": value}


def tool_call(call_id, name, arguments=None):
    return {
        "type": "toolCall",
        "id": call_id,
        "name": name,
        "arguments": arguments or {},
    }


class Trace:
    def __init__(self, session_id, cwd="/work/project", parent=None):
        self.id = session_id
        self.header = {
            "type": "session",
            "version": 3,
            "id": session_id,
            "timestamp": timestamp(0),
            "cwd": cwd,
        }
        if parent:
            self.header["parentSession"] = parent
        self.entries = []
        self.last = None

    def add(self, entry_type, parent=..., entry_id=None, **fields):
        entry_id = entry_id or f"{len(self.entries) + 1:08x}"
        parent = self.last if parent is ... else parent
        entry = {
            "type": entry_type,
            "id": entry_id,
            "parentId": parent,
            "timestamp": timestamp(len(self.entries) + 1),
        }
        entry.update(fields)
        self.entries.append(entry)
        self.last = entry_id
        return entry_id

    def message(self, role, parent=..., entry_id=None, **fields):
        message = {"role": role, "timestamp": (EPOCH + len(self.entries) + 1) * 1000}
        message.update(fields)
        return self.add("message", parent, entry_id, message=message)

    def user(self, value, **kwargs):
        return self.message("user", content=[text(value)], **kwargs)

    def assistant(self, blocks, model="model-a", spend=0.5, **kwargs):
        return self.message(
            "assistant",
            content=blocks,
            provider="provider-a",
            model=model,
            usage=usage(100, spend),
            stopReason="toolUse"
            if any(b.get("type") == "toolCall" for b in blocks)
            else "stop",
            **kwargs,
        )

    def tool_result(self, call_id, name, value, spend=None, **kwargs):
        fields = {
            "toolCallId": call_id,
            "toolName": name,
            "content": [text(value)],
            "isError": False,
        }
        if spend is not None:
            fields["usage"] = usage(20, spend)
        return self.message("toolResult", **fields, **kwargs)

    def write(
        self, directory, name=None, before=(), after=(), terminated=True, mtime=0
    ):
        os.makedirs(directory, exist_ok=True)
        path = os.path.join(directory, name or f"trace_{self.id}.jsonl")
        records = list(before) + [json.dumps(self.header, ensure_ascii=False)]
        records += [json.dumps(entry, ensure_ascii=False) for entry in self.entries]
        records += list(after)
        with open(path, "w", encoding="utf-8") as stream:
            stream.write("\n".join(records) + ("\n" if terminated else ""))
        os.utime(path, (EPOCH + mtime, EPOCH + mtime))
        return path


def run(*arguments, code=0, timeout=60):
    result = subprocess.run(
        [sys.executable, SCRIPT] + [str(value) for value in arguments],
        capture_output=True,
        encoding="utf-8",
        timeout=timeout,
        check=False,
    )
    if code is not None and result.returncode != code:
        raise AssertionError(
            f"exit {result.returncode}, expected {code}\nstdout={result.stdout[-2000:]}"
            f"\nstderr={result.stderr[-2000:]}"
        )
    return result


def records(result):
    output = [json.loads(line) for line in result.stdout.splitlines()]
    assert output and output[-1]["kind"] == "summary", output
    assert sum(item["kind"] == "summary" for item in output) == 1
    return output


def kind(output, name):
    return [record for record in output if record["kind"] == name]


class TempCase(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = os.path.join(self.temporary.name, "sessions")
        self.folder = os.path.join(self.root, "--work-project--")

    def tearDown(self):
        self.temporary.cleanup()

    def simple(self, session_id="01a00000-0000-7000-8000-000000000001", mtime=0):
        trace = Trace(session_id)
        trace.user("hello")
        trace.assistant([text("world")])
        return trace, trace.write(self.folder, mtime=mtime)


class DiscoveryTests(TempCase):
    def test_recursive_discovery_header_rules_and_paging(self):
        first, first_path = self.simple("01a00000-0000-7000-8000-000000000001", mtime=1)
        second = Trace("01a00000-0000-7000-8000-000000000002")
        second.user("two")
        second_path = second.write(
            os.path.join(self.root, "--other--"),
            before=("", "not json"),
            mtime=2,
        )
        with open(os.path.join(self.folder, "not-pi.jsonl"), "w") as stream:
            stream.write('{"type":"user"}\n')
        with open(os.path.join(self.folder, "notes.txt"), "w") as stream:
            stream.write("ignored")

        output = records(run("sessions", self.root, "--limit", 1, "--json"))
        self.assertEqual(
            [item["path"] for item in kind(output, "session")], [second_path]
        )
        self.assertEqual(
            {key: output[-1][key] for key in ("total", "shown", "skip", "remaining")},
            {"total": 2, "shown": 1, "skip": 0, "remaining": 1},
        )
        self.assertEqual(output[-1]["stoppedBy"], "limit")
        rest = records(run("sessions", self.root, "--skip", 1, "--json"))
        self.assertEqual([item["path"] for item in kind(rest, "session")], [first_path])
        self.assertTrue(rest[-1]["complete"])
        self.assertEqual(first.id, kind(rest, "session")[0]["id"])

    def test_selection_exact_prefix_ambiguous_and_non_pi(self):
        self.simple("abc-one")
        self.simple("abc-two", mtime=1)
        result = run("inspect", self.root, "--session", "abc", code=2)
        self.assertIn("ambiguous", result.stderr)
        output = records(run("inspect", self.root, "--session", "abc-one", "--json"))
        self.assertEqual(kind(output, "session")[0]["id"], "abc-one")
        bad = os.path.join(self.temporary.name, "bad.jsonl")
        with open(bad, "w") as stream:
            stream.write("{}\n")
        self.assertIn("no Pi session", run("sessions", bad, code=2).stderr)


class TreeAndProjectionTests(TempCase):
    def test_branch_selection_annotations_cycles_and_orphans(self):
        trace = Trace("tree")
        root = trace.user("root")
        left = trace.user("left")
        right = trace.user("right", parent=root)
        compact = trace.add(
            "compaction",
            parent=left,
            summary="short",
            firstKeptEntryId=left,
            tokensBefore=9,
        )
        branch = trace.add("branch_summary", summary="gone", fromId=right)
        trace.user("cycle", parent="00000006", entry_id="00000006")
        trace.user("orphan", parent="missing")
        path = trace.write(self.folder)

        output = records(
            run("show", path, "--entry", root, "--leaf", branch, "--all", "--json")
        )
        entries = kind(output, "entry")
        self.assertEqual(
            [entry["id"] for entry in entries], [root, left, compact, branch]
        )
        self.assertIn(right, entries[0]["branchPoint"]["others"])
        self.assertIn("replaces older", entries[2]["context"])
        self.assertIn("abandoned-branch", entries[3]["context"])

        report = kind(records(run("inspect", path, "--json")), "session")[0]
        self.assertEqual(report["tree"]["orphanCount"], 1)
        inspected = records(run("inspect", path, "--json"))
        self.assertEqual(kind(inspected, "session")[0]["tree"]["cycleCount"], 1)
        warning_text = " ".join(item["message"] for item in kind(inspected, "warning"))
        self.assertIn("parent cycle", warning_text)
        warning_text += " " + " ".join(
            item["message"]
            for item in kind(records(run("show", path, "--json")), "warning")
        )
        self.assertIn("walk stopped", warning_text)

    def test_allowlist_images_thinking_tools_unknowns_and_long_ids(self):
        secret = "SECRET_MUST_NOT_LEAK"
        trace = Trace("projection")
        long_id = "a" * 50000
        trace.message(
            "user",
            content=[
                text("safe"),
                {"type": "image", "mimeType": "image/png", "data": secret},
            ],
        )
        trace.assistant(
            [
                {
                    "type": "thinking",
                    "thinking": "private thought",
                    "signature": secret,
                },
                tool_call("call-1", "read", {"path": "/tmp/a"}),
                {"type": "future", "payload": secret},
            ],
            entry_id=long_id,
        )
        trace.tool_result("call-1", "read", "tool output", parent=long_id)
        trace.entries[-1]["message"]["details"] = {"opaque": secret}
        trace.add("future_entry", payload=secret, usage=usage(999, 9))
        path = trace.write(self.folder)

        result = run("show", path, "--all", "--json", "--unlimited")
        self.assertNotIn(secret, result.stdout)
        output = records(result)
        image = kind(output, "entry")[0]["content"][1]
        self.assertEqual(image["base64Chars"], len(secret))
        assistant = kind(output, "entry")[1]
        self.assertTrue(assistant["content"][0]["hidden"])
        self.assertLessEqual(len(assistant["id"]), 240)
        self.assertTrue(
            any("structural id" in item["message"] for item in kind(output, "warning"))
        )
        with_thinking = run(
            "show", path, "--all", "--thinking", "--json", "--unlimited"
        )
        self.assertIn("private thought", with_thinking.stdout)
        stubs = run("show", path, "--all", "--no-tools", "--json", "--unlimited")
        self.assertNotIn("tool output", stubs.stdout)


class SearchTests(TempCase):
    def test_literal_regex_case_thinking_and_model_fields(self):
        trace = Trace("search")
        trace.user('Alpha "quoted"\nline')
        trace.assistant(
            [{"type": "thinking", "thinking": "hidden needle"}, text("Beta 123")],
            model="Model-Z",
        )
        path = trace.write(self.folder)

        literal = records(run("search", path, "alpha", "-i", "--json"))
        self.assertEqual(len(kind(literal, "hit")), 1)
        self.assertEqual(kind(literal, "hit")[0]["field"], "text")
        regex = records(run("search", path, r"Beta\s+\d+", "-e", "--json"))
        self.assertEqual(len(kind(regex, "hit")), 1)
        self.assertEqual(
            run("search", path, "hidden needle", "--json", code=1).returncode, 1
        )
        thinking = records(run("search", path, "hidden needle", "--thinking", "--json"))
        self.assertEqual(kind(thinking, "hit")[0]["field"], "thinking")
        model = records(run("search", path, "model-z", "-i", "--json"))
        self.assertEqual(kind(model, "hit")[0]["field"], "model")

    def test_count_pagination_and_safe_fields(self):
        trace = Trace("pages")
        for number in range(5):
            trace.user(f"needle {number}")
        trace.entries[0]["signature"] = "opaque-hit"
        path = trace.write(self.folder)
        output = records(
            run("search", path, "needle", "--skip", 1, "--limit", 2, "--json")
        )
        self.assertEqual([item["line"] for item in kind(output, "hit")], [3, 4])
        self.assertEqual((output[-1]["hits"], output[-1]["skipped"]), (2, 1))
        self.assertEqual(output[-1]["stoppedBy"], "limit")
        self.assertGreaterEqual(output[-1]["recordsDecoded"], 4)
        self.assertEqual(
            run("search", path, "opaque-hit", "--json", code=1).returncode, 1
        )
        self.assertEqual(run("search", path, "[", "-e", code=2).returncode, 2)


class InspectTests(TempCase):
    def test_pinned_usage_tool_correlation_counts_and_fork_warning(self):
        trace = Trace("usage", parent="parent-id")
        trace.user("prompt")
        trace.assistant([tool_call("call-1", "shell", {"cmd": "true"})], spend=0.5)
        trace.tool_result("call-1", "shell", "ok", spend=0.25)
        trace.add(
            "compaction",
            summary="summary",
            firstKeptEntryId="00000001",
            usage=usage(10, 0.125),
        )
        trace.add("usage", provider="future", model="future", usage=usage(1000, 8))
        trace.add("future_type", payload="opaque")
        path = trace.write(self.folder)
        output = records(run("inspect", path, "--json"))
        report = kind(output, "session")[0]
        self.assertEqual(report["prompts"], 1)
        self.assertEqual(report["counts"]["types"]["message"], 3)
        self.assertEqual(report["models"]["assistant"], {"provider-a/model-a": 1})
        self.assertEqual(report["tools"]["shell"]["calls"], 1)
        self.assertEqual(report["tools"]["shell"]["withoutResult"], 0)
        costs = {
            source: value["cost"]["total"]
            for source, value in report["usage"]["bySource"].items()
        }
        self.assertEqual(
            costs,
            {"conversation": 0.5, "toolExecution": 0.25, "summarization": 0.125},
        )
        self.assertNotIn("standalone", report["usage"]["bySource"])
        warnings = " ".join(item["message"] for item in kind(output, "warning"))
        self.assertIn("metadata only", warnings)
        self.assertIn("forked session", warnings)

    def test_bounded_leaves_orphans_and_session_paging(self):
        for number in range(3):
            trace = Trace(f"inspect-{number}")
            root = trace.user("root")
            for branch in range(15):
                trace.user(str(branch), parent=root)
            trace.user("orphan", parent="missing")
            trace.write(self.folder, mtime=number)
        output = records(run("inspect", self.root, "--limit", 1, "--json"))
        report = kind(output, "session")[0]
        self.assertEqual(report["tree"]["leafCount"], 16)
        self.assertEqual(len(report["tree"]["leaves"]), 10)
        self.assertEqual(report["tree"]["orphanCount"], 1)
        self.assertEqual(
            (output[-1]["total"], output[-1]["shown"], output[-1]["remaining"]),
            (3, 1, 2),
        )


class BudgetAndRobustnessTests(TempCase):
    def test_fixed_cap_json_text_item_too_large_unlimited_and_field_clipping(self):
        trace = Trace("budget")
        trace.user("x" * 30000)
        path = trace.write(self.folder)
        for json_flag in ((), ("--json",)):
            result = run("show", path, "--all", "--max-field-chars", 0, *json_flag)
            self.assertLessEqual(len(result.stdout), 20000)
            if json_flag:
                output = records(result)
                self.assertEqual(len(kind(output, "entry")), 0)
                self.assertEqual(output[-1]["stoppedBy"], "item-too-large")
            else:
                self.assertIn("stoppedBy=item-too-large", result.stdout)
        unlimited = records(
            run("show", path, "--all", "--max-field-chars", 0, "--unlimited", "--json")
        )
        self.assertEqual(len(kind(unlimited, "entry")), 1)
        self.assertIn("x" * 30000, json.dumps(unlimited[0]))
        clipped = records(run("show", path, "--all", "--max-field-chars", 10, "--json"))
        self.assertIn("clipped", clipped[0]["content"][0]["text"])

    def bulky(self, trace):
        # Four arguments clipped at 2,000 chars each keep one entry near 8,000.
        return trace.assistant(
            [
                tool_call(
                    f"call-{len(trace.entries)}-{n}", "write", {"body": "y" * 5000}
                )
                for n in range(4)
            ]
        )

    def test_show_keeps_the_anchor_and_trims_context_around_it(self):
        trace = Trace("anchor")
        order = [trace.user("go")]
        order += [self.bulky(trace) for _ in range(3)]
        answer = trace.assistant([text("final answer")])
        order.append(answer)
        path = trace.write(self.folder)

        for selector in (("--entry", answer), ()):
            result = run("show", path, *selector)
            self.assertLessEqual(len(result.stdout), 20000)
            self.assertRegex(result.stdout, rf"(?m)^L\d+  {answer}  ")
            self.assertIn(f"anchor={answer} anchorShown=True", result.stdout)
            self.assertIn("stoppedBy=output-limit", result.stdout)

            result = run("show", path, *selector, "--json")
            self.assertLessEqual(len(result.stdout), 20000)
            output = records(result)
            ids = [entry["id"] for entry in kind(output, "entry")]
            # The newest entries win: older context is dropped from the front.
            self.assertLess(len(ids), len(order))
            self.assertEqual(ids, order[-len(ids) :])
            summary = output[-1]
            self.assertEqual(
                (summary["anchor"], summary["anchorShown"]), (answer, True)
            )
            self.assertEqual(summary["stoppedBy"], "output-limit")
            self.assertEqual(summary["entriesBefore"], len(order) - len(ids))
            self.assertEqual(summary["entriesAfter"], 0)

        # Continuing backward from the first printed entry leaves no gap; only
        # that entry, the new anchor, is printed twice.
        earlier = records(
            run("show", path, "--entry", ids[0], "--before", 5, "--after", 0, "--json")
        )
        earlier_ids = [entry["id"] for entry in kind(earlier, "entry")]
        self.assertEqual(earlier_ids[-1], ids[0])
        joined = earlier_ids[:-1] + ids
        self.assertEqual(joined, order[-len(joined) :])

    def test_show_grows_past_a_side_that_no_longer_fits(self):
        trace = Trace("after")
        order = [trace.user("go"), trace.assistant([text("picked")])]
        picked = order[-1]
        order += [self.bulky(trace) for _ in range(4)]
        path = trace.write(self.folder)

        output = records(run("show", path, "--entry", picked, "--json"))
        ids = [entry["id"] for entry in kind(output, "entry")]
        self.assertLess(len(ids), len(order))
        self.assertEqual(ids, order[: len(ids)])
        summary = output[-1]
        self.assertEqual((summary["anchor"], summary["anchorShown"]), (picked, True))
        self.assertEqual(
            (summary["entriesBefore"], summary["entriesAfter"]), (0, 6 - len(ids))
        )

        later = records(
            run("show", path, "--entry", ids[-1], "--before", 0, "--after", 5, "--json")
        )
        later_ids = [entry["id"] for entry in kind(later, "entry")]
        self.assertEqual(later_ids[0], ids[-1])
        joined = ids + later_ids[1:]
        self.assertEqual(joined, order[: len(joined)])

    def test_show_anchor_too_large_and_empty_session(self):
        trace = Trace("huge")
        trace.user("small")
        huge = trace.user("x" * 30000)
        last = trace.user("after")
        path = trace.write(self.folder)

        result = run("show", path, "--entry", huge, "--max-field-chars", 0)
        self.assertLessEqual(len(result.stdout), 20000)
        self.assertIn(f"anchor={huge} anchorShown=False", result.stdout)
        self.assertIn("stoppedBy=item-too-large", result.stdout)
        output = records(
            run("show", path, "--entry", huge, "--max-field-chars", 0, "--json")
        )
        self.assertEqual(kind(output, "entry"), [])
        self.assertEqual(output[-1]["stoppedBy"], "item-too-large")
        self.assertEqual(
            (output[-1]["anchor"], output[-1]["anchorShown"]), (huge, False)
        )

        # The tail keeps its leaf; the oversized entry before it stops that
        # side, so the small entry beyond it is not printed out of order.
        output = records(run("show", path, "--max-field-chars", 0, "--json"))
        self.assertEqual([entry["id"] for entry in kind(output, "entry")], [last])
        self.assertEqual(output[-1]["stoppedBy"], "output-limit")

        empty = Trace("empty").write(self.folder)
        summary = records(run("show", empty, "--json"))[-1]
        self.assertEqual((summary["entriesBefore"], summary["entriesAfter"]), (0, 0))
        self.assertEqual((summary["anchor"], summary["anchorShown"]), (None, False))

    def test_malformed_partial_records_and_argument_errors(self):
        trace = Trace("broken")
        trace.user("good")
        path = trace.write(
            self.folder, after=("{bad", '{"type":"message"}'), terminated=False
        )
        output = records(run("inspect", path, "--json"))
        warnings = [item["message"] for item in kind(output, "warning")]
        self.assertTrue(any("unparseable" in message for message in warnings))
        self.assertTrue(any("no newline" in message for message in warnings))
        self.assertEqual(run("show", path, "--line", 1, code=2).returncode, 2)
        self.assertEqual(run("sessions", path, "--skip", "nope", code=2).returncode, 2)
        self.assertEqual(
            run("show", path, "--format", "markdown", code=2).returncode, 2
        )
        self.assertEqual(
            run("show", path, "--max-output-chars", 1, code=2).returncode, 2
        )

    def test_broken_pipe_and_twenty_thousand_entries(self):
        trace = Trace("large")
        for number in range(20000):
            trace.user(f"prompt {number}")
        path = trace.write(self.folder)
        started = time.monotonic()
        output = records(run("inspect", path, "--json", timeout=60))
        self.assertEqual(kind(output, "session")[0]["entries"], 20000)
        self.assertLess(time.monotonic() - started, 20)

        process = subprocess.Popen(
            [sys.executable, SCRIPT, "show", path, "--all", "--unlimited"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        process.stdout.read(1)
        process.stdout.close()
        stderr = process.stderr.read().decode()
        process.stderr.close()
        self.assertEqual(process.wait(timeout=10), 0, stderr)
        self.assertEqual(stderr, "")


if __name__ == "__main__":
    print(f"# pi_trace_test.py under Python {sys.version.split()[0]}")
    unittest.main(verbosity=2)
