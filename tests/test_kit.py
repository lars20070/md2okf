"""Static checks on the kit's agent config, which no other suite covers.

Ported from the retired tests/test-sandbox-mounts.sh. These are assertions
about prose, not about the driver: `make validate` checks spec.yaml against
the Sandbox Kit schema, and tests/test-sandbox-guest-pi.sh checks what a running
sandbox delivers, but neither reads what the agent is told to do.
"""

from __future__ import annotations

import pytest

from md2okf import resources

_AGENT_DIR = resources.kit_dir("pi") / "files" / "home" / ".pi" / "agent"
_WIKI_SKILLS = ("compile-okf", "inspect-okf", "size-okf", "merkle-okf")
# Finder metadata a macOS host scatters through the tree. Gitignored, so CI
# never sees it, and never part of the kit. Skipped by name rather than
# scanning an allowlist of suffixes, so a runtime file in a format nobody has
# used yet — .txt, .yaml, an extensionless script — is still read.
_METADATA_NAMES = frozenset({".DS_Store", ".localized"})


def _is_metadata(path):
    # "._name" is the sidecar Finder writes next to a file on a non-native disk.
    return path.name in _METADATA_NAMES or path.name.startswith("._")


def _runtime_files():
    return sorted(p for p in _AGENT_DIR.rglob("*") if p.is_file() and not _is_metadata(p))


def test_runtime_instructions_never_call_the_wiki_root_dot_dot_okf():
    """Regression, seen live: agents created okf/okf/.

    Pi starts in the wiki root, so `../okf` resolves to the same inode but
    reads as though the wiki were a child directory.
    """
    scanned = _runtime_files()
    assert scanned, f"no runtime instruction files found under {_AGENT_DIR}"
    # errors="replace" so an unreadable byte is a substituted character rather
    # than a crash: a binary that is not Finder metadata should still be
    # searched, not halt the sweep before the files after it.
    offenders = [
        path.relative_to(_AGENT_DIR)
        for path in scanned
        if "../okf" in path.read_text(encoding="utf-8", errors="replace")
    ]
    assert not offenders, f"runtime instructions still refer to the wiki as ../okf: {offenders}"


@pytest.mark.parametrize("skill", _WIKI_SKILLS)
def test_wiki_skills_name_the_workspace_root_as_pwd(skill):
    """The counterpart of the rule above: name the wiki as "$PWD"."""
    text = (_AGENT_DIR / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
    assert '"$PWD"' in text, f'{skill} does not name the wiki root as "$PWD"'
