"""
markdown_parser.py
Markdown ingestion parser for llmtestgen.

Extracts:
- headings and sections
- lists (bullets and numbered)
- fenced code blocks
- requirement-like sentences
- acceptance criteria / examples
"""

from __future__ import annotations

from typing import Dict, List, Optional
from pathlib import Path

from markdown_it import MarkdownIt
from pydantic import BaseModel


# ============================================================
# Models returned by the parser
# ============================================================

class ParsedMarkdown(BaseModel):
    title: Optional[str]
    sections: Dict[str, str]
    bullets: List[str]
    numbered: List[str]
    code_blocks: List[str]
    requirements: List[str]
    acceptance_criteria: List[str]
    examples: List[str]
    raw_text: str
    source_path: str


# ============================================================
# Parser
# ============================================================

class MarkdownParser:
    """Extract domain-relevant structure from a Markdown file."""

    requirement_keywords = [
        "must", "shall", "should", "need to", "required", "cannot", "must not"
    ]

    acceptance_keywords = [
        "given", "when", "then", "acceptance", "criteria"
    ]

    example_keywords = [
        "example", "for instance", "e.g.", "sample"
    ]

    def parse(self, filepath: str | Path) -> ParsedMarkdown:
        path = Path(filepath)
        text = path.read_text(encoding="utf-8")

        md = MarkdownIt().enable("table").enable("fence")
        tokens = md.parse(text)

        title = None
        sections: Dict[str, str] = {}
        bullets: List[str] = []
        numbered: List[str] = []
        code_blocks: List[str] = []

        current_section_name = None
        current_section_content: List[str] = []

        # Token-based extraction
        for token in tokens:
            # ---------------------------
            # Headings
            # ---------------------------
            if token.type == "heading_open":
                # Save previous section if exists
                if current_section_name:
                    sections[current_section_name] = "\n".join(current_section_content)
                    current_section_content = []

            if token.type == "heading_close":
                pass

            if token.type == "inline" and token.map:
                if token.markup.startswith("#"):
                    heading_text = token.content.strip()
                    if title is None:
                        title = heading_text
                    current_section_name = heading_text
                    continue

            # ---------------------------
            # Lists
            # ---------------------------
            if token.type == "list_item_open":
                pass

            if token.type == "inline" and token.content:
                # bullets: "-", "*" or "+"
                if token.content.startswith(("-", "*", "+")):
                    bullets.append(token.content.lstrip("-*+ ").strip())

                # ordered lists: "1. Something"
                if token.content[:2].isdigit() and token.content[1] == ".":
                    numbered.append(token.content[2:].strip())

            # ---------------------------
            # Code blocks
            # ---------------------------
            if token.type == "fence":
                code_blocks.append(token.content.strip())

            # ---------------------------
            # Collect section content
            # ---------------------------
            if current_section_name and token.type == "inline" and token.content:
                current_section_content.append(token.content)

        # Save last section
        if current_section_name and current_section_content:
            sections[current_section_name] = "\n".join(current_section_content)

        # ------------------------------------------------
        # Requirement & acceptance criteria extraction
        # ------------------------------------------------
        requirements = self._extract_sentences(text, self.requirement_keywords)
        acceptance = self._extract_sentences(text, self.acceptance_keywords)
        examples = self._extract_sentences(text, self.example_keywords)

        return ParsedMarkdown(
            title=title,
            sections=sections,
            bullets=bullets,
            numbered=numbered,
            code_blocks=code_blocks,
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
        """Grab sentences containing any of the given keywords."""
        output = []
        sentences = text.split("\n")

        for s in sentences:
            normalized = s.lower().strip()
            if any(kw in normalized for kw in keywords):
                output.append(s.strip())

        return output


# ============================================================
# Public factory function
# ============================================================

def parse_markdown(path: str | Path) -> ParsedMarkdown:
    return MarkdownParser().parse(path)
