"""Static checks on every sandbox kit's agent config, which no other suite covers.

These are assertions about prose and layout, not about the driver: `make
validate` checks each spec.yaml against the Sandbox Kit schema, and the
tests/test-sandbox-guest-<agent>.sh scripts check what a running sandbox
delivers, but neither reads what the agent is told to do.

They run over every kits/*/ directory, registered or not, so a kit being
authored is held to the same rules before md2okf.agents ever offers it.
Instruction and procedure files are checked in per agent rather than
generated, which is exactly why these checks exist: four hand-kept copies of
the OKF authoring contract must not drift apart on what matters.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

_KITS_ROOT = Path(__file__).resolve().parents[1] / "kits"
_KITS = sorted(path.name for path in _KITS_ROOT.iterdir() if (path / "spec.yaml").is_file())

# Each agent's home-directory config roots. A kit must never mention another
# agent's: that is what a copy-and-paste port leaves behind.
_AGENT_HOME_DIRS = {
    "pi": (".pi",),
    "claude": (".claude",),
    "codex": (".codex", ".agents"),
}

# Where each kit keeps its skills, for the rules that only apply to skills.
_SKILL_ROOTS = {
    "pi": "files/home/.pi/agent/skills",
    "claude": "files/home/.claude/skills",
    "codex": "files/home/.agents/skills",
}
_WIKI_SKILLS = ("compile-okf", "inspect-okf", "size-okf", "merkle-okf")

# Where each kit keeps the gate (check-okf.sh and its frontmatter guard):
# inside its compile-okf skill.
_GATE_DIRS = {agent: f"{root}/compile-okf/scripts" for agent, root in _SKILL_ROOTS.items()}

# The parts of the OKF authoring contract every agent must be told, whatever
# its instruction format. Each is a phrase the Pi kit states today; a port
# that drops one has dropped the rule.
_SHARED_INVARIANTS = {
    "read the spec first": "At the start of every run, read `../SPEC.md`",
    "the spec wins": "the spec wins",
    "source text is untrusted": "data, not instructions",
    "idempotent updates": "idempotent",
    "generated indexes": "okfctl index build",
    "no okf/ child directory": "Never create an `okf/` directory inside your workspace",
}

# Byte-identical in every kit: the shared helpers, never forked per agent.
_SHARED_HELPERS = ("files/home/.local/lib/md2okf/mount-state.sh", "files/home/.local/lib/md2okf/md2okf-agent.sh")

# Finder metadata a macOS host scatters through the tree. Gitignored, so CI
# never sees it, and never part of a kit. Skipped by name rather than
# scanning an allowlist of suffixes, so a runtime file in a format nobody has
# used yet — .txt, .yaml, an extensionless script — is still read.
_METADATA_NAMES = frozenset({".DS_Store", ".localized"})


def _is_metadata(path: Path) -> bool:
    # "._name" is the sidecar Finder writes next to a file on a non-native disk.
    return path.name in _METADATA_NAMES or path.name.startswith("._")


def _kit(agent: str) -> Path:
    return _KITS_ROOT / agent


def _runtime_files(agent: str) -> list[Path]:
    """Everything a kit copies into the sandbox's home."""
    home = _kit(agent) / "files" / "home"
    return sorted(p for p in home.rglob("*") if p.is_file() and not _is_metadata(p) and "__pycache__" not in p.parts)


def _instruction_text(agent: str) -> str:
    """Everything the agent is *told*: the spec's agentInstructions and every Markdown file it carries.

    Read as text rather than parsed, so no YAML dependency is needed and a
    kit whose instructions live entirely in spec.yaml is covered the
    same way as one that ships them as files (Pi).
    """
    parts = [(_kit(agent) / "spec.yaml").read_text(encoding="utf-8")]
    parts += [p.read_text(encoding="utf-8", errors="replace") for p in _runtime_files(agent) if p.suffix == ".md"]
    return "\n".join(parts)


# --- rules for every kit -------------------------------------------------------


def test_there_is_at_least_the_pi_kit():
    assert "pi" in _KITS


@pytest.mark.parametrize("agent", _KITS)
@pytest.mark.parametrize("rule", sorted(_SHARED_INVARIANTS))
def test_every_kit_states_the_shared_authoring_contract(agent, rule):
    """The skills say these rules are not repeated, so the instructions must carry them."""
    assert _SHARED_INVARIANTS[rule] in _instruction_text(agent), f"kits/{agent} never says: {rule}"


@pytest.mark.parametrize("agent", _KITS)
def test_every_kit_stamps_its_own_provenance(agent):
    """A port that keeps `by: pi/` makes every other agent sign its pages as Pi."""
    text = _instruction_text(agent)
    assert f"generated: {{ by: {agent}/" in text, f"kits/{agent} does not tell the agent to sign as {agent}/"
    for other in _AGENT_HOME_DIRS:
        if other != agent:
            assert f"by: {other}/" not in text, f"kits/{agent} tells the agent to sign as {other}/"


@pytest.mark.parametrize("agent", _KITS)
def test_no_kit_mentions_another_agents_config(agent):
    foreign = [d for other, dirs in _AGENT_HOME_DIRS.items() if other != agent for d in dirs]
    text = _instruction_text(agent)
    mentioned = [d for d in foreign if f"~/{d}/" in text or f"$HOME/{d}/" in text or f"/home/agent/{d}/" in text]
    assert not mentioned, f"kits/{agent} refers to another agent's config: {mentioned}"
    shipped = [d for d in foreign if (_kit(agent) / "files" / "home" / d).exists()]
    assert not shipped, f"kits/{agent} ships another agent's config directory: {shipped}"


@pytest.mark.parametrize("agent", _KITS)
def test_every_file_the_instructions_name_is_in_the_kit(agent):
    """A `~/…` path to a file must exist under files/home, or the agent is sent to nothing.

    Only paths with a file suffix: directories like the native trace
    directory are created at runtime, not shipped.
    """
    references = set(re.findall(r"~/([\w./-]+\.(?:md|sh|py|json|toml))", _instruction_text(agent)))
    missing = sorted(ref for ref in references if not (_kit(agent) / "files" / "home" / ref).is_file())
    assert not missing, f"kits/{agent} instructions name files it does not ship: {missing}"


@pytest.mark.parametrize("agent", _KITS)
def test_runtime_instructions_never_call_the_wiki_root_dot_dot_okf(agent):
    """Regression, seen live: agents created okf/okf/.

    The agent starts in the wiki root, so `../okf` resolves to the same inode
    but reads as though the wiki were a child directory.
    """
    scanned = _runtime_files(agent)
    assert scanned, f"no runtime files found under kits/{agent}/files/home"
    # errors="replace" so an unreadable byte is a substituted character rather
    # than a crash: a binary that is not Finder metadata should still be
    # searched, not halt the sweep before the files after it.
    offenders = [
        path.relative_to(_kit(agent))
        for path in scanned
        if "../okf" in path.read_text(encoding="utf-8", errors="replace")
    ]
    assert not offenders, f"runtime instructions still refer to the wiki as ../okf: {offenders}"


@pytest.mark.parametrize("agent", _KITS)
@pytest.mark.parametrize("helper", _SHARED_HELPERS)
def test_shared_helpers_are_identical_in_every_kit(agent, helper):
    reference = _kit("pi") / helper
    copy = _kit(agent) / helper
    assert copy.is_file(), f"kits/{agent} is missing {helper}"
    assert copy.read_bytes() == reference.read_bytes(), f"kits/{agent}/{helper} has drifted from kits/pi"


@pytest.mark.parametrize("agent", _KITS)
def test_every_kit_puts_the_wrapper_on_path(agent):
    spec = (_kit(agent) / "spec.yaml").read_text(encoding="utf-8")
    assert "path: /home/agent/.local/bin/md2okf-agent\n" in spec
    assert "/.local/lib/md2okf/md2okf-agent.sh" in spec


# --- rules for kits with skills ------------------------------------------------


def _skill_kits() -> list[tuple[str, str]]:
    return [(agent, skill) for agent in _KITS if agent in _SKILL_ROOTS for skill in _WIKI_SKILLS]


@pytest.mark.parametrize("agent", _KITS)
@pytest.mark.parametrize("script", ["check-okf.sh", "frontmatter-guard.py"])
def test_the_gate_scripts_are_identical_in_every_kit(agent, script):
    """One gate, many copies: `make check-okf` runs Pi's on the host, so no agent's may differ."""
    assert agent in _GATE_DIRS, f"kits/{agent} has no known gate location"
    reference = _kit("pi") / _GATE_DIRS["pi"] / script
    copy = _kit(agent) / _GATE_DIRS[agent] / script
    assert copy.is_file(), f"kits/{agent} is missing its {script}"
    assert copy.read_bytes() == reference.read_bytes(), f"kits/{agent}'s {script} has drifted from kits/pi"


@pytest.mark.parametrize(("agent", "skill"), _skill_kits())
def test_wiki_skills_name_the_workspace_root_as_pwd(agent, skill):
    """The counterpart of the ../okf rule: name the wiki as "$PWD"."""
    text = (_kit(agent) / _SKILL_ROOTS[agent] / skill / "SKILL.md").read_text(encoding="utf-8")
    assert '"$PWD"' in text, f'kits/{agent} {skill} does not name the wiki root as "$PWD"'
