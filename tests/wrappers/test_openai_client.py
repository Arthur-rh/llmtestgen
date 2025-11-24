"""Tests for the OpenAI client abstractions."""
from __future__ import annotations

import pytest

from llmtestgen.wrappers import openai_client as oac


@pytest.fixture(autouse=True)
def _env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-ai-key")
    monkeypatch.setenv("OPENAI_DEFAULT_MODEL", "gpt-test")


def test_send_prompt_returns_text(stub_httpx_client) -> None:
    httpx_helper = stub_httpx_client(oac)
    httpx_helper["queue_post"]({"choices": [{"message": {"content": "pong"}}]})

    result = oac.send_prompt("ping")

    assert result == "pong" #nosec
    payload = httpx_helper["calls"]["post"][0]["json"]
    assert payload["model"] == "gpt-test" #nosec
    assert payload["messages"][-1]["content"] == "ping" #nosec


def test_chat_completion_error_raises(stub_httpx_client) -> None:
    httpx_helper = stub_httpx_client(oac)
    httpx_helper["queue_post"]({}, status_code=401, text="Unauthorized")

    client = oac.OpenAIClient()
    with pytest.raises(oac.OpenAIError):
        client.chat_completion([{"role": "user", "content": "Hello"}])


def test_test_connection_false_on_failure(stub_httpx_client) -> None:
    httpx_helper = stub_httpx_client(oac)
    httpx_helper["queue_get"]({}, status_code=500, text="Down")

    client = oac.OpenAIClient()
    assert client.test_connection() is False #nosec
