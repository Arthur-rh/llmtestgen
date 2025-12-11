## Test 001: Creating a task with a valid title succeeds
**Requirement:** Create task with valid title

### Preconditions
- Task service initialized  
- No existing tasks  

### Target code elements
- `create_task` (src/task_service.py)

### Steps
1. Call `create_task("Valid Title")`.

### Expected Result
- A task is created with:
  - Matching title
  - Non-empty ID
  - Non-null `created_at` timestamp

---

## Test 002: Creating a task with an empty title raises validation error
**Requirement:** Empty title validation

### Preconditions
- Task service initialized

### Target code elements
- `create_task` (src/task_service.py)

### Steps
1. Call `create_task("")`.

### Expected Result
- `ValidationError` is raised.

---

## Test 003: Creating a task with whitespace-only title raises validation error
**Requirement:** Whitespace title validation

### Preconditions
- Task service initialized

### Target code elements
- `create_task` (src/task_service.py)

### Steps
1. Call `create_task("   ")`.

### Expected Result
- `ValidationError` is raised.

---

## Test 004: Listing all tasks returns all created tasks
**Requirement:** List all tasks

### Preconditions
- Task service initialized  
- Two tasks created  

### Target code elements
- `list_tasks` (src/task_service.py)

### Steps
1. Call `list_tasks()`.

### Expected Result
- The returned list contains both previously created tasks.

---

## Test 005: Retrieving a valid task returns the correct object
**Requirement:** Retrieve valid task

### Preconditions
- Task service initialized  
- One task created  

### Target code elements
- `get_task_by_id` (src/task_service.py)

### Steps
1. Call `get_task_by_id(<task_id>)`.

### Expected Result
- The correct task object is returned.

---

## Test 006: Retrieving a non-existing task raises TaskNotFoundError
**Requirement:** Retrieve invalid task

### Preconditions
- Task service initialized

### Target code elements
- `get_task_by_id` (src/task_service.py)

### Steps
1. Call `get_task_by_id(999)`.

### Expected Result
- `TaskNotFoundError` is raised.

---

## Test 007: Marking a valid task as completed updates its completion fields
**Requirement:** Mark valid task completed

### Preconditions
- Task service initialized  
- One task created  

### Target code elements
- `mark_task_completed` (src/task_service.py)

### Steps
1. Call `mark_task_completed(<task_id>)`.

### Expected Result
- `completed` flag becomes `True`  
- `completed_at` is set to a non-null timestamp

---

## Test 008: Completing an already-completed task does not modify timestamp
**Requirement:** Recomplete task

### Preconditions
- Task service initialized  
- One completed task  

### Target code elements
- `mark_task_completed` (src/task_service.py)

### Steps
1. Record the existing completion timestamp.  
2. Call `mark_task_completed(<task_id>)` again.

### Expected Result
- Task remains completed  
- Completion timestamp is unchanged

---

## Test 009: Deleting a valid task removes it from the service
**Requirement:** Delete valid task

### Preconditions
- Task service initialized  
- One task created  

### Target code elements
- `delete_task` (src/task_service.py)  
- `get_task_by_id` (src/task_service.py)

### Steps
1. Call `delete_task(<task_id>)`.  
2. Attempt to call `get_task_by_id(<task_id>)`.

### Expected Result
- `TaskNotFoundError` is raised when retrieving the deleted task.

---

## Test 010: Deleting a non-existing task raises TaskNotFoundError
**Requirement:** Delete invalid task

### Preconditions
- Task service initialized

### Target code elements
- `delete_task` (src/task_service.py)

### Steps
1. Call `delete_task(999)`.

### Expected Result
- `TaskNotFoundError` is raised.

---

## Test 011: Newly created tasks have unique IDs
**Requirement:** Task ID uniqueness

### Preconditions
- Task service initialized

### Target code elements
- `create_task` (src/task_service.py)

### Steps
1. Create task A with title `"Task 1"`.  
2. Create task B with title `"Task 2"`.

### Expected Result
- The two tasks have different numeric IDs.

---

## Test 012: Completing a task again preserves the original timestamp
**Requirement:** Completion timestamp persistence

### Preconditions
- Task service initialized  
- One completed task  

### Target code elements
- `mark_task_completed` (src/task_service.py)

### Steps
1. Record the initial `completed_at` timestamp.  
2. Call `mark_task_completed(<task_id>)` again.

### Expected Result
- The `completed_at` timestamp remains exactly the same as before.

---
