"""Inspect an OKF wiki directory tree (stdlib only)."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("inspectokf")
except PackageNotFoundError:
    __version__ = "0.0.0+local"
