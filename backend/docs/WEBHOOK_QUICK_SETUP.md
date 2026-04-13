# Webhook Setup Quick Reference

## 3-Step Webhook Setup

### Step 1: Get Backend URL
```bash
# Local development (use ngrok)
brew install ngrok
ngrok http 8000
# Output: https://1234-567-890-abc.ngrok.io

# OR use Stripe CLI
stripe listen --forward-to localhost:8000/billing/webhook
```

### Step 2: Configure in Stripe Dashboard
1. Go to: https://dashboard.stripe.com/webhooks
2. Click "Add an endpoint"
3. Enter URL: `https://YOUR_URL/billing/webhook`
4. Select events:
   - ✓ `checkout.session.completed`
   - ✓ `customer.subscription.updated`
   - ✓ `customer.subscription.deleted`
5. Click "Add endpoint"
6. Copy "Signing secret" (whsec_...)

### Step 3: Add to .env
```bash
STRIPE_WEBHOOK_SECRET=whsec_test_your_secret_here
```

Restart backend and you're done!

---

## Test Your Webhook

**Option A: Stripe CLI**
```bash
stripe trigger checkout.session.completed
```

**Option B: Stripe Dashboard**
1. Go to Webhooks
2. Click your endpoint
3. Click "Send test event"
4. Select event type
5. Click "Send test event"

**Option C: cURL**
```bash
curl -X POST http://localhost:8000/billing/webhook \
  -H "Content-Type: application/json" \
  -H "Stripe-Signature: t=123456789,v1=your_signature_hash" \
  -d '{"type":"checkout.session.completed","data":{"object":{"id":"cs_test_123","metadata":{"plan":"pro"}}}}'
```

---

## Verify It's Working

✓ Check Stripe Dashboard → Webhooks → Your endpoint → View recent attempts
✓ Check backend logs → Should show webhook processed
✓ Check Firestore → Organization plan should be updated

---

## Common Issues

| Issue | Solution |
|-------|----------|
| 400 Invalid signature | Check STRIPE_WEBHOOK_SECRET in .env |
| Webhook not called | Verify endpoint URL is correct and accessible |
| Endpoint not responding | Make sure backend is running |
| Database not updating | Check Firestore connection and rules |

---

## Need Details?

See [WEBHOOK_SETUP.md](WEBHOOK_SETUP.md) for complete guide.
