#!/usr/bin/env bash
# Backend Setup Guide for Plan Upgrade Feature
# This script provides setup instructions for the plan upgrade backend endpoints

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== OpenResQ Plan Upgrade Backend Setup ===${NC}\n"

echo -e "${YELLOW}Step 1: Environment Variables${NC}"
echo -e "${GREEN}Add these to your .env file:${NC}\n"

cat << 'EOF'
# Stripe API Keys (from your Stripe dashboard)
STRIPE_SECRET_KEY=sk_test_YOUR_SECRET_KEY_HERE
STRIPE_WEBHOOK_SECRET=whsec_test_YOUR_WEBHOOK_SECRET_HERE

# Stripe Price IDs (create these in Stripe dashboard)
# For subscription mode checkout
STRIPE_PRICE_BASIC=price_1234567890abcdef
STRIPE_PRICE_PRO=price_0987654321fedcba
STRIPE_PRICE_ENTERPRISE=price_abcdef1234567890

# Optional: Setup/One-time fees
STRIPE_PRICE_BASIC_SETUP=price_setup_basic
STRIPE_PRICE_PRO_SETUP=price_setup_pro

# Frontend URL (for Stripe redirect URLs)
NEXT_PUBLIC_SITE_URL=http://localhost:3000
# For production:
# NEXT_PUBLIC_SITE_URL=https://yourdomain.com

# Backend URL (optional, for internal communication)
BACKEND_API_URL=http://localhost:8000
# For production:
# BACKEND_API_URL=https://api.yourdomain.com
EOF

echo -e "\n${YELLOW}Step 2: Firestore Security Rules${NC}"
echo -e "${GREEN}Update your Firestore security rules to protect the upgrade_requests collection:${NC}\n"

cat << 'EOF'
// Allow authenticated users to read their own upgrade requests
match /upgrade_requests/{document=**} {
  allow read: if request.auth != null && resource.data.uid == request.auth.uid;
  allow write: if request.auth != null && request.resource.data.uid == request.auth.uid;
  allow create: if true; // Allow public creation (recording endpoint)
}

// Existing users collection rules
match /users/{uid} {
  allow read: if request.auth.uid == uid;
  allow write: if request.auth.uid == uid;
  allow update: if request.auth.uid == uid;
}
EOF

echo -e "\n${YELLOW}Step 3: Stripe Configuration${NC}"
echo -e "${GREEN}Create subscription prices in Stripe:${NC}\n"

echo "1. Go to https://dashboard.stripe.com/products"
echo "2. Create or update products for: Basic, Pro, Enterprise"
echo "3. For each product, create a Price with:"
echo "   - Billing period: Monthly (or your preferred)"
echo "   - Currency: Your preferred currency"
echo "   - Amount: As defined in app/constants.py"
echo "4. Copy the Price IDs (price_xxx) and add to .env"
echo ""
echo -e "${GREEN}Current price amounts (from app/constants.py):${NC}"
echo "   - Basic: $100/month"
echo "   - Pro: $250/month"
echo "   - Enterprise: $1000/month"

echo -e "\n${YELLOW}Step 4: Verify Installation${NC}"
echo -e "${GREEN}Check that the endpoints are registered:${NC}\n"

echo "Run your FastAPI server and check:"
echo "- http://localhost:8000/docs#/Billing"
echo ""
echo "You should see:"
echo "  POST /billing/upgrade-plan"
echo "  POST /billing/public/record-upgrade"

echo -e "\n${YELLOW}Step 5: Test the Endpoints${NC}"
echo -e "${GREEN}Test with curl (replace with valid Firebase token):${NC}\n"

cat << 'EOF'
# 1. Get a valid Firebase ID token from your frontend or auth flow

# 2. Test upgrade-plan endpoint
curl -X POST http://localhost:8000/billing/upgrade-plan \
  -H "Authorization: Bearer YOUR_VALID_FIREBASE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plan_id": "pro",
    "uid": "YOUR_FIREBASE_USER_ID",
    "latitude": 40.7128,
    "longitude": -74.0060
  }'

# 3. Test public record-upgrade endpoint
curl -X POST http://localhost:8000/billing/public/record-upgrade \
  -H "Content-Type: application/json" \
  -d '{
    "uid": "YOUR_FIREBASE_USER_ID",
    "plan_id": "pro",
    "org_name": "Test Organization",
    "admin_email": "admin@example.com",
    "latitude": 40.7128,
    "longitude": -74.0060
  }'
EOF

echo -e "\n${YELLOW}Step 6: Frontend Integration${NC}"
echo -e "${GREEN}The Next.js frontend code should already be configured. Verify:${NC}\n"

echo "1. Frontend has NEXT_PUBLIC_SITE_URL set to backend URL"
echo "2. Frontend includes Authorization header with Bearer token"
echo "3. Frontend calls both endpoints in correct order"
echo "4. Stripe publishable key is configured in frontend"

echo -e "\n${YELLOW}Step 7: Stripe Webhooks (Optional but Recommended)${NC}"
echo -e "${GREEN}To auto-update subscriptions when checkout completes:${NC}\n"

echo "1. Go to https://dashboard.stripe.com/webhooks"
echo "2. Create new endpoint: POST http://yourapi.com/billing/webhook"
echo "3. Subscribe to events:"
echo "   - checkout.session.completed"
echo "   - customer.subscription.updated"
echo "   - customer.subscription.deleted"
echo "4. Copy webhook signing secret to STRIPE_WEBHOOK_SECRET in .env"

echo -e "\n${YELLOW}Step 8: Database Indexes${NC}"
echo -e "${GREEN}Optional: Create Firestore indexes for better query performance:${NC}\n"

echo "1. Go to https://console.firebase.google.com/project/YOUR_PROJECT/firestore/indexes"
echo "2. Create composite index:"
echo "   - Collection: upgrade_requests"
echo "   - Fields: uid (Ascending), created_at (Descending)"
echo "   - This helps query user upgrades by date"

echo -e "\n${GREEN}Setup Complete!${NC}"
echo -e "${BLUE}Next: Run your FastAPI server and test the endpoints${NC}\n"

# Print the Pydantic models for reference
echo -e "${YELLOW}Reference: Request Models${NC}"
echo -e "${GREEN}UpgradePlanRequest:{NC}"
cat << 'EOF'
{
  "plan_id": "pro",           # Required: basic, pro, or enterprise
  "uid": "firebase_user_id",  # Required: Firebase user ID
  "latitude": 40.7128,        # Optional: User's latitude
  "longitude": -74.0060       # Optional: User's longitude
}
EOF

echo -e "\n${GREEN}RecordUpgradeRequest:${NC}"
cat << 'EOF'
{
  "uid": "firebase_user_id",     # Required: Firebase user ID
  "plan_id": "pro",              # Required: basic, pro, or enterprise
  "org_name": "Organization",    # Optional: Organization name
  "admin_email": "admin@test.com",# Optional: Admin email
  "latitude": 40.7128,           # Optional: User's latitude
  "longitude": -74.0060          # Optional: User's longitude
}
EOF

echo -e "\n${BLUE}For more details, see: UPGRADE_PLAN_BACKEND.md${NC}\n"
