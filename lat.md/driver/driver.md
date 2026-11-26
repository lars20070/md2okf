# Driver

The `md2okf` host driver in [[src/md2okf]]: a stdlib-only Python package that stages a run, drives one sandboxed agent and mirrors the wiki out.

Each concern has one owner. `cli` orchestrates and maps failures to exit codes. `compile` resolves documents and loops until the wiki converges. `workbench` stages the fixed host tree and decides the sandbox lifecycle. `sandbox` is the only module that talks to `sbx`. `agents` and `protocols` hold everything that differs between Pi, Claude Code and Codex, so the generic modules never branch on the agent.

- [[cli]] — command-line modes, option rules, exit codes and output streams.
- [[compile-loop]] — document resolution, the Ralph loop, convergence and per-turn verdicts.
- [[workbench]] — the fixed staging tree, its mounts, the run lock and output adoption.
- [[sandbox]] — the sbx seam, the configuration fingerprint and the create-or-reuse decision.
- [[agents]] — the agent contract, the registry and each agent's event-stream verdict.
