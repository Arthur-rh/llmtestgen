"""Git repository helpers built on top of GitPython."""
from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
from typing import Optional

from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError, NoSuchPathError


class GitRepositoryError(RuntimeError):
    """Raised when interacting with a Git repository fails."""


class GitRepository:
    """Wrapper that opens a repo (local or remote) and exposes file helpers."""

    def __init__(
        self,
        source: str,
        *,
        branch: Optional[str] = None,
        ref: Optional[str] = None,
    ) -> None:
        if Repo is None:
            raise GitRepositoryError(
                "GitPython is required for GitRepository. Ensure 'gitpython' is installed."
            )
        if branch and ref:
            raise ValueError("Provide either branch or ref, not both.")

        self.source = source
        self.branch = branch
        self.ref = ref

        self._tempdir: Optional[Path] = None
        self._repo: Optional[Repo] = None
        self._path: Optional[Path] = None

    @property
    def path(self) -> Path:
        if self._path is None:
            raise GitRepositoryError("Repository not initialized. Call open() first.")
        return self._path

    @property
    def repo(self) -> Repo:
        if self._repo is None:
            raise GitRepositoryError("Repository not initialized. Call open() first.")
        return self._repo

    def open(self) -> Optional[Repo]:
        """Open or clone the repository and checkout the requested ref.

        This supports both Git repositories and plain directories so the helpers can
        operate on simple file trees without requiring `git init`.
        """

        if self._repo is not None or self._path is not None:
            return self._repo

        local_path = Path(self.source)
        try:
            if local_path.exists():
                self._path = local_path
                try:
                    self._repo = Repo(local_path)
                except InvalidGitRepositoryError:
                    # Treat regular directories as read-only sources without Git.
                    self._repo = None
            else:
                tempdir = Path(tempfile.mkdtemp(prefix="llmtestgen-repo-"))
                self._tempdir = tempdir
                self._repo = Repo.clone_from(self.source, tempdir)
                self._path = tempdir
        except (GitCommandError, NoSuchPathError) as exc:
            raise GitRepositoryError(f"Unable to open repository '{self.source}': {exc}") from exc

        if self._repo is None:
            if self.branch or self.ref:
                raise GitRepositoryError(
                    "Cannot checkout a branch/ref for a non-git directory source."
                )
            return None

        try:
            if self.branch:
                self.repo.git.checkout(self.branch)
            elif self.ref:
                self.repo.git.checkout(self.ref)
        except GitCommandError as exc:
            self.close()
            raise GitRepositoryError(
                f"Unable to checkout ref '{self.branch or self.ref}' in '{self.source}': {exc}"
            ) from exc

        return self.repo

    def close(self) -> None:
        """Clean up any temporary clone created for this repository."""

        if self._tempdir and self._tempdir.exists():
            shutil.rmtree(self._tempdir, ignore_errors=True)
        self._tempdir = None
        self._path = None
        self._repo = None

    def __enter__(self) -> "GitRepository":
        self.open()
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()

    def get_file_contents(self, file_path: str, encoding: str = "utf-8") -> str:
        """Return the content of `file_path` from the repository."""

        self.open()
        target = self.path / file_path
        if not target.is_file():
            raise GitRepositoryError(f"File '{file_path}' not found in repository '{self.path}'.")
        return target.read_text(encoding=encoding)

    def list_files(self) -> list[str]:
        """Return relative paths to all files tracked in the working tree."""

        self.open()
        files: list[str] = []
        for path in self.path.rglob("*"):
            if path.is_file():
                files.append(str(path.relative_to(self.path)))
        return files


def get_file_from_repo(
    repo_source: str,
    file_path: str,
    *,
    branch: Optional[str] = None,
    ref: Optional[str] = None,
    encoding: str = "utf-8",
) -> str:
    """Convenience helper to fetch file content from a repo in a single call."""

    with GitRepository(repo_source, branch=branch, ref=ref) as repo:
        return repo.get_file_contents(file_path, encoding=encoding)


def list_repo_files(
    repo_source: str,
    *,
    branch: Optional[str] = None,
    ref: Optional[str] = None,
) -> list[str]:
    """Convenience helper to list files for a repository without manual class usage."""

    with GitRepository(repo_source, branch=branch, ref=ref) as repo:
        return repo.list_files()
