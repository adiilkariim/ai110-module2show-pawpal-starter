"""PawPal+ terminal demo: runs the scheduler end to end on sample data.

The owner, pets, and tasks below are demo data for testing the scheduler in the
terminal, not real users or pets. The real app gets its data from the Streamlit form.
"""

from pawpal_system import Owner, Pet, Task, Scheduler


def build_sample_owner() -> Owner:
    """Create a sample owner with two pets and tasks chosen to exercise each scheduler feature."""
    owner = Owner("Sample Owner", available_minutes=90, preferences={"preferred_categories": ["walk"]})

    dog = Pet("Dog 1", "dog")
    cat = Pet("Cat 1", "cat")

    # Added out of time order on purpose, so sort_by_time() has something to sort
    dog.add_task(Task("Fetch play", "18:00", 40, "medium", "play"))
    cat.add_task(Task("Brush fur", "10:00", 20, "low", "grooming"))  # won't fit the time budget
    dog.add_task(Task("Medication", "09:00", 5, "high", "meds"))
    cat.add_task(Task("Vitamins", "09:00", 5, "medium", "meds"))  # exact same time as Medication
    dog.add_task(Task("Morning walk", "08:00", 30, "high", "walk"))  # preferred category
    cat.add_task(Task("Breakfast", "08:15", 10, "high", "feeding"))  # overlaps the walk

    litter = Task("Clean litter box", "07:30", 5, "medium", "cleaning")
    litter.mark_complete()  # already done, so the scheduler filters it out
    cat.add_task(litter)

    owner.add_pet(dog)
    owner.add_pet(cat)
    return owner


def print_section(title: str) -> None:
    """Print a section heading."""
    print(f"\n--- {title} ---")


def print_tasks(tasks) -> None:
    """Print (pet, task) pairs as aligned rows."""
    for pet, task in tasks:
        status = "done" if task.is_complete else "to do"
        print(f"  {pet.name:<6} {task.due_time}  {task.description:<17} "
              f"{task.duration_minutes:>3} min  {task.priority:<6}  ({status})")


def main() -> None:
    """Run the demo: gather, sort, and filter tasks, build and explain the plan, then show recurrence."""
    owner = build_sample_owner()
    scheduler = Scheduler(owner)

    print(f"PawPal+ demo for {owner.name}: {len(owner.pets)} pets, "
          f"{owner.available_minutes} min available today")

    print_section("Step 1: All tasks across pets (in the order they were added)")
    print_tasks(scheduler.get_all_tasks())

    print_section("Step 2: Sorted by time with sort_by_time()")
    print_tasks(scheduler.sort_by_time(scheduler.get_all_tasks()))

    print_section("Step 3: Filtered with filter_by()")
    print("  Only Dog 1's tasks:")
    print_tasks(scheduler.filter_by(pet_name="Dog 1"))
    print("  Only tasks still to do:")
    print_tasks(scheduler.filter_by(is_complete=False))
    print("  Only completed tasks:")
    print_tasks(scheduler.filter_by(is_complete=True))

    print_section("Step 4: Sorted by priority, then preferred category, then time (before filtering)")
    for rank, (pet, task) in enumerate(scheduler.sort_tasks(scheduler.get_all_tasks()), start=1):
        print(f"  {rank}. {task.description} ({pet.name}) [{task.priority}, {task.category}]")

    print_section("Step 5: Build the plan")
    plan = scheduler.generate_plan()
    print(plan.display_plan())

    print_section("Step 6: Explain the plan")
    print(plan.explain_reasoning())

    print_section("Step 7: Recurring tasks")
    dog = owner.pets[0]
    medication = next(task for task in dog.get_tasks() if task.description == "Medication")
    next_task = dog.complete_task(medication)
    print(f"  Completed '{medication.description}' ({medication.frequency}) due {medication.due_date}.")
    print(f"  Next occurrence added for {dog.name}: due {next_task.due_date} at {next_task.due_time}, "
          f"complete={next_task.is_complete}")
    still_today = [st.task.description for st in scheduler.generate_plan().scheduled_tasks]
    print(f"  Rebuilt plan for today: {', '.join(still_today)} (tomorrow's copy is not included)")


if __name__ == "__main__":
    main()
