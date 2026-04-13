# Quick Start Guide - Plan Upgrade Endpoints

## 5-Minute Setup

### 1. Add Environment Variables
```bash
# Add to your .env file (copy from .env.example.stripe)
STRIPE_SECRET_KEY=sk_test_YOUR_KEY
STRIPE_PRICE_PRO=price_YOUR_PRICE_ID
NEXT_PUBLIC_SITE_URL=http://localhost:3000
```

### 2. Verify Installation
```bash
# The endpoints are already in the code
# Check they're registered by visiting:
# http://localhost:8000/docs#/Billing
```

### 3. Test the Endpoints
```bash
# Create a checkout session (requires valid Firebase token)
curl -X POST http://localhost:8000/billing/upgrade-plan \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plan_id": "pro",
    "uid": "firebase_user_id"
  }'

# Record an upgrade (no auth required)
curl -X POST http://localhost:8000/billing/public/record-upgrade \
  -H "Content-Type: application/json" \
  -d '{
    "uid": "firebase_user_id",
    "plan_id": "pro"
  }'
```

## API Quick Reference

### Create Checkout Session
```
POST /billing/upgrade-plan
Authorization: Bearer {FIREBASE_TOKEN}
Content-Type: application/json

{
  "plan_id": "pro",
  "uid": "user_id",
  "latitude": 40.7128,
  "longitude": -74.0060
}

Response: { "url": "https://checkout.stripe.com/..." }
```

### Record Upgrade
```
POST /billing/public/record-upgrade
Content-Type: application/json

{
  "uid": "user_id",
  "plan_id": "pro",
  "org_name": "Org Name",
  "admin_email": "admin@example.com",
  "latitude": 40.7128,
  "longitude": -74.0060
}

Response: { "status": "ok", "message": "Upgrade recorded successfully" }
```

## Configuration Reference

### Required Environment Variables
| Variable | Value | Example |
|----------|-------|---------|
| `STRIPE_SECRET_KEY` | Your Stripe secret key | `sk_test_51O...` |
| `STRIPE_PRICE_PRO` | Stripe price ID | `price_1O...` |
| `NEXT_PUBLIC_SITE_URL` | Frontend URL | `http://localhost:3000` |

### Optional Environment Variables
| Variable | Value | Example |
|----------|-------|---------|
| `STRIPE_PRICE_BASIC` | Stripe price ID | `price_1O...` |
| `STRIPE_PRICE_BASIC_SETUP` | Setup fee price ID | `price_1O...` |
| `STRIPE_PRICE_PRO_SETUP` | Setup fee price ID | `price_1O...` |
| `BACKEND_API_URL` | Backend URL | `http://localhost:8000` |

## Request/Response Examples

### Success Response
```json
HTTP 200
{
  "url": "https://checkout.stripe.com/pay/cs_test_123456789"
}
```

### Error Response
```json
HTTP 401
{
  "detail": "Unauthorized - Invalid token"
}
```

## Troubleshooting

### "Unauthorized" Error
- Ensure Firebase token is valid and not expired
- Check Authorization header format: `Bearer {TOKEN}`
- Verify token UID matches request UID

### "Invalid plan ID" Error
- Check plan_id is one of: `basic`, `pro`, `enterprise`
- Verify PLANS constant in app/constants.py

### "User not found" Error
- Ensure user exists in Firestore
- Check UID format matches Firebase

### "Stripe error" on checkout creation
- Verify STRIPE_SECRET_KEY is set correctly
- Check STRIPE_PRICE_XXX environment variables
- Confirm prices exist in Stripe dashboard

## Files Reference

| File | Purpose |
|------|---------|
| [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) | Complete implementation details |
| [UPGRADE_PLAN_BACKEND.md](UPGRADE_PLAN_BACKEND.md) | Full API documentation |
| [SETUP_UPGRADE_PLAN.sh](SETUP_UPGRADE_PLAN.sh) | Setup instructions |
| [.env.example.stripe](.env.example.stripe) | Environment variable examples |
| [app/services/plan_upgrade_client.py](app/services/plan_upgrade_client.py) | Python client library |
| [tests/test_plan_upgrade.py](tests/test_plan_upgrade.py) | Test suite |
| [app/routers/billing.py](app/routers/billing.py) | Endpoint implementation |

## Common Workflows

### Workflow 1: Full Upgrade Flow
1. Frontend calls `/billing/upgrade-plan` with Firebase token
2. Backend returns Stripe checkout URL
3. User completes Stripe checkout
4. Frontend calls `/billing/public/record-upgrade`
5. Backend records upgrade in Firestore

### Workflow 2: Testing
1. Get Firebase test token from your auth system
2. Call `/billing/upgrade-plan` with test token
3. Curl the response URL to test Stripe integration
4. Call `/billing/public/record-upgrade` to test recording

## Key Features

✅ Firebase token verification  
✅ Automatic user location update  
✅ Stripe checkout session creation  
✅ Upgrade request logging  
✅ Comprehensive error handling  
✅ Pydantic request validation  
✅ Full test suite included  
✅ Production-ready logging

## Next Steps

1. **Configure Stripe**: Add API keys to .env
2. **Test locally**: Use curl commands above
3. **Set Firestore rules**: See SETUP_UPGRADE_PLAN.sh
4. **Connect frontend**: Use provided Next.js code
5. **Deploy**: Follow deployment checklist in IMPLEMENTATION_SUMMARY.md

## Support Resources

- **API Docs**: [UPGRADE_PLAN_BACKEND.md](UPGRADE_PLAN_BACKEND.md)
- **Setup Guide**: [SETUP_UPGRADE_PLAN.sh](SETUP_UPGRADE_PLAN.sh)
- **Test Examples**: [tests/test_plan_upgrade.py](tests/test_plan_upgrade.py)
- **Example Config**: [.env.example.stripe](.env.example.stripe)
- **Client Library**: [app/services/plan_upgrade_client.py](app/services/plan_upgrade_client.py)

## Status Check

Run this to verify everything is working:

```bash
# 1. Check Python syntax
python3 -m py_compile app/routers/billing.py

# 2. Check endpoint registration
# Visit: http://localhost:8000/docs

# 3. Run tests
pytest tests/test_plan_upgrade.py -v
```

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Status**: Production Ready
