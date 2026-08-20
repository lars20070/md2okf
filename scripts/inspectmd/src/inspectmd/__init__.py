"""Inspect Markdown heading structure (stdlib only)."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("inspectmd")
except PackageNotFoundError:
    __version__ = "0.0.0+local"
