# Compile loop

How one compile run turns its inputs into documents and drives the agent over each one until the wiki stops changing, in [[src/md2okf/compile.py]].

## Document resolution

[[src/md2okf/compile.py#resolve_documents]] turns the positional arguments into an ordered list of documents, each staged under its basename in the workbench.

- `-` or no arguments means stdin, staged as `stdin.md`. Stdin is refused when it is a terminal, and only one `-` may be given.
- A directory contributes its `*.md` files, sorted and non-recursive.
- Duplicate arguments are kept in the order given, never de-duplicated.
- Two different sources that would stage under the same basename are refused, since one would silently overwrite the other.
- Every path and every discovered file goes through [[src/md2okf/workbench.py#reject_if_unsafe]], so a symlink or special file is refused with exit 2 rather than failing later during staging.

## Ralph loop

[[src/md2okf/compile.py#compile_document]] reruns the agent on the same document until the wiki's root hash is unchanged after a turn, capped at [[src/md2okf/compile.py#DEFAULT_MAX_ITERATIONS]] unless `-n` says otherwise.

Each iteration is one fresh agent turn, started with the agent's own first-turn prompt. From the second iteration on, [[src/md2okf/compile.py#CONTINUATION_PROMPT]] is appended, telling the agent the wiki may hold partial work and to continue at the first gap rather than start over.

A first pass that leaves the hash unchanged is convergence, not failure: one iteration, equal hashes. Hitting the cap is a failure that names the document. If the wiki held no Markdown before and still holds none afterwards, the run fails, because a converged empty wiki means nothing was compiled.

Tests: [[tests/test_compile.py#test_loop_runs_until_hash_stabilises]], [[tests/test_compile.py#test_continuation_prompt_appended_from_iteration_two]] and [[tests/test_compile.py#test_iteration_cap_is_a_failure_naming_the_document]].

## Convergence

[[src/md2okf/compile.py#wiki_root_hash]] runs `merkleokf --nolog -L 0` on the workbench wiki inside the sandbox and validates the root digest it prints.

`--nolog` leaves the root `log.md` out of the hash, so a turn that only appends a log entry still counts as no change. A failed `merkleokf`, a missing root row or a malformed digest raises an error, so a broken hash can never read as convergence.

A stable hash means the agent stopped changing the wiki. It does not mean the wiki is correct: correctness is the job of the agent's own gate (see [[lat.md/kits#Skills]]).

## Turn verdict

A turn fails if the agent's protocol reports a failure, if the process exits nonzero, or if the turn made no tool calls. Any one of these is enough.

Failure is checked before the tool-call count: a turn that did work and then reported a terminal error must neither pass nor be misreported as "no tool calls". An agent can report a failure and still exit 0, which is why the protocol's verdict is authoritative (see [[agents#Event record]]).

A turn with zero tool calls means the agent did not follow the skill. The failure message combines how the turn ended, the protocol's reason and the last plain-text lines of output, so it shows the cause rather than a wall of JSON envelopes.

Tests: [[tests/test_compile.py#test_exit_zero_with_a_protocol_failure_fails_and_mirrors_nothing]] and [[tests/test_compile.py#test_zero_tool_calls_is_a_failure]].

## Mirroring cadence

The workbench wiki is mirrored out to `-o` only after an iteration completes and passes its verdict, never mid-turn.

The stream is closed in a `finally` block that runs before the mirror, so Ctrl-C during a turn stops the local `sbx exec` conduit without copying anything. A failed mirror-out is a failure of that document, with exit 1. The copy itself is not atomic. [[workbench#Mirror failure recovery]] is the one place that sets out what `-o` and the workbench hold in each case, and how to recover.

Test: [[tests/test_compile.py#test_mirrors_out_after_every_iteration]].

## Errors

Two exception types carry the exit-code split: `UsageError` is decided before work starts (exit 2), `CompileError` happens once compiling has started (exit 1).

`CompileError` folds the document's path into its message, because the message is what every caller prints, and a document kept only on an attribute would never reach the user. Workbench failures during a turn, such as a failed mirror-out, are re-raised as `CompileError` so the per-document loop in [[cli]] handles them.
