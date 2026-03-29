from fastapi import APIRouter, HTTPException
from app.firebase_config import db
from app.utils.logger import get_logger
from firebase_admin import firestore
from app.utils.geo import haversine_distance_km
from pydantic import BaseModel 
from datetime import datetime

router = APIRouter(prefix="/teams", tags=["Teams"])

logger = get_logger("app.teams")

class JoinRequest(BaseModel): 
    team_id: str 
    responder_uid: str 
    responder_email: str

class ApproveJoin(BaseModel): 
    request_id: str

class RejectJoin(BaseModel):
    request_id: str

@router.post("/{team_id}/add_member")
def add_member(team_id: str, payload: dict):
    uid = payload["uid"]

    team_ref = db.collection("teams").document(team_id)
    team_ref.update({
        "members": firestore.ArrayUnion([uid])
    })

    db.collection("users").document(uid).update({
        "team_id": team_id
    })

    return {"status": "member_added"}


@router.get("/nearby") 
def get_nearby_teams(lat: float, lng: float, radius_km: float = 25): 
    
    teams_ref = db.collection("teams").stream() 
    nearby = [] 
    
    for doc in teams_ref: 
        data = doc.to_dict() 
        team_id = doc.id 
        
        # 1) Προτεραιότητα: χρήση πεδίου area αν υπάρχει 
        area = data.get("area") or {}
        team_lat = area.get("latitude") or area.get("lat")
        team_lng = area.get("longitude") or area.get("lng")

        # 2) Fallback: αν δεν βρέθηκε, έλεγξε για απλά πεδία latitude/longitude 
        if team_lat is None or team_lng is None:
            team_lat = team_lat or data.get("latitude")
            team_lng = team_lng or data.get("longitude")

        # ----- NEW: FETCH LEADER INFO (To get the Name and Fallback Location) -----
        leader_name = None
        leader_uid = data.get("leader_uid") 
        if leader_uid: 
            leader_doc = db.collection("users").document(leader_uid).get() 
            if leader_doc.exists: 
                leader_data = leader_doc.to_dict() 
                
                # Automatically extract 'name', 'full_name' or 'username' depending on your schema setup
                leader_name = leader_data.get("display_name") or leader_data.get("displayName")

                # 3) Τελική ευκαιρία: πάρε το location του ηγέτη 
                if team_lat is None or team_lng is None: 
                    loc = leader_data.get("location") 
                    if loc: 
                        team_lat = loc.get("lat") 
                        team_lng = loc.get("lng") 

        # 4) Αν ακόμα δεν έχουμε location → skip 
        if team_lat is None or team_lng is None: 
            continue 

        # 5) Υπολόγισε απόσταση 
        dist = haversine_distance_km(lat, lng, team_lat, team_lng) 
        if dist <= radius_km: 
            nearby.append({ 
                "id": team_id, 
                "name": data.get("name", "Unnamed Team"), 
                "latitude": team_lat, 
                "longitude": team_lng, 
                "distance_km": round(dist, 2),
                "leader_name": leader_name  # <- Injected perfectly here!
            }) 
    return nearby

@router.post("/join_request") 
def create_join_request(req: JoinRequest): 
    team_ref = db.collection("teams").document(req.team_id).get() 
    if not team_ref.exists: 
        raise HTTPException(status_code=404, detail="Team not found") 
    db.collection("team_join_requests").add({ 
        "team_id": req.team_id, 
        "responder_uid": req.responder_uid, 
        "responder_email": req.responder_email, 
        "timestamp": datetime.utcnow() }) 
    logger.info(f"JOIN REQUEST RECEIVED: {req}")
    print(req)
    return {"status": "request_sent"}

@router.post("/approve_join") 
def approve_join(req: ApproveJoin): 
    req_ref = db.collection("team_join_requests").document(req.request_id).get() 
    if not req_ref.exists: 
        raise HTTPException(status_code=404, detail="Join request not found") 
    data = req_ref.to_dict() 
    team_id = data["team_id"] 
    responder_uid = data["responder_uid"] 
    # Update user 
    db.collection("users").document(responder_uid).update({ "team_id": team_id }) 
    # Delete request 
    db.collection("team_join_requests").document(req.request_id).delete() 
    return {"status": "approved", "team_id": team_id}

@router.post("/reject_join")
def reject_join(req: RejectJoin):
    req_ref = db.collection("team_join_requests").document(req.request_id).get()
    if not req_ref.exists:
        raise HTTPException(status_code=404, detail="Join request not found")

    db.collection("team_join_requests").document(req.request_id).delete()

    return {"status": "rejected"}

@router.get("/join_requests/{team_id}")
def get_join_requests(team_id: str):
    reqs = db.collection("team_join_requests") \
             .where("team_id", "==", team_id) \
             .stream()

    return [
        {
            "id": r.id,
            "responder_uid": r.to_dict().get("responder_uid"),
            "responder_email": r.to_dict().get("responder_email"),
            "timestamp": r.to_dict().get("timestamp")
        }
        for r in reqs
    ]
