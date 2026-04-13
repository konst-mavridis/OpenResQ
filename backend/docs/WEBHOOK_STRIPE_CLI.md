# Webhook Setup with Stripe CLI - Visual Guide

## What is a Webhook?

```
┌──────────────┐              ┌──────────────────┐              ┌─────────────────┐
│   Customer   │              │      Stripe      │              │  Your Backend   │
│  Completes   │─────────────▶│   Processes      │─────────────▶│   Receives      │
│  Checkout    │              │   Payment        │   Webhook    │   Notification  │
└──────────────┘              └──────────────────┘              └─────────────────┘
                                                                         │
                                                                         ▼
                                                              Update database
                                                              Set plan to "pro"
```

---

## Installation

### macOS
```bash
# Using Homebrew
brew install stripe/stripe-cli/stripe

# Verify installation
stripe version
```

### Linux
```bash
# Download and install
wget https://github.com/stripe/stripe-cli/releases/download/v1.13.0/stripe_linux_x86_64.tar.gz
tar -xvf stripe_linux_x86_64.tar.gz
sudo ./stripe
sudo chmod +x /usr/local/bin/stripe
```

### Windows
```bash
# Using Homebrew (Windows)
brew install stripe/stripe-cli/stripe

# Or download from:
# https://github.com/stripe/stripe-cli/releases
```

---

## Setup Flow

### Phase 1: Login to Stripe
```bash
# Log in to your Stripe account
stripe login

# Follow browser prompt to authorize
# You'll get API credentials
```

### Phase 2: Forward Webhooks to Local Machine
```bash
# Start webhook forwarding
stripe listen --forward-to localhost:8000/billing/webhook

# Output:
# > Ready to accept webhook events from Stripe...
# > Webhook signing secret: whsec_test_abc123xyz

# COPY THIS SECRET! Add to .env file
```

### Phase 3: Start Your Backend
In another terminal:
```bash
cd /Users/kmavridis/Desktop/OpenResQ/backend

# Add signing secret to .env first
echo "STRIPE_WEBHOOK_SECRET=whsec_test_abc123xyz" >> .env

# Start backend
python -m uvicorn app.main:app --reload
```

### Phase 4: Test the Webhook
In yet another terminal:
```bash
# Send a test checkout event
stripe trigger checkout.session.completed

# Output:
# > Event created: evt_test_123abc
# > 
# > Forwarding to http://localhost:8000/billing/webhook

# Check first terminal - you should see the webhook forwarded
```

---

## Complete Terminal Session Example

```bash
# Terminal 1: Setup Stripe CLI forwarding
$ stripe login
# Opens browser, you authorize
$ stripe listen --forward-to localhost:8000/billing/webhook
> [✓] Ready to accept webhook events from Stripe...
> [✓] Webhook signing secret: whsec_test_abc123defghijk

# Terminal 2: Add secret to .env and start backend
$ cd /Users/kmavridis/Desktop/OpenResQ/backend
$ echo "STRIPE_WEBHOOK_SECRET=whsec_test_abc123defghijk" >> .env
$ python -m uvicorn app.main:app --reload
# Backend running on http://127.0.0.1:8000

# Terminal 3: Send test webhook
$ stripe trigger checkout.session.completed
> Event created evt_test_123456789
# Check Terminal 1 for "Forwarding to http://localhost:8000/billing/webhook"
```

---

## Important Commands

### Setup
```bash
stripe login                    # Authenticate with Stripe
stripe listen                   # Start listening for webhooks
stripe trigger <event>          # Send test event
```

### Testing
```bash
# Send specific test events
stripe trigger checkout.session.completed
stripe trigger customer.subscription.deleted
stripe trigger customer.subscription.updated
stripe trigger invoice.payment_succeeded
stripe trigger invoice.payment_failed
```

### Monitoring
```bash
stripe logs tail                # View real-time logs
stripe logs tail --filter=webhook  # Only webhook logs
stripe logs tail --filter=error    # Only errors
stripe logs tail --limit=50        # Last 50 events
```

### View Configuration
```bash
stripe config                   # View your configuration
stripe whoami                   # View logged in account
stripe status                   # Check webhook forwarding status
```

---

## Event Types for Testing

### Subscription Events
```bash
stripe trigger checkout.session.completed      # Customer completes payment
stripe trigger customer.subscription.created   # New subscription created
stripe trigger customer.subscription.updated   # Subscription plan changed
stripe trigger customer.subscription.deleted   # Subscription cancelled
```

### Invoice Events
```bash
stripe trigger invoice.created                 # Invoice generated
stripe trigger invoice.payment_succeeded       # Payment processed
stripe trigger invoice.payment_failed          # Payment failed
stripe trigger invoice.finalized               # Invoice ready
```

### Payment Events
```bash
stripe trigger payment_intent.created          # Payment intent created
stripe trigger payment_intent.succeeded        # Payment completed
stripe trigger payment_intent.payment_failed   # Payment failed
```

---

## Webhook Data Example

When you trigger `checkout.session.completed`, here's what gets sent:

```json
{
  "id": "evt_test_123456789",
  "object": "event",
  "api_version": "2023-10-16",
  "created": 1234567890,
  "type": "checkout.session.completed",
  "data": {
    "object": {
      "id": "cs_test_123456789",
      "object": "checkout.session",
      "billing_address_collection": null,
      "cancel_url": "http://localhost:3000/billing",
      "client_secret": null,
      "consent": null,
      "consent_collection": null,
      "currency": "usd",
      "customer": null,
      "customer_creation": null,
      "customer_email": "user@example.com",
      "expires_at": 1234567999,
      "livemode": false,
      "locale": null,
      "mode": "subscription",
      "metadata": {
        "plan_id": "pro",
        "uid": "user_123",
        "org_name": "Test Org",
        "admin_email": "admin@example.com",
        "upgrade_type": "plan_upgrade"
      },
      "payment_intent": null,
      "payment_link": null,
      "payment_method_collection": null,
      "payment_method_types": [
        "card"
      ],
      "payment_status": "attached",
      "phone_number_collection": null,
      "recovered_from": null,
      "status": "complete",
      "submit_type": null,
      "subscription": "sub_test_123",
      "success_url": "http://localhost:3000/billing?success=true",
      "total_details": null,
      "url": null
    }
  }
}
```

---

## Backend Processing

Your webhook handler processes this:

```python
@router.post("/webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None)):
    # 1. Verify signature (using STRIPE_WEBHOOK_SECRET)
    event = stripe.Webhook.construct_event(
        payload, stripe_signature, webhook_secret
    )
    
    # 2. Check event type
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        
        # 3. Extract metadata
        org_id = session["metadata"].get("org_id")
        plan = session["metadata"].get("plan")
        
        # 4. Update database
        db.collection("organizations").document(org_id).update({
            "plan": plan,
            "subscription_status": "active",
            "subscription_id": session.get("subscription"),
            "limits": PLANS[plan]["limits"],
        })
    
    # 5. Return success
    return {"status": "success"}
```

---

## Troubleshooting with Stripe CLI

### Check Webhook Status
```bash
# View last 100 webhook events
stripe logs tail --filter=webhook

# View with error filter
stripe logs tail --filter=error

# Monitor in real-time
stripe logs tail --follow
```

### Re-send Failed Webhooks
```bash
# List events
stripe events list

# Resend specific event
stripe events resend evt_test_123456789
```

### Debug Webhook Connection
```bash
# Test connectivity
stripe trigger checkout.session.completed --verbose

# This shows:
# - Event created
# - Forwarding to your URL
# - Response from your server
# - Any errors
```

---

## Deployment to Production

### Step 1: Get Production Webhook Secret
```bash
# Login with production API key
stripe login --project-name production

# Listen for production events
stripe listen --events checkout.session.completed
# Get production signing secret: whsec_live_...
```

### Step 2: Update Production .env
```bash
STRIPE_WEBHOOK_SECRET=whsec_live_production_secret_key
```

### Step 3: Add Production Endpoint in Stripe Dashboard
1. Login to Stripe production mode
2. Go to Dashboard → Webhooks
3. Add endpoint: `https://api.yourdomain.com/billing/webhook`
4. Subscribe to events
5. Copy signing secret to production .env

### Step 4: Verify Production Webhooks
```bash
# Use Stripe Dashboard to test
# Or use Stripe CLI with production account
stripe trigger checkout.session.completed --live
```

---

## Files Modified

- `app/routers/billing.py` - Webhook handler at POST `/webhook`
- `.env` - Add `STRIPE_WEBHOOK_SECRET`

---

## Next Steps

1. ✓ Install Stripe CLI: `brew install stripe/stripe-cli/stripe`
2. ✓ Login: `stripe login`
3. ✓ Forward webhooks: `stripe listen --forward-to localhost:8000/billing/webhook`
4. ✓ Copy signing secret to `.env`
5. ✓ Restart backend
6. ✓ Test: `stripe trigger checkout.session.completed`
7. ✓ Check logs in first terminal for confirmation

---

## Quick Command Reference

```bash
# Setup
stripe login
stripe listen --forward-to localhost:8000/billing/webhook

# Testing
stripe trigger checkout.session.completed
stripe logs tail

# Production
stripe login --project-name production
stripe trigger --live checkout.session.completed
```

That's it! Your webhooks are now configured.
