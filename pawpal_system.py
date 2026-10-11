"""PawPal+ logic layer: the backend classes for pet care scheduling."""

from dataclasses import dataclass, field


@dataclass
class Task:
    """A single pet care activity."""

    description: str
    due_time: str  # "HH:MM", e.g. "08:00"
    duration_minutes: int
    priority: str = "medium"  # "low", "medium", or "high"
    category: str = "general"  # e.g. "walk", "feeding", "meds"
    frequency: str = "daily"  # "daily" or "weekly"
    is_complete: bool = False

    def mark_complete(self) -> None:
        pass

    def get_duration(self) -> int:
        pass


@dataclass
class Pet:
    """A pet and its care tasks."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task: Task) -> None:
        pass

    def edit_task(self, task: Task, changes: dict) -> None:
        pass

    def get_tasks(self) -> list[Task]:
        pass

    def get_task_count(self) -> int:
        pass


class Owner:
    """A pet owner with their pets, daily time budget, and preferences."""

    def __init__(self, name: str, available_minutes: int, preferences: dict | None = None):
        self.name = name
        self.available_minutes = available_minutes
        self.preferences = preferences or {}
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        pass

    def remove_pet(self, pet: Pet) -> None:
        pass

    def update_preferences(self, preferences: dict) -> None:
        pass

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        pass


@dataclass
class ScheduledTask:
    """A task placed in the plan at a specific time."""

    pet_name: str
    task: Task
    start_time: str
    end_time: str
    reason: str


@dataclass
class DailyPlan:
    """The generated schedule for one owner's day."""

    owner_name: str
    scheduled_tasks: list[ScheduledTask] = field(default_factory=list)
    skipped_tasks: list[Task] = field(default_factory=list)
    reasoning: list[str] = field(default_factory=list)

    def display_plan(self) -> str:
        pass

    def explain_reasoning(self) -> str:
        pass


class Scheduler:
    """Builds a daily plan from the tasks of all the owner's pets."""

    def __init__(self, owner: Owner, day_start: str = "08:00"):
        self.owner = owner
        self.day_start = day_start

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        pass

    def sort_tasks(self, tasks: list[tuple[Pet, Task]]) -> list[tuple[Pet, Task]]:
        pass

    def filter_tasks(self, tasks: list[tuple[Pet, Task]]) -> list[tuple[Pet, Task]]:
        pass

    def check_conflicts(self, tasks: list[tuple[Pet, Task]]) -> list[str]:
        pass

    def generate_plan(self) -> DailyPlan:
        pass
