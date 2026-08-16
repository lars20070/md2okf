"""Tests for inspectokf.cli."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from inspectokf import __version__
from inspectokf.cli import main


def test_main_success(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    wiki = tmp_path / "okf"
    wiki.mkdir()
    monkeypatch.setattr("inspectokf.cli.shutil.which", lambda _: "/usr/bin/tree")
    mock_run = MagicMock(return_value=MagicMock(returncode=0))
    monkeypatch.setattr("inspectokf.cli.subprocess.run", mock_run)
    assert main([str(wiki)]) == 0
    mock_run.assert_called_once_with(["/usr/bin/tree", str(wiki)], check=False)


def test_main_default_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    okf = tmp_path / "okf"
    okf.mkdir()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("inspectokf.cli.shutil.which", lambda _: "/usr/bin/tree")
    mock_run = MagicMock(return_value=MagicMock(returncode=0))
    monkeypatch.setattr("inspectokf.cli.subprocess.run", mock_run)
    assert main([]) == 0
    mock_run.assert_called_once_with(["/usr/bin/tree", "okf"], check=False)


def test_main_missing_dir(capsys):
    assert main(["/no/such/wiki"]) == 2
    err = capsys.readouterr().err
    assert "not a directory" in err


def test_main_tree_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys):
    wiki = tmp_path / "okf"
    wiki.mkdir()
    monkeypatch.setattr("inspectokf.cli.shutil.which", lambda _: None)
    assert main([str(wiki)]) == 2
    err = capsys.readouterr().err
    assert "tree" in err


def test_main_tree_nonzero(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    wiki = tmp_path / "okf"
    wiki.mkdir()
    monkeypatch.setattr("inspectokf.cli.shutil.which", lambda _: "/usr/bin/tree")
    monkeypatch.setattr(
        "inspectokf.cli.subprocess.run",
        MagicMock(return_value=MagicMock(returncode=1)),
    )
    assert main([str(wiki)]) == 2


def test_main_version(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])
    assert exc_info.value.code == 0
    out = capsys.readouterr().out
    assert out == f"inspectokf {__version__}\n"
