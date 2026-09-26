"""Tests for md2okf.agents: the registry and Pi's entry in it."""

from __future__ import annotations

from pathlib import Path

import pytest

from md2okf import agents, sandbox, workbench
from md2okf.protocols import pi as pi_protocol

_REPO_ROOT = Path(__file__).resolve().parents[1]
PI_SANDBOX = workbench.sandbox_name("pi")

# The first-turn prompt before prompts became agent-owned, verbatim. Pi's must
# not drift from it: the kit's compile-okf skill is what it activates.
_LEGACY_PI_PROMPT = (
    "Load the compile-okf skill: read ~/.pi/agent/skills/compile-okf/SKILL.md, "
    "then follow it to compile {document} directly into the workspace root. "
    "You are already in the OKF wiki; never create an okf/ child directory."
)


# --- the registry ------------------------------------------------------------


def test_only_agents_with_a_shipped_kit_are_registered():
    """A value is only valid once its kit exists; see pyproject.toml's force-include."""
    assert sorted(agents.AGENTS) == ["pi"]
    for name, agent in agents.AGENTS.items():
        assert agent.name == name
        assert (_REPO_ROOT / "kits" / name / "spec.yaml").is_file()


def test_resolve_returns_the_registered_agent():
    assert agents.resolve("pi") is agents.PI


@pytest.mark.parametrize("value", ["bogus", "Pi", "claude", " pi", ""])
def test_resolve_rejects_anything_unregistered_and_lists_the_valid_names(value):
    with pytest.raises(agents.UnknownAgentError) as excinfo:
        agents.resolve(value)
    message = str(excinfo.value)
    assert "MD2OKF_AGENT" in message
    assert "valid: pi" in message


def test_from_env_defaults_to_pi_when_unset_or_empty(monkeypatch):
    monkeypatch.delenv("MD2OKF_AGENT", raising=False)
    assert agents.from_env() is agents.PI
    monkeypatch.setenv("MD2OKF_AGENT", "")
    assert agents.from_env() is agents.PI


def test_from_env_honours_an_explicit_value(monkeypatch):
    monkeypatch.setenv("MD2OKF_AGENT", "pi")
    assert agents.from_env() is agents.PI
    monkeypatch.setenv("MD2OKF_AGENT", "bogus")
    with pytest.raises(agents.UnknownAgentError):
        agents.from_env()


# --- Pi ----------------------------------------------------------------------


def test_pi_compile_args_are_unchanged():
    assert agents.PI.compile_args("do it") == ["pi", "--mode", "json", "do it"]


def test_pi_interactive_args():
    assert agents.PI.interactive_args == ("pi",)


def test_pi_prompt_is_byte_identical_to_the_legacy_prompt():
    document = Path("/state/md2okf/pi/work/md/doc.md")
    assert agents.PI.compile_prompt(document) == _LEGACY_PI_PROMPT.format(document=document)


def test_pi_prompt_names_a_skill_its_kit_installs():
    """The prompt tells the agent to read a file; the kit must actually carry it."""
    assert "~/.pi/agent/skills/compile-okf/SKILL.md" in agents.PI.compile_prompt(Path("/x.md"))
    skill = _REPO_ROOT / "kits" / "pi" / "files" / "home" / ".pi" / "agent" / "skills" / "compile-okf" / "SKILL.md"
    assert skill.is_file()


def test_pi_prompt_ends_with_the_shared_workspace_rule():
    assert agents.PI.compile_prompt(Path("/x.md")).endswith(agents.WORKSPACE_ROOT_RULE)


def test_pi_keeps_the_default_sbx_minimum():
    assert agents.PI.min_sbx_version == sandbox.MIN_VERSION == (0, 43, 0)


def test_pi_uses_the_pi_protocol():
    assert agents.PI.protocol is pi_protocol


def test_pi_credentials_are_ready_when_the_key_is_proxy_managed(fake_sbx):
    fake_sbx.register(PI_SANDBOX)
    fake_sbx.openrouter_key = "proxy-managed"
    assert agents.PI.check_credentials(PI_SANDBOX) is None


def test_pi_credential_remedy_names_the_openrouter_commands(fake_sbx):
    """Regression.

    This used to tell the user to run a GitHub secret command for an
    OpenRouter key problem -- the wrong provider entirely.
    """
    fake_sbx.register(PI_SANDBOX)
    fake_sbx.openrouter_key = "sk-literal-value"

    remedy = agents.PI.check_credentials(PI_SANDBOX)

    assert remedy is not None
    assert "sbx secret set openrouter" in remedy
    assert f"sbx secret set-custom --sandbox {PI_SANDBOX}" in remedy
    assert "openrouter.ai" in remedy
    assert "github" not in remedy.lower()


def test_pi_credential_check_is_local_and_unpaid(fake_sbx):
    """It runs on every create and reuse, so it may only read the env -- never start a model turn."""
    fake_sbx.register(PI_SANDBOX)
    agents.PI.check_credentials(PI_SANDBOX)
    assert fake_sbx.turn_argvs == []
    assert fake_sbx.calls[-1] == ["sbx", "exec", PI_SANDBOX, "--", "sh", "-lc", 'echo "$OPENROUTER_API_KEY"']
