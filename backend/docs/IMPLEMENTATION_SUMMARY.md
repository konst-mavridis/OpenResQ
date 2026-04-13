# Backend Implementation Summary
# Plan Upgrade Feature for OpenResQ

## Overview
This implementation adds complete plan upgrade functionality to the OpenResQ backend, enabling users to upgrade their subscription plans through Stripe checkout. The backend integrates seamlessly with the provided Next.js frontend code.

## Files Modified/Created

### Modified Files
1. **[app/routers/billing.py](app/routers/billing.py)** 
   - Added dependency: `from pydantic import BaseModel`
   - Added 2 Pydantic request models:
     - `UpgradePlanRequest`: For /upgrade-plan endpoint
     - `RecordUpgradeRequest`: For /public/record-upgrade endpoint
   - Added 2 new endpoints:
     - `POST /billing/upgrade-plan`: Create Stripe checkout session
     - `POST /billing/public/record-upgrade`: Record upgrade request

### New Files Created
1. **[UPGRADE_PLAN_BACKEND.md](UPGRADE_PLAN_BACKEND.md)**
   - Complete API documentation
   - Endpoint descriptions and examples
   - Firestore schema documentation
   - Security features overview
   - Testing instructions

2. **[SETUP_UPGRADE_PLAN.sh](SETUP_UPGRADE_PLAN.sh)**
   - Step-by-step setup guide
   - Environment variable configuration
   - Firestore security rules examples
   - Testing commands
   - Integration checklist

3. **[.env.example.stripe](.env.example.stripe)**
   - Example environment variables
   - All required Stripe configuration keys
   - Detailed comments explaining each variable
   - Test vs production examples

4. **[app/services/plan_upgrade_client.py](app/services/plan_upgrade_client.py)**
   - Async client class: `PlanUpgradeClient`
   - Sync client class: `PlanUpgradeClientSync`
   - Methods for creating checkout sessions and recording upgrades
   - Comprehensive error handling and logging
   - Usage examples

5. **[tests/test_plan_upgrade.py](tests/test_plan_upgrade.py)**
   - Unit tests for both endpoints
   - Request model validation tests
   - Mock tests for Stripe and Firestore
   - Integration test framework
   - Load test data generation

## API Endpoints

### 1. POST /billing/upgrade-plan
**Authentication:** Bearer token (Firebase ID token) required

Creates a Stripe checkout session for plan upgrade.

**Request:**
```json
{
  "plan_id": "pro",
  "uid": "firebase_user_id",
  "latitude": 40.7128,
  "longitude": -74.0060
}
```

**Response:**
```json
{
  "url": "https://checkout.stripe.com/pay/cs_..."
}
```

**Features:**
- Firebase token verification
- User validation
- Plan validation
- Location update in Firestore
- Upgrade request logging
- Error handling and logging

### 2. POST /billing/public/record-upgrade
**Authentication:** None required (public endpoint)

Records a plan upgrade request for database tracking.

**Request:**
```json
{
  "uid": "firebase_user_id",
  "plan_id": "pro",
  "org_name": "Organization Name",
  "admin_email": "admin@example.com",
  "latitude": 40.7128,
  "longitude": -74.0060
}
```

**Response:**
```json
{
  "status": "ok",
  "message": "Upgrade recorded successfully"
}
```

## Pydantic Models

### UpgradePlanRequest
```python
class UpgradePlanRequest(BaseModel):
    plan_id: str                    # Required: basic, pro, enterprise
    latitude: float = None          # Optional
    longitude: float = None         # Optional
    uid: str                        # Required
```

### RecordUpgradeRequest
```python
class RecordUpgradeRequest(BaseModel):
    uid: str                        # Required
    plan_id: str                    # Required
    org_name: str = None            # Optional
    admin_email: str = None         # Optional
    latitude: float = None          # Optional
    longitude: float = None         # Optional
```

## Dependencies

Uses existing dependencies (no new packages required):
- `fastapi` - API framework
- `stripe` - Stripe API client
- `firebase-admin` - Firebase integration
- `pydantic` - Request validation

## Environment Variables Required

```bash
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PRICE_BASIC=price_...
STRIPE_PRICE_PRO=price_...
STRIPE_PRICE_BASIC_SETUP=price_...        # Optional
STRIPE_PRICE_PRO_SETUP=price_...          # Optional
NEXT_PUBLIC_SITE_URL=http://localhost:3000
BACKEND_API_URL=http://localhost:8000     # Optional
```

## Firestore Collections

### upgrade_requests
Stores all plan upgrade requests for tracking and analytics.

**Schema:**
```javascript
{
  uid: string,
  plan_id: string,
  org_name: string,
  admin_email: string,
  latitude: number,
  longitude: number,
  stripe_session_id: string,
  status: string,  // pending, completed, failed
  created_at: Timestamp
}
```

## Feature Breakdown

### POST /billing/upgrade-plan
- ✅ Firebase ID token verification
- ✅ User validation and loading from Firestore
- ✅ Plan validation against PLANS constant
- ✅ Stripe checkout session creation
- ✅ Optional location update in Firestore
- ✅ Upgrade request logging
- ✅ Comprehensive error handling
- ✅ Logging for debugging

### POST /billing/public/record-upgrade
- ✅ Upgrade request recording in Firestore
- ✅ Firestore data persistence
- ✅ Error handling and logging
- ✅ Public access for frontend recording

## Security Features

1. **Token Verification**: Firebase ID token verified before creating checkout session
2. **User Validation**: Ensures token UID matches request UID
3. **Plan Validation**: Verifies plan exists in PLANS constant
4. **Error Handling**: Appropriate HTTP status codes and error messages
5. **Logging**: All operations logged for audit trail
6. **Firestore Rules**: Recommend setting up security rules for upgrade_requests

## Testing

Run unit tests:
```bash
pytest tests/test_plan_upgrade.py -v
```

Run specific test:
```bash
pytest tests/test_plan_upgrade.py::TestUpgradePlanEndpoint::test_invalid_plan_id -v
```

Test endpoints manually:
```bash
# Create checkout session
curl -X POST http://localhost:8000/billing/upgrade-plan \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"plan_id":"pro","uid":"USER_ID"}'

# Record upgrade
curl -X POST http://localhost:8000/billing/public/record-upgrade \
  -H "Content-Type: application/json" \
  -d '{"uid":"USER_ID","plan_id":"pro"}'
```

## Integration with Next.js Frontend

The backend endpoints work with the provided Next.js code:

1. Frontend calls `/billing/upgrade-plan` with Firebase token
2. Backend returns Stripe checkout URL
3. User redirected to Stripe checkout
4. After checkout, frontend calls `/billing/public/record-upgrade`
5. Stripe webhook updates subscription status (existing endpoint)

## Error Handling

Both endpoints return appropriate HTTP status codes:
- **200**: Success
- **400**: Bad request (invalid parameters)
- **401**: Unauthorized (invalid/missing token)
- **404**: Not found (user not found)
- **500**: Server error (Stripe/database failure)

All errors are logged with details for debugging.

## Logging

All operations are logged using Python's logging module:
- `logger.info()`: Success operations
- `logger.error()`: Failures and exceptions
- `logger.warning()`: Non-critical issues

## Client Integration

Use the `PlanUpgradeClient` or `PlanUpgradeClientSync` from `app/services/plan_upgrade_client.py`:

```python
from app.services.plan_upgrade_client import PlanUpgradeClient

client = PlanUpgradeClient("http://localhost:8000")

# Create checkout session
result = await client.create_upgrade_checkout_session(
    plan_id="pro",
    uid="user_id",
    firebase_token="token",
)

# Record upgrade
await client.record_upgrade(
    uid="user_id",
    plan_id="pro",
)
```

## Performance Considerations

- Stripe API calls are synchronous (blocking)
- Location update errors don't block the response
- Upgrade recording is best-effort (doesn't block checkout)
- Database queries are minimal (direct doc access)
- No database indexing required (but recommended for queries)

## Future Enhancements

1. Add webhook validation for Stripe events
2. Add retry logic for failed Stripe API calls
3. Add rate limiting for upgrade endpoint
4. Add analytics tracking for upgrade conversions
5. Add email notifications on upgrade
6. Add support for plan downgrades
7. Add billing history queries

## Deployment Checklist

- [ ] Configure Stripe API keys in production environment
- [ ] Set correct NEXT_PUBLIC_SITE_URL for production
- [ ] Create Firestore security rules for upgrade_requests
- [ ] Test end-to-end with Stripe test mode
- [ ] Configure Stripe webhooks for production
- [ ] Verify CORS settings allow frontend domain
- [ ] Set up logging and monitoring
- [ ] Load test the endpoints
- [ ] Document any custom setup for your hosting

## Support

For issues or questions:
1. Check UPGRADE_PLAN_BACKEND.md for detailed API docs
2. Review SETUP_UPGRADE_PLAN.sh for setup instructions
3. Check logs in app service for error details
4. Review test cases in tests/test_plan_upgrade.py for examples
5. Verify Stripe configuration and API keys

## Version

Implementation Date: 2024
Backend Version: 1.0.0
Compatible with: FastAPI 0.104.1+, Stripe 15.0.1+
