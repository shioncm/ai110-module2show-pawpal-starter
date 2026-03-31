from datetime import datetime
from pawpal_system import Task, Pet, Owner, Scheduler

# -- Tasks ---------------------------------------------------------------------
feed_morning = Task("Morning Feed", "07:00", frequency="daily")
walk_park    = Task("Park Walk", datetime(2026, 3, 31, 8, 0), frequency="daily")
annual_checkup = Task("Vet Checkup", "2026-04-15", frequency="once")
groom        = Task("Groom", "10:00", frequency="weekly")

# -- Pets ----------------------------------------------------------------------
dog = Pet("Biscuit", "Dog", age=3)
cat = Pet("Luna", "Cat", age=5)

dog.add_task(feed_morning)
dog.add_task(walk_park)
dog.add_task(annual_checkup)

cat.add_task(Task("Morning Feed", "07:30", frequency="daily"))
cat.add_task(groom)

# -- Owner & Pets --------------------------------------------------------------
alice = Owner("Alice", contact="alice@example.com")
alice.add_pet(dog)
alice.add_pet(cat)

bob = Owner("Bob", contact="555-9876")
parrot = Pet("Rio", "Parrot", age=2)
parrot.add_task(Task("Feed Seeds", "08:00", frequency="daily"))
parrot.add_task(Task("Socialise", "17:00", frequency="daily"))
bob.add_pet(parrot)

# -- Scheduler -----------------------------------------------------------------
scheduler = Scheduler()
scheduler.register_owner(alice)
scheduler.register_owner(bob)

# -- Today's Schedule ----------------------------------------------------------
print("=" * 50)
print("         TODAY'S SCHEDULE")
print("=" * 50)

for owner in scheduler.owners:
    print(f"\nOwner: {owner.name}")
    for pet in owner.pets:
        print(f"  {pet.name} ({pet.species}, age {pet.age})")
        for task in pet.tasks:
            status = "[x]" if task.is_completed else "[ ]"
            recur  = f"  ({task.frequency})" if task.is_recurring() else ""
            print(f"    {status} {task.description:<20} @ {task.time_display()}{recur}")

print()
print("-" * 50)
total   = len(scheduler.get_all_tasks())
pending = len(scheduler.get_pending_tasks())
print(f"Total tasks: {total}  |  Pending: {pending}  |  Done: {total - pending}")
print("=" * 50)
