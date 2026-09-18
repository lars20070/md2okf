# Replace `okf-lint` with `okfctl`, and migrate the wiki to OKF v0.2

## Context

The wiki compiler currently checks its output with **`okf-lint`** (`@thisismydesign/okf-lint@0.1.0`, npm), wrapped by
`kits/md2okf/files/home/.pi/agent/skills/compile-okf/scripts/lint-okf.sh` and mirrored on the host by `make lint-okf`.
It is a pure checker: Pi hand-writes every `index.md` and `log.md` entry itself.

[`okfctl`](https://github.com/cwest/okfctl) (Apache-2.0, Go single binary, v0.4.0) covers the same ground and more —
spec-floor `validate`, curation-health `lint`, a weakness report (`analyze`), a link graph, **authoring** verbs that
maintain the reserved files and rewrite inbound links on a rename, and a two-phase v0.1 → v0.2 `migrate`. The README
Mermaid diagram at `README.md:37` already says `LINT["okfctl linter"]`, so the repo has been ahead of the code on this.

`SPEC.md` has just been updated to **OKF v0.2** (the upstream text verbatim). The wiki is still v0.1-shaped — root
`index.md` declares `okf_version: "0.1"`, all 14 pages carry a legacy `timestamp:` — so the spec that outranks every
instruction file no longer describes the corpus. Closing that gap is now part of this work.

### Verified against the real wiki (okfctl v0.4.0, linux/arm64)

| Command | Result on `okf/` |
| --- | --- |
| `okfctl validate` | `OK: bundle conforms to the OKF spec floor` (exit 0) |
| `okfctl lint` | `OK: no lint findings` (exit 0) |
| `okfctl analyze` | Useful signal: 1 thin node, 14 uncited nodes, 3 tag-cluster candidates, no orphans |
| `okfctl node mv --dry-run` | Rewrites inbound links **preserving bundle-absolute form** (`/general-principles/…`) |
| `okfctl index build` | Byte-identical to today's indexes **except** links become relative; root frontmatter preserved |
| `okfctl migrate` | 0 deterministic edits, 14 `missing-actor` judgment items; with `--generated-by` all 14 migrate |
| `okfctl log append` | **Incompatible** — prepends a second `# Change Log` H1 with flat `- DATE — msg` bullets |
| Install | Pinned tarball + `checksums.txt` from GitHub releases; SHA-256 verified; **no new egress hosts needed** |

### An upstream bug this plan works around

`okfctl migrate` **truncates timestamps to a bare date**: `timestamp: 2026-08-01T06:28:39Z` becomes
`generated: {by: …, at: 2026-08-01}`, losing the time and the UTC offset that v0.2 §5 requires of every
timestamp-valued key. `okfctl validate` does not catch it, because the floor only checks `type`.

Root cause: `internal/okf/analyze.go:537` `frontmatterTimeString` formats a `time.Time` with the layout `"2006-01-02"`
— correct for analyze's human-readable freshness report, but `migrate.go:134` reuses it to compute the value it
**persists**. It only bites when yaml.v3 parses the value as a `time.Time`, which happens for an *unquoted* ISO
datetime; a *quoted* one stays a string and passes through intact. Our wiki's timestamps are unquoted.

**Verified workaround:** quote the timestamps before migrating, and the full datetime survives —
`generated: {by: pi/qwen3.6-35b-a3b, at: "2026-08-01T06:28:39Z"}`. Stage 3 does this.

**Upstream status:** reported as [cwest/okfctl#171](https://github.com/cwest/okfctl/issues/171) (open, labelled `bug`),
with a fix proposed in [PR #172](https://github.com/cwest/okfctl/pull/172) — **open, not merged**, against `main`. The
PR takes the lossless route of carrying the verbatim source scalar across rather than re-rendering the parsed time, so
quoted and unquoted inputs become identical by construction and a legitimate bare date is left alone. Neither is in
v0.4.0, the version this plan pins, so Stage 3 keeps the quoting pre-step. Once a release contains the fix, bump
`OKFCTL_VERSION` in `kits/md2okf/spec.yaml` and drop that pre-step — it is then redundant, though harmless, since the
fix preserves a quoted value verbatim too.

## Settled decisions

1. `okfctl` **replaces** `okf-lint` — the npm package, its wrapper, and `okf/.okflintrc.json` all go.
2. Pi may run the **authoring** commands (`node new`/`mv`/`rm`, `index build`), not only the read-only ones.
3. Installed in **both** the sandbox (pinned) and on the host (Homebrew).
4. **No `.okf` sidecar.** It is an okfctl artifact, absent from OKF v0.1 *and* v0.2; §12 puts the marker in bundle-root
   `index.md` frontmatter, "the only place frontmatter is permitted in an `index.md`", which the wiki already carries.
5. The frontmatter conventions are enforced by a **small guard script** — no `Type Template` node in the wiki.
6. Generated indexes **adopt okfctl's relative links**; the `prefer-absolute-links` convention retires with `okf-lint`.
7. The wiki **migrates to v0.2** via `okfctl migrate`, recording the actor as **`pi/<model-id>`** (today
   `pi/qwen3.6-35b-a3b`) — §7's `<producer>/<version>` form, matching the spec's own `reference_agent/gemini-2.5-pro`.

### Accepted trade-offs (flagged, chosen deliberately)

- okfctl's floor only requires a non-empty `type`. Everything `okf-lint` enforced beyond that is re-implemented in the
  guard script (Stage 2) or dropped.
- `index.md` files switch to relative links. Spec-legal (§6.1), though it calls absolute the "recommended" form. Node
  **prose** keeps its absolute links — `node mv` preserves whatever form it finds.
- The type-template overlay is **not** used: it is an okfctl invention (its PRD §9, absent from both OKF revisions), it
  only checks field *presence*, and its template node would appear as an entry in the wiki's own `index.md`.
- Migration converts provenance but cannot invent it: the 14 `analyze` "uncited" findings persist, because the pages
  carry an inline `*Source: <url>*` line rather than a `# Citations` list for `migrate` to lift into `sources`. Mapping
  `resource:` into `sources` is wiki-content work for another day.

## Staging

Five stages, ordered so that **`okf-lint` keeps working until its replacement has been proven against it**, and so the
wiki is migrated before Pi starts writing into it. Stages 1–4 are additive: okf-lint stays installed, so a rollback is
reverting that stage's edits and rebuilding. Only Stage 5 removes anything.

| Stage | Does | Pipeline state at the end |
| --- | --- | --- |
| 1 | Install okfctl in the sandbox | Both linters installed; okf-lint still the gate |
| 2 | Build `check-okf.sh` + the guard, prove they agree with okf-lint | New gate exists, not yet wired |
| 3 | Migrate the wiki to v0.2, then tighten the guard | Wiki is v0.2; okf-lint now visibly obsolete |
| 4 | Switch Pi over (skills, conventions) | Pi uses okfctl; okf-lint still installed as fallback |
| 5 | Remove okf-lint; Makefile, docs, CHANGELOG | okfctl only |

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

Same file, two more edits — nothing removed yet:

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

Two new files beside `lint-okf.sh`, which stays for now.

**`…/skills/compile-okf/scripts/check-okf.sh`** — same contract as the script it will replace (`[bundle]` argument
defaulting to `.`, exit `0` clean / `1` findings / `2` usage-or-runtime), shellcheck-clean under `.shellcheckrc`
(`enable=all`, so `[[ ]]`, quote everything, `case` needs a default). Order:

1. `command -v okfctl` and the bundle directory exist, else exit 2.
2. `okfctl validate "$bundle"` — spec floor. **Without `--strict`**: floor violations fail regardless, while git drift
   stays advisory (on the host `okf/` sits in a repo but is gitignored, so `--strict` would be noise).
3. `python3 frontmatter-guard.py "$bundle"` — the conventions below.
4. Dangling-link gate: `okfctl analyze --json "$bundle" | jq -e '.coverage_gaps.dangling_links | length == 0'`.
5. `okfctl lint "$bundle"` — advisory, printed for Pi to act on (orphans, missing-xref, coverage gaps, type hygiene).

**`…/skills/compile-okf/scripts/frontmatter-guard.py`** — stdlib, PyYAML-free (parse the frontmatter block directly, as
`scripts/sync-descriptions.py` does). It walks concept nodes (`*.md` minus the reserved `index.md`/`log.md`):

| Retired `okf-lint` rule | Replacement |
| --- | --- |
| `recommended-title`, `recommended-description` | guard: present and non-blank |
| `recommended-timestamp` | guard: provenance present — `generated.at`, **or** legacy `timestamp` until Stage 3 |
| `timestamp-format` | guard: ISO-8601 with an explicit UTC offset (§5), not a bare date |
| `tags-type` | guard: non-empty list of strings |
| `okf-version-declared` | guard: root `index.md` carries `okf_version` matching the `**Version X.Y**` line in `SPEC.md` |
| `recommended-log`, `log-date-order` | guard: root `log.md` exists; `## YYYY-MM-DD` headings, newest first (§9) |
| `valid-links` | `check-okf.sh` step 4 (okfctl computes it; no duplicate link logic) |
| *(type present)* | `okfctl validate` — the spec floor |
| `prefer-absolute-links` | **dropped** by decision 6 |

Accepting either provenance form in this stage is what lets the guard run against the pre-migration wiki; §13.1
explicitly permits the legacy fallback. Stage 3 tightens it. Reading the expected `okf_version` out of `SPEC.md` keeps
the check honest the next time the spec is updated — which has already happened once.

Both files are the single implementation for host and sandbox: the Stage 5 `make` target calls the same path.

**Host:** `brew install cwest/tap/okfctl`. Homebrew tracks latest while the kit pins 0.4.0, so host and sandbox can
drift — `okfctl version` reports which.

### Check

```bash
make lint                                                    # shellcheck + markdownlint over the new files
kits/md2okf/files/home/.pi/agent/skills/compile-okf/scripts/check-okf.sh ./okf   # expect exit 0
pnpm dlx @thisismydesign/okf-lint ./okf                      # the old gate, for comparison
```

**The equivalence check is the point of this stage:** on today's wiki both gates must agree it is clean. If okf-lint
reports a class of finding `check-okf.sh` cannot see, the guard has a gap — fix it before Stage 3.

Then the negative checks, on a throwaway copy (`cp -r okf /tmp/okf-check`), since they are the whole reason the guard
exists. Each must make `check-okf.sh` exit 1, and `okfctl validate` alone must **not** catch any of them:

- break a timestamp into a non-ISO value, and separately into a bare date (the upstream-bug shape);
- replace a `tags` list with a bare string;
- point an `index.md` entry at a page that does not exist.

---

## Stage 3 — Migrate the wiki to OKF v0.2

`okf/` is gitignored, so there is no git safety net here. **Take a copy first** — `cp -r okf /tmp/okf-premigration` —
and keep it until the stage's checks pass.

1. **Quote the timestamps**, to dodge the truncation bug documented above:

   ```bash
   find okf -name '*.md' -exec sed -i '' -E "s/^timestamp: ([0-9T:+-]+Z?)$/timestamp: '\1'/" {} +
   ```

   (GNU `sed` drops the `''` after `-i`.) Confirm with `grep -rh '^timestamp:' okf | head`.

2. **Phase 1 — plan (pure read):**

   ```bash
   okfctl migrate okf --generated-by "pi/qwen3.6-35b-a3b" --plan /tmp/migrate-plan.json
   ```

   Expect `14 node(s) with deterministic edits (14 edit(s)), 0 judgment item(s)`. A non-zero judgment count means
   something changed since this plan was written — read `/tmp/migrate-plan.json` before going further. Write the plan
   **outside** `okf/`, so the migrator's own artifact never lands in the wiki.

3. **Phase 2 — preview, then apply:**

   ```bash
   okfctl migrate okf --apply --plan /tmp/migrate-plan.json --dry-run   # byte-identical to the real apply
   okfctl migrate okf --apply --plan /tmp/migrate-plan.json
   ```

4. **Tighten the guard:** `generated.by` (an actor in §7 form) and `generated.at` are now required; a bare legacy
   `timestamp` becomes a finding rather than an accepted fallback.

5. **Update `kits/md2okf/files/home/.pi/agent/AGENTS.md`** so new pages are written the migrated way. Its documented
   content-page frontmatter (`type`, `title`, `description`, `tags`) never mentioned a timestamp at all — the wiki only
   has them because okf-lint demanded them, per `okf/log.md`. Add `generated: { by: pi/<model-id>, at: <ISO-8601 UTC> }`
   to that block with the double-quoting rule the section already applies to `title` and `description`.

### Check

```bash
grep -rh '^generated:' okf | sort -u        # full datetimes, not bare dates — the bug this stage works around
okfctl bundle info okf                      # okf_version: 0.2
head -3 okf/index.md                        # root marker bumped to "0.2"
check-okf.sh ./okf                          # the tightened guard, exit 0
diff -rq /tmp/okf-premigration okf          # only the 14 frontmatter blocks and index.md should differ
```

Expect `pnpm dlx @thisismydesign/okf-lint ./okf` to start failing `recommended-timestamp` on every page from here on.
That is not a regression — it is okf-lint checking a v0.1 field that v0.2 §13.1 superseded, and it is the clearest
possible signal that the old gate has outlived its usefulness.

---

## Stage 4 — Switch Pi over to okfctl

### Command policy

**Allowed:** `validate`, `lint`, `analyze`, `bundle info`, `node list|show|new|mv|rm`, `index build|check`, `search`,
`graph export`, `template list|show`, `version`.

**Forbidden, with the reason stated in the skill:**

- `log append` / `log show` — writes a second `# Change Log` H1 with flat `- DATE — msg` bullets. §9 requires ISO-8601
  date *headings*, newest first, and SPEC outranks every instruction file. Pi keeps writing `log.md` by hand.
- `migrate` — a one-off developer operation, done in Stage 3 and needing the timestamp-quoting workaround. Nothing is
  left for Pi to migrate, and running it unattended risks re-truncating any page still carrying a legacy `timestamp`.
- `eval` — grades on `epistemic`/`authority` keys that appear in neither OKF revision; pure noise here.
- `serve` (web server), `registry` / `connect` (network), `okfctl-search` / `lint --semantic` (model download).

One gotcha the skill must call out: `node new` writes `created`/`modified`, **not** the `generated: { by, at }` this
wiki uses, so Pi must complete the frontmatter afterwards — the guard catches it if it forgets.

### Files

- **New tool skill** `kits/md2okf/files/home/.pi/agent/skills/curate-okf/SKILL.md`, following the seven-part house
  template exemplified by `skills/size-okf/SKILL.md` (46–59 lines: two-key frontmatter, `# … with \`okfctl\`` H1, the
  "the skill name is `curate-okf`; the binary is `okfctl` — never shell the skill id" sentence, `## Invocation` with a
  `bash` block and the verbatim `- Exit codes:` line, `## Workflow`, `## Reading the output`, `## Limits`). The
  allowed/forbidden split above lives here.
- **`…/.pi/agent/AGENTS.md`** — add `curate-okf` to the `- Available skills:` list and to the "Tool skills … are read
  when the work calls for them" sentence; fix the `okf-lint` mention in the `log.md` bullet; and amend the
  "Write cross-links and index links as **bundle-absolute** paths" rule, which decision 6 retires for *index* links
  while keeping it for page prose.
- **`…/skills/compile-okf/SKILL.md`** — rewrite the final section `## Check your output with \`okf-lint\`` (lines
  90–135) to call `~/.pi/agent/skills/compile-okf/scripts/check-okf.sh`, keep the "end your final message with the
  summary line" rule, and point at `curate-okf` for the authoring verbs. Drop the `.okflintrc.json` paragraph.
- **`kits/md2okf/spec.yaml`** — point the `chmod 0755` step at `check-okf.sh` (add it; `lint-okf.sh` may keep its own
  chmod until Stage 5).
- **`tests/test-sandbox-guest.sh`** — add `check_exec` for `check-okf.sh` and `check_file` lines for
  `frontmatter-guard.py` and `skills/curate-okf/SKILL.md`.

### Check

```bash
make validate
sbx rm --force md2okf && make test-sandbox   # new skill + scripts land in the VM
cp -r okf /tmp/okf-prerun                    # okf/ is gitignored; this is the only diff baseline
make wiki                                    # a real compile with the new gate
diff -rq /tmp/okf-prerun okf                 # what actually moved
```

What to look for, in order of importance:

1. The run finishes and Pi's final message carries the `check-okf.sh` summary line — the gate is wired and passing.
2. The only structural change is `index.md` links going relative, and any page Pi genuinely rewrote carrying a fresh
   `generated` block. Anything else moving is a surprise worth understanding before Stage 5.
3. `merkleokf --nolog -L 0 okf` settles between consecutive runs, as `scripts/compile-okf.sh`'s Ralph loop expects —
   a gate that reports differently each run would never converge.

---

## Stage 5 — Remove okf-lint and finish the documentation

### Removals

- **`kits/md2okf/spec.yaml`** — drop `OKF_LINT_VERSION` and the `npm_install_retry "@thisismydesign/okf-lint@…"` line;
  update the `# npm: pi-coding-agent, okf-lint, markdownlint-cli2, cspell.` comment above `registry.npmjs.org:443`;
  drop the `okf-lint` bullet from `## Installed tools`; drop the `lint-okf.sh` chmod step.
- Delete **`…/skills/compile-okf/scripts/lint-okf.sh`** and **`okf/.okflintrc.json`**, and remove the
  `!okf/.okflintrc.json` un-ignore from `.gitignore`.
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
- **`CHANGELOG.md`** — under `## [Unreleased]`: `### Added` okfctl + the `curate-okf` skill, `### Changed` the wiki
  migrated to OKF v0.2, `### Removed` okf-lint. `VERSION` stays `0.1.0` (the `make lint` check only compares it to the
  first `[X.Y.Z]` heading).

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

The rebuild here is the one that matters: Stages 1–4 always ran on a VM that still had okf-lint installed, so this is
the first run that proves the pipeline is genuinely free of it. `CHANGELOG.md` is excluded from the `rg` sweep because
the removal entry legitimately names the tool.

## Follow-ups (not in this plan)

- Watch [cwest/okfctl#171](https://github.com/cwest/okfctl/issues/171) / [#172](https://github.com/cwest/okfctl/pull/172).
  When the fix ships in a release, bump the pinned `OKFCTL_VERSION` and drop Stage 3's timestamp-quoting pre-step.
- Lift each page's `resource:` into a v0.2 `sources` entry, which would clear the 14 `analyze` "uncited" findings.
