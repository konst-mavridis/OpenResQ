from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from datetime import datetime
from app.database import Base

class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    category = Column(String, nullable=False)
    description = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    status = Column(String, default="pending")  # pending/approved/rejected
    timestamp = Column(DateTime, default=datetime.utcnow)
