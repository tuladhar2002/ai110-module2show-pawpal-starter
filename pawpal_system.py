from dataclasses import dataclass, field


@dataclass
class Task:
    description: str
    time: str               # "08:00" 24-hour format
    frequency: str          # "daily", "weekly", "once"
    priority: str           # "low", "medium", "high"
    duration_minutes: int
    assigned_pet_name: str
    is_complete: bool = False

    def complete(self) -> int:
        """Mark task done and return points earned based on priority."""
        self.is_complete = True
        return {"low": 5, "medium": 10, "high": 20}.get(self.priority, 5)

    def get_priority_score(self) -> int:
        """Return a numeric score (1-3) for sorting by priority."""
        return {"low": 1, "medium": 2, "high": 3}.get(self.priority, 1)

    def __str__(self) -> str:
        """Return a formatted one-line summary of the task."""
        status = "Done" if self.is_complete else "Pending"
        return (
            f"[{self.time}] {self.description} | {self.priority} priority | "
            f"{self.duration_minutes} min | {self.frequency} | {status}"
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

    def earn_points(self, amount: int) -> None:
        """Add points to the owner's total."""
        self.points += amount

    def spend_points(self, amount: int) -> bool:
        """Deduct points if the owner has enough; return True on success."""
        if self.points >= amount:
            self.points -= amount
            return True
        print(f"Not enough points. Have {self.points}, need {amount}.")
        return False

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

    def complete_task(self, task: Task) -> None:
        """Mark a task complete and award earned points to the owner."""
        if task.is_complete:
            print(f"'{task.description}' is already complete.")
            return
        points = task.complete()
        self.owner.earn_points(points)
        print(f"Completed '{task.description}'. +{points} points! Total: {self.owner.points}")

    def print_schedule(self) -> None:
        """Print the sorted daily schedule to the terminal."""
        schedule = self.get_sorted_schedule()
        if not schedule:
            print("No pending tasks — all done!")
            return
        print(f"\n=== Daily Schedule for {self.owner.name}'s Pets ===")
        for task in schedule:
            print(f"  {task}")
        print(f"  ({len(schedule)} task(s) remaining)")
