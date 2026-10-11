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

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Output of `python main.py`, which runs the scheduler on sample demo data (one owner with 90 minutes, two pets, six tasks):

```
PawPal+ demo for Sample Owner: 2 pets, 90 min available today

--- Step 1: All tasks across pets ---
  Dog 1  08:00  Morning walk       30 min  high    (to do)
  Dog 1  09:00  Medication          5 min  high    (to do)
  Dog 1  18:00  Fetch play         40 min  medium  (to do)
  Cat 1  08:15  Breakfast          10 min  high    (to do)
  Cat 1  10:00  Brush fur          20 min  low     (to do)
  Cat 1  07:30  Clean litter box    5 min  medium  (done)

--- Step 2: Sorted by priority, then preferred category, then time (before filtering) ---
  1. Morning walk (Dog 1) [high, walk]
  2. Breakfast (Cat 1) [high, feeding]
  3. Medication (Dog 1) [high, meds]
  4. Clean litter box (Cat 1) [medium, cleaning]
  5. Fetch play (Dog 1) [medium, play]
  6. Brush fur (Cat 1) [low, grooming]

--- Step 3: Build the plan ---
Today's Schedule for Sample Owner
=================================
  Time         Task          Pet    Priority  Duration  Time left
  ---------------------------------------------------------------
  08:00-08:30  Morning walk  Dog 1  high        30 min     60 min
  08:15-08:25  Breakfast     Cat 1  high        10 min     50 min
  09:00-09:05  Medication    Dog 1  high         5 min     45 min
  18:00-18:40  Fetch play    Dog 1  medium      40 min      5 min

Skipped:
  - Brush fur (Cat 1): low priority, needs 20 min, only 5 min left

Warnings:
  ! Conflict: Morning walk (Dog 1) 08:00-08:30 overlaps Breakfast (Cat 1) 08:15-08:25

Time: 85 of 90 min used, 5 min remaining. Your tasks need 105 min in total, 15 min more than you have. Tip: shorten or reschedule a lower-priority task to fit everything.

--- Step 4: Explain the plan ---
Why this plan:
  - Tasks were chosen by priority (high first), then preferred category, then time, until the available time ran out.
  - 1 task(s) did not fit in the available time and were skipped.
  - 1 time conflict(s) found. Both tasks stay in the plan, so you can decide which one to move.
  - Morning walk (Dog 1) at 08:00: high priority, preferred category (walk), fits in your time
  - Breakfast (Cat 1) at 08:15: high priority, fits in your time
  - Medication (Dog 1) at 09:00: high priority, fits in your time
  - Fetch play (Dog 1) at 18:00: medium priority, fits in your time
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | | e.g., by priority, duration |
| Filtering | | e.g., skip tasks if time runs out |
| Conflict handling | | e.g., overlapping time slots |
| Recurring tasks | | e.g., daily vs. weekly |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
