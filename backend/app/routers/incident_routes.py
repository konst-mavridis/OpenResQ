"""
DEPRECATED: This module is deprecated. Use /reports router instead.
Kept for backward compatibility during migration.
All functionality has been consolidated into the reports router.
"""
from fastapi import APIRouter, Depends, HTTPException
from app.routers.reports import create_report as _create_report_service
from app.utils.verify import verify_token

router = APIRouter()

@router.post("/incidents/")
async def create_incident(report: dict, user: dict = Depends(verify_token)):
    """
    DEPRECATED: Use POST /reports/ instead.
    This endpoint is maintained for backward compatibility only.
    """
    # Convert to reports format and call reports router
    from app.schemas.report import CreateReport
    
    try:
        report_data = CreateReport(**report)
        return await _create_report_service(report_data, user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

