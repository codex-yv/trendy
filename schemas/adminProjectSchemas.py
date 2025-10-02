from pydantic import BaseModel
from typing import List, Dict

class Project(BaseModel):
    project_name: str
    due_date: str
    team: str
    assigned_members: List[str]
    project_manager: str
    components: Dict[str, str]