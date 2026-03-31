from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List


@dataclass
class Task:
    category: str
    priority: int
    duration: int
    date_time: datetime
    status: str

    def add(self):
        pass

    def delete(self):
        pass

    def edit(self):
        pass


@dataclass
class Pet:
    pet_type: str
    name: str
    tasks: List[Task] = field(default_factory=list)

    def add(self):
        pass

    def delete(self):
        pass

    def get_tasks(self) -> List[Task]:
        pass


class Owner:
    def __init__(self, name: str):
        self.name: str = name
        self.pets: List[Pet] = []

    def add_pet(self):
        pass

    def remove_pet(self):
        pass

    def change_name(self):
        pass


class Scheduler:
    def __init__(self, pet: Pet, date: date):
        self.tasks: List[Task] = []
        self.available_time: int = 0
        self.pet: Pet = pet
        self.date: date = date

    def generate_plan(self):
        pass

    def view_today(self):
        pass

    def get_summary(self):
        pass
