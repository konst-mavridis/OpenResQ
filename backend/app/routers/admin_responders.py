from fastapi import APIRouter, Depends, BackgroundTasks
from app.services.responder_service import ResponderService
from app.utils.verify import require_role
import logging
import asyncio

router = APIRouter(prefix="/admin/responders", tags=["Admin Responders"])

service = ResponderService()
logger = logging.getLogger(__name__)

@router.get("")
def list_responders(user=Depends(require_role("admin", "team_leader")), background_tasks: BackgroundTasks = None):
    responders = service.list_responders()
    
    async def _broadcast():
        try:
            await service.broadcast_responder_list()
        except Exception as e:
            logger.warning(f"Failed to broadcast responder list: {e}")
    
    if background_tasks:
        background_tasks.add_task(_broadcast)
    return responders

from app.dependencies.subscription import check_responder_limit

@router.post("/{uid}/add")
def add_responder(uid: str, admin=Depends(require_role("admin")), org=Depends(check_responder_limit), background_tasks: BackgroundTasks = None):
    service.add_responder(uid)
    
    async def _broadcast():
        try:
            responder = service.db.collection("users").document(uid).get().to_dict()
            await service.broadcast_responder_activated(uid, responder)
        except Exception as e:
            logger.warning(f"Failed to broadcast responder activated: {e}")
    
    if background_tasks:
        background_tasks.add_task(_broadcast)
    return {"status": "responder_added"}

@router.post("/{uid}/remove")
def remove_responder(uid: str, admin=Depends(require_role("admin")), background_tasks: BackgroundTasks = None):
    service.remove_responder(uid)
    
    async def _broadcast():
        try:
            await service.broadcast_responder_deactivated(uid)
        except Exception as e:
            logger.warning(f"Failed to broadcast responder deactivated: {e}")
    
    if background_tasks:
        background_tasks.add_task(_broadcast)
    return {"status": "responder_removed"}

@router.post("/{uid}/active/{state}")
def toggle_responder(uid: str, state: bool, admin=Depends(require_role("admin")), background_tasks: BackgroundTasks = None):
    service.toggle_active(uid, state)
    
    async def _broadcast():
        try:
            await service.broadcast_responder_list()
        except Exception as e:
            logger.warning(f"Failed to broadcast responder list: {e}")
    
    if background_tasks:
        background_tasks.add_task(_broadcast)
    return {"status": "updated", "active": state}
