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

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```

## 🧪 Testing PawPal+

```bash
python -m pytest
```

**What the tests cover:**

- **Sorting** — tasks are returned in chronological order; high-priority tasks rank above low-priority ones regardless of scheduled time
- **Recurrence** — completing a `daily` task spawns a new task for the next day; `weekly` tasks advance by 7 days; `once` tasks produce no clone; completing the same task twice does not award points a second time
- **Conflict detection** — overlapping windows on the same pet are flagged; back-to-back tasks (touching but not overlapping) are not; cross-pet overlaps are caught separately; a pet with no tasks returns an empty conflict list

**Successful test run:**

```
========================== test session starts ===========================
platform darwin -- Python 3.12.4, pytest-7.4.4, pluggy-1.0.0
rootdir: /Users/tuladhar2002/ai110-module2show-pawpal-starter
plugins: anyio-4.2.0
collected 13 items

tests/test_pawpal.py .............                                 [100%]

=========================== 13 passed in 0.01s ===========================
```

Confidence Level: ★★★★☆ (4/5)

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Sort by priority then time | `Scheduler.get_sorted_schedule()` | High-priority tasks first; ties broken by `HH:MM` |
| Sort by time only | `Scheduler.sort_by_time()` | Strict chronological order, any task list |
| Filter by pet | `Scheduler.get_tasks_by_pet()` | All tasks for a named pet regardless of status |
| Filter by status | `Scheduler.get_tasks_by_status()` | Pending or completed tasks across all pets |
| Filter pending by pet | `Scheduler.get_pending_by_pet()` | Combines pet + completion filter in one call |
| Same-pet conflict detection | `Scheduler.get_conflicts()` | Flags overlapping duration windows on the same pet |
| Cross-pet conflict detection | `Scheduler.get_cross_pet_conflicts()` | Flags windows where owner would need to be in two places |
| Combined conflict warnings | `Scheduler.warn_conflicts()` | Prints `[SAME-PET]` / `[CROSS-PET]` labels; never raises |
| Auto-schedule next occurrence | `Task.next_occurrence()` + `Scheduler.complete_task()` | Completing a daily/weekly task spawns the next one via `timedelta` |

## 📸 Demo Walkthrough

### UI Features

The Streamlit app (`app.py`) exposes four sections:

- **Owner Setup** — enter a name and email, click "Create owner" to initialise the session
- **Add a Pet** — add one or more pets (name, species, age); all pets appear in a live table
- **Schedule a Task** — pick a pet, set a description, time, priority, duration, and frequency; tasks accumulate across sessions
- **Generate Schedule** — displays the sorted schedule as a table, per-pet pending counts as metric cards, and any conflicts as labelled warning tables

### Example Workflow

1. Create owner "Jordan"
2. Add pet "Mochi" (dog, age 3) and pet "Luna" (cat, age 2)
3. Add a high-priority "Morning walk" for Mochi at 07:00 for 30 min (daily)
4. Add a medium-priority "Early grooming" for Mochi at 07:15 for 20 min — this overlaps the walk
5. Click **Generate Schedule** — Mochi's walk appears first (higher priority), and a `[SAME-PET]` conflict warning fires for the overlap
6. Mark "Morning walk" complete — the scheduler awards 20 points and auto-creates the next occurrence for tomorrow

### Key Scheduler Behaviors

| Behavior | What you see |
|---|---|
| Priority-first sort | Evening medication (high) ranks above afternoon training (medium) even though it's later in the day |
| Chronological sort | `sort_by_time()` reorders any insertion-order list into `07:00 → 08:00 → … → 20:00` |
| Same-pet conflict | `[SAME-PET]` label with both task names, times, and a suggested fix |
| Cross-pet conflict | `[CROSS-PET]` label when the owner would need to attend two pets simultaneously |
| Daily recurrence | Completing a task prints `→ Next '...' auto-scheduled for <tomorrow>` and adds it to the pet |

### Sample CLI Output (`python main.py`)

```
=== All Tasks Sorted by Time ===
  [07:00] Morning walk | high priority | 30 min | daily | Pending
  [07:00] Morning stretch | low priority | 20 min | daily | Pending
  [07:15] Early grooming | medium priority | 20 min | once | Pending
  [08:00] Feed breakfast | high priority | 10 min | daily | Pending
  [09:30] Clean litter box | medium priority | 10 min | daily | Pending
  [11:00] Vet check-up | high priority | 45 min | once | Pending
  [14:00] Afternoon training | medium priority | 20 min | weekly | Pending
  [18:00] Playtime with feather toy | low priority | 20 min | daily | Pending
  [19:30] Evening medication | high priority | 5 min | daily | Pending
  [20:00] Evening brush | low priority | 10 min | daily | Pending

Completed 'Morning walk'. +20 points! Total: 20
  → Next 'Morning walk' auto-scheduled for 2026-07-07
Completed 'Feed breakfast'. +20 points! Total: 40
  → Next 'Feed breakfast' auto-scheduled for 2026-07-07
Completed 'Clean litter box'. +10 points! Total: 50
  → Next 'Clean litter box' auto-scheduled for 2026-07-07

=== Conflict Warnings for Jordan's Schedule ===
  [SAME-PET]   Mochi: 'Early grooming' (07:15, 20min) overlaps 'Morning walk' (07:00, 30min)
  [CROSS-PET]  'Early grooming' (Mochi, 07:15, 20min) overlaps 'Morning stretch' (Luna, 07:00, 20min)
  [CROSS-PET]  'Morning walk' (Mochi, 07:00, 30min) overlaps 'Morning stretch' (Luna, 07:00, 20min)

=== Auto-Spawned Next Occurrences (due_date set by timedelta) ===
  [07:00] Morning walk | high priority | 30 min | daily | due 2026-07-07 | Pending
  [08:00] Feed breakfast | high priority | 10 min | daily | due 2026-07-07 | Pending
  [09:30] Clean litter box | medium priority | 10 min | daily | due 2026-07-07 | Pending
```
