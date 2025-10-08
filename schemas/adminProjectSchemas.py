from pydantic import BaseModel
from typing import List, Dict, Tuple

class Project(BaseModel):
    project_name: str
    due_date: str
    team: str
    assigned_members: List[List[str]]
    project_manager: List[List[str]]
    components: Dict[str, str]