# Replace `okf-lint` with `okfctl`

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
  guard script (Stage 2) or dropped.
- `index.md` files switch to relative links on the next run. Spec-legal (SPEC §5.2), though §5.1 calls absolute the
  "recommended" form. Node **prose** keeps its absolute links — `node mv` preserves whatever form it finds.
- The type-template overlay is **not** used: it is an okfctl invention (its PRD §9, absent from OKF v0.1 *and* v0.2),
  it only checks field *presence*, and its template node would appear as an entry in the wiki's own `index.md`.

## Staging

Four stages, ordered so that **`okf-lint` keeps working until its replacement has been proven against it**. Stages 1–3
are additive: okf-lint stays installed and wired, so a rollback is reverting that stage's edits and rebuilding. Only
Stage 4 removes anything.

| Stage | Adds | Removes | Pipeline state at the end |
| --- | --- | --- | --- |
| 1 | okfctl in the sandbox | — | Both linters installed; okf-lint still the gate |
| 2 | `.okf` sidecar, check script + guard, host okfctl | — | New gate exists and agrees with the old one; not yet wired |
| 3 | `curate-okf` skill; compile-okf switched to the new gate | — | Pi uses okfctl; okf-lint still installed as fallback |
| 4 | Makefile target, docs, CHANGELOG | okf-lint, `lint-okf.sh`, `.okflintrc.json` | okfctl only |

> **Note:** `okf/.okflintrc.json` is already deleted in the working tree. That is Stage 4 work done early; it is
> harmless (okf-lint falls back to default severities), but keep it in mind when reading Stage 2's cross-check — see
> the note there.

---

## Stage 1 — Install okfctl in the sandbox (additive)

### `kits/md2okf/spec.yaml`

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

Same file, two more edits — and nothing removed yet:

- In `agentInstructions.content` → `## Installed tools`, add
  `` - `okfctl` — OKF bundle tool: validate, lint, analyze, and the authoring verbs (the curate-okf skill covers it) ``
  **beside** the existing `okf-lint` bullet.
- **No `permissions.network.allow` change** — `github.com:443` and `objects.githubusercontent.com:443` are already
  listed for `mq`; extend that comment to name okfctl too.

### `tests/test-sandbox-guest.sh`

Add `check okfctl` under the pinned-release-binary comment next to `check mq`. Leave `check okf-lint` in place.

### Check

```bash
make validate                               # kit spec schema — mandatory after any kits/ change
sbx rm --force md2okf && make test-sandbox  # must pass with BOTH okfctl and okf-lint listed ok
```

The rebuild is the point of this stage: it proves the download, checksum and architecture mapping work through the
sandbox proxy before anything depends on them. If it fails here, nothing else has moved.

---

## Stage 2 — Build the replacement gate and prove it agrees with okf-lint

### `okf/.okf`

Add the tracked sidecar containing `okf_version: 0.1` — otherwise `okfctl bundle info` silently reports 0.2. Update
`.gitignore` to un-ignore it (`!okf/.okf`), alongside the existing `okf/*` rule.

### Two new files beside `lint-okf.sh` (which stays, for now)

**`…/skills/compile-okf/scripts/check-okf.sh`** — same contract as the script it will replace (`[bundle]` argument
defaulting to `.`, exit `0` clean / `1` findings / `2` usage-or-runtime), and shellcheck-clean under `.shellcheckrc`
(`enable=all`, so `[[ ]]`, quote everything, `case` needs a default). Order:

1. `command -v okfctl` and the bundle directory exist, else exit 2.
2. `okfctl validate "$bundle"` — spec floor. **Without `--strict`**: floor violations fail regardless, while git drift
   stays advisory (on the host `okf/` sits in a repo but is gitignored, so `--strict` would be noise).
3. `python3 frontmatter-guard.py "$bundle"` — the conventions below.
4. Dangling-link gate: `okfctl analyze --json "$bundle" | jq -e '.coverage_gaps.dangling_links | length == 0'`.
5. `okfctl lint "$bundle"` — advisory, printed for Pi to act on (orphans, missing-xref, coverage gaps, type hygiene).

**`…/skills/compile-okf/scripts/frontmatter-guard.py`** — stdlib, PyYAML-free (parse the frontmatter block directly, as
`scripts/sync-descriptions.py` does). It walks concept nodes (`*.md` minus the reserved `index.md`/`log.md`) and checks:

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

Both files are the single implementation for host and sandbox: the Stage 4 `make` target calls the same path.

### Host

`brew install cwest/tap/okfctl`. Homebrew tracks latest while the kit pins 0.4.0, so host and sandbox can drift —
`okfctl version` reports which.

### Check

```bash
make lint                                                    # shellcheck + markdownlint over the new files
okfctl bundle info ./okf                                     # expect okf_version: 0.1 from the new sidecar
kits/md2okf/files/home/.pi/agent/skills/compile-okf/scripts/check-okf.sh ./okf   # expect exit 0
pnpm dlx @thisismydesign/okf-lint ./okf                      # the old gate, for comparison
```

**The equivalence check is the point of this stage:** on today's wiki both gates must agree it is clean. If okf-lint
reports findings that `check-okf.sh` misses, the guard has a gap — fix it before Stage 3. (With `.okflintrc.json`
already deleted, okf-lint runs at default severities, so read its output qualitatively: no *new* class of complaint
should appear that the guard cannot see.)

Then the negative checks, on a throwaway copy — `cp -r okf /tmp/okf-check` — since they are the whole reason the guard
exists. Each must make `check-okf.sh` exit 1, and `okfctl validate` alone must **not** catch any of them:

- break a `timestamp` into a non-ISO value;
- replace a `tags` list with a bare string;
- point an `index.md` entry at a page that does not exist.

---

## Stage 3 — Switch Pi over to okfctl

### Command policy

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

### Files

- **New tool skill** `kits/md2okf/files/home/.pi/agent/skills/curate-okf/SKILL.md`, following the seven-part house
  template exemplified by `skills/size-okf/SKILL.md` (46–59 lines: two-key frontmatter, `# … with \`okfctl\`` H1, the
  "the skill name is `curate-okf`; the binary is `okfctl` — never shell the skill id" sentence, `## Invocation` with a
  `bash` block and the verbatim `- Exit codes:` line, `## Workflow`, `## Reading the output`, `## Limits`). The
  allowed/forbidden split above lives here.
- **`kits/md2okf/files/home/.pi/agent/AGENTS.md`** — add `curate-okf` to the `- Available skills:` list and to the
  "Tool skills … are read when the work calls for them" sentence; fix the `okf-lint` mention at line 83.
- **`…/skills/compile-okf/SKILL.md`** — rewrite the final section `## Check your output with \`okf-lint\`` (lines
  90–135) to call `~/.pi/agent/skills/compile-okf/scripts/check-okf.sh`, keep the "end your final message with the
  summary line" rule, and point at `curate-okf` for the authoring verbs. Drop the `.okflintrc.json` paragraph.
- **`kits/md2okf/spec.yaml`** — point the `chmod 0755` step at `check-okf.sh` (add it; `lint-okf.sh` may keep its own
  chmod until Stage 4).
- **`tests/test-sandbox-guest.sh`** — add `check_exec` for `check-okf.sh` and `check_file` lines for
  `frontmatter-guard.py` and `skills/curate-okf/SKILL.md`.

### Check

```bash
make validate
sbx rm --force md2okf && make test-sandbox   # new skill + scripts land in the VM
merkleokf ./okf -L 1                         # record hashes BEFORE the run
make wiki                                    # a real compile with the new gate
merkleokf ./okf -L 1                         # compare: what actually moved
git diff --stat -- okf                       # okf/ is gitignored; use `git diff --no-index` against a pre-run copy
```

What to look for, in order of importance:

1. The run finishes and Pi's final message carries the `check-okf.sh` summary line — the gate is wired and passing.
2. The only structural change to the wiki is `index.md` links going relative. Anything else moving is a surprise worth
   understanding before Stage 4.
3. As a last cross-check, run `pnpm dlx @thisismydesign/okf-lint ./okf` once more. Expect its **only** remaining
   complaints to be `prefer-absolute-links` on the regenerated indexes — that is the one rule being retired on purpose.
   Any other finding means the new gate let something through.

---

## Stage 4 — Remove okf-lint and finish the documentation

### Removals

- **`kits/md2okf/spec.yaml`** — drop `OKF_LINT_VERSION` and the `npm_install_retry "@thisismydesign/okf-lint@…"` line;
  update the `# npm: pi-coding-agent, okf-lint, markdownlint-cli2, cspell.` comment above `registry.npmjs.org:443`;
  drop the `okf-lint` bullet from `## Installed tools`; drop the `lint-okf.sh` chmod step.
- Delete **`…/skills/compile-okf/scripts/lint-okf.sh`**.
- Delete **`okf/.okflintrc.json`** (already done in the working tree) and remove its `!okf/.okflintrc.json` un-ignore
  from `.gitignore`.
- **`tests/test-sandbox-guest.sh`** — drop `check okf-lint` and the `check_exec` for `lint-okf.sh`.

### Host wiring and prose

- **`Makefile`** — replace the `lint-okf` target (`pnpm dlx @thisismydesign/okf-lint ./okf`) with `check-okf`, invoking
  `kits/md2okf/files/home/.pi/agent/skills/compile-okf/scripts/check-okf.sh ./okf`. Keep it out of `make lint` and CI
  for the existing reason (`okf/` is gitignored output). Update `.PHONY`.
- **`.cspell.json`** — add `okfctl` (and `cwest`). `kits/**` is not in `ignorePaths`, so the new `SKILL.md` is
  spell-checked.
- **Docs**: `README.md` (the Mermaid `LINT` node is now correct — update the caption prose, Requirements, the mounts
  and layout tables), root `AGENTS.md` (command blocks + the skills-vs-`AGENTS.md` split), `CONTRIBUTING.md` (command
  list, Helper CLIs table, skill roster, "Linting the wiki" → okfctl), `kits/md2okf/README.md` (pinned installs).
- **`CHANGELOG.md`** — under `## [Unreleased]`: `### Added` okfctl + the `curate-okf` skill, `### Removed` okf-lint.
  `VERSION` stays `0.1.0` (the `make lint` check only compares it to the first `[X.Y.Z]` heading).

Not in scope: `scripts/sync-descriptions.py` becomes largely redundant once `index build` owns the descriptions, but it
is already unwired from the Makefile — leave it.

### Check

```bash
rg -n 'okf-lint|okflintrc|lint-okf' -g '!.claude/**' -g '!CHANGELOG.md'   # expect no hits
make lint                                    # cspell will catch an unregistered `okfctl`
make validate
sbx rm --force md2okf && make test-sandbox   # proves nothing still depends on okf-lint
make check-okf                               # host path, exit 0
make wiki                                    # full compile on a sandbox that has never had okf-lint
```

The rebuild here is the one that matters: Stages 1–3 always ran on a VM that still had okf-lint installed, so this is
the first run that proves the pipeline is genuinely free of it. `CHANGELOG.md` is excluded from the `rg` sweep because
the removal entry legitimately names the tool.
