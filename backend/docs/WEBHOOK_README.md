# Webhook Setup Summary

## The 10-Minute Setup

### What is a Webhook?
Stripe sends HTTP POST requests to your backend when events happen (checkout completed, subscription updated, etc.)

### 3 Quick Steps

**Step 1: Get Signing Secret**
```bash
# Option A: Using Stripe CLI (easiest for local dev)
brew install stripe/stripe-cli/stripe
stripe login
stripe listen --forward-to localhost:8000/billing/webhook
# Copy the signing secret: whsec_test_...

# Option B: Using Stripe Dashboard
# Go to: https://dashboard.stripe.com/webhooks
# Add endpoint: http://localhost:8000/billing/webhook
# Copy signing secret
```

**Step 2: Add to Environment**
```bash
# Add to .env file
STRIPE_WEBHOOK_SECRET=whsec_test_your_secret_here
```

**Step 3: Restart Backend**
```bash
python -m uvicorn app.main:app --reload
```

Done! ✓

---

## Verify It Works

```bash
# Using Stripe CLI (simplest)
stripe trigger checkout.session.completed

# OR using Dashboard
# https://dashboard.stripe.com/webhooks
# Click endpoint → "Send test event"
```

Check your backend logs - should show webhook processed!

---

## File Index

| File | Purpose |
|------|---------|
| [WEBHOOK_QUICK_SETUP.md](WEBHOOK_QUICK_SETUP.md) | Ultra-quick reference (1-2 min read) |
| [WEBHOOK_SETUP.md](WEBHOOK_SETUP.md) | Complete setup guide with troubleshooting |
| [WEBHOOK_STRIPE_CLI.md](WEBHOOK_STRIPE_CLI.md) | Detailed Stripe CLI guide with examples |
| [POSTMAN_WEBHOOK_COLLECTION.md](POSTMAN_WEBHOOK_COLLECTION.md) | Postman collection for testing |

## Implementation Files

- `app/routers/billing.py` - Webhook handler (POST `/billing/webhook`)
- `.env` - Add `STRIPE_WEBHOOK_SECRET`

---

## What Gets Updated When

### Event: `checkout.session.completed`
**When**: Customer completes Stripe checkout

**What Updates**:
```python
organization:
  - plan: "pro"
  - subscription_status: "active"
  - subscription_id: "sub_..."
  - limits: {responders: 50, reports: 10000}
  
payments:
  - amount: 25.00
  - status: "paid"
  - created_at: now()
```

### Event: `customer.subscription.updated`
**When**: Subscription plan changes

**What Updates**:
```python
organization:
  - plan: "new_plan"
  - updated_at: now()
```

### Event: `customer.subscription.deleted`
**When**: Customer cancels subscription

**What Updates**:
```python
organization:
  - subscription_status: "inactive"
  - plan: "free"  # or keep current
```

---

## Local Development Workflow

```bash
# Terminal 1: Start Stripe CLI forwarding
stripe listen --forward-to localhost:8000/billing/webhook
# Copy signing secret to .env

# Terminal 2: Start backend
cd /Users/kmavridis/Desktop/OpenResQ/backend
python -m uvicorn app.main:app --reload

# Terminal 3: Test webhook
stripe trigger checkout.session.completed

# Watch Terminal 1 and 2 for webhook processing
```

---

## Testing Methods

| Method | Ease | Best For |
|--------|------|----------|
| **Stripe CLI** | ⭐⭐⭐ Easy | Local dev, quick testing |
| **Stripe Dashboard** | ⭐⭐ Medium | Verifying setup, test payloads |
| **Postman** | ⭐ Hard | Custom payloads, debugging |
| **cURL** | ⭐ Hard | Scripts, automation |

---

## Environment Variables Needed

```bash
# Required
STRIPE_SECRET_KEY=sk_test_...           # Your Stripe secret key
STRIPE_WEBHOOK_SECRET=whsec_test_...    # Added from Stripe

# Optional but recommended
STRIPE_PRICE_PRO=price_...              # For checkout
NEXT_PUBLIC_SITE_URL=http://localhost:3000
```

---

## Troubleshooting at a Glance

| Problem | Solution |
|---------|----------|
| 400 Invalid signature | Check STRIPE_WEBHOOK_SECRET in .env |
| Webhook not called | Verify endpoint URL is correct |
| Backend not responding | Make sure backend is running |
| Database not updating | Check Firestore connection |
| "Unauthorized" error | Verify webhook secret matches Stripe |

---

## Common Events You Can Test

```bash
# Subscription events
stripe trigger checkout.session.completed
stripe trigger customer.subscription.created
stripe trigger customer.subscription.updated
stripe trigger customer.subscription.deleted

# Invoice events
stripe trigger invoice.created
stripe trigger invoice.payment_succeeded
stripe trigger invoice.payment_failed

# Payment events
stripe trigger payment_intent.succeeded
stripe trigger charge.succeeded
```

---

## Production Deployment

Same steps, use production URLs:

```bash
# Login with production keys
stripe login --project-name production

# Get production signing secret
stripe listen --forward-to https://api.yourdomain.com/billing/webhook

# Add to production .env
STRIPE_WEBHOOK_SECRET=whsec_live_...
```

---

## Handler Code Location

Your webhook is handled here:
```
app/routers/billing.py
└─ @router.post("/webhook")
   └─ async def stripe_webhook(...)
      ├─ Verify signature with STRIPE_WEBHOOK_SECRET
      ├─ Parse event type
      ├─ Handle checkout.session.completed
      ├─ Handle customer.subscription.updated  
      ├─ Handle customer.subscription.deleted
      └─ Return 200 OK
```

---

## Next Steps

1. ✓ **Install Stripe CLI**: `brew install stripe/stripe-cli/stripe`
2. ✓ **Get signing secret**: `stripe listen --forward-to localhost:8000/billing/webhook`
3. ✓ **Add to .env**: `STRIPE_WEBHOOK_SECRET=whsec_test_...`
4. ✓ **Restart backend** with new .env
5. ✓ **Test**: `stripe trigger checkout.session.completed`
6. ✓ **Verify**: Check logs show webhook processed

## Questions?

- **Quick setup?** → See [WEBHOOK_QUICK_SETUP.md](WEBHOOK_QUICK_SETUP.md)
- **Detailed guide?** → See [WEBHOOK_SETUP.md](WEBHOOK_SETUP.md)
- **Stripe CLI steps?** → See [WEBHOOK_STRIPE_CLI.md](WEBHOOK_STRIPE_CLI.md)
- **Postman testing?** → See [POSTMAN_WEBHOOK_COLLECTION.md](POSTMAN_WEBHOOK_COLLECTION.md)
- **Having issues?** → See troubleshooting in WEBHOOK_SETUP.md

Done! Webhooks are now set up and ready to use. 🎉
