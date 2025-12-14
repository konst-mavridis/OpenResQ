from pydantic import BaseModel
from typing import Optional, List

class Location(BaseModel):
    latitude: float
    longitude: float

class CreateReport(BaseModel):
    title: str
    description: str
    event_type: str      # fire, flood, accident...
    severity: str        # low, medium, high
    latitude: float
    longitude: float
    media: Optional[List[str]] = []  # list of media URLs

class UpdateReport(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    event_type: Optional[str] = None
    severity: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    media: Optional[List[str]] = None
    status: Optional[str] = None  # pending, investigating, resolved
    responder_note: Optional[str] = None

class ReportResponse(BaseModel):
    id: str
    title: str
    description: str
    event_type: str
    severity: str
    latitude: float
    longitude: float
    media: Optional[List[str]] = []
    status: str
    responder_notes: Optional[List[str]] = []

    class Config:
        orm_mode = True
