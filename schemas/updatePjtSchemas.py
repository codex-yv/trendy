from pydantic import BaseModel

class UpdateProjets(BaseModel):
    project_id:str
    status:int