"""Tests for Git repository convenience wrappers."""
from __future__ import annotations

from pathlib import Path

import pytest

from llmtestgen.wrappers import git_repository as gitrepo


@pytest.fixture
def temp_local_repo(tmp_path: Path) -> Path:
    root = tmp_path / "sample"
    root.mkdir()
    (root / "README.md").write_text("sample content")
    (root / "src").mkdir()
    (root / "src" / "main.py").write_text("print('hello')\n")
    return root


def test_get_file_contents_local(temp_local_repo: Path) -> None:
    repo = gitrepo.GitRepository(str(temp_local_repo))
    assert "sample content" in repo.get_file_contents("README.md") # nosec



def test_list_files_local(temp_local_repo: Path) -> None:
    repo = gitrepo.GitRepository(str(temp_local_repo))
    files = repo.list_files()
    assert "README.md" in files # nosec
    assert "src/main.py" in files # nosec


def test_clone_linux_repo_lists_files(live_git: bool) -> None:
    if not live_git:
        pytest.skip("Skipping remote clone test (enable with --live-git).")

    files = gitrepo.list_repo_files("https://github.com/octocat/Hello-World", branch="master")
    assert "README" in files # nosec
    readme = gitrepo.get_file_from_repo("https://github.com/octocat/Hello-World", "README", branch="master")
    assert "Hello World" in readme # nosec