from pydantic import BaseModel

class MediaBase(BaseModel):
    report_id: int
    url: str
    type: str = "image"

class MediaOut(MediaBase):
    id: int

    class Config:
        orm_mode = True
