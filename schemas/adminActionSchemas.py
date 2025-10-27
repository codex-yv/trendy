from pydantic import BaseModel

class AdminAction(BaseModel):
    email:str
    action:int # action {-1:Pending, 0:Rejected, 1:Approved}
