"""
yaml_parser.py
YAML ingestion parser for llmtestgen.

Extracts:
- title (if present)
- sections (top-level keys)
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

class ParsedYAML(BaseModel):
    title: Optional[str]
    sections: Dict[str, str]
    requirements: List[str]
    acceptance_criteria: List[str]
    examples: List[str]
    raw_text: str
    source_path: str


# ============================================================
# Parser
# ============================================================

class YAMLParser:
    """Extract domain-relevant structure from a YAML spec file."""

    requirement_keywords = [
        "must", "shall", "should", "need to", "required", "cannot", "must not"
    ]

    acceptance_keywords = [
        "given", "when", "then", "acceptance", "criteria"
    ]

    example_keywords = [
        "example", "for instance", "e.g.", "sample"
    ]

    def parse(self, filepath: str | Path) -> ParsedYAML:
        path = Path(filepath)
        text = path.read_text(encoding="utf-8")

        try:
            data = yaml.safe_load(text)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in {filepath}: {e}") from e

        title = None
        if isinstance(data, dict):
            title = data.get("title")

        # ------------------------------
        # Sections: each top-level key
        # ------------------------------
        sections: Dict[str, str] = {}

        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    sections[key] = yaml.safe_dump(value, sort_keys=False).strip()
                else:
                    sections[key] = str(value)

        # ------------------------------------
        # Keyword-based extraction (like MD/JSON)
        # ------------------------------------
        requirements = self._extract_sentences(text, self.requirement_keywords)
        acceptance = self._extract_sentences(text, self.acceptance_keywords)
        examples = self._extract_sentences(text, self.example_keywords)

        return ParsedYAML(
            title=title,
            sections=sections,
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
        """Grab YAML lines containing keywords (similar to the MD/JSON parser)."""
        output = []
        lines = text.split("\n")

        for line in lines:
            normalized = line.lower().strip()
            if any(kw in normalized for kw in keywords):
                output.append(line.strip())

        return output


# ============================================================
# Public factory
# ============================================================

def parse_yaml(path: str | Path) -> ParsedYAML:
    return YAMLParser().parse(path)
