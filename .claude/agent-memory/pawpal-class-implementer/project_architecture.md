---
name: PawPal Core Architecture
description: Key design decisions and class relationships in pawpal_system.py
type: project
---

All four core classes live in a single file: `pawpal_system.py`.

Class hierarchy (composition, no inheritance):
  Task -> Pet (Pet._tasks: List[Task])
  Pet  -> Owner (Owner._pets: List[Pet])
  Owner -> Scheduler (Scheduler._owners: List[Owner])

**Key decisions:**

- Task is a plain class (not @dataclass) to enable property validation without
  fighting dataclass machinery. Attributes are stored with a leading underscore
  and exposed via @property.
- All mutable collections (_tasks, _pets, _owners) are private; public
  properties return shallow copies to prevent external mutation.
- Task.time accepts both str and datetime (Union[str, datetime]) for flexibility.
- Task equality and hashing are based on (description, str(time), frequency),
  NOT on is_completed, so the same logical task is not duplicated in sets/dicts.
- Pet equality is case-insensitive name comparison. Same for Owner.
- Scheduler.__init__ takes no arguments; owners are registered via
  register_owner(). The old skeleton's single-pet constructor was replaced.
- Owner.get_all_tasks() flattens via list.extend over pet.tasks.
- Scheduler.get_all_tasks() flattens via owner.get_all_tasks().
- reset_recurring_tasks() returns the count of tasks reset (int), useful for
  logging/testing.
- summary() returns a str (not None); caller decides whether to print it.

**Naming conventions (snake_case throughout):**
  - Method verbs: add_*, remove_*, get_*, complete(), reset(), register_*
  - Boolean properties: is_completed, is_recurring()
  - Display helpers: time_display(), summary()

**Why:** Original skeleton used @dataclass for Task/Pet but lacked validation,
property protection, and proper dunder methods. The rewrite prioritises
defensive programming and clean encapsulation over brevity.

**How to apply:** When extending PawPal classes, keep all mutable state private
(_attr), expose via @property with validation, and return copies from
collection properties.
