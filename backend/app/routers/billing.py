from fastapi import APIRouter, Depends, HTTPException, Request, Header
from app.dependencies.auth import get_current_user
from app.dependencies.subscription import get_current_org
from app.firebase_config import get_db
from app.constants import PLANS
import stripe
import os
from datetime import datetime

router = APIRouter(prefix="/billing", tags=["Billing"])

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
    responder_count = db.collection("responders").where("org_id", "==", org["id"]).count().get()[0].value
    
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
