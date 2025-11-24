import pytest
import yaml

from llmtestgen.services.spec_analyser.parsers.parser_openapi import parse_openapi


def test_parses_openapi_fields(write_file):
    spec = {
        "openapi": "3.0.0",
        "info": {"title": "Pet API", "version": "1.0.0"},
        "paths": {
            "/pets": {
                "get": {"summary": "List pets"},
                "post": {"operationId": "createPet"},
            }
        },
    }
    path = write_file("openapi.yaml", yaml.safe_dump(spec))

    parsed = parse_openapi(path)

    assert parsed.title == "Pet API"
    assert parsed.version == "1.0.0"
    assert "paths" in parsed.sections
    assert any("GET /pets - List pets" in ep for ep in parsed.endpoints)
    assert any("POST /pets - createPet" in ep for ep in parsed.endpoints)
    assert parsed.raw_text.startswith("openapi: 3.0.0")
    assert parsed.source_path.endswith("openapi.yaml")


def test_invalid_openapi_raises_value_error(write_file):
    path = write_file("bad_openapi.yaml", "[]")
    with pytest.raises(ValueError):
        parse_openapi(path)
