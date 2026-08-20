"""Report sizes for an OKF wiki folder (stdlib only)."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("sizeokf")
except PackageNotFoundError:
    __version__ = "0.0.0+local"
