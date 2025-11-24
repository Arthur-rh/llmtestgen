"""llmtestgen package."""
from __future__ import annotations

__all__ = ["__version__"]

try:  # pragma: no cover - only runs when package metadata is present
    from importlib.metadata import version
except ImportError:  # pragma: no cover
    __version__ = "0.0.0"
else:
    try:
        __version__ = version("llmtestgen")
    except Exception:  # pragma: no cover - fallback when metadata missing
        __version__ = "0.0.0"
