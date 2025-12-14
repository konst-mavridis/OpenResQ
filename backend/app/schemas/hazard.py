from pydantic import BaseModel

class HazardCreate(BaseModel):
    type: str
    description: str
    location: dict
    severity: str  # low, medium, high
