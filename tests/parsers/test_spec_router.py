import json
import pytest
import yaml

from llmtestgen.core.utils_errors import SpecParsingError
from llmtestgen.services.spec_analyser.parse_router_normalizer import parse_spec


def test_routes_markdown_by_extension(write_file):
    path = write_file("spec.md", "# Title\nMust comply.")
    result = parse_spec(path, send_prompt_fn=lambda *a, **k: "", llm_fallback=False)

    assert result.spec.title is None
    assert any("Must comply." in r for r in result.spec.requirements)


def test_routes_json_by_extension(write_file):
    path = write_file("spec.json", json.dumps({"title": "API", "note": "must work"}))
    result = parse_spec(path, send_prompt_fn=lambda *a, **k: "", llm_fallback=False)

    assert result.spec.title == "API"
    assert any("must work" in r for r in result.spec.requirements)


def test_routes_yaml_by_extension(write_file):
    path = write_file("spec.yaml", yaml.safe_dump({"title": "Service", "note": "should run"}))
    result = parse_spec(path, send_prompt_fn=lambda *a, **k: "", llm_fallback=False)

    assert result.spec.title == "Service"
    assert any("should run" in r for r in result.spec.requirements)


def test_detects_openapi_via_content_sniff(write_file):
    data = {"openapi": "3.0.0", "info": {"title": "Pet API"}, "paths": {}}
    path = write_file("api.yaml", yaml.safe_dump(data))
    result = parse_spec(path, send_prompt_fn=lambda *a, **k: "", llm_fallback=False)

    assert result.spec.title == "Pet API"
    assert "openapi" in result.spec.sections


def test_router_fails_unknown_extension_without_llm(write_file):
    path = write_file("spec.txt", "some text")
    with pytest.raises(SpecParsingError):
        parse_spec(path, send_prompt_fn=lambda *a, **k: "", llm_fallback=False)


def test_router_wraps_parser_errors(write_file):
    path = write_file("bad.json", "{invalid")
    with pytest.raises(SpecParsingError):
        parse_spec(path, send_prompt_fn=lambda *a, **k: "", llm_fallback=False)
