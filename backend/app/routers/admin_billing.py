from fastapi import APIRouter, Depends, HTTPException
from app.firebase_config import get_db
from app.utils.verify import require_role
from app.constants import PLANS
from datetime import datetime, timedelta

router = APIRouter(prefix="/superadmin/billing", tags=["Admin Billing"])

@router.get("/organizations")
async def list_organizations(
    limit: int = 50,
    admin=Depends(require_role("superadmin")) # or "superadmin" if you have that role
):
    """
    List all organizations with their subscription status.
    """
    db = get_db()
    orgs_ref = db.collection("organizations").limit(limit).stream()
    
    orgs = []
    for doc in orgs_ref:
        data = doc.to_dict()
        data["id"] = doc.id
        orgs.append(data)
        
    return orgs

@router.get("/organizations/{org_id}")
async def get_organization_details(
    org_id: str,
    admin=Depends(require_role("superadmin"))
):
    """
    Get detailed subscription and usage info for an organization.
    """
    db = get_db()
    org_doc = db.collection("organizations").document(org_id).get()
    
    if not org_doc.exists:
        raise HTTPException(404, "Organization not found")
        
    org_data = org_doc.to_dict()
    org_data["id"] = org_id
    
    # Get payments history
    payments_ref = db.collection("payments").where("org_id", "==", org_id).order_by("created_at", direction="DESCENDING").limit(10).stream()
    payments = [doc.to_dict() for doc in payments_ref]
    org_data["payments"] = payments
    
    return org_data

@router.post("/organizations/{org_id}/subscription")
async def update_org_subscription(
    org_id: str,
    data: dict,
    admin=Depends(require_role("superadmin"))
):
    """
    Manually update an organization's subscription plan and limits.
    """
    plan = data.get("plan")
    if plan and plan not in PLANS and plan != "custom":
        raise HTTPException(400, "Invalid plan")
        
    db = get_db()
    org_ref = db.collection("organizations").document(org_id)
    
    if not org_ref.get().exists:
        raise HTTPException(404, "Organization not found")
        
    update_data = {
        "updated_at": datetime.utcnow(),
        "updated_by": admin["uid"],
        "manual_override": True
    }
    
    if plan:
        update_data["plan"] = plan
        if plan in PLANS:
            update_data["limits"] = PLANS[plan]["limits"]
            update_data["features"] = PLANS[plan]["features"]
            update_data["subscription_status"] = "active"
            
    # Allow explicit limit overrides
    if "limits" in data:
        update_data["limits"] = data["limits"]
        
    if "subscription_status" in data:
        update_data["subscription_status"] = data["subscription_status"]
        
    if "current_period_end" in data:
        # Expecting timestamp or ISO string
        val = data["current_period_end"]
        if isinstance(val, (int, float)):
            update_data["current_period_end"] = val
        else:
            try:
                update_data["current_period_end"] = datetime.fromisoformat(val).timestamp()
            except:
                pass

    org_ref.update(update_data)
    
    # Log the manual override payment (if amount provided)
    if data.get("amount"):
        db.collection("payments").add({
            "org_id": org_id,
            "amount": data.get("amount"),
            "currency": data.get("currency", "eur"),
            "status": "paid",
            "type": "subscription",
            "source": "manual",
            "created_at": datetime.utcnow(),
            "notes": data.get("notes", "Manual activation by admin")
        })

    return {"status": "ok", "message": "Organization subscription updated"}
