from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.hazard import HazardZone
from app.schemas.hazard import HazardZoneBase, HazardZoneOut

router = APIRouter()

@router.post("/", response_model=HazardZoneOut)
def create_hazard(hazard: HazardZoneBase, db: Session = Depends(get_db)):
    new_hazard = HazardZone(**hazard.dict())
    db.add(new_hazard)
    db.commit()
    db.refresh(new_hazard)
    return new_hazard

@router.get("/", response_model=list[HazardZoneOut])
def get_hazards(db: Session = Depends(get_db)):
    return db.query(HazardZone).all()
