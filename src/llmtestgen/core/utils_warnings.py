"""Centralized warning messages for spec parsing."""

from enum import Enum


class SpecWarning(str, Enum):
    UNKNOWN_EXTENSION = "Unrecognized file extension; using LLM parser fallback."
    UNKNOWN_EXTENSION_NO_LLM = "Unrecognized file extension and LLM fallback disabled."

    OPENAPI_PARSE_FAILED = "OpenAPI parsing failed ({exc})."
    JSON_PARSE_FAILED = "JSON parsing failed ({exc})."
    YAML_PARSE_FAILED = "YAML parsing failed ({exc})."
    SAFE_YAML_INSPECT_FAILED = "Failed to inspect YAML/JSON content ({exc})."

    LLM_FALLBACK_NOTICE = "Falling back to LLM parser."

    LLM_NO_CONFIDENCE = "LLM did not return a confidence score."
    LLM_LOW_CONFIDENCE = (
        "LLM confidence {confidence}% is below threshold {threshold}%; results may be incomplete."
    )
