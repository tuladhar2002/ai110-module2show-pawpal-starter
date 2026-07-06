import streamlit as st
from pawpal_system import Task, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# --- session state vault ---------------------------------------------------
# Each key is checked with "not in" so the object is created only once.
# Streamlit reruns the entire script on every interaction; the guard prevents
# overwriting data the user has already entered.
if "owner" not in st.session_state:
    st.session_state.owner = None
if "scheduler" not in st.session_state:
    st.session_state.scheduler = None
# --------------------------------------------------------------------------

# ── 1. Owner setup ─────────────────────────────────────────────────────────
st.subheader("Owner Setup")
owner_name = st.text_input("Owner name", value="Jordan")
owner_email = st.text_input("Owner email", value="jordan@example.com")

if st.button("Create owner"):
    st.session_state.owner = Owner(name=owner_name, email=owner_email)
    st.session_state.scheduler = Scheduler(owner=st.session_state.owner)
    st.success(f"Owner '{owner_name}' created.")

if st.session_state.owner:
    st.info(st.session_state.owner.get_summary())

st.divider()

# ── 2. Add a pet ───────────────────────────────────────────────────────────
# When the form is submitted:
#   1. A Pet instance is built from the form values.
#   2. owner.add_pet(pet) appends it to owner.pets  ← the key method call.
#   3. Streamlit reruns; the pet list below re-renders automatically because
#      st.session_state.owner now has one more pet in its .pets list.
st.subheader("Add a Pet")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])
pet_age = st.number_input("Pet age (years)", min_value=0, max_value=30, value=3)

if st.button("Add pet"):
    if st.session_state.owner is None:
        st.error("Create an owner first.")
    else:
        pet = Pet(name=pet_name, species=species, age=pet_age)
        st.session_state.owner.add_pet(pet)          # Owner.add_pet() does the work
        st.success(f"Added pet '{pet_name}' to {st.session_state.owner.name}.")

if st.session_state.owner and st.session_state.owner.pets:
    st.write("**Pets on file:**")
    for p in st.session_state.owner.pets:
        st.markdown(f"- {p.get_info()}")

st.divider()

# ── 3. Schedule a task ─────────────────────────────────────────────────────
st.subheader("Schedule a Task")

owner = st.session_state.owner
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
        # find the matching Pet and call Pet.add_task()
        for p in owner.pets:
            if p.name == selected_pet:
                p.add_task(task)
                break
        st.success(f"Task '{task_desc}' added to {selected_pet}.")

st.divider()

# ── 4. Generate schedule ───────────────────────────────────────────────────
st.subheader("Generate Schedule")

if st.button("Generate schedule"):
    if st.session_state.scheduler is None:
        st.error("Create an owner first.")
    else:
        scheduler: Scheduler = st.session_state.scheduler
        schedule = scheduler.get_sorted_schedule()

        if not schedule:
            st.warning("No pending tasks to schedule.")
        else:
            st.success(f"{len(schedule)} task(s) — high priority first:")
            for task in schedule:
                st.markdown(f"- `{task}`")

        conflicts = scheduler.get_conflicts()
        if conflicts:
            st.error("Conflicts detected:")
            for a, b in conflicts:
                st.markdown(
                    f"- **{a.assigned_pet_name}**: '{a.description}' "
                    f"({a.time}, {a.duration_minutes}min) overlaps "
                    f"'{b.description}' ({b.time}, {b.duration_minutes}min)"
                )
        else:
            st.info("No scheduling conflicts.")
