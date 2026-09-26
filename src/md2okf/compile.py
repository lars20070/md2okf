"""Document resolution and the Ralph loop.

The prompts, the loop, the cap and `merkleokf --nolog -L 0` as the convergence
check are carried over from the retired scripts/compile-okf.sh (see the git
history for the original, and .claude/plans/interface-plan.md for why each
rule is what it is).
"""

from __future__ import annotations

import re
import sys
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from md2okf import sandbox, workbench

if TYPE_CHECKING:
    from md2okf.agents import Agent

DEFAULT_MAX_ITERATIONS = 10

# The first-turn prompt is the agent's own (Agent.compile_prompt): each runtime
# activates the compile procedure its kit installs in its own way. This is
# appended on Ralph loop iterations after the first, for every agent, so it
# knows it may be resuming unfinished work rather than starting the document
# over.
CONTINUATION_PROMPT = (
    "This is a follow-up pass on this document: the wiki may already hold "
    "partial work from a previous pass. Compare the source against what is "
    "on disk and continue at the first gap -- do not start over."
)

_HASH_RE = re.compile(r"^[0-9a-f]+$")

# How much of the agent's raw output to fold into a CompileError on a failed turn.
# Bounded so one runaway session can't blow up an error message, generous
# enough that the actual cause (a traceback, sbx's own diagnostic text) is
# almost always still in view.
_DIAGNOSTIC_TAIL_LINES = 20


def _diagnostic_tail(raw_lines: list[str]) -> str:
    """The last few non-JSON lines, for folding into a failure message.

    The agent's own protocol events are JSON objects and mostly say nothing
    useful about why a run died; what does is whatever arrived on stderr in
    plain text (a traceback, an sbx diagnostic), merged into the same stream.
    Keeping only those makes the message the cause rather than a wall of
    envelopes. A protocol event that *does* state the cause reaches the
    message separately, as Event.failure.
    """
    meaningful = [line for line in raw_lines if line.strip() and not line.lstrip().startswith("{")]
    return "\n".join(meaningful[-_DIAGNOSTIC_TAIL_LINES:])


def _failure_message(agent: Agent, returncode: int | None, failure: str | None, raw_lines: list[str]) -> str:
    """One failed turn, described: how it ended, then the protocol's own reason, then plain-text context."""
    status = f"{agent.name} exited {returncode}" if returncode != 0 else f"{agent.name} reported a failed turn"
    detail = [part for part in (failure, _diagnostic_tail(raw_lines)) if part]
    return f"{status}: " + "\n".join(detail) if detail else status


class UsageError(Exception):
    """A problem decided before any work starts -- exit 2."""


class CompileError(Exception):
    """A run failure once compiling has started -- exit 1."""

    def __init__(self, message: str, *, document: str | None = None) -> None:
        """Fold `document` into the message itself, so naming it is not optional.

        str(exc) is what every caller actually prints; a document recorded
        only on a separate attribute is a document that silently never
        reaches the user, which is exactly what the plan's "exit 1 naming
        the document" contract requires.
        """
        self.document = document
        super().__init__(f"{message} ({document})" if document else message)


@dataclass(frozen=True)
class Document:
    """One document to compile, resolved from a CLI positional argument."""

    display: str
    """Printed verbatim in TSV rows -- the path as supplied, or "-" for stdin."""

    basename: str
    """The name it is staged under in work/md."""

    stdin: bool = False


@dataclass(frozen=True)
class Row:
    """One TSV output row: path, iterations, hash-before, hash-after."""

    path: str
    iterations: int
    hash_before: str
    hash_after: str

    def as_tsv(self) -> str:
        """Render as the one TSV line this document contributes to stdout."""
        return f"{self.path}\t{self.iterations}\t{self.hash_before}\t{self.hash_after}"


def _check_display_path(display: str) -> None:
    """A tab or newline in a TSV row's path column would corrupt the row."""
    if "\t" in display or "\n" in display:
        raise UsageError(f"path contains a tab or newline: {display!r}")


def resolve_documents(
    paths: list[str], *, stdin_is_tty: Callable[[], bool] = lambda: sys.stdin.isatty()
) -> list[Document]:
    """Resolve CLI positionals into documents, per the input contract.

    "-" or no arguments means stdin (refused on a TTY, via UsageError); a
    directory means its *.md, sorted, non-recursive; duplicate arguments are
    kept, in the order given, never de-duplicated; two different sources that
    would stage under the same basename is a UsageError.
    """
    raw_paths = paths or ["-"]
    if raw_paths.count("-") > 1:
        raise UsageError("only one '-' (stdin) may be given")

    docs: list[Document] = []
    for raw in raw_paths:
        if raw == "-":
            if stdin_is_tty():
                raise UsageError("refusing to read from a terminal; pipe input or name a file")
            docs.append(Document(display="-", basename="stdin.md", stdin=True))
            continue
        _check_display_path(raw)
        path = Path(raw)
        workbench.reject_if_unsafe(path, what="an input path")
        if path.is_dir():
            for md in sorted(path.glob("*.md")):
                # Checked individually, same as the directory argument above:
                # a symlinked or tab/newline-carrying *.md discovered inside
                # it must be rejected up front (exit 2), not surface later as
                # a staging failure or a corrupted TSV row.
                workbench.reject_if_unsafe(md, what="an input path")
                display = str(md)
                _check_display_path(display)
                docs.append(Document(display=display, basename=md.name))
        elif path.is_file():
            docs.append(Document(display=raw, basename=path.name))
        else:
            raise UsageError(f"not a file or directory: {raw}")

    seen: dict[str, str] = {}
    for doc in docs:
        if doc.basename in seen and seen[doc.basename] != doc.display:
            raise UsageError(
                f"two different inputs would both stage as {doc.basename!r}: "
                f"{seen[doc.basename]!r} and {doc.display!r}"
            )
        seen[doc.basename] = doc.display

    if not docs:
        raise UsageError("no documents to compile")
    return docs


def stage_items(documents: Iterable[Document]) -> list[tuple[str, Path | bytes]]:
    """(basename, source) pairs for workbench.stage_inputs, reading stdin now."""
    items: list[tuple[str, Path | bytes]] = []
    for doc in documents:
        items.append((doc.basename, sys.stdin.buffer.read()) if doc.stdin else (doc.basename, Path(doc.display)))
    return items


def _parse_hash(output: str) -> str:
    lines = output.splitlines()
    if len(lines) < 3 or not lines[2].split():
        raise CompileError(f"merkleokf produced no root row: {output!r}")
    digest = lines[2].split()[0]
    if not _HASH_RE.match(digest):
        raise CompileError(f"merkleokf produced a malformed hash: {digest!r}")
    return digest


def wiki_root_hash(name: str, work_okf: Path) -> str:
    """The wiki root's hash, validated -- a missing or malformed hash is never convergence."""
    result = sandbox.exec_capture(name, ["merkleokf", "--nolog", "-L", "0", str(work_okf)])
    if result.returncode != 0:
        raise CompileError(f"merkleokf failed: {result.stderr.strip()}")
    return _parse_hash(result.stdout)


def compile_document(
    agent: Agent,
    name: str,
    doc: Document,
    wb: workbench.Workbench,
    output_dir: Path,
    max_iterations: int = DEFAULT_MAX_ITERATIONS,
    *,
    on_progress: Callable[[str], None] | None = None,
    on_event: Callable[[str], None] | None = None,
) -> Row:
    """Run the Ralph loop for one document with `agent`, in sandbox `name`.

    Re-runs the agent on the same document until merkleokf --nolog -L 0 reports an
    unchanged wiki root hash, capped at max_iterations. Mirrors work_okf out
    to output_dir after every iteration, so an interruption leaves the last
    completed pass on disk. A hash-stable first pass is convergence, not
    failure -- iterations=1, equal hashes.
    """
    document_path = wb.work_md / doc.basename
    hash_before = wiki_root_hash(name, wb.work_okf)
    had_markdown_before = workbench.has_markdown(wb.work_okf)

    iteration = 0
    current_hash = hash_before
    while True:
        iteration += 1
        if iteration > max_iterations:
            raise CompileError(f"hit {max_iterations} iterations without converging", document=doc.display)
        if on_progress is not None:
            on_progress(f"Compiling document {doc.display} (iteration {iteration})")

        prompt = agent.compile_prompt(document_path)
        if iteration > 1:
            prompt = f"{prompt} {CONTINUATION_PROMPT}"

        stream = sandbox.exec_stream(name, agent.compile_args(prompt))
        tool_calls = 0
        failure: str | None = None
        raw_lines: list[str] = []
        try:
            for event in agent.protocol.process(stream):
                raw_lines.append(event.raw)
                if event.is_tool_call:
                    tool_calls += 1
                if event.failure is not None:
                    failure = event.failure
                # The protocol has already decided what is worth showing:
                # rendered tool calls and assistant prose, plus any non-JSON
                # diagnostic. Protocol events we do not render come back as
                # None and are dropped here.
                if on_event is not None and event.display and event.display.strip():
                    on_event(event.display)
        finally:
            # Reached on Ctrl-C too, so an interrupted run does not leave the
            # local `sbx exec` conduit behind. mirror_out() is below this
            # point, which is what keeps a half-finished iteration from ever
            # reaching -o DIR.
            stream.close()
        # Failure first, whatever the tool-call count: a turn that did work
        # and then reported a terminal error must neither pass as a success
        # nor be misreported as "no tool calls". Either signal is enough; an
        # agent can report a failure and still exit 0.
        if failure is not None or stream.returncode != 0:
            raise CompileError(_failure_message(agent, stream.returncode, failure, raw_lines), document=doc.display)
        if tool_calls == 0:
            raise CompileError(
                f"{agent.name} session made no tool calls -- it did not follow the skill", document=doc.display
            )

        try:
            workbench.mirror_out(wb.work_okf, output_dir)
        except workbench.WorkbenchError as exc:
            # Re-raised as a CompileError, not left as a WorkbenchError: the
            # caller's per-document loop only catches CompileError, and a
            # failed mirror-out is a failed run for *this* document (exit 1),
            # not a setup problem decided before any work started.
            raise CompileError(str(exc), document=doc.display) from exc

        next_hash = wiki_root_hash(name, wb.work_okf)
        if on_progress is not None:
            on_progress(f"{current_hash} -> {next_hash}")
        if next_hash == current_hash:
            break
        current_hash = next_hash

    if not had_markdown_before and not workbench.has_markdown(wb.work_okf):
        raise CompileError("the wiki is still empty after compiling", document=doc.display)

    return Row(path=doc.display, iterations=iteration, hash_before=hash_before, hash_after=current_hash)
