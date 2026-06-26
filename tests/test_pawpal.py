import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Task, Pet


def make_task(priority="medium"):
    return Task(
        description="Test task",
        time="09:00",
        frequency="daily",
        priority=priority,
        duration_minutes=15,
        assigned_pet_name="Mochi",
    )


def test_task_completion_changes_status():
    task = make_task()
    assert task.is_complete is False
    task.complete()
    assert task.is_complete is True


def test_adding_task_increases_pet_task_count():
    pet = Pet(name="Mochi", species="Dog", age=3)
    assert len(pet.tasks) == 0
    pet.add_task(make_task())
    assert len(pet.tasks) == 1
    pet.add_task(make_task())
    assert len(pet.tasks) == 2
