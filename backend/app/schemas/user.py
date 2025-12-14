<<<<<<< HEAD
"""
User schemas for request/response validation.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class RegisterUser(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    display_name: str = Field(..., min_length=1, max_length=100)
    
    class Config:
        example = {
            "email": "user@example.com",
            "password": "secure_password_123",
            "display_name": "John Doe"
        }


class UserResponse(BaseModel):
    """Schema for user profile response."""
    uid: str
    email: str
    display_name: str
    role: str
    area: Optional[dict] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class UpdateUserArea(BaseModel):
    """Schema for updating user's area of interest."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    radius_km: float = Field(default=20.0, ge=1, le=100)
    
    class Config:
        example = {
            "latitude": 37.9838,
            "longitude": 23.7275,
            "radius_km": 20.0
        }


class UserRole(BaseModel):
    """Schema for updating user role."""
    role: str = Field(..., regex="^(citizen|responder|admin)$")
    
    class Config:
        example = {
            "role": "responder"
        }

=======
from pydantic import BaseModel, EmailStr

class RegisterUser(BaseModel):
    email: EmailStr
    password: str
    display_name: str | None = None

class LoginUser(BaseModel):
    email: EmailStr
    password: str
>>>>>>> 327748fd30086a4fd58a614cd888531a2bd9417a
