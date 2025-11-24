"""Shared pytest fixtures for stubbing HTTP clients and guarding LLM calls."""
from __future__ import annotations

import json
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


# ---------------------------------------------------------------------------
# LLM guard and helpers
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def forbid_llm_calls(monkeypatch: pytest.MonkeyPatch, request: pytest.FixtureRequest):
    """Prevent LLM parser usage unless explicitly marked live."""
    if request.node.get_closest_marker("live_llm") or request.node.get_closest_marker("live-llm"):
        return

    def _forbid(*_args: Any, **_kwargs: Any):
        raise AssertionError("LLM parser called unexpectedly")

    monkeypatch.setattr(
        "src.services.spec_extractor.parsers.parser_llm.LLMParser.parse",
        _forbid,
        raising=True,
    )
    monkeypatch.setattr(
        "src.services.spec_extractor.parsers.parser_llm.parse_with_llm",
        _forbid,
        raising=True,
    )


@pytest.fixture
def live_llm(request):
    """Enable live LLM usage only when marker and flag are provided."""
    if not request.node.get_closest_marker("live_llm") and not request.node.get_closest_marker("live-llm"):
        pytest.skip("live LLM tests require @pytest.mark.live_llm")
    if not request.config.getoption("--live-llm"):
        pytest.skip("live LLM tests require --live-llm")
    return True


@pytest.fixture
def live_git(request):
    """Return True only if --live-git was passed."""
    return request.config.getoption("--live-git")


@pytest.fixture
def write_file(tmp_path: Path):
    def _write(name: str, content: str) -> Path:
        path = tmp_path / name
        path.write_text(content, encoding="utf-8")
        return path

    return _write


@pytest.fixture
def dummy_send_prompt_fn():
    def _send(prompt: str, *, api_key=None, model=None, system_prompt=None, **kwargs):
        return json.dumps(
            {
                "title": "Dummy",
                "sections": {"Body": "Content"},
                "requirements": ["must work"],
                "acceptance_criteria": ["then succeed"],
                "examples": ["example"],
                "raw_text": prompt,
                "source_path": "dummy",
                "confidence": 100,
            }
        )

    return _send


# ---------------------------------------------------------------------------
# HTTP stubbing helpers
# ---------------------------------------------------------------------------

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
