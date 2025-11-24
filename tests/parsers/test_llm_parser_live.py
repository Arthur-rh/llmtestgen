import pytest

from llmtestgen.services.spec_analyser.parsers.parser_llm import parse_with_llm


pytestmark = pytest.mark.live_llm


def test_llm_parser_live(live_llm, tmp_path):
    path = tmp_path / "spec.txt"
    path.write_text("Sample spec must behave.", encoding="utf-8")

    def dummy_send_prompt(prompt, *, api_key=None, model=None, system_prompt=None, **kwargs):
        return (
            '{"title": "Live", "sections": {"Body": "Sample"}, '
            '"requirements": ["must behave"], "acceptance_criteria": ["then done"], '
            '"examples": ["example"], "confidence": 100}'
        )

    parsed = parse_with_llm(path, dummy_send_prompt)

    assert parsed.title == "Live"
    assert parsed.confidence == 1.0
    assert any("must behave" in r for r in parsed.requirements)
