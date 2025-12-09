
# LLM Test Generation Backend

A Python tool for generating automated software tests using Large Language Models.  
This project can retrieve specification files and source code directly from Git repositories, process them and create test cases using various configurable LLMs.

---

## Features

- Git integration: pull specs and code from remote repositories (or use local directories)
- LLM support (OpenAI, OpenRouter)
- Command line interface

---

## Installation

### Manual Installation

```bash
git clone <repository_url>
cd llmtestgen
pip install -e .
```

### Using pip

```bash
pip install llmtestgen
```

---

## Usage

### Setup the application

```bash
llmtestgen-setup
```

### Edit settings

This is where you can configure your LLM API keys and other settings.
The auth for git is handled by your local git configuration.

```bash
llmtestgen-settings
```

### Starting the app

```bash
llmtestgen <spec_path> <repo_source> [--output-path <output_path>] [--code-context-level <level>] [--force-spec-llm] [--fallback-spec-llm]
```

## Development

### Running Tests

To run the test suite, use:

```bash
pytest
```

Note: some test cases may require network access and LLM API access tokens, these tests are skipped by default. Use the `--live-git` flag to enable tests that clone remote Git repositories and `--live-llm` to enable tests that interact with LLM APIs.

### Possible points of improvement

- Add support for more LLM providers, local models, custom API endpoints & format
- GUI/web interface
<<<<<<< HEAD
- Better prompt design
=======
>>>>>>> b3f59046dd8960bb044c30c46bde24125ef3c2c8
