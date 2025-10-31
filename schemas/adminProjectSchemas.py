from pydantic import BaseModel
from typing import List, Dict, Tuple

class Project(BaseModel):
    project_name: str
    due_date: str
    team: str
    assigned_members: List[List] # / assigned_members = [[email, name, status]]
    project_manager: List[List]
    components: Dict[str, str]