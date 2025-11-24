
# 🧪 LLM Test Generation Backend  

A FastAPI backend and Python package for generating automated software tests using Large Language Models.  
This project can retrieve specification files and source code directly from Git repositories, process them and create test cases using various configurable LLMs.

---

## Features

- Git integration: pull specs and code from remote repositories  
- LLM support (OpenAI, Anthropic, local models, etc.)  
- Browser interface for easy interaction with the backend

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

```bash
llmtestgen-settings
```

### Starting the app

```bash
llmtestgen
```

Then open your browser at `http://localhost:3485` to access the web interface.
