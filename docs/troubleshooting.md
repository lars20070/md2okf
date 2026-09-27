# Troubleshooting

Known failure messages and what to do about them. For installing and a first
compile, see [the README](../README.md).

**`sbx` reports unknown fields from a kit's `spec.yaml`.** Every agent requires
sbx 0.45.0 or newer. Upgrade sbx through Homebrew or APT.

**`… inside 'md2okf-<agent>' is not proxy-managed` or `is not logged in`.**
The agent's credential did not reach its sandbox. Run the commands the message
prints — they store it on the host — and then `sbx rm --force md2okf-<agent>`:
sbx hands a credential over only when it creates a sandbox, so an existing one
never sees a secret set afterwards.

**A runtime command fails to authenticate.** `md2okf` and `make test-sandbox`
need an active `sbx login` session.

**`hit 10 iterations without converging`.** The wiki root hash kept changing.
Raise the cap for one run with `md2okf -n 20 …`, or inspect
`$XDG_STATE_HOME/md2okf/<agent>/sessions` to see what the agent was doing (by
default, `~/.local/state/md2okf/pi/sessions` for Pi).

**`a sandbox called 'md2okf-<agent>' exists but is not recognisably ours`.** Most often
you changed `XDG_STATE_HOME` since the sandbox was built, so the ownership
record it left behind is under the old state root. It can also mean something
else created it — an older release, or a manual `sbx run`. Either way `md2okf`
will not delete a sandbox it cannot prove it owns, and `--fresh` will not either:
run `sbx rm --force md2okf-<agent>` yourself and try again.

**An old `md2okf` sandbox is left over after upgrading.** Releases before
per-agent sandboxes used one sandbox called `md2okf` and a workbench directly
under `$XDG_STATE_HOME/md2okf`. Neither is used any more; remove the sandbox
with `sbx rm --force md2okf`. See [the CHANGELOG](../CHANGELOG.md) for the
workbench files that can go.
