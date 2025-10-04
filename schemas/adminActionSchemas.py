from pydantic import BaseModel

class AdminAction(BaseModel):
    email:str
    action:int
