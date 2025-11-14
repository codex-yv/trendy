from email import message
from pydantic import BaseModel

class DevMessage(BaseModel):
    message:str