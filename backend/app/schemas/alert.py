<<<<<<< HEAD
"""
Alert schemas for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional


class CreateAlert(BaseModel):
    """Schema for creating a new alert."""
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=1000)
    level: str = Field(default="warning")  # info, warning, critical
    
    class Config:
        example = {
            "title": "Fire Warning",
            "message": "Multiple fires reported in downtown area",
            "level": "critical"
        }


class AlertResponse(BaseModel):
    """Schema for alert response."""
    id: str
    uid: str
    title: str
    message: str
    level: str
    status: str  # active, resolved, archived
    created_at: str
    updated_at: Optional[str] = None


class UpdateAlertStatus(BaseModel):
    """Schema for updating alert status."""
    status: str = Field(..., regex="^(active|resolved|archived)$")
    
    class Config:
        example = {
            "status": "resolved"
        }

=======
from pydantic import BaseModel
from datetime import datetime

class AlertBase(BaseModel):
    type: str
    description: str | None = None
    latitude: float
    longitude: float
    severity: str = "medium"

class AlertOut(AlertBase):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True
>>>>>>> 327748fd30086a4fd58a614cd888531a2bd9417a
