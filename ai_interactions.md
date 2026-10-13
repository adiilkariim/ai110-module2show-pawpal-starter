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

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | | |
| **Prompt** | | |
| **Response summary** | | |
| **What was useful** | | |
| **Problems noticed** | | |
| **Decision** | | |

**Which approach did you use in your final implementation and why?**

<!-- Your conclusion -->
