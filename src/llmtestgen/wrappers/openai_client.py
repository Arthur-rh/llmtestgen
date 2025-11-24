"""Utility helpers for interacting with the OpenAI API."""
from __future__ import annotations

import os
from typing import Any, Dict, Iterable, Mapping, MutableMapping, Optional, Sequence

import httpx


class OpenAIError(RuntimeError):
    """Raised when the OpenAI API returns an error response."""


class OpenAIClient:
    """Simple wrapper around the OpenAI REST API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        base_url: str = "https://api.openai.com/v1",
        default_model: Optional[str] = None,
        timeout: float = 30.0,
        organization: Optional[str] = None,
    ) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("An OpenAI API key is required.")

        self.base_url = base_url.rstrip("/")
        self.default_model = default_model or os.getenv("OPENAI_DEFAULT_MODEL")
        self.organization = organization or os.getenv("OPENAI_ORG")
        self._client = httpx.Client(base_url=self.base_url, timeout=timeout)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "OpenAIClient":
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()

    def _build_headers(self) -> Dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if self.organization:
            headers["OpenAI-Organization"] = self.organization
        return headers

    def _post(self, endpoint: str, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        response = self._client.post(endpoint, headers=self._build_headers(), json=payload)
        if response.status_code >= 400:
            raise OpenAIError(
                f"OpenAI request failed ({response.status_code}): {response.text}"
            )
        return response.json()

    def chat_completion(
        self,
        messages: Sequence[Mapping[str, str]],
        *,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        extra_body: Optional[MutableMapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        """Send a chat completion request and return the parsed JSON response."""

        chosen_model = model or self.default_model
        if not chosen_model:
            raise ValueError("A model must be provided either per-call or as default.")

        payload: Dict[str, Any] = {
            "model": chosen_model,
            "messages": list(messages),
        }
        if temperature is not None:
            payload["temperature"] = temperature
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if extra_body:
            payload.update(extra_body)

        return self._post("/chat/completions", payload)

    def list_models(self) -> Mapping[str, Any]:
        response = self._client.get("/models", headers=self._build_headers())
        if response.status_code >= 400:
            raise OpenAIError(
                f"OpenAI model listing failed ({response.status_code}): {response.text}"
            )
        return response.json()

    def test_connection(self) -> bool:
        try:
            self.list_models()
        except OpenAIError:
            return False
        return True


def send_prompt(
    prompt: str,
    *,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    system_prompt: Optional[str] = None,
    **kwargs: Any,
) -> str:
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    with OpenAIClient(api_key=api_key, default_model=model) as client:
        result = client.chat_completion(messages, extra_body=kwargs)

    choices: Iterable[Mapping[str, Any]] = result.get("choices", [])
    for choice in choices:
        message = choice.get("message")
        if message and "content" in message:
            return str(message["content"])

    raise OpenAIError("No message content returned from OpenAI response.")


def test_connection(api_key: Optional[str] = None) -> bool:
    with OpenAIClient(api_key=api_key) as client:
        return client.test_connection()
