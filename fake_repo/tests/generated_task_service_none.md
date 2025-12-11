## Test 001: Creating a task with a valid non-empty title succeeds
**Requirement:** Creating tasks

### Preconditions
- System has no existing tasks

### Target code elements
- `create_task`

### Steps
1. Call `create_task("Valid title")`.

### Expected Result
- A task is created with:
  - Assigned ID
  - Non-null `created_at` timestamp
  - Presence in the task list

---

## Test 002: Creating a task with an empty title raises a validation error
**Requirement:** Title validation

### Preconditions
- System has no existing tasks

### Target code elements
- `create_task`

### Steps
1. Call `create_task("")`.

### Expected Result
- A validation error is raised.

---

## Test 003: Creating a task with a whitespace-only title raises a validation error
**Requirement:** Title validation

### Preconditions
- System has no existing tasks

### Target code elements
- `create_task`

### Steps
1. Call `create_task("   ")`.

### Expected Result
- A validation error is raised.

---

## Test 004: Creating multiple tasks assigns unique IDs
**Requirement:** Unique ID assignment

### Preconditions
- System has no existing tasks

### Target code elements
- `create_task`

### Steps
1. Create a task titled `"First task"`.  
2. Create a task titled `"Second task"`.

### Expected Result
- The two tasks have different numeric IDs.

---

## Test 005: Created tasks have a non-null creation timestamp
**Requirement:** Creation timestamp

### Preconditions
- System has no existing tasks

### Target code elements
- `create_task`

### Steps
1. Create a new task.

### Expected Result
- The returned task object contains a non-null `created_at` timestamp.

---

## Test 006: Listing tasks returns all existing tasks
**Requirement:** Listing tasks

### Preconditions
- System contains multiple tasks

### Target code elements
- `list_tasks`

### Steps
1. Call `list_tasks()`.

### Expected Result
- The returned list contains all created tasks.

---

## Test 007: Retrieving a task by ID returns the correct object
**Requirement:** Task retrieval

### Preconditions
- System contains at least one task

### Target code elements
- `get_task`

### Steps
1. Call `get_task(<valid_task_id>)`.

### Expected Result
- The correct task object is returned.

---

## Test 008: Retrieving a non-existing task raises an error
**Requirement:** Task access error

### Preconditions
- System contains no tasks

### Target code elements
- `get_task`

### Steps
1. Call `get_task(<invalid_id>)`.

### Expected Result
- An error indicating “task not found” is raised.

---

## Test 009: Marking an existing task as completed updates its completion fields
**Requirement:** Task completion

### Preconditions
- System contains an uncompleted task

### Target code elements
- `mark_completed`

### Steps
1. Call `mark_completed(<valid_task_id>)`.

### Expected Result
- Task is marked completed:
  - `completed == True`
  - `completed_at` timestamp is set

---

## Test 010: Completing an already completed task preserves its timestamp
**Requirement:** Completion timestamp persistence

### Preconditions
- System contains a completed task

### Target code elements
- `mark_completed`

### Steps
1. Call `mark_completed(<already_completed_id>)`.

### Expected Result
- The `completed_at` timestamp remains unchanged.

---

## Test 011: Deleting an existing task removes it from the system
**Requirement:** Task deletion

### Preconditions
- System contains at least one task

### Target code elements
- `delete_task`

### Steps
1. Identify an existing task ID.  
2. Call `delete_task(<valid_task_id>)`.

### Expected Result
- The task no longer appears when listing tasks.

---

## Test 012: Deleting a non-existing task raises an error
**Requirement:** Deletion error

### Preconditions
- System contains no tasks

### Target code elements
- `delete_task`

### Steps
1. Call `delete_task(<invalid_id>)`.

### Expected Result
- An error indicating “task not found” is raised.

---
