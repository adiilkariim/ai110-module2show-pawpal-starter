# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**Tool used:** Claude Code (agent mode in VS Code)

**What task did you give the agent?**

I asked the agent to add a third algorithmic capability, **time-budget fitting**, to the scheduler. I noticed that the owner's `available_minutes` was never compared with each task's `duration_minutes`, so the app couldn't tell the owner how their time was being used. I asked for the scheduler to fit tasks into the available time by priority and to show how much time is left for each task and for the whole day.

**What did the agent do?**

Files modified:

- `pawpal_system.py`
  - `Scheduler.filter_tasks()` now walks through the priority-sorted tasks, keeps each task that fits in the remaining minutes, and skips the rest with a reason such as "needs 20 min, only 5 min left". It keeps checking after a skip, so a shorter task later in the list can still fit.
  - `DailyPlan` got new fields: `available_minutes`, `minutes_requested`, `minutes_used`, and `minutes_remaining`, plus a `get_time_summary()` method that reports usage and how far over budget the tasks are.
  - `ScheduledTask` got `minutes_left`, a running balance shown next to each task.
  - `Scheduler.generate_plan()` fills in these values and lists skipped tasks with their pet and reason.
- `diagrams/uml.mmd`: added the new attributes and methods so the diagram matches the code.
- `reflection.md`: added the change and the reason for it to section 1b.

The agent also tested the logic against several scenarios: over budget, a task bigger than the whole budget, a budget of 0, completed tasks, and a shorter task fitting after a longer one was skipped.

**What did you have to verify or fix manually?**

- I reviewed the design before any files were changed. I had the agent show the proposed attributes and the example output in the chat first, and only approved the edit after checking it.
- I ran `python main.py` and `python -m pytest` myself to confirm the output and that all tests pass.
- In the Streamlit app, I noticed the minutes field said "today" even though a plan can be for any date, and that it allowed 0 minutes, which doesn't make sense for planning a day. I had the label changed to "per day" and the minimum changed to 1.
- I rejected an extra configuration file (`pytest.ini`) that the agent added without being asked, and deleted it, because the assignment didn't require it and `python -m pytest` works without it.
- I asked for conflict warnings in the app to be shown next to the specific field or task they're about, instead of one general warning bar.

---

## Prompt Comparison (SF11)

> Compare two different prompts (or two different models) on the same task.

**Task compared:** designing the UML class diagram for PawPal+. I gave both models the same prompt.

**Prompt (same for both):**

> I'm designing a UML class diagram for a pet-care planning app called PawPal+. The app should help an owner plan and schedule care tasks for their pet or pets, considering available time, task priority, and preferences. It should also explain why each task was selected and when it is scheduled.
>
> I have a few initial class ideas, but they are incomplete:
> Owner: name, available_minutes. Pet: name, species, and the care tasks needed by the pet. Task: title, description, priority (high, medium, or low)
>
> Please suggest improvements and any additional classes, attributes, methods, or relationships that would make the UML diagram relevant to the app and its assignment requirements. Explain how the proposed classes would work together to build and explain a daily schedule.

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | GPT 6 Luna (free chat) | Claude Opus 5.5 (medium effort) in Claude Code |
| **Prompt** | The prompt above | The same prompt above |
| **Response summary** | Kept Owner, Pet, Task, and Scheduler and added an optional `ScheduleEntry` class (task, scheduled time, start/end time, reason). Suggested `sort_by_priority_then_time()`, `filter_tasks_by_pet()`, `detect_conflicts()`, `build_daily_schedule()`, and `explain_schedule()`. Walked through how a day is built step by step, with example explanations like "Walk scheduled at 7:30 AM because it is high priority". No Mermaid code. | Based the design on the assignment requirements and said why each change earns points. Kept the four required classes and added what the rubric needs: `pets` and `get_all_tasks()` on Owner, `duration_minutes`, `time`, `due_date`, `frequency`, `completed`, and `next_occurrence()` on Task, and a Scheduler with `sort_by_time()`, `sort_by_priority()`, `filter_tasks(pet_name, completed)`, `detect_conflicts()`, `mark_task_complete()`, `build_daily_plan()`, and `explain_plan()`. Gave a ready-to-use Mermaid diagram and asked before saving any file. |
| **What was useful** | The `ScheduleEntry` idea: separating a task from its scheduled time and the reason it was picked fits the "explain why and when" requirement well. The step-by-step flow and example explanations were easy to understand. | It was tied directly to the assignment: the method names match the instructions (`sort_by_time()`, `get_all_tasks()`), it covered recurrence with `timedelta`, and it pointed out that the Scheduler must read from `get_all_tasks()` for the multi-pet point. The Mermaid code was ready to save, and it asked before creating a file. |
| **Problems noticed** | It didn't follow the assignment's specific requirements closely: no `frequency` or recurrence logic, and no `sort_by_time()` method by that name. It put `preferences` on Pet instead of Owner, put `explain_reason()` on Task, which mixes up responsibilities, and gave ScheduleEntry both `scheduled_time` and `start_time`, which overlap. The text formatting was crammed together and hard to read. | It left out a schedule-entry class to keep things simple, so the reason and time for each scheduled task had nowhere to live except inside the Scheduler. It listed `preferences` but never used them in the scheduling logic. `title` and `description` overlap, and `pet_name` on Task repeats the Pet-Task relationship. |
| **Decision** | Used as a source of ideas for explaining the plan. | Used as the main base for the design. |

**Which approach did you use in your final implementation and why?**

I mainly followed Claude's design, because it matched the assignment and the grading rubric closely: the four required classes, the method names the instructions use, `get_all_tasks()` for the multi-pet requirement, and recurrence with `due_date`, `frequency`, and `next_occurrence()`. It was also ready to turn into a Mermaid file. But I kept one good idea from Luna: a separate class for a scheduled task with its time and reason. In my final code this is `ScheduledTask` (with start time, end time, the reason it was chosen, and minutes left), inside a `DailyPlan`. That makes the "why and when" explanation clear without overloading the Scheduler. I also fixed the problems I noticed in both: preferences belong to the Owner and are actually used as a tie-breaker, and I used one `description` field instead of both `title` and `description`.
