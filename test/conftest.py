"""Shared pytest fixtures for stubbing HTTP clients."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable, Dict

import pytest
from dotenv import load_dotenv

# Ensure the project root is importable when tests run without installing the package.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Load environment variables from .env so live tests can use stored API keys.
load_dotenv(ROOT / ".env", override=False)


class _DummyResponse:
    def __init__(self, status_code: int = 200, payload: Dict[str, Any] | None = None, text: str = "") -> None:
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text

    def json(self) -> Dict[str, Any]:
        return self._payload
    
def pytest_addoption(parser: pytest.Parser) -> None:
    """Add custom command-line options to pytest."""
    parser.addoption(
        "--live-llm",
        action="store_true",
        default=False,
        help="Run tests that hit live LLM APIs (requires network access and valid API keys).",
    )
    parser.addoption(
        "--live-git",
        action="store_true",
        default=False,
        help="Run tests that clone remote Git repositories (requires network access).",
    )
    
@pytest.fixture
def live_llm(request):
    """Return True only if --live-llm was passed."""
    return request.config.getoption("--live-llm")


@pytest.fixture
def live_git(request):
    """Return True only if --live-git was passed."""
    return request.config.getoption("--live-git")


@pytest.fixture
def stub_httpx_client(monkeypatch: pytest.MonkeyPatch) -> Callable[[Any], Dict[str, Any]]:
    """Provide a helper that replaces `httpx.Client` inside a target module."""

    def _apply(target_module: Any) -> Dict[str, Any]:
        calls: Dict[str, list[Dict[str, Any]]] = {"post": [], "get": []}

        class DummyClient:
            post_queue: list[_DummyResponse] = []
            get_queue: list[_DummyResponse] = []

            def __init__(self, *_args: Any, **_kwargs: Any) -> None:
                pass

            def post(self, endpoint: str, *, headers: Dict[str, Any] | None = None, json: Dict[str, Any] | None = None):
                calls["post"].append({"endpoint": endpoint, "headers": headers or {}, "json": json or {}})
                if DummyClient.post_queue:
                    return DummyClient.post_queue.pop(0)
                return _DummyResponse()

            def get(self, endpoint: str, *, headers: Dict[str, Any] | None = None):
                calls["get"].append({"endpoint": endpoint, "headers": headers or {}})
                if DummyClient.get_queue:
                    return DummyClient.get_queue.pop(0)
                return _DummyResponse()

            def close(self) -> None:  # pragma: no cover - nothing to clean up
                pass

        def queue_post(payload: Dict[str, Any] | None = None, *, status_code: int = 200, text: str = "") -> None:
            DummyClient.post_queue.append(_DummyResponse(status_code=status_code, payload=payload, text=text))

        def queue_get(payload: Dict[str, Any] | None = None, *, status_code: int = 200, text: str = "") -> None:
            DummyClient.get_queue.append(_DummyResponse(status_code=status_code, payload=payload, text=text))

        monkeypatch.setattr(target_module.httpx, "Client", DummyClient)

        return {"queue_post": queue_post, "queue_get": queue_get, "calls": calls}

    return _apply
