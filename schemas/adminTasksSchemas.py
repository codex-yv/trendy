from pydantic import BaseModel
from typing import List

class Task(BaseModel):
    task_name: str
    desc: str
    due_date: str
    assigned_members: List[str]