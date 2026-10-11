"""PawPal+ logic layer: the backend classes for pet care scheduling."""

from dataclasses import dataclass, field, fields, replace

# Lower number = scheduled first. Also used to reject invalid priorities.
PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}
FREQUENCIES = ("daily", "weekly")
LAST_MINUTE_OF_DAY = 23 * 60 + 59  # 23:59; tasks must finish by then


def time_to_minutes(time_str: str) -> int:
    """Convert "HH:MM" (or "H:MM") to minutes since midnight."""
    parts = time_str.split(":") if isinstance(time_str, str) else []
    if (
        len(parts) != 2
        or not (parts[0].isdigit() and len(parts[0]) in (1, 2))
        or not (parts[1].isdigit() and len(parts[1]) == 2)
    ):
        raise ValueError(f"Invalid time '{time_str}', expected HH:MM like '08:30'")
    hours, minutes = int(parts[0]), int(parts[1])
    if hours > 23 or minutes > 59:
        raise ValueError(f"Invalid time '{time_str}', must be between 00:00 and 23:59")
    return hours * 60 + minutes


def minutes_to_time(minutes: int) -> str:
    """Convert minutes since midnight to a zero-padded "HH:MM" string."""
    if not 0 <= minutes <= LAST_MINUTE_OF_DAY:
        raise ValueError(f"{minutes} minutes is outside a single day")
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


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
        """Validate the task's fields and normalize its due time to "HH:MM"."""
        if not isinstance(self.description, str) or not self.description.strip():
            raise ValueError("Task description cannot be empty")
        if self.priority not in PRIORITY_ORDER:
            raise ValueError(
                f"Invalid priority '{self.priority}', choose from {', '.join(PRIORITY_ORDER)}"
            )
        if self.frequency not in FREQUENCIES:
            raise ValueError(
                f"Invalid frequency '{self.frequency}', choose from {', '.join(FREQUENCIES)}"
            )
        # bool is a subclass of int, so rule it out explicitly
        if (
            not isinstance(self.duration_minutes, int)
            or isinstance(self.duration_minutes, bool)
            or self.duration_minutes < 1
        ):
            raise ValueError("Task duration must be a whole number of at least 1 minute")
        start = time_to_minutes(self.due_time)
        if start + self.duration_minutes > LAST_MINUTE_OF_DAY:
            raise ValueError(
                f"Task '{self.description}' at {self.due_time} for "
                f"{self.duration_minutes} min would run past 23:59"
            )
        self.due_time = minutes_to_time(start)  # "8:00" -> "08:00"

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
        """Update a task's fields; all changes are validated and applied together or not at all."""
        if task not in self.tasks:
            raise ValueError(f"Task '{task.description}' not found for {self.name}")
        allowed = [f.name for f in fields(Task)]
        unknown = [key for key in changes if key not in allowed]
        if unknown:
            raise ValueError(f"Unknown field(s) {unknown}. Allowed: {', '.join(allowed)}")
        # replace() builds a new Task, which runs __post_init__ validation on the changes
        validated = replace(task, **changes)
        # Copy onto the original so anything already holding this task sees the edit
        for name in allowed:
            setattr(task, name, getattr(validated, name))

    def get_tasks(self) -> list[Task]:
        """Return a copy of this pet's tasks."""
        return list(self.tasks)

    def get_task_count(self) -> int:
        """Return how many tasks this pet has."""
        return len(self.tasks)


class Owner:
    """A pet owner with their pets, daily time budget, and preferences."""

    def __init__(self, name: str, available_minutes: int, preferences: dict | None = None):
        if (
            not isinstance(available_minutes, int)
            or isinstance(available_minutes, bool)
            or available_minutes < 0
        ):
            raise ValueError("Available minutes must be a whole number of 0 or more")
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
    minutes_left: int  # time budget left after this task, counted through the day in time order


@dataclass
class DailyPlan:
    """The generated schedule for one owner's day."""

    owner_name: str
    available_minutes: int = 0
    minutes_requested: int = 0  # total duration of all incomplete tasks
    minutes_used: int = 0  # total duration of the scheduled tasks
    minutes_remaining: int = 0
    scheduled_tasks: list[ScheduledTask] = field(default_factory=list)
    skipped_tasks: list[tuple[Pet, Task, str]] = field(default_factory=list)  # (pet, task, reason)
    reasoning: list[str] = field(default_factory=list)

    def display_plan(self) -> str:
        pass

    def explain_reasoning(self) -> str:
        pass

    def get_time_summary(self) -> str:
        """Describe how the time budget was used, and how far over it the tasks are, if at all."""
        if self.minutes_requested == 0:
            return f"No tasks need time today; all {self.available_minutes} min are free."
        if self.available_minutes == 0:
            return "No time available today; all tasks were skipped."
        summary = (
            f"{self.minutes_used} of {self.available_minutes} min used, "
            f"{self.minutes_remaining} min remaining."
        )
        shortfall = self.minutes_requested - self.available_minutes
        if shortfall > 0:
            summary += (
                f" Your tasks need {self.minutes_requested} min in total, "
                f"{shortfall} min more than you have."
                " Tip: shorten or reschedule a lower-priority task to fit everything."
            )
        else:
            summary += " All tasks fit."
        return summary


class Scheduler:
    """Builds a daily plan from the tasks of all the owner's pets."""

    def __init__(self, owner: Owner):
        self.owner = owner

    def _preferred_categories(self) -> list[str]:
        """Return the owner's preferred categories, lowercased."""
        return [c.lower() for c in self.owner.preferences.get("preferred_categories", [])]

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Gather every task from every pet, through the owner."""
        return self.owner.get_all_tasks()

    def sort_tasks(self, tasks: list[tuple[Pet, Task]]) -> list[tuple[Pet, Task]]:
        """Order tasks by priority, then preferred category, then due time."""
        preferred = self._preferred_categories()
        return sorted(
            tasks,
            key=lambda pair: (
                PRIORITY_ORDER[pair[1].priority],
                0 if pair[1].category.lower() in preferred else 1,
                time_to_minutes(pair[1].due_time),
            ),
        )

    def filter_tasks(
        self, tasks: list[tuple[Pet, Task]]
    ) -> tuple[list[tuple[Pet, Task]], list[tuple[Pet, Task, str]]]:
        """Drop completed tasks, then keep tasks in the given order while they fit the time budget.

        Returns (kept, skipped), where each skipped entry carries the reason it was left out.
        """
        kept, skipped = [], []
        minutes_left = self.owner.available_minutes
        for pet, task in tasks:
            if task.is_complete:
                continue
            if task.duration_minutes <= minutes_left:
                kept.append((pet, task))
                minutes_left -= task.duration_minutes
            else:
                # Keep going: a shorter task later in the list may still fit
                reason = (
                    f"{task.priority} priority, needs {task.duration_minutes} min, "
                    f"only {minutes_left} min left"
                )
                skipped.append((pet, task, reason))
        return kept, skipped

    def check_conflicts(self, tasks: list[tuple[Pet, Task]]) -> list[str]:
        """Return a warning for every pair of tasks whose times overlap, across all pets."""
        timed = []
        for pet, task in tasks:
            start = time_to_minutes(task.due_time)
            timed.append((start, start + task.duration_minutes, pet, task))
        timed.sort(key=lambda item: item[0])

        warnings = []
        # Compare every pair, not just neighbours: one long task can overlap several later ones
        for i, (start_a, end_a, pet_a, task_a) in enumerate(timed):
            for start_b, end_b, pet_b, task_b in timed[i + 1:]:
                # Touching tasks (one ends exactly when the next starts) do not overlap
                if start_a < end_b and start_b < end_a:
                    warnings.append(
                        f"Conflict: {task_a.description} ({pet_a.name}) "
                        f"{minutes_to_time(start_a)}-{minutes_to_time(end_a)} overlaps "
                        f"{task_b.description} ({pet_b.name}) "
                        f"{minutes_to_time(start_b)}-{minutes_to_time(end_b)}"
                    )
        return warnings

    def generate_plan(self) -> DailyPlan:
        """Build today's plan: gather, sort, fit to the time budget, check conflicts, explain."""
        all_tasks = self.get_all_tasks()
        pending = [(pet, task) for pet, task in all_tasks if not task.is_complete]
        kept, skipped = self.filter_tasks(self.sort_tasks(pending))
        preferred = self._preferred_categories()

        plan = DailyPlan(
            owner_name=self.owner.name,
            available_minutes=self.owner.available_minutes,
            minutes_requested=sum(task.duration_minutes for _, task in pending),
            minutes_used=sum(task.duration_minutes for _, task in kept),
            skipped_tasks=skipped,
        )
        plan.minutes_remaining = plan.available_minutes - plan.minutes_used

        # Priority decided which tasks got in; show them in the order the day happens
        minutes_left = plan.available_minutes
        for pet, task in sorted(kept, key=lambda pair: time_to_minutes(pair[1].due_time)):
            minutes_left -= task.duration_minutes
            reason = f"{task.priority} priority"
            if task.category.lower() in preferred:
                reason += f", preferred category ({task.category})"
            reason += ", fits in your time"
            start = time_to_minutes(task.due_time)
            plan.scheduled_tasks.append(
                ScheduledTask(
                    pet_name=pet.name,
                    task=task,
                    start_time=task.due_time,
                    end_time=minutes_to_time(start + task.duration_minutes),
                    reason=reason,
                    minutes_left=minutes_left,
                )
            )

        if not all_tasks:
            plan.reasoning.append("No tasks to schedule today. Add a pet and some tasks first.")
        elif not pending:
            plan.reasoning.append("All tasks are already complete. Nothing left to schedule today.")
        else:
            plan.reasoning.append(
                "Tasks were chosen by priority (high first), then preferred category, then time, "
                "until the available time ran out."
            )
            if skipped:
                plan.reasoning.append(
                    f"{len(skipped)} task(s) did not fit in the available time and were skipped."
                )
            plan.reasoning.extend(self.check_conflicts(kept))
        return plan
