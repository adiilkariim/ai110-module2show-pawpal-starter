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
- **Task**: one care activity (walk, feeding, meds, grooming, etc.) with a description, due time, duration, priority, category, frequency (once, daily, or weekly), due date, and completion status. It can mark itself complete and report its duration.
- **Scheduler**: the "brain" of the app. It works from the owner, so it handles tasks across all pets. It sorts tasks by priority and due time, filters out completed tasks and ones that don't fit in the available time, flags tasks whose times overlap, and generates the daily plan.
- **DailyPlan**: the result for the owner's day. It stores the scheduled tasks, the skipped tasks, and the reasoning, and it can display the plan and explain why it was built that way.
- **ScheduledTask**: a small helper that wraps a `Task` with the pet's name, its start time, end time, and the reason it was scheduled.

**b. Design changes**

Yes. After writing the class skeletons, I asked AI to review `pawpal_system.py` for missing relationships and logic bottlenecks, and I made these changes:

- **Removed `day_start` from the `Scheduler`.** Tasks already have a `due_time`, but the scheduler also had a day start time, which suggested placing tasks back-to-back from the morning. Those are two different ways to schedule, and they conflict. I chose to schedule each task at its own due time and use `check_conflicts()` to flag overlaps, because pet care usually happens at set times (meals, meds).
- **Added a `PRIORITY_ORDER` lookup.** Priority is stored as a word, and sorting words alphabetically puts "low" before "medium", which is wrong. Mapping each priority to a number (high = 0, medium = 1, low = 2) makes sorting correct, and it lets `Task` reject typos like "hgih" when it is created.
- **Added time helpers (`time_to_minutes`, `minutes_to_time`).** Times are stored as "HH:MM" text, and comparing text breaks for times like "9:00" vs "10:00". Converting to minutes makes sorting, end times, and overlap checks reliable.
- **Skipped tasks now keep their pet.** `skipped_tasks` stores the pet along with each task instead of just the task, so the plan can say which pet's task was skipped.
- **Tasks are compared by identity (`eq=False`).** Dataclasses normally treat two tasks with the same values as equal, so removing one of two identical "Feeding 08:00" tasks could remove the wrong one.
- **Gave preferences one clear use.** `preferences` was never used, so it is now a tie-breaker when sorting, e.g. `{"preferred_categories": ["walk"]}`.

While implementing the scheduler, I noticed that the owner's `available_minutes` was only used behind the scenes. The app compared it to each task's `duration_minutes`, but never showed the owner how their time was being spent, so they couldn't plan around it. I added a visible time budget:

- **`DailyPlan` now tracks time:** `available_minutes`, `minutes_requested` (all incomplete tasks), `minutes_used` (scheduled tasks), `minutes_remaining`, and a `get_time_summary()` message such as "85 of 90 min used, 5 min remaining. Your tasks need 105 min in total, 15 min more than you have."
- **Each `ScheduledTask` shows `minutes_left`**, a running balance through the day, so the owner can see how each task uses up their time.
- **Skipped tasks explain the numbers.** Each skipped entry is now `(pet, task, reason)`, with reasons like "needs 20 min, only 5 min left", and `filter_tasks()` returns both the kept and the skipped tasks.
- **Conflicts got their own list.** Conflict warnings were first mixed into `reasoning` with the general notes. I gave `DailyPlan` a separate `conflicts` list so the schedule can show them in their own "Warnings" section.

At first I decided not to add recurring task logic, because a weekly task would need a date to know when it's due. When the testing phase required recurrence, I added it:

- **`Task` now has a `due_date`** (today by default), and `frequency` can be `"once"`, `"daily"`, or `"weekly"`.
- **`Task.next_occurrence()`** returns a fresh copy due 1 day later (daily) or 7 days later (weekly), and nothing for one-time tasks.
- **`Pet.complete_task()`** marks a task done and adds its next occurrence to the pet. I put this on `Pet` instead of inside `mark_complete()`, because a task doesn't know which pet it belongs to, so it can't add the new copy anywhere.
- **The `Scheduler` plans one date (`plan_date`).** Without this, completing today's walk would create tomorrow's walk, and that copy would show up in today's plan, use up time, and cause a false conflict. Conflicts are also only checked between tasks on the same day.
- **Added `sort_by_time()`** so chronological sorting is its own method that can be tested, next to `sort_tasks()` for priority.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

My scheduler considers four constraints:

1. **Priority:** high, medium, or low. High-priority tasks get the owner's time first.
2. **Available time:** the owner's minutes per day. Tasks are added only while they fit, and the rest are skipped with a reason.
3. **Task time:** each task happens at its own time, so the plan is shown in time order and overlapping tasks are flagged.
4. **Preferences:** the owner's preferred task types, used only to break ties between tasks with the same priority.

I decided priority matters most because in pet care, missing medication or a meal is worse than missing playtime. Available time comes next because it is the real limit for a busy owner. Preferences matter least, so I only use them as a tie-breaker; they should never push a low-priority task ahead of a high-priority one.

**b. Tradeoffs**

My scheduler fills the time budget **greedily by priority**: it goes through the tasks from most to least important and keeps each one that still fits. This doesn't always use the time in the best possible way. For example, with 50 minutes, a 45-minute high-priority hike gets scheduled first; then a 20-minute medium-priority bath doesn't fit, but a 5-minute low-priority treat does. So a lower-priority task gets in while a more important one is skipped, only because it is shorter.

Finding the perfect combination would be a much harder problem (similar to the "knapsack problem"), and the result would be harder for an owner to understand. The greedy approach is simple, fast, and easy to explain ("high-priority tasks get your time first"), and the plan always says why each task was skipped. For a daily pet care plan, that clarity is worth more than squeezing out a few extra minutes.

A second tradeoff: conflicts only **warn** instead of moving tasks automatically. Both overlapping tasks stay in the plan, and the owner decides which one to move, because the owner knows better than the app which task can wait.

---

## 3. AI Collaboration

**a. How you used AI**

I used two AI tools in two separate chat sessions, each for a different job:

- **Claude (Opus 5.5) in Claude Code, for building:** design review of my UML and skeleton, writing the class logic, the scheduler algorithms, the tests, connecting the Streamlit UI, and updating the UML and docs as the code changed. Its code was well structured and it didn't use much of my credit.
- **Luna 6.5 (free), for understanding and organizing:** explaining how the app and its parts work, and helping me organize my answers and notes. It was not good for code: it often skipped steps. But using it for explanations saved me from spending Claude's credit on long explanations.

The AI features that were most effective for the scheduler were **agent mode editing several files at once** (for example, adding recurrence touched `pawpal_system.py`, `main.py`, the tests, and the UML together) and **design review before coding**. Asking Claude to review my skeleton for missing relationships and bottlenecks found real problems (priority words sorting in the wrong order, times compared as text) before they turned into bugs.

The most helpful prompts were specific ones that pointed at a file and asked for problems instead of solutions, like "review my skeleton for missing relationships or logic bottlenecks", and asking "what can go wrong in these calculations?" before implementing the scheduler.

Using **separate sessions for different jobs** helped me stay organized: the coding session stayed focused on the code and files, and the explaining session was where I asked my "what is this and why" questions without cluttering the coding session or using up its credit.

**b. Judgment and verification**

I rejected or changed several AI suggestions to keep the design clean and focused on the assignment:

- **Date pickers in the app.** The AI added date fields so the owner could plan any day. I realized the assignment only asks for a **daily** plan for today, and the calendar controls were confusing, so I had them removed. Dates stay only inside the code, where recurrence needs them ("today + 1 day").
- **Custom typed task types.** The AI let users type their own task types. Since the assignment doesn't require it and it caused mismatches between the preference list and the task type list, I had it removed and kept a fixed list.
- **Extra files and features.** The AI added a `pytest.ini` file I hadn't asked for. I deleted it because the assignment didn't require it and `python -m pytest` works without it. After that I made a rule that the AI only adds what the assignment asks for, and shows me changes before applying them.
- **Big warning boxes.** I asked for warnings to sit next to the specific field they're about instead of one general bar, and later for them to be small colored text so they don't push the inputs out of line.
- **The time budget.** This one was my idea: I noticed the AI's scheduler used `available_minutes` behind the scenes but never showed the owner how much time was left, so I asked for a visible time summary and a "minutes left" column.

I didn't just trust that the code worked: I checked the code and the logic behind it myself, making sure I understood why each method does what it does. I also used **more than one AI model for verification and comparison**. Sometimes I gave one model the code another model had written and asked it to look for bugs and contradictions, for example between what the code actually did and what the documentation or the UML said. When the models disagreed, that told me where to look more closely.

To verify, I also **ran everything myself**: `python main.py` to check the demo output, `python -m pytest` to confirm all 21 tests pass, and the Streamlit app to try each feature by hand. Using the app is how I found several problems, like the minutes field only stepping down to 5, the date picker confusion, and task names keeping stray quotes.

---

## 4. Testing and Verification

**a. What you tested**

My test suite (`tests/test_pawpal.py`, 21 passing tests) covers:

- **Core behavior:** `mark_complete()` changes the status, and adding a task increases the pet's task count.
- **Sorting:** tasks come out in chronological order across pets, and priority sorting puts high before medium before low, with preferences breaking ties.
- **Recurrence:** a completed daily task creates a new task for the next day, weekly tasks come back after 7 days, one-time tasks don't recur, completing twice doesn't duplicate, and tomorrow's copy isn't in today's plan.
- **Conflict detection:** two tasks at the exact same time are flagged, overlaps between different pets are flagged, and tasks that only touch or are on different days are not.
- **Time budget:** tasks that don't fit are skipped with a reason while a shorter later task can still fit, and completed tasks are left out without being called "skipped".
- **Edge cases:** a pet with no tasks, an owner with no pets, invalid input (bad priority, bad time, zero duration, a task past midnight), and `edit_task()` applying all changes or none.

These tests matter because the scheduler's mistakes would be quiet: a wrong sort order or a missed overlap doesn't crash anything, it just gives the owner a bad plan. The tests use a fixed date, so they give the same result on any day.

**b. Confidence**

I'm fairly confident: about **4 out of 5**. All 21 tests pass, each feature has both normal and edge-case tests, and I also checked the demo output and the app by hand. I hold back one point because the greedy time budget isn't always the best fit, and a daily task that isn't completed doesn't carry over to the next day.

If I had more time, I would test: a daily task left incomplete overnight, many tasks overlapping in a chain, two pets with the same name, and the Streamlit app itself (currently only the backend logic has automated tests).

---

## 5. Reflection

**a. What went well**

I'm most satisfied with the scheduler logic and how clearly it explains itself. The plan doesn't just list tasks: it shows how much time each task uses, what was skipped and exactly why, and which tasks overlap. I'm also happy that the design, the code, and the UML stayed in sync through all the changes.

**b. What you would improve**

I would keep the app simpler from the start. Several features were added and later removed (date pickers, typed task types, large warning boxes), which cost time. Next time I would check each feature against the assignment before building it. I would also add saving pets and tasks to a file, so the data isn't lost when the app restarts.

**c. Key takeaway**

Being the **lead architect** means the AI writes code fast, but I have to decide what should be built. The AI tends to add more than is needed: extra features, extra files, extra options. That can make the app more confusing, not better. My job was to keep checking its work against the requirements, test it myself, say no to things that didn't belong, and ask for explanations whenever I didn't understand something I was responsible for. The best results came when I reviewed the design first and only then let the AI write the code.
