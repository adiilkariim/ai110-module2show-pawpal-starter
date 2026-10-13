import os
from datetime import date, time

import streamlit as st

from pawpal_system import (
    FREQUENCIES,
    LAST_MINUTE_OF_DAY,
    PRIORITY_ORDER,
    Owner,
    Pet,
    Scheduler,
    Task,
    describe_slot,
    time_to_minutes,
)

CATEGORIES = ["walk", "feeding", "meds", "grooming", "play", "cleaning"]
DATA_FILE = "data.json"  # pets and tasks are saved here so they survive restarts

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# The Owner object holds all pets and tasks, so it lives in session state across reruns.
# On the first run, load the saved data if there is any.
if "owner" not in st.session_state:
    loaded = None
    if os.path.exists(DATA_FILE):
        try:
            loaded = Owner.load_from_json(DATA_FILE)
        except (ValueError, KeyError, TypeError):
            loaded = None  # unreadable file: start fresh instead of crashing
    st.session_state.owner = loaded or Owner("", 60)
    # Fill the "You" inputs with the saved values
    st.session_state.owner_name = st.session_state.owner.name
    st.session_state.available_minutes = st.session_state.owner.available_minutes
    st.session_state.preferred_categories = [
        c for c in st.session_state.owner.preferences.get("preferred_categories", []) if c in CATEGORIES
    ]
if "errors" not in st.session_state:
    st.session_state.errors = {}  # field key -> message shown above that field
if "flash" not in st.session_state:
    st.session_state.flash = {}  # section -> (kind, message) shown once after an action

owner: Owner = st.session_state.owner


def show_field_error(field_key: str) -> None:
    """Show the error for one input field as small red text above it (no box, so fields stay aligned)."""
    message = st.session_state.errors.get(field_key)
    if message:
        st.markdown(f":red[⚠ {message}]")


def show_flash(section: str) -> None:
    """Show (once) the result message of the last action in a section."""
    kind, message = st.session_state.flash.pop(section, (None, None))
    if message:
        getattr(st, kind)(message)


def find_task_overlaps(pet: Pet, description: str, due_date: date, start: str, duration: int):
    """Return the existing (pet, task) pairs a new task would overlap on its day, across all pets."""
    try:
        draft = Task(description=description or "New task", due_time=start,
                     duration_minutes=duration, due_date=due_date)
    except ValueError:
        return []  # the field errors already explain what's wrong
    same_day = [(p, t) for p, t in owner.get_all_tasks() if not t.is_complete and t.due_date == due_date]
    found = []
    for first, second in Scheduler(owner).find_overlaps(same_day + [(pet, draft)]):
        if first[1] is draft:
            found.append(second)
        elif second[1] is draft:
            found.append(first)
    return found


# --- Button callbacks (run before the page redraws, so messages land above the right fields) ---


def add_pet() -> None:
    name = st.session_state.pet_name.strip()
    st.session_state.errors.pop("pet_name", None)
    if not name:
        st.session_state.errors["pet_name"] = "Please enter a pet name."
    elif any(p.name.lower() == name.lower() for p in owner.pets):
        st.session_state.errors["pet_name"] = f"You already have a pet named {name}. Use a different name."
    else:
        owner.add_pet(Pet(name, st.session_state.pet_species))
        st.session_state.pet_name = ""
        st.session_state.flash["pets"] = ("success", f"Added {name}.")


def add_task() -> None:
    errors = st.session_state.errors
    for key in ("task_description", "task_duration", "task_other"):
        errors.pop(key, None)

    pet = owner.pets[st.session_state.task_pet]
    # Drop stray wrapping quotes and trailing periods, e.g. "'Morning walk'." -> "Morning walk"
    description = st.session_state.task_description.strip().rstrip(".").strip().strip("'\"").strip()
    start = st.session_state.task_time.strftime("%H:%M")
    duration = int(st.session_state.task_duration)
    if not description:
        errors["task_description"] = "Please enter a description, e.g. 'Morning walk'."
    if time_to_minutes(start) + duration > LAST_MINUTE_OF_DAY:
        errors["task_duration"] = f"Starting at {start}, {duration} min would run past midnight. Shorten it or start earlier."
    if errors.get("task_description") or errors.get("task_duration"):
        return

    try:
        task = Task(
            description=description,
            due_time=start,
            duration_minutes=duration,
            priority=st.session_state.task_priority,
            category=(st.session_state.task_category or "").strip() or "general",
            frequency=st.session_state.task_frequency,
            due_date=date.today(),
        )
    except ValueError as error:
        errors["task_other"] = str(error)
        return
    overlaps = find_task_overlaps(pet, description, task.due_date, start, duration)
    pet.add_task(task)
    st.session_state.task_description = ""
    message = f"Added '{description}' for {pet.name} on {task.due_date:%b %d} at {start}."
    if overlaps:
        message += " Note: it overlaps another task. You can see it in the schedule."
    st.session_state.flash["tasks"] = ("success", message)


def complete_task(pet: Pet, task: Task) -> None:
    next_task = pet.complete_task(task)
    message = f"Marked '{task.description}' ({pet.name}) as done."
    if next_task is not None:
        message += f" Next {task.frequency} occurrence added for {next_task.due_date:%A, %b %d}."
    st.session_state.flash["task_list"] = ("info", message)


def remove_task(pet: Pet, task: Task) -> None:
    pet.remove_task(task)
    st.session_state.flash["task_list"] = ("info", f"Removed '{task.description}' ({pet.name}).")


# --- Page ---

st.title("🐾 PawPal+")
st.caption("Plan your pets' care for the day: add your pets and their tasks, then build a schedule "
           "that fits your available time, puts important tasks first, and flags overlaps.")

st.header("👤 You")
owner.name = st.text_input("Your name", placeholder="e.g. Alex", key="owner_name").strip()
owner.available_minutes = int(
    st.number_input("Minutes available for pet care per day (1–1440 min)",
                    min_value=1, max_value=1440, step=1, key="available_minutes")
)
owner.update_preferences({
    "preferred_categories": st.multiselect(
        "Preferred task types (optional)",
        CATEGORIES,
        key="preferred_categories",
        placeholder="Choose task types",
    )
})
st.caption(
    "**What it's for:** when two tasks have the same priority and there's only time for one, "
    "the type you prefer is scheduled first. For example, if you prefer *walk*, an evening walk "
    "gets the time before grooming.  \n"
    "**How to use it:** click the box and pick one or more types from the list."
)

st.header("🐶 Pets")
show_field_error("pet_name")
col_name, col_species = st.columns([2, 1])
with col_name:
    st.text_input("Pet name", placeholder="e.g. Biscuit", key="pet_name")
with col_species:
    st.selectbox("Species", ["dog", "cat", "other"], key="pet_species")
st.button("Add pet", on_click=add_pet)
show_flash("pets")

if owner.pets:
    st.table([{"Pet": p.name, "Species": p.species, "Number of tasks": p.get_task_count()} for p in owner.pets])
else:
    st.info("Add a pet to start adding care tasks.")

st.header("📝 Care tasks")
no_pets = not owner.pets  # tasks belong to a pet, so the form stays disabled until one exists
if no_pets:
    st.info("Add a pet above first, then add its tasks here.")
st.selectbox("Pet", range(len(owner.pets)), key="task_pet", disabled=no_pets,
             format_func=lambda i: f"{owner.pets[i].name} ({owner.pets[i].species})")

show_field_error("task_description")
st.text_input("Description", placeholder="e.g. Morning walk", key="task_description", disabled=no_pets)

# Values from the previous run let the warnings sit above the fields they describe
current_time = st.session_state.get("task_time", time(8, 0)).strftime("%H:%M")
current_duration = int(st.session_state.get("task_duration", 15))
current_pet = None if no_pets else owner.pets[st.session_state.get("task_pet") or 0]

# Time and duration warnings sit right above that row, so the two inputs stay lined up
if current_pet is not None:
    for other_pet, other_task in find_task_overlaps(
        current_pet, st.session_state.get("task_description", ""), date.today(),
        current_time, current_duration,
    ):
        st.markdown(f":orange[⚠ Time: {current_time} overlaps {describe_slot(other_pet, other_task)}. "
                    "You can still add it, or pick another time.]")
show_field_error("task_duration")
if time_to_minutes(current_time) + current_duration > LAST_MINUTE_OF_DAY:
    st.markdown(":orange[⚠ Duration: this would run past midnight. Shorten it or start earlier.]")

col_time, col_duration = st.columns(2)
with col_time:
    st.time_input("Time", value=time(8, 0), step=300, key="task_time", disabled=no_pets)
with col_duration:
    st.number_input("Duration (minutes)", min_value=1, max_value=LAST_MINUTE_OF_DAY,
                    value=15, step=1, key="task_duration", disabled=no_pets)

col_priority, col_category, col_frequency = st.columns(3)
with col_priority:
    st.selectbox("Priority", list(PRIORITY_ORDER), index=1, key="task_priority", disabled=no_pets)
with col_category:
    st.selectbox("Type", CATEGORIES, key="task_category", disabled=no_pets)
with col_frequency:
    st.selectbox("Repeats", FREQUENCIES, index=FREQUENCIES.index("daily"), key="task_frequency",
                 disabled=no_pets)

show_field_error("task_other")
st.button("Add task", on_click=add_task, disabled=no_pets)
show_flash("tasks")

if owner.pets:
    st.subheader("Task list")
    show_flash("task_list")
    any_tasks = False
    for pet in owner.pets:
        tasks = Scheduler(owner).sort_by_time([(pet, task) for task in pet.get_tasks()])
        if not tasks:
            continue
        any_tasks = True
        st.markdown(f"**{pet.name}** ({pet.species})")
        for _, task in tasks:
            col_text, col_done, col_remove = st.columns([5, 1, 1])
            status = " · done ✓" if task.is_complete else ""
            col_text.markdown(
                f"{task.due_date:%b %d} **{task.due_time}** {task.description} · "
                f"{task.duration_minutes} min · {task.priority} · {task.frequency}{status}"
            )
            col_done.button("Done", key=f"done_{id(task)}", disabled=task.is_complete,
                            on_click=complete_task, args=(pet, task))
            col_remove.button("Remove", key=f"remove_{id(task)}", on_click=remove_task, args=(pet, task))
    if not any_tasks:
        st.info("No tasks yet. Add one above.")

st.header("📅 Schedule")
if st.button("Generate today's schedule", type="primary"):
    st.session_state.show_plan = True

if st.session_state.get("show_plan"):
    scheduler = Scheduler(owner)  # plans for today
    plan = scheduler.generate_plan()

    st.subheader(f"Schedule for {owner.name or 'your pets'} on {plan.plan_date:%A, %B %d}")
    col_available, col_used, col_left = st.columns(3)
    col_available.metric("Available", f"{plan.available_minutes} min")
    col_used.metric("Scheduled", f"{plan.minutes_used} min")
    col_left.metric("Remaining", f"{plan.minutes_remaining} min")

    summary = plan.get_time_summary()
    if plan.minutes_requested == 0:
        st.info(summary)
    elif plan.minutes_requested > plan.available_minutes:
        st.warning(summary)
    else:
        st.success(summary)

    if plan.scheduled_tasks:
        # Each overlapping task gets its own note naming what it overlaps
        pet_of = {id(task): pet for pet, task in owner.get_all_tasks()}
        scheduled = [(pet_of[id(item.task)], item.task) for item in plan.scheduled_tasks]
        notes: dict[int, list[str]] = {}
        for (pet_a, task_a), (pet_b, task_b) in scheduler.find_overlaps(scheduled):
            notes.setdefault(id(task_a), []).append(f"overlaps {describe_slot(pet_b, task_b)}")
            notes.setdefault(id(task_b), []).append(f"overlaps {describe_slot(pet_a, task_a)}")

        st.table([
            {
                "Time": f"{item.start_time}-{item.end_time}",
                "Task": item.task.description,
                "Pet": item.pet_name,
                "Priority": item.task.priority,
                "Duration": f"{item.task.duration_minutes} min",
                "Time left": f"{item.minutes_left} min",
                "Note": ("⚠️ " + "; ".join(notes[id(item.task)])) if id(item.task) in notes else "",
            }
            for item in plan.scheduled_tasks
        ])
    elif plan.skipped_tasks:
        st.info("No tasks fit in your available time.")
    else:
        st.info(plan.reasoning[0] if plan.reasoning else "No tasks scheduled.")

    for pet, task, reason in plan.skipped_tasks:
        st.warning(f"Skipped **{task.description}** ({pet.name}): {reason}.")

    with st.expander("Why this plan?"):
        st.markdown(plan.explain_reasoning())

# Every change (adding a pet or task, Done, Remove, editing your details) reruns the page,
# so saving here keeps data.json up to date
owner.save_to_json(DATA_FILE)
