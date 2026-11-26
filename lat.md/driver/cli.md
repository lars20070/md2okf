# CLI

The `md2okf` command, [[src/md2okf/cli.py#main]]: it decides everything that can be decided before work starts, then hands off to the compile loop or to an interactive sandbox session.

## Modes

One command has four modes: compile (the default), dry run, `--shell` and `--agent`. [[docs/usage.md]] is the full option reference.

The agent comes from [[src/md2okf/agents.py#from_env]] before either path runs, so an unknown `MD2OKF_AGENT` is refused with exit 2 in every mode.

The interactive check comes before input resolution, because resolving no paths reads stdin and `md2okf --shell` would otherwise block waiting for a document.

## Option rules

Options that an interactive session cannot honour are refused, never silently ignored: `--shell -o wiki` reads like "mount this output".

[[src/md2okf/cli.py#_reject_compile_only_options]] compares each compile-only option with the parser's own default rather than tracking which flags were typed. A user who spells out the default (`-o okf`) is not caught, which costs nothing because nothing changes. Positional paths are refused outright. Only `--fresh` combines with `--shell` and `--agent`.

## Interactive sessions

`--shell` and `--agent` make the sandbox current, then replace the md2okf process with `sbx exec -it` so the terminal, job control and exit code are the guest's own.

[[src/md2okf/cli.py#_enter_sandbox]] checks for a terminal on stdin before preflight. Without one the session can never open, and failing later would mean a sandbox built, or with `--fresh` destroyed and rebuilt, for nothing.

The run lock is taken with `survive_exec`, so the replacement process inherits the lock and holds it until the session exits (see [[workbench#Run lock]]). A concurrent compile or `--fresh` is refused meanwhile.

`--shell` downgrades a failed credential check to a warning, because a diagnostic shell is most useful exactly then (see [[sandbox#Credential check]]). Interactive sessions restage only the tooling and spec, never the inputs or the wiki.

## Dry run

`--dry-run` resolves and validates the inputs, then prints the agent, spec, output, documents, mounts and the `sbx` command lines that would run.

[[src/md2okf/cli.py#_print_dry_run]] needs no `sbx`, takes no lock and starts nothing paid. It shows the `sbx run` line unconditionally, because whether the sandbox would be reused is a live decision that would mean querying `sbx`. It shows only the first iteration's agent command, since how many iterations run is what compiling decides.

## Exit codes

Exit 0 means every document compiled, 1 means a failure after work started, and 2 means a refusal before any work started.

Exit 2 covers usage errors, unsafe paths, an output that cannot be adopted, a failed preflight, a held or unsafe lock, an unowned sandbox and a credential that is not ready. Exit 1 covers staging failures, a failed agent turn, the iteration cap and a failed mirror-out.

The `UnsafeLockFile` catch in `main` is deliberately narrow: a broad `WorkbenchError` clause there would also swallow run-phase failures that owe exit 1. Ctrl-C exits 1 with a message rather than a traceback, and the lock is released. Which copy of the wiki is complete after a Ctrl-C depends on when it arrived, and the message is right only for a Ctrl-C during an agent turn (see [[workbench#Mirror failure recovery]]). Tests: [[tests/test_cli.py#test_ctrl_c_exits_1_with_a_message_not_a_traceback]] and [[tests/test_cli.py#test_ctrl_c_releases_the_lock]].

## Output streams

Stdout carries only the TSV result rows: one per document with its path, iteration count and the wiki hash before and after. Everything else goes to stderr.

Progress lines go to stderr unless `-q` is set, and `-v` adds the agent's tool calls and messages, as rendered by its protocol (see [[agents#Event record]]). A path containing a tab or newline is refused at resolution time, so it can never corrupt a row.
