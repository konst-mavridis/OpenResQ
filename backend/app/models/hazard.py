from sqlalchemy import Column, Integer, String, Float
from app.database import Base

class HazardZone(Base):
    __tablename__ = "hazard_zones"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    type = Column(String)  # flood, fire, earthquake, etc.
