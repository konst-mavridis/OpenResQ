from fastapi import APIRouter, Depends, HTTPException, Request, Header
from pydantic import BaseModel
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


# ===== Plan Upgrade Endpoints =====

class UpgradePlanRequest(BaseModel):
    plan_id: str
    latitude: float = None
    longitude: float = None
    uid: str

class RecordUpgradeRequest(BaseModel):
    uid: str
    plan_id: str
    org_name: str = None
    admin_email: str = None
    latitude: float = None
    longitude: float = None


class UpgradeCompletedRequest(BaseModel):
    session_id: str = None
    sessionId: str = None
    plan_id: str = None
    planId: str = None
    uid: str = None
    admin_email: str = None
    adminEmail: str = None
    subscription_id: str = None
    subscriptionId: str = None
    customer_id: str = None
    customerId: str = None

@router.post("/upgrade-plan")
async def upgrade_plan(
    request_data: UpgradePlanRequest,
    authorization: str = Header(None)
):
    """
    Create a Stripe checkout session for a plan upgrade.
    Called from Next.js frontend to initiate plan upgrade.
    
    - Verifies user token
    - Gets user data from Firestore
    - Creates Stripe checkout session
    - Updates user location if provided
    - Records upgrade in backend
    
    Returns: Stripe checkout session URL
    """
    logger.info(f"Upgrade Plan API Hit for user {request_data.uid}")
    
    try:
        # Validate inputs
        if not request_data.uid:
            raise HTTPException(400, "User ID required")
        
        # Verify user token
        if not authorization:
            raise HTTPException(401, "Unauthorized - Missing token")
        
        token = authorization.replace("Bearer ", "")
        if not token:
            raise HTTPException(401, "Unauthorized - Invalid token format")
        
        auth = get_auth()
        db = get_db()
        
        try:
            decoded_token = auth.verify_id_token(token)
            token_uid = decoded_token.get("uid")
            if token_uid != request_data.uid:
                raise HTTPException(401, "Token UID does not match request UID")
        except Exception as err:
            logger.error(f"Token verification failed: {err}")
            raise HTTPException(401, "Invalid token")
        
        # Get user data from Firestore
        user_doc = db.collection("users").document(request_data.uid).get()
        if not user_doc.exists:
            raise HTTPException(404, "User not found")
        
        user_data = user_doc.to_dict()
        
        # Validate plan
        if request_data.plan_id not in PLANS:
            raise HTTPException(400, "Invalid plan ID")
        
        selected_plan = PLANS[request_data.plan_id]
        
        # Get price IDs from environment
        price_id = os.getenv(f"STRIPE_PRICE_{request_data.plan_id.upper()}")
        setup_price_id = os.getenv(f"STRIPE_PRICE_{request_data.plan_id.upper()}_SETUP")
        
        if not price_id:
            raise HTTPException(500, f"Stripe price not configured for plan {request_data.plan_id}")
        
        # Create Stripe checkout session
        line_items = [
            {
                "price": price_id,
                "quantity": 1,
            }
        ]
        
        # Add setup fee if available
        if setup_price_id:
            line_items.append({
                "price": setup_price_id,
                "quantity": 1,
            })
        
        frontend_url = os.getenv("NEXT_PUBLIC_SITE_URL", "http://localhost:3000")
        
        session = stripe.checkout.Session.create(
            customer_email=user_data.get("email"),
            payment_method_types=["card"],
            line_items=line_items,
            mode="subscription",
            success_url=f"{frontend_url}/billing?upgrade=success&session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{frontend_url}/billing",
            metadata={
                "plan_id": request_data.plan_id,
                "uid": request_data.uid,
                "org_name": user_data.get("org_name", "Unknown"),
                "admin_email": user_data.get("email"),
                "upgrade_type": "plan_upgrade",
            },
        )
        
        logger.info(f"Stripe session created: {session.id}")
        
        # Update user location in Firestore if provided
        if request_data.latitude and request_data.longitude:
            try:
                db.collection("users").document(request_data.uid).update({
                    "area": {
                        "latitude": float(request_data.latitude),
                        "longitude": float(request_data.longitude),
                        "radius_km": 20.0,
                    },
                    "last_updated": datetime.utcnow(),
                })
                logger.info(f"User location updated for upgrade")
            except Exception as loc_err:
                logger.error(f"Failed to update location: {loc_err}")
                # Don't fail the entire request
        
        # Record upgrade request in Firestore
        try:
            db.collection("upgrade_requests").add({
                "uid": request_data.uid,
                "plan_id": request_data.plan_id,
                "org_name": user_data.get("org_name"),
                "admin_email": user_data.get("email"),
                "latitude": request_data.latitude,
                "longitude": request_data.longitude,
                "stripe_session_id": session.id,
                "status": "pending",
                "created_at": datetime.utcnow(),
            })
            logger.info("Upgrade request recorded in Firestore")
        except Exception as db_err:
            logger.error(f"Failed to record upgrade in Firestore: {db_err}")
            # Continue - payment process should proceed
        
        return {"url": session.url}
        
    except HTTPException:
        raise
    except Exception as err:
        logger.error(f"Upgrade Plan Error: {err}")
        raise HTTPException(500, str(err))


@router.post("/public/record-upgrade")
async def record_upgrade(request_data: RecordUpgradeRequest):
    """
    Public endpoint to record a plan upgrade in the backend database.
    Called by Next.js after Stripe checkout is initiated.
    
    Records the upgrade request for database/analytics purposes.
    """
    logger.info(f"Recording upgrade: {request_data.uid} to {request_data.plan_id}")
    
    try:
        if not request_data.uid or not request_data.plan_id:
            raise HTTPException(400, "User ID and Plan ID required")
        
        db = get_db()
        
        # Record upgrade in upgrade_requests collection
        db.collection("upgrade_requests").add({
            "uid": request_data.uid,
            "plan_id": request_data.plan_id,
            "org_name": request_data.org_name,
            "admin_email": request_data.admin_email,
            "latitude": request_data.latitude,
            "longitude": request_data.longitude,
            "status": "pending",
            "created_at": datetime.utcnow(),
        })
        
        logger.info("Upgrade recorded in backend successfully")
        return {"status": "ok", "message": "Upgrade recorded successfully"}
        
    except Exception as err:
        logger.error(f"Failed to record upgrade: {err}")
        raise HTTPException(500, str(err))


@router.post("/public/upgrade-completed")
async def upgrade_completed(request_data: UpgradeCompletedRequest):
    """
    Public endpoint called after Stripe checkout confirms payment.
    Finalizes plan upgrade in Firestore and marks upgrade requests as completed.
    """
    try:
        session_id = request_data.session_id or request_data.sessionId
        plan_id = request_data.plan_id or request_data.planId
        uid = request_data.uid
        admin_email = request_data.admin_email or request_data.adminEmail
        subscription_id = request_data.subscription_id or request_data.subscriptionId
        customer_id = request_data.customer_id or request_data.customerId

        if not session_id:
            raise HTTPException(400, "Session ID required")

        db = get_db()

        # Resolve missing plan from previously recorded upgrade request when possible.
        if not plan_id:
            existing_request_docs = list(
                db.collection("upgrade_requests")
                .where("stripe_session_id", "==", session_id)
                .limit(1)
                .stream()
            )
            if existing_request_docs:
                plan_id = existing_request_docs[0].to_dict().get("plan_id")

        if not plan_id:
            raise HTTPException(400, "Plan ID required")

        if plan_id not in PLANS:
            raise HTTPException(400, "Invalid plan ID")

        user_data = None

        if uid:
            user_doc = db.collection("users").document(uid).get()
            if user_doc.exists:
                user_data = user_doc.to_dict()

        if not user_data and admin_email:
            user_docs = list(
                db.collection("users")
                .where("email", "==", admin_email)
                .limit(1)
                .stream()
            )
            if user_docs:
                uid = user_docs[0].id
                user_data = user_docs[0].to_dict()

        org_id = user_data.get("org_id") if user_data else None

        if not org_id and customer_id:
            org_docs = list(
                db.collection("organizations")
                .where("customer_id", "==", customer_id)
                .limit(1)
                .stream()
            )
            if org_docs:
                org_id = org_docs[0].id

        # Final fallback: query organizations directly by owner_uid
        if not org_id and uid:
            org_docs = list(
                db.collection("organizations")
                .where("owner_uid", "==", uid)
                .limit(1)
                .stream()
            )
            if org_docs:
                org_id = org_docs[0].id
                logger.info(f"Resolved org_id={org_id} via owner_uid lookup")

        org_updated = False
        if org_id:
            plan_info = PLANS[plan_id]
            org_update = {
                "plan": plan_id,
                "subscription_status": "active",
                "limits": plan_info.get("limits", {}),
                "features": plan_info.get("features", []),
                "manual_override": False,
                "updated_at": datetime.utcnow(),
            }
            if subscription_id:
                org_update["subscription_id"] = subscription_id
            if customer_id:
                org_update["customer_id"] = customer_id

            db.collection("organizations").document(org_id).set(org_update, merge=True)
            org_updated = True
            logger.info(f"Organization {org_id} updated to plan={plan_id}")
        else:
            logger.warning(f"Could not resolve org_id for uid={uid}, email={admin_email}, customer={customer_id} — org NOT updated")
            update_payload = {
                "status": "completed",
                "completed_at": datetime.utcnow(),
                "plan_id": plan_id
            }
        if uid:
            update_payload["uid"] = uid
        if admin_email:
            update_payload["admin_email"] = admin_email
        if subscription_id:
            update_payload["subscription_id"] = subscription_id

        matched_docs = list(
            db.collection("upgrade_requests")
            .where("stripe_session_id", "==", session_id)
            .stream()
        )

        if matched_docs:
            for doc in matched_docs:
                doc.reference.set(update_payload, merge=True)
        else:
            db.collection("upgrade_requests").add(
                {
                    **update_payload,
                    "stripe_session_id": session_id,
                    "created_at": datetime.utcnow(),
                }
            )

        logger.info(
            f"Upgrade completion recorded: session={session_id}, uid={uid}, plan={plan_id}, org={org_id}"
        )

        return {
            "status": "ok",
            "message": "Upgrade completion processed",
            "session_id": session_id,
            "plan_id": plan_id,
            "uid": uid,
            "org_id": org_id,
            "org_updated": org_updated,
        }
    except HTTPException:
        raise
    except Exception as err:
        logger.error(f"Failed to process upgrade completion: {err}")
        raise HTTPException(500, str(err))
