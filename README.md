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
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

test output:

```
=== Daily Schedule for Jordan's Pets ===
  [07:00] Morning walk | high priority | 30 min | daily | Pending
  [08:00] Feed breakfast | high priority | 10 min | daily | Pending
  [09:30] Clean litter box | medium priority | 10 min | daily | Pending
  [18:00] Playtime with feather toy | low priority | 20 min | daily | Pending
  (4 task(s) remaining)
```

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

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
