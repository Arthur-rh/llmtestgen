# Task Service Specification

## Overview

The Task Service is a small in-memory service that manages to-do tasks for a single user.
It must support creating tasks, listing tasks, marking tasks as completed, and deleting tasks.

## Functional Requirements

- The system must allow creating a task with a non-empty title.
- The system shall assign a unique integer ID to each new task.
- The system must store the creation timestamp for each task.
- The system must allow listing all existing tasks.
- The system must allow retrieving a task by its ID.
- The system must allow marking a task as completed.
- When a task is completed, the system must store the completion timestamp.
- The system must allow deleting a task by its ID.
- The system must raise an error when trying to access or delete a non-existing task.
- The system must not accept titles that are empty or only whitespace.

## Acceptance Criteria

- Given a valid title, when the client creates a task, then the task appears in the list of tasks.
- Given a task that exists, when the client marks it as completed, then the task's `completed` flag is set to `True` and `completed_at` is not null.
- Given a task that does not exist, when the client tries to retrieve it, then an error is raised.
- Given a task that does not exist, when the client tries to delete it, then an error is raised.
- Given an empty title, when the client tries to create a task, then a validation error is raised.

## Examples

- Example: creating two tasks with titles "Buy milk" and "Send email" should result in two tasks with different IDs.
- Example: completing the same task twice should not reset the completion timestamp.
