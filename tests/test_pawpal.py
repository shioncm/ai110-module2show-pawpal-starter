import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import datetime
import pytest
from pawpal_system import Task, Pet, Owner, Scheduler


def test_task_complete_changes_status():
    task = Task("Feed", duration_minutes=10, priority="high")
    assert task.is_completed is False
    task.complete()
    assert task.is_completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet("Buddy", "Dog", age=3)
    assert len(pet.tasks) == 0
    pet.add_task(Task("Walk", duration_minutes=30, priority="medium"))
    assert len(pet.tasks) == 1


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_scheduler():
    """Return a Scheduler with two owners/pets and tasks at known times."""
    walk  = Task("Walk",  duration_minutes=30, priority="high",   scheduled_time=600)  # 10:00
    feed  = Task("Feed",  duration_minutes=10, priority="high",   scheduled_time=420)  # 07:00
    groom = Task("Groom", duration_minutes=45, priority="low")                         # unscheduled

    dog = Pet("Biscuit", "Dog", age=3)
    dog.add_task(walk)
    dog.add_task(feed)
    dog.add_task(groom)

    play  = Task("Play",  duration_minutes=15, priority="medium", scheduled_time=540)  # 09:00
    cat = Pet("Luna", "Cat", age=2)
    cat.add_task(play)

    owner = Owner("Alice")
    owner.add_pet(dog)
    owner.add_pet(cat)

    scheduler = Scheduler()
    scheduler.register_owner(owner)
    return scheduler, dog, cat, walk, feed, groom, play


# ── sort_tasks_by_time tests ──────────────────────────────────────────────────

def test_sort_tasks_by_time_ascending_order():
    scheduler, *_, walk, feed, groom, play = _make_scheduler()
    result = scheduler.sort_tasks_by_time()
    scheduled = [t for t in result if t.scheduled_time is not None]
    times = [t.scheduled_time for t in scheduled]
    assert times == sorted(times), "scheduled tasks should be in ascending time order"


def test_sort_tasks_by_time_unscheduled_appended_at_end():
    scheduler, *_, groom, _ = _make_scheduler()
    result = scheduler.sort_tasks_by_time()
    # All tasks with scheduled_time come before any None
    seen_none = False
    for task in result:
        if task.scheduled_time is None:
            seen_none = True
        else:
            assert not seen_none, "a scheduled task appeared after an unscheduled one"


def test_sort_tasks_by_time_exclude_unscheduled():
    scheduler, *_ = _make_scheduler()
    result = scheduler.sort_tasks_by_time(include_unscheduled=False)
    assert all(t.scheduled_time is not None for t in result)


def test_sort_tasks_by_time_includes_all_tasks_by_default():
    scheduler, dog, cat, *_ = _make_scheduler()
    total = len(dog.tasks) + len(cat.tasks)
    assert len(scheduler.sort_tasks_by_time()) == total


def test_scheduled_time_str_formats_correctly():
    task = Task("Feed", duration_minutes=10, priority="high", scheduled_time=480)
    assert task.scheduled_time_str() == "08:00"


def test_scheduled_time_str_unscheduled():
    task = Task("Groom", duration_minutes=20, priority="low")
    assert task.scheduled_time_str() == "unscheduled"


# ── filter_tasks tests ────────────────────────────────────────────────────────

def test_filter_tasks_no_args_returns_all():
    scheduler, dog, cat, *_ = _make_scheduler()
    total = len(dog.tasks) + len(cat.tasks)
    assert len(scheduler.filter_tasks()) == total


def test_filter_tasks_pending_only():
    scheduler, _, _, walk, feed, groom, play = _make_scheduler()
    feed.complete()
    result = scheduler.filter_tasks(is_completed=False)
    assert feed not in result
    assert all(not t.is_completed for t in result)


def test_filter_tasks_completed_only():
    scheduler, _, _, walk, feed, groom, play = _make_scheduler()
    feed.complete()
    walk.complete()
    result = scheduler.filter_tasks(is_completed=True)
    assert set(result) == {feed, walk}
    assert all(t.is_completed for t in result)


def test_filter_tasks_by_pet_name():
    scheduler, dog, cat, walk, feed, groom, play = _make_scheduler()
    result = scheduler.filter_tasks(pet_name="Biscuit")
    assert set(result) == set(dog.tasks)


def test_filter_tasks_by_pet_name_case_insensitive():
    scheduler, dog, *_ = _make_scheduler()
    assert scheduler.filter_tasks(pet_name="biscuit") == scheduler.filter_tasks(pet_name="Biscuit")


def test_filter_tasks_combined_pet_name_and_completed():
    scheduler, dog, _, walk, feed, groom, play = _make_scheduler()
    feed.complete()
    result = scheduler.filter_tasks(is_completed=True, pet_name="Biscuit")
    assert result == [feed]


def test_filter_tasks_combined_pet_name_and_pending():
    scheduler, dog, _, walk, feed, groom, play = _make_scheduler()
    feed.complete()
    result = scheduler.filter_tasks(is_completed=False, pet_name="Biscuit")
    assert feed not in result
    assert all(t in dog.tasks for t in result)


def test_filter_tasks_unknown_pet_raises():
    scheduler, *_ = _make_scheduler()
    with pytest.raises(ValueError, match="No pet named"):
        scheduler.filter_tasks(pet_name="Ghost")


# ── frequency / recurrence tests ──────────────────────────────────────────────

def _make_recurring_scheduler(frequency: str):
    """One owner, one pet, one recurring task."""
    today = datetime.date.today()
    task = Task("Feed", duration_minutes=10, priority="high",
                frequency=frequency, due_date=today)
    pet = Pet("Biscuit", "Dog", age=3)
    pet.add_task(task)
    owner = Owner("Alice")
    owner.add_pet(pet)
    scheduler = Scheduler()
    scheduler.register_owner(owner)
    return scheduler, pet, task, today


def test_daily_task_due_date_defaults_to_today():
    today = datetime.date.today()
    task = Task("Feed", duration_minutes=10, priority="high", frequency="daily")
    assert task.due_date == today


def test_weekly_task_due_date_defaults_to_today():
    today = datetime.date.today()
    task = Task("Bath", duration_minutes=20, priority="low", frequency="weekly")
    assert task.due_date == today


def test_no_frequency_task_due_date_is_none():
    task = Task("Groom", duration_minutes=15, priority="low")
    assert task.due_date is None
    assert task.frequency is None


def test_next_occurrence_daily_advances_one_day():
    today = datetime.date.today()
    task = Task("Feed", duration_minutes=10, priority="high",
                frequency="daily", due_date=today)
    nxt = task.next_occurrence()
    assert nxt.due_date == today + datetime.timedelta(days=1)


def test_next_occurrence_weekly_advances_seven_days():
    today = datetime.date.today()
    task = Task("Bath", duration_minutes=20, priority="low",
                frequency="weekly", due_date=today)
    nxt = task.next_occurrence()
    assert nxt.due_date == today + datetime.timedelta(days=7)


def test_next_occurrence_inherits_task_attributes():
    task = Task("Feed", duration_minutes=10, priority="high",
                scheduled_time=420, frequency="daily")
    nxt = task.next_occurrence()
    assert nxt.title == task.title
    assert nxt.duration_minutes == task.duration_minutes
    assert nxt.priority == task.priority
    assert nxt.scheduled_time == task.scheduled_time
    assert nxt.frequency == task.frequency
    assert nxt.is_completed is False


def test_next_occurrence_raises_without_frequency():
    task = Task("Groom", duration_minutes=15, priority="low")
    with pytest.raises(ValueError, match="no frequency"):
        task.next_occurrence()


def test_complete_task_daily_adds_next_occurrence_to_pet():
    scheduler, pet, task, today = _make_recurring_scheduler("daily")
    assert len(pet.tasks) == 1
    next_task = scheduler.complete_task(task)
    assert task.is_completed is True
    assert len(pet.tasks) == 2
    assert next_task is not None
    assert next_task.due_date == today + datetime.timedelta(days=1)
    assert next_task.is_completed is False


def test_complete_task_weekly_adds_next_occurrence_to_pet():
    scheduler, pet, task, today = _make_recurring_scheduler("weekly")
    next_task = scheduler.complete_task(task)
    assert next_task is not None
    assert next_task.due_date == today + datetime.timedelta(days=7)


def test_complete_task_non_recurring_returns_none():
    task = Task("Groom", duration_minutes=15, priority="low")
    pet = Pet("Luna", "Cat", age=2)
    pet.add_task(task)
    owner = Owner("Bob")
    owner.add_pet(pet)
    scheduler = Scheduler()
    scheduler.register_owner(owner)
    result = scheduler.complete_task(task)
    assert result is None
    assert len(pet.tasks) == 1  # no new task added


def test_complete_task_chaining_daily():
    """Completing the spawned task should spawn another one."""
    scheduler, pet, task, today = _make_recurring_scheduler("daily")
    day1 = scheduler.complete_task(task)
    assert day1 is not None
    day2 = scheduler.complete_task(day1)
    assert day2 is not None
    assert day2.due_date == today + datetime.timedelta(days=2)
    assert len(pet.tasks) == 3


def test_invalid_frequency_raises():
    with pytest.raises(ValueError, match="frequency"):
        Task("Feed", duration_minutes=10, priority="high", frequency="monthly")


# ── check_conflicts tests ─────────────────────────────────────────────────────

def _sched_with_tasks(*task_pet_pairs):
    """Build a Scheduler from [(task, pet_name), ...] under a single owner."""
    owner = Owner("Alice")
    pets = {}
    for task, pet_name in task_pet_pairs:
        if pet_name not in pets:
            pets[pet_name] = Pet(pet_name, "Dog", age=1)
            owner.add_pet(pets[pet_name])
        pets[pet_name].add_task(task)
    scheduler = Scheduler()
    scheduler.register_owner(owner)
    return scheduler


def test_no_conflicts_non_overlapping():
    # 07:00–07:10 and 08:00–08:30 — gap between them
    t1 = Task("Feed",      duration_minutes=10, priority="high",   scheduled_time=420)
    t2 = Task("Park Walk", duration_minutes=30, priority="medium", scheduled_time=480)
    scheduler = _sched_with_tasks((t1, "Biscuit"), (t2, "Biscuit"))
    assert scheduler.check_conflicts() == []


def test_conflict_same_pet_overlapping():
    # 08:00–08:30 and 08:15–09:00 — 15-minute overlap
    t1 = Task("Walk",  duration_minutes=30, priority="high",   scheduled_time=480)
    t2 = Task("Groom", duration_minutes=45, priority="medium", scheduled_time=495)
    scheduler = _sched_with_tasks((t1, "Biscuit"), (t2, "Biscuit"))
    conflicts = scheduler.check_conflicts()
    assert len(conflicts) == 1
    assert "Walk" in conflicts[0]
    assert "Groom" in conflicts[0]
    assert "CONFLICT" in conflicts[0]


def test_conflict_different_pets_overlapping():
    # Dog's walk and cat's vet both at 09:00
    t1 = Task("Walk",     duration_minutes=30, priority="high",   scheduled_time=540)
    t2 = Task("Vet Visit",duration_minutes=60, priority="high",   scheduled_time=540)
    scheduler = _sched_with_tasks((t1, "Biscuit"), (t2, "Luna"))
    conflicts = scheduler.check_conflicts()
    assert len(conflicts) == 1
    assert "Biscuit" in conflicts[0]
    assert "Luna" in conflicts[0]


def test_no_conflict_adjacent_tasks():
    # 08:00–08:30 ends exactly when 08:30 starts — no overlap
    t1 = Task("Walk", duration_minutes=30, priority="high",   scheduled_time=480)
    t2 = Task("Feed", duration_minutes=10, priority="medium", scheduled_time=510)
    scheduler = _sched_with_tasks((t1, "Biscuit"), (t2, "Biscuit"))
    assert scheduler.check_conflicts() == []


def test_completed_tasks_excluded_from_conflicts():
    # Two tasks that would conflict, but the first is already done
    t1 = Task("Walk",  duration_minutes=30, priority="high",   scheduled_time=480)
    t2 = Task("Groom", duration_minutes=30, priority="medium", scheduled_time=480)
    t1.complete()
    scheduler = _sched_with_tasks((t1, "Biscuit"), (t2, "Biscuit"))
    assert scheduler.check_conflicts() == []


def test_unscheduled_tasks_excluded_from_conflicts():
    # One task has no scheduled_time — should never conflict
    t1 = Task("Walk",  duration_minutes=30, priority="high",   scheduled_time=480)
    t2 = Task("Groom", duration_minutes=30, priority="medium")  # no scheduled_time
    scheduler = _sched_with_tasks((t1, "Biscuit"), (t2, "Biscuit"))
    assert scheduler.check_conflicts() == []


def test_multiple_conflicts_reported():
    # Three overlapping tasks → 3 pairs, each a conflict
    t1 = Task("A", duration_minutes=60, priority="high",   scheduled_time=480)
    t2 = Task("B", duration_minutes=60, priority="medium", scheduled_time=510)
    t3 = Task("C", duration_minutes=60, priority="low",    scheduled_time=500)
    scheduler = _sched_with_tasks((t1, "Biscuit"), (t2, "Biscuit"), (t3, "Biscuit"))
    assert len(scheduler.check_conflicts()) == 3


def test_check_conflicts_never_raises_on_empty_scheduler():
    scheduler = Scheduler()
    assert scheduler.check_conflicts() == []


# ── edge cases ────────────────────────────────────────────────────────────────

def test_sort_filter_conflicts_pet_with_no_tasks():
    """A pet registered with zero tasks should not crash any query."""
    pet = Pet("Ghost", "Cat", age=1)
    owner = Owner("Alice")
    owner.add_pet(pet)
    scheduler = Scheduler()
    scheduler.register_owner(owner)
    assert scheduler.sort_tasks_by_time() == []
    assert scheduler.filter_tasks() == []
    assert scheduler.check_conflicts() == []


def test_sort_tasks_exclude_unscheduled_when_all_are_unscheduled():
    """include_unscheduled=False with no scheduled tasks returns empty list."""
    t1 = Task("Groom", duration_minutes=20, priority="low")
    t2 = Task("Play",  duration_minutes=15, priority="medium")
    scheduler = _sched_with_tasks((t1, "Biscuit"), (t2, "Biscuit"))
    result = scheduler.sort_tasks_by_time(include_unscheduled=False)
    assert result == []


def test_complete_task_twice_on_recurring_raises():
    """Completing a recurring task a second time should raise — the next
    occurrence with the same due_date is already registered on the pet."""
    scheduler, pet, task, today = _make_recurring_scheduler("daily")
    scheduler.complete_task(task)           # marks done, adds day+1
    assert len(pet.tasks) == 2
    with pytest.raises(ValueError):
        scheduler.complete_task(task)       # day+1 already exists → add_task raises


def test_all_tasks_completed_means_no_conflicts_and_no_pending():
    """When every scheduled task is already done, conflicts and pending are empty."""
    t1 = Task("Walk", duration_minutes=30, priority="high",   scheduled_time=480)
    t2 = Task("Feed", duration_minutes=30, priority="high",   scheduled_time=490)
    t1.complete()
    t2.complete()
    scheduler = _sched_with_tasks((t1, "Biscuit"), (t2, "Biscuit"))
    assert scheduler.check_conflicts() == []
    assert scheduler.get_pending_tasks() == []


def test_scheduled_time_str_at_boundary_values():
    """scheduled_time_str() should format midnight (0) and end-of-day (1439)."""
    assert Task("A", duration_minutes=10, priority="low", scheduled_time=0).scheduled_time_str() == "00:00"
    assert Task("B", duration_minutes=10, priority="low", scheduled_time=1439).scheduled_time_str() == "23:59"


# ── sorting correctness (chronological order) ─────────────────────────────────

def test_sort_tasks_exact_chronological_order():
    """Tasks must come back in strict ascending time order, not just 'sorted'."""
    t1 = Task("Feed",  duration_minutes=10, priority="high",   scheduled_time=420)   # 07:00
    t2 = Task("Play",  duration_minutes=15, priority="medium", scheduled_time=540)   # 09:00
    t3 = Task("Walk",  duration_minutes=30, priority="high",   scheduled_time=600)   # 10:00
    scheduler = _sched_with_tasks((t3, "Biscuit"), (t1, "Biscuit"), (t2, "Biscuit"))
    result = scheduler.sort_tasks_by_time(include_unscheduled=False)
    assert [t.scheduled_time for t in result] == [420, 540, 600]


# ── recurrence logic ──────────────────────────────────────────────────────────

def test_complete_daily_task_creates_next_day_task():
    """Completing a daily task must produce exactly one new pending task dated tomorrow."""
    scheduler, pet, task, today = _make_recurring_scheduler("daily")
    next_task = scheduler.complete_task(task)
    assert task.is_completed is True
    assert next_task is not None
    assert next_task.due_date == today + datetime.timedelta(days=1)
    assert next_task.is_completed is False
    assert len(pet.tasks) == 2


# ── conflict detection ────────────────────────────────────────────────────────

def test_conflict_tasks_at_identical_start_time():
    """Two tasks with the exact same scheduled_time always overlap."""
    t1 = Task("Feed",  duration_minutes=10, priority="high",   scheduled_time=480)
    t2 = Task("Groom", duration_minutes=30, priority="medium", scheduled_time=480)
    scheduler = _sched_with_tasks((t1, "Biscuit"), (t2, "Biscuit"))
    conflicts = scheduler.check_conflicts()
    assert len(conflicts) == 1
    assert "CONFLICT" in conflicts[0]
