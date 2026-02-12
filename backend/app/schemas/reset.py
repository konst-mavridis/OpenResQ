# app/schemas.py
from pydantic import BaseModel, EmailStr

class ResetEmailRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class OTPRequest(BaseModel): 
    email: EmailStr

class OTPVerify(BaseModel): 
    email: EmailStr 
    otp: str