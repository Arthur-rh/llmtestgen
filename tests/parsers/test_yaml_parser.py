import pytest
import yaml

from llmtestgen.services.spec_analyser.parsers.parser_yaml import parse_yaml


def test_parses_basic_structure(write_file):
    payload = {
        "title": "Service",
        "config": {"port": 8000},
        "note": "must be secure",
        "example": "sample usage",
    }
    path = write_file("spec.yaml", yaml.safe_dump(payload))

    parsed = parse_yaml(path)

    assert parsed.title == "Service"
    assert "config" in parsed.sections
    assert "port" in parsed.sections["config"]
    assert any("must be secure" in r for r in parsed.requirements)
    assert any("sample usage" in e for e in parsed.examples)
    assert parsed.raw_text.startswith("title:")
    assert parsed.source_path.endswith("spec.yaml")


def test_invalid_yaml_raises_value_error(write_file):
    path = write_file("bad.yaml", "title: test: nope")
    with pytest.raises(ValueError):
        parse_yaml(path)
