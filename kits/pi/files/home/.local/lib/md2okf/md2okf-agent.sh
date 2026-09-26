#!/bin/sh
# Prepare one agent process, then become it.
# Usage: sh md2okf-agent.sh TRACE_DIR COMMAND [ARG...]
#
# The driver starts every compile turn and every `md2okf --agent` session with
# `sbx exec`, which never passes through the kit's entrypoint -- so whatever an
# agent process needs is done here instead. Today that is one thing: making
# sure TRACE_DIR, the agent's native trace directory, is bind-mounted onto the
# host-backed state before the agent writes a single trace. The startup hook
# normally did it already and mount-state.sh is idempotent; it is fatal here
# all the same, so an agent never runs with its traces landing on the VM's
# disposable disk.
#
# Identical in every kit. Each kit's `md2okf-agent` shim on PATH supplies its
# own TRACE_DIR; the command and its flags come from the driver
# (md2okf.agents.Agent), where they are unit-tested.
set -eu

if [ "$#" -lt 2 ]; then
	echo "usage: md2okf-agent.sh TRACE_DIR COMMAND [ARG...]" >&2
	exit 2
fi
trace_dir=$1
shift

HOME="${HOME:-/home/agent}"
export HOME

if ! sh "${HOME}/.local/lib/md2okf/mount-state.sh" "${trace_dir}" sessions; then
	echo "md2okf: could not relocate traces onto state; refusing to start $1" >&2
	exit 1
fi
exec "$@"
