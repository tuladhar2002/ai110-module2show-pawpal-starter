from pawpal_system import Task, Pet, Owner, Scheduler


# --- Setup Owner ---
owner = Owner(name="Jordan", email="jordan@pawpal.com")

# --- Setup Pets ---
mochi = Pet(name="Mochi", species="Dog", age=3)
luna = Pet(name="Luna", species="Cat", age=2)

owner.add_pet(mochi)
owner.add_pet(luna)

# --- Assign Tasks to Mochi ---
mochi.add_task(Task(
    description="Morning walk",
    time="07:00",
    frequency="daily",
    priority="high",
    duration_minutes=30,
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

# --- Assign Tasks to Luna ---
luna.add_task(Task(
    description="Clean litter box",
    time="09:30",
    frequency="daily",
    priority="medium",
    duration_minutes=10,
    assigned_pet_name="Luna",
))
luna.add_task(Task(
    description="Playtime with feather toy",
    time="18:00",
    frequency="daily",
    priority="low",
    duration_minutes=20,
    assigned_pet_name="Luna",
))

# --- Run Scheduler ---
scheduler = Scheduler(owner=owner)
scheduler.print_schedule()
