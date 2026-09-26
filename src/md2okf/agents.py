"""The agent frameworks md2okf can drive, and everything that differs between them.

An :class:`Agent` owns what is specific to one runtime -- its command lines,
its first-turn prompt, how to tell whether its credential is ready, the sbx
version its kit needs, and the parser for its event stream -- so the workbench,
the Ralph loop and the CLI stay agent-neutral. MD2OKF_AGENT picks one; only
registered agents are accepted, and each registers only once its kit ships.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from md2okf import sandbox
from md2okf.protocols import EventProtocol
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
        '--env OPENROUTER_API_KEY --value "$OPENROUTER_API_KEY"'
    )


PI = Agent(
    name="pi",
    min_sbx_version=sandbox.MIN_VERSION,
    compile_args=lambda prompt: ["pi", "--mode", "json", prompt],
    interactive_args=("pi",),
    compile_prompt=_pi_compile_prompt,
    check_credentials=_pi_check_credentials,
    protocol=pi_protocol,
)

AGENTS: dict[str, Agent] = {PI.name: PI}


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
