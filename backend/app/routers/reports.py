from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.report import Report
from app.schemas.report import ReportBase, ReportOut
from app.models.media import Media
import os
import uuid

router = APIRouter()

UPLOAD_DIR = "uploads/"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/", response_model=ReportOut)
def create_report(report: ReportBase, db: Session = Depends(get_db)):
    new_report = Report(**report.dict(), user_id=1)  # προσωρινό user_id
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    return new_report

@router.post("/upload/{report_id}")
def upload_media(report_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    filename = f"{uuid.uuid4()}_{file.filename}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(file.file.read())
    media = Media(report_id=report_id, url=filepath)
    db.add(media)
    db.commit()
    db.refresh(media)
    return {"url": filepath}
