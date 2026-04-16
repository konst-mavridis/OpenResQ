from fastapi import Depends, HTTPException
from app.dependencies.auth import get_current_user
from app.firebase_config import get_db
from app.constants import PLANS
from datetime import datetime

async def get_current_org(user: dict = Depends(get_current_user)):
    """
    Dependency to get the current user's organization.
    """
    org_id = user.get("org_id")
    if not org_id:
        raise HTTPException(status_code=403, detail="User is not associated with an organization")

    db = get_db()
    org_doc = db.collection("organizations").document(org_id).get()
    
    if not org_doc.exists:
        # For development/demo purposes, we might want to create a default organization if it doesn't exist
        # logic for that can go here or we can just raise an error
        raise HTTPException(status_code=404, detail="Organization not found")

    org_data = org_doc.to_dict()
    org_data["id"] = org_id
    return org_data

def check_subscription_active(org: dict = Depends(get_current_org)):
    """
    Ensures the organization's subscription is active.
    """
    status = org.get("subscription_status")
    
    # Check if manual override is active
    if org.get("manual_override"):
        return org

    if status != "active":
        raise HTTPException(status_code=403, detail=f"Subscription is {status or 'inactive'}. Please check your billing status.")
    
    # Check if subscription has expired (Stripe)
    current_period_end = org.get("current_period_end")
    if current_period_end and current_period_end < datetime.utcnow().timestamp():
        raise HTTPException(status_code=403, detail="Subscription has expired. Please renew.")

    return org

def require_feature(feature_name: str):
    """
    Factory function to create a dependency for requiring a specific feature.
    """
    async def feature_checker(org: dict = Depends(check_subscription_active)):
        features = org.get("features") or []
        # If enterprise or manual override with 'all'
        if "all" in features:
            return org
            
        # Get standard features from plan if not explicitly in org doc
        plan_key = org.get("plan", "basic")
        plan_features = PLANS.get(plan_key, {}).get("features", [])
        
        if feature_name not in features and feature_name not in plan_features:
            raise HTTPException(
                status_code=403, 
                detail=f"The '{feature_name}' feature is not available on your {plan_key} plan. Please upgrade."
            )
        return org
    return feature_checker

async def check_responder_limit(org: dict = Depends(get_current_org)):
    """
    Dependency to check if organization has reached its responder limit.
    """
    limit = org.get("limits", {}).get("responders")
    if limit is None:
        plan_key = org.get("plan", "basic")
        limit = PLANS.get(plan_key, {}).get("limits", {}).get("responders", 10)

    db = get_db()
    current_count = db.collection("responders").where("org_id", "==", org["id"]).count().get()[0].value

    if current_count >= limit:
        raise HTTPException(
            status_code=403, 
            detail=f"Responder limit reached ({current_count}/{limit}). Please upgrade your plan."
        )
    return org

async def check_report_limit(org: dict = Depends(get_current_org)):
    """
    Dependency to check if organization has reached its reports-per-month limit.
    """
    limit = org.get("limits", {}).get("reports_per_month")
    if limit is None:
        plan_key = org.get("plan", "basic")
        limit = PLANS.get(plan_key, {}).get("limits", {}).get("reports_per_month", 1000)

    db = get_db()
    current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    report_count_query = db.collection("reports") \
        .where("org_id", "==", org["id"]) \
        .where("created_at", ">=", current_month_start).count()
    report_count_result = report_count_query.get()

    current_count = 0
    try:
        if report_count_result and len(report_count_result) > 0 and len(report_count_result[0]) > 0:
            current_count = int(report_count_result[0][0].value)
    except Exception:
        current_count = 0

    if current_count >= limit:
        raise HTTPException(
            status_code=403,
            detail=f"Monthly report limit reached ({current_count}/{limit}). Please upgrade your plan."
        )

    return org
