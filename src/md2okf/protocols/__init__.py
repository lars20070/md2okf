"""Per-agent event-stream parsers, normalised to one record.

Every agent framework streams its own NDJSON protocol; each module in this
package turns one of them into :class:`Event` records, so compile.py can run
the Ralph loop without knowing which agent it is talking to. A module exposes
``translate(line)``, ``is_tool_call(line)`` and ``process(lines)``; only
``process`` is part of the :class:`Protocol` the driver relies on.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import NamedTuple, Protocol

# Tool calls are cut to this many characters for -v, the same for every agent,
# so the verbose view reads alike whichever one is running.
DISPLAY_WIDTH = 120


class Event(NamedTuple):
    """One raw line of agent output, and what the driver makes of it."""

    raw: str
    """The line exactly as the agent printed it (stdout and stderr merged)."""

    display: str | None
    """What -v should print for this line, or None to show nothing."""

    is_tool_call: bool
    """Whether this line starts a tool call -- the "did any work" signal."""

    failure: str | None
    """The protocol's own statement that the turn failed, or None.

    Authoritative, like a non-zero exit: an agent can report a terminal error
    and still exit 0, or report one after tool calls it already made.
    """


class EventProtocol(Protocol):
    """What compile.py needs from a protocol module."""

    def process(self, lines: Iterable[str]) -> Iterator[Event]:
        """Yield one Event per line, in order."""
        ...
