#!/bin/sh

# The agent-neutral half of the in-sandbox checks. tests/test-sandbox.sh pipes
# tests/test-sandbox-guest-<agent>.sh and then this file into
# `sbx exec ... sh -l -s` as one script (tests/ is not mounted, so neither can
# be named as a path inside the VM). Run on the host it would happily report
# on your laptop's toolchain instead, which proves nothing.
#
# The agent file comes first and only defines things; this file does the work.
# It provides:
#   AGENT_NAME          the agent, as md2okf.agents names it (pi, claude, ...)
#   AGENT_BINARY        the agent's CLI, checked like every other tool
#   AGENT_TRACE_DIR     the agent's native trace directory, where md2okf mounts
#                       the workbench's sessions/ (Agent.trace_target)
#   AGENT_CONFIG_DIR    the agent's config directory, which holds the trace
#                       directory and must stay the agent's to write
#   AGENT_SKILLS_DIR    where the agent finds its skills, compile-okf included
#   AGENT_INSTRUCTIONS  the file that tells the agent the OKF contract; it must
#                       sign pages as "$AGENT_NAME/"
#   AGENT_RUNTIME_PATHS space-separated files and directories of agent config,
#                       searched for the forbidden ../okf spelling
#   agent_checks        a function: the agent's own files and credential
#
# POSIX sh, not bash: the guest shell is `sh`, so the `#!/bin/sh` shebang above
# is what makes shellcheck reject a bashism here rather than leaving it to fail
# inside the VM. Everything below relies on the login shell (`sh -l`) having put
# ~/.local/bin and the npm prefix on PATH.
#
# Deliberately no `set -e`: every check runs, and all failures are reported in
# one pass rather than stopping at the first.
#
# shellcheck disable=SC2154 # the AGENT_* variables come from the agent file

failures=0

ok() { echo "ok $*"; }
broken() {
	echo "BROKEN $*"
	failures=$((failures + 1))
}

# `command -v` first, then a uniform smoke run: `--version`, falling back to
# `--help`. That fallback is what makes CLIs with unknown flag support (pi,
# markdownlint-cli2, cspell) checkable without fixture files or
# hard-coding which flag each one accepts. `timeout` guards a tool that waits
# rather than prints. Output is discarded, so no version is asserted.
check() {
	if ! command -v "$1" >/dev/null 2>&1; then
		echo "MISSING $1"
		failures=$((failures + 1))
		return
	fi
	if timeout 20 "$1" --version >/dev/null 2>&1 ||
		timeout 20 "$1" --help >/dev/null 2>&1; then
		echo "ok $1"
	else
		echo "BROKEN $1"
		failures=$((failures + 1))
	fi
}

check_file() {
	if [ -f "$1" ]; then
		echo "ok $1"
	else
		echo "MISSING $1"
		failures=$((failures + 1))
	fi
}

# The kit COPIES files in, so a lost exec bit is a real failure mode. Distinguish
# "absent" from "present but not executable" so the message points at the fix.
check_exec() {
	if [ ! -e "$1" ]; then
		echo "MISSING $1"
		failures=$((failures + 1))
	elif [ ! -x "$1" ]; then
		echo "NOT_EXECUTABLE $1"
		failures=$((failures + 1))
	else
		echo "ok $1"
	fi
}

for required in AGENT_NAME AGENT_BINARY AGENT_TRACE_DIR AGENT_CONFIG_DIR AGENT_SKILLS_DIR AGENT_INSTRUCTIONS \
	AGENT_RUNTIME_PATHS; do
	eval "value=\${${required}-}"
	if [ -z "${value}" ]; then
		echo "BROKEN the agent file does not set ${required}"
		exit 1
	fi
done

# The tool list must match BOTH what kits/md2okf-<agent> installs (the descriptor's
# install hooks and the recipe) AND the instructions' "Installed tools" prose.
# That prose is the promise being tested here, so a tool installed but not
# promised — or promised but not installed — is itself the bug.

case "$(pwd -P)" in
*/okf) ok "sandbox workspace is the wiki root" ;;
*) broken "sandbox workspace is not the wiki root: $(pwd -P)" ;;
esac

# The driver assumes each workspace sits at its host path, which is what sbx
# reports as WORKSPACE_DIR, and the compile-okf gate finds ../SPEC.md through
# it. test-sandbox.sh repeats this under a plain `sbx exec`.
if [ -z "${WORKSPACE_DIR:-}" ]; then
	broken "WORKSPACE_DIR is not set, so the compile-okf gate cannot find ../SPEC.md"
elif [ "$(cd "${WORKSPACE_DIR}" 2>/dev/null && pwd -P)" = "$(pwd -P)" ]; then
	ok "WORKSPACE_DIR is the wiki root"
else
	broken "WORKSPACE_DIR (${WORKSPACE_DIR}) is not the wiki root $(pwd -P)"
fi

# apt. The `fd-find` package provides `fdfind`; `rg` is the command provided
# by the `ripgrep` package.
check curl
check fdfind
check jq
check python3
check rg
check shellcheck
check tree

# The agent itself.
check "${AGENT_BINARY}"

# npm, Markdown and spelling linters.
check markdownlint-cli2
check cspell

# uv.
check ruff
check yamllint

# Shims written at create: workspace-backed CLIs on PATH.
check inspectmd
check inspectokf
check sizeokf
check merkleokf

# The shims on real input, not only --help. merkleokf runs from a cold uv
# cache, so it also proves the runtime PyPI grant: the shim builds the
# mounted project, and its build backend comes from PyPI.
cold_cache="$(mktemp -d)"
if UV_CACHE_DIR="${cold_cache}" timeout 300 merkleokf --nolog -L 0 "$(pwd -P)" >/dev/null 2>&1; then
	ok "merkleokf hashes the wiki root from a cold uv cache"
else
	broken "merkleokf could not hash the wiki root from a cold uv cache (PyPI blocked?)"
fi
rm -rf "${cold_cache}"
if timeout 120 inspectmd "$(dirname "$(pwd -P)")/SPEC.md" >/dev/null 2>&1; then
	ok "inspectmd maps ../SPEC.md"
else
	broken "inspectmd could not map ../SPEC.md"
fi
if timeout 120 sizeokf "$(pwd -P)" >/dev/null 2>&1 && timeout 120 inspectokf "$(pwd -P)" >/dev/null 2>&1; then
	ok "sizeokf and inspectokf read the wiki root"
else
	broken "sizeokf or inspectokf could not read the wiki root"
fi

# pinned release binaries: checksummed download, no package manager.
check mq
check okfctl

# The gate's frontmatter guard must find md2okf's SPEC.md from where the kit
# installed it. Exit 2 is "could not run"; 0 or 1 (findings, as on an empty
# wiki) means it found the spec and checked.
guard="${AGENT_SKILLS_DIR}/compile-okf/scripts/frontmatter-guard.py"
python3 "${guard}" "$(pwd -P)" >/dev/null 2>&1
if [ "$?" -ne 2 ]; then
	ok "the frontmatter guard finds md2okf's SPEC.md"
else
	broken "the frontmatter guard cannot run: python3 ${guard} $(pwd -P)"
fi

# Provenance: pages must be signed by the agent that wrote them.
check_file "${AGENT_INSTRUCTIONS}"
if grep -q "generated: { by: ${AGENT_NAME}/" "${AGENT_INSTRUCTIONS}" 2>/dev/null; then
	ok "the instructions sign pages as ${AGENT_NAME}/"
else
	broken "the instructions do not sign pages as ${AGENT_NAME}/: ${AGENT_INSTRUCTIONS}"
fi

# shellcheck disable=SC2086 # AGENT_RUNTIME_PATHS is a deliberate word list
if grep -R -F -q -- '../okf' ${AGENT_RUNTIME_PATHS}; then
	broken "runtime instructions refer to the wiki as ../okf"
else
	ok "runtime instructions use the workspace root"
fi

# Ownership. A mount target's missing parents, or an overlay's directory
# entries, can leave the agent's home or config directory owned by root, and
# then the agent cannot write its own settings next to the trace mount.
agent_uid="$(id -u)"
if [ "$(stat -c '%u' /home)" = 0 ]; then
	ok "/home is root's"
else
	broken "/home is not owned by root"
fi
if [ "$(stat -c '%u' "${HOME}")" = "${agent_uid}" ]; then
	ok "${HOME} is the agent's"
else
	broken "${HOME} is not owned by the agent"
fi
if [ "$(stat -c '%u' "${AGENT_CONFIG_DIR}" 2>/dev/null)" = "${agent_uid}" ] &&
	dir_probe="${AGENT_CONFIG_DIR}/.md2okf-owner-probe-$$" &&
	(: >"${dir_probe}") 2>/dev/null; then
	rm -f "${dir_probe}"
	ok "${AGENT_CONFIG_DIR} is the agent's and writable"
else
	broken "${AGENT_CONFIG_DIR} is not the agent's to write"
fi

# Persistent traces. The native path is a host mount (the workbench's
# sessions/), so it must be a real, writable directory on a different
# filesystem from the config directory around it.
trace_dir="${AGENT_TRACE_DIR}"
if [ -L "${trace_dir}" ]; then
	broken "${trace_dir} is a symlink"
elif [ ! -d "${trace_dir}" ]; then
	echo "MISSING trace directory ${trace_dir}"
	failures=$((failures + 1))
elif [ "$(stat -c '%d' "${trace_dir}")" = "$(stat -c '%d' "$(dirname "${trace_dir}")")" ]; then
	broken "${trace_dir} is not a mount; traces would stay on the VM's disk"
else
	# Left in place for test-sandbox.sh to find on the host: proof that a
	# write through the native path lands in the workbench, not in a
	# VM-local directory that merely looks right from in here.
	host_probe_token="$$-$(date +%s)"
	if printf '%s\n' "${host_probe_token}" >"${trace_dir}/.md2okf-host-probe"; then
		ok "${trace_dir} is a writable mount"
		echo "trace-probe ${host_probe_token}"
	else
		broken "could not write the host trace probe into ${trace_dir}"
	fi
fi

# --- Workbench mount invariants ---------------------------------------------
#
# Five mounts: the wiki (rw, this shell's cwd) plus its ../md, ../scripts and
# ../SPEC.md siblings (ro), and the workbench's sessions/ (rw) at the agent's
# trace directory. Read-only
# has to mean read-only as a property of the filesystem, not of instructions:
# the agent treats every source document as untrusted, so a prompt-injected
# document must not be able to rewrite the spec the run is held to.
#
# `sbx` enforces `:ro` on the host side, so a read-only export stays read-only
# whatever the guest does — but that survives only while nothing writable
# *contains* it. A plain `mount --bind` does not replicate nested submounts, so
# binding a writable parent elsewhere would expose the underlying writable view
# of everything below it. sudo is passwordless here, so these checks try the
# escape rather than assuming it is impossible.

wiki_root="$(pwd -P)"
work_dir="$(dirname "${wiki_root}")"
# The workbench root on the host, <state>/md2okf/<agent>: work/ is mounted at
# its host path, so its parent's path is the host's too.
state_root="$(dirname "${work_dir}")"

# 0 when a write succeeded (and was cleaned up again), 1 otherwise.
#
# The probe runs in a subshell on purpose. `:` is a POSIX *special* builtin,
# and a redirection failure on one is fatal to the whole shell in dash — the
# guest's `sh` — so writing this the obvious way silently aborted every check
# after the first read-only mount instead of reporting it.
dir_is_writable() {
	probe="$1/.md2okf-write-probe-$$"
	if (: >"${probe}") 2>/dev/null; then
		rm -f "${probe}"
		return 0
	fi
	return 1
}

# Opening for append needs write permission but truncates nothing, so this is a
# non-destructive probe that still fails with EROFS on a read-only mount.
file_is_writable() {
	(: >>"$1") 2>/dev/null
}

assert_readonly() {
	label="$1"
	path="$2"
	if [ -d "${path}" ]; then
		if dir_is_writable "${path}"; then
			echo "BROKEN ${label} is writable: ${path}"
			failures=$((failures + 1))
			return
		fi
	elif [ -f "${path}" ]; then
		if file_is_writable "${path}"; then
			echo "BROKEN ${label} is writable: ${path}"
			failures=$((failures + 1))
			return
		fi
	else
		echo "MISSING ${label}: ${path}"
		failures=$((failures + 1))
		return
	fi
	echo "ok ${label} is read-only"
}

# The read-only mounts, reached exactly as the agent config reaches them.
assert_readonly "../md" "${work_dir}/md"
assert_readonly "../scripts" "${work_dir}/scripts"
assert_readonly "../SPEC.md" "${work_dir}/SPEC.md"

# The spec the run is held to was staged, not left as the empty placeholder
# sbx needs to mount a path.
if [ -s "${work_dir}/SPEC.md" ]; then
	ok "../SPEC.md is the staged spec"
else
	broken "../SPEC.md is empty"
fi

# The wiki is the one place the agent may write.
if dir_is_writable "${wiki_root}"; then
	echo "ok the wiki root is writable"
else
	echo "BROKEN the wiki root is not writable: ${wiki_root}"
	failures=$((failures + 1))
fi

# No read-write mount may be an ancestor of a read-only one. This is a path
# property, checked against the mounts themselves.
for rw in "${wiki_root}" "${AGENT_TRACE_DIR}"; do
	for ro in "${work_dir}/md" "${work_dir}/scripts" "${work_dir}/SPEC.md"; do
		case "${ro}/" in
		"${rw}/"*)
			echo "BROKEN read-write ${rw} is an ancestor of read-only ${ro}"
			failures=$((failures + 1))
			;;
		*) ;; # not nested: the invariant holds for this pair
		esac
	done
done
echo "ok no read-write mount is an ancestor of a read-only one"

# Host-side control files must be outside the VM's namespace entirely. The
# workbench root exists in here only as the synthetic parent of work/, so the
# files the host really does write beside it prove the root itself is not
# shared. An injected document that could reach these could rewrite the
# ownership marker the host trusts. sessions/ is mounted elsewhere, at the
# trace directory, so it must not appear at its host path either.
for host_only in sandbox-fingerprint sandbox-identity sessions; do
	if [ -e "${state_root}/${host_only}" ]; then
		echo "BROKEN host-only ${host_only} is visible inside the sandbox at ${state_root}"
		failures=$((failures + 1))
	else
		echo "ok host-only ${host_only} is not visible"
	fi
done

# Re-check the read-only mounts after bind-mounting every writable mount to a
# scratch path — the plan's specific concern, since a bind of a writable
# ancestor is what would flatten the nested read-only ones.
if sudo -n true 2>/dev/null; then
	for rw in "${wiki_root}" "${AGENT_TRACE_DIR}"; do
		[ -d "${rw}" ] || continue
		scratch="$(mktemp -d)"
		if sudo -n mount --bind "${rw}" "${scratch}" 2>/dev/null; then
			assert_readonly "../md after a bind of ${rw}" "${work_dir}/md"
			assert_readonly "../SPEC.md after a bind of ${rw}" "${work_dir}/SPEC.md"
			sudo -n umount "${scratch}" 2>/dev/null || true
		fi
		rmdir "${scratch}" 2>/dev/null || true
	done

	# And the sharper case: bind the shared parent the read-only mounts live
	# under. A plain bind does not carry nested submounts, so what appears
	# underneath must not be the host's read-only content in writable form.
	# An empty stub is fine — writes there land in the VM's own throwaway
	# layer and never reach the host.
	scratch="$(mktemp -d)"
	if sudo -n mount --bind "${work_dir}" "${scratch}" 2>/dev/null; then
		exposed=0
		sample="$(find "${work_dir}/md" -maxdepth 1 -type f -name '*.md' 2>/dev/null | head -n 1)"
		if [ -n "${sample}" ]; then
			through="${scratch}/md/$(basename "${sample}")"
			if [ -e "${through}" ] && file_is_writable "${through}"; then
				echo "BROKEN ../md content is writable through a bind of its parent"
				failures=$((failures + 1))
				exposed=1
			fi
		fi
		if [ -e "${scratch}/SPEC.md" ] && file_is_writable "${scratch}/SPEC.md"; then
			echo "BROKEN ../SPEC.md is writable through a bind of its parent"
			failures=$((failures + 1))
			exposed=1
		fi
		[ "${exposed}" -eq 0 ] &&
			echo "ok binding the parent does not expose the read-only mounts"
		sudo -n umount "${scratch}" 2>/dev/null || true
	fi
	rmdir "${scratch}" 2>/dev/null || true
else
	echo "ok mount-escape checks skipped (no password-free sudo)"
fi

# --- The agent's own checks ---------------------------------------------------

agent_checks

if [ "${failures}" -ne 0 ]; then
	echo "FAILED: ${failures} check(s)"
	exit 1
fi
echo "All toolchain checks passed."
