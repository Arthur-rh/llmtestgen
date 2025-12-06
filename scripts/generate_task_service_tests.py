#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# -------------------------------------------------------------------
# Make sure `src/` is on sys.path so that `import llmtestgen` works
# -------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Now we can import the project package
from llmtestgen.services.test_generation.test_spec_generator import (
    generate_test_spec_from_paths,
    CodeContextLevel,
)
from llmtestgen.services.test_generation.python_test_writer import (
    write_test_spec_pytest_file,
)
from llmtestgen.wrappers.openrouter_client import send_prompt


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate pytest tests for the task service using LLMTestGen."
    )

    parser.add_argument(
        "--spec-path",
        type=str,
        default="specs/task_service.md",
        help="Path to the specification file (Markdown, JSON, YAML, OpenAPI, etc.).",
    )
    parser.add_argument(
        "--repo-source",
        type=str,
        default="fake_repo",
        help="Path to the Python project root (Git repo or plain directory).",
    )
    parser.add_argument(
        "--output-path",
        type=str,
        default="tests/generated_test_task_service.py",
        help="Where to write the generated pytest file.",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,  # will fall back to OPENROUTER_DEFAULT_MODEL if None
        help="LLM model name (optional, defaults to OPENROUTER_DEFAULT_MODEL).",
    )
    parser.add_argument(
        "--code-context-level",
        type=str,
        choices=[lvl.value for lvl in CodeContextLevel],
        default=CodeContextLevel.FILE_SNIPPETS.value,
        help=(
            "How much code context to provide to the LLM: "
            f"{[lvl.value for lvl in CodeContextLevel]}"
        ),
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # Map CLI string to CodeContextLevel enum
    code_context_level = CodeContextLevel(args.code_context_level)

    print(f"Using spec: {args.spec_path}")
    print(f"Using repo: {args.repo_source}")
    print(f"Output file: {args.output_path}")
    print(f"Code context level: {code_context_level.value}")

    # Call the high-level pipeline:
    # - parse_spec(...)
    # - GitRepository(...)
    # - TestSpecGenerator(...).generate(...)
    test_spec = generate_test_spec_from_paths(
        spec_path=args.spec_path,
        repo_source=args.repo_source,
        send_prompt_fn=send_prompt,   # OpenRouter backend
        model=args.model,             # None -> uses OPENROUTER_DEFAULT_MODEL
        api_key=None,                 # None -> uses OPENROUTER_API_KEY env var
        code_context_level=code_context_level,
        max_files=20,
        max_chars_per_file=4000,
        use_llm_for_spec=False,       # parse spec with classical parsers first
        llm_fallback_for_spec=True,   # if parsing fails, fallback to LLM
    )

    output_path = Path(args.output_path)
    write_test_spec_pytest_file(test_spec, output_path=output_path)

    print(f"\n✅ Generated tests written to: {output_path}")
    print("You can now run:")
    print(f"  pytest {output_path}")


if __name__ == "__main__":
    main()
