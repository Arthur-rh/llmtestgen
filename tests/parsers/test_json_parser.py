import json
import pytest

from llmtestgen.services.spec_analyser.parsers.parser_json import parse_json


def test_parses_basic_structure(write_file):
    payload = {
        "title": "API",
        "feature": {"enabled": True},
        "note": "Must work",
        "example": "for instance",
    }
    path = write_file("spec.json", json.dumps(payload))

    parsed = parse_json(path)

    assert parsed.title == "API"
    assert "feature" in parsed.sections
    assert "enabled" in parsed.sections["feature"]
    assert "note" in parsed.sections
    assert any("Must work" in r for r in parsed.requirements)
    assert any("instance" in e for e in parsed.examples)
    assert parsed.raw_text.strip().startswith("{")
    assert parsed.source_path.endswith("spec.json")


def test_invalid_json_raises_value_error(write_file):
    path = write_file("bad.json", "{invalid")
    with pytest.raises(ValueError):
        parse_json(path)
