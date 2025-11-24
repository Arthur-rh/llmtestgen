"""
json_parser.py
JSON ingestion parser for llmtestgen.

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
import json

from pydantic import BaseModel


# ============================================================
# Models returned by the parser
# ============================================================

class ParsedJSON(BaseModel):
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

class JSONParser:
    """Extract domain-relevant structure from a JSON spec file."""

    requirement_keywords = [
        "must", "shall", "should", "need to", "required", "cannot", "must not"
    ]

    acceptance_keywords = [
        "given", "when", "then", "acceptance", "criteria"
    ]

    example_keywords = [
        "example", "for instance", "e.g.", "sample"
    ]

    def parse(self, filepath: str | Path) -> ParsedJSON:
        path = Path(filepath)
        text = path.read_text(encoding="utf-8")

        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {filepath}: {e}") from e

        title = data.get("title") if isinstance(data, dict) else None

        # ------------------------------
        # Sections: each top-level key
        # ------------------------------
        sections: Dict[str, str] = {}
        for key, value in (data.items() if isinstance(data, dict) else []):
            if isinstance(value, (dict, list)):
                sections[key] = json.dumps(value, indent=2)
            else:
                sections[key] = str(value)

        # ------------------------------------
        # Extract requirements, acceptance, examples
        # from the raw text (like Markdown parser)
        # ------------------------------------
        requirements = self._extract_sentences(text, self.requirement_keywords)
        acceptance = self._extract_sentences(text, self.acceptance_keywords)
        examples = self._extract_sentences(text, self.example_keywords)

        return ParsedJSON(
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
        """Search all lines for keywords (same logic as MD parser)."""
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

def parse_json(path: str | Path) -> ParsedJSON:
    return JSONParser().parse(path)
