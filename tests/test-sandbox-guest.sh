#!/bin/sh

# Runs INSIDE the md2okf sandbox, piped into `sbx exec ... sh -l -s` by
# tests/test-sandbox.sh (tests/ is not mounted, so this file cannot be named as
# a path inside the VM). Run on the host it would happily report on your
# laptop's toolchain instead, which proves nothing.
#
# POSIX sh, not bash: the guest shell is `sh`, so the `#!/bin/sh` shebang above
# is what makes shellcheck reject a bashism here rather than leaving it to fail
# inside the VM. Everything below relies on the login shell (`sh -l`) having put
# ~/.local/bin and the npm prefix on PATH.
#
# Deliberately no `set -e`: every check runs, and all failures are reported in
# one pass rather than stopping at the first.

failures=0

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

# The tool list must match BOTH lists in kits/md2okf/spec.yaml: the
# setup.install / setup.files steps AND the agentInstructions "Installed tools"
# prose. That prose is the promise being tested here, so a tool installed but
# not promised — or promised but not installed — is itself the bug.

case "$(pwd -P)" in
*/okf) echo "ok sandbox workspace is the wiki root" ;;
*)
	echo "BROKEN sandbox workspace is not the wiki root: $(pwd -P)"
	failures=$((failures + 1))
	;;
esac

# apt (kits/md2okf/spec.yaml). Ubuntu's `fd-find` package provides `fdfind`;
# `rg` is the command provided by the `ripgrep` package.
check curl
check fdfind
check jq
check python3
check rg
check shellcheck
check tree

# npm through the retry wrapper (kits/md2okf/spec.yaml).
check pi

# npm, Markdown and spelling linters (kits/md2okf/spec.yaml).
check markdownlint-cli2
check cspell

# uv (kits/md2okf/spec.yaml).
check ruff
check yamllint

# setup.files shims (kits/md2okf/spec.yaml): workspace-backed CLIs on PATH.
check inspectmd
check inspectokf
check sizeokf
check merkleokf

# pinned release binaries (kits/md2okf/spec.yaml): checksummed download, no
# package manager.
check mq
check okfctl

# Config delivery: kits/md2okf/files/home/.pi/agent/ is copied at kit build
# time, not mounted, so a layout change can leave Pi with no instructions and
# no skill.
check_file "${HOME}/.pi/agent/AGENTS.md"
check_file "${HOME}/.pi/agent/settings.json"
check_file "${HOME}/.pi/agent/models.json"
check_file "${HOME}/.pi/agent/skills/compile-okf/SKILL.md"
check_exec "${HOME}/.pi/agent/skills/compile-okf/scripts/check-okf.sh"
check_file "${HOME}/.pi/agent/skills/compile-okf/scripts/frontmatter-guard.py"
check_file "${HOME}/.pi/agent/skills/inspect-md/SKILL.md"
check_file "${HOME}/.pi/agent/skills/inspect-okf/SKILL.md"
check_file "${HOME}/.pi/agent/skills/size-okf/SKILL.md"
check_file "${HOME}/.pi/agent/skills/merkle-okf/SKILL.md"
check_file "${HOME}/.pi/agent/skills/curate-okf/SKILL.md"
check_file "${HOME}/.local/lib/md2okf/mount-state.sh"

if grep -R -F -q -- '../okf' "${HOME}/.pi/agent/AGENTS.md" \
	"${HOME}/.pi/agent/skills"; then
	echo "BROKEN Pi runtime instructions refer to the wiki as ../okf"
	failures=$((failures + 1))
else
	echo "ok Pi runtime instructions use the workspace root"
fi

# Persistent Pi sessions. The stock path must remain a real directory and be
# the same bind-mounted directory as the host-backed state target.
if [ -z "${MD2OKF_STATE_DIR:-}" ]; then
	echo "MISSING MD2OKF_STATE_DIR"
	failures=$((failures + 1))
else
	session_link="${HOME}/.pi/agent/sessions"
	session_target="${MD2OKF_STATE_DIR}/sessions"
	if [ -L "${session_link}" ]; then
		echo "BROKEN ${session_link} is a symlink"
		failures=$((failures + 1))
	elif [ ! -d "${session_link}" ] || [ ! -d "${session_target}" ]; then
		echo "MISSING persistent Pi session directories"
		failures=$((failures + 1))
	elif [ "$(stat -c '%d:%i' "${session_link}")" != \
		"$(stat -c '%d:%i' "${session_target}")" ]; then
		echo "BROKEN ${session_link} is not bind-mounted onto state"
		failures=$((failures + 1))
	else
		probe=".md2okf-sandbox-test-$$"
		if printf 'persistent\n' >"${session_link}/${probe}" &&
			grep -qx persistent "${session_target}/${probe}"; then
			echo "ok persistent Pi session bind"
		else
			echo "BROKEN write through Pi session path did not reach state"
			failures=$((failures + 1))
		fi
		rm -f "${session_link:?}/${probe}"
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
# of everything below it. sudo is passwordless here (kits/md2okf/spec.yaml), so
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

# Context7 native Pi package (kits/md2okf/spec.yaml setup.install +
# settings.json packages). Presence only — no live Context7 API call.
if timeout 20 pi list 2>/dev/null | grep -q context7-pi; then
	echo "ok context7-pi (pi list)"
else
	echo "MISSING context7-pi (pi list)"
	failures=$((failures + 1))
fi

if grep -q 'npm:@upstash/context7-pi@0.1.2' "${HOME}/.pi/agent/settings.json"; then
	echo "ok settings.json context7-pi package"
else
	echo "MISSING settings.json context7-pi package"
	failures=$((failures + 1))
fi

c7_skill=$(
	find "${HOME}/.pi/agent/npm" \
		-path '*context7-pi*/skills/context7-docs/SKILL.md' \
		2>/dev/null | head -n 1
)
if [ -n "${c7_skill}" ] && [ -f "${c7_skill}" ]; then
	echo "ok ${c7_skill}"
else
	echo "MISSING context7-docs SKILL.md under ~/.pi/agent/npm"
	failures=$((failures + 1))
fi

# Credentials (kits/md2okf/spec.yaml). Automates the manual check in the README.
# Never print the value — case-match and report only a verdict.
case "${OPENROUTER_API_KEY-}" in
"")
	echo "MISSING OPENROUTER_API_KEY"
	failures=$((failures + 1))
	;;
proxy-managed)
	echo "ok OPENROUTER_API_KEY"
	;;
*)
	echo "BROKEN OPENROUTER_API_KEY (literal value in the VM, expected the proxy-managed sentinel)"
	failures=$((failures + 1))
	;;
esac

if [ "${failures}" -ne 0 ]; then
	echo "FAILED: ${failures} check(s)"
	exit 1
fi
echo "All toolchain checks passed."
