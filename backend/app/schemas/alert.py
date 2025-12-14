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
