from fastapi import APIRouter, HTTPException, Query
from firebase_admin import firestore
import logging
from app.services.report_service import ReportService
from datetime import datetime
from app.firebase_config import get_db

router = APIRouter(prefix="/responders", tags=["responders"])
logger = logging.getLogger(__name__)
service = ReportService()
db = get_db()


@router.post("/{uid}/on_duty")
def set_responder_on_duty(uid: str):
    doc = db.collection("users").document(uid).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Responder not found")

    data = doc.to_dict()
    if data.get("role") != "responder":
        raise HTTPException(status_code=400, detail="User is not a responder")

    db.collection("users").document(uid).update({
        "on_duty": True,
        "last_active": datetime.utcnow()
    })

    return {"uid": uid, "on_duty": True}


@router.post("/{uid}/off_duty")
def set_responder_off_duty(uid: str):
    doc = db.collection("users").document(uid).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Responder not found")

    data = doc.to_dict()
    if data.get("role") != "responder":
        raise HTTPException(status_code=400, detail="User is not a responder")

    db.collection("users").document(uid).update({
        "on_duty": False,
        "area": firestore.DELETE_FIELD,
        "last_active": datetime.utcnow()
    })

    return {"uid": uid, "on_duty": False}


@router.get("/on_duty")
def get_on_duty_responders():
    docs = db.collection("users") \
        .where("role", "==", "responder") \
        .where("on_duty", "==", True) \
        .stream()

    responders = []
    for d in docs:
        data = d.to_dict()
        data["uid"] = d.id
        responders.append(data)

    return {"responders": responders}


@router.get("/nearby")
def get_nearby_responders(
    admin_lat: float = Query(...),
    admin_lng: float = Query(...),
    radius_km: float = 20
):
    docs = db.collection("users") \
        .where("role", "==", "responder") \
        .where("on_duty", "==", True) \
        .stream()

    responders = []
    for d in docs:
        data = d.to_dict()
        area = data.get("area", {})

        lat = area.get("latitude")
        lng = area.get("longitude")

        if lat is None or lng is None:
            continue

        dist = service.haversine_distance(admin_lat, admin_lng, lat, lng)
        if dist <= radius_km:
            data["uid"] = d.id
            data["distance_km"] = dist
            responders.append(data)

    return {"responders": responders}


@router.post("/update_area")
def update_area(uid: str, latitude: float, longitude: float, radius_km: float):
    doc = db.collection("users").document(uid).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Responder not found")

    data = doc.to_dict()
    if not data.get("on_duty", False):
        raise HTTPException(status_code=400, detail="Responder is OFF DUTY")

    db.collection("users").document(uid).update({
        "area": {
            "latitude": latitude,
            "longitude": longitude,
            "radius_km": radius_km
        },
        "last_active": datetime.utcnow()
    })

    return {"status": "ok"}
