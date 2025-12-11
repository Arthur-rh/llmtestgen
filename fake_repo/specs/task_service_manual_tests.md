# Manual Test Specification for Task Service

## Test Case 1: Create a task with a valid title

- Preconditions:
  - The service is empty.
- Steps:
  1. Call `create_task("Buy milk")`.
  2. Call `list_tasks()`.
- Expected result:
  - The returned list contains exactly one task.
  - The task has title "Buy milk".
  - The task has a non-null `created_at`.
  - The task has `completed == False`.
  - The task has `completed_at == None`.

## Test Case 2: Reject empty title

- Steps:
  1. Call `create_task("")`.
- Expected result:
  - A `ValueError` is raised.

## Test Case 3: Complete an existing task

- Preconditions:
  - A task exists with title "Send email".
- Steps:
  1. Call `create_task("Send email")` and store the returned ID.
  2. Call `complete_task(id)`.
- Expected result:
  - The returned task has `completed == True`.
  - The returned task has a non-null `completed_at`.

## Test Case 4: Completing a task twice

- Preconditions:
  - A task exists and is already completed.
- Steps:
  1. Call `create_task("Pay bills")` and store the ID.
  2. Call `complete_task(id)` (first time).
  3. Store the value of `completed_at`.
  4. Call `complete_task(id)` again.
- Expected result:
  - `completed` remains `True`.
  - `completed_at` is not changed (same value as before).

## Test Case 5: Get a non-existing task

- Steps:
  1. Call `get_task(9999)`.
- Expected result:
  - A `TaskNotFoundError` is raised.

## Test Case 6: Delete a non-existing task

- Steps:
  1. Call `delete_task(9999)`.
- Expected result:
  - A `TaskNotFoundError` is raised.
