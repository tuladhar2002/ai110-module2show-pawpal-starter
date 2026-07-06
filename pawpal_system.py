import dataclasses
from dataclasses import dataclass, field
from datetime import date, timedelta


def _time_to_minutes(time_str: str) -> int:
    """Convert 'HH:MM' to total minutes since midnight for arithmetic comparisons."""
    h, m = time_str.split(":")
    return int(h) * 60 + int(m)


def _windows_overlap(a, b) -> bool:
    """Return True if two tasks' time windows overlap (start_a < end_b and start_b < end_a)."""
    return _time_to_minutes(a.time) < b.end_time_minutes() and _time_to_minutes(b.time) < a.end_time_minutes()


@dataclass
class Task:
    description: str
    time: str               # "08:00" 24-hour format
    frequency: str          # "daily", "weekly", "once"
    priority: str           # "low", "medium", "high"
    duration_minutes: int
    assigned_pet_name: str
    is_complete: bool = False
    due_date: str = ""          # "YYYY-MM-DD"; empty = no specific date

    def complete(self) -> int:
        """Mark task done and return points earned based on priority."""
        self.is_complete = True
        return {"low": 5, "medium": 10, "high": 20}.get(self.priority, 5)

    def get_priority_score(self) -> int:
        """Return a numeric score (1-3) for sorting by priority."""
        return {"low": 1, "medium": 2, "high": 3}.get(self.priority, 1)

    def next_occurrence(self) -> "Task":
        """Return a new Task scheduled for the next daily/weekly occurrence.

        timedelta(days=1) moves the date forward by exactly 24 hours;
        timedelta(weeks=1) moves it forward by 7 days — both are stdlib
        helpers that handle month/year rollovers automatically.
        """
        if self.frequency == "daily":
            delta = timedelta(days=1)
        elif self.frequency == "weekly":
            delta = timedelta(weeks=1)
        else:
            raise ValueError(f"next_occurrence() called on a '{self.frequency}' task")
        base = date.fromisoformat(self.due_date) if self.due_date else date.today()
        next_date = base + delta
        return dataclasses.replace(self, due_date=next_date.isoformat(), is_complete=False)

    def reset(self) -> None:
        """Reset a recurring task to incomplete for the next cycle. No-ops on 'once' tasks."""
        if self.frequency != "once":
            self.is_complete = False

    def end_time_minutes(self) -> int:
        """Return the minute-of-day when this task ends (start + duration)."""
        return _time_to_minutes(self.time) + self.duration_minutes

    def conflicts_with(self, other: "Task") -> bool:
        """Return True if this task's window overlaps with another task on the same pet.

        Tasks with different non-empty due_dates are on different calendar days
        and cannot conflict even if their HH:MM windows overlap.
        """
        if self.assigned_pet_name != other.assigned_pet_name or self is other:
            return False
        if self.due_date and other.due_date and self.due_date != other.due_date:
            return False
        return _windows_overlap(self, other)

    def __str__(self) -> str:
        """Return a formatted one-line summary of the task."""
        status = "Done" if self.is_complete else "Pending"
        date_part = f" | due {self.due_date}" if self.due_date else ""
        return (
            f"[{self.time}] {self.description} | {self.priority} priority | "
            f"{self.duration_minutes} min | {self.frequency}{date_part} | {status}"
        )


@dataclass
class Pet:
    name: str
    species: str
    age: int
    level: int = 1
    tasks: list = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Append a task to this pet's task list."""
        self.tasks.append(task)

    def get_pending_tasks(self) -> list:
        """Return only tasks that have not been completed yet."""
        return [t for t in self.tasks if not t.is_complete]

    def level_up(self) -> None:
        """Increment the pet's level by one."""
        self.level += 1
        print(f"{self.name} leveled up to level {self.level}!")

    def get_info(self) -> str:
        """Return a formatted summary string of this pet's details."""
        return (
            f"{self.name} ({self.species}) | Age: {self.age} | "
            f"Level: {self.level} | Tasks: {len(self.tasks)}"
        )


@dataclass
class Owner:
    name: str
    email: str
    points: int = 0
    pets: list = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's pet list."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list:
        """Collect every task from every pet the owner has."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks

    def adjust_points(self, amount: int) -> bool:
        """Add (positive) or deduct (negative) points. Returns False if funds are insufficient."""
        if amount < 0 and self.points < -amount:
            print(f"Not enough points. Have {self.points}, need {-amount}.")
            return False
        self.points += amount
        return True

    def earn_points(self, amount: int) -> None:
        """Add points to the owner's total."""
        self.adjust_points(amount)

    def spend_points(self, amount: int) -> bool:
        """Deduct points if the owner has enough; return True on success, False otherwise."""
        return self.adjust_points(-amount)

    def get_summary(self) -> str:
        """Return a formatted one-line overview of the owner's status."""
        return (
            f"Owner: {self.name} | Points: {self.points} | "
            f"Pets: {len(self.pets)}"
        )


@dataclass
class Scheduler:
    """Retrieves and organizes all pet tasks from the owner into a sorted daily schedule."""
    owner: Owner

    def get_pending_tasks(self) -> list:
        """Return all incomplete tasks across every pet the owner has."""
        return [t for t in self.owner.get_all_tasks() if not t.is_complete]

    def get_sorted_schedule(self) -> list:
        """Sort pending tasks by priority (high first), then by scheduled time."""
        pending = self.get_pending_tasks()
        return sorted(pending, key=lambda t: (-t.get_priority_score(), t.time))

    def get_schedule_by_time(self) -> list:
        """Return all pending tasks in strict chronological order."""
        pending = self.get_pending_tasks()
        return sorted(pending, key=lambda t: _time_to_minutes(t.time))

    def sort_by_time(self, tasks: list) -> list:
        """Return a copy of tasks sorted by their 'HH:MM' time string (lexicographic, zero-padded)."""
        return sorted(tasks, key=lambda t: t.time)

    def _filter_tasks(self, pet_name: str = None, completed: bool = None) -> list:
        """Internal filter — combine pet_name and/or completion status. Use named wrappers externally."""
        tasks = self.owner.get_all_tasks()
        if pet_name is not None:
            tasks = [t for t in tasks if t.assigned_pet_name == pet_name]
        if completed is not None:
            tasks = [t for t in tasks if t.is_complete == completed]
        return tasks

    def get_tasks_by_pet(self, pet_name: str) -> list:
        """Return all tasks (any status) assigned to the named pet."""
        return self._filter_tasks(pet_name=pet_name)

    def get_tasks_by_status(self, completed: bool = False) -> list:
        """Return tasks filtered by completion status across all pets."""
        return self._filter_tasks(completed=completed)

    def get_pending_by_pet(self, pet_name: str) -> list:
        """Return only pending tasks for a specific pet."""
        return self._filter_tasks(pet_name=pet_name, completed=False)

    def reset_recurring_tasks(self, frequency: str = "daily") -> int:
        """Reset completed recurring tasks of the given frequency. Returns number of tasks reset."""
        count = 0
        for task in self.owner.get_all_tasks():
            if task.frequency == frequency and task.is_complete:
                task.reset()
                count += 1
        return count

    def get_conflicts(self, tasks: list = None) -> list:
        """Return (task_a, task_b) pairs whose time windows overlap on the same pet.

        Pass a pre-built pending list to avoid a redundant traversal when called
        from get_all_conflicts(); omit to let this method build its own.
        """
        pending = tasks if tasks is not None else self.get_pending_tasks()
        conflicts = []
        for i, task_a in enumerate(pending):
            for task_b in pending[i + 1:]:
                if task_a.conflicts_with(task_b):
                    conflicts.append((task_a, task_b))
        return conflicts

    def get_cross_pet_conflicts(self, tasks: list = None) -> list:
        """Return (task_a, task_b) pairs that overlap in time across *different* pets.

        A single owner cannot physically attend to two pets simultaneously, so
        overlapping windows across pets are flagged even though they pass
        Task.conflicts_with() (which only checks same-pet pairs).
        Pass a pre-built pending list to avoid a redundant traversal when called
        from get_all_conflicts(); omit to let this method build its own.
        """
        pending = tasks if tasks is not None else self.get_pending_tasks()
        conflicts = []
        for i, task_a in enumerate(pending):
            for task_b in pending[i + 1:]:
                if task_a.assigned_pet_name == task_b.assigned_pet_name:
                    continue  # same-pet pairs handled by get_conflicts()
                if task_a.due_date and task_b.due_date and task_a.due_date != task_b.due_date:
                    continue  # different calendar days — no real overlap
                if _windows_overlap(task_a, task_b):
                    conflicts.append((task_a, task_b))
        return conflicts

    def get_all_conflicts(self) -> list:
        """Combine same-pet and cross-pet conflicts with a single pending-task traversal."""
        pending = self.get_pending_tasks()
        return self.get_conflicts(pending) + self.get_cross_pet_conflicts(pending)

    def warn_conflicts(self) -> None:
        """Print human-readable warnings for all conflicts. Never raises — safe to call anywhere."""
        pending = self.get_pending_tasks()          # one traversal shared by both calls below
        same   = self.get_conflicts(pending)
        across = self.get_cross_pet_conflicts(pending)

        if not same and not across:
            print("No scheduling conflicts detected.")
            return

        print(f"\n=== Conflict Warnings for {self.owner.name}'s Schedule ===")

        for task_a, task_b in same:
            print(
                f"  [SAME-PET]   {task_a.assigned_pet_name}: "
                f"'{task_a.description}' ({task_a.time}, {task_a.duration_minutes}min) "
                f"overlaps '{task_b.description}' ({task_b.time}, {task_b.duration_minutes}min)"
            )

        for task_a, task_b in across:
            print(
                f"  [CROSS-PET]  '{task_a.description}' ({task_a.assigned_pet_name}, "
                f"{task_a.time}, {task_a.duration_minutes}min) "
                f"overlaps '{task_b.description}' ({task_b.assigned_pet_name}, "
                f"{task_b.time}, {task_b.duration_minutes}min)"
            )

    def complete_task(self, task: Task) -> None:
        """Mark a task complete, award points, and auto-schedule the next occurrence.

        For "daily" tasks timedelta(days=1) advances the due date by one day;
        for "weekly" tasks timedelta(weeks=1) advances it by seven days.
        The new Task is appended to the same pet so it shows up in the next schedule.
        """
        if task.is_complete:
            print(f"'{task.description}' is already complete.")
            return
        points = task.complete()
        self.owner.earn_points(points)
        print(f"Completed '{task.description}'. +{points} points! Total: {self.owner.points}")

        if task.frequency in ("daily", "weekly"):
            next_task = task.next_occurrence()
            for pet in self.owner.pets:
                if pet.name == task.assigned_pet_name:
                    pet.add_task(next_task)
                    print(f"  → Next '{next_task.description}' auto-scheduled for {next_task.due_date}")
                    break

    def print_schedule(self) -> None:
        """Print the priority-sorted daily schedule to the terminal."""
        schedule = self.get_sorted_schedule()
        if not schedule:
            print("No pending tasks — all done!")
            return
        print(f"\n=== Daily Schedule for {self.owner.name}'s Pets (by priority) ===")
        for task in schedule:
            print(f"  {task}")
        print(f"  ({len(schedule)} task(s) remaining)")

    def print_conflicts(self) -> None:
        """Print any detected time-overlap conflicts to the terminal."""
        conflicts = self.get_conflicts()
        if not conflicts:
            print("No scheduling conflicts detected.")
            return
        print(f"\n=== Scheduling Conflicts for {self.owner.name}'s Pets ===")
        for task_a, task_b in conflicts:
            print(
                f"  CONFLICT [{task_a.assigned_pet_name}]: "
                f"'{task_a.description}' ({task_a.time}, {task_a.duration_minutes}min) "
                f"overlaps '{task_b.description}' ({task_b.time}, {task_b.duration_minutes}min)"
            )
