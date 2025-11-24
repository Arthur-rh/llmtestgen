"""
openapi_parser.py
OpenAPI ingestion parser for llmtestgen.

Extracts:
- title and version from `info`
- sections (top-level keys)
- endpoint summaries (HTTP method + path + summary/operationId)
- requirement-like sentences
- acceptance criteria
- examples
"""

from __future__ import annotations

from typing import Dict, List, Optional
from pathlib import Path

import yaml
from pydantic import BaseModel


# ============================================================
# Models returned by the parser
# ============================================================

class ParsedOpenAPI(BaseModel):
    title: Optional[str]
    version: Optional[str]
    sections: Dict[str, str]
    endpoints: List[str]
    requirements: List[str]
    acceptance_criteria: List[str]
    examples: List[str]
    raw_text: str
    source_path: str


# ============================================================
# Parser
# ============================================================

class OpenAPIParser:
    """Extract domain-relevant structure from an OpenAPI spec (YAML or JSON)."""

    requirement_keywords = [
        "must", "shall", "should", "need to", "required", "cannot", "must not"
    ]

    acceptance_keywords = [
        "given", "when", "then", "acceptance", "criteria"
    ]

    example_keywords = [
        "example", "for instance", "e.g.", "sample"
    ]

    http_methods = {
        "get", "post", "put", "delete", "patch", "options", "head", "trace"
    }

    def parse(self, filepath: str | Path) -> ParsedOpenAPI:
        path = Path(filepath)
        text = path.read_text(encoding="utf-8")

        # OpenAPI is usually YAML but can be JSON; yaml.safe_load handles both
        try:
            data = yaml.safe_load(text)
        except yaml.YAMLError as err:
            raise ValueError(f"Invalid OpenAPI (YAML/JSON) in {filepath}: {err}") from err

        if not isinstance(data, dict):
            raise ValueError(f"OpenAPI spec in {filepath} must be a mapping at the top level")

        info = data.get("info") or {}
        title = None
        version = None

        if isinstance(info, dict):
            title = info.get("title")
            version = info.get("version")

        # ------------------------------
        # Sections: each top-level key
        # ------------------------------
        sections: Dict[str, str] = {}
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                sections[key] = yaml.safe_dump(value, sort_keys=False).strip()
            else:
                sections[key] = str(value)

        # ------------------------------
        # Endpoints: methods under `paths`
        # ------------------------------
        endpoints: List[str] = []
        paths = data.get("paths") or {}
        if isinstance(paths, dict):
            for route, methods in paths.items():
                if not isinstance(methods, dict):
                    continue
                for method, operation in methods.items():
                    method_lower = str(method).lower()
                    if method_lower not in self.http_methods:
                        continue
                    summary = None
                    operation_id = None
                    if isinstance(operation, dict):
                        summary = operation.get("summary")
                        operation_id = operation.get("operationId")

                    # Build a compact endpoint descriptor
                    descriptor_parts = [method_lower.upper(), route]
                    if summary:
                        descriptor_parts.append(f"- {summary}")
                    elif operation_id:
                        descriptor_parts.append(f"- {operation_id}")

                    endpoints.append(" ".join(descriptor_parts))

        # ------------------------------------
        # Keyword-based extraction
        # ------------------------------------
        requirements = self._extract_sentences(text, self.requirement_keywords)
        acceptance = self._extract_sentences(text, self.acceptance_keywords)
        examples = self._extract_sentences(text, self.example_keywords)

        return ParsedOpenAPI(
            title=title,
            version=version,
            sections=sections,
            endpoints=endpoints,
            requirements=requirements,
            acceptance_criteria=acceptance,
            examples=examples,
            raw_text=text,
            source_path=str(path),
        )

    # ============================================================
    # Helpers
    # ============================================================

    def _extract_sentences(self, text: str, keywords: List[str]) -> List[str]:
        """Grab lines containing any of the given keywords (simple heuristic)."""
        output = []
        lines = text.split("\n")

        for line in lines:
            normalized = line.lower().strip()
            if any(kw in normalized for kw in keywords):
                output.append(line.strip())

        return output


# ============================================================
# Public factory function
# ============================================================

def parse_openapi(path: str | Path) -> ParsedOpenAPI:
    return OpenAPIParser().parse(path)
