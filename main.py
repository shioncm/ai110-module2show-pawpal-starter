from pawpal_system import Task, Pet, Owner, Scheduler

# -- Tasks (intentionally added out of chronological order) -------------------
# scheduled_time is minutes from midnight: 480 = 08:00, 420 = 07:00, etc.
feed_morning   = Task("Morning Feed",   duration_minutes=10, priority="high",   scheduled_time=420)  # 07:00
walk_park      = Task("Park Walk",      duration_minutes=30, priority="high",   scheduled_time=600)  # 10:00
annual_checkup = Task("Vet Checkup",    duration_minutes=60, priority="medium", scheduled_time=540)  # 09:00
groom          = Task("Groom",          duration_minutes=45, priority="low")                         # unscheduled

# -- Pets ----------------------------------------------------------------------
dog = Pet("Biscuit", "Dog", age=3)
cat = Pet("Luna",    "Cat", age=5)

# Added out of order on purpose: walk (10:00) before checkup (09:00) before feed (07:00)
dog.add_task(walk_park)
dog.add_task(annual_checkup)
dog.add_task(feed_morning)

cat.add_task(Task("Morning Feed", duration_minutes=10, priority="high", scheduled_time=420))  # 07:00
cat.add_task(groom)

# -- Owner & Pets --------------------------------------------------------------
alice = Owner("Alice", contact="alice@example.com")
alice.add_pet(dog)
alice.add_pet(cat)

bob    = Owner("Bob", contact="555-9876")
parrot = Pet("Rio", "Parrot", age=2)
parrot.add_task(Task("Feed Seeds", duration_minutes=5,  priority="high",   scheduled_time=480))  # 08:00
parrot.add_task(Task("Socialise",  duration_minutes=20, priority="medium", scheduled_time=660))  # 11:00
bob.add_pet(parrot)

# -- Conflict scenario: two tasks that overlap ---------------------------------
# Biscuit's "Park Walk" starts at 10:00 and runs 30 min (ends 10:30).
# "Play Fetch" starts at 10:15 — a 15-minute overlap with Park Walk.
# Rio's "Socialise" (11:00, 20 min) and "Sing Practice" (11:10, 15 min) also overlap.
play_fetch    = Task("Play Fetch",    duration_minutes=20, priority="medium", scheduled_time=615)  # 10:15
sing_practice = Task("Sing Practice", duration_minutes=15, priority="low",    scheduled_time=670)  # 11:10
dog.add_task(play_fetch)
parrot.add_task(sing_practice)

# -- Scheduler -----------------------------------------------------------------
scheduler = Scheduler()
scheduler.register_owner(alice)
scheduler.register_owner(bob)

# Mark a couple of tasks done so filtering by completion is visible
feed_morning.complete()
cat.tasks[0].complete()

# ── Demo 1: sort_tasks_by_time() ──────────────────────────────────────────────
print("=" * 55)
print("  DEMO 1 — All tasks sorted by scheduled time")
print("=" * 55)
for task in scheduler.sort_tasks_by_time():
    time_str = task.scheduled_time_str()
    status   = "[x]" if task.is_completed else "[ ]"
    print(f"  {status} {time_str:<12} {task.title:<20} {task.duration_minutes} min  [{task.priority}]")

print()
print("  — Scheduled tasks only (no unscheduled) —")
for task in scheduler.sort_tasks_by_time(include_unscheduled=False):
    time_str = task.scheduled_time_str()
    status   = "[x]" if task.is_completed else "[ ]"
    print(f"  {status} {time_str:<12} {task.title:<20} {task.duration_minutes} min  [{task.priority}]")

# ── Demo 2: filter_tasks(is_completed=False) ──────────────────────────────────
print()
print("=" * 55)
print("  DEMO 2 — Pending tasks across all pets")
print("=" * 55)
for task in scheduler.filter_tasks(is_completed=False):
    print(f"  [ ] {task.title:<20} {task.duration_minutes} min  [{task.priority}]")

# ── Demo 3: filter_tasks(is_completed=True) ───────────────────────────────────
print()
print("=" * 55)
print("  DEMO 3 — Completed tasks across all pets")
print("=" * 55)
for task in scheduler.filter_tasks(is_completed=True):
    print(f"  [x] {task.title:<20} {task.duration_minutes} min  [{task.priority}]")

# ── Demo 4: filter_tasks(pet_name=...) ───────────────────────────────────────
print()
print("=" * 55)
print("  DEMO 4 — All tasks for Biscuit (by pet name)")
print("=" * 55)
for task in scheduler.filter_tasks(pet_name="Biscuit"):
    status = "[x]" if task.is_completed else "[ ]"
    print(f"  {status} {task.title:<20} {task.duration_minutes} min  [{task.priority}]")

# ── Demo 5: filter_tasks(is_completed=False, pet_name=...) ───────────────────
print()
print("=" * 55)
print("  DEMO 5 — Pending tasks for Biscuit only")
print("=" * 55)
for task in scheduler.filter_tasks(is_completed=False, pet_name="Biscuit"):
    print(f"  [ ] {task.title:<20} {task.duration_minutes} min  [{task.priority}]")

# ── Demo 6: check_conflicts() ─────────────────────────────────────────────────
print()
print("=" * 55)
print("  DEMO 6 — Conflict detection")
print("=" * 55)
conflicts = scheduler.check_conflicts()
if conflicts:
    for warning in conflicts:
        print(f"  ⚠  {warning}")
else:
    print("  No scheduling conflicts found.")

print()
print("-" * 55)
total   = len(scheduler.get_all_tasks())
pending = len(scheduler.get_pending_tasks())
print(f"Total tasks: {total}  |  Pending: {pending}  |  Done: {total - pending}")
print("=" * 55)
