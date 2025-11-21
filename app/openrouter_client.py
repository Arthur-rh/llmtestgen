"""Utility helpers for interacting with the OpenRouter API."""
from __future__ import annotations

import os
from typing import Any, Dict, Iterable, Mapping, MutableMapping, Optional, Sequence

import httpx


class OpenRouterError(RuntimeError):
    """Raised when the OpenRouter API returns an error response."""


class OpenRouterClient:
    """Simple wrapper around the OpenRouter REST API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://openrouter.ai/api/v1",
        default_model: Optional[str] = None,
        timeout: float = 30.0,
        site_url: Optional[str] = None,
        app_title: Optional[str] = None,
    ) -> None:
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("An OpenRouter API key is required.")

        self.base_url = base_url.rstrip("/")
        self.default_model = default_model or os.getenv("OPENROUTER_DEFAULT_MODEL")
        self.site_url = site_url or os.getenv("OPENROUTER_SITE_URL")
        self.app_title = app_title or os.getenv("OPENROUTER_APP_TITLE")
        self._client = httpx.Client(base_url=self.base_url, timeout=timeout)

    def close(self) -> None:
        """Close the underlying HTTP client."""

        self._client.close()

    def __enter__(self) -> "OpenRouterClient":
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()

    def _build_headers(self) -> Dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if self.site_url:
            headers["HTTP-Referer"] = self.site_url
        if self.app_title:
            headers["X-Title"] = self.app_title
        return headers

    def _post(self, endpoint: str, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        response = self._client.post(endpoint, headers=self._build_headers(), json=payload)
        if response.status_code >= 400:
            details = response.text
            raise OpenRouterError(f"OpenRouter request failed ({response.status_code}): {details}")
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
        """Return the available models exposed by the OpenRouter API."""

        response = self._client.get("/models", headers=self._build_headers())
        if response.status_code >= 400:
            raise OpenRouterError(
                f"OpenRouter model listing failed ({response.status_code}): {response.text}"
            )
        return response.json()


def send_prompt(
    prompt: str,
    *,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    system_prompt: Optional[str] = None,
    **kwargs: Any,
) -> str:
    """Convenience helper for single-turn prompts.

    Returns just the assistant's text output which is the most common need for the app.
    """

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    with OpenRouterClient(api_key=api_key, default_model=model) as client:
        result = client.chat_completion(messages, extra_body=kwargs)

    choices: Iterable[Mapping[str, Any]] = result.get("choices", [])
    for choice in choices:
        message = choice.get("message")
        if message and "content" in message:
            return str(message["content"])

    raise OpenRouterError("No message content returned from OpenRouter response.")
