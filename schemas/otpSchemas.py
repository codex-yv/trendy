from pydantic import BaseModel

class OTPDetails(BaseModel):
    email:str
