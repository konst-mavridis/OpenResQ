# Plan Upgrade Backend Implementation

## Overview

This implementation adds plan upgrade functionality to the OpenResQ backend, enabling users to upgrade their subscription plans via Stripe checkout. The backend works seamlessly with the Next.js frontend code provided.

## Endpoints

### 1. POST `/billing/upgrade-plan`

Creates a Stripe checkout session for a plan upgrade. This endpoint:
- Verifies the user's Firebase ID token
- Retrieves user data from Firestore
- Creates a Stripe checkout session with the selected plan
- Updates user location (if provided)
- Records the upgrade request in Firestore

**Request Headers:**
```
Authorization: Bearer <FIREBASE_ID_TOKEN>
```

**Request Body:**
```json
{
  "plan_id": "pro",
  "uid": "user_id_from_firebase",
  "latitude": 40.7128,
  "longitude": -74.0060
}
```

**Response:**
```json
{
  "url": "https://checkout.stripe.com/pay/cs_test_..."
}
```

**Error Responses:**
- `400`: Missing required fields (plan_id, uid)
- `401`: Missing or invalid authorization token
- `404`: User not found in Firestore
- `500`: Stripe session creation failed

---

### 2. POST `/billing/public/record-upgrade`

Public endpoint to record plan upgrade requests in the database. This is called by the Next.js frontend after Stripe checkout is initiated.

**Request Body:**
```json
{
  "uid": "user_id",
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

**Error Responses:**
- `400`: Missing required fields (uid, plan_id)
- `500`: Database recording failed

---

## Environment Variables

Add the following to your `.env` file:

```bash
# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_...                          # Your Stripe secret key
STRIPE_PRICE_BASIC=price_...                           # Stripe price ID for basic plan
STRIPE_PRICE_PRO=price_...                             # Stripe price ID for pro plan
STRIPE_PRICE_BASIC_SETUP=price_...                     # Optional: setup fee for basic
STRIPE_PRICE_PRO_SETUP=price_...                       # Optional: setup fee for pro

# Frontend Configuration
NEXT_PUBLIC_SITE_URL=https://yourdomain.com            # Frontend URL for redirect
```

## Firestore Collections

### `upgrade_requests`
Records all plan upgrade requests for analytics and tracking.

**Document Structure:**
```javascript
{
  "uid": "firebase_user_id",
  "plan_id": "pro",
  "org_name": "Organization Name",
  "admin_email": "admin@example.com",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "stripe_session_id": "cs_test_...",
  "status": "pending",  // pending, completed, failed
  "created_at": Timestamp
}
```

### `users` (Updated)
When location is updated during upgrade:
```javascript
{
  // ... existing fields
  "area": {
    "latitude": 40.7128,
    "longitude": -74.0060,
    "radius_km": 20.0
  },
  "last_updated": Timestamp
}
```

## Frontend Integration

The Next.js frontend code calls these endpoints in this flow:

1. **User initiates upgrade** → Calls `/billing/upgrade-plan`
2. **Backend returns Stripe checkout URL** → Redirect user to Stripe
3. **After checkout completion** → Frontend calls `/billing/public/record-upgrade`
4. **User redirected to success page** → `NEXT_PUBLIC_SITE_URL/billing?upgrade=success`

## Data Flow

```
Next.js Frontend
    ↓
    POST /billing/upgrade-plan
    ├─ Verify Firebase token
    ├─ Get user from Firestore
    ├─ Create Stripe session
    ├─ Update user location (optional)
    ├─ Record upgrade request
    └─ Return checkout URL
    ↓
User completes Stripe checkout
    ↓
    POST /billing/public/record-upgrade
    └─ Record upgrade in database
    ↓
Stripe webhook (existing endpoint)
    └─ Update subscription status
```

## Security Features

1. **Token Verification**: Firebase ID token is verified for authenticated endpoint
2. **User Validation**: Ensures token UID matches request UID
3. **Public Endpoint**: The recording endpoint is public but requires user UID (can be enhanced with token verification if needed)
4. **Firestore Security Rules**: Ensure database security rules protect sensitive data

## Error Handling

All endpoints include comprehensive error logging and appropriate HTTP status codes:
- **400** - Bad Request (missing/invalid parameters)
- **401** - Unauthorized (invalid token)
- **404** - Not Found (user not found)
- **500** - Internal Server Error (Stripe/database failures)

Errors are logged to the application logger for debugging.

## Models

Two Pydantic models handle request validation:

### `UpgradePlanRequest`
```python
class UpgradePlanRequest(BaseModel):
    plan_id: str
    latitude: float = None
    longitude: float = None
    uid: str
```

### `RecordUpgradeRequest`
```python
class RecordUpgradeRequest(BaseModel):
    uid: str
    plan_id: str
    org_name: str = None
    admin_email: str = None
    latitude: float = None
    longitude: float = None
```

## Testing

### Test the upgrade-plan endpoint:
```bash
curl -X POST http://localhost:8000/billing/upgrade-plan \
  -H "Authorization: Bearer YOUR_FIREBASE_ID_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plan_id": "pro",
    "uid": "YOUR_USER_ID",
    "latitude": 40.7128,
    "longitude": -74.0060
  }'
```

### Test the record-upgrade endpoint:
```bash
curl -X POST http://localhost:8000/billing/public/record-upgrade \
  -H "Content-Type: application/json" \
  -d '{
    "uid": "YOUR_USER_ID",
    "plan_id": "pro",
    "org_name": "Test Org",
    "admin_email": "admin@example.com",
    "latitude": 40.7128,
    "longitude": -74.0060
  }'
```

## Implementation Notes

- **Location Update**: User location is updated with radius_km set to 20.0 as default
- **Idempotency**: Recording the same upgrade multiple times creates separate records (suitable for current use case)
- **Logging**: All operations are logged for debugging and monitoring
- **Error Recovery**: If location update fails, the upgrade process continues
- **Stripe Session**: Session creates line items with optional setup fees

## File Modified

- [app/routers/billing.py](app/routers/billing.py) - Added upgrade plan endpoints

## Integration Checklist

- [ ] Add Stripe price IDs to `.env` file
- [ ] Add `NEXT_PUBLIC_SITE_URL` to `.env` file
- [ ] Create Firestore security rules for `upgrade_requests` collection
- [ ] Test endpoints with valid Firebase tokens
- [ ] Verify Stripe environment variables are set correctly
- [ ] Set up Firestore indexes if needed for queries
- [ ] Configure Stripe webhooks for subscription completion
- [ ] Test end-to-end flow from frontend to backend
