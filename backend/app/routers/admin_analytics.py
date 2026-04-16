from fastapi import APIRouter, Depends, BackgroundTasks
from app.services.analytics_service import AnalyticsService
from app.utils.verify import require_role
import logging
import asyncio

router = APIRouter(prefix="/admin/analytics", tags=["Admin Analytics"])

service = AnalyticsService()
logger = logging.getLogger(__name__)

async def _broadcast_overview():
    try:
        await service.broadcast_overview()
    except Exception as e:
        logger.warning(f"Failed to broadcast analytics overview: {e}")

@router.get("/overview")
def analytics_overview(admin=Depends(require_role("admin") | require_role("superadmin")), background_tasks: BackgroundTasks = None):
    data = service.overview()
    # Broadcast analytics overview to all admins in background
    if background_tasks:
        background_tasks.add_task(_broadcast_overview)
    return data

@router.get("/reports/last24h")
def reports_last_24h(admin=Depends(require_role("admin") | require_role("superadmin"))):
    return {
        "count": service.reports_last_24h()
    }

async def _broadcast_hazards():
    try:
        await service.broadcast_hazards()
    except Exception as e:
        logger.warning(f"Failed to broadcast analytics hazards: {e}")

@router.get("/hazards/top")
def top_hazards(admin=Depends(require_role("admin")), background_tasks: BackgroundTasks = None):
    data = {
        "hazards": service.top_hazards()
    }
    # Broadcast top hazards to all admins in background
    if background_tasks:
        background_tasks.add_task(_broadcast_hazards)
    return data

async def _broadcast_heatmap(hazard: str):
    try:
        await service.broadcast_heatmap(hazard)
    except Exception as e:
        logger.warning(f"Failed to broadcast analytics heatmap: {e}")

@router.get("/heatmap/{hazard}")
def heatmap(
    hazard: str,
    admin = Depends(require_role("admin") | require_role("superadmin")),
    background_tasks: BackgroundTasks = None
):
    data = {
        "points": service.heatmap_by_hazard(
            hazard,
            admin["uid"],
            admin["area"]["latitude"],
            admin["area"]["longitude"],
            admin["area"]["radius_km"]
        )
    }

    if background_tasks:
        background_tasks.add_task(_broadcast_heatmap, hazard)

    return data

@router.get("/stats")
def analytics_stats(admin=Depends(require_role("admin") | require_role("superadmin")), background_tasks: BackgroundTasks = None):
    """
    Get comprehensive analytics statistics.
    Combines overview, last 24h reports, and top hazards.
    """
    overview = service.overview(
        admin["uid"],
        admin["area"]["latitude"],
        admin["area"]["longitude"],
        admin["area"]["radius_km"]
    )
    reports_24h = service.reports_last_24h(admin["uid"], admin["area"]["latitude"], admin["area"]["longitude"], admin["area"]["radius_km"])
    top_hazards_list = service.top_hazards(user_id=admin["uid"], latitude=admin["area"]["latitude"], longitude=admin["area"]["longitude"], radius_km=admin["area"]["radius_km"])
    
    data = {
        "overview": overview,
        "reports_last_24h": reports_24h,
        "top_hazards": top_hazards_list
    }
    
    # Broadcast all analytics to admins in background
    async def _broadcast_stats():
        try:
            await service.broadcast_overview()
            await service.broadcast_hazards()
        except Exception as e:
            logger.warning(f"Failed to broadcast analytics stats: {e}")
    
    if background_tasks:
        background_tasks.add_task(_broadcast_stats)
    
    return data