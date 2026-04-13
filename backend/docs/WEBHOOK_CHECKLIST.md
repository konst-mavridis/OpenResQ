# Webhook Setup Checklist

## Pre-Setup ✓

- [ ] Backend installed and running (`python -m uvicorn app.main:app --reload`)
- [ ] Stripe account created (https://stripe.com)
- [ ] Stripe API keys obtained
- [ ] Git configured for your OpenResQ backend

---

## Setup (Choose One Method)

### METHOD A: Stripe CLI (Recommended for Local Dev)
⏱️ Time: 5 minutes

```bash
# □ Step 1: Install Stripe CLI
brew install stripe/stripe-cli/stripe

# □ Step 2: Verify installation
stripe --version

# □ Step 3: Login to Stripe
stripe login
# (Browser will open, authorize access)

# □ Step 4: Start webhook forwarding (Terminal 1)
stripe listen --forward-to localhost:8000/billing/webhook
# Output: Ready to accept webhooks...
# ⚠️ COPY THE SIGNING SECRET (whsec_test_...)

# □ Step 5: Add to .env (in backend folder)
echo "STRIPE_WEBHOOK_SECRET=whsec_test_your_secret_here" >> .env

# □ Step 6: Restart backend (Terminal 2)
cd /Users/kmavridis/Desktop/OpenResQ/backend
python -m uvicorn app.main:app --reload

# □ Step 7: Test webhook (Terminal 3)
stripe trigger checkout.session.completed

# □ Step 8: Verify
# Look at Terminal 1 output - should show "Forwarding to ..."
# Look at Terminal 2 logs - should show webhook processed
```

### METHOD B: Stripe Dashboard (For Production)
⏱️ Time: 10 minutes

```
□ Step 1: Login to Stripe Dashboard
  https://dashboard.stripe.com

□ Step 2: Go to Webhooks
  Developers → Webhooks

□ Step 3: Click "Add an endpoint"

□ Step 4: Enter Endpoint URL
  For local dev: https://your-ngrok-url/billing/webhook
  For production: https://api.yourdomain.com/billing/webhook

□ Step 5: Select Events
  ✓ checkout.session.completed
  ✓ customer.subscription.updated
  ✓ customer.subscription.deleted
  ✓ invoice.payment_succeeded
  ✓ invoice.payment_failed

□ Step 6: Click "Add endpoint"

□ Step 7: Copy Signing Secret
  (Click endpoint → Copy "Signing secret")

□ Step 8: Add to .env
  STRIPE_WEBHOOK_SECRET=whsec_...

□ Step 9: Restart backend

□ Step 10: Test from Dashboard
  Click endpoint → "Send test event"
  Select "checkout.session.completed"
  Click "Send test event"
```

---

## Configuration ✓

### .env File
```bash
# Check these are in your .env:
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_test_...     # ← CRITICAL: Add this!
NEXT_PUBLIC_SITE_URL=http://localhost:3000
STRIPE_PRICE_PRO=price_...
```

Command to verify:
```bash
grep "STRIPE_WEBHOOK_SECRET" .env
# Should output: STRIPE_WEBHOOK_SECRET=whsec_test_...
```

### Restart Backend
```bash
# Kill current process: Ctrl+C
# Restart:
python -m uvicorn app.main:app --reload
# Should show: Uvicorn running on http://127.0.0.1:8000
```

---

## Testing ✓

### Quick Test (Choose One)

**Option A: Stripe CLI**
```bash
stripe trigger checkout.session.completed
# Should see "Forwarding to..." in stripe listen terminal
# Should see webhook processing in backend terminal
```

**Option B: Stripe Dashboard**
1. Go to Webhooks
2. Click your endpoint
3. Scroll to "Events to send"
4. Click "Send test event"
5. Select event type
6. Click "Send test event"
7. Check "Response" tab for 200 OK

**Option C: cURL**
```bash
curl -X POST http://localhost:8000/billing/webhook \
  -H "Content-Type: application/json" \
  -d '{"type":"checkout.session.completed","data":{"object":{}}}'
# Should get 400 (invalid signature) or 200 if signature valid
```

### Verification Steps
- [ ] Backend running (`http://localhost:8000`)
- [ ] Test webhook sent
- [ ] No errors in backend logs
- [ ] Firestore shows updated data (for completed events)
- [ ] Stripe Dashboard shows "sent" status

---

## Troubleshooting ✓

| Issue | Check | Solution |
|-------|-------|----------|
| ❌ 400 Invalid signature | STRIPE_WEBHOOK_SECRET in .env | Verify secret matches (whsec_...) and restart |
| ❌ Webhook not received | Endpoint URL in Stripe | Verify URL is correct and publicly accessible |
| ❌ Backend not running | Terminal showing "Uvicorn running" | Start backend: `python -m uvicorn app.main:app` |
| ❌ No events in logs | Backend logs | Restart backend and check STRIPE_WEBHOOK_SECRET |
| ❌ Firestore not updating | Firebase connection | Check Firebase credentials and rules |

---

## Production Setup ✓

When ready for production:

```bash
# □ Step 1: Update to production Stripe account
stripe login --project-name production

# □ Step 2: Get production signing secret
stripe listen --forward-to https://api.yourdomain.com/billing/webhook

# □ Step 3: Update .env for production
STRIPE_WEBHOOK_SECRET=whsec_live_production_secret

# □ Step 4: Add production endpoint in Stripe Dashboard
https://api.yourdomain.com/billing/webhook

# □ Step 5: Verify with production test
stripe trigger --live checkout.session.completed

# □ Step 6: Monitor production webhooks
stripe logs tail --live
```

---

## Files Verified ✓

Check these files exist and are correct:

```bash
# Main webhook handler
ls -la app/routers/billing.py
# Should show: app/routers/billing.py (500+ lines)

# Test suite
ls -la tests/test_plan_upgrade.py
# Should exist with webhook tests

# Environment
cat .env | grep STRIPE_WEBHOOK_SECRET
# Should show: STRIPE_WEBHOOK_SECRET=whsec_...
```

---

## Final Verification ✓

Run this before going live:

```bash
# 1. Python syntax check
python3 -m py_compile app/routers/billing.py
# Should output nothing (success)

# 2. Check endpoint registered
curl http://localhost:8000/docs#/Billing
# Should show /billing/webhook endpoint

# 3. Test webhook
stripe trigger checkout.session.completed
# Should see webhook processed in logs

# 4. Check Firestore
# Visit https://console.firebase.google.com
# Check upgrade_requests collection for new records

# 5. Review logs
tail -f /path/to/backend/logs
# Should show webhook events being processed
```

---

## Sign-Off ✓

```
Date: ________
Webhook Method: ☐ CLI  ☐ Dashboard
Status: ☐ Local Testing Complete  ☐ Production Ready
Signing Secret: whsec_test_____
Environment: ☐ Development  ☐ Production
```

---

## Reference Links

📚 **Documentation**
- Quick Setup: [WEBHOOK_QUICK_SETUP.md](WEBHOOK_QUICK_SETUP.md)
- Full Guide: [WEBHOOK_SETUP.md](WEBHOOK_SETUP.md)
- CLI Guide: [WEBHOOK_STRIPE_CLI.md](WEBHOOK_STRIPE_CLI.md)
- Postman: [POSTMAN_WEBHOOK_COLLECTION.md](POSTMAN_WEBHOOK_COLLECTION.md)

📖 **External Resources**
- Stripe Webhook Docs: https://stripe.com/docs/webhooks
- Stripe CLI: https://stripe.com/docs/stripe-cli
- Stripe Events: https://stripe.com/docs/api/events/types

💬 **Getting Help**
- Check troubleshooting section above
- Review backend logs: `python -m uvicorn app.main:app --reload`
- Test with Stripe CLI: `stripe trigger event_type`
- Check Stripe Dashboard: https://dashboard.stripe.com/webhooks

---

## Notes

```
___________________________________________________________
___________________________________________________________
___________________________________________________________
___________________________________________________________
```

---

**Status**: ✓ Ready to use webhooks!

**Next Steps**:
1. Complete checklist above
2. Test webhook with your specific events
3. Monitor production webhooks daily
4. Update this checklist when issues arise
