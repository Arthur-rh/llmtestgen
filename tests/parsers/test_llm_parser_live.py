import pytest
# from pathlib import Path

from llmtestgen.services.spec_analyser.parsers.parser_llm import parse_with_llm
from llmtestgen.wrappers.openrouter_client import send_prompt

pytestmark = pytest.mark.live_llm


def test_llm_parser_live(live_llm, tmp_path):
    """Integration test using the real OpenRouter LLM with full verbose output."""

    # ------------------------------------------------------------------
    # Create a temporary test spec
    # ------------------------------------------------------------------
    path = tmp_path / "spec.txt"
    spec_text = """
Feature: Multi-format User Profile Management

Overview:
The platform shall allow users to manage, export, and delete their personal profile data across multiple formats.
All actions must comply with security and audit requirements.

User Profile Fields:
A user profile contains:
- Basic information (name, email, locale)
- Account metadata (creation date, last login, verification status)
- Optional preferences (theme, notifications)

Requirements:
1. The system must support exporting user profiles as JSON, CSV, and XML.
2. Profile deletion must require a two-factor confirmation step.
3. The system shall log all profile exports, updates, and deletions for audit purposes.
4. Export operations should complete within 3 seconds under normal load.
5. The UI must warn users if exporting data may include sensitive information.
6. Administrators must be able to bulk-export up to 5,000 profiles at once.
7. If an export fails, the system must return a machine-readable error message.

Security:
Profile data is considered sensitive. All exports must:
- be encrypted in transit,
- be available only to authenticated users,
- respect per-user access control and permissions.

Acceptance Criteria:
Given a user with a verified account,
When they export their profile as JSON,
Then the system returns a downloadable JSON file containing all profile fields.

Given an administrator with bulk-export permissions,
When they export 2,000 profiles as CSV,
Then the system successfully produces a CSV file and logs the export.

Given a user attempting to delete their profile,
When they confirm with two-factor authentication,
Then the system deletes the profile and records the deletion event.

Given an error occurs during export,
When the system retries and still fails,
Then the user is shown a machine-readable error with a failure code.

Examples:
- CLI: `profile export --format xml --user alice`
- REST: `POST /v1/profile/export { "format": "json", "userId": 123 }`
- Admin console: "Bulk Export → Select 5000 users → Format = CSV → Export"
- Error example: `{ "error": "EXPORT_TIMEOUT", "status": 504 }`

Notes:
The system should be prepared for future export formats.
Developers should consider adding PDF and Parquet export support in later releases.
"""
    path.write_text(spec_text, encoding="utf-8")

    print("\n==================== SPEC INPUT ====================")
    print(spec_text)

    # ------------------------------------------------------------------
    # Real LLM wrapper: calls your send_prompt wrapper
    # ------------------------------------------------------------------
    def real_send_prompt(prompt, *, api_key=None, model=None, system_prompt=None, **kwargs):
        print("\n==================== LLM PROMPT SENT ====================")
        print(prompt)

        response = send_prompt(
            prompt,
            api_key=api_key,
            model=model,
            system_prompt=system_prompt,
            **kwargs,
        )

        print("\n==================== RAW LLM RESPONSE ====================")
        print(response)

        return response

    # ------------------------------------------------------------------
    # Run the actual parser
    # ------------------------------------------------------------------
    parsed = parse_with_llm(path, real_send_prompt)

    # ------------------------------------------------------------------
    # Print parsed structure for manual validation
    # ------------------------------------------------------------------
    print("\n==================== PARSED SPEC MODEL ====================")
    print(f"Title: {parsed.title}")
    print(f"Confidence: {parsed.confidence:.2f}")
    print("\nSections:")
    for k, v in parsed.sections.items():
        print(f"  - {k}: {v}")

    print("\nRequirements:")
    for r in parsed.requirements:
        print(f"  - {r}")

    print("\nAcceptance Criteria:")
    for a in parsed.acceptance_criteria:
        print(f"  - {a}")

    print("\nExamples:")
    for e in parsed.examples:
        print(f"  - {e}")

    print("\nRaw Text:")
    print(parsed.raw_text)

    # ------------------------------------------------------------------
    # Assertions (loose, because real LLM output can vary)
    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    # ASSERTIONS for the COMPLEX SPEC
    # These are intentionally flexible because LLM output is non-deterministic
    # ------------------------------------------------------------------

    # 1. Title must exist and be non-empty
    assert parsed.title is not None and parsed.title.strip(), \
        "LLM failed to extract a title."

    # 2. Confidence must be normalized 0.0–1.0
    assert 0.0 <= parsed.confidence <= 1.0, \
        "Confidence normalization failed."

    # 3. Sections must be a dict with at least 2 meaningful entries
    assert isinstance(parsed.sections, dict) and len(parsed.sections) >= 2, \
        "LLM did not extract enough sections."

    # 4. Requirements: must capture several ‘must/shall/should’ items
    joined_req = " ".join(parsed.requirements).lower()
    assert "must" in joined_req or "shall" in joined_req or "should" in joined_req, \
        "LLM did not extract requirement-like statements."

    # 5. Expected requirement topics should appear
    expected_requirement_keywords = [
        "export", "json", "csv", "xml", "delete", "audit", "encrypt", "bulk"
    ]
    assert any(keyword in joined_req for keyword in expected_requirement_keywords), \
        "Key requirement concepts (export/delete/audit/bulk/etc.) missing."

    # 6. Acceptance criteria: check that Given/When/Then appear somewhere
    joined_ac = " ".join(parsed.acceptance_criteria).lower()
    assert "given" in joined_ac and "when" in joined_ac and "then" in joined_ac, \
        "LLM did not extract acceptance criteria with G/W/T patterns."

    # 7. Acceptance criteria should mention profile export OR deletion
    assert (
        "export" in joined_ac or
        "delete" in joined_ac or
        "file" in joined_ac
    ), "Acceptance criteria did not capture expected behaviors."

    # 8. Examples: must extract at least 2 items
    assert isinstance(parsed.examples, list) and len(parsed.examples) >= 2, \
        "LLM did not extract enough examples."

    # 9. Examples should include a CLI, REST, or error-style element
    joined_examples = " ".join(parsed.examples).lower()
    assert (
        "cli" in joined_examples or
        "http" in joined_examples or
        "post" in joined_examples or
        "error" in joined_examples or
        "csv" in joined_examples
    ), "Examples do not contain CLI/REST/error patterns expected."

    # 10. Raw text must include meaningful content from file
    assert "export" in parsed.raw_text.lower(), \
        "raw_text missing expected original content."