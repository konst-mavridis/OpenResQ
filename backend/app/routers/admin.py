from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.report import Report
from app.schemas.report import ReportOut

router = APIRouter()

@router.get("/reports", response_model=list[ReportOut])
def all_reports(db: Session = Depends(get_db)):
    return db.query(Report).all()

@router.put("/reports/{report_id}/status")
def update_report_status(report_id: int, status: str, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    report.status = status
    db.commit()
    db.refresh(report)
    return report
