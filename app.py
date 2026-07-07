import streamlit as st
from pawpal_system import Task, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ── session state vault ────────────────────────────────────────────────────
if "owner" not in st.session_state:
    st.session_state.owner = None
if "scheduler" not in st.session_state:
    st.session_state.scheduler = None

# ── 1. Owner setup ─────────────────────────────────────────────────────────
st.subheader("Owner Setup")
owner_name  = st.text_input("Owner name",  value="Jordan")
owner_email = st.text_input("Owner email", value="jordan@example.com")

if st.button("Create owner"):
    st.session_state.owner     = Owner(name=owner_name, email=owner_email)
    st.session_state.scheduler = Scheduler(owner=st.session_state.owner)
    st.success(f"Owner '{owner_name}' created.")

if st.session_state.owner:
    st.info(st.session_state.owner.get_summary())

st.divider()

# ── 2. Add a pet ───────────────────────────────────────────────────────────
st.subheader("Add a Pet")
pet_name = st.text_input("Pet name", value="Mochi")
species  = st.selectbox("Species", ["dog", "cat", "other"])
pet_age  = st.number_input("Pet age (years)", min_value=0, max_value=30, value=3)

if st.button("Add pet"):
    if st.session_state.owner is None:
        st.error("Create an owner first.")
    else:
        st.session_state.owner.add_pet(Pet(name=pet_name, species=species, age=pet_age))
        st.success(f"Added '{pet_name}' to {st.session_state.owner.name}.")

if st.session_state.owner and st.session_state.owner.pets:
    st.table([
        {"Name": p.name, "Species": p.species, "Age": p.age, "Level": p.level,
         "Tasks": len(p.tasks)}
        for p in st.session_state.owner.pets
    ])

st.divider()

# ── 3. Schedule a task ─────────────────────────────────────────────────────
st.subheader("Schedule a Task")

owner      = st.session_state.owner
pet_options = [p.name for p in owner.pets] if owner else []

if not pet_options:
    st.info("Add a pet above before scheduling tasks.")
else:
    selected_pet = st.selectbox("Assign to pet", pet_options)
    col1, col2, col3 = st.columns(3)
    with col1:
        task_desc = st.text_input("Task description", value="Morning walk")
    with col2:
        task_time = st.text_input("Time (HH:MM)", value="08:00")
    with col3:
        task_priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    col4, col5 = st.columns(2)
    with col4:
        task_duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
    with col5:
        task_freq = st.selectbox("Frequency", ["daily", "weekly", "once"])

    if st.button("Add task"):
        task = Task(
            description=task_desc,
            time=task_time,
            frequency=task_freq,
            priority=task_priority,
            duration_minutes=int(task_duration),
            assigned_pet_name=selected_pet,
        )
        for p in owner.pets:
            if p.name == selected_pet:
                p.add_task(task)
                break
        st.success(f"Task '{task_desc}' added to {selected_pet}.")

st.divider()

# ── 4. Generate schedule ───────────────────────────────────────────────────
st.subheader("Today's Schedule")

if st.button("Generate schedule"):
    if st.session_state.scheduler is None:
        st.error("Create an owner first.")
    else:
        scheduler: Scheduler = st.session_state.scheduler

        # ── sorted schedule table ──────────────────────────────────────────
        schedule = scheduler.get_sorted_schedule()   # high priority first

        if not schedule:
            st.warning("No pending tasks — all done or none added yet.")
        else:
            st.success(f"{len(schedule)} task(s) pending")
            st.table([
                {
                    "Time":     t.time,
                    "Task":     t.description,
                    "Pet":      t.assigned_pet_name,
                    "Priority": t.priority.capitalize(),
                    "Duration": f"{t.duration_minutes} min",
                    "Repeat":   t.frequency,
                }
                for t in schedule
            ])

        # ── per-pet pending summary ────────────────────────────────────────
        if st.session_state.owner and st.session_state.owner.pets:
            st.markdown("**Pending tasks by pet:**")
            cols = st.columns(len(st.session_state.owner.pets))
            for col, pet in zip(cols, st.session_state.owner.pets):
                pending = scheduler.get_pending_by_pet(pet.name)
                col.metric(label=f"{pet.name} ({pet.species})",
                           value=f"{len(pending)} task(s)")

        st.divider()

        # ── conflict warnings ──────────────────────────────────────────────
        # A conflict means the owner would need to be in two places at once,
        # so we surface it prominently with actionable detail.
        same   = scheduler.get_conflicts()
        across = scheduler.get_cross_pet_conflicts()

        if not same and not across:
            st.success("No scheduling conflicts — you're all clear!")
        else:
            total = len(same) + len(across)
            st.error(f"{total} conflict(s) detected — review before your day starts.")

            if same:
                st.markdown("**Same-pet conflicts** *(one pet, two overlapping tasks)*")
                st.table([
                    {
                        "Pet":      a.assigned_pet_name,
                        "Task A":   f"{a.description} @ {a.time} ({a.duration_minutes}min)",
                        "Task B":   f"{b.description} @ {b.time} ({b.duration_minutes}min)",
                        "Fix":      "Reschedule one task to avoid the overlap",
                    }
                    for a, b in same
                ])

            if across:
                st.markdown("**Cross-pet conflicts** *(you can't be in two places at once)*")
                st.table([
                    {
                        "Pet A":  f"{a.assigned_pet_name}",
                        "Task A": f"{a.description} @ {a.time} ({a.duration_minutes}min)",
                        "Pet B":  f"{b.assigned_pet_name}",
                        "Task B": f"{b.description} @ {b.time} ({b.duration_minutes}min)",
                        "Fix":    "Stagger start times or ask for help",
                    }
                    for a, b in across
                ])
