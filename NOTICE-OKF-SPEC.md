# Third-party notice: the Open Knowledge Format specification

md2okf itself is MIT-licensed — see [LICENSE](LICENSE). This notice covers the
one third-party file it redistributes.

`SPEC.md` at the repository root is the **Open Knowledge Format (OKF) v0.2
specification**. It is not part of md2okf: it is the format md2okf compiles
into, and the agent reads it at the start of every run, which is why it ships
inside the wheel and the source distribution as well as living in the
repository.

| | |
| --- | --- |
| Source | <https://github.com/GoogleCloudPlatform/open-knowledge-format> |
| File | `SPEC.md` (repository root) |
| Revision | `0b87c52c6ef999286c745e19998fdfcd03d5dbee` |
| Licence | Apache License 2.0 — full text in [LICENSE-OKF-SPEC.txt](LICENSE-OKF-SPEC.txt) |
| Modified | No. Included verbatim, byte for byte. |

Upstream carries no `NOTICE` file, so there is none to propagate; this file
exists to satisfy the attribution and licence-copy obligations of Apache-2.0
§4(a) and §4(c) for the bundled copy.

## Keeping it current

`SPEC.md` is a vendored copy, so it does not update itself. To refresh it,
replace the file, update the revision above, and re-check the licence:

```bash
curl -sL https://raw.githubusercontent.com/GoogleCloudPlatform/open-knowledge-format/main/SPEC.md -o SPEC.md
curl -s "https://api.github.com/repos/GoogleCloudPlatform/open-knowledge-format/commits?path=SPEC.md&per_page=1" |
  jq -r '.[0].sha'
```

A new OKF revision is a wiki migration, not just a file swap: the agent writes
the version it reads into the bundle root's `index.md`, and `check-okf.sh`
fails a wiki whose declared `okf_version` disagrees with the spec.
