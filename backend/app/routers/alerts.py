from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.alert import Alert
from app.schemas.alert import AlertBase, AlertOut

router = APIRouter()

@router.post("/", response_model=AlertOut)
def create_alert(alert: AlertBase, db: Session = Depends(get_db)):
    new_alert = Alert(**alert.dict())
    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)
    return new_alert

@router.get("/", response_model=list[AlertOut])
def get_alerts(db: Session = Depends(get_db)):
    return db.query(Alert).all()
