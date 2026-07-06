from pawpal_system import Task, Pet, Owner, Scheduler


# --- Setup Owner ---
owner = Owner(name="Jordan", email="jordan@pawpal.com")

# --- Setup Pets ---
mochi = Pet(name="Mochi", species="Dog", age=3)
luna = Pet(name="Luna", species="Cat", age=2)

owner.add_pet(mochi)
owner.add_pet(luna)

# --- Tasks added out of order (not chronological) ---
mochi.add_task(Task(
    description="Evening medication",
    time="19:30",
    frequency="daily",
    priority="high",
    duration_minutes=5,
    assigned_pet_name="Mochi",
))
mochi.add_task(Task(
    description="Feed breakfast",
    time="08:00",
    frequency="daily",
    priority="high",
    duration_minutes=10,
    assigned_pet_name="Mochi",
))
mochi.add_task(Task(
    description="Afternoon training",
    time="14:00",
    frequency="weekly",
    priority="medium",
    duration_minutes=20,
    assigned_pet_name="Mochi",
))
mochi.add_task(Task(
    description="Morning walk",
    time="07:00",
    frequency="daily",
    priority="high",
    duration_minutes=30,
    assigned_pet_name="Mochi",
))

luna.add_task(Task(
    description="Playtime with feather toy",
    time="18:00",
    frequency="daily",
    priority="low",
    duration_minutes=20,
    assigned_pet_name="Luna",
))
luna.add_task(Task(
    description="Clean litter box",
    time="09:30",
    frequency="daily",
    priority="medium",
    duration_minutes=10,
    assigned_pet_name="Luna",
))
luna.add_task(Task(
    description="Evening brush",
    time="20:00",
    frequency="daily",
    priority="low",
    duration_minutes=10,
    assigned_pet_name="Luna",
))
luna.add_task(Task(
    description="Vet check-up",
    time="11:00",
    frequency="once",
    priority="high",
    duration_minutes=45,
    assigned_pet_name="Luna",
))

# --- Deliberate conflict A: same pet, overlapping windows ---
# "Morning walk" for Mochi starts at 07:00 for 30 min (ends 07:30).
# "Early grooming" starts at 07:15 for 20 min (ends 07:35) → overlaps.
mochi.add_task(Task(
    description="Early grooming",
    time="07:15",
    frequency="once",
    priority="medium",
    duration_minutes=20,
    assigned_pet_name="Mochi",
))

# --- Deliberate conflict B: cross-pet, owner can't be in two places ---
# Luna's "Morning stretch" starts at 07:00 for 20 min — clashes with
# Mochi's "Morning walk" (07:00–07:30) and "Early grooming" (07:15–07:35).
luna.add_task(Task(
    description="Morning stretch",
    time="07:00",
    frequency="daily",
    priority="low",
    duration_minutes=20,
    assigned_pet_name="Luna",
))

scheduler = Scheduler(owner=owner)

# --- 1. Tasks as added (insertion order, out of order) ---
print("=== Tasks as Added (insertion order) ===")
for task in owner.get_all_tasks():
    print(f"  {task}")

# --- 2. sort_by_time on all tasks ---
print("\n=== All Tasks Sorted by Time ===")
for task in scheduler.sort_by_time(owner.get_all_tasks()):
    print(f"  {task}")

# --- 3. filter_tasks: pending tasks for Mochi, sorted by time ---
print("\n=== Mochi's Pending Tasks (sorted by time) ===")
for task in scheduler.sort_by_time(scheduler.get_pending_by_pet("Mochi")):
    print(f"  {task}")

# --- 4. filter_tasks: pending tasks for Luna, sorted by time ---
print("\n=== Luna's Pending Tasks (sorted by time) ===")
for task in scheduler.sort_by_time(scheduler.get_pending_by_pet("Luna")):
    print(f"  {task}")

# --- 5. Complete a few tasks across both pets ---
print()
scheduler.complete_task(mochi.tasks[3])   # Morning walk (07:00)
scheduler.complete_task(mochi.tasks[1])   # Feed breakfast (08:00)
scheduler.complete_task(luna.tasks[1])    # Clean litter box (09:30)

# --- 6. filter_tasks: all completed tasks, sorted by time ---
print("\n=== Completed Tasks (sorted by time) ===")
for task in scheduler.sort_by_time(scheduler.get_tasks_by_status(completed=True)):
    print(f"  {task}")

# --- 7. remaining pending tasks, sorted by time ---
print("\n=== Remaining Pending Tasks (sorted by time) ===")
for task in scheduler.sort_by_time(scheduler.get_tasks_by_status(completed=False)):
    print(f"  {task}")

# --- 8. conflict warnings (lightweight — never crashes) ---
scheduler.warn_conflicts()

# --- 9. auto-spawned next occurrences ---
print("\n=== Auto-Spawned Next Occurrences (due_date set by timedelta) ===")
next_tasks = [t for t in scheduler.get_tasks_by_status(completed=False) if t.due_date]
if next_tasks:
    for task in scheduler.sort_by_time(next_tasks):
        print(f"  {task}")
else:
    print("  (none)")
