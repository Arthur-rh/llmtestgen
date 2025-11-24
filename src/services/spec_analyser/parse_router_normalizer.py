"""
Unified routing and normalization of spec files into a normalized model.
"""

from __future__ import annotations
from pathlib import Path
from typing import Optional, Dict, List, Union

import yaml
from pydantic import BaseModel, Field

from src.core.utils_errors import SpecParsingError
from src.core.utils_warnings import SpecWarning

# --- Parser models -------------------------------------------------------------

from .parsers.parser_json import JSONParser, ParsedJSON
from .parsers.parser_yaml import YAMLParser, ParsedYAML
from .parsers.parser_md import MarkdownParser, ParsedMarkdown
from .parsers.parser_openapi import OpenAPIParser, ParsedOpenAPI
from .parsers.parser_llm import LLMParser, ParsedLLMSpec


# ==============================================================================
# Normalized Model
# ==============================================================================

class NormalizedSpec(BaseModel):
    """Normalized representation returned by the router."""

    title: Optional[str] = None
    sections: Dict[str, str] = Field(default_factory=dict)
    requirements: List[str] = Field(default_factory=list)
    acceptance_criteria: List[str] = Field(default_factory=list)
    examples: List[str] = Field(default_factory=list)
    raw_text: str
    source_path: str
    confidence: Optional[float] = None


ParsedSpecType = Union[
    ParsedMarkdown,
    ParsedJSON,
    ParsedYAML,
    ParsedOpenAPI,
    ParsedLLMSpec,
]


def normalize_parsed_spec(parsed: ParsedSpecType) -> NormalizedSpec:
    """Normalize any parser output into a unified model."""
    return NormalizedSpec(
        title=getattr(parsed, "title", None),
        sections=getattr(parsed, "sections", {}) or {},
        requirements=getattr(parsed, "requirements", []) or [],
        acceptance_criteria=getattr(parsed, "acceptance_criteria", []) or [],
        examples=getattr(parsed, "examples", []) or [],
        raw_text=getattr(parsed, "raw_text", ""),
        source_path=getattr(parsed, "source_path", ""),
        confidence=getattr(parsed, "confidence", None),
    )


# ==============================================================================
# Public ParseResult model
# ==============================================================================

class ParseResult(BaseModel):
    """Unified parse output for API consumption."""
    spec: NormalizedSpec
    warnings: List[str]


# ==============================================================================
# SpecRouter
# ==============================================================================

class SpecRouter:
    """Route a spec file through the appropriate parser and normalize the output."""

    DEFAULT_CONFIDENCE_THRESHOLD = 0.7

    def __init__(
        self,
        send_prompt_fn,
        *,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
        llm_fallback: bool = False,
    ) -> None:

        self.send_prompt_fn = send_prompt_fn
        self.model = model
        self.api_key = api_key
        self.confidence_threshold = confidence_threshold
        self.llm_fallback = llm_fallback

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def parse(
        self,
        filepath: str | Path,
        *,
        use_llm: bool = False,
    ) -> ParseResult:
        path = Path(filepath)
        warnings: List[str] = []

        try:
            if use_llm:
                parsed = self._parse_via_llm(path, warnings)
            else:
                parsed = self._route(path, warnings)

            return ParseResult(spec=parsed, warnings=warnings)

        except SpecParsingError:
            raise
        except Exception as exc:
            raise SpecParsingError(str(exc)) from exc

    # ------------------------------------------------------------------
    # Routing
    # ------------------------------------------------------------------
    def _route(self, path: Path, warnings: List[str]) -> NormalizedSpec:
        suffix = path.suffix.lower()

        # Markdown
        if suffix == ".md":
            parsed = MarkdownParser().parse(path)
            return normalize_parsed_spec(parsed)

        # JSON
        if suffix == ".json":
            return self._parse_json_like(path, warnings)

        # YAML
        if suffix in {".yaml", ".yml"}:
            return self._parse_yaml_like(path, warnings)

        # Fallback
        if self.llm_fallback:
            warnings.append(SpecWarning.UNKNOWN_EXTENSION.value)
            return self._parse_via_llm(path, warnings)

        raise SpecParsingError(SpecWarning.UNKNOWN_EXTENSION_NO_LLM.value)

    # JSON routing
    def _parse_json_like(self, path: Path, warnings: List[str]) -> NormalizedSpec:
        data = self._safe_yaml_load(path, warnings)

        if data is not None and self._looks_like_openapi(data):
            try:
                parsed = OpenAPIParser().parse(path)
                return normalize_parsed_spec(parsed)
            except Exception as exc:
                warnings.append(
                    SpecWarning.OPENAPI_PARSE_FAILED.value.format(exc=exc)
                )
                if self.llm_fallback:
                    warnings.append(SpecWarning.LLM_FALLBACK_NOTICE.value)
                    return self._parse_via_llm(path, warnings)
                raise SpecParsingError(
                    "OpenAPI parsing failed and LLM fallback disabled."
                ) from exc

        try:
            parsed = JSONParser().parse(path)
            return normalize_parsed_spec(parsed)
        except Exception as exc:
            warnings.append(SpecWarning.JSON_PARSE_FAILED.value.format(exc=exc))
            if self.llm_fallback:
                warnings.append(SpecWarning.LLM_FALLBACK_NOTICE.value)
                return self._parse_via_llm(path, warnings)
            raise SpecParsingError(
                "JSON parsing failed and LLM fallback disabled."
            ) from exc

    # YAML routing
    def _parse_yaml_like(self, path: Path, warnings: List[str]) -> NormalizedSpec:
        data = self._safe_yaml_load(path, warnings)

        if data is not None and self._looks_like_openapi(data):
            try:
                parsed = OpenAPIParser().parse(path)
                return normalize_parsed_spec(parsed)
            except Exception as exc:
                warnings.append(
                    SpecWarning.OPENAPI_PARSE_FAILED.value.format(exc=exc)
                )
                if self.llm_fallback:
                    warnings.append(SpecWarning.LLM_FALLBACK_NOTICE.value)
                    return self._parse_via_llm(path, warnings)
                raise SpecParsingError(
                    "OpenAPI parsing failed and LLM fallback disabled."
                ) from exc

        try:
            parsed = YAMLParser().parse(path)
            return normalize_parsed_spec(parsed)
        except Exception as exc:
            warnings.append(SpecWarning.YAML_PARSE_FAILED.value.format(exc=exc))
            if self.llm_fallback:
                warnings.append(SpecWarning.LLM_FALLBACK_NOTICE.value)
                return self._parse_via_llm(path, warnings)
            raise SpecParsingError(
                "YAML parsing failed and LLM fallback disabled."
            ) from exc

    # ------------------------------------------------------------------
    # LLM Parser
    # ------------------------------------------------------------------
    def _parse_via_llm(self, path: Path, warnings: List[str]) -> NormalizedSpec:
        parsed = LLMParser(
            self.send_prompt_fn,
            model=self.model,
            api_key=self.api_key,
            confidence_threshold=self.confidence_threshold,
        ).parse(path)

        warnings.extend(self._collect_llm_warnings(parsed))
        return normalize_parsed_spec(parsed)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _collect_llm_warnings(self, parsed: ParsedLLMSpec) -> List[str]:
        warnings: List[str] = []

        if parsed.confidence is None:
            warnings.append(SpecWarning.LLM_NO_CONFIDENCE.value)
        elif parsed.confidence < self.confidence_threshold:
            warnings.append(
                SpecWarning.LLM_LOW_CONFIDENCE.value.format(
                    confidence=int(parsed.confidence * 100),
                    threshold=int(self.confidence_threshold * 100),
                )
            )

        return warnings

    @staticmethod
    def _looks_like_openapi(data: object) -> bool:
        if not isinstance(data, dict):
            return False
        return "openapi" in data or "swagger" in data or "paths" in data

    @staticmethod
    def _safe_yaml_load(path: Path, warnings: List[str]):
        try:
            return yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception as exc:
            warnings.append(
                SpecWarning.SAFE_YAML_INSPECT_FAILED.value.format(exc=exc)
            )
            return None


# ==============================================================================
# Convenience function
# ==============================================================================

def parse_spec(
    filepath: str | Path,
    *,
    send_prompt_fn,
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    confidence_threshold: float = SpecRouter.DEFAULT_CONFIDENCE_THRESHOLD,
    use_llm: bool = False,
    llm_fallback: bool = False,
) -> ParseResult:

    router = SpecRouter(
        send_prompt_fn,
        model=model,
        api_key=api_key,
        confidence_threshold=confidence_threshold,
        llm_fallback=llm_fallback,
    )
    return router.parse(filepath, use_llm=use_llm)
