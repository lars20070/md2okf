"""`fetch_html` — caching, retries, and backoff, all against a mock transport.

`httpx.MockTransport` maps requests to canned responses without opening a socket
(https://www.python-httpx.org/advanced/transports).
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from pathlib import Path

import httpx
import pytest

import web2md

URL = "https://developers.google.com/style/tense"


def client_returning(
    responses: Iterable[httpx.Response], log: list[httpx.Request]
) -> httpx.Client:
    """A client that replays `responses` in order, recording each request."""
    queue = list(responses)

    def handler(request: httpx.Request) -> httpx.Response:
        log.append(request)
        return queue.pop(0) if queue else httpx.Response(200, text="<html>fallback</html>")

    return httpx.Client(transport=httpx.MockTransport(handler))


@pytest.fixture
def fetch(tmp_path: Path) -> Callable[..., tuple[str, list[httpx.Request]]]:
    def _fetch(
        responses: Iterable[httpx.Response],
        *,
        refresh: bool = False,
        cache_name: str = "tense.html",
    ) -> tuple[str, list[httpx.Request]]:
        log: list[httpx.Request] = []
        with client_returning(responses, log) as client:
            html = web2md.fetch_html(client, URL, tmp_path / cache_name, refresh=refresh)
        return html, log

    return _fetch


def test_warm_cache_is_served_without_a_request(tmp_path: Path) -> None:
    cache = tmp_path / "tense.html"
    cache.write_text("<html>cached</html>", encoding="utf-8")
    log: list[httpx.Request] = []

    with client_returning([], log) as client:
        html = web2md.fetch_html(client, URL, cache, refresh=False)

    assert html == "<html>cached</html>"
    assert log == []


def test_cache_miss_fetches_and_writes_the_file(
    fetch: Callable[..., tuple[str, list[httpx.Request]]], tmp_path: Path
) -> None:
    html, log = fetch([httpx.Response(200, text="<html>fresh</html>")])

    assert html == "<html>fresh</html>"
    assert (tmp_path / "tense.html").read_text(encoding="utf-8") == "<html>fresh</html>"
    assert len(log) == 1
    assert log[0].url.params["hl"] == "en"


def test_cache_directory_is_created_on_demand(tmp_path: Path) -> None:
    cache = tmp_path / "nested" / "deeper" / "tense.html"
    log: list[httpx.Request] = []

    with client_returning([httpx.Response(200, text="<html>x</html>")], log) as client:
        web2md.fetch_html(client, URL, cache, refresh=False)

    assert cache.read_text(encoding="utf-8") == "<html>x</html>"


def test_refresh_bypasses_a_warm_cache(tmp_path: Path) -> None:
    cache = tmp_path / "tense.html"
    cache.write_text("<html>stale</html>", encoding="utf-8")
    log: list[httpx.Request] = []

    with client_returning([httpx.Response(200, text="<html>fresh</html>")], log) as client:
        html = web2md.fetch_html(client, URL, cache, refresh=True)

    assert html == "<html>fresh</html>"
    assert cache.read_text(encoding="utf-8") == "<html>fresh</html>"
    assert len(log) == 1


def test_rate_limit_is_retried_honouring_retry_after(
    fetch: Callable[..., tuple[str, list[httpx.Request]]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    slept: list[float] = []
    monkeypatch.setattr(web2md.time, "sleep", slept.append)

    html, log = fetch(
        [
            httpx.Response(429, headers={"Retry-After": "7"}, text=""),
            httpx.Response(200, text="<html>ok</html>"),
        ]
    )

    assert html == "<html>ok</html>"
    assert len(log) == 2
    assert 7.0 in slept


def test_non_numeric_retry_after_falls_back_to_the_backoff_delay(
    fetch: Callable[..., tuple[str, list[httpx.Request]]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    slept: list[float] = []
    monkeypatch.setattr(web2md.time, "sleep", slept.append)

    html, _ = fetch(
        [
            httpx.Response(429, headers={"Retry-After": "Wed, 21 Oct 2026 07:28:00 GMT"}, text=""),
            httpx.Response(200, text="<html>ok</html>"),
        ]
    )

    assert html == "<html>ok</html>"
    assert slept[0] == web2md.REQUEST_DELAY_S


def test_server_errors_are_retried(
    fetch: Callable[..., tuple[str, list[httpx.Request]]],
) -> None:
    html, log = fetch(
        [
            httpx.Response(503, text=""),
            httpx.Response(500, text=""),
            httpx.Response(200, text="<html>ok</html>"),
        ]
    )

    assert html == "<html>ok</html>"
    assert len(log) == 3


def test_client_errors_are_retried_until_the_budget_runs_out(
    fetch: Callable[..., tuple[str, list[httpx.Request]]],
) -> None:
    # A 404 skips the 429/5xx branch and reaches raise_for_status, which
    # fetch_html catches as an HTTPError and retries like a transport failure.
    with pytest.raises(SystemExit, match="failed to fetch"):
        fetch([httpx.Response(404, text="") for _ in range(web2md.MAX_RETRIES)])


def test_exhausting_the_retry_budget_is_fatal(tmp_path: Path) -> None:
    log: list[httpx.Request] = []
    responses = [httpx.Response(500, text="") for _ in range(web2md.MAX_RETRIES)]

    with (
        client_returning(responses, log) as client,
        pytest.raises(SystemExit, match="failed to fetch"),
    ):
        web2md.fetch_html(client, URL, tmp_path / "tense.html", refresh=False)

    assert len(log) == web2md.MAX_RETRIES
    assert not (tmp_path / "tense.html").exists()


def test_transport_errors_are_retried_then_reported(tmp_path: Path) -> None:
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        raise httpx.ConnectError("boom", request=request)

    with (
        httpx.Client(transport=httpx.MockTransport(handler)) as client,
        pytest.raises(SystemExit, match="boom"),
    ):
        web2md.fetch_html(client, URL, tmp_path / "tense.html", refresh=False)

    assert attempts == web2md.MAX_RETRIES


def test_backoff_grows_and_is_capped(
    fetch: Callable[..., tuple[str, list[httpx.Request]]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    slept: list[float] = []
    monkeypatch.setattr(web2md.time, "sleep", slept.append)

    with pytest.raises(SystemExit):
        fetch([httpx.Response(500, text="") for _ in range(web2md.MAX_RETRIES)])

    assert slept == [0.2, 0.4, 0.8, 1.6, 3.2]
    assert max(slept) <= 30.0
