from pydantic import BaseModel

class Useless(BaseModel):
    x:str

class UselessClient(BaseModel):
    x:str

