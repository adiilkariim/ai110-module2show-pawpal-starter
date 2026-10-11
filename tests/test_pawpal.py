"""Automated tests for the PawPal+ scheduling system."""

from datetime import date, timedelta

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task

# A fixed date keeps the tests reproducible no matter what day they run
DAY = date(2026, 10, 10)


def make_task(description, due_time, duration, priority="medium", category="general", **kwargs):
    """Create a task due on DAY unless another date is given."""
    kwargs.setdefault("due_date", DAY)
    return Task(description, due_time, duration, priority, category, **kwargs)


def make_owner(minutes=120, preferences=None, pets=()):
    """Create an owner with the given pets."""
    owner = Owner("Test Owner", minutes, preferences)
    for pet in pets:
        owner.add_pet(pet)
    return owner


# --- Core behavior ---------------------------------------------------------


def test_mark_complete_changes_status():
    task = make_task("Morning walk", "08:00", 30)
    assert task.is_complete is False
    task.mark_complete()
    assert task.is_complete is True


def test_add_task_increases_count():
    pet = Pet("Pet A", "dog")
    assert pet.get_task_count() == 0
    pet.add_task(make_task("Breakfast", "08:00", 10))
    assert pet.get_task_count() == 1


# --- Sorting ---------------------------------------------------------------


def test_sort_by_time_returns_chronological_order():
    dog, cat = Pet("Pet A", "dog"), Pet("Pet B", "cat")
    dog.add_task(make_task("Evening walk", "18:00", 30, "low"))
    cat.add_task(make_task("Breakfast", "07:30", 10, "high"))
    dog.add_task(make_task("Lunch", "12:00", 10, "medium"))
    scheduler = Scheduler(make_owner(pets=[dog, cat]), plan_date=DAY)

    sorted_times = [task.due_time for _, task in scheduler.sort_by_time(scheduler.get_all_tasks())]
    assert sorted_times == ["07:30", "12:00", "18:00"]

    plan_times = [st.start_time for st in scheduler.generate_plan().scheduled_tasks]
    assert plan_times == ["07:30", "12:00", "18:00"]


def test_sort_tasks_by_priority_then_preference_then_time():
    pet = Pet("Pet A", "dog")
    pet.add_task(make_task("Nail trim", "07:00", 10, "low", "grooming"))
    pet.add_task(make_task("Feeding", "08:00", 10, "high", "feeding"))
    pet.add_task(make_task("Walk", "09:00", 30, "high", "walk"))
    pet.add_task(make_task("Play", "06:00", 15, "medium", "play"))
    owner = make_owner(preferences={"preferred_categories": ["walk"]}, pets=[pet])
    scheduler = Scheduler(owner, plan_date=DAY)

    order = [task.description for _, task in scheduler.sort_tasks(scheduler.get_all_tasks())]
    # Walk beats the earlier Feeding because both are high and walk is preferred
    assert order == ["Walk", "Feeding", "Play", "Nail trim"]


# --- Recurrence ------------------------------------------------------------


def test_completing_daily_task_creates_task_for_next_day():
    pet = Pet("Pet A", "dog")
    meds = make_task("Medication", "09:00", 5, "high", frequency="daily")
    pet.add_task(meds)

    next_task = pet.complete_task(meds)

    assert meds.is_complete is True
    assert next_task is not None
    assert next_task.due_date == DAY + timedelta(days=1)
    assert next_task.is_complete is False
    assert (next_task.description, next_task.due_time) == ("Medication", "09:00")
    assert pet.get_task_count() == 2


def test_completing_weekly_task_creates_task_seven_days_later():
    pet = Pet("Pet A", "cat")
    bath = make_task("Bath", "10:00", 20, frequency="weekly")
    pet.add_task(bath)

    next_task = pet.complete_task(bath)

    assert next_task.due_date == DAY + timedelta(days=7)


def test_completing_one_time_task_does_not_recur():
    pet = Pet("Pet A", "dog")
    vet = make_task("Vet visit", "14:00", 60, "high", frequency="once")
    pet.add_task(vet)

    assert pet.complete_task(vet) is None
    assert pet.get_task_count() == 1


def test_completing_a_task_twice_does_not_duplicate_next_occurrence():
    pet = Pet("Pet A", "dog")
    walk = make_task("Walk", "08:00", 30, frequency="daily")
    pet.add_task(walk)

    pet.complete_task(walk)
    assert pet.complete_task(walk) is None
    assert pet.get_task_count() == 2


def test_next_occurrence_is_planned_tomorrow_not_today():
    pet = Pet("Pet A", "dog")
    walk = make_task("Walk", "08:00", 30, frequency="daily")
    pet.add_task(walk)
    owner = make_owner(pets=[pet])
    pet.complete_task(walk)

    today = Scheduler(owner, plan_date=DAY).generate_plan()
    tomorrow = Scheduler(owner, plan_date=DAY + timedelta(days=1)).generate_plan()

    assert today.scheduled_tasks == []
    assert [st.task.description for st in tomorrow.scheduled_tasks] == ["Walk"]


# --- Conflict detection ----------------------------------------------------


def test_conflict_flagged_for_tasks_at_the_same_time():
    pet = Pet("Pet A", "dog")
    pet.add_task(make_task("Breakfast", "08:00", 10))
    pet.add_task(make_task("Medication", "08:00", 5))
    scheduler = Scheduler(make_owner(pets=[pet]), plan_date=DAY)

    conflicts = scheduler.check_conflicts(scheduler.get_all_tasks())

    assert len(conflicts) == 1
    assert "Breakfast" in conflicts[0] and "Medication" in conflicts[0]


def test_conflict_flagged_across_pets_but_not_for_touching_tasks():
    dog, cat = Pet("Pet A", "dog"), Pet("Pet B", "cat")
    dog.add_task(make_task("Walk", "08:00", 30))
    cat.add_task(make_task("Breakfast", "08:15", 10))  # overlaps the walk
    cat.add_task(make_task("Play", "08:30", 10))  # starts exactly when the walk ends
    plan = Scheduler(make_owner(pets=[dog, cat]), plan_date=DAY).generate_plan()

    assert len(plan.conflicts) == 1
    assert "Walk (Pet A)" in plan.conflicts[0] and "Breakfast (Pet B)" in plan.conflicts[0]


def test_same_time_on_different_days_is_not_a_conflict():
    pet = Pet("Pet A", "dog")
    pet.add_task(make_task("Walk", "08:00", 30))
    pet.add_task(make_task("Walk", "08:00", 30, due_date=DAY + timedelta(days=1)))
    scheduler = Scheduler(make_owner(pets=[pet]), plan_date=DAY)

    assert scheduler.check_conflicts(scheduler.get_all_tasks()) == []


# --- Filtering and time budget ---------------------------------------------


def test_tasks_over_budget_are_skipped_and_smaller_ones_still_fit():
    pet = Pet("Pet A", "dog")
    pet.add_task(make_task("Long hike", "07:00", 45, "high"))
    pet.add_task(make_task("Bath", "12:00", 20, "medium"))
    pet.add_task(make_task("Treat", "15:00", 5, "low"))
    plan = Scheduler(make_owner(minutes=50, pets=[pet]), plan_date=DAY).generate_plan()

    assert [st.task.description for st in plan.scheduled_tasks] == ["Long hike", "Treat"]
    assert [task.description for _, task, _ in plan.skipped_tasks] == ["Bath"]
    assert "needs 20 min, only 5 min left" in plan.skipped_tasks[0][2]
    assert (plan.minutes_requested, plan.minutes_used, plan.minutes_remaining) == (70, 50, 0)


def test_completed_tasks_are_excluded_and_not_listed_as_skipped():
    pet = Pet("Pet A", "dog")
    done = make_task("Morning walk", "08:00", 30)
    done.mark_complete()
    pet.add_task(done)
    pet.add_task(make_task("Breakfast", "08:30", 10))
    plan = Scheduler(make_owner(pets=[pet]), plan_date=DAY).generate_plan()

    assert [st.task.description for st in plan.scheduled_tasks] == ["Breakfast"]
    assert plan.skipped_tasks == []
    assert plan.minutes_requested == 10


# --- Edge cases ------------------------------------------------------------


def test_pet_with_no_tasks_gives_an_empty_plan():
    plan = Scheduler(make_owner(pets=[Pet("Pet A", "dog")]), plan_date=DAY).generate_plan()

    assert plan.scheduled_tasks == [] and plan.skipped_tasks == [] and plan.conflicts == []
    assert "No tasks to schedule today" in plan.display_plan()


def test_owner_with_no_pets_gives_an_empty_plan():
    plan = Scheduler(make_owner(), plan_date=DAY).generate_plan()

    assert plan.scheduled_tasks == []
    assert plan.minutes_used == 0


@pytest.mark.parametrize(
    "kwargs",
    [
        {"priority": "hgih"},
        {"due_time": "25:00"},
        {"duration": 0},
        {"due_time": "23:50", "duration": 20},  # would run past midnight
    ],
)
def test_invalid_task_input_is_rejected(kwargs):
    args = {"description": "Walk", "due_time": "08:00", "duration": 30, "priority": "medium"}
    args.update(kwargs)
    with pytest.raises(ValueError):
        make_task(args["description"], args["due_time"], args["duration"], args["priority"])


def test_edit_task_is_all_or_nothing():
    pet = Pet("Pet A", "dog")
    walk = make_task("Walk", "08:00", 30)
    pet.add_task(walk)

    with pytest.raises(ValueError):
        pet.edit_task(walk, {"due_time": "09:00", "priority": "hgih"})

    assert walk.due_time == "08:00" and walk.priority == "medium"
