# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Running PawPal+

With the virtual environment active, run these from the project folder:

```bash
# Terminal demo: builds and prints a schedule from sample data
python main.py

# Streamlit app: opens in your browser at http://localhost:8501
python -m streamlit run app.py

# Tests
python -m pytest
```

Press `Ctrl + C` in the terminal to stop the Streamlit app.

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Output of `python main.py`, which runs the scheduler on sample demo data (one owner with 90 minutes, two pets, seven tasks):

```
PawPal+ demo for Sample Owner: 2 pets, 90 min available today

--- Step 1: All tasks across pets (in the order they were added) ---
  Dog 1  18:00  Fetch play         40 min  medium  (to do)
  Dog 1  09:00  Medication          5 min  high    (to do)
  Dog 1  08:00  Morning walk       30 min  high    (to do)
  Cat 1  10:00  Brush fur          20 min  low     (to do)
  Cat 1  09:00  Vitamins            5 min  medium  (to do)
  Cat 1  08:15  Breakfast          10 min  high    (to do)
  Cat 1  07:30  Clean litter box    5 min  medium  (done)

--- Step 2: Sorted by time with sort_by_time() ---
  Cat 1  07:30  Clean litter box    5 min  medium  (done)
  Dog 1  08:00  Morning walk       30 min  high    (to do)
  Cat 1  08:15  Breakfast          10 min  high    (to do)
  Dog 1  09:00  Medication          5 min  high    (to do)
  Cat 1  09:00  Vitamins            5 min  medium  (to do)
  Cat 1  10:00  Brush fur          20 min  low     (to do)
  Dog 1  18:00  Fetch play         40 min  medium  (to do)

--- Step 3: Filtered with filter_by() ---
  Only Dog 1's tasks:
  Dog 1  18:00  Fetch play         40 min  medium  (to do)
  Dog 1  09:00  Medication          5 min  high    (to do)
  Dog 1  08:00  Morning walk       30 min  high    (to do)
  Only tasks still to do:
  Dog 1  18:00  Fetch play         40 min  medium  (to do)
  Dog 1  09:00  Medication          5 min  high    (to do)
  Dog 1  08:00  Morning walk       30 min  high    (to do)
  Cat 1  10:00  Brush fur          20 min  low     (to do)
  Cat 1  09:00  Vitamins            5 min  medium  (to do)
  Cat 1  08:15  Breakfast          10 min  high    (to do)
  Only completed tasks:
  Cat 1  07:30  Clean litter box    5 min  medium  (done)

--- Step 4: Sorted by priority, then preferred category, then time (before filtering) ---
  1. Morning walk (Dog 1) [high, walk]
  2. Breakfast (Cat 1) [high, feeding]
  3. Medication (Dog 1) [high, meds]
  4. Clean litter box (Cat 1) [medium, cleaning]
  5. Vitamins (Cat 1) [medium, meds]
  6. Fetch play (Dog 1) [medium, play]
  7. Brush fur (Cat 1) [low, grooming]

--- Step 5: Build the plan ---
Schedule for Sample Owner on Monday, 2026-10-12
===============================================
  Time         Task          Pet    Priority  Duration  Time left
  ---------------------------------------------------------------
  08:00-08:30  Morning walk  Dog 1  high        30 min     60 min
  08:15-08:25  Breakfast     Cat 1  high        10 min     50 min
  09:00-09:05  Medication    Dog 1  high         5 min     45 min
  09:00-09:05  Vitamins      Cat 1  medium       5 min     40 min
  18:00-18:40  Fetch play    Dog 1  medium      40 min      0 min

⏭️ Skipped:
  - Brush fur (Cat 1): low priority, needs 20 min, only 0 min left

⚠️ Warnings:
  ⚠️ Conflict: Morning walk (Dog 1) 08:00-08:30 overlaps Breakfast (Cat 1) 08:15-08:25
  ⚠️ Conflict: Medication (Dog 1) 09:00-09:05 overlaps Vitamins (Cat 1) 09:00-09:05

⏱️ Time: 90 of 90 min used, 0 min remaining. Your tasks need 110 min in total, 20 min more than you have. Tip: shorten or reschedule a lower-priority task to fit everything.

--- Step 6: Explain the plan ---
Why this plan:
  - Tasks were chosen by priority (high first), then preferred category, then time, until the available time ran out.
  - 1 task(s) did not fit in the available time and were skipped.
  - 2 time conflict(s) found. Both tasks stay in the plan, so you can decide which one to move.
  - Morning walk (Dog 1) at 08:00: high priority, preferred category (walk), fits in your time
  - Breakfast (Cat 1) at 08:15: high priority, fits in your time
  - Medication (Dog 1) at 09:00: high priority, fits in your time
  - Vitamins (Cat 1) at 09:00: medium priority, fits in your time
  - Fetch play (Dog 1) at 18:00: medium priority, fits in your time

--- Step 7: Recurring tasks ---
  Completed 'Medication' (daily) due 2026-10-12.
  Next occurrence added for Dog 1: due 2026-10-13 at 09:00, complete=False
  Rebuilt plan for today: Morning walk, Breakfast, Vitamins, Fetch play (tomorrow's copy is not included)
```

## 🧪 Testing PawPal+

Run the full test suite from the project folder:

```bash
python -m pytest
```

### What the tests cover

The suite in `tests/test_pawpal.py` has 21 tests:

- **Core behavior:** `mark_complete()` changes a task's status, and `add_task()` increases a pet's task count.
- **Sorting:** tasks come out in chronological order across pets, and priority sorting puts high before medium before low, with the owner's preferred category breaking ties.
- **Recurrence:** completing a daily task creates a new task for the next day, a weekly task comes back 7 days later, a one-time task doesn't recur, completing a task twice doesn't create duplicates, and tomorrow's copy appears in tomorrow's plan, not today's.
- **Conflict detection:** two tasks at the exact same time are flagged, overlaps between different pets are flagged, and tasks that only touch (one ends when the next starts) or fall on different days are not.
- **Time budget and filtering:** tasks that don't fit the available time are skipped with a reason while smaller tasks can still fit, and completed tasks are left out without being listed as skipped.
- **Edge cases:** a pet with no tasks, an owner with no pets, invalid input (bad priority, bad time, zero duration, a task running past midnight), and `edit_task()` applying all changes or none.

Sample test output:

```
================================================================== test session starts ==================================================================
platform win32 -- Python 3.13.15, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\user4\Desktop\ai110-module2show-pawpal-starter
plugins: anyio-4.15.1
collected 21 items

tests\test_pawpal.py .....................                                                                                                         [100%]

================================================================== 21 passed in 0.08s ===================================================================
```

### Confidence level

★★★★☆ (4/5): all 21 tests pass, covering each scheduling feature plus edge cases. One star is held back because the scheduler fills time by priority, which isn't always the best possible fit, and a daily task that isn't completed doesn't carry over to the next day.

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | | e.g., by priority, duration |
| Filtering | | e.g., skip tasks if time runs out |
| Conflict handling | | e.g., overlapping time slots |
| Recurring tasks | | e.g., daily vs. weekly |

## 🧠 Advanced Scheduling Logic

PawPal+ goes beyond sorting by time. It builds the day's plan with priority-based scheduling inside a time budget:

1. **Priority-based sorting:** `Scheduler.sort_tasks()` orders tasks by priority first (high, then medium, then low, using the `PRIORITY_ORDER` lookup), then by the owner's preferred task types as a tie-breaker, then by time.
2. **Time-budget fitting:** `Scheduler.filter_tasks()` goes through the sorted tasks and keeps each one that fits in the owner's remaining available minutes. A task that doesn't fit is skipped with a reason, and the scheduler keeps checking the rest, so a shorter task later in the list can still fit.
3. **Overlap detection:** `Scheduler.find_overlaps()` and `Scheduler.check_conflicts()` compare the start and end of every pair of tasks on the same day, across all pets. They flag overlapping durations, not just identical start times, while tasks that only touch (one ends when the next starts) are not flagged.

CLI output examples from `python main.py`:

Priority-based order. The walk comes before the other high-priority tasks because *walk* is the owner's preferred type:

```
--- Step 4: Sorted by priority, then preferred category, then time (before filtering) ---
  1. Morning walk (Dog 1) [high, walk]
  2. Breakfast (Cat 1) [high, feeding]
  3. Medication (Dog 1) [high, meds]
  4. Clean litter box (Cat 1) [medium, cleaning]
  5. Vitamins (Cat 1) [medium, meds]
  6. Fetch play (Dog 1) [medium, play]
  7. Brush fur (Cat 1) [low, grooming]
```

The resulting plan. High-priority tasks get the 90 minutes first, the low-priority task that doesn't fit is skipped with a reason, and two conflicts between different pets' tasks are flagged: one overlap and one at the exact same time:

```
Schedule for Sample Owner on Monday, 2026-10-12
===============================================
  Time         Task          Pet    Priority  Duration  Time left
  ---------------------------------------------------------------
  08:00-08:30  Morning walk  Dog 1  high        30 min     60 min
  08:15-08:25  Breakfast     Cat 1  high        10 min     50 min
  09:00-09:05  Medication    Dog 1  high         5 min     45 min
  09:00-09:05  Vitamins      Cat 1  medium       5 min     40 min
  18:00-18:40  Fetch play    Dog 1  medium      40 min      0 min

⏭️ Skipped:
  - Brush fur (Cat 1): low priority, needs 20 min, only 0 min left

⚠️ Warnings:
  ⚠️ Conflict: Morning walk (Dog 1) 08:00-08:30 overlaps Breakfast (Cat 1) 08:15-08:25
  ⚠️ Conflict: Medication (Dog 1) 09:00-09:05 overlaps Vitamins (Cat 1) 09:00-09:05

⏱️ Time: 90 of 90 min used, 0 min remaining. Your tasks need 110 min in total, 20 min more than you have. Tip: shorten or reschedule a lower-priority task to fit everything.
```

## 🎨 Output Formatting

**Terminal (CLI) output**, in `pawpal_system.py`:

- `DailyPlan.display_plan()` prints the schedule as an aligned table using Python f-string width and alignment specifiers (for example `{text:<20}` and `{number:>5}`), with no external library. Column widths are sized to the longest task and pet name, so the table stays lined up for any input.
- The output is split into labeled sections with emoji markers: the schedule table, **⏭️ Skipped** (each task with its reason), **⚠️ Warnings** (each conflict marked with ⚠️), and a **⏱️ Time** summary from `DailyPlan.get_time_summary()`.
- `DailyPlan.explain_reasoning()` prints a "Why this plan" list with the reason each task was chosen.

**Streamlit app**, in `app.py`:

- `st.table` for the pets list and the schedule, and `st.metric` tiles for available, scheduled, and remaining minutes.
- `st.success`, `st.warning`, and `st.info` for the time summary, depending on whether everything fits.
- Emoji output: a ⚠️ note in the schedule row of each task that overlaps another, naming what it overlaps, and the 🐾 app icon.
- Field-level messages: `st.error` and `st.warning` appear directly above the input they're about (for example, an overlap warning above the Time field).
- `st.expander` for the "Why this plan?" explanation.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
