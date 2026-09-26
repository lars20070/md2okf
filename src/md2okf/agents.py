"""The agent frameworks md2okf can drive, and everything that differs between them.

An :class:`Agent` owns what is specific to one runtime -- its command lines,
its first-turn prompt, how to tell whether its credential is ready, the sbx
version its kit needs, and the parser for its event stream -- so the workbench,
the Ralph loop and the CLI stay agent-neutral. MD2OKF_AGENT picks one; only
registered agents are accepted, and each registers only once its kit ships.
"""

from __future__ import annotations

import json
import os
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from md2okf import sandbox
from md2okf.protocols import EventProtocol
from md2okf.protocols import claude as claude_protocol
from md2okf.protocols import codex as codex_protocol
from md2okf.protocols import pi as pi_protocol

ENV_VAR = "MD2OKF_AGENT"
DEFAULT_AGENT = "pi"

# The one sentence every agent's first-turn prompt ends with. The agent starts
# in the wiki root; told nothing, agents have created okf/okf/.
WORKSPACE_ROOT_RULE = "You are already in the OKF wiki; never create an okf/ child directory."


class UnknownAgentError(Exception):
    """MD2OKF_AGENT names no registered agent -- exit 2."""


@dataclass(frozen=True)
class Agent:
    """One agent framework: how to run it, prompt it, check it and parse it."""

    name: str
    """Registry key; also names the kit (kits/<name>), sandbox and workbench."""

    min_sbx_version: tuple[int, int, int]
    """The oldest sbx this agent's kit is known to work with."""

    compile_args: Callable[[str], list[str]]
    """Prompt -> the full in-sandbox argv for one Ralph-loop turn."""

    interactive_args: tuple[str, ...]
    """The in-sandbox argv `md2okf --agent` hands the terminal to."""

    compile_prompt: Callable[[Path], str]
    """Staged document path -> the first-turn prompt, naming this kit's procedure."""

    check_credentials: Callable[[str], str | None]
    """Sandbox name -> None when the credential is ready, else the remedy to print.

    Runs on every create and every reuse, so it must be local, unpaid and
    non-interactive: an env sentinel or an auth-status command, never a model
    request.
    """

    protocol: EventProtocol
    """The parser for this agent's streamed output."""


def _pi_compile_prompt(document: Path) -> str:
    return (
        "Load the compile-okf skill: read ~/.pi/agent/skills/compile-okf/SKILL.md, "
        f"then follow it to compile {document} directly into the workspace root. "
        f"{WORKSPACE_ROOT_RULE}"
    )


def _pi_check_credentials(name: str) -> str | None:
    """OPENROUTER_API_KEY must be the proxy-managed sentinel, never a literal key.

    The remedy names the two-step setup in README.md, "Set up the OpenRouter
    key". Regression: it once named `sbx secret set github ...` -- the wrong
    provider entirely, copied from an unrelated GitHub-auth pattern.
    """
    if sandbox.key_is_proxy_managed(name):
        return None
    return (
        f"OPENROUTER_API_KEY inside {name!r} is not proxy-managed.\n"
        '  Set it via sbx secret (see README.md, "Set up the OpenRouter key"):\n'
        '  echo "$OPENROUTER_API_KEY" | sbx secret set openrouter\n'
        f"  sbx secret set-custom --sandbox {name} --host openrouter.ai "
        '--env OPENROUTER_API_KEY --value "$OPENROUTER_API_KEY"\n'
        f"{_rebuild_hint(name)}"
    )


def _rebuild_hint(name: str) -> str:
    """The last line of every remedy: sbx injects credentials only when a sandbox is created.

    Measured by the Claude spike, and what `sbx secret set-custom` itself warns
    about: a secret set afterwards does not reach a sandbox that already
    exists, so re-running would reuse the same unready one.
    """
    return f"  Then remove the sandbox so the next run rebuilds it with the credential: sbx rm --force {name}"


def _claude_compile_prompt(document: Path) -> str:
    """The same shape as Pi's: name the skill file, which works however skills are activated.

    The plan proposed `/compile-okf`; whether a slash-invoked skill works in
    `claude -p` was not measured by the spike, and reading the file is what
    Pi already does reliably.
    """
    return (
        "Load the compile-okf skill: read ~/.claude/skills/compile-okf/SKILL.md, "
        f"then follow it to compile {document} directly into the workspace root. "
        f"{WORKSPACE_ROOT_RULE}"
    )


def _claude_check_credentials(name: str) -> str | None:
    """`claude auth status` must report `"loggedIn": true`.

    Local, non-interactive and unpaid: it reads the credential sbx injected at
    create time (the host's `anthropic` secret, OAuth or API key) and starts no
    model turn. Anything else -- a non-zero exit, output that is not that JSON
    -- is "not ready".

    The remedy's subscription route is a sign-in inside a Claude sandbox: sbx
    0.45 refuses `sbx secret set anthropic --oauth` ("openai/global only") and
    says to sign in from inside the Claude sandbox instead.
    """
    result = sandbox.exec_capture(name, ["claude", "auth", "status"])
    try:
        status = json.loads(result.stdout)
    except ValueError:
        status = None
    if result.returncode == 0 and isinstance(status, dict) and status.get("loggedIn") is True:
        return None
    return (
        f"Claude Code inside {name!r} is not logged in.\n"
        "  Give sbx the credential on the host, as one of:\n"
        "  sbx run claude, then /login in it    # a Claude subscription; sbx keeps the sign-in\n"
        "  sbx secret set anthropic            # an Anthropic API key\n"
        f"{_rebuild_hint(name)}"
    )


# Every in-sandbox argv starts with the kit's `md2okf-agent` wrapper, not the
# agent itself: `sbx exec` bypasses the kit entrypoint, so the wrapper is what
# guarantees the agent's traces land on host-backed state (see
# kits/<agent>/files/home/.local/lib/md2okf/md2okf-agent.sh).
WRAPPER = "md2okf-agent"

PI = Agent(
    name="pi",
    min_sbx_version=sandbox.MIN_VERSION,
    compile_args=lambda prompt: [WRAPPER, "pi", "--mode", "json", prompt],
    interactive_args=(WRAPPER, "pi"),
    compile_prompt=_pi_compile_prompt,
    check_credentials=_pi_check_credentials,
    protocol=pi_protocol,
)

CLAUDE = Agent(
    name="claude",
    # The only version the spike ran on; the kit relies on the claude parent's
    # behaviour there. See the Claude spike findings in the plan.
    min_sbx_version=(0, 45, 0),
    # --permission-mode: the parent already defaults to bypassPermissions, but
    # a compile must not depend on a parent default. --strict-mcp-config with
    # no --mcp-config: no MCP servers at all -- neither the parent's gateway
    # nor the logged-in account's claude.ai connectors, none of which a
    # compile uses.
    compile_args=lambda prompt: [
        WRAPPER,
        "claude",
        "-p",
        "--output-format",
        "stream-json",
        "--verbose",
        "--permission-mode",
        "bypassPermissions",
        "--strict-mcp-config",
        prompt,
    ],
    interactive_args=(WRAPPER, "claude", "--permission-mode", "bypassPermissions"),
    compile_prompt=_claude_compile_prompt,
    check_credentials=_claude_check_credentials,
    protocol=claude_protocol,
)


def _codex_compile_prompt(document: Path) -> str:
    """`$compile-okf` activates the skill directly (measured by the Codex spike).

    Naming the file path also worked, but only after the model first guessed
    `~` as the host's home; `$name` found the skill at once.
    """
    return f"$compile-okf Compile {document} directly into the workspace root. {WORKSPACE_ROOT_RULE}"


def _codex_check_credentials(name: str) -> str | None:
    """`codex login status` must exit 0 and report "Logged in".

    Local, non-interactive and unpaid. The codex parent routes the host's
    `openai` secret through sbx's own model provider and leaves a placeholder
    login behind at create time, which this sees; without the secret there is
    nothing to see.
    """
    result = sandbox.exec_capture(name, ["codex", "login", "status"])
    if result.returncode == 0 and "Logged in" in f"{result.stdout}\n{result.stderr}":
        return None
    return (
        f"Codex inside {name!r} is not logged in.\n"
        "  Store the credential on the host with sbx secret, as one of:\n"
        "  sbx secret set openai --oauth    # a ChatGPT subscription\n"
        "  sbx secret set openai            # an OpenAI API key\n"
        f"{_rebuild_hint(name)}"
    )


CODEX = Agent(
    name="codex",
    # The only version the Codex spike ran on.
    min_sbx_version=(0, 45, 0),
    # Neither --skip-git-repo-check nor --dangerously-bypass-... was
    # load-bearing in the spike (the parent's config already allows both), but
    # a compile must not depend on a parent default. The -c override switches
    # off the parent's MCP gateway, which a compile does not use -- the
    # counterpart of Claude's --strict-mcp-config (measured: `-c
    # mcp_servers={}` does not remove it, `enabled=false` does).
    compile_args=lambda prompt: [
        WRAPPER,
        "codex",
        "exec",
        "--json",
        "--skip-git-repo-check",
        "--dangerously-bypass-approvals-and-sandbox",
        "-c",
        "mcp_servers.mcp-gateway.enabled=false",
        prompt,
    ],
    interactive_args=(WRAPPER, "codex", "--dangerously-bypass-approvals-and-sandbox"),
    compile_prompt=_codex_compile_prompt,
    check_credentials=_codex_check_credentials,
    protocol=codex_protocol,
)

AGENTS: dict[str, Agent] = {PI.name: PI, CLAUDE.name: CLAUDE, CODEX.name: CODEX}


def resolve(value: str) -> Agent:
    """The registered agent called `value`, or UnknownAgentError naming the valid ones."""
    try:
        return AGENTS[value]
    except KeyError:
        valid = ", ".join(sorted(AGENTS))
        raise UnknownAgentError(f"{ENV_VAR}={value!r} is not a known agent (valid: {valid})") from None


def from_env() -> Agent:
    """The agent MD2OKF_AGENT selects; unset or empty means the default."""
    return resolve(os.environ.get(ENV_VAR) or DEFAULT_AGENT)
