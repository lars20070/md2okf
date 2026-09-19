"""Static checks on the kit's agent config, which no other suite covers.

Ported from the retired tests/test-sandbox-mounts.sh. These are assertions
about prose, not about the driver: `make validate` checks spec.yaml against
the Sandbox Kit schema, and tests/test-sandbox-guest.sh checks what a running
sandbox delivers, but neither reads what the agent is told to do.
"""

from __future__ import annotations

import pytest

from md2okf import resources

_AGENT_DIR = resources.kit_dir() / "files" / "home" / ".pi" / "agent"
_WIKI_SKILLS = ("compile-okf", "inspect-okf", "size-okf", "merkle-okf")


def test_runtime_instructions_never_call_the_wiki_root_dot_dot_okf():
    """Regression, seen live: agents created okf/okf/.

    Pi starts in the wiki root, so `../okf` resolves to the same inode but
    reads as though the wiki were a child directory.
    """
    offenders = [
        path.relative_to(_AGENT_DIR)
        for path in _AGENT_DIR.rglob("*")
        if path.is_file() and "../okf" in path.read_text(encoding="utf-8")
    ]
    assert not offenders, f"runtime instructions still refer to the wiki as ../okf: {offenders}"


@pytest.mark.parametrize("skill", _WIKI_SKILLS)
def test_wiki_skills_name_the_workspace_root_as_pwd(skill):
    """The counterpart of the rule above: name the wiki as "$PWD"."""
    text = (_AGENT_DIR / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
    assert '"$PWD"' in text, f'{skill} does not name the wiki root as "$PWD"'
