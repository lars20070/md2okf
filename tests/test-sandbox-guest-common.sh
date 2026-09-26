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
#   AGENT_TRACE_DIR     the agent's native trace directory, which the kit binds
#                       onto $MD2OKF_STATE_DIR/sessions
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

for required in AGENT_NAME AGENT_BINARY AGENT_TRACE_DIR AGENT_INSTRUCTIONS AGENT_RUNTIME_PATHS; do
	eval "value=\${${required}-}"
	if [ -z "${value}" ]; then
		echo "BROKEN the agent file does not set ${required}"
		exit 1
	fi
done

# The tool list must match BOTH lists in kits/<agent>/spec.yaml: the
# setup.install / setup.files steps AND the agentInstructions "Installed tools"
# prose. That prose is the promise being tested here, so a tool installed but
# not promised — or promised but not installed — is itself the bug.

case "$(pwd -P)" in
*/okf) ok "sandbox workspace is the wiki root" ;;
*) broken "sandbox workspace is not the wiki root: $(pwd -P)" ;;
esac

# apt. Ubuntu's `fd-find` package provides `fdfind`; `rg` is the command
# provided by the `ripgrep` package.
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

# setup.files shims: workspace-backed CLIs on PATH.
check inspectmd
check inspectokf
check sizeokf
check merkleokf

# pinned release binaries: checksummed download, no package manager.
check mq
check okfctl

# Shared by every kit, byte for byte.
check_file "${HOME}/.local/lib/md2okf/mount-state.sh"
check_file "${HOME}/.local/lib/md2okf/md2okf-agent.sh"
# The shim is a setup.files entry with an explicit mode; its exec bit is what
# lets `sbx exec … md2okf-agent` start at all. test-sandbox.sh runs it the way
# the driver does, outside this login shell.
check_exec "${HOME}/.local/bin/md2okf-agent"

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

# Persistent traces. The native path must remain a real directory and be the
# same bind-mounted directory as the host-backed state target.
if [ -z "${MD2OKF_STATE_DIR:-}" ]; then
	echo "MISSING MD2OKF_STATE_DIR"
	failures=$((failures + 1))
else
	trace_link="${AGENT_TRACE_DIR}"
	trace_target="${MD2OKF_STATE_DIR}/sessions"
	if [ -L "${trace_link}" ]; then
		broken "${trace_link} is a symlink"
	elif [ ! -d "${trace_link}" ] || [ ! -d "${trace_target}" ]; then
		echo "MISSING persistent trace directories: ${trace_link} ${trace_target}"
		failures=$((failures + 1))
	elif [ "$(stat -c '%d:%i' "${trace_link}")" != \
		"$(stat -c '%d:%i' "${trace_target}")" ]; then
		broken "${trace_link} is not bind-mounted onto state"
	else
		probe=".md2okf-sandbox-test-$$"
		if printf 'persistent\n' >"${trace_link}/${probe}" &&
			grep -qx persistent "${trace_target}/${probe}"; then
			ok "persistent ${AGENT_NAME} trace bind"
		else
			broken "write through ${trace_link} did not reach state"
		fi
		rm -f "${trace_link:?}/${probe}"

		# Left in place for test-sandbox.sh to find on the host: proof that
		# a write through the native path lands in host-backed state, not in
		# a VM-local directory that merely looks right from in here.
		host_probe_token="$$-$(date +%s)"
		if printf '%s\n' "${host_probe_token}" >"${trace_link}/.md2okf-host-probe"; then
			echo "trace-probe ${host_probe_token}"
		else
			broken "could not write the host trace probe"
		fi
	fi
fi

# --- Workbench mount invariants ---------------------------------------------
#
# Five mounts: the wiki (rw, this shell's cwd) plus its ../md, ../scripts and
# ../SPEC.md siblings (ro), and the state directory's sessions/ (rw). Read-only
# has to mean read-only as a property of the filesystem, not of instructions:
# the agent treats every source document as untrusted, so a prompt-injected
# document must not be able to rewrite the spec the run is held to.
#
# `sbx` enforces `:ro` on the host side, so a read-only export stays read-only
# whatever the guest does — but that survives only while nothing writable
# *contains* it. A plain `mount --bind` does not replicate nested submounts, so
# binding a writable parent elsewhere would expose the underlying writable view
# of everything below it. sudo is passwordless here (kits/pi/spec.yaml), so
# these checks try the escape rather than assuming it is impossible.

wiki_root="$(pwd -P)"
work_dir="$(dirname "${wiki_root}")"

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

# The wiki is the one place the agent may write.
if dir_is_writable "${wiki_root}"; then
	echo "ok the wiki root is writable"
else
	echo "BROKEN the wiki root is not writable: ${wiki_root}"
	failures=$((failures + 1))
fi

# No read-write mount may be an ancestor of a read-only one. This is a path
# property, checked against the mounts themselves — note the state *root* is
# deliberately not in this list, because only its sessions/ child is mounted.
for rw in "${wiki_root}" "${MD2OKF_STATE_DIR:-/nonexistent}/sessions"; do
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
# state root exists in here only as the synthetic parent of the sessions/
# mount, so its siblings — which the host really does write — prove the root
# itself is not shared. An injected document that could reach these could
# rewrite the ownership marker the host trusts.
if [ -n "${MD2OKF_STATE_DIR:-}" ]; then
	for host_only in sandbox-fingerprint sandbox-identity; do
		if [ -e "${MD2OKF_STATE_DIR}/${host_only}" ]; then
			echo "BROKEN host-only ${host_only} is visible inside the sandbox"
			failures=$((failures + 1))
		else
			echo "ok host-only ${host_only} is not visible"
		fi
	done
fi

# Re-check the read-only mounts after bind-mounting every writable mount to a
# scratch path — the plan's specific concern, since a bind of a writable
# ancestor is what would flatten the nested read-only ones.
if sudo -n true 2>/dev/null; then
	for rw in "${wiki_root}" "${MD2OKF_STATE_DIR:-}/sessions"; do
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
