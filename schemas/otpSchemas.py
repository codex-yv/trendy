from pydantic import BaseModel

class OTPDetails(BaseModel):
    email:str

class Email(BaseModel):
    email:str