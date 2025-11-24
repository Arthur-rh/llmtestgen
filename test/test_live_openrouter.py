"""Optional integration test that can hit the real OpenRouter API."""
from __future__ import annotations
import textwrap
import pytest
from src.wrappers import openrouter_client as orc


@pytest.mark.live_llm
def test_openrouter_live_prompt(live_llm) -> None:
    if not live_llm:
        pytest.skip("Skipping live LLM test since --live-llm was not provided.")
    
    prompt = "hello world! (this is a live api test, say whatever you want)"
    response = orc.send_prompt(prompt)
    print(textwrap.fill(f"""
======== Discussion with the provided OpenRouter model ========
me:{prompt}
----
model: {response}")
----
===============================================================""", width=80, replace_whitespace=False))
    assert isinstance(response, str) and response.strip() #nosec
