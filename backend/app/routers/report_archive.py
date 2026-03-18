from fastapi import APIRouter
from app.services.report_archiver import archive_old_reports

router = APIRouter(prefix="/cron", tags=["Cron"])

@router.get("/archive-reports")
def run_archive():
    archive_old_reports()
    return {"status": "ok", "message": "Archived old reports"}
