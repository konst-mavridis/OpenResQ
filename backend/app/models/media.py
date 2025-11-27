from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base

class Media(Base):
    __tablename__ = "media"
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"))
    url = Column(String, nullable=False)
    type = Column(String, default="image")  # image/video
