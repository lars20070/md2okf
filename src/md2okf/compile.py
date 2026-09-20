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

from md2okf import events, sandbox, workbench

DEFAULT_MAX_ITERATIONS = 10

COMPILE_PROMPT = (
    "Load the compile-okf skill: read ~/.pi/agent/skills/compile-okf/SKILL.md, "
    "then follow it to compile {document} directly into the workspace root. "
    "You are already in the OKF wiki; never create an okf/ child directory."
)
# Appended on Ralph loop iterations after the first, so Pi knows it may be
# resuming unfinished work rather than starting the document over.
CONTINUATION_PROMPT = (
    "This is a follow-up pass on this document: the wiki may already hold "
    "partial work from a previous pass. Compare the source against what is "
    "on disk and continue at the first gap -- do not start over."
)

_HASH_RE = re.compile(r"^[0-9a-f]+$")

# How much of pi's raw output to fold into a CompileError on a non-zero exit.
# Bounded so one runaway session can't blow up an error message, generous
# enough that the actual cause (a traceback, sbx's own diagnostic text) is
# almost always still in view.
_DIAGNOSTIC_TAIL_LINES = 20


def _diagnostic_tail(raw_lines: list[str]) -> str:
    """The last few non-JSON lines, for folding into a failure message.

    Pi's own protocol events are JSON objects and say nothing useful about
    why a run died; what does is whatever arrived on stderr in plain text
    (a traceback, an sbx diagnostic), merged into the same stream. Keeping
    only those makes the message the cause rather than a wall of envelopes.
    """
    meaningful = [line for line in raw_lines if line.strip() and not line.lstrip().startswith("{")]
    return "\n".join(meaningful[-_DIAGNOSTIC_TAIL_LINES:])


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
    name: str,
    doc: Document,
    wb: workbench.Workbench,
    output_dir: Path,
    max_iterations: int = DEFAULT_MAX_ITERATIONS,
    *,
    on_progress: Callable[[str], None] | None = None,
    on_event: Callable[[str], None] | None = None,
) -> Row:
    """Run the Ralph loop for one document.

    Re-runs Pi on the same document until merkleokf --nolog -L 0 reports an
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

        prompt = COMPILE_PROMPT.format(document=document_path)
        if iteration > 1:
            prompt = f"{prompt} {CONTINUATION_PROMPT}"

        stream = sandbox.exec_stream(name, ["pi", "--mode", "json", prompt])
        tool_calls = 0
        raw_lines: list[str] = []
        try:
            for line, display, is_tool_call in events.process(stream):
                raw_lines.append(line)
                if is_tool_call:
                    tool_calls += 1
                # events.process() has already decided what is worth showing:
                # rendered tool calls and assistant prose, plus any non-JSON
                # diagnostic. Protocol events we do not render come back as
                # None and are dropped here.
                if on_event is not None and display and display.strip():
                    on_event(display)
        finally:
            # Reached on Ctrl-C too, so an interrupted run does not leave the
            # local `sbx exec` conduit behind. mirror_out() is below this
            # point, which is what keeps a half-finished iteration from ever
            # reaching -o DIR.
            stream.close()
        if stream.returncode != 0:
            tail = _diagnostic_tail(raw_lines)
            detail = f": {tail}" if tail else ""
            raise CompileError(f"pi exited {stream.returncode}{detail}", document=doc.display)
        if tool_calls == 0:
            raise CompileError("pi session made no tool calls -- it did not follow the skill", document=doc.display)

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
