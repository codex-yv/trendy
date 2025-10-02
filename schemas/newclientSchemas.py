from pydantic import BaseModel

class NewUser(BaseModel):
    fullName: str
    email: str
    otp: str
    phone: str
    role: str
    password: str