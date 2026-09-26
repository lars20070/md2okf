"""Tests for md2okf.agents: the registry and Pi's entry in it."""

from __future__ import annotations

from pathlib import Path

import pytest

from md2okf import agents, sandbox, workbench
from md2okf.protocols import claude as claude_protocol
from md2okf.protocols import codex as codex_protocol
from md2okf.protocols import pi as pi_protocol

_REPO_ROOT = Path(__file__).resolve().parents[1]
PI_SANDBOX = workbench.sandbox_name("pi")
CLAUDE_SANDBOX = workbench.sandbox_name("claude")
CODEX_SANDBOX = workbench.sandbox_name("codex")

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
    assert sorted(agents.AGENTS) == ["claude", "codex", "pi"]
    for name, agent in agents.AGENTS.items():
        assert agent.name == name
        assert (_REPO_ROOT / "kits" / name / "spec.yaml").is_file()


def test_resolve_returns_the_registered_agent():
    assert agents.resolve("pi") is agents.PI
    assert agents.resolve("claude") is agents.CLAUDE
    assert agents.resolve("codex") is agents.CODEX


@pytest.mark.parametrize("value", ["bogus", "Pi", "Claude", "gemini", " pi", ""])
def test_resolve_rejects_anything_unregistered_and_lists_the_valid_names(value):
    with pytest.raises(agents.UnknownAgentError) as excinfo:
        agents.resolve(value)
    message = str(excinfo.value)
    assert "MD2OKF_AGENT" in message
    assert "valid: claude, codex, pi" in message


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


def test_pi_compile_args_run_pi_json_mode_through_the_wrapper():
    assert agents.PI.compile_args("do it") == ["md2okf-agent", "pi", "--mode", "json", "do it"]


def test_pi_interactive_args_run_pi_through_the_wrapper():
    assert agents.PI.interactive_args == ("md2okf-agent", "pi")


@pytest.mark.parametrize("name", sorted(agents.AGENTS))
def test_every_agent_process_starts_with_the_wrapper(name):
    """`sbx exec` bypasses the kit entrypoint; the wrapper is the trace-mount guard on every turn."""
    agent = agents.AGENTS[name]
    assert agent.compile_args("p")[0] == agents.WRAPPER
    assert agent.interactive_args[0] == agents.WRAPPER


@pytest.mark.parametrize("name", sorted(agents.AGENTS))
def test_every_registered_kit_ships_the_wrapper_shim(name):
    spec = (_REPO_ROOT / "kits" / name / "spec.yaml").read_text(encoding="utf-8")
    assert f"path: /home/agent/.local/bin/{agents.WRAPPER}\n" in spec
    assert (_REPO_ROOT / "kits" / name / "files" / "home" / ".local" / "lib" / "md2okf" / "md2okf-agent.sh").is_file()


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


def test_pi_remedy_ends_by_rebuilding_the_sandbox(fake_sbx):
    """Credentials are injected at create time, so a fixed secret needs a new sandbox."""
    fake_sbx.register(PI_SANDBOX)
    fake_sbx.openrouter_key = "sk-literal-value"
    remedy = agents.PI.check_credentials(PI_SANDBOX)
    assert remedy.splitlines()[-1].endswith(f"sbx rm --force {PI_SANDBOX}")


# --- Claude --------------------------------------------------------------------
#
# Every value here is the one the Claude spike measured; see its findings in
# .claude/plans/generalise-agent-framework.md.


def test_claude_compile_args():
    assert agents.CLAUDE.compile_args("do it") == [
        "md2okf-agent",
        "claude",
        "-p",
        "--output-format",
        "stream-json",
        "--verbose",
        "--permission-mode",
        "bypassPermissions",
        "--strict-mcp-config",
        "do it",
    ]


def test_claude_interactive_args_keep_mcp_but_bypass_prompts():
    assert agents.CLAUDE.interactive_args == ("md2okf-agent", "claude", "--permission-mode", "bypassPermissions")


def test_claude_prompt_names_a_skill_its_kit_installs():
    prompt = agents.CLAUDE.compile_prompt(Path("/state/md2okf/claude/work/md/doc.md"))
    assert "read ~/.claude/skills/compile-okf/SKILL.md" in prompt
    assert "compile /state/md2okf/claude/work/md/doc.md directly into the workspace root" in prompt
    assert prompt.endswith(agents.WORKSPACE_ROOT_RULE)
    skill = _REPO_ROOT / "kits" / "claude" / "files" / "home" / ".claude" / "skills" / "compile-okf" / "SKILL.md"
    assert skill.is_file()


def test_claude_needs_sbx_0_45_and_parses_claude_output():
    assert agents.CLAUDE.min_sbx_version == (0, 45, 0)
    assert agents.CLAUDE.protocol is claude_protocol


def test_claude_credentials_are_ready_when_logged_in(fake_sbx):
    fake_sbx.register(CLAUDE_SANDBOX)
    assert agents.CLAUDE.check_credentials(CLAUDE_SANDBOX) is None


def test_claude_credential_check_is_local_and_unpaid(fake_sbx):
    """`claude auth status` reads the injected credential; it must never start a model turn."""
    fake_sbx.register(CLAUDE_SANDBOX)
    agents.CLAUDE.check_credentials(CLAUDE_SANDBOX)
    assert fake_sbx.turn_argvs == []
    assert fake_sbx.calls[-1] == ["sbx", "exec", CLAUDE_SANDBOX, "--", "claude", "auth", "status"]


def test_claude_remedy_names_both_host_credentials_and_the_rebuild(fake_sbx):
    fake_sbx.register(CLAUDE_SANDBOX)
    fake_sbx.claude_logged_in = False
    remedy = agents.CLAUDE.check_credentials(CLAUDE_SANDBOX)
    assert remedy is not None
    assert f"inside {CLAUDE_SANDBOX!r} is not logged in" in remedy
    assert "sbx run claude, then /login" in remedy
    assert "sbx secret set anthropic " in remedy
    # sbx 0.45 refuses it: --oauth is "openai/global only".
    assert "anthropic --oauth" not in remedy
    assert remedy.splitlines()[-1].endswith(f"sbx rm --force {CLAUDE_SANDBOX}")


@pytest.mark.parametrize(
    ("returncode", "stdout"),
    [
        (0, '{"loggedIn": false}'),
        (0, "not json at all"),
        (0, '["loggedIn"]'),
        (0, '{"loggedIn": "true"}'),
        (1, '{"loggedIn": true}'),
    ],
)
def test_anything_but_a_clean_logged_in_status_is_not_ready(monkeypatch, returncode, stdout):
    monkeypatch.setattr(
        sandbox,
        "exec_capture",
        lambda _name, argv: __import__("subprocess").CompletedProcess(argv, returncode, stdout, ""),
    )
    assert agents.CLAUDE.check_credentials(CLAUDE_SANDBOX) is not None


# --- Codex ---------------------------------------------------------------------
#
# Every value here is the one the Codex spike (stages 3.1 and 3.1b) measured;
# see its findings in .claude/plans/generalise-agent-framework.md.


def test_codex_compile_args():
    assert agents.CODEX.compile_args("do it") == [
        "md2okf-agent",
        "codex",
        "exec",
        "--json",
        "--skip-git-repo-check",
        "--dangerously-bypass-approvals-and-sandbox",
        "-c",
        "mcp_servers.mcp-gateway.enabled=false",
        "do it",
    ]


def test_codex_interactive_args_keep_the_gateway():
    assert agents.CODEX.interactive_args == ("md2okf-agent", "codex", "--dangerously-bypass-approvals-and-sandbox")


def test_codex_prompt_activates_a_skill_its_kit_installs():
    prompt = agents.CODEX.compile_prompt(Path("/state/md2okf/codex/work/md/doc.md"))
    assert prompt.startswith("$compile-okf Compile /state/md2okf/codex/work/md/doc.md directly into")
    assert prompt.endswith(agents.WORKSPACE_ROOT_RULE)
    skill = _REPO_ROOT / "kits" / "codex" / "files" / "home" / ".agents" / "skills" / "compile-okf" / "SKILL.md"
    assert "name: compile-okf" in skill.read_text(encoding="utf-8")


def test_codex_needs_sbx_0_45_and_parses_codex_output():
    assert agents.CODEX.min_sbx_version == (0, 45, 0)
    assert agents.CODEX.protocol is codex_protocol


def test_codex_credentials_are_ready_when_logged_in(fake_sbx):
    fake_sbx.register(CODEX_SANDBOX)
    assert agents.CODEX.check_credentials(CODEX_SANDBOX) is None
    assert fake_sbx.calls[-1] == ["sbx", "exec", CODEX_SANDBOX, "--", "codex", "login", "status"]
    assert fake_sbx.turn_argvs == []


def test_codex_remedy_names_both_host_credentials_and_the_rebuild(fake_sbx):
    fake_sbx.register(CODEX_SANDBOX)
    fake_sbx.codex_logged_in = False
    remedy = agents.CODEX.check_credentials(CODEX_SANDBOX)
    assert f"inside {CODEX_SANDBOX!r} is not logged in" in remedy
    assert "sbx secret set openai --oauth" in remedy
    assert remedy.splitlines()[-1].endswith(f"sbx rm --force {CODEX_SANDBOX}")


@pytest.mark.parametrize(
    ("returncode", "stdout", "stderr"), [(0, "", "Not logged in"), (1, "", "Logged in"), (0, "", "")]
)
def test_codex_anything_but_a_clean_login_is_not_ready(monkeypatch, returncode, stdout, stderr):
    monkeypatch.setattr(
        sandbox,
        "exec_capture",
        lambda _name, argv: __import__("subprocess").CompletedProcess(argv, returncode, stdout, stderr),
    )
    assert agents.CODEX.check_credentials(CODEX_SANDBOX) is not None
