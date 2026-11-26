# Workbench

The fixed host directory tree, one per agent under `$XDG_STATE_HOME/md2okf/<agent>`, that every run is staged through, in [[src/md2okf/workbench.py]].

## Why a fixed workbench

sbx fixes a sandbox's mounts when it is created. A fixed staging tree lets one long-lived sandbox per agent serve every run, whatever inputs and `-o` it is given.

Runs differ only in the contents of the mount roots, never in the roots themselves. So a different input folder or output directory never forces a rebuild, and the kit's agent instructions can rely on one sibling layout: the wiki as the workspace, with `../md/`, `../scripts/` and `../SPEC.md` beside it.

## Layout and mounts

[[src/md2okf/workbench.py#Workbench#mounts]] returns the five `sbx run` mounts in a fixed order. The order is part of the sandbox fingerprint.

1. `work/okf`, read-write: the wiki, and the agent's working directory.
2. `work/md`, read-only: this run's staged documents.
3. `work/scripts`, read-only: the four helper CLI projects.
4. `work/SPEC.md`, read-only: the bundled OKF spec.
5. `sessions`, read-write: the agent's transcripts, the only persistent state inside the sandbox. It is mounted at the agent's own trace directory (`trace_target` on [[src/md2okf/agents.py#Agent]]), not at its host path; the other four keep their host paths.

No read-write mount contains a read-only one: `work/` itself is never mounted, so the agent cannot reach around a read-only mount through a writable parent. [[src/md2okf/workbench.py#Workbench#ensure_roots]] creates the roots before the first `sbx run`, because sbx cannot mount a missing path. After that it never replaces them.

## Run lock

[[src/md2okf/workbench.py#lock]] serialises every md2okf run for a user, across all agents, with a non-blocking `flock`. A second run is refused at once rather than queued.

- The path is per uid in `/tmp`, not under `XDG_STATE_HOME`: two shells with different state homes must still race on the same lock.
- The file sits in a world-writable directory, so it is opened with `O_NOFOLLOW` and then checked with `fstat`. A symlink, a non-regular file or a file owned by someone else is refused, never unlinked.
- One lock covers every agent, because two agents mirroring into one `-o` would need output locking that md2okf does not attempt.
- `survive_exec` makes the descriptor inheritable, so an interactive session that replaces the process with `execvp` keeps the lock until it exits. Every other caller keeps the default close-on-exec.

Tests: [[tests/test_workbench.py#test_lock_is_non_blocking_and_exclusive]] for exclusivity, [[tests/test_workbench.py#test_lock_can_survive_process_replacement]] and [[tests/test_workbench.py#test_lock_is_close_on_exec_by_default]] for descriptor inheritance, and [[tests/test_workbench.py#test_lock_refuses_a_symlinked_lock_path]], [[tests/test_workbench.py#test_lock_refuses_a_lock_path_that_is_not_a_regular_file]] and [[tests/test_workbench.py#test_lock_refuses_a_lock_file_owned_by_someone_else]] for the untrusted path.

## Staging

Staging happens in two steps: the tooling and spec on every sandbox ensure, then the run's own documents and wiki once the sandbox is ready.

[[src/md2okf/workbench.py#stage_tooling]] stages the helper CLIs and the spec at the start of [[src/md2okf/workbench.py#ensure_sandbox]], interactive sessions included, so the sandbox never sees an empty scripts mount.

[[src/md2okf/workbench.py#restage]] runs only after the ensure, including its credential check, has succeeded. It stages the documents into `work/md`, the CLIs into `work/scripts` again, and mirrors `-o` into `work/okf`, so an existing wiki is continued rather than restarted. A run refused at the ensure therefore leaves the previous run's documents and wiki in the workbench.

[[src/md2okf/workbench.py#stage_clis]] copies only each project's `pyproject.toml` and `src/`, the same subset the wheel ships. A project's `.venv`, caches, tests and lockfile never reach the sandbox.

[[src/md2okf/workbench.py#rewrite_spec]] rewrites `work/SPEC.md` in place, truncating and writing rather than renaming over it, because the bind mount is tied to the file's inode. Because the tooling step calls it on every ensure, even `--shell` and `--agent` never see an empty spec.

## Output adoption

[[src/md2okf/workbench.py#is_adoptable_output]] answers "may md2okf overwrite this folder?" before any work starts. Anything it cannot prove adoptable is refused with exit 2.

Mirroring out propagates deletions, so a wrong `-o` would delete the user's files. Adoption is therefore proved, never guessed:

- A missing or empty directory is adoptable. Tests: [[tests/test_workbench.py#test_missing_output_is_adoptable]] and [[tests/test_workbench.py#test_empty_output_is_adoptable]].
- A non-empty directory is adoptable only as an OKF bundle root: its `index.md` frontmatter must hold exactly one key, `okf_version`. Tests: [[tests/test_workbench.py#test_output_with_okf_version_only_frontmatter_is_adoptable]], [[tests/test_workbench.py#test_output_with_extra_frontmatter_keys_is_not_adoptable]] and [[tests/test_workbench.py#test_output_with_bare_index_md_is_not_adoptable]].
- A symlink is never adoptable, including a dangling one that would otherwise read as missing. Tests: [[tests/test_workbench.py#test_output_that_is_a_symlink_is_not_adoptable]] and [[tests/test_workbench.py#test_output_that_is_a_dangling_symlink_is_not_adoptable]].

The marker check is deliberately about the key set only. `_parse_simple_frontmatter` reads flat `key: value` lines without a YAML dependency, and the value of `okf_version` is not compared with the spec. That stricter check, that the root index declares exactly the bundled spec's version, belongs to the kit's frontmatter guard (see [[lat.md/kits#Skills]]). As a result, a wiki that declares an older version is still adoptable, and the guard reports the mismatch the next time the agent runs its gate. Change either check with the other in view.

This is a different question from whether a sandbox may be replaced (see [[sandbox#Create or reuse]]).

## Path safety

Two checks keep a run from reading through links or eating its own output, both decided before work starts.

[[src/md2okf/workbench.py#reject_if_unsafe]] refuses a symlink or special file (device, socket, FIFO) as an input, a mirrored entry or a helper CLI file. Mirroring never creates or follows a symlink.

[[src/md2okf/workbench.py#check_no_overlap]] refuses when any two of the inputs, the spec, the output and the workbench resolve to the same path or nest. Otherwise an output inside an input would be compiled as input, or copied into itself.

## Mirror failure recovery

What `-o` holds after a run stops early depends on whether it stopped during an agent turn or during the copy out. The copy is not atomic.

[[src/md2okf/workbench.py#sync_children]] clears the destination's children first and then copies the source in place. So:

- **Stopped during an agent turn** (Ctrl-C, or a failed turn): nothing is copied for that turn. `-o` keeps the last completed pass, or its pre-run content if no pass completed. The workbench wiki may hold the agent's partial work. Tests: [[tests/test_compile.py#test_ctrl_c_mid_stream_does_not_mirror_a_partial_iteration]] and [[tests/test_compile.py#test_exit_zero_with_a_protocol_failure_fails_and_mirrors_nothing]].
- **Stopped during the copy** (Ctrl-C, or an error such as a full disk): `-o` may be incomplete, with old files already removed. The workbench wiki holds the completed pass.

A failed copy raises `MirrorError`. [[src/md2okf/workbench.py#mirror_out]] puts the workbench path in the message itself rather than only on an attribute, because the message is what every caller prints. Tests: [[tests/test_workbench.py#test_mirror_out_failure_names_the_workbench_path]] and [[tests/test_compile.py#test_a_real_mirror_out_failure_names_the_recovery_path_end_to_end]].

A Ctrl-C cannot tell the two cases apart from where it is caught in [[src/md2okf/cli.py#main]]. Its message says `-o` holds the last completed pass and the workbench copy may be partial, which is true only for the first case.

To recover, save the workbench wiki before running again. The next compile mirrors `-o` into the workbench, which replaces the workbench copy, so an incomplete `-o` would overwrite the complete one.
