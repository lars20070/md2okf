"""Tests for merkleokf.cli."""

import pytest

from merkleokf import __version__
from merkleokf.cli import main


def test_main_does_nothing_and_succeeds(capsys):
    assert main([]) == 0
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_main_version(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])
    assert exc_info.value.code == 0
    out = capsys.readouterr().out
    assert out == f"merkleokf {__version__}\n"


def test_main_help(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])
    assert exc_info.value.code == 0
    out = capsys.readouterr().out
    assert "usage: merkleokf" in out


def test_main_unknown_flag(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["--nope"])
    assert exc_info.value.code == 2
    assert "unrecognized arguments" in capsys.readouterr().err


def test_main_takes_no_positional(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["okf"])
    assert exc_info.value.code == 2
    assert "unrecognized arguments" in capsys.readouterr().err
