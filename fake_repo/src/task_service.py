from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from .models import Task


class TaskNotFoundError(Exception):
    """Raised when a task with the given ID does not exist."""


class TaskService:
    """Very small in-memory task management service."""

    def __init__(self) -> None:
        self._tasks: Dict[int, Task] = {}
        self._next_id: int = 1

    def list_tasks(self) -> List[Task]:
        """Return all tasks, unsorted."""
        return list(self._tasks.values())

    def get_task(self, task_id: int) -> Task:
        """Return a single task by ID or raise TaskNotFoundError."""
        try:
            return self._tasks[task_id]
        except KeyError:
            raise TaskNotFoundError(f"Task with id={task_id} not found")

    def create_task(self, title: str) -> Task:
        """Create a new task with the given title."""
        if not title or not title.strip():
            raise ValueError("Title must be a non-empty string")

        task = Task(
            id=self._next_id,
            title=title.strip(),
            completed=False,
            created_at=datetime.utcnow(),
            completed_at=None,
        )
        self._tasks[task.id] = task
        self._next_id += 1
        return task

    def complete_task(self, task_id: int) -> Task:
        """Mark a task as completed and set completed_at."""
        task = self.get_task(task_id)
        if not task.completed:
            task.completed = True
            task.completed_at = datetime.utcnow()
        return task

    def delete_task(self, task_id: int) -> None:
        """Delete a task. Raise TaskNotFoundError if it does not exist."""
        if task_id not in self._tasks:
            raise TaskNotFoundError(f"Task with id={task_id} not found")
        del self._tasks[task_id]
