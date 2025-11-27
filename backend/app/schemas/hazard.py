from pydantic import BaseModel

class HazardZoneBase(BaseModel):
    name: str
    latitude: float
    longitude: float
    type: str

class HazardZoneOut(HazardZoneBase):
    id: int

    class Config:
        orm_mode = True
