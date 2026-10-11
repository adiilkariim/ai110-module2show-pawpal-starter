# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

### Three core actions a user should be able to perform

### 1. Enter owner and pet information
The user can enter their name, their pet’s name, and select the pet type.

### 2. Add and prioritize care tasks
The user can create tasks for the pet, assign a duration, and choose a priority level.

### 3. View and organize the daily plan
The user can review the tasks for the day and see how the app organizes them into a scheduling plan.

### UML design overview
My design (in `diagrams/uml.mmd`) separates the data from the planning logic. An `Owner` owns one or more `Pet`s, and each `Pet` has its own list of `Task`s. The `Scheduler` is linked to the owner, so it can gather tasks from every pet at once, sort and filter them, check for time conflicts, and produce one `DailyPlan` for the whole household. The plan lists each chosen task with its pet, start time, and the reason it was picked, plus any tasks that didn't fit.

When I reviewed the first AI-drafted diagram, I found gaps and added them: `Owner` had `add_pet()` but no `pets` list to store them, there was no way to edit or remove a task, the owner's preferences never reached the scheduler, and the plan had no start times. After checking the design against the project requirements, I also gave `Task` a due time and frequency, added a method to list a pet's tasks, and changed the `Scheduler` from planning for one pet to planning across all of the owner's pets.

### Classes and responsibilities
- **Owner**: holds the owner's name, daily available minutes, preferences, and list of pets. It can add or remove pets, update preferences, and return every task across all of its pets.
- **Pet**: holds the pet's name, species, and care tasks. It can add, edit, remove, and list tasks and report how many it has.
- **Task**: one care activity (walk, feeding, meds, grooming, etc.) with a description, due time, duration, priority, category, frequency (daily or weekly), and completion status. It can mark itself complete and report its duration.
- **Scheduler**: the "brain" of the app. It works from the owner, so it handles tasks across all pets. It sorts tasks by priority and due time, filters out completed tasks and ones that don't fit in the available time, flags tasks whose times overlap, and generates the daily plan.
- **DailyPlan**: the result for the owner's day. It stores the scheduled tasks, the skipped tasks, and the reasoning, and it can display the plan and explain why it was built that way.
- **ScheduledTask**: a small helper that wraps a `Task` with the pet's name, its start time, end time, and the reason it was scheduled.

**b. Design changes**

Yes. After writing the class skeletons, I asked AI to review `pawpal_system.py` for missing relationships and logic bottlenecks, and I made these changes:

- **Removed `day_start` from the `Scheduler`.** Tasks already have a `due_time`, but the scheduler also had a day start time, which suggested placing tasks back-to-back from the morning. Those are two different ways to schedule, and they conflict. I chose to schedule each task at its own due time and use `check_conflicts()` to flag overlaps, because pet care usually happens at set times (meals, meds).
- **Added a `PRIORITY_ORDER` lookup.** Priority is stored as a word, and sorting words alphabetically puts "low" before "medium", which is wrong. Mapping each priority to a number (high = 0, medium = 1, low = 2) makes sorting correct, and it lets `Task` reject typos like "hgih" when it is created.
- **Added time helpers (`time_to_minutes`, `minutes_to_time`).** Times are stored as "HH:MM" text, and comparing text breaks for times like "9:00" vs "10:00". Converting to minutes makes sorting, end times, and overlap checks reliable.
- **Skipped tasks now keep their pet.** `skipped_tasks` stores `(pet, task)` pairs instead of just tasks, so the plan can say which pet's task was skipped.
- **Tasks are compared by identity (`eq=False`).** Dataclasses normally treat two tasks with the same values as equal, so removing one of two identical "Feeding 08:00" tasks could remove the wrong one.
- **Gave preferences one clear use.** `preferences` was never used, so it is now a tie-breaker when sorting, e.g. `{"preferred_categories": ["walk"]}`.

I decided not to add recurring task logic yet. A weekly task would need a "last completed" date to know whether it's due, so I'm leaving that as a stretch feature.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
