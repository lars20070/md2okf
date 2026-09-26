"""The md2okf command.

Compiles Markdown into an OKF wiki with a coding agent (Pi by default, chosen
by MD2OKF_AGENT), via a sandboxed sbx runtime. See
.claude/plans/interface-plan.md and .claude/plans/generalise-agent-framework.md.
"""

from __future__ import annotations

import argparse
import shlex
import sys
from pathlib import Path

from md2okf import __version__, agents, resources, sandbox, workbench
from md2okf import compile as compile_mod

# One string, two call sites (the compile path and the interactive one), so the
# two cannot drift into saying different things about the same condition.
LOCK_HELD_MESSAGE = "md2okf: another md2okf run is using the sandbox; try again later"

# With --shell/--agent only --fresh still means something: the sandbox is
# entered, not driven. The rest are refused rather than ignored, because
# `--shell -o mywiki` reads like "mount this output", and quietly doing nothing
# with it would mislead more than saying no does.
_COMPILE_ONLY_OPTIONS = (
    ("output", "-o"),
    ("spec", "--spec"),
    ("n", "-n"),
    ("quiet", "-q"),
    ("verbose", "-v"),
    ("dry_run", "--dry-run"),
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="md2okf",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Compile Markdown into an OKF wiki with a coding agent (Pi by default).",
        # Held to 79 columns so it renders in a standard terminal; the epilog is
        # printed verbatim. These are the only four variables a user of the
        # command can set -- MD2OKF_STATE_DIR and WORKDIR are ours to inject.
        epilog=f"""\
Environment:
  MD2OKF_AGENT        agent framework to run: {", ".join(sorted(agents.AGENTS))}. Each agent
                      has its own sandbox (md2okf-<agent>) and workbench.
                      (default: {agents.DEFAULT_AGENT})
  OPENROUTER_API_KEY  required for pi, but read from `sbx secret`, never from
                      this environment
  XDG_STATE_HOME      session state and the run workbench. Absolute paths
                      only; a relative value counts as unset.
                      (default: ~/.local/state)
  SPEC_MD             spec the frontmatter guard reads when checking a wiki
                      outside this repository
""",
    )
    parser.add_argument(
        "paths", nargs="*", metavar="FILE|DIR", help="Markdown files or folders; '-' or none means stdin"
    )
    parser.add_argument("-o", "--output", default="okf", metavar="DIR", help="wiki output directory (default: ./okf)")
    parser.add_argument("--spec", metavar="FILE", help="OKF spec file (default: the bundled SPEC.md)")
    parser.add_argument(
        "-n",
        type=int,
        default=compile_mod.DEFAULT_MAX_ITERATIONS,
        metavar="N",
        help="max Ralph loop iterations per document (default: 10)",
    )
    parser.add_argument("--fresh", action="store_true", help="recreate the sandbox even if it could be reused")
    parser.add_argument("--dry-run", action="store_true", help="resolve and print what would run; do nothing paid")
    interactive = parser.add_mutually_exclusive_group()
    interactive.add_argument(
        "--shell", action="store_true", help="open an interactive shell in the sandbox"
    )
    interactive.add_argument(
        "--agent", action="store_true", help="open an interactive agent session in the sandbox"
    )
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument(
        "-q", "--quiet", action="store_true", help="suppress progress and TSV rows (fatal errors still print)"
    )
    verbosity.add_argument("-v", "--verbose", action="store_true", help="also show the agent's tool calls and prose")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def _resolve_inputs(
    args: argparse.Namespace, agent: agents.Agent
) -> tuple[list[compile_mod.Document], Path, Path, workbench.Workbench] | int:
    """Everything decided before any work starts. Returns exit code 2 on failure."""
    try:
        if args.n < 1:
            raise compile_mod.UsageError(f"-n must be at least 1 (got {args.n})")
        documents = compile_mod.resolve_documents(args.paths)
        spec_path = Path(args.spec) if args.spec else resources.spec_md()
        workbench.reject_if_unsafe(spec_path, what="--spec")
        if not spec_path.is_file():
            raise compile_mod.UsageError(f"--spec is not a file: {spec_path}")

        output_dir = Path(args.output)
        if not workbench.is_adoptable_output(output_dir):
            raise compile_mod.UsageError(
                f"-o {output_dir} is not empty and is not a recognised OKF bundle root; refusing to adopt it"
            )

        wb = workbench.Workbench.default(agent.name)
        overlap_paths = [Path(raw) for raw in args.paths if raw != "-"]
        overlap_paths += [spec_path, output_dir, wb.root]
        workbench.check_no_overlap(overlap_paths)
    except (compile_mod.UsageError, workbench.WorkbenchError, resources.ResourcesError) as exc:
        print(f"md2okf: {exc}", file=sys.stderr)
        return 2
    return documents, spec_path, output_dir, wb


def _print_dry_run(
    agent: agents.Agent,
    documents: list[compile_mod.Document],
    spec_path: Path,
    output_dir: Path,
    wb: workbench.Workbench,
) -> None:
    print("md2okf --dry-run: resolving only -- no sandbox will be created, nothing paid will run.")
    print(f"  agent:  {agent.name}")
    print(f"  spec:   {spec_path}")
    print(f"  output: {output_dir}")
    print("  documents:")
    for doc in documents:
        print(f"    {doc.display} -> work/md/{doc.basename}")
    print("  mounts:")
    for mount in wb.mounts():
        print(f"    {mount.as_arg()}")
    print("  commands:")
    print(f"    {_format_sbx_run(agent, wb)}")
    for doc in documents:
        print(f"    {_format_sbx_exec_agent(agent, wb, doc)}")


def _format_sbx_run(agent: agents.Agent, wb: workbench.Workbench) -> str:
    """The `sbx run` line that would create the sandbox, if one is needed.

    Whether it actually runs depends on sandbox reuse -- a live decision
    --dry-run must not make (that would mean querying `sbx`). This shows
    what *would* run if a (re)creation turns out to be necessary.
    """
    mount_args = " ".join(mount.as_arg() for mount in wb.mounts())
    return (
        f"sbx run --detached --name {workbench.sandbox_name(agent.name)} "
        f"-e MD2OKF_STATE_DIR={wb.root} {resources.kit_dir(agent.name)} {mount_args}"
    )


def _format_sbx_exec_agent(agent: agents.Agent, wb: workbench.Workbench, doc: compile_mod.Document) -> str:
    """The first-iteration `sbx exec ... <agent>` line for one document.

    Later Ralph loop iterations append the continuation prompt; --dry-run
    shows only the first, since how many would actually run is exactly
    what compiling determines.
    """
    prompt = agent.compile_prompt(wb.work_md / doc.basename)
    return f"sbx exec {workbench.sandbox_name(agent.name)} -- {shlex.join(agent.compile_args(prompt))}"


def _ensure_sandbox(
    wb: workbench.Workbench, agent: agents.Agent, args: argparse.Namespace, *, credentials_optional: bool = False
) -> int | None:
    """Reuse or (re)create the sandbox. Returns an exit code on failure, else None.

    With `credentials_optional` (only --shell), a credential that is not ready
    is a warning rather than a refusal: the sandbox itself is ready by then,
    and a diagnostic shell is most needed exactly when credentials are broken.
    """
    try:
        workbench.ensure_sandbox(wb, agent, fresh=args.fresh)
    except workbench.CredentialNotReadyError as exc:
        if not credentials_optional:
            print(f"md2okf: {exc}", file=sys.stderr)
            return 2
        print(f"md2okf: warning: {exc}", file=sys.stderr)
    except (
        # The base, not just UnownedSandboxError and CredentialNotReadyError:
        # ensure_sandbox also stages the tooling, and a staging failure there
        # arrives as a plain WorkbenchError. Catching only the two subclasses
        # let that one through as a traceback.
        workbench.WorkbenchError,
        sandbox.SandboxError,
        resources.ResourcesError,
    ) as exc:
        print(f"md2okf: {exc}", file=sys.stderr)
        return 2
    return None


def _reject_compile_only_options(args: argparse.Namespace, parser: argparse.ArgumentParser, flag: str) -> int | None:
    """Refuse the compile options an interactive session cannot honour.

    Compares each value against the parser's own default rather than tracking
    which options were explicitly given, which would mean a custom action for
    every one of them. A user who spells out the default anyway (`-o okf`) is
    not caught, which costs nothing: naming the default changes neither what
    runs nor what they see.
    """
    if args.paths:
        print(f"md2okf: {flag} takes no FILE|DIR arguments", file=sys.stderr)
        return 2
    for attr, option in _COMPILE_ONLY_OPTIONS:
        if getattr(args, attr) != parser.get_default(attr):
            print(f"md2okf: {option} has no meaning with {flag}", file=sys.stderr)
            return 2
    return None


def _enter_sandbox(args: argparse.Namespace, parser: argparse.ArgumentParser, agent: agents.Agent) -> int:  # noqa: RET503
    """Make the sandbox current, then hand this terminal over to it.

    Returns an exit code only on refusal: on success exec_interactive replaces
    this process and nothing below it runs.

    LockHeld and UnsafeLockFile are caught here rather than reusing main()'s
    handlers, which sit inside the compile-path `try` that this path never
    enters -- a held lock would otherwise surface as a traceback.

    The RET503 waiver is that missing final return: exec_interactive is
    annotated NoReturn, which ruff does not follow across the module boundary.
    """
    flag = "--shell" if args.shell else "--agent"

    refusal = _reject_compile_only_options(args, parser, flag)
    if refusal is not None:
        return refusal

    # Before preflight, and so before anything that touches the sandbox:
    # `sbx exec -it` needs a terminal, so without one this invocation can only
    # fail. Letting it fail down there instead would mean a sandbox built over
    # minutes -- or with --fresh a working one destroyed and rebuilt -- for a
    # session that was never going to open. Only stdin is checked; redirecting
    # stdout is a reasonable thing to do and `-i` does not care.
    if not sys.stdin.isatty():
        print(f"md2okf: {flag} needs a terminal on stdin", file=sys.stderr)
        return 2

    try:
        sandbox.preflight(agent.min_sbx_version)
    except sandbox.SandboxError as exc:
        print(f"md2okf: {exc}", file=sys.stderr)
        return 2

    wb = workbench.Workbench.default(agent.name)
    try:
        # Held through setup and the whole interactive session. Python creates
        # the descriptor close-on-exec, so survive_exec makes this one
        # inheritable: the replacement `sbx exec -it` process retains the flock
        # and releases it when the session exits. Setup failures still leave the
        # context normally and release it here.
        with workbench.lock(survive_exec=True):
            wb.ensure_roots()
            failure = _ensure_sandbox(wb, agent, args, credentials_optional=args.shell)
            if failure is not None:
                return failure
            argv = ["bash"] if args.shell else list(agent.interactive_args)
            sandbox.exec_interactive(workbench.sandbox_name(agent.name), argv)
    except workbench.LockHeld:
        print(LOCK_HELD_MESSAGE, file=sys.stderr)
        return 2
    except workbench.UnsafeLockFile as exc:
        print(f"md2okf: {exc}", file=sys.stderr)
        return 2


def _run(
    args: argparse.Namespace,
    agent: agents.Agent,
    documents: list[compile_mod.Document],
    spec_path: Path,
    output_dir: Path,
    wb: workbench.Workbench,
) -> int:
    wb.ensure_roots()

    failure = _ensure_sandbox(wb, agent, args)
    if failure is not None:
        return failure

    try:
        clis_dir = resources.clis_dir()
    except resources.ResourcesError as exc:
        print(f"md2okf: {exc}", file=sys.stderr)
        return 2

    try:
        workbench.restage(
            wb,
            inputs=compile_mod.stage_items(documents),
            clis_dir=clis_dir,
            spec_source=spec_path,
            output_dir=output_dir,
        )
    except workbench.WorkbenchError as exc:
        print(f"md2okf: {exc}", file=sys.stderr)
        return 1

    def on_progress(line: str) -> None:
        if not args.quiet:
            print(line, file=sys.stderr)

    def on_event(line: str) -> None:
        if args.verbose:
            print(line, file=sys.stderr)

    for doc in documents:
        try:
            row = compile_mod.compile_document(
                agent,
                workbench.sandbox_name(agent.name),
                doc,
                wb,
                output_dir,
                args.n,
                on_progress=on_progress,
                on_event=on_event,
            )
        except compile_mod.CompileError as exc:
            print(f"md2okf: {exc}", file=sys.stderr)
            return 1
        if not args.quiet:
            print(row.as_tsv())
    return 0


def main(argv: list[str] | None = None) -> int:
    """Parse argv, run, and return a process exit code."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    # Before either path, so the interactive and the compile path both get one
    # validated agent, and an unknown one is refused before any work starts.
    try:
        agent = agents.from_env()
    except agents.UnknownAgentError as exc:
        print(f"md2okf: {exc}", file=sys.stderr)
        return 2

    # Before _resolve_inputs, which reads stdin when no paths are given --
    # `md2okf --shell` would otherwise block waiting for a document.
    if args.shell or args.agent:
        return _enter_sandbox(args, parser, agent)

    resolved = _resolve_inputs(args, agent)
    if isinstance(resolved, int):
        return resolved
    documents, spec_path, output_dir, wb = resolved

    if args.dry_run:
        try:
            _print_dry_run(agent, documents, spec_path, output_dir, wb)
        except resources.ResourcesError as exc:
            print(f"md2okf: {exc}", file=sys.stderr)
            return 2
        return 0

    try:
        sandbox.preflight(agent.min_sbx_version)
    except sandbox.SandboxError as exc:
        print(f"md2okf: {exc}", file=sys.stderr)
        return 2

    try:
        with workbench.lock():
            return _run(args, agent, documents, spec_path, output_dir, wb)
    except workbench.LockHeld:
        print(LOCK_HELD_MESSAGE, file=sys.stderr)
        return 2
    except workbench.UnsafeLockFile as exc:
        # Caught here rather than with the setup errors above because lock()
        # is entered after them; it is still an environment problem decided
        # before any work starts, so exit 2. Kept narrow on purpose: a broad
        # WorkbenchError clause here would also swallow run-phase failures
        # that owe the caller exit 1.
        print(f"md2okf: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        # Ctrl-C is a failed run (exit 1), not a crash: a bare traceback tells
        # the user nothing about what survived. The lock is already released
        # by lock()'s own finally, and mirror_out() only ever runs after a
        # completed iteration, so -o DIR cannot hold a half-written pass --
        # though the copy itself is not atomic, hence "may be partial" for
        # the workbench side.
        print(
            f"\nmd2okf: interrupted. {output_dir} holds the last completed pass; "
            f"the workbench copy at {wb.work_okf} may be a partial one.",
            file=sys.stderr,
        )
        return 1
