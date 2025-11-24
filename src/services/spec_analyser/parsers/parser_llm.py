"""
llm_parser.py
LLM-based ingestion parser for llmtestgen.

Uses an LLM to interpret arbitrary specification files and
extract a structured spec model plus a confidence score.
"""

from __future__ import annotations

from typing import Dict, Optional
from pathlib import Path
import json
from pydantic import BaseModel, ValidationError


# ============================================================
# Model returned by the parser
# ============================================================

class ParsedLLMSpec(BaseModel):
    """Model returned after LLM parses a spec file."""
    title: Optional[str]
    sections: Dict[str, str]
    requirements: list[str]
    acceptance_criteria: list[str]
    examples: list[str]
    raw_text: str
    source_path: str
    confidence: float


# ============================================================
# Parser
# ============================================================

class LLMParser:
    """
    Use an LLM to parse a specification file into a structured model.

    The parser sends:
    - A system prompt describing how the LLM should behave
    - A user prompt containing the spec text and the extraction instructions

    The LLM must return a strict JSON object containing:
      {
        "title": str or null,
        "sections": { ... },
        "requirements": [...],
        "acceptance_criteria": [...],
        "examples": [...],
        "confidence": 0-100
      }
    """

    DEFAULT_CONFIDENCE_THRESHOLD = 0.7  # 70%

    def __init__(
        self,
        send_prompt_fn,
        *,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
    ) -> None:
        """
        Args:
            send_prompt_fn: callback function with signature:
                send_prompt(prompt: str, *, api_key, model, system_prompt, **kwargs) -> str
            model: default LLM model
            api_key: default API key
            confidence_threshold: warn if LLM confidence % < threshold * 100
        """
        self.send_prompt_fn = send_prompt_fn
        self.model = model
        self.api_key = api_key
        self.confidence_threshold = confidence_threshold

    # ------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------

    def parse(self, filepath: str | Path) -> ParsedLLMSpec:
        path = Path(filepath)
        text = path.read_text(encoding="utf-8")

        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(text)

        response = self.send_prompt_fn(
            user_prompt,
            api_key=self.api_key,
            model=self.model,
            system_prompt=system_prompt,
        )

        parsed = self._parse_llm_json(
            response,
            raw_text=text,
            source_path=str(path),
        )

        return parsed

    # ------------------------------------------------------------
    # PROMPT GENERATION
    # ------------------------------------------------------------

    def _build_system_prompt(self) -> str:
        """Explain how the LLM should behave and what to extract."""
        return (
            "You are a strict specification parser. "
            "Your task is to read input text and extract structured information.\n\n"
            "Return ONLY a JSON object with these exact fields:\n"
            "  - title: string or null\n"
            "  - sections: object mapping section names to text\n"
            "  - requirements: array of requirement-like sentences\n"
            "  - acceptance_criteria: array of acceptance criteria\n"
            "  - examples: array of example statements\n"
            "  - confidence: integer 0-100 expressing how confident you are "
            "    that you extracted the spec correctly\n\n"
            "DO NOT return explanations. DO NOT wrap the JSON in code fences. "
            "Only output raw JSON."
        )

    def _build_user_prompt(self, text: str) -> str:
        return (
            "Parse the following specification file. Use your best judgment to identify:\n"
            "- title or heading\n"
            "- sections and subsections\n"
            "- requirement-like sentences (must, shall, should, cannot, etc.)\n"
            "- acceptance criteria (Given/When/Then patterns, etc.)\n"
            "- examples or usage patterns\n\n"
            "Return ONLY the JSON object described above.\n\n"
            "Here is the specification content:\n"
            "------------------\n"
            f"{text}\n"
            "------------------\n"
        )

    # ------------------------------------------------------------
    # JSON PARSING
    # ------------------------------------------------------------

    def _parse_llm_json(
        self, response_text: str, *, raw_text: str, source_path: str
    ) -> ParsedLLMSpec:
        """Validate LLM output JSON and return the pydantic model."""
        try:
            data = json.loads(response_text)
        except json.JSONDecodeError as err:
            raise ValueError(
                "LLM returned invalid JSON. Response was:\n"
                f"{response_text}"
            ) from err

        try:
            return ParsedLLMSpec(
                title=data.get("title"),
                sections=data.get("sections") or {},
                requirements=data.get("requirements") or [],
                acceptance_criteria=data.get("acceptance_criteria") or [],
                examples=data.get("examples") or [],
                raw_text=data.get("raw_text") or raw_text,
                source_path=data.get("source_path") or source_path,
                confidence=self._normalize_confidence(data.get("confidence")),
            )
        except ValidationError as err:
            raise ValueError(f"LLM JSON did not match ParsedLLMSpec requirements: {err}") from err

    def _normalize_confidence(self, value: object) -> float:
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return 0.0
        normalized = max(0.0, min(1.0, numeric / 100))
        return normalized


# ============================================================
# Public factory function
# ============================================================

def parse_with_llm(
    filepath: str | Path,
    send_prompt_fn,
    *,
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    confidence_threshold: float = LLMParser.DEFAULT_CONFIDENCE_THRESHOLD,
) -> ParsedLLMSpec:
    parser = LLMParser(
        send_prompt_fn,
        model=model,
        api_key=api_key,
        confidence_threshold=confidence_threshold,
    )
    return parser.parse(filepath)
