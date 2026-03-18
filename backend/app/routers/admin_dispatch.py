from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict
from app.services.priority_service import set_service_priority, get_service_priority

router = APIRouter(prefix="/admin/dispatch", tags=["admin-dispatch"])

class ServicePriorityConfig(BaseModel):
    service_id: str
    priorities: Dict[str, int]


@router.post("/service-priority/set")
def api_set_service_priority(cfg: ServicePriorityConfig):
    set_service_priority(cfg.service_id, cfg.priorities)
    return {"status": "ok"}


@router.get("/service-priority/get")
def api_get_service_priority(service_id: str):
    priorities = get_service_priority(service_id)
    if not priorities:
        raise HTTPException(404, "No priorities configured")
    return {"service_id": service_id, "priorities": priorities}


@router.get("/service-priority/ai_suggest")
def ai_suggest(service_name: str):
    name = service_name.lower()

    if "fire" in name or "πυροσβε" in name:
        return {
            "priorities": {
                "fire": 1,
                "hazard": 2,
                "accident": 3,
                "flood": 4
            }
        }

    if "police" in name or "αστυνομ" in name:
        return {
            "priorities": {
                "accident": 1,
                "hazard": 2,
                "fire": 3,
                "flood": 4
            }
        }

    if "ems" in name or "ekab" in name or "εκαβ" in name:
        return {
            "priorities": {
                "medical": 1,
                "accident": 2,
                "fire": 3,
                "hazard": 4
            }
        }

    # fallback
    return {
        "priorities": {
            "fire": 1,
            "accident": 2,
            "hazard": 3,
            "flood": 4
        }
    }
