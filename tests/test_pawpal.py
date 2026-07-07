import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import date, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler


# ── shared helpers ─────────────────────────────────────────────────────────

def make_task(description="Test task", time="09:00", priority="medium",
              frequency="daily", duration_minutes=15, pet_name="Mochi"):
    return Task(
        description=description,
        time=time,
        frequency=frequency,
        priority=priority,
        duration_minutes=duration_minutes,
        assigned_pet_name=pet_name,
    )


def make_scheduler(*pets):
    """Build an Owner+Scheduler pre-loaded with the given Pet objects."""
    owner = Owner(name="Jordan", email="jordan@test.com")
    for pet in pets:
        owner.add_pet(pet)
    return Scheduler(owner=owner)


# ── existing tests (kept) ──────────────────────────────────────────────────

def test_task_completion_changes_status():
    # complete() flips is_complete from False to True
    task = make_task()
    assert task.is_complete is False
    task.complete()
    assert task.is_complete is True


def test_adding_task_increases_pet_task_count():
    # add_task() appends to pet.tasks; len grows with each call
    pet = Pet(name="Mochi", species="Dog", age=3)
    assert len(pet.tasks) == 0
    pet.add_task(make_task())
    assert len(pet.tasks) == 1
    pet.add_task(make_task())
    assert len(pet.tasks) == 2


# ── 1. sorting correctness ─────────────────────────────────────────────────

def test_sort_by_time_returns_chronological_order():
    # sort_by_time() should reorder tasks by HH:MM regardless of insertion order.
    # We insert evening → morning → afternoon and expect morning → afternoon → evening back.
    pet = Pet(name="Mochi", species="Dog", age=3)
    evening = make_task("Evening meds",   time="19:30", pet_name="Mochi")
    morning = make_task("Morning walk",   time="07:00", pet_name="Mochi")
    noon    = make_task("Afternoon feed", time="12:00", pet_name="Mochi")
    for t in [evening, morning, noon]:
        pet.add_task(t)

    scheduler = make_scheduler(pet)
    sorted_tasks = scheduler.sort_by_time(pet.tasks)

    # Extract just the time strings so the assertion message is readable
    times = [t.time for t in sorted_tasks]
    assert times == ["07:00", "12:00", "19:30"]


def test_get_sorted_schedule_priority_before_time():
    # get_sorted_schedule() ranks by priority first (high > medium > low),
    # then breaks ties with time. A low-priority early task must come AFTER
    # a high-priority late task.
    pet = Pet(name="Mochi", species="Dog", age=3)
    low_early  = make_task("Low early",  time="07:00", priority="low",  pet_name="Mochi")
    high_late  = make_task("High late",  time="19:00", priority="high", pet_name="Mochi")
    mid_noon   = make_task("Mid noon",   time="12:00", priority="medium", pet_name="Mochi")
    for t in [low_early, high_late, mid_noon]:
        pet.add_task(t)

    scheduler = make_scheduler(pet)
    schedule = scheduler.get_sorted_schedule()

    assert schedule[0].description == "High late"
    assert schedule[1].description == "Mid noon"
    assert schedule[2].description == "Low early"


def test_sorted_schedule_empty_when_no_pending_tasks():
    # A pet whose only task is already complete should produce an empty schedule.
    pet = Pet(name="Mochi", species="Dog", age=3)
    task = make_task(pet_name="Mochi")
    task.complete()
    pet.add_task(task)

    scheduler = make_scheduler(pet)
    assert scheduler.get_sorted_schedule() == []


# ── 2. recurrence logic ────────────────────────────────────────────────────

def test_completing_daily_task_spawns_next_occurrence():
    # complete_task() on a daily task must add a new task to the pet
    # with due_date = today + 1 day and is_complete = False.
    pet = Pet(name="Mochi", species="Dog", age=3)
    task = make_task(frequency="daily", pet_name="Mochi")
    pet.add_task(task)

    scheduler = make_scheduler(pet)
    scheduler.complete_task(task)

    # pet.tasks now has the original (complete) + the spawned clone
    assert len(pet.tasks) == 2
    next_task = pet.tasks[1]
    assert next_task.is_complete is False
    assert next_task.due_date == (date.today() + timedelta(days=1)).isoformat()


def test_completing_weekly_task_spawns_next_occurrence():
    # Same as above but for weekly — due_date must be today + 7 days.
    pet = Pet(name="Mochi", species="Dog", age=3)
    task = make_task(frequency="weekly", pet_name="Mochi")
    pet.add_task(task)

    scheduler = make_scheduler(pet)
    scheduler.complete_task(task)

    next_task = pet.tasks[1]
    assert next_task.due_date == (date.today() + timedelta(weeks=1)).isoformat()


def test_completing_once_task_does_not_spawn():
    # "once" tasks are one-offs; no next occurrence should be created.
    pet = Pet(name="Mochi", species="Dog", age=3)
    task = make_task(frequency="once", pet_name="Mochi")
    pet.add_task(task)

    scheduler = make_scheduler(pet)
    scheduler.complete_task(task)

    assert len(pet.tasks) == 1   # still just the original


def test_completing_task_twice_does_not_double_award_points():
    # complete_task() on an already-done task must be a no-op —
    # points should only be awarded once.
    pet = Pet(name="Mochi", species="Dog", age=3)
    task = make_task(priority="high", pet_name="Mochi")  # high = 20 pts
    pet.add_task(task)

    scheduler = make_scheduler(pet)
    scheduler.complete_task(task)
    scheduler.complete_task(task)   # second call — should be ignored

    assert scheduler.owner.points == 20


# ── 3. conflict detection ──────────────────────────────────────────────────

def test_same_pet_overlapping_tasks_flagged():
    # Two tasks on the same pet whose windows overlap must appear in get_conflicts().
    # "Morning walk" 07:00 for 30 min (ends 07:30) overlaps
    # "Early groom"  07:15 for 20 min (ends 07:35).
    pet = Pet(name="Mochi", species="Dog", age=3)
    walk  = make_task("Morning walk",  time="07:00", duration_minutes=30, pet_name="Mochi")
    groom = make_task("Early groom",   time="07:15", duration_minutes=20, pet_name="Mochi")
    pet.add_task(walk)
    pet.add_task(groom)

    scheduler = make_scheduler(pet)
    conflicts = scheduler.get_conflicts()

    assert len(conflicts) == 1
    descriptions = {t.description for pair in conflicts for t in pair}
    assert "Morning walk" in descriptions
    assert "Early groom"  in descriptions


def test_back_to_back_tasks_do_not_conflict():
    # Tasks that touch but do not overlap (end of A == start of B) are NOT conflicts.
    # "Feed"  08:00 for 10 min ends exactly at 08:10.
    # "Walk"  08:10 for 20 min starts at 08:10 — no overlap.
    pet = Pet(name="Mochi", species="Dog", age=3)
    feed = make_task("Feed", time="08:00", duration_minutes=10, pet_name="Mochi")
    walk = make_task("Walk", time="08:10", duration_minutes=20, pet_name="Mochi")
    pet.add_task(feed)
    pet.add_task(walk)

    scheduler = make_scheduler(pet)
    assert scheduler.get_conflicts() == []


def test_cross_pet_overlapping_tasks_flagged():
    # Overlapping windows across two different pets must appear in get_cross_pet_conflicts().
    mochi = Pet(name="Mochi", species="Dog", age=3)
    luna  = Pet(name="Luna",  species="Cat", age=2)
    mochi.add_task(make_task("Mochi walk",    time="07:00", duration_minutes=30, pet_name="Mochi"))
    luna.add_task( make_task("Luna stretch",  time="07:00", duration_minutes=20, pet_name="Luna"))

    scheduler = make_scheduler(mochi, luna)
    conflicts = scheduler.get_cross_pet_conflicts()

    assert len(conflicts) == 1


def test_no_conflicts_when_pet_has_no_tasks():
    # A pet with zero tasks must not raise and must return an empty conflict list.
    pet = Pet(name="Mochi", species="Dog", age=3)
    scheduler = make_scheduler(pet)
    assert scheduler.get_conflicts() == []
    assert scheduler.get_cross_pet_conflicts() == []
