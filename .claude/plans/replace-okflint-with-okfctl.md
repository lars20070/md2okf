# Add `okfctl` to the md2okf sandbox toolchain

## Context

The wiki compiler currently checks its output with **`okf-lint`** (`@thisismydesign/okf-lint@0.1.0`, npm), wrapped by
`kits/md2okf/files/home/.pi/agent/skills/compile-okf/scripts/lint-okf.sh` and mirrored on the host by `make lint-okf`.
It is a pure checker: Pi hand-writes every `index.md` and `log.md` entry itself.

[`okfctl`](https://github.com/cwest/okfctl) (Apache-2.0, Go single binary, v0.4.0) covers the same ground and more —
spec-floor `validate`, curation-health `lint`, a weakness report (`analyze`), a link graph, and **authoring** verbs that
maintain the reserved files and rewrite inbound links on a rename. The README Mermaid diagram at `README.md:37` already
says `LINT["okfctl linter"]`, so the repo has been ahead of the code on this.

The decision is to **replace `okf-lint` with `okfctl`** and let Pi use the authoring commands, not just the checks.

### Verified against the real wiki (okfctl v0.4.0, linux/arm64)

| Command | Result on `okf/` |
| --- | --- |
| `okfctl validate` | `OK: bundle conforms to the OKF spec floor` (exit 0) |
| `okfctl lint` | `OK: no lint findings` (exit 0) |
| `okfctl analyze` | Useful signal: 1 thin node, 14 uncited nodes, 3 tag-cluster candidates, no orphans |
| `okfctl node mv --dry-run` | Rewrites inbound links **preserving bundle-absolute form** (`/general-principles/…`) |
| `okfctl index build` | Byte-identical to today's indexes **except** links become relative; root frontmatter preserved |
| `okfctl log append` | **Incompatible** — prepends a second `# Change Log` H1 with flat `- DATE — msg` bullets |
| Install | Pinned tarball + `checksums.txt` from GitHub releases; SHA-256 verified; **no new egress hosts needed** |

## Settled decisions

1. `okfctl` **replaces** `okf-lint` — the npm package, its wrapper, and `okf/.okflintrc.json` all go.
2. Pi may run the **authoring** commands (`node new`/`mv`/`rm`, `index build`), not only the read-only ones.
3. Installed in **both** the sandbox (pinned) and on the host (Homebrew).
4. The wiki gains a tracked **`okf/.okf`** sidecar declaring `okf_version: 0.1`.
5. The frontmatter conventions are enforced by a **small guard script** — no `Type Template` node in the wiki.
6. Generated indexes **adopt okfctl's relative links**; the `prefer-absolute-links` convention retires with `okf-lint`.

### Accepted trade-offs (flagged, chosen deliberately)

- okfctl's floor only requires a non-empty `type`. Everything `okf-lint` enforced beyond that is re-implemented in the
  guard script (below) or dropped.
- `index.md` files switch to relative links on the next run. Spec-legal (SPEC §5.2), though §5.1 calls absolute the
  "recommended" form. Node **prose** keeps its absolute links — `node mv` preserves whatever form it finds.
- The type-template overlay is **not** used: it is an okfctl invention (its PRD §9, absent from OKF v0.1 *and* v0.2),
  it only checks field *presence*, and its template node would appear as an entry in the wiki's own `index.md`.

## 1. Install okfctl

### Sandbox — `kits/md2okf/spec.yaml`

Add a `setup.install` step cloned from the existing **`mq`** step (same file, `user: "1000"`, pinned + checksummed,
`install -m 0755` into `$HOME/.local/bin`). Two differences from `mq`: the asset is a **tarball**, and the
`checksums.txt` second column is a plain filename, so the `awk` match is `$2 == "$archive"`.

```yaml
    # No apt/uv/npm package; fetched as a pinned, checksummed release archive.
    - command: |
        set -eu
        OKFCTL_VERSION=0.4.0

        case "$(uname -m)" in
          x86_64) OKFCTL_ARCH=amd64 ;;
          aarch64) OKFCTL_ARCH=arm64 ;;
          *)
            echo "okfctl: unsupported architecture: $(uname -m)" >&2
            exit 1
            ;;
        esac

        tmp=$(mktemp -d)
        archive="okfctl_${OKFCTL_VERSION}_linux_${OKFCTL_ARCH}.tar.gz"
        base="https://github.com/cwest/okfctl/releases/download/v${OKFCTL_VERSION}"
        curl -fsSL -o "$tmp/$archive" "${base}/${archive}"
        curl -fsSL -o "$tmp/checksums.txt" "${base}/checksums.txt"

        expected=$(awk -v f="$archive" '$2 == f { print $1 }' "$tmp/checksums.txt")
        actual=$(sha256sum "$tmp/$archive" | awk '{ print $1 }')
        if [ -z "$expected" ] || [ "$expected" != "$actual" ]; then
          echo "okfctl: checksum mismatch for ${archive}" >&2
          exit 1
        fi

        tar -xzf "$tmp/$archive" -C "$tmp" okfctl
        mkdir -p "$HOME/.local/bin"
        install -m 0755 "$tmp/okfctl" "$HOME/.local/bin/okfctl"
        rm -rf "$tmp"
      user: "1000"
      description: Install okfctl (OKF bundle tool)
```

Extract **only `okfctl`** — the archive also carries `okfctl-search`, whose semantic index needs a model2vec download
from a host that is not allowlisted. Leave it out.

Same file, three more edits:

- Drop `OKF_LINT_VERSION` and the `npm_install_retry "@thisismydesign/okf-lint@…"` line from the npm step; update the
  `# npm: pi-coding-agent, okf-lint, markdownlint-cli2, cspell.` comment above `registry.npmjs.org:443`.
- In `agentInstructions.content` → `## Installed tools`, replace the `okf-lint` bullet with
  `` - `okfctl` — OKF bundle tool: validate, lint, analyze, and the authoring verbs (the curate-okf skill covers it) ``.
- Point the `chmod 0755` step at the renamed wrapper (§2).
- **No `permissions.network.allow` change** — `github.com:443` and `objects.githubusercontent.com:443` are already
  listed for `mq`; extend that comment to name okfctl too.

### Host

`brew install cwest/tap/okfctl`, documented in `README.md` (Requirements) and `CONTRIBUTING.md`. Note the caveat in
both: Homebrew tracks latest while the kit pins 0.4.0, so host and sandbox can drift — `okfctl version` reports which.

## 2. Replace the wrapper with a check script + guard

Delete `…/skills/compile-okf/scripts/lint-okf.sh`; add two files beside it:

**`check-okf.sh`** — same contract as the script it replaces (`[bundle]` argument defaulting to `.`, exit `0` clean /
`1` findings / `2` usage-or-runtime), and shellcheck-clean under `.shellcheckrc` (`enable=all`, so `[[ ]]`, quote
everything, `case` needs a default). Order:

1. `command -v okfctl` and the bundle directory exist, else exit 2.
2. `okfctl validate "$bundle"` — spec floor. **Without `--strict`**: floor violations fail regardless, while git drift
   stays advisory (on the host `okf/` sits in a repo but is gitignored, so `--strict` would be noise).
3. `python3 frontmatter-guard.py "$bundle"` — the conventions below.
4. Dangling-link gate: `okfctl analyze --json "$bundle" | jq -e '.coverage_gaps.dangling_links | length == 0'`.
5. `okfctl lint "$bundle"` — advisory, printed for Pi to act on (orphans, missing-xref, coverage gaps, type hygiene).

**`frontmatter-guard.py`** — stdlib + PyYAML-free (parse the frontmatter block directly, as `scripts/sync-descriptions.py`
does, or reuse its approach). It walks concept nodes (`*.md` minus the reserved `index.md`/`log.md`) and checks:

| Retired `okf-lint` rule | Replacement |
| --- | --- |
| `recommended-title`, `recommended-description`, `recommended-timestamp` | guard: present and non-blank |
| `timestamp-format` | guard: ISO-8601 UTC, `YYYY-MM-DDTHH:MM:SSZ` |
| `tags-type` | guard: non-empty list of strings |
| `okf-version-declared` | guard: root `index.md` frontmatter carries `okf_version`, and it matches `.okf` |
| `recommended-log`, `log-date-order` | guard: root `log.md` exists; `## YYYY-MM-DD` headings, newest first (SPEC §7) |
| `valid-links` | `check-okf.sh` step 4 (okfctl computes it; no duplicate link logic) |
| *(type present)* | `okfctl validate` — the spec floor |
| `prefer-absolute-links` | **dropped** by decision 6 |

Both files are the single implementation for host and sandbox: the host `make` target calls the same path.

## 3. Command policy for Pi

**Allowed:** `validate`, `lint`, `analyze`, `bundle info`, `node list|show|new|mv|rm`, `index build|check`, `search`,
`graph export`, `template list|show`, `version`.

**Forbidden, with the reason stated in the skill:**

- `log append` / `log show` — writes a second `# Change Log` H1 with flat `- DATE — msg` bullets. SPEC §7 requires
  ISO-8601 date *headings*, newest first, and SPEC outranks every instruction file. Pi keeps writing `log.md` by hand.
- `migrate` — would convert the bundle to v0.2; `SPEC.md` pins v0.1.
- `eval` — grades on `epistemic`/`authority` keys that exist in neither v0.1 nor this wiki; pure noise here.
- `serve` (web server), `registry` / `connect` (network), `okfctl-search` / `lint --semantic` (model download).

One gotcha the skill must call out: `node new` writes v0.2 `created`/`modified` provenance, **not** the wiki's
`timestamp`, so Pi must complete the frontmatter afterwards — the guard catches it if it forgets.

## 4. Skill and instruction changes

- **New tool skill** `kits/md2okf/files/home/.pi/agent/skills/curate-okf/SKILL.md`, following the seven-part house
  template exemplified by `skills/size-okf/SKILL.md` (46–59 lines: two-key frontmatter, `# … with \`okfctl\`` H1, the
  "the skill name is `curate-okf`; the binary is `okfctl` — never shell the skill id" sentence, `## Invocation` with a
  `bash` block and the verbatim `- Exit codes:` line, `## Workflow`, `## Reading the output`, `## Limits`). The
  allowed/forbidden split from §3 lives here.
- **`kits/md2okf/files/home/.pi/agent/AGENTS.md`** — add `curate-okf` to the `- Available skills:` list and to the
  "Tool skills … are read when the work calls for them" sentence; fix the `okf-lint` mention at line 83.
- **`…/skills/compile-okf/SKILL.md`** — rewrite the final section `## Check your output with \`okf-lint\`` (lines
  90–135) to call `~/.pi/agent/skills/compile-okf/scripts/check-okf.sh`, keep the "end your final message with the
  summary line" rule, and point at `curate-okf` for the authoring verbs. Drop the `.okflintrc.json` paragraph.

## 5. Wiki changes

- Add tracked **`okf/.okf`** containing `okf_version: 0.1` — otherwise `okfctl bundle info` silently reports 0.2.
- Delete **`okf/.okflintrc.json`**.
- `.gitignore`: swap the `!okf/.okflintrc.json` un-ignore for `!okf/.okf`.
- Expect the three `index.md` files to switch to relative links on the next `make wiki`. That is the intended diff.

## 6. Host wiring, docs, lint config

- **`Makefile`** — replace the `lint-okf` target (`pnpm dlx @thisismydesign/okf-lint ./okf`) with `check-okf`, invoking
  `kits/md2okf/files/home/.pi/agent/skills/compile-okf/scripts/check-okf.sh ./okf`. Keep it out of `make lint` and CI
  for the existing reason (`okf/` is gitignored output). Update `.PHONY`.
- **`tests/test-sandbox-guest.sh`** — drop `check okf-lint`; add `check okfctl` under the pinned-release-binary comment
  next to `check mq`; swap the `check_exec` for `lint-okf.sh` to `check-okf.sh`; add `check_file` lines for
  `frontmatter-guard.py` and `skills/curate-okf/SKILL.md`. The file's stated contract — the tool list must match both
  lists in `spec.yaml` — is what makes this mandatory.
- **`.cspell.json`** — add `okfctl` (and `cwest`). `kits/**` is not in `ignorePaths`, so the new `SKILL.md` is spell-checked.
- **Docs**: `README.md` (the Mermaid `LINT` node is now correct — update the caption prose, Requirements, the mounts and
  layout tables), root `AGENTS.md` (command blocks + the skills-vs-`AGENTS.md` split), `CONTRIBUTING.md` (command list,
  Helper CLIs table, skill roster, "Linting the wiki" → okfctl), `kits/md2okf/README.md` (pinned installs).
- **`CHANGELOG.md`** — under `## [Unreleased]`: `### Added` okfctl + the `curate-okf` skill, `### Removed` okf-lint.
  `VERSION` stays `0.1.0` (the `make lint` check only compares it to the first `[X.Y.Z]` heading).

Not in scope: `scripts/sync-descriptions.py` becomes largely redundant once `index build` owns the descriptions, but it
is already unwired from the Makefile — leave it.

## Verification

```bash
make validate                              # kit spec schema — mandatory after any kits/ change
make lint                                  # markdownlint + cspell + shellcheck over the new files
sbx rm --force md2okf && make test-sandbox # rebuild: proves okfctl installs and the skills land
make check-okf                             # host path, against the current okf/
make wiki                                  # full compile; indexes should come back relative
```

Then, inside the sandbox (`./scripts/bash.sh`), confirm the agent-facing behaviour:

```bash
okfctl version && okfctl bundle info .     # expect okf_version: 0.1 from the new .okf sidecar
~/.pi/agent/skills/compile-okf/scripts/check-okf.sh   # expect exit 0 on a clean wiki
okfctl analyze .                           # the advisory report Pi is meant to act on
```

Negative checks worth running once, since they are the whole reason for the guard: break a `timestamp` format, drop a
`tags` list to a string, and point an index entry at a missing page — each must make `check-okf.sh` exit 1, and
`okfctl validate` alone must **not** catch any of them.
