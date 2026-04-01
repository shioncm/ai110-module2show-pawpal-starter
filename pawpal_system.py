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

import datetime
from typing import List, Optional, Union


# ── Task ──────────────────────────────────────────────────────────────────────


class Task:
    """Represents a single pet-care activity.

    Attributes:
        title (str): Human-readable label for the activity
            (e.g. "Morning walk", "Feed", "Groom").
        duration_minutes (int): How long the task takes in minutes.
        priority (str): Urgency level.  Must be one of "low", "medium",
            or "high".
        is_completed (bool): Completion flag.  Defaults to False.
    """

    VALID_PRIORITIES = {"low", "medium", "high"}
    VALID_FREQUENCIES = {"daily", "weekly"}

    def __init__(
        self,
        title: str,
        duration_minutes: int,
        priority: str = "medium",
        is_completed: bool = False,
        scheduled_time: Optional[int] = None,
        frequency: Optional[str] = None,
        due_date: Optional[datetime.date] = None,
    ) -> None:
        """Initialise a Task.

        Args:
            title: What the task involves.
            duration_minutes: How long the task takes (must be > 0).
            priority: Urgency level ("low", "medium", or "high").
                Defaults to "medium".
            is_completed: Initial completion state.  Defaults to False.
            scheduled_time: When the task is scheduled, expressed as minutes
                from midnight (0–1439, e.g. 480 = 08:00).  None means
                unscheduled.  Defaults to None.
            frequency: Recurrence cadence.  Must be None, "daily", or
                "weekly".  When set, completing the task via
                Scheduler.complete_task() automatically adds the next
                occurrence to the same pet.  Defaults to None.
            due_date: The calendar date this occurrence is due.  Defaults
                to today when frequency is set and no date is provided;
                otherwise None.

        Raises:
            ValueError: If title is empty, duration_minutes <= 0,
                priority is not recognised, scheduled_time is outside
                0–1439, or frequency is not a recognised value.
            TypeError: If duration_minutes or scheduled_time are the wrong
                type.
        """
        if not title or not title.strip():
            raise ValueError("title must be a non-empty string.")
        if not isinstance(duration_minutes, int):
            raise TypeError("duration_minutes must be an int.")
        if duration_minutes <= 0:
            raise ValueError("duration_minutes must be > 0.")
        if priority not in self.VALID_PRIORITIES:
            raise ValueError(
                f"priority must be one of {self.VALID_PRIORITIES}, got '{priority}'."
            )
        if scheduled_time is not None:
            if not isinstance(scheduled_time, int):
                raise TypeError("scheduled_time must be an int (minutes from midnight).")
            if not (0 <= scheduled_time <= 1439):
                raise ValueError("scheduled_time must be between 0 and 1439.")
        if frequency is not None and frequency not in self.VALID_FREQUENCIES:
            raise ValueError(
                f"frequency must be one of {self.VALID_FREQUENCIES}, got '{frequency}'."
            )
        if due_date is not None and not isinstance(due_date, datetime.date):
            raise TypeError("due_date must be a datetime.date instance.")

        self._title: str = title.strip()
        self._duration_minutes: int = duration_minutes
        self._priority: str = priority.strip().lower()
        self._is_completed: bool = bool(is_completed)
        self._scheduled_time: Optional[int] = scheduled_time
        self._frequency: Optional[str] = frequency
        # Default due_date to today when a frequency is given
        self._due_date: Optional[datetime.date] = (
            due_date if due_date is not None else (datetime.date.today() if frequency else None)
        )

    # ── Properties ────────────────────────────────────────────────────────────

    @property
    def title(self) -> str:
        """str: What the task involves."""
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        if not value or not value.strip():
            raise ValueError("title must be a non-empty string.")
        self._title = value.strip()

    @property
    def duration_minutes(self) -> int:
        """int: How long the task takes in minutes."""
        return self._duration_minutes

    @duration_minutes.setter
    def duration_minutes(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError("duration_minutes must be an int.")
        if value <= 0:
            raise ValueError("duration_minutes must be > 0.")
        self._duration_minutes = value

    @property
    def priority(self) -> str:
        """str: Urgency level of the task."""
        return self._priority

    @priority.setter
    def priority(self, value: str) -> None:
        if value not in self.VALID_PRIORITIES:
            raise ValueError(
                f"priority must be one of {self.VALID_PRIORITIES}, got '{value}'."
            )
        self._priority = value.strip().lower()

    @property
    def is_completed(self) -> bool:
        """bool: Whether the task has been completed."""
        return self._is_completed

    @property
    def scheduled_time(self) -> Optional[int]:
        """int | None: Scheduled start time as minutes from midnight (0–1439),
        or None if the task has no assigned time."""
        return self._scheduled_time

    @scheduled_time.setter
    def scheduled_time(self, value: Optional[int]) -> None:
        if value is not None:
            if not isinstance(value, int):
                raise TypeError("scheduled_time must be an int (minutes from midnight).")
            if not (0 <= value <= 1439):
                raise ValueError("scheduled_time must be between 0 and 1439.")
        self._scheduled_time = value

    def scheduled_time_str(self) -> str:
        """Return scheduled_time as an 'HH:MM' string, or 'unscheduled'."""
        if self._scheduled_time is None:
            return "unscheduled"
        return f"{self._scheduled_time // 60:02d}:{self._scheduled_time % 60:02d}"

    @property
    def frequency(self) -> Optional[str]:
        """str | None: Recurrence cadence — 'daily', 'weekly', or None."""
        return self._frequency

    @property
    def due_date(self) -> Optional[datetime.date]:
        """datetime.date | None: The calendar date this occurrence is due."""
        return self._due_date

    @due_date.setter
    def due_date(self, value: Optional[datetime.date]) -> None:
        if value is not None and not isinstance(value, datetime.date):
            raise TypeError("due_date must be a datetime.date instance.")
        self._due_date = value

    def next_occurrence(self) -> "Task":
        """Return a new pending Task for the next recurrence.

        The new task is identical to this one except:
        - is_completed is False
        - due_date is advanced by 1 day (daily) or 7 days (weekly)

        Returns:
            Task: The next occurrence, ready to be added to a pet.

        Raises:
            ValueError: If this task has no frequency set.
        """
        if self._frequency is None:
            raise ValueError(
                f"Task '{self._title}' has no frequency set; cannot generate next occurrence."
            )
        base = self._due_date or datetime.date.today()
        delta = datetime.timedelta(days=1 if self._frequency == "daily" else 7)
        return Task(
            title=self._title,
            duration_minutes=self._duration_minutes,
            priority=self._priority,
            scheduled_time=self._scheduled_time,
            frequency=self._frequency,
            due_date=base + delta,
        )

    # ── State Mutations ───────────────────────────────────────────────────────

    def complete(self) -> None:
        """Mark this task as completed.

        Idempotent — calling it on an already-completed task is a no-op.
        """
        self._is_completed = True

    def reset(self) -> None:
        """Reset completion status back to incomplete.

        Idempotent.
        """
        self._is_completed = False

    # ── Helpers ───────────────────────────────────────────────────────────────

    def is_high_priority(self) -> bool:
        """Return True if this task's priority is 'high'.

        Returns:
            bool: True when priority == "high".
        """
        return self._priority == "high"

    # ── Dunder Methods ────────────────────────────────────────────────────────

    def __str__(self) -> str:
        status = "done" if self._is_completed else "pending"
        return (
            f"Task('{self._title}', {self._duration_minutes} min, "
            f"priority={self._priority}, {status})"
        )

    def __repr__(self) -> str:
        return (
            f"Task(title={self._title!r}, "
            f"duration_minutes={self._duration_minutes!r}, "
            f"priority={self._priority!r}, "
            f"is_completed={self._is_completed!r})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Task):
            return NotImplemented
        return (
            self._title == other._title
            and self._duration_minutes == other._duration_minutes
            and self._priority == other._priority
            and self._due_date == other._due_date
        )

    def __hash__(self) -> int:
        return hash((self._title, self._duration_minutes, self._priority, self._due_date))


# ── Pet ───────────────────────────────────────────────────────────────────────


class Pet:
    """Stores pet details and manages a list of associated Tasks.

    Attributes:
        name (str): The pet's name.
        species (str): Type of animal (e.g. "dog", "cat").
        age (int | float): The pet's age in years.  Defaults to 0.
        tasks (list[Task]): Tasks assigned to this pet.
    """

    def __init__(
        self,
        name: str,
        species: str,
        age: Union[int, float] = 0,
    ) -> None:
        """Initialise a Pet.

        Args:
            name: The pet's name.
            species: The type of animal.
            age: The pet's age in years (must be >= 0).  Defaults to 0.

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
                f"Task '{task.title}' is already registered for {self._name}."
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
                f"Task '{task.title}' not found for pet '{self._name}'."
            )

    def remove_task_by_title(self, title: str) -> None:
        """Remove the first task whose title matches (case-insensitive).

        Args:
            title: The title to search for.

        Raises:
            ValueError: If no matching task is found.
        """
        target = title.strip().lower()
        for task in self._tasks:
            if task.title.lower() == target:
                self._tasks.remove(task)
                return
        raise ValueError(
            f"No task with title '{title}' found for pet '{self._name}'."
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
        if pet in self._pets:
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
        return [t for pet in self._pets for t in pet.tasks]

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
        if owner in self._owners:
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
        return [t for owner in self._owners for t in owner.get_all_tasks()]

    def get_tasks_by_priority(self, priority: str) -> List[Task]:
        """Filter all system tasks by priority level.

        Args:
            priority: The priority string to match ("low", "medium", "high").

        Returns:
            list[Task]: Tasks whose priority matches the given value.

        Raises:
            ValueError: If priority is not a recognised value.
        """
        if priority not in Task.VALID_PRIORITIES:
            raise ValueError(
                f"priority must be one of {Task.VALID_PRIORITIES}, got '{priority}'."
            )
        return [t for t in self.get_all_tasks() if t.priority == priority]

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

    def sort_tasks_by_time(self, include_unscheduled: bool = True) -> List[Task]:
        """Return all system tasks sorted by their scheduled_time.

        Tasks with a scheduled_time come first, ordered earliest to latest.
        Tasks with no scheduled_time (None) are appended at the end when
        include_unscheduled is True, or omitted when False.

        Args:
            include_unscheduled: When True (default), tasks without a
                scheduled_time are included at the end of the list.
                When False, only tasks with an explicit scheduled_time
                are returned.

        Returns:
            list[Task]: Tasks sorted by scheduled_time ascending.
        """
        all_tasks = self.get_all_tasks()
        if not include_unscheduled:
            all_tasks = [t for t in all_tasks if t.scheduled_time is not None]
        # Tuple key: (is_unscheduled, time) — False sorts before True, so
        # scheduled tasks come first; unscheduled tasks sort among themselves
        # by title (second element) to keep output stable.
        return sorted(
            all_tasks,
            key=lambda t: (t.scheduled_time is None, t.scheduled_time or 0),
        )

    def filter_tasks(
        self,
        *,
        is_completed: Optional[bool] = None,
        pet_name: Optional[str] = None,
    ) -> List[Task]:
        """Return tasks filtered by completion status and/or pet name.

        Both filters are optional and can be combined.  Passing neither
        returns all tasks (equivalent to get_all_tasks()).

        Args:
            is_completed: When True, return only completed tasks.  When
                False, return only pending tasks.  When None (default),
                completion status is not filtered.
            pet_name: When provided, return only tasks belonging to the
                pet with this name (case-insensitive).  When None
                (default), tasks from all pets are included.

        Returns:
            list[Task]: Tasks matching every supplied filter criterion.

        Raises:
            ValueError: If pet_name is provided but no pet with that name
                exists in the system.

        Examples:
            # All pending tasks for any pet
            scheduler.filter_tasks(is_completed=False)

            # All tasks (done or not) for "Mochi"
            scheduler.filter_tasks(pet_name="Mochi")

            # Only completed tasks for "Mochi"
            scheduler.filter_tasks(is_completed=True, pet_name="Mochi")
        """
        if pet_name is not None:
            target = pet_name.strip().lower()
            pet = None
            for owner in self._owners:
                pet = owner.get_pet_by_name(target)
                if pet is not None:
                    break
            if pet is None:
                raise ValueError(
                    f"No pet named '{pet_name}' found in the system."
                )
            tasks = pet.tasks
        else:
            tasks = self.get_all_tasks()

        if is_completed is not None:
            tasks = [t for t in tasks if t.is_completed == is_completed]

        return tasks

    def get_tasks_for_pet(self, pet_name: str) -> List[Task]:
        """Return all tasks assigned to a specific pet (searched by name).

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

    def complete_task(self, task: Task) -> Optional[Task]:
        """Mark a specific Task as complete.

        If the task has a frequency of "daily" or "weekly", a new Task is
        automatically created for the next occurrence and added to the same
        pet.

        Args:
            task: The Task object to complete.

        Returns:
            Task | None: The newly created next-occurrence Task if the task
                is recurring, otherwise None.

        Raises:
            TypeError: If task is not a Task instance.
            ValueError: If the task does not belong to any registered pet.
        """
        if not isinstance(task, Task):
            raise TypeError("task must be a Task instance.")

        # Find the pet that owns this task (identity check, not equality)
        owner_pet = next(
            (pet for owner in self._owners for pet in owner.pets if any(t is task for t in pet.tasks)),
            None,
        )
        if owner_pet is None:
            raise ValueError("The given task is not tracked by this Scheduler.")

        task.complete()

        if task.frequency is not None:
            next_task = task.next_occurrence()
            owner_pet.add_task(next_task)
            return next_task

        return None

    # ── Conflict Detection ────────────────────────────────────────────────────

    def check_conflicts(self) -> List[str]:
        """Detect scheduling conflicts across all pets and owners.

        A conflict occurs when two tasks have a scheduled_time and their
        time windows overlap:
            task_a.scheduled_time < task_b.scheduled_time + task_b.duration_minutes
            AND
            task_b.scheduled_time < task_a.scheduled_time + task_a.duration_minutes

        Only pending (incomplete) tasks with a scheduled_time are considered.
        The method never raises — it always returns a (possibly empty) list of
        human-readable warning strings so the caller can decide how to surface
        them.

        Returns:
            list[str]: One warning string per conflicting pair, in the order
                the pairs are encountered.  An empty list means no conflicts.

        Example warning:
            "CONFLICT: 'Park Walk' for Biscuit (08:00–08:30) overlaps with
             'Vet Checkup' for Luna (08:15–09:15)"
        """
        # Collect (task, pet_name) for every scheduled, pending task
        candidates: List[tuple[Task, str]] = []
        for owner in self._owners:
            for pet in owner.pets:
                for task in pet.tasks:
                    if task.scheduled_time is not None and not task.is_completed:
                        candidates.append((task, pet.name))

        warnings: List[str] = []
        for i in range(len(candidates)):
            task_a, pet_a = candidates[i]
            for j in range(i + 1, len(candidates)):
                task_b, pet_b = candidates[j]
                a_start = task_a.scheduled_time  # type: ignore[assignment]
                a_end   = a_start + task_a.duration_minutes
                b_start = task_b.scheduled_time  # type: ignore[assignment]
                b_end   = b_start + task_b.duration_minutes
                if a_start < b_end and b_start < a_end:
                    warnings.append(
                        f"CONFLICT: '{task_a.title}' for {pet_a} "
                        f"({task_a.scheduled_time_str()}–"
                        f"{a_end // 60:02d}:{a_end % 60:02d}) overlaps with "
                        f"'{task_b.title}' for {pet_b} "
                        f"({task_b.scheduled_time_str()}–"
                        f"{b_end // 60:02d}:{b_end % 60:02d})"
                    )
        return warnings

    # ── Summary / Reporting ───────────────────────────────────────────────────

    def summary(self) -> str:
        """Build and return a human-readable summary of the entire system.

        Returns:
            str: Multi-line formatted summary string.
        """
        if not self._owners:
            return "Scheduler: no owners registered."

        lines: List[str] = ["=== PawPal Scheduler Summary ==="]
        all_tasks = self.get_all_tasks()
        total_tasks = len(all_tasks)
        total_pending = sum(1 for t in all_tasks if not t.is_completed)
        total_done = total_tasks - total_pending
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
                        f"    {status_icon} {task.title} "
                        f"({task.duration_minutes} min, {task.priority} priority)"
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
