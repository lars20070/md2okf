"""Static checks on every sandbox kit's agent config, which no other suite covers.

These are assertions about prose and layout, not about the driver: `make
validate` builds each kit and checks the artifact with kit-tck, and the
tests/test-sandbox-guest-<agent>.sh scripts check what a running sandbox
delivers, but neither reads what the agent is told to do.

They run over every kits/*/ directory, registered or not, so a kit being
authored is held to the same rules before md2okf.agents ever offers it.
Instruction and procedure files are checked in per agent rather than
generated, which is exactly why these checks exist: hand-kept copies of the
OKF authoring contract must not drift apart on what matters.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

_KITS_ROOT = Path(__file__).resolve().parents[1] / "kits"


def _descriptor_path(kit: str) -> Path:
    """A kit's v3 descriptor: kits/<kit>/md2okf-<kit>.yaml, beside its .dockerfile recipe."""
    return _KITS_ROOT / kit / f"md2okf-{kit}.yaml"


_KITS = sorted(path.name for path in _KITS_ROOT.iterdir() if _descriptor_path(path.name).is_file())

# Each agent's home-directory config roots. A kit must never mention another
# agent's: that is what a copy-and-paste port leaves behind.
_AGENT_HOME_DIRS = {
    "pi": (".pi",),
    "claude": (".claude",),
    "codex": (".codex", ".agents"),
}

# Where each kit keeps its skills in the repository, and where the agent finds
# them in the guest (relative to ~). Pi ships its skills in its own home; the
# two mixins ship theirs under /usr/share and the runtime exposes them in the
# workload's skills directory (agent-skill@1).
_SKILL_ROOTS = {
    "pi": "files/home/.pi/agent/skills",
    "claude": "files/skills",
    "codex": "files/skills",
}
_GUEST_SKILL_DIRS = {
    "pi": ".pi/agent/skills",
    "claude": ".claude/skills",
    "codex": ".agents/skills",
}
# The instruction profile the runtime writes from agent-context@2, so no kit
# ships it as a file (relative to ~).
_RUNTIME_PROFILES = {
    "claude": ".claude/CLAUDE.md",
    "codex": ".codex/AGENTS.md",
}
_WIKI_SKILLS = ("compile-okf", "inspect-okf", "size-okf", "merkle-okf")
_ALL_SKILLS = ("compile-okf", "curate-okf", "inspect-md", "inspect-okf", "merkle-okf", "size-okf")

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


def _descriptor(agent: str) -> str:
    return _descriptor_path(agent).read_text(encoding="utf-8")


def _runtime_files(agent: str) -> list[Path]:
    """Everything a kit's recipe copies into the sandbox: its whole files/ tree."""
    root = _kit(agent) / "files"
    return sorted(p for p in root.rglob("*") if p.is_file() and not _is_metadata(p) and "__pycache__" not in p.parts)


def _context_body(agent: str) -> str:
    """The descriptor's agent-context@2 body, dedented; empty when it declares none (Pi).

    Read as text rather than parsed, so no YAML dependency is needed: the body
    is the `content: |` block scalar after the capability's type line, which
    ends at the first line indented less than its own first line.
    """
    lines = _descriptor(agent).splitlines()
    try:
        start = next(i for i, line in enumerate(lines) if line.strip() == "- type: com.docker.sandbox/agent-context@2")
    except StopIteration:
        return ""
    content = next(i for i in range(start, len(lines)) if lines[i].strip() == "content: |")
    body = lines[content + 1 :]
    indent = len(body[0]) - len(body[0].lstrip())
    kept = []
    for line in body:
        if line.strip() and len(line) - len(line.lstrip()) < indent:
            break
        kept.append(line[indent:])
    return "\n".join(kept)


def _instruction_text(agent: str) -> str:
    """Everything the agent is *told*: the descriptor's agent-context body and every Markdown file it carries.

    A kit whose instructions live entirely in its descriptor is covered the
    same way as one that ships them as files (Pi). Descriptor comments are
    not instructions, so they are not read.
    """
    parts = [_context_body(agent)]
    parts += [p.read_text(encoding="utf-8", errors="replace") for p in _runtime_files(agent) if p.suffix == ".md"]
    return "\n".join(parts)


def _repo_path_for_guest_file(agent: str, home_relative: str) -> Path | None:
    """Where a `~/…` file the instructions name lives in the kit, or None for a runtime-written profile."""
    if _RUNTIME_PROFILES.get(agent) == home_relative:
        return None
    skills = _GUEST_SKILL_DIRS[agent] + "/"
    if home_relative.startswith(skills):
        return _kit(agent) / _SKILL_ROOTS[agent] / home_relative.removeprefix(skills)
    return _kit(agent) / "files" / "home" / home_relative


def _shim_hook(agent: str) -> str:
    """The install hook that writes the four helper CLI shims, comment block included."""
    match = re.search(
        r"^ *# The four helper CLIs are shims.*?description: Write the workspace-backed helper CLI shims\n",
        _descriptor(agent),
        re.MULTILINE | re.DOTALL,
    )
    assert match, f"kits/{agent} has no shim-writing install hook"
    return match.group(0)


# --- rules for every kit -------------------------------------------------------


def test_every_registered_kit_is_found():
    assert {"pi", "claude", "codex"} <= set(_KITS)


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
    """A `~/…` path to a file must exist in the kit, or the agent is sent to nothing.

    Only paths with a file suffix: directories like the native trace
    directory are mounted at runtime, not shipped. The instruction profile the
    runtime writes from agent-context@2 is exempt, since no kit ships it.
    """
    references = set(re.findall(r"~/([\w./-]+\.(?:md|sh|py|json|toml))", _instruction_text(agent)))
    missing = []
    for ref in sorted(references):
        path = _repo_path_for_guest_file(agent, ref)
        if path is not None and not path.is_file():
            missing.append(ref)
    assert not missing, f"kits/{agent} instructions name files it does not ship: {missing}"


@pytest.mark.parametrize("agent", _KITS)
def test_no_instruction_points_at_the_retired_state_variable(agent):
    """MD2OKF_STATE_DIR is gone: the trace directory is a host mount, named by its guest path."""
    assert "MD2OKF_STATE_DIR" not in _instruction_text(agent)


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
def test_no_kit_is_left_in_the_v2_layout(agent):
    """A leftover spec.yaml or bind helper would be dead weight that still moves the fingerprint."""
    assert not (_kit(agent) / "spec.yaml").exists()
    assert not (_kit(agent) / "files" / "home" / ".local" / "lib" / "md2okf").exists()
    assert (_kit(agent) / f"md2okf-{agent}.dockerfile").is_file()


@pytest.mark.parametrize("agent", _KITS)
def test_every_descriptor_pins_one_frontend_and_schema_3(agent):
    """One frontend digest for every kit: it produces the published bytes, so it moves deliberately."""
    first_line = _descriptor(agent).splitlines()[0]
    assert re.fullmatch(r"# syntax=docker/sandbox-kit:3@sha256:[0-9a-f]{64}", first_line)
    assert first_line == _descriptor("pi").splitlines()[0]
    assert '\nschemaVersion: "3"\n' in _descriptor(agent)


@pytest.mark.parametrize("agent", _KITS)
def test_no_descriptor_references_an_arg(agent):
    """Placeholders are found by text search, comments included, and no kit declares an arg."""
    assert "${{" not in _descriptor(agent)


@pytest.mark.parametrize("agent", _KITS)
def test_the_shim_hook_is_identical_in_every_kit(agent):
    """One shim writer, never forked per agent: it is how every kit finds ../scripts."""
    assert _shim_hook(agent) == _shim_hook("pi")


@pytest.mark.parametrize("agent", [kit for kit in _KITS if _SKILL_ROOTS.get(kit) == "files/skills"])
def test_every_shipped_skill_is_declared_and_every_declaration_shipped(agent):
    """A mixin's skills reach the agent only through agent-skill@1, one entry per directory."""
    shipped = sorted(p.name for p in (_kit(agent) / "files" / "skills").iterdir() if p.is_dir())
    declared = sorted(re.findall(rf"path: /usr/share/md2okf-{agent}/skills/([\w-]+)\n", _descriptor(agent)))
    assert shipped == declared == sorted(_ALL_SKILLS)


def _capability(agent: str, kind: str) -> str:
    """One capability entry of a descriptor, as text: from its type line to the next entry."""
    match = re.search(
        rf"^  - type: com\.docker\.sandbox/{re.escape(kind)}\n.*?(?=^  (?:- type: |#)|\Z)",
        _descriptor(agent),
        re.MULTILINE | re.DOTALL,
    )
    assert match, f"kits/{agent} declares no {kind}"
    return match.group(0)


@pytest.mark.parametrize("kind", ["network-policy@1", "lifecycle@1"])
def test_the_two_mixins_install_and_allow_the_same(kind):
    """The Claude Code and Codex kits add the same toolchain; only their skills and instructions differ."""
    assert _capability("claude", kind) == _capability("codex", kind)


def test_the_mixin_recipes_fetch_the_same_pinned_binaries():
    """The mq and okfctl digests are pinned in three recipes; one bump must reach all of them."""

    def pins(agent: str) -> set[str]:
        recipe = (_kit(agent) / f"md2okf-{agent}.dockerfile").read_text(encoding="utf-8")
        return set(re.findall(r"^\s*(?:mq_target|mq_sha256|okfctl_sha256)=\S+$", recipe, re.MULTILINE))

    assert pins("claude") == pins("codex") == pins("pi")
    assert len(pins("pi")) == 6


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
