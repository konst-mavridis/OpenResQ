from pydantic import BaseModel, EmailStr

class RegisterUser(BaseModel):
    email: EmailStr
    password: str
    display_name: str | None = None

class LoginUser(BaseModel):
    email: EmailStr
    password: str
