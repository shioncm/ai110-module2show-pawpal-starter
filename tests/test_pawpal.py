import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Task, Pet


def test_task_complete_changes_status():
    task = Task("Feed", "08:00")
    assert task.is_completed is False
    task.complete()
    assert task.is_completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet("Buddy", "Dog", 3)
    assert len(pet.tasks) == 0
    pet.add_task(Task("Walk", "07:00"))
    assert len(pet.tasks) == 1
