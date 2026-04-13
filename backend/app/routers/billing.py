from fastapi import APIRouter, Depends, HTTPException, Request, Header
from app.dependencies.auth import get_current_user
from app.dependencies.subscription import get_current_org
from app.firebase_config import get_db, get_auth
from app.constants import PLANS
import stripe
import os
import logging
from datetime import datetime

router = APIRouter(prefix="/billing", tags=["Billing"])
logger = logging.getLogger(__name__)

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

@router.post("/create-checkout-session")
async def create_checkout_session(
    plan_id: str, 
    org: dict = Depends(get_current_org)
):
    """
    Create a Stripe checkout session for a specific plan.
    """
    if plan_id not in PLANS:
        raise HTTPException(400, "Invalid plan ID")

    try:
        # Check if customer exists in Stripe, otherwise create one
        customer_id = org.get("customer_id")
        if not customer_id:
            customer = stripe.Customer.create(
                email=org.get("contact_email") or f"org_{org['id']}@openresq.com",
                metadata={"org_id": org["id"]}
            )
            customer_id = customer.id
            # Save customer_id to org
            db = get_db()
            db.collection("organizations").document(org["id"]).update({"customer_id": customer_id})

        # Create checkout session
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[{
                "price": os.getenv(f"STRIPE_PRICE_{plan_id.upper()}"),
                "quantity": 1,
            }],
            mode="subscription",
            success_url=os.getenv("FRONTEND_URL", "http://localhost:3000") + "/billing?success=true",
            cancel_url=os.getenv("FRONTEND_URL", "http://localhost:3000") + "/billing?canceled=true",
            metadata={
                "org_id": org["id"],
                "plan": plan_id
            }
        )
        return {"url": session.url}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None)):
    """
    Handle Stripe webhooks for subscription updates.
    """
    payload = await request.body()
    
    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, webhook_secret
        )
    except Exception as e:
        raise HTTPException(400, f"Invalid webhook signature: {e}")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        org_id = session["metadata"].get("org_id")
        plan = session["metadata"].get("plan")
        
        if org_id and plan:
            db = get_db()
            # Update organization
            db.collection("organizations").document(org_id).update({
                "plan": plan,
                "subscription_status": "active",
                "subscription_id": session.get("subscription"),
                "current_period_end": datetime.utcnow().timestamp() + (30 * 24 * 60 * 60), # Approx 1 month, better to get from subscription object
                "limits": PLANS[plan]["limits"],
                "manual_override": False,
                "updated_at": datetime.utcnow()
            })
            
            # Log payment
            db.collection("payments").add({
                "org_id": org_id,
                "amount": session.get("amount_total", 0) / 100,
                "currency": session.get("currency", "eur"),
                "status": "paid",
                "type": "subscription",
                "source": "stripe",
                "created_at": datetime.utcnow(),
                "stripe_session_id": session.get("id")
            })

    elif event["type"] in ["customer.subscription.deleted", "customer.subscription.updated"]:
        subscription = event["data"]["object"]
        # Handle subscription status changes
        # ... logic to update Firestore accordingly
        pass

    return {"status": "success"}

@router.get("/status")
async def get_billing_status(org: dict = Depends(get_current_org)):
    """
    Get the billing status and usage for the current organization.
    """
    plan_key = org.get("plan", "basic")
    plan_info = PLANS.get(plan_key, PLANS["basic"])
    
    # Calculate current usage
    db = get_db()
    responder_count_query = db.collection("responders").where("org_id", "==", org["id"]).count()
    responder_count_result = responder_count_query.get()
    responder_count = 0
    try:
        if responder_count_result and len(responder_count_result) > 0 and len(responder_count_result[0]) > 0:
            responder_count = int(responder_count_result[0][0].value)
    except Exception as e:
        logger.warning(f"Error getting responder count: {e}")
        pass

    
    # Mock incident count for this month (should be calculated from records)
    incident_count = 0 
    
    return {
        "plan": plan_key,
        "status": org.get("subscription_status", "inactive"),
        "current_period_end": org.get("current_period_end"),
        "manual_override": org.get("manual_override", False),
        "limits": org.get("limits", plan_info["limits"]),
        "usage": {
            "responders": responder_count,
            "incidents_this_month": incident_count
        },
        "features": plan_info["features"]
    }

@router.post("/public/record-checkout")
async def record_checkout(data: dict):
    """
    Called by the site API to record a pending organization setup after checkout initiation.
    """
    print(f"DEBUG: Recording checkout: {data}")
    customer_id = data.get("customerId")
    if not customer_id:
        raise HTTPException(400, "Customer ID required")
    
    db = get_db()
    db.collection("pending_organizations").document(customer_id).set({
        "org_name": data.get("orgName"),
        "admin_email": data.get("adminEmail"),
        "admin_name": data.get("adminName"),
        "plan_id": data.get("planId"),
        "created_at": datetime.utcnow(),
        "status": "pending_setup"
    })
    
    return {"status": "ok", "customerId": customer_id}

@router.get("/public/debug-pending")
async def debug_pending():
    """
    Debug endpoint to list all pending organizations.
    """
    db = get_db()
    docs = db.collection("pending_organizations").stream()
    pending = []
    for doc in docs:
        d = doc.to_dict()
        d["id"] = doc.id
        pending.append(d)
    return pending

@router.post("/public/verify-customer-id")
async def verify_customer_id(data: dict):
    """
    Verify if a customer ID exists and is pending setup.
    """
    customer_id = data.get("customerId")
    print(f"DEBUG: Verifying Customer ID: {customer_id}")
    db = get_db()
    doc = db.collection("pending_organizations").document(customer_id).get()
    
    if not doc.exists:
        print(f"DEBUG: Customer ID {customer_id} NOT FOUND in pending_organizations")
        raise HTTPException(404, "Invalid Customer ID")
    
    org_data = doc.to_dict()
    if org_data.get("status") != "pending_setup":
        raise HTTPException(400, "Account already set up for this ID")
        
    return {
        "orgName": org_data.get("org_name"),
        "adminEmail": org_data.get("admin_email"),
        "adminName": org_data.get("admin_name")
    }

@router.post("/public/lookup-id")
async def lookup_id(data: dict):
    """
    Look up an organization's admin email by customer ID (for return logins).
    """
    customer_id = data.get("customerId")
    db = get_db()
    
    # Search in organizations collection
    orgs = db.collection("organizations").where("customer_id", "==", customer_id).limit(1).stream()
    
    org_doc = None
    for doc in orgs:
        org_doc = doc.to_dict()
        break
        
    if not org_doc:
        raise HTTPException(404, "Customer ID not found or account not set up")
        
    # Get the owner's email
    owner_uid = org_doc.get("owner_uid")
    user_doc = db.collection("users").document(owner_uid).get()
    
    if not user_doc.exists:
        raise HTTPException(404, "Owner user not found")
        
    return {"email": user_doc.to_dict().get("email")}

@router.post("/public/setup-password")
async def setup_password(data: dict):
    """
    Create a Firebase user and organization for a customer ID.
    """
    customer_id = data.get("customerId")
    password = data.get("password")
    
    if not customer_id or not password:
        raise HTTPException(400, "Customer ID and password required")
        
    db = get_db()
    auth = get_auth()
    
    pending_ref = db.collection("pending_organizations").document(customer_id)
    pending_doc = pending_ref.get()
    
    if not pending_doc.exists:
        raise HTTPException(404, "Invalid Customer ID")
        
    org_data = pending_doc.to_dict()
    if org_data.get("status") != "pending_setup":
        raise HTTPException(400, "Account already set up")
        
    try:
        # 1. Create Firebase User
        user = auth.create_user(
            email=org_data["admin_email"],
            password=password,
            display_name=org_data["admin_name"]
        )
        
        # 2. Set custom claims (admin role)
        auth.set_custom_user_claims(user.uid, {"role": "admin"})
        
        # 3. Create Organization
        plan_id = org_data["plan_id"]
        plan_info = PLANS.get(plan_id, PLANS["basic"])
        
        org_id = f"org_{user.uid[:8]}"
        db.collection("organizations").document(org_id).set({
            "name": org_data["org_name"],
            "owner_uid": user.uid,
            "plan": plan_id,
            "subscription_status": "active",
            "limits": plan_info["limits"],
            "features": plan_info["features"],
            "created_at": datetime.utcnow(),
            "customer_id": customer_id
        })
        
        # 4. Create Admin record
        db.collection("users").document(user.uid).set({
            "email": org_data["admin_email"],
            "name": org_data["admin_name"],
            "role": "admin",
            "org_id": org_id,
            "created_at": datetime.utcnow()
        })
        
        # 5. Mark pending as completed
        pending_ref.update({"status": "completed", "completed_at": datetime.utcnow()})
        
        return {"status": "ok", "message": "Account created successfully"}
        
    except Exception as e:
        logger.error(f"Error setting up account: {e}")
        raise HTTPException(500, str(e))
