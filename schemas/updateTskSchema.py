from pydantic import BaseModel

class UpdateTask(BaseModel):
    task_id:str
    status:int