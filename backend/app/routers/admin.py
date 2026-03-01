import secrets
from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime, timedelta
from fastapi import Query
from app.firebase_config import db
from app.schemas import user
from app.services.fcm_service import send_push_to_token
from app.utils.verify import require_role
from app.schemas.report import UpdateReport
from app.utils.logger import get_logger, log_action
from app.utils.geo import haversine_distance_km
from app.utils.email import send_email

router = APIRouter(prefix="/admin", tags=["Admin"])

logger = get_logger("app.admin")
# ---------------- USERS ----------------

@router.post("/promote/{user_id}")
def promote_user(
    user_id: str,
    # admin=Depends(require_role("admin"))
):
    doc_ref = db.collection("users").document(user_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="User not found")

    doc_ref.update({
        "role": "responder",
        "updated_at": datetime.utcnow()
    })

    token = user.get("fcm_token") 
    if token: 
        send_push_to_token( token, "You are now a responder!", "An admin has approved your account.", )

    # log_action(
    #     user_id=user_id,
    #     action="promote_user",
    #     # target_id=user_id,
    #     reason="Promoted to responder"
    # )

    return {"message": "User promoted to responder"}

@router.post("/teams/create")
def create_team(payload: dict):
    name = payload["name"]
    team_ref = db.collection("teams").document()
    team_ref.set({
        "name": name,
        "leader_uid": None,
        "members": [],
        "created_at": datetime.utcnow()
    })
    return {"team_id": team_ref.id}

@router.post("/teams/{team_id}/assign_leader")
def assign_leader(team_id: str, payload: dict):
    leader_uid = payload["leader_uid"]

    team_ref = db.collection("teams").document(team_id)
    team_data = team_ref.get().to_dict()

    # 1) Remove old leader (if exists)
    old_leader = team_data.get("leader_uid")
    if old_leader and old_leader != leader_uid:
        db.collection("users").document(old_leader).update({
            "role": "responder"
        })

    # 2) Update team with new leader
    #    also copy leader's area if available
    leader_doc = db.collection("users").document(leader_uid).get()
    leader_data = leader_doc.to_dict() or {}
    leader_area = leader_data.get("area")

    update_payload = {"leader_uid": leader_uid}
    if leader_area is not None:
        update_payload["area"] = leader_area

    team_ref.update(update_payload)

    # 3) Update new leader role
    db.collection("users").document(leader_uid).update({
        "role": "team_leader",
        "team_id": team_id
    })



    return {"status": "leader_changed"}

@router.post("/responder/{user_id}/area")
def set_responder_area(
    user_id: str,
    area: dict,
    admin=Depends(require_role("admin"))
):
    doc_ref = db.collection("users").document(user_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="User not found")

    # expected area keys: lat, lng, radius_km
    doc_ref.update({
        "area": area,
        "updated_at": datetime.utcnow()
    })

    log_action(
        user_id=admin["uid"],
        action="set_responder_area",
        target_id=user_id,
        reason=f"Area set to {area}"
    )

    return {"message": "Responder area updated"}


# ---------------- REPORTS ----------------

@router.delete("/report/{report_id}")
def delete_report(
    report_id: str,
    reason: str = "No reason provided",
    hard: bool = False,
    confirm: bool = False,
    user = Depends(require_role("admin", "responder"))
):
    print("🔥 ENTERED delete_report")
    doc_ref = db.collection("reports").document(report_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Report not found")

    role = user["role"]
    delete_type = "soft"

    # Κοινά πεδία soft delete
    soft_delete_data = {
        "deleted": True,
        "deleted_at": datetime.utcnow(),
        "deleted_by": user["uid"],
        "deleted_by_role": role,
        "delete_reason": reason
    }

    # 🚨 ROLE RULES
    if role == "responder":
        # Responder → ΜΟΝΟ soft delete
        doc_ref.update(soft_delete_data)

    elif role == "admin":
        if hard:
            if not confirm:
                raise HTTPException(
                    status_code=400,
                    detail="Hard delete requires confirm=true"
                )

            # 🔒 Snapshot πριν το hard delete (audit safety)
            deleted_snapshot = doc.to_dict()

            doc_ref.delete()
            delete_type = "hard"

            # Προαιρετικό: κράτα archive
            db.collection("deleted_reports").document(report_id).set({
                **deleted_snapshot,
                "hard_deleted_at": datetime.utcnow(),
                "hard_deleted_by": user["uid"],
            })

        else:
            # Admin soft delete
            doc_ref.update(soft_delete_data)

    # 🧾 LOG (console + Firestore)
    log_action(
        logger=logger,
        action="delete_report",
        status="success",
        user_id=user["uid"],
        resource_id=report_id,
        details={
            "role": role,
            "delete_type": delete_type,
            "reason": reason
        },
    )

    return {
        "message": f"Report {delete_type} deleted",
        "deleted_by_role": role,
        "delete_type": delete_type
    }

@router.patch("/report/{report_id}")
def admin_edit_report(
    report_id: str,
    data: UpdateReport,
    admin=Depends(require_role("admin"))
):
    doc_ref = db.collection("reports").document(report_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Report not found")

    updates = data.dict(exclude_unset=True)
    updates["updated_at"] = datetime.utcnow()
    updates["updated_by"] = admin["uid"]

    doc_ref.update(updates)

    log_action(
        user_id=admin["uid"],
        action="edit_report",
        target_id=report_id,
        reason=str(updates)
    )

    return {"message": "Report updated by admin"}


@router.get("/logs")
def get_logs(
    limit: int = Query(50, ge=1, le=200),
    admin=Depends(require_role("admin"))
):
    """
    Fetch latest system logs (admin only)
    """
    try:
        logs_ref = (
            db.collection("logs")
            .order_by("timestamp", direction="DESCENDING")
            .limit(limit)
        )

        logs = []
        for doc in logs_ref.stream():
            data = doc.to_dict()
            data["id"] = doc.id

            # Firestore Timestamp → ISO
            if "timestamp" in data:
                data["timestamp"] = data["timestamp"].isoformat()

            logs.append(data)

        return logs

    except Exception as e:
        logger.error(f"Failed to fetch logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to load logs")

@router.get("/nearby-citizens")
def nearby_citizens(
    lat: float,
    lng: float,
    radius_km: float = 25,
    # admin=Depends(require_role("admin"))
):
    users_ref = db.collection("users").where("role", "==", "citizen")
    users = users_ref.stream()

    results = []

    for doc in users:
        data = doc.to_dict()
        area = data.get("area")

        if not area:
            continue

        dist = haversine_distance_km(lat, lng, area["latitude"], area["longitude"])

        if dist <= radius_km:
            results.append({
                "uid": doc.id,
                "email": data.get("email"),
                "displayName": data.get("displayName"),
                "distance": dist
            })

    return results

@router.post("/invite-responder")
def invite_responder(
    email: str, 
    # admin=Depends(require_role("admin"))
):
    email = email.lower()
    token = secrets.token_urlsafe(32)

    db.collection("invites").document(token).set({
        "email": email,
        "role": "responder",
        "created_at": datetime.utcnow().isoformat(),
        "expires_at": (datetime.utcnow() + timedelta(days=3)).isoformat()
    })

    invite_link = f"https://openresq.pages.dev/invite?token={token}"

    send_email(
        email,
        "OpenResQ Responder Invitation",
        f"""
        <h2>You are invited to join OpenResQ</h2>
        <p>Click here to register as a responder:</p>
        <a href="{invite_link}">Join Now</a>
        """
    )

    return {"success": True, "invite_link": invite_link}
