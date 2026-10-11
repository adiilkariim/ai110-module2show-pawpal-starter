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

    dog.add_task(Task("Morning walk", "08:00", 30, "high", "walk"))  # preferred category
    cat.add_task(Task("Breakfast", "08:15", 10, "high", "feeding"))  # overlaps the walk
    dog.add_task(Task("Medication", "09:00", 5, "high", "meds"))
    cat.add_task(Task("Brush fur", "10:00", 20, "low", "grooming"))  # won't fit the time budget
    dog.add_task(Task("Fetch play", "18:00", 40, "medium", "play"))

    litter = Task("Clean litter box", "07:30", 5, "medium", "cleaning")
    litter.mark_complete()  # already done, so the scheduler filters it out
    cat.add_task(litter)

    owner.add_pet(dog)
    owner.add_pet(cat)
    return owner


def print_section(title: str) -> None:
    """Print a section heading."""
    print(f"\n--- {title} ---")


def main() -> None:
    """Run the demo: gather tasks, sort them, build the plan, and explain it."""
    owner = build_sample_owner()
    scheduler = Scheduler(owner)

    print(f"PawPal+ demo for {owner.name}: {len(owner.pets)} pets, "
          f"{owner.available_minutes} min available today")

    print_section("Step 1: All tasks across pets")
    for pet, task in scheduler.get_all_tasks():
        status = "done" if task.is_complete else "to do"
        print(f"  {pet.name:<6} {task.due_time}  {task.description:<17} "
              f"{task.duration_minutes:>3} min  {task.priority:<6}  ({status})")

    print_section("Step 2: Sorted by priority, then preferred category, then time (before filtering)")
    for rank, (pet, task) in enumerate(scheduler.sort_tasks(scheduler.get_all_tasks()), start=1):
        print(f"  {rank}. {task.description} ({pet.name}) [{task.priority}, {task.category}]")

    print_section("Step 3: Build the plan")
    plan = scheduler.generate_plan()
    print(plan.display_plan())

    print_section("Step 4: Explain the plan")
    print(plan.explain_reasoning())


if __name__ == "__main__":
    main()
