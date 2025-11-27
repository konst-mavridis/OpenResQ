from pydantic import BaseModel
from datetime import datetime

class ReportBase(BaseModel):
    category: str
    description: str | None = None
    latitude: float
    longitude: float

class ReportOut(ReportBase):
    id: int
    user_id: int
    status: str
    timestamp: datetime

    class Config:
        orm_mode = True
