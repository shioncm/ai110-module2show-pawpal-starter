# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Smarter Scheduling

The scheduling logic in `pawpal_system.py` has four "smart" features:

**Time-aware sorting**: Tasks have an optional `scheduled_time` (minutes from midnight, e.g. `480` = 08:00). `Scheduler.sort_tasks_by_time()` returns all tasks in chronological order in a single pass, with unscheduled tasks appended at the end. Pass `include_unscheduled=False` to get only timed tasks.

**Flexible filtering**: `Scheduler.filter_tasks()` accepts any combination of `is_completed` and `pet_name` as keyword arguments.

**Automatic recurrence**: Tasks support a `frequency` of `"daily"` or `"weekly"`. When `Scheduler.complete_task()` is called on a recurring task, it automatically creates the next occurrence (advancing `due_date` by 1 or 7 days) and adds it to the same pet.

**Conflict detection**: `Scheduler.check_conflicts()` scans all pending, scheduled tasks and returns a list of human-readable warning strings for any overlapping time windows. If there are no conflicts the list is empty.

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
