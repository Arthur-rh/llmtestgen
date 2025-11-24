import pytest

from llmtestgen.services.spec_analyser.parsers.parser_md import parse_markdown


def test_parses_basic_structure(write_file):
    content = (
        "# Title\n\n"
        "## Section One\n"
        "- item one\n"
        "1. first\n"
        "```\ncode block\n```\n"
        "Must comply.\n"
        "Given condition then result."
    )
    path = write_file("spec.md", content)

    parsed = parse_markdown(path)

    assert parsed.title == "Title"
    assert "Section One" in parsed.sections
    assert "item one" in parsed.bullets
    assert "first" in parsed.numbered
    assert any("code block" in cb for cb in parsed.code_blocks)
    assert any("Must" in r for r in parsed.requirements)
    assert any("Given" in a for a in parsed.acceptance_criteria)
    assert parsed.raw_text == content
    assert parsed.source_path.endswith("spec.md")


def test_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        parse_markdown("nonexistent.md")
