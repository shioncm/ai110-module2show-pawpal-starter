"""
pawpal_system.py
================
Core domain classes for the PawPal pet-care scheduling system.

Class hierarchy
---------------
Task      — a single pet activity (feed, walk, groom, etc.)
Pet       — a pet that owns a collection of Tasks
Owner     — a person who owns one or more Pets
Scheduler — system-wide coordinator that aggregates tasks across all Owners

Design decisions
----------------
* Task is a plain class (not a dataclass) so that property validation and
  richer dunder methods can be added without fighting dataclass machinery.
* Relationships are composition: Owner holds Pet objects, Scheduler holds
  Owner objects.  No inheritance is used because the entities are unrelated
  domain concepts.
* All mutating helpers raise ValueError on bad input so callers get
  actionable error messages instead of silent no-ops.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Union


# ── Task ──────────────────────────────────────────────────────────────────────


class Task:
    """Represents a single pet-care activity.

    Attributes:
        description (str): Human-readable label for the activity
            (e.g. "Feed", "Walk", "Groom").
        time (str | datetime): When the task should occur.  Accepts either a
            formatted string (e.g. "08:00") or a full datetime object.
        frequency (str): Recurrence cadence.  Conventional values are
            "once", "daily", "weekly", and "monthly", but the field is
            freeform.
        is_completed (bool): Completion flag.  Defaults to False.
    """

    # Recognised frequency tokens used for validation in Scheduler helpers.
    VALID_FREQUENCIES = {"once", "daily", "weekly", "monthly"}

    def __init__(
        self,
        description: str,
        time: Union[str, datetime],
        frequency: str = "once",
        is_completed: bool = False,
    ) -> None:
        """Initialise a Task.

        Args:
            description: What the task involves.
            time: When the task should occur (string or datetime).
            frequency: How often the task recurs.  Defaults to "once".
            is_completed: Initial completion state.  Defaults to False.

        Raises:
            ValueError: If description is empty or frequency is an empty
                string.
            TypeError: If time is not a str or datetime instance.
        """
        if not description or not description.strip():
            raise ValueError("description must be a non-empty string.")
        if not isinstance(time, (str, datetime)):
            raise TypeError("time must be a str or datetime instance.")
        if frequency == "":
            raise ValueError("frequency must be a non-empty string.")

        self._description: str = description.strip()
        self._time: Union[str, datetime] = time
        self._frequency: str = frequency.strip().lower()
        self._is_completed: bool = bool(is_completed)

    # ── Properties ────────────────────────────────────────────────────────────

    @property
    def description(self) -> str:
        """str: What the task involves."""
        return self._description

    @description.setter
    def description(self, value: str) -> None:
        if not value or not value.strip():
            raise ValueError("description must be a non-empty string.")
        self._description = value.strip()

    @property
    def time(self) -> Union[str, datetime]:
        """str | datetime: When the task should occur."""
        return self._time

    @time.setter
    def time(self, value: Union[str, datetime]) -> None:
        if not isinstance(value, (str, datetime)):
            raise TypeError("time must be a str or datetime instance.")
        self._time = value

    @property
    def frequency(self) -> str:
        """str: How often the task recurs."""
        return self._frequency

    @frequency.setter
    def frequency(self, value: str) -> None:
        if value == "":
            raise ValueError("frequency must be a non-empty string.")
        self._frequency = value.strip().lower()

    @property
    def is_completed(self) -> bool:
        """bool: Whether the task has been completed."""
        return self._is_completed

    # ── State Mutations ───────────────────────────────────────────────────────

    def complete(self) -> None:
        """Mark this task as completed.

        Idempotent — calling it on an already-completed task is a no-op.
        """
        self._is_completed = True

    def reset(self) -> None:
        """Reset completion status back to incomplete.

        Intended for recurring tasks that need to be re-scheduled after each
        cycle.  Idempotent.
        """
        self._is_completed = False

    # ── Helpers ───────────────────────────────────────────────────────────────

    def is_recurring(self) -> bool:
        """Return True if this task repeats (i.e. frequency is not 'once').

        Returns:
            bool: True when frequency != "once".
        """
        return self._frequency != "once"

    def time_display(self) -> str:
        """Return a consistently formatted string representation of the time.

        Returns:
            str: ISO-format string if time is a datetime; the raw string
                otherwise.
        """
        if isinstance(self._time, datetime):
            return self._time.strftime("%Y-%m-%d %H:%M")
        return str(self._time)

    # ── Dunder Methods ────────────────────────────────────────────────────────

    def __str__(self) -> str:
        status = "done" if self._is_completed else "pending"
        return (
            f"Task('{self._description}' at {self.time_display()}, "
            f"{self._frequency}, {status})"
        )

    def __repr__(self) -> str:
        return (
            f"Task(description={self._description!r}, "
            f"time={self._time!r}, "
            f"frequency={self._frequency!r}, "
            f"is_completed={self._is_completed!r})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Task):
            return NotImplemented
        return (
            self._description == other._description
            and self._time == other._time
            and self._frequency == other._frequency
        )

    def __hash__(self) -> int:
        return hash((self._description, str(self._time), self._frequency))


# ── Pet ───────────────────────────────────────────────────────────────────────


class Pet:
    """Stores pet details and manages a list of associated Tasks.

    Attributes:
        name (str): The pet's name.
        species (str): Type of animal (e.g. "Dog", "Cat").
        age (int | float): The pet's age in years.
        tasks (list[Task]): Tasks assigned to this pet.
    """

    def __init__(
        self,
        name: str,
        species: str,
        age: Union[int, float],
    ) -> None:
        """Initialise a Pet.

        Args:
            name: The pet's name.
            species: The type of animal.
            age: The pet's age in years (must be >= 0).

        Raises:
            ValueError: If name or species is empty, or age is negative.
            TypeError: If age is not numeric.
        """
        if not name or not name.strip():
            raise ValueError("name must be a non-empty string.")
        if not species or not species.strip():
            raise ValueError("species must be a non-empty string.")
        if not isinstance(age, (int, float)):
            raise TypeError("age must be a numeric value.")
        if age < 0:
            raise ValueError("age must be >= 0.")

        self._name: str = name.strip()
        self._species: str = species.strip()
        self._age: Union[int, float] = age
        self._tasks: List[Task] = []

    # ── Properties ────────────────────────────────────────────────────────────

    @property
    def name(self) -> str:
        """str: The pet's name."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not value or not value.strip():
            raise ValueError("name must be a non-empty string.")
        self._name = value.strip()

    @property
    def species(self) -> str:
        """str: The type of animal."""
        return self._species

    @species.setter
    def species(self, value: str) -> None:
        if not value or not value.strip():
            raise ValueError("species must be a non-empty string.")
        self._species = value.strip()

    @property
    def age(self) -> Union[int, float]:
        """int | float: The pet's age in years."""
        return self._age

    @age.setter
    def age(self, value: Union[int, float]) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("age must be a numeric value.")
        if value < 0:
            raise ValueError("age must be >= 0.")
        self._age = value

    @property
    def tasks(self) -> List[Task]:
        """list[Task]: A shallow copy of the task list (read-only view)."""
        return list(self._tasks)

    # ── Task Management ───────────────────────────────────────────────────────

    def add_task(self, task: Task) -> None:
        """Add a Task to this pet's task list.

        Args:
            task: The Task to add.

        Raises:
            TypeError: If task is not a Task instance.
            ValueError: If the identical task object is already registered.
        """
        if not isinstance(task, Task):
            raise TypeError("task must be a Task instance.")
        if task in self._tasks:
            raise ValueError(
                f"Task '{task.description}' is already registered for {self._name}."
            )
        self._tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a Task from this pet's task list.

        Args:
            task: The Task object to remove.

        Raises:
            TypeError: If task is not a Task instance.
            ValueError: If the task is not found in the list.
        """
        if not isinstance(task, Task):
            raise TypeError("task must be a Task instance.")
        try:
            self._tasks.remove(task)
        except ValueError:
            raise ValueError(
                f"Task '{task.description}' not found for pet '{self._name}'."
            )

    def remove_task_by_description(self, description: str) -> None:
        """Remove the first task whose description matches (case-insensitive).

        Args:
            description: The description to search for.

        Raises:
            ValueError: If no matching task is found.
        """
        target = description.strip().lower()
        for task in self._tasks:
            if task.description.lower() == target:
                self._tasks.remove(task)
                return
        raise ValueError(
            f"No task with description '{description}' found for pet '{self._name}'."
        )

    def get_pending_tasks(self) -> List[Task]:
        """Return all tasks that have not yet been completed.

        Returns:
            list[Task]: Incomplete tasks in insertion order.
        """
        return [t for t in self._tasks if not t.is_completed]

    def get_completed_tasks(self) -> List[Task]:
        """Return all tasks that have been completed.

        Returns:
            list[Task]: Completed tasks in insertion order.
        """
        return [t for t in self._tasks if t.is_completed]

    # ── Dunder Methods ────────────────────────────────────────────────────────

    def __str__(self) -> str:
        pending = len(self.get_pending_tasks())
        return (
            f"Pet('{self._name}', {self._species}, age={self._age}, "
            f"tasks={len(self._tasks)} [{pending} pending])"
        )

    def __repr__(self) -> str:
        return (
            f"Pet(name={self._name!r}, species={self._species!r}, "
            f"age={self._age!r}, tasks={self._tasks!r})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Pet):
            return NotImplemented
        return self._name.lower() == other._name.lower()

    def __hash__(self) -> int:
        return hash(self._name.lower())


# ── Owner ─────────────────────────────────────────────────────────────────────


class Owner:
    """Manages multiple Pets and provides aggregated access to all their Tasks.

    Attributes:
        name (str): The owner's full name.
        contact (str): Contact information (email address or phone number).
        pets (list[Pet]): The pets registered under this owner.
    """

    def __init__(self, name: str, contact: str = "") -> None:
        """Initialise an Owner.

        Args:
            name: The owner's full name.
            contact: Email or phone contact info.  Defaults to empty string.

        Raises:
            ValueError: If name is empty.
        """
        if not name or not name.strip():
            raise ValueError("name must be a non-empty string.")

        self._name: str = name.strip()
        self._contact: str = contact.strip()
        self._pets: List[Pet] = []

    # ── Properties ────────────────────────────────────────────────────────────

    @property
    def name(self) -> str:
        """str: The owner's full name."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not value or not value.strip():
            raise ValueError("name must be a non-empty string.")
        self._name = value.strip()

    @property
    def contact(self) -> str:
        """str: The owner's contact information."""
        return self._contact

    @contact.setter
    def contact(self, value: str) -> None:
        self._contact = value.strip() if value else ""

    @property
    def pets(self) -> List[Pet]:
        """list[Pet]: A shallow copy of the pet list (read-only view)."""
        return list(self._pets)

    # ── Pet Management ────────────────────────────────────────────────────────

    def add_pet(self, pet: Pet) -> None:
        """Register a new Pet under this owner.

        Args:
            pet: The Pet to add.

        Raises:
            TypeError: If pet is not a Pet instance.
            ValueError: If a pet with the same name is already registered.
        """
        if not isinstance(pet, Pet):
            raise TypeError("pet must be a Pet instance.")
        if any(p.name.lower() == pet.name.lower() for p in self._pets):
            raise ValueError(
                f"A pet named '{pet.name}' is already registered to {self._name}."
            )
        self._pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Unregister a Pet from this owner by reference.

        Args:
            pet: The Pet object to remove.

        Raises:
            TypeError: If pet is not a Pet instance.
            ValueError: If the pet is not found.
        """
        if not isinstance(pet, Pet):
            raise TypeError("pet must be a Pet instance.")
        try:
            self._pets.remove(pet)
        except ValueError:
            raise ValueError(
                f"Pet '{pet.name}' is not registered to owner '{self._name}'."
            )

    def remove_pet_by_name(self, name: str) -> None:
        """Unregister the first pet whose name matches (case-insensitive).

        Args:
            name: The pet name to search for.

        Raises:
            ValueError: If no pet with that name is found.
        """
        target = name.strip().lower()
        for pet in self._pets:
            if pet.name.lower() == target:
                self._pets.remove(pet)
                return
        raise ValueError(
            f"No pet named '{name}' is registered to owner '{self._name}'."
        )

    def get_pet_by_name(self, name: str) -> Optional[Pet]:
        """Find and return a Pet by name (case-insensitive).

        Args:
            name: The pet's name to look up.

        Returns:
            Pet | None: The matching Pet, or None if not found.
        """
        target = name.strip().lower()
        for pet in self._pets:
            if pet.name.lower() == target:
                return pet
        return None

    def get_all_tasks(self) -> List[Task]:
        """Return a flat list of all Tasks across every registered Pet.

        Returns:
            list[Task]: All tasks in pet-registration order.
        """
        result: List[Task] = []
        for pet in self._pets:
            result.extend(pet.tasks)
        return result

    # ── Dunder Methods ────────────────────────────────────────────────────────

    def __str__(self) -> str:
        return (
            f"Owner('{self._name}', contact='{self._contact}', "
            f"pets={len(self._pets)})"
        )

    def __repr__(self) -> str:
        return (
            f"Owner(name={self._name!r}, contact={self._contact!r}, "
            f"pets={self._pets!r})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Owner):
            return NotImplemented
        return self._name.lower() == other._name.lower()

    def __hash__(self) -> int:
        return hash(self._name.lower())


# ── Scheduler ─────────────────────────────────────────────────────────────────


class Scheduler:
    """System-wide coordinator that aggregates and manages tasks across all
    Owners and their Pets.

    The Scheduler is the single entry point for cross-cutting queries such as
    "what tasks are pending today?" or "reset all recurring tasks after a new
    day begins."

    Attributes:
        owners (list[Owner]): All registered owners in the system.
    """

    def __init__(self) -> None:
        """Initialise an empty Scheduler with no registered owners."""
        self._owners: List[Owner] = []

    # ── Properties ────────────────────────────────────────────────────────────

    @property
    def owners(self) -> List[Owner]:
        """list[Owner]: A shallow copy of the owners list (read-only view)."""
        return list(self._owners)

    # ── Owner Registration ────────────────────────────────────────────────────

    def register_owner(self, owner: Owner) -> None:
        """Add an Owner to the scheduler.

        Args:
            owner: The Owner to register.

        Raises:
            TypeError: If owner is not an Owner instance.
            ValueError: If an owner with the same name is already registered.
        """
        if not isinstance(owner, Owner):
            raise TypeError("owner must be an Owner instance.")
        if any(o.name.lower() == owner.name.lower() for o in self._owners):
            raise ValueError(
                f"An owner named '{owner.name}' is already registered."
            )
        self._owners.append(owner)

    def unregister_owner(self, owner: Owner) -> None:
        """Remove an Owner from the scheduler.

        Args:
            owner: The Owner to remove.

        Raises:
            TypeError: If owner is not an Owner instance.
            ValueError: If the owner is not found.
        """
        if not isinstance(owner, Owner):
            raise TypeError("owner must be an Owner instance.")
        try:
            self._owners.remove(owner)
        except ValueError:
            raise ValueError(f"Owner '{owner.name}' is not registered.")

    # ── Task Queries ──────────────────────────────────────────────────────────

    def get_all_tasks(self) -> List[Task]:
        """Retrieve every Task across all Owners and their Pets.

        Returns:
            list[Task]: Flat list in owner-registration / pet-registration
                order.
        """
        result: List[Task] = []
        for owner in self._owners:
            result.extend(owner.get_all_tasks())
        return result

    def get_tasks_by_frequency(self, frequency: str) -> List[Task]:
        """Filter all system tasks by their recurrence frequency.

        Args:
            frequency: The frequency string to match (case-insensitive).
                e.g. "daily", "weekly", "once".

        Returns:
            list[Task]: Tasks whose frequency matches the given value.

        Raises:
            ValueError: If frequency is an empty string.
        """
        if not frequency or not frequency.strip():
            raise ValueError("frequency must be a non-empty string.")
        target = frequency.strip().lower()
        return [t for t in self.get_all_tasks() if t.frequency == target]

    def get_pending_tasks(self) -> List[Task]:
        """Return all incomplete tasks across the entire system.

        Returns:
            list[Task]: Tasks where is_completed is False.
        """
        return [t for t in self.get_all_tasks() if not t.is_completed]

    def get_completed_tasks(self) -> List[Task]:
        """Return all completed tasks across the entire system.

        Returns:
            list[Task]: Tasks where is_completed is True.
        """
        return [t for t in self.get_all_tasks() if t.is_completed]

    def get_tasks_for_pet(self, pet_name: str) -> List[Task]:
        """Return all tasks assigned to a specific pet (searched by name).

        The search is case-insensitive and spans every registered owner.

        Args:
            pet_name: The pet's name to look up.

        Returns:
            list[Task]: All tasks for the named pet, or an empty list if the
                pet is not found.
        """
        target = pet_name.strip().lower()
        for owner in self._owners:
            pet = owner.get_pet_by_name(target)
            if pet is not None:
                return pet.tasks
        return []

    # ── Task Mutations ────────────────────────────────────────────────────────

    def complete_task(self, task: Task) -> None:
        """Mark a specific Task as complete.

        Args:
            task: The Task object to complete.

        Raises:
            TypeError: If task is not a Task instance.
            ValueError: If the task does not belong to any registered pet.
        """
        if not isinstance(task, Task):
            raise TypeError("task must be a Task instance.")
        all_tasks = self.get_all_tasks()
        if task not in all_tasks:
            raise ValueError("The given task is not tracked by this Scheduler.")
        task.complete()

    def reset_recurring_tasks(self) -> int:
        """Reset the completion status of all recurring tasks in the system.

        A task is considered recurring if its frequency is not "once".

        Returns:
            int: The number of tasks that were reset.
        """
        count = 0
        for task in self.get_all_tasks():
            if task.is_recurring() and task.is_completed:
                task.reset()
                count += 1
        return count

    # ── Summary / Reporting ───────────────────────────────────────────────────

    def summary(self) -> str:
        """Build and return a human-readable summary of the entire system.

        The summary lists every owner, each of their pets, and each pet's
        task statuses.

        Returns:
            str: Multi-line formatted summary string.
        """
        if not self._owners:
            return "Scheduler: no owners registered."

        lines: List[str] = ["=== PawPal Scheduler Summary ==="]
        total_tasks = len(self.get_all_tasks())
        total_pending = len(self.get_pending_tasks())
        total_done = len(self.get_completed_tasks())
        lines.append(
            f"Owners: {len(self._owners)}  |  "
            f"Total tasks: {total_tasks}  |  "
            f"Pending: {total_pending}  |  "
            f"Completed: {total_done}"
        )
        lines.append("")

        for owner in self._owners:
            lines.append(f"Owner: {owner.name}  (contact: {owner.contact or 'N/A'})")
            if not owner.pets:
                lines.append("  (no pets registered)")
                continue
            for pet in owner.pets:
                lines.append(
                    f"  Pet: {pet.name} ({pet.species}, age {pet.age})"
                )
                if not pet.tasks:
                    lines.append("    (no tasks)")
                    continue
                for task in pet.tasks:
                    status_icon = "[x]" if task.is_completed else "[ ]"
                    lines.append(
                        f"    {status_icon} {task.description} "
                        f"@ {task.time_display()} "
                        f"({task.frequency})"
                    )
            lines.append("")

        return "\n".join(lines).rstrip()

    # ── Dunder Methods ────────────────────────────────────────────────────────

    def __str__(self) -> str:
        return (
            f"Scheduler(owners={len(self._owners)}, "
            f"total_tasks={len(self.get_all_tasks())})"
        )

    def __repr__(self) -> str:
        return f"Scheduler(owners={self._owners!r})"

