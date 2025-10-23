from pydantic import BaseModel

class NewUser(BaseModel):
    fullName: str
    email: str
    otp: str
    phone: str
    role: str
    team: str
    password: str
    skills:list
    tnp:list