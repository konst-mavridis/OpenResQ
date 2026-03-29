from fastapi import APIRouter, Depends, HTTPException
from app.firebase_config import db
from app.utils.logger import get_logger
from firebase_admin import firestore
from app.utils.geo import haversine_distance_km
from pydantic import BaseModel 
from datetime import datetime
from app.utils.verify import verify_token

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

class ManageTeam(BaseModel):
    display_name: str
    leader_uid: str


def _get_user_display_name(user_data: dict) -> str:
    return (
        user_data.get("display_name")
        or user_data.get("displayName")
        or user_data.get("name")
        or user_data.get("email")
        or "Unknown"
    )


def _get_user_role(user_data: dict, uid: str, leader_uid: str | None) -> str:
    if leader_uid and uid == leader_uid:
        return "team_leader"
    return user_data.get("role", "responder")


def _get_user_incidents_resolved(user_doc, uid: str) -> int:
    user_data = user_doc.to_dict() or {}

    for field in ("incidents_resolved", "resolved_reports"):
        value = user_data.get(field)
        if isinstance(value, (int, float)):
            return int(value)

    stats_doc = user_doc.reference.collection("stats").document("dispatch_stats").get()
    if stats_doc.exists:
        stats_data = stats_doc.to_dict() or {}
        for field in ("incidents_resolved", "resolved_reports"):
            value = stats_data.get(field)
            if isinstance(value, (int, float)):
                return int(value)

    return 0


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


@router.get("/{team_id}")
def get_team_details(team_id: str, user=Depends(verify_token)):
    team_doc = db.collection("teams").document(team_id).get()
    if not team_doc.exists:
        raise HTTPException(status_code=404, detail="Team not found")

    team_data = team_doc.to_dict() or {}
    leader_uid = team_data.get("leader_uid")
    member_uids = set(team_data.get("members") or [])

    if leader_uid:
        member_uids.add(leader_uid)

    members = []
    leader_name = None

    for member_uid in member_uids:
        user_doc = db.collection("users").document(member_uid).get()
        if not user_doc.exists:
            continue

        member_data = user_doc.to_dict() or {}
        member_name = _get_user_display_name(member_data)

        if member_uid == leader_uid:
            leader_name = member_name

        members.append({
            "uid": member_uid,
            "name": member_name,
            "role": _get_user_role(member_data, member_uid, leader_uid),
            "incidents_resolved": _get_user_incidents_resolved(user_doc, member_uid),
        })

    members.sort(key=lambda member: (member["uid"] != leader_uid, member["name"].lower()))

    return {
        "id": team_doc.id,
        "displayName": team_data.get("displayName") or team_data.get("display_name") or team_data.get("name") or "Unnamed Team",
        "leader_uid": leader_uid,
        "leader_name": leader_name,
        "members": members,
    }


@router.post("/{team_id}/manage")
def manage_team(team_id: str, payload: ManageTeam, user=Depends(verify_token)):
    team_ref = db.collection("teams").document(team_id)
    team_doc = team_ref.get()
    
    if not team_doc.exists:
        raise HTTPException(status_code=404, detail="Team not found")
    
    team_data = team_doc.to_dict() or {}
    current_leader = team_data.get("leader_uid")
    new_leader = payload.leader_uid
    
    # Check authorization: only current leader or admin can manage team
    current_uid = user.get("uid")
    current_role = user.get("role")
    if current_uid != current_leader and current_role != "admin":
        raise HTTPException(status_code=403, detail="Only the team leader or admin can manage team settings")
    
    # Prepare update payload
    update_payload = {
        "displayName": payload.display_name,
    }
    
    # Handle leader change if needed
    if new_leader != current_leader:
        # 1) Revert old leader's role if they exist and are changing
        if current_leader:
            db.collection("users").document(current_leader).update({
                "role": "responder"
            })
        
        # 2) Update team with new leader and copy their area if available
        leader_doc = db.collection("users").document(new_leader).get()
        if not leader_doc.exists:
            raise HTTPException(status_code=404, detail="Leader user not found")
        
        leader_data = leader_doc.to_dict() or {}
        leader_area = leader_data.get("area")
        
        update_payload["leader_uid"] = new_leader
        if leader_area is not None:
            update_payload["area"] = leader_area
        
        # 3) Set new leader's role
        db.collection("users").document(new_leader).update({
            "role": "team_leader",
            "team_id": team_id
        })
    
    # Apply all updates to team
    team_ref.update(update_payload)
    
    logger.info(f"Team {team_id} updated: displayName={payload.display_name}, leader={new_leader}")
    
    return {"status": "team_updated", "team_id": team_id}

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
