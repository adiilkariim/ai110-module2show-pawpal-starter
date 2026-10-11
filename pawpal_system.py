"""PawPal+ logic layer: the backend classes for pet care scheduling."""

from dataclasses import dataclass, field

# Lower number = scheduled first. Also used to reject invalid priorities.
PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def time_to_minutes(time_str: str) -> int:
    pass


def minutes_to_time(minutes: int) -> str:
    pass


@dataclass(eq=False)  # compare tasks by identity, so identical tasks stay distinct
class Task:
    """A single pet care activity."""

    description: str
    due_time: str  # "HH:MM", e.g. "08:00"
    duration_minutes: int
    priority: str = "medium"  # a key of PRIORITY_ORDER
    category: str = "general"  # e.g. "walk", "feeding", "meds"
    frequency: str = "daily"  # "daily" or "weekly"; recurrence is a later stretch feature
    is_complete: bool = False

    def __post_init__(self) -> None:
        pass

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.is_complete = True

    def get_duration(self) -> int:
        """Return how long this task takes, in minutes."""
        return self.duration_minutes


@dataclass
class Pet:
    """A pet and its care tasks."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a care task from this pet."""
        if task not in self.tasks:
            raise ValueError(f"Task '{task.description}' not found for {self.name}")
        self.tasks.remove(task)

    def edit_task(self, task: Task, changes: dict) -> None:
        pass

    def get_tasks(self) -> list[Task]:
        """Return a copy of this pet's tasks."""
        return list(self.tasks)

    def get_task_count(self) -> int:
        """Return how many tasks this pet has."""
        return len(self.tasks)


class Owner:
    """A pet owner with their pets, daily time budget, and preferences."""

    def __init__(self, name: str, available_minutes: int, preferences: dict | None = None):
        self.name = name
        self.available_minutes = available_minutes
        # e.g. {"preferred_categories": ["walk"]}, used as a sorting tie-breaker
        self.preferences = preferences or {}
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet, ignoring one that is already added."""
        # Identity check: two different pets can have equal fields (same name, species, no tasks)
        if not any(p is pet for p in self.pets):
            self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner."""
        for i, p in enumerate(self.pets):
            if p is pet:
                del self.pets[i]
                return
        raise ValueError(f"Pet '{pet.name}' not found for {self.name}")

    def update_preferences(self, preferences: dict) -> None:
        """Merge new preferences into the existing ones."""
        self.preferences.update(preferences)

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return every task across all pets as (pet, task) pairs."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]


@dataclass
class ScheduledTask:
    """A task placed in the plan at its due time."""

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
    skipped_tasks: list[tuple[Pet, Task]] = field(default_factory=list)
    reasoning: list[str] = field(default_factory=list)

    def display_plan(self) -> str:
        pass

    def explain_reasoning(self) -> str:
        pass


class Scheduler:
    """Builds a daily plan from the tasks of all the owner's pets."""

    def __init__(self, owner: Owner):
        self.owner = owner

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
