"""
Alerts router - handles alert creation and management.
All business logic is delegated to AlertService.
"""
from fastapi import APIRouter, Depends, HTTPException
import logging
from typing import List
from app.services.alert_service import AlertService
from app.utils.verify import verify_token, require_role

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/alerts", tags=["Alerts"])
alert_service = AlertService()


@router.post("/")
async def create_alert(
    title: str,
    message: str,
    level: str = "warning",
    user=Depends(require_role("responder", "admin"))
):
    """
    Create a new alert (responder/admin only).
    
    Args:
        title: Alert title
        message: Alert message
        level: Alert level (info, warning, critical)
        user: Responder/admin user context
    
    Returns:
        Created alert with ID
    """
    if level not in ["info", "warning", "critical"]:
        raise HTTPException(status_code=400, detail="Invalid alert level")
    
    try:
        alert = alert_service.create_alert(
            user["uid"],
            title,
            message,
            level
        )
        return alert
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/")
async def get_active_alerts(user=Depends(verify_token)):
    """Get all active alerts."""
    try:
        alerts = alert_service.get_active_alerts()
        return alerts
    except Exception as e:
        logger.error(f"Failed to get alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve alerts")


@router.get("/{alert_id}")
async def get_alert(alert_id: str, user=Depends(verify_token)):
    """Get a specific alert by ID."""
    try:
        alert = alert_service.get_alert(alert_id)
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        return alert
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{alert_id}/status/{status}")
async def update_alert_status(
    alert_id: str,
    status: str,
    user=Depends(require_role("responder", "admin"))
):
    """
    Update alert status (responder/admin only).
    
    Args:
        alert_id: Alert ID
        status: New status
        user: Responder/admin user context
    
    Returns:
        Success message
    """
    valid_statuses = ["active", "resolved", "archived"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    
    try:
        alert_service.update_alert_status(alert_id, status)
        return {"message": f"Alert status updated to {status}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

