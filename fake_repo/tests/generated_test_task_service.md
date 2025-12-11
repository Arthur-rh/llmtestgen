## Test 001: Creating a task with a valid non-empty title succeeds
**Requirement:** Task creation with validation

### Preconditions
- TaskService is initialized

### Target code elements
- `TaskService.create_task`

### Steps
1. Call `create_task("Valid title")`.

### Expected Result
- A task is created with:
  - Title `"Valid title"`
  - ID > 0
  - `completed == False`
  - `created_at` set
  - `completed_at == None`

---

## Test 002: Creating a task with an empty title raises an error
**Requirement:** Title validation

### Preconditions
- TaskService is initialized

### Target code elements
- `TaskService.create_task`

### Steps
1. Call `create_task("")`.

### Expected Result
- `ValueError` is raised.

---

## Test 003: Creating a task with whitespace-only title raises an error
**Requirement:** Title validation

### Preconditions
- TaskService is initialized

### Target code elements
- `TaskService.create_task`

### Steps
1. Call `create_task("   ")`.

### Expected Result
- `ValueError` is raised.

---

## Test 004: Consecutive task creations receive incremental IDs
**Requirement:** Unique ID assignment

### Preconditions
- TaskService is initialized

### Target code elements
- `TaskService.create_task`

### Steps
1. Create task A using `create_task("First")`.  
2. Create task B using `create_task("Second")`.

### Expected Result
- Task B's ID = Task A's ID + 1.

---

## Test 005: Retrieving an existing task by ID returns the correct task
**Requirement:** Task retrieval

### Preconditions
- TaskService contains at least one task

### Target code elements
- `TaskService.get_task`

### Steps
1. Call `get_task(<valid_id>)`.

### Expected Result
- The correct task object is returned.

---

## Test 006: Retrieving a non-existing task raises TaskNotFoundError
**Requirement:** Error handling

### Preconditions
- TaskService is initialized

### Target code elements
- `TaskService.get_task`

### Steps
1. Call `get_task(999)`.

### Expected Result
- `TaskNotFoundError` is raised.

---

## Test 007: First completion sets the completion timestamp
**Requirement:** Task completion

### Preconditions
- TaskService contains an uncompleted task

### Target code elements
- `TaskService.complete_task`

### Steps
1. Call `complete_task(<valid_task_id>)`.

### Expected Result
- Task is marked completed:
  - `completed == True`
  - `completed_at` timestamp is set to the current time

---

## Test 008: Completing an already completed task does not change the timestamp
**Requirement:** Idempotent completion

### Preconditions
- TaskService contains a completed task

### Target code elements
- `TaskService.complete_task`

### Steps
1. Store the original `completed_at` timestamp.  
2. Call `complete_task(<same_id>)` again.  
3. Compare timestamps.

### Expected Result
- The completion timestamp remains unchanged.

---

## Test 009: Deleting an existing task removes it from the service
**Requirement:** Task deletion

### Preconditions
- TaskService contains at least one task

### Target code elements
- `TaskService.delete_task`
- `TaskService.list_tasks`

### Steps
1. Store the task ID.  
2. Call `delete_task(<valid_id>)`.  
3. Call `list_tasks()`.

### Expected Result
- The deleted task no longer appears in the task list.

---

## Test 010: Deleting a non-existing task raises TaskNotFoundError
**Requirement:** Error handling

### Preconditions
- TaskService is initialized

### Target code elements
- `TaskService.delete_task`

### Steps
1. Call `delete_task(999)`.

### Expected Result
- `TaskNotFoundError` is raised.

---

## Test 011: Listing tasks returns all created tasks
**Requirement:** Task listing

### Preconditions
- TaskService contains multiple tasks

### Target code elements
- `TaskService.list_tasks`

### Steps
1. Call `list_tasks()`.

### Expected Result
- The returned list contains all created tasks.

---
