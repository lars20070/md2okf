# Remove the container runtime; flatten the kit to `pi/`

## Context

The repo currently carries **two independent Pi runtimes** that compile the same
OKF wiki: `pi/sandbox/` (Docker Sandbox / sbx) and `pi/container/` (Docker
Compose). They share no code and each keeps its own hand-maintained copy of the
Pi agent config, so every config change has to be made twice and the two
`okf/log.md` formats must never be mixed. The sandbox is already the documented
one to reach for — it lints its own output, dates its log entries, and keeps the
OpenRouter key out of the VM.

Dropping the container runtime removes that duplication, the only Dockerfile and
compose file in the repo, two driver scripts, and the whole hadolint toolchain
(config file, Makefile call, CI install step, CodeRabbit tool entry) that existed
solely to lint `pi/container/Dockerfile`.

With `pi/container/` gone, the `sandbox/` level under `pi/` holds a single child
and no longer distinguishes anything, so the kit moves up to `pi/`. The `files/`
level below it **cannot** be removed: `sbx kit pack --help` and the kit authoring
doc embedded in the `sbx` binary require the kit root to contain `spec.yaml` plus
a `files/` directory with `home/` / `workspace/` children. Verified with
`sbx kit inspect ./pi/sandbox/` → `Files: 5 home, 0 workspace`, discovered purely
by convention (spec.yaml has no `files:` key at all).

Because there is nothing left to disambiguate against, the `-sandbox` suffix is
dropped from the make target and the driver scripts — hard cut, no aliases.

Outcome: one runtime, one config copy, one kit directory, `make wiki`.

## Decisions taken

| | Before | After |
| --- | --- | --- |
| Kit root | `pi/sandbox/` | `pi/` |
| Pi config | `pi/sandbox/files/home/.pi/agent/` | `pi/files/home/.pi/agent/` |
| Compile | `make wiki-sandbox` / `make wiki-container` | `make wiki` (hard cut) |
| Drivers | `scripts/compile-wiki-{sandbox,container}.sh` | `scripts/compile-wiki.sh` |
| Shell | `scripts/bash-{sandbox,container}.sh` | `scripts/bash.sh` |
| README | `## The two runtimes` + comparison tables | fold a short kit/config note into `## How the agent knows what to do`; no dedicated runtime section |

**Keep the sandbox agent config as-is.** Do **not** merge anything from
`pi/container/agent/`. The copies already diverge on purpose (no `bash` → no
lint step, flat undated `okf/log.md`, `read`-tool wording). The sandbox copy is
the surviving source of truth; deleting the container tree discards its
`AGENTS.md` / `SKILL.md` / `settings.json` / `models.json` entirely.

CI's `pi/**` path filter and the "anything under `pi/` or `scripts/`" prose stay
correct unchanged — that is why `pi/` was chosen over a top-level `sandbox/`.

**Non-goals:** no compat shims for old target/script names; no change to kit
`name: pi-kit` or sbx secret setup; no change to `SPEC.md`, `okf/`, `web2md/`,
or the sandbox agent instructions beyond path updates in host docs.

## Implementation order

Do the filesystem moves first, then rewrite every reference to the new paths.
One commit is enough (delete + move + path rewrites are one logical change).

### 1. Delete the container runtime and hadolint

```bash
git rm -r pi/container
git rm scripts/bash-container.sh scripts/compile-wiki-container.sh .hadolint.yaml
```

`pi/container/` is the whole tree (`Dockerfile`, `compose.yaml`, `agent/…`, plus
any untracked `.DS_Store`). Nothing under `pi/sandbox/` references the container
runtime — only [pi/sandbox/spec.yaml:31](../../pi/sandbox/spec.yaml#L31) says
"container", meaning the microVM's own container; leave that wording alone.

### 2. Flatten the kit and rename the sandbox drivers (`git mv`)

```bash
git mv pi/sandbox/spec.yaml pi/spec.yaml
git mv pi/sandbox/files     pi/files
rm -rf pi/sandbox                       # only an untracked .DS_Store left
git mv scripts/compile-wiki-sandbox.sh  scripts/compile-wiki.sh
git mv scripts/bash-sandbox.sh          scripts/bash.sh
```

After this, `sbx kit validate ./pi/` and `sbx kit inspect ./pi/` must work before
any further edits are considered done. An existing local `pi-kit` sandbox is
fine: `compile-wiki.sh` already does `sbx rm --force` before each run, so the
next `make wiki` rebuilds from the new kit root.

### 3. Build / CI

**[Makefile](../../Makefile)**

- Header comment (3–5): drop the "two Pi runtimes … deleting a runtime later is a
  line-level edit" note; state there is one sandbox runtime under `pi/`.
- Drop the `HADOLINT` doc block (13–15) and `HADOLINT ?= hadolint` (21).
- `.PHONY` (25): `lint lint-okf validate test wiki scrape` — no aliases.
- `lint` comment (27–30): drop "and the container Dockerfile" and "One Markdown
  glob per runtime".
- `lint` recipe: remove the `pi/container/agent/**/*.md` glob (37); repoint the
  markdownlint glob (38) and the shellcheck glob (41) to `pi/files/...`; delete
  the `$(HADOLINT) pi/container/Dockerfile` line (43).
- Delete the `wiki-container` target (63–65); rename `wiki-sandbox` → `wiki`
  calling `./scripts/compile-wiki.sh`.

**[.github/workflows/ci.yml](../../.github/workflows/ci.yml)**

- Lint job lead-in (32–36): drop the hadolint clause from the comment that ends
  "shellcheck is pre-installed…; hadolint is downloaded…".
- Delete the whole `Install hadolint` step (53–61) and its comment (53–54).
- Rename step 63 to `Lint (markdownlint, shellcheck, ruff)`.
- `validate-kit` comment (89): `pi/sandbox/spec.yaml` → `pi/spec.yaml`, and drop
  the now-meaningless "Sandbox-only:" prefix.
- Leave the `paths:` filter (7–18) alone — `pi/**` still matches. Do **not** add
  `.hadolint.yaml` / `.coderabbit.yaml` / `.cspell.json` to the filter just for
  this change; they are not CI inputs today.

**[.coderabbit.yaml](../../.coderabbit.yaml)**

- Remove the `**/Dockerfile` (50–57) and `**/compose.yaml` (58–65)
  `path_instructions` — no such files remain. Keep `**/spec.yaml`.
- Remove `tools.hadolint` (136–137).
- Reword the comment at 146–147 ("…and builds a container image") so it no
  longer claims the repo builds an image (API key handling remains).

**[.cspell.json](../../.cspell.json)** — remove `"containerised"` (19) and
`"hadolint"` (22); both become unused everywhere after the Makefile/README cut.

**`.claude/settings.local.json`** (untracked, local only) — drop the
`compile-wiki-container.sh` permission entry; repoint
`Bash(bash -n scripts/compile-wiki-sandbox.sh)` to `scripts/compile-wiki.sh`.
Not part of the commit.

### 4. Scripts

Only three live path strings change; the rest is comment text. Keep the existing
structure — the `repo_root` resolution, the `sbx` presence check, the
`kit_name="pi-kit"` constant and the `</dev/null` guard are all still correct.

- **[scripts/compile-wiki.sh](../../scripts/compile-wiki-sandbox.sh)** — usage
  line to `compile-wiki.sh [md-folder]`; drop "this driver shares no code with
  the container driver" (10) and the "(the container driver needs it too)"
  parenthetical (43) — keep the rest of the `</dev/null` explanation; config
  path comment → `pi/files/home/.pi/agent/`; `kit_name` comment → `pi/spec.yaml`;
  **live**: `--kit ./pi/` (37).
- **[scripts/bash.sh](../../scripts/bash-sandbox.sh)** — usage line; drop the
  container-driver clause (9); `kit_name` comment → `pi/spec.yaml`;
  **live**: `--kit ./pi/` (28).
- **[scripts/validate-spec.sh](../../scripts/validate-spec.sh)** — comment (3) →
  `pi/spec.yaml`; **live**: echo text (22) and
  `sbx kit validate "${repo_root}/pi/"` (23).

### 5. Docs

**[README.md](../../README.md)** — the largest edit. Simplify and shorten.

- L3 and L46: `make wiki-sandbox` → `make wiki`. L39: `pi/spec.yaml`.
- L84–86: "Both drivers name the path to `SKILL.md`…" → singular ("The driver…").
- **Delete `## The two runtimes` entirely** (L88–137): intro, both tables, the
  "edit both by hand" paragraph, the "stay with one runtime" warning, and
  `### The container runtime`. Do **not** replace it with a dedicated runtime
  section.
- **Fold a short kit/config note into `## How the agent knows what to do`**
  (after the skill/`SKILL.md` paragraphs, before `### Model configuration`):
  one short paragraph — kit at `pi/`, Pi config at `pi/files/home/.pi/agent/`,
  copied in at kit build time, so edits land on the fresh sandbox that
  `make wiki` always builds. No tables, no comparison, no second `##`.
- Promote the former children of the deleted section: `### Model configuration,
  sandbox only` → `### Model configuration`; keep `### Using another provider`.
  Both now sit directly under `## How the agent knows what to do`.
- Path rewrites in those subsections: L141, L174, L177, L181 → `pi/files/...`
  and `pi/spec.yaml`. L184: `make wiki`. L167: "Both `models.json` copies
  carry…" → "`models.json` carries…". L172: "Switching the sandbox to it…" →
  "Switching to it…".
- **L245–256** — delete `#### The container runtime, in short` entirely.
- L266: "neither driver calls it" → "the driver does not call it" (or equivalent).
- L267–274: keep the host and sandbox lint bullets (path → `pi/spec.yaml`),
  delete the "In the container" bullet.
- L279: drop `hadolint` from the `make lint` comment. L281: `make validate`
  comment → `pi/spec.yaml`.
- L290–295: "To look inside either runtime" → "To look inside the sandbox", with
  only `./scripts/bash.sh`.
- L285 ("Touch anything under `pi/` or `scripts/`") stays as-is.

**[AGENTS.md](../../AGENTS.md)**

- L8: `pi/files/home/.pi/agent/AGENTS.md`.
- **L32–53** — replace the "two independent Pi runtimes" list, the "either
  runtime compiles the same wiki" warning and the "two config copies are
  deliberately not a single source of truth / edit both by hand" paragraph with
  one paragraph describing the single sandbox runtime: kit at `pi/`, config at
  `pi/files/home/.pi/agent/`, copied in at kit build time so edits only land in
  a fresh sandbox, which `make wiki` always builds.
- L55–59: "Within each config" → "Within the config".
- Commands block: drop `hadolint` from the `make lint` line (64); collapse
  67–68 to `make wiki`; in the second block (74–76) keep only
  `./scripts/bash.sh` and `./scripts/compile-wiki.sh md/other-books`.
- L79–83: drop the `make wiki-container` / `OPENROUTER_API_KEY` sentence and the
  "neither driver" wording if it remains; keep the `sbx secret` pointer. The
  `make lint-okf` sentence becomes "the driver does not call it" (singular).
- L94: `pi/spec.yaml`.

**[web2md/README.md:7](../../web2md/README.md#L7)** — `make wiki-sandbox` →
`make wiki`.

**CLAUDE.md** — no change (`@AGENTS.md` only). **SPEC.md**, **.gitignore**,
**pyproject.toml**, **.markdownlint-cli2.yaml**, **pdf2md/**, **web2md/src/**,
**web2md/tests/** — no changes. The `container` hits in web2md are the CSS class
`devsite-rating-container`; `.cursor/settings.json:10`
(`remote.containers.reopenFolderInContainer`) is an unrelated VS Code setting;
`md/GoogleStyleGuide.md` has incidental "container" prose from the scraped book
— leave it. (Note: `md/` is *not* actually gitignored — the `md/*` rule in
`.gitignore:17` is commented out and `md/GoogleStyleGuide.md` is tracked. That
contradicts `AGENTS.md:15` and `README.md:51`, but it is pre-existing and out of
scope here.)

## Verification

```bash
make lint      # markdownlint + shellcheck + ruff, no hadolint; proves the
               # repointed pi/files globs still match real files
make test      # pytest, offline web2md suite — should be untouched
make validate  # sbx kit validate ./pi/ — must pass before finishing (AGENTS.md)
```

Then confirm the kit still resolves from its new root and still ships all five
config files:

```bash
sbx kit inspect ./pi/          # expect: Name pi-kit, Files: 5 home, 0 workspace
bash -n scripts/compile-wiki.sh scripts/bash.sh scripts/validate-spec.sh
```

Sweep for leftovers. Expected surviving hits only:

- `pi/spec.yaml` — microVM "container" wording
- `web2md/src/web2md.py` — the `devsite-rating-container` CSS class, plus two
  BeautifulSoup `.decompose()` calls that the `compose` pattern also matches
- `web2md/tests/test_cleaning.py` — the same CSS class in fixtures
- `.cursor/settings.json` — VS Code Remote Containers setting

```bash
# Tracked tree only; skip generated/scraped content and local plan notes.
git grep -niE 'container|compose|hadolint|wiki-sandbox|wiki-container|-container\.sh|pi/sandbox' \
  -- ':!.claude/plans/**' ':!md/**' ':!okf/**'
# Expect only the four bullets above. In particular: no pi/sandbox, no
# Dockerfile, no compose.yaml, no hadolint, no wiki-container / *-container.sh.
```

End-to-end (optional, spends OpenRouter credit): with a file in `md/`, run
`make wiki` and check `okf/` is written and `okf/log.md` gains a dated `##`
entry; `./scripts/bash.sh` then
`sbx exec pi-kit -- sh -lc 'echo "$OPENROUTER_API_KEY"'` should print
`proxy-managed`.

CI should go green on all three jobs (`lint`, `test`, `validate-kit`) with the
hadolint step gone.
