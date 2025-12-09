import argparse

from llmtestgen.services.test_generation.test_spec_generator import CodeContextLevel

parser = argparse.ArgumentParser(
    description="Generate pytest tests for the task service using LLMTestGen."
)

parser.add_argument(
    "spec-path",
    type=str,
    help="Path to the specification file (Markdown, JSON, YAML, OpenAPI, etc.).",
)
parser.add_argument(
    "repo-source",
    type=str,
    help="Path to the Python project root (Git repo or plain directory).",
)
parser.add_argument(
    "--output-path",
    type=str,
    default=".",
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
parser.add_argument(
    "--force-spec-llm",
    action="store_true",
    help="Force using LLM to parse the specification, bypassing classical parsers.",
)
parser.add_argument(
    "--fallback-spec-llm",
    action="store_true",
    help="Fallback to LLM parsing if classical parsing of the specification fails.",
)

# Parse the arguments
# use import from other files to access them
args = parser.parse_args()