import datetime

import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.
"""
)

st.divider()

# ── Owner & Pet Setup ─────────────────────────────────────────────────────────
st.subheader("Owner & Pet Setup")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name   = st.text_input("Pet name",   value="Mochi")
species    = st.selectbox("Species", ["dog", "cat", "other"])

# Initialize owner, pet, and scheduler once in session state.
# The "not in" guard means these are only created on the first run,
# not wiped out every time the page re-renders.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(owner_name)
if "pet" not in st.session_state:
    st.session_state.pet = Pet(pet_name, species)
    st.session_state.owner.add_pet(st.session_state.pet)
if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler()
    st.session_state.scheduler.register_owner(st.session_state.owner)

# ── Add another pet ───────────────────────────────────────────────────────────
st.markdown("#### Add another pet")
col_a, col_b = st.columns(2)
with col_a:
    new_pet_name = st.text_input("New pet name", key="new_pet_name")
with col_b:
    new_pet_species = st.selectbox("Species", ["dog", "cat", "other"], key="new_pet_species")

if st.button("Add pet"):
    try:
        new_pet = Pet(new_pet_name, new_pet_species)
        st.session_state.owner.add_pet(new_pet)
        st.success(f"Added '{new_pet_name}' ({new_pet_species}) to {st.session_state.owner.name}.")
    except (ValueError, TypeError) as e:
        st.error(str(e))

registered_pets = st.session_state.owner.pets
st.caption(
    "Registered pets: "
    + ", ".join(f"{p.name} ({p.species})" for p in registered_pets)
)

st.divider()

# ── Add a Task ────────────────────────────────────────────────────────────────
st.subheader("Add a Task")
st.caption("Each click calls pet.add_task() on the selected pet.")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

col4, col5, col6 = st.columns(3)
with col4:
    pet_names   = [p.name for p in st.session_state.owner.pets]
    task_pet    = st.selectbox("Assign to pet", pet_names)
with col5:
    use_time = st.checkbox("Set a scheduled time")
    scheduled_time_val = None
    if use_time:
        t = st.time_input("Scheduled time", value=datetime.time(8, 0))
        scheduled_time_val = t.hour * 60 + t.minute
with col6:
    freq_choice = st.selectbox("Repeat", ["none", "daily", "weekly"])
    frequency   = None if freq_choice == "none" else freq_choice

if st.button("Add task"):
    try:
        task = Task(
            task_title,
            duration_minutes=int(duration),
            priority=priority,
            scheduled_time=scheduled_time_val,
            frequency=frequency,
        )
        target_pet = st.session_state.owner.get_pet_by_name(task_pet)
        target_pet.add_task(task)
        st.success(f"Added '{task_title}' to {task_pet} ({priority} priority, {duration} min).")
    except (ValueError, TypeError) as e:
        st.error(str(e))

st.divider()

# ── Current Tasks — sorted by scheduled time ──────────────────────────────────
st.subheader("Current Tasks")
st.caption("Sorted by scheduled time via scheduler.sort_tasks_by_time().")

include_unscheduled = st.checkbox("Include unscheduled tasks", value=True)
sorted_tasks = st.session_state.scheduler.sort_tasks_by_time(
    include_unscheduled=include_unscheduled
)

if sorted_tasks:
    # Build a lookup so we can label each task with its pet's name.
    task_to_pet: dict = {}
    for pet in st.session_state.owner.pets:
        for t in pet.tasks:
            task_to_pet[id(t)] = pet.name

    st.table([
        {
            "pet":      task_to_pet.get(id(t), "—"),
            "time":     t.scheduled_time_str(),
            "title":    t.title,
            "duration": f"{t.duration_minutes} min",
            "priority": t.priority,
            "repeats":  t.frequency or "—",
            "status":   "✓ done" if t.is_completed else "pending",
        }
        for t in sorted_tasks
    ])

    # ── Conflict warnings — calls scheduler.check_conflicts() ─────────────────
    conflicts = st.session_state.scheduler.check_conflicts()
    if conflicts:
        for warning in conflicts:
            st.warning(warning)
    else:
        st.success("No scheduling conflicts detected.")
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# ── Mark Task Complete ────────────────────────────────────────────────────────
st.subheader("Mark Task Complete")
st.caption("Calls scheduler.complete_task(). Recurring tasks auto-generate the next occurrence.")

pending = st.session_state.scheduler.filter_tasks(is_completed=False)
if pending:
    # Include pet name in each label so the user can tell tasks apart.
    task_labels = {}
    for pet in st.session_state.owner.pets:
        for t in pet.get_pending_tasks():
            label = f"{t.scheduled_time_str()} — {t.title} [{pet.name}] ({t.priority})"
            task_labels[label] = t

    selected_label = st.selectbox("Select a pending task", list(task_labels.keys()))

    if st.button("Mark as complete"):
        selected_task = task_labels[selected_label]
        next_task = st.session_state.scheduler.complete_task(selected_task)
        if next_task:
            st.success(
                f"'{selected_task.title}' marked complete. "
                f"Next occurrence added for {next_task.due_date}."
            )
        else:
            st.success(f"'{selected_task.title}' marked complete.")
else:
    st.info("No pending tasks — all done!")

st.divider()

# ── Build Schedule — filtered view ────────────────────────────────────────────
st.subheader("Build Schedule")
st.caption(
    "Uses scheduler.filter_tasks(is_completed, pet_name) then sorts results by time."
)

col_f1, col_f2 = st.columns(2)
with col_f1:
    filter_choice = st.radio(
        "Show tasks",
        ["All", "Pending only", "Completed only"],
        horizontal=True,
    )
with col_f2:
    pet_options   = ["All pets"] + [p.name for p in st.session_state.owner.pets]
    pet_filter    = st.selectbox("Filter by pet", pet_options)
    pet_name_filter = None if pet_filter == "All pets" else pet_filter

if st.button("Generate schedule"):
    is_completed_filter = None
    if filter_choice == "Pending only":
        is_completed_filter = False
    elif filter_choice == "Completed only":
        is_completed_filter = True

    try:
        filtered = st.session_state.scheduler.filter_tasks(
            is_completed=is_completed_filter,
            pet_name=pet_name_filter,
        )
    except ValueError as e:
        st.error(str(e))
        filtered = []

    # Sort the filtered results by scheduled time — mirrors main.py Demo 1+2 combined.
    filtered_sorted = sorted(
        filtered,
        key=lambda t: (t.scheduled_time is None, t.scheduled_time or 0),
    )

    if filtered_sorted:
        st.table([
            {
                "time":     t.scheduled_time_str(),
                "title":    t.title,
                "duration": f"{t.duration_minutes} min",
                "priority": t.priority,
                "status":   "✓ done" if t.is_completed else "pending",
            }
            for t in filtered_sorted
        ])
        total = len(filtered_sorted)
        done  = sum(1 for t in filtered_sorted if t.is_completed)
        st.caption(f"{total} task(s) shown — {done} completed, {total - done} pending.")
    else:
        st.info("No tasks match the selected filter.")
