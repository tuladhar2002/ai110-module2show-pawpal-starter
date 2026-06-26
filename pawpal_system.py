from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Pet:
    name: str
    species: str
    age: int
    owner_name: str
    level: int = 1

    def level_up(self) -> None:
        pass

    def get_info(self) -> str:
        pass


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str  # "low", "medium", "high"
    assigned_pet_name: str
    scheduled_time: Optional[str] = None
    is_complete: bool = False

    def complete(self) -> int:
        """Mark task complete and return points earned."""
        pass

    def schedule(self, time: str) -> None:
        pass

    def get_priority_score(self) -> int:
        pass


@dataclass
class PetStore:
    available_pets: list = field(default_factory=list)
    items: dict = field(default_factory=dict)
    adoption_cost: int = 100

    def browse_items(self) -> list:
        pass

    def adopt_pet(self, user: "User", pet_name: str) -> Optional[Pet]:
        pass

    def purchase_item(self, user: "User", item_name: str) -> bool:
        pass


@dataclass
class User:
    name: str
    email: str
    points: int = 0
    pets: list = field(default_factory=list)
    tasks: list = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        pass

    def complete_task(self, task: Task) -> None:
        pass

    def spend_points(self, amount: int) -> bool:
        pass

    def get_total_points(self) -> int:
        pass

    def view_schedule(self) -> list:
        pass
