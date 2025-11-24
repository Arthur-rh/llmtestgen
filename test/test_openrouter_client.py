"""Tests for the OpenRouter client abstractions."""
from __future__ import annotations

import pytest

from llmtestgen.core import openrouter_client as orc


@pytest.fixture(autouse=True)
def _env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setenv("OPENROUTER_DEFAULT_MODEL", "router-model")


def test_send_prompt_returns_assistant_text(stub_httpx_client) -> None:
    httpx_helper = stub_httpx_client(orc)
    httpx_helper["queue_post"]({"choices": [{"message": {"content": "Hello user"}}]})

    response = orc.send_prompt("Hi there")

    assert response == "Hello user" #nosec
    sent_payload = httpx_helper["calls"]["post"][0]["json"]
    assert sent_payload["model"] == "router-model" #nosec
    assert sent_payload["messages"][0]["content"] == "Hi there" #nosec


def test_chat_completion_raises_on_http_error(stub_httpx_client) -> None:
    httpx_helper = stub_httpx_client(orc)
    httpx_helper["queue_post"]({}, status_code=500, text="Server error")

    client = orc.OpenRouterClient()
    with pytest.raises(orc.OpenRouterError):
        client.chat_completion([{"role": "user", "content": "ping"}])


def test_test_connection_handles_failure(stub_httpx_client) -> None:
    httpx_helper = stub_httpx_client(orc)
    httpx_helper["queue_get"]({}, status_code=502, text="Bad gateway")

    client = orc.OpenRouterClient()
    assert client.test_connection() is False #nosec
