# Stripe Webhook Setup Guide

## Overview

Webhooks allow Stripe to notify your backend when important events occur (checkout completed, subscription updated, etc.). The backend already has a webhook handler at `POST /billing/webhook`.

## Prerequisites

- Stripe account with Live and Test modes
- Backend running and publicly accessible (for production)
- `STRIPE_WEBHOOK_SECRET` environment variable configured

---

## Step 1: Get Your Backend URL

### Local Development (Testing)
If testing locally, use a tunnel service:

```bash
# Option A: Using ngrok (free)
brew install ngrok
ngrok http 8000
# Get URL like: https://1234-567-890-abc.ngrok.io

# Option B: Using localtunnel
npm install -g localtunnel
lt --port 8000
# Get URL like: https://subdomain.loca.lt

# Option C: Using Tailscale
# Configure Tailscale for secure tunneling
tailscale up
# Get your Tailscale IP for backend access
```

### Production
Use your production backend URL:
```
https://api.yourdomain.com
# or
https://your-render-app.onrender.com
# or
https://your-vercel-function.vercel.app
```

---

## Step 2: Configure Stripe Webhook Endpoint

### Via Stripe Dashboard (Manual)

1. **Go to Stripe Dashboard**
   - https://dashboard.stripe.com/webhooks

2. **Click "Add an endpoint"**

3. **Enter Endpoint URL**
   ```
   https://your-backend-url/billing/webhook
   ```
   Replace `your-backend-url` with:
   - Local dev: `https://1234-567-890-abc.ngrok.io`
   - Production: `https://api.yourdomain.com`

4. **Select Events to Listen For**
   - ✓ `checkout.session.completed`
   - ✓ `customer.subscription.updated`
   - ✓ `customer.subscription.deleted`
   - ✓ `invoice.payment_succeeded`
   - ✓ `invoice.payment_failed`

5. **Click "Add endpoint"**

6. **Copy Signing Secret**
   - Click the endpoint you just created
   - Copy the "Signing secret" (starts with `whsec_`)

### Via Stripe CLI (Development)

```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe
# or see: https://stripe.com/docs/stripe-cli

# Login to your Stripe account
stripe login

# Forward webhook events to local machine
stripe listen --events checkout.session.completed,customer.subscription.updated,customer.subscription.deleted --forward-to localhost:8000/billing/webhook

# This will output your signing secret
# Copy and save for .env file
```

---

## Step 3: Add Environment Variables

Add the webhook secret to your `.env` file:

```bash
# From Stripe Dashboard or Stripe CLI
STRIPE_WEBHOOK_SECRET=whsec_test_1234567890abcdefghijklmnopqrstuvwxyz
```

For production (replace with your production secret):
```bash
STRIPE_WEBHOOK_SECRET=whsec_live_abcdefghijklmnopqrstuvwxyz1234567890
```

---

## Step 4: Test Webhook Locally

### Using Stripe CLI

```bash
# In one terminal: Start your backend
cd /Users/kmavridis/Desktop/OpenResQ/backend
python -m uvicorn app.main:app --reload

# In another terminal: Forward Stripe events
stripe listen --events checkout.session.completed --forward-to localhost:8000/billing/webhook

# In a third terminal: Send test event
stripe trigger checkout.session.completed

# Check your backend logs for webhook processing
```

### Using Postman

1. **Get your webhook secret** from `.env`

2. **Calculate signature** (HMAC-SHA256):
   ```
   Signature = HMAC-SHA256(
     "1234567890.{request_body}",
     webhook_secret
   )
   ```

3. **Send test request**:
   ```bash
   curl -X POST http://localhost:8000/billing/webhook \
     -H "Content-Type: application/json" \
     -H "Stripe-Signature: t=1234567890,v1=CALCULATED_SIGNATURE" \
     -d '{
       "type": "checkout.session.completed",
       "data": {
         "object": {
           "id": "cs_test_123",
           "metadata": {
             "plan": "pro",
             "uid": "user_123"
           }
         }
       }
     }'
   ```

### Using Stripe Dashboard

1. **Go to Webhooks** section
2. **Click your endpoint**
3. **Scroll to "Events to send"**
4. **Click "Send test webhook"**
5. **Select event type**: `checkout.session.completed`
6. **Click "Send test event"**
7. **Check Response tab** for success/error

---

## Step 5: Verify Webhook Handler

Check that the webhook endpoint is working:

```bash
# Verify endpoint exists
curl -X OPTIONS http://localhost:8000/billing/webhook

# Should return 200 OK with CORS headers

# Or check via FastAPI docs
# http://localhost:8000/docs#/Billing/stripe_webhook_billing_webhook_post
```

---

## Webhook Events Explained

### Event: `checkout.session.completed`
**Triggered**: When customer completes checkout

**What it does**:
- Updates organization plan
- Sets subscription as active
- Stores subscription ID
- Records payment in database

**Example payload**:
```json
{
  "type": "checkout.session.completed",
  "data": {
    "object": {
      "id": "cs_test_123",
      "metadata": {
        "plan": "pro",
        "uid": "user_123"
      },
      "subscription": "sub_123",
      "amount_total": 25000
    }
  }
}
```

### Event: `customer.subscription.updated`
**Triggered**: When subscription plan changes

**What it does**:
- Updates plan in database
- Updates subscription status

### Event: `customer.subscription.deleted`
**Triggered**: When subscription is cancelled

**What it does**:
- Sets subscription status to inactive
- Downgrades to free tier

---

## Webhook Flow Diagram

```
Stripe Event Occurs
↓
Stripe sends POST to /billing/webhook
↓
Verify signature (whsec_...)
↓
Parse event type
↓
Handle checkout.session.completed
├─ Update organization plan
├─ Set subscription active
└─ Record payment
↓
Return 200 OK
```

---

## Troubleshooting

### "Invalid webhook signature"
- ✓ Verify `STRIPE_WEBHOOK_SECRET` is correct (starts with `whsec_`)
- ✓ Make sure you're using signing secret, not API key
- ✓ Check `.env` file is loaded
- ✓ Restart backend after adding secret

### Webhook not being called
- ✓ Verify endpoint URL is correct and publicly accessible
- ✓ Check Stripe dashboard shows "Enabled" status
- ✓ Look at webhook attempts log in Stripe dashboard
- ✓ For local dev, make sure ngrok tunnel is running
- ✓ Check firewall/network settings

### Backend not receiving events
- ✓ Verify backend is running
- ✓ Check logs for errors
- ✓ Ensure CORS allows Stripe IP ranges
- ✓ Use Stripe CLI to test: `stripe trigger checkout.session.completed`

### Events not persisting in database
- ✓ Check Firestore connection
- ✓ Verify Firebase credentials in `.env`
- ✓ Check Firestore security rules allow writes
- ✓ Check for errors in backend logs

---

## Testing Checklist

- [ ] Webhook secret copied to `.env`
- [ ] Webhook endpoint URL added to Stripe dashboard
- [ ] Events selected: checkout.session.completed, subscription.updated, subscription.deleted
- [ ] Backend running and accessible
- [ ] Test webhook sent from Stripe dashboard
- [ ] Backend logs show webhook processed
- [ ] Organization updated in Firestore

---

## Webhook Response Codes

| Code | Meaning |
|------|---------|
| 200 | Success - Webhook processed |
| 400 | Invalid signature or payload |
| 401 | Unauthorized (shouldn't happen) |
| 500 | Server error processing webhook |

**Important**: Always return 200 OK after validating signature. Stripe will retry on non-200 responses.

---

## Required Webhook Handlers

Currently implemented in `app/routers/billing.py`:

```python
@router.post("/webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None)):
    # Validates signature
    # Handles checkout.session.completed
    # Handles customer.subscription.deleted
    # Handles customer.subscription.updated
```

Handles these event types:
- ✓ `checkout.session.completed` - Updates plan when checkout done
- ✓ `customer.subscription.updated` - Updates subscription info
- ✓ `customer.subscription.deleted` - Cancels subscription

---

## Production Setup

### 1. Update Backend URL
```bash
# In production .env
STRIPE_WEBHOOK_SECRET=whsec_live_production_secret
```

### 2. Add Production Endpoint to Stripe
1. Go to Stripe dashboard (production mode)
2. Go to Webhooks
3. Add new endpoint with production URL
4. Copy production signing secret

### 3. Testing in Production
```bash
# Use Stripe dashboard to send test event
# Or use Stripe CLI with production account
stripe login --project-name production
stripe trigger checkout.session.completed
```

### 4. Monitor Webhooks
- **Stripe Dashboard** → Webhooks → Click endpoint → View attempts
- **Backend logs** → Check for webhook processing errors
- **Firestore** → Verify data is being updated

---

## Advanced: Custom Webhook Handler

If you need to handle additional events, modify `app/routers/billing.py`:

```python
@router.post("/webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None)):
    payload = await request.body()
    
    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, webhook_secret
        )
    except Exception as e:
        raise HTTPException(400, f"Invalid signature: {e}")
    
    event_type = event["type"]
    
    if event_type == "checkout.session.completed":
        handle_checkout_completed(event["data"]["object"])
    
    elif event_type == "customer.subscription.updated":
        handle_subscription_updated(event["data"]["object"])
    
    elif event_type == "customer.subscription.deleted":
        handle_subscription_deleted(event["data"]["object"])
    
    elif event_type == "invoice.payment_succeeded":
        handle_payment_succeeded(event["data"]["object"])
    
    return {"status": "success"}

def handle_checkout_completed(session):
    # Your custom logic
    pass
```

---

## Common Events Reference

| Event | When | What To Do |
|-------|------|-----------|
| `checkout.session.completed` | Customer finishes checkout | Update plan, activate subscription |
| `customer.subscription.updated` | Plan/billing changes | Update plan or billing info |
| `customer.subscription.deleted` | Subscription cancelled | Downgrade to free tier |
| `invoice.payment_succeeded` | Payment processed | Log payment, send receipt |
| `invoice.payment_failed` | Payment failed | Alert user, retry billing |
| `payment_intent.succeeded` | One-time charge done | Update balance |

---

## Webhook Security Best Practices

1. **Always verify signature** ✓ (Already done in code)
2. **Never trust request data** - Always verify with Stripe API
3. **Process asynchronously** - Return 200 OK immediately
4. **Handle duplicates** - Events may arrive multiple times
5. **Log all webhooks** - For debugging and auditing
6. **Set timeouts** - Don't let webhook handler hang
7. **Use HTTPS only** - Stripe won't send to HTTP endpoints

---

## Quick Setup Command

```bash
# 1. Install ngrok (for local testing)
brew install ngrok

# 2. Start ngrok
ngrok http 8000

# 3. Copy URL from output (https://xxxx-xxxx-xxx.ngrok.io)

# 4. Add to Stripe Dashboard:
# https://dashboard.stripe.com/webhooks
# Endpoint: https://YOUR_NGROK_URL/billing/webhook

# 5. Copy signing secret to .env
# STRIPE_WEBHOOK_SECRET=whsec_test_...

# 6. Start backend
python -m uvicorn app.main:app --reload

# 7. Test webhook
curl -X POST https://YOUR_NGROK_URL/billing/webhook \
  -H "Content-Type: application/json" \
  -d '{"type": "checkout.session.completed"}'
```

---

## Next Steps

1. ✓ Add webhook secret to `.env`
2. ✓ Restart backend
3. ✓ Test with Stripe CLI or dashboard
4. ✓ Monitor webhook attempts in Stripe dashboard
5. ✓ Verify Firestore data is updated
6. ✓ Deploy to production with production secret

For issues, check **Troubleshooting** section above.
