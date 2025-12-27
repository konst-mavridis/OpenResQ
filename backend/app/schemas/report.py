"""
Report/Incident schemas for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, List


class CreateReport(BaseModel):
    """Schema for creating a new report."""
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=5000)
    event_type: str = Field(...)  # fire, flood, accident, etc.
    severity: str = Field(...)  # low, medium, high, critical
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    media: Optional[List[dict]] = Field(default_factory=list)
    deleted: bool = False
    class Config:
        example = {
            "title": "Fire in building",
            "description": "Fire on 2nd floor of apartment building",
            "event_type": "fire",
            "severity": "critical",
            "latitude": 37.9838,
            "longitude": 23.7275,
            "media": []
        }


class UpdateReport(BaseModel):
    """Schema for updating a report."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    event_type: Optional[str] = None
    severity: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    media: Optional[List[dict]] = None
    status: Optional[str] = None  # pending, in_progress, resolved, closed


class ReportResponse(BaseModel):
    """Schema for report response."""
    id: str
    uid: str
    title: str
    description: str
    event_type: str
    severity: str
    latitude: float
    longitude: float
    media: List[dict]
    status: str
    responder_notes: List[dict] = Field(default_factory=list)
    created_at: str
    updated_at: str
    deleted: bool


class ReportNote(BaseModel):
    """Schema for responder notes."""
    text: str = Field(..., min_length=1, max_length=1000)
    
    class Config:
        example = {
            "text": "Dispatched fire truck to location"
        }


class ChatMessageCreate(BaseModel):
    text: str
