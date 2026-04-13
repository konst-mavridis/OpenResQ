```json
{
  "info": {
    "name": "Stripe Webhook Testing",
    "description": "Postman collection for testing Stripe webhook endpoints",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Test Webhooks",
      "item": [
        {
          "name": "Webhook - Checkout Session Completed",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              },
              {
                "key": "Stripe-Signature",
                "value": "t={{timestamp}},v1={{webhook_signature}}",
                "description": "Generate using HMAC-SHA256"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"id\": \"evt_test_checkout_completed\",\n  \"object\": \"event\",\n  \"api_version\": \"2023-10-16\",\n  \"created\": {{timestamp}},\n  \"type\": \"checkout.session.completed\",\n  \"data\": {\n    \"object\": {\n      \"id\": \"cs_test_123456789\",\n      \"object\": \"checkout.session\",\n      \"customer_email\": \"user@example.com\",\n      \"mode\": \"subscription\",\n      \"payment_status\": \"attached\",\n      \"status\": \"complete\",\n      \"subscription\": \"sub_test_123456789\",\n      \"metadata\": {\n        \"plan\": \"pro\",\n        \"uid\": \"user_123\",\n        \"org_name\": \"Test Organization\",\n        \"admin_email\": \"admin@example.com\",\n        \"upgrade_type\": \"plan_upgrade\"\n      },\n      \"success_url\": \"http://localhost:3000/billing?success=true\",\n      \"cancel_url\": \"http://localhost:3000/billing\"\n    }\n  }\n}"
            },
            "url": {
              "raw": "{{base_url}}/billing/webhook",
              "host": ["{{base_url}}"],
              "path": ["billing", "webhook"]
            },
            "description": "Test checkout.session.completed event"
          }
        },
        {
          "name": "Webhook - Subscription Updated",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              },
              {
                "key": "Stripe-Signature",
                "value": "t={{timestamp}},v1={{webhook_signature}}"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"id\": \"evt_test_subscription_updated\",\n  \"object\": \"event\",\n  \"api_version\": \"2023-10-16\",\n  \"created\": {{timestamp}},\n  \"type\": \"customer.subscription.updated\",\n  \"data\": {\n    \"object\": {\n      \"id\": \"sub_test_123456789\",\n      \"object\": \"subscription\",\n      \"customer\": \"cus_test_123\",\n      \"status\": \"active\",\n      \"current_period_start\": {{current_period_start}},\n      \"current_period_end\": {{current_period_end}},\n      \"metadata\": {\n        \"plan\": \"pro\",\n        \"org_id\": \"org_123\"\n      }\n    }\n  }\n}"
            },
            "url": {
              "raw": "{{base_url}}/billing/webhook",
              "host": ["{{base_url}}"],
              "path": ["billing", "webhook"]
            },
            "description": "Test customer.subscription.updated event"
          }
        },
        {
          "name": "Webhook - Subscription Deleted",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              },
              {
                "key": "Stripe-Signature",
                "value": "t={{timestamp}},v1={{webhook_signature}}"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"id\": \"evt_test_subscription_deleted\",\n  \"object\": \"event\",\n  \"api_version\": \"2023-10-16\",\n  \"created\": {{timestamp}},\n  \"type\": \"customer.subscription.deleted\",\n  \"data\": {\n    \"object\": {\n      \"id\": \"sub_test_123456789\",\n      \"object\": \"subscription\",\n      \"customer\": \"cus_test_123\",\n      \"status\": \"canceled\",\n      \"metadata\": {\n        \"org_id\": \"org_123\"\n      }\n    }\n  }\n}"
            },
            "url": {
              "raw": "{{base_url}}/billing/webhook",
              "host": ["{{base_url}}"],
              "path": ["billing", "webhook"]
            },
            "description": "Test customer.subscription.deleted event"
          }
        },
        {
          "name": "Webhook - Invoice Payment Succeeded",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              },
              {
                "key": "Stripe-Signature",
                "value": "t={{timestamp}},v1={{webhook_signature}}"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"id\": \"evt_test_invoice_payment_succeeded\",\n  \"object\": \"event\",\n  \"api_version\": \"2023-10-16\",\n  \"created\": {{timestamp}},\n  \"type\": \"invoice.payment_succeeded\",\n  \"data\": {\n    \"object\": {\n      \"id\": \"in_test_123456789\",\n      \"object\": \"invoice\",\n      \"customer\": \"cus_test_123\",\n      \"subscription\": \"sub_test_123456789\",\n      \"amount_paid\": 25000,\n      \"currency\": \"usd\",\n      \"paid\": true,\n      \"status\": \"paid\",\n      \"metadata\": {\n        \"org_id\": \"org_123\",\n        \"plan\": \"pro\"\n      }\n    }\n  }\n}"
            },
            "url": {
              "raw": "{{base_url}}/billing/webhook",
              "host": ["{{base_url}}"],
              "path": ["billing", "webhook"]
            },
            "description": "Test invoice.payment_succeeded event"
          }
        },
        {
          "name": "Webhook - Invalid Signature (Should Fail)",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              },
              {
                "key": "Stripe-Signature",
                "value": "t={{timestamp}},v1=invalid_signature_here"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"id\": \"evt_test_invalid\",\n  \"type\": \"checkout.session.completed\",\n  \"data\": {}\n}"
            },
            "url": {
              "raw": "{{base_url}}/billing/webhook",
              "host": ["{{base_url}}"],
              "path": ["billing", "webhook"]
            },
            "description": "Test with invalid signature - should return 400"
          }
        }
      ]
    },
    {
      "name": "Setup Instructions",
      "item": [
        {
          "name": "1. Get Webhook Secret (Stripe CLI)",
          "request": {
            "method": "GET",
            "url": {
              "raw": "https://stripe.com/docs/stripe-cli"
            },
            "description": "1. Install Stripe CLI\n2. Run: stripe listen --forward-to localhost:8000/billing/webhook\n3. Copy the signing secret (whsec_test_...)\n4. Add to Postman variable: webhook_secret"
          }
        },
        {
          "name": "2. Configure Postman Variables",
          "request": {
            "method": "GET",
            "url": {
              "raw": "https://learning.postman.com/docs/sending-requests/variables/"
            },
            "description": "Create these variables in Postman:\n\n1. base_url = http://localhost:8000\n2. webhook_secret = whsec_test_your_secret_here\n3. timestamp = {{$timestamp}}\n\nThen use in headers:\nStripe-Signature: t={{timestamp}},v1={{webhook_signature}}"
          }
        }
      ]
    },
    {
      "name": "Utils",
      "item": [
        {
          "name": "Health Check",
          "request": {
            "method": "GET",
            "url": {
              "raw": "{{base_url}}/",
              "host": ["{{base_url}}"],
              "path": ["/"]
            },
            "description": "Verify backend is running"
          }
        },
        {
          "name": "API Documentation",
          "request": {
            "method": "GET",
            "url": {
              "raw": "{{base_url}}/docs",
              "host": ["{{base_url}}"],
              "path": ["docs"]
            },
            "description": "View OpenAPI documentation"
          }
        }
      ]
    }
  ],
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8000",
      "type": "string"
    },
    {
      "key": "webhook_secret",
      "value": "whsec_test_your_secret_here",
      "type": "string"
    },
    {
      "key": "timestamp",
      "value": "{{$timestamp}}",
      "type": "string"
    },
    {
      "key": "webhook_signature",
      "value": "calculated_hmac_sha256_hash",
      "type": "string"
    },
    {
      "key": "current_period_start",
      "value": "1234567890",
      "type": "string"
    },
    {
      "key": "current_period_end",
      "value": "1237159890",
      "type": "string"
    }
  ]
}
```

## How to Use This Collection

### Import into Postman

1. Copy the JSON above
2. Open Postman
3. Click **Import** (top left)
4. Click **Raw text** tab
5. Paste the JSON
6. Click **Import**

### Set Up Variables

1. Click the collection name
2. Go to **Variables** tab
3. Set these variables:
   - `base_url`: `http://localhost:8000`
   - `webhook_secret`: Your trailing `whsec_` secret

### Generate Webhook Signature

To test with proper signatures, you need to generate HMAC-SHA256:

**Using Node.js**:
```javascript
const crypto = require('crypto');

const secret = 'whsec_test_abc123';
const timestamp = Math.floor(Date.now() / 1000);
const payload = `${timestamp}.{"type":"checkout.session.completed"}`;

const signature = crypto
  .createHmac('sha256', secret)
  .update(payload)
  .digest('hex');

console.log(`t=${timestamp},v1=${signature}`);
```

**Using Python**:
```python
import hmac
import hashlib
import time
import json

secret = 'whsec_test_abc123'
timestamp = int(time.time())
payload = f'{timestamp}.{json.dumps({"type":"checkout.session.completed"})}'

signature = hmac.new(
    secret.encode(),
    payload.encode(),
    hashlib.sha256
).hexdigest()

print(f't={timestamp},v1={signature}')
```

**Using OpenSSL**:
```bash
# Set your variables
SECRET='whsec_test_abc123'
TIMESTAMP=$(date +%s)
PAYLOAD='{"type":"checkout.session.completed"}'

# Generate signature
SIGNATURE=$(echo -n "$TIMESTAMP.$PAYLOAD" | openssl dgst -sha256 -hmac "$SECRET" | awk '{print $2}')

echo "t=$TIMESTAMP,v1=$SIGNATURE"
```

### Test Webhook

1. Set the signature in Postman header
2. Click "Send" on webhook request
3. Should return **200 OK**
4. Check backend logs for "Webhook processed"

---

## Expected Responses

### Success (200 OK)
```json
{
  "status": "success"
}
```

### Invalid Signature (400 Bad Request)
```json
{
  "detail": "Invalid webhook signature"
}
```

### Server Error (500)
```json
{
  "detail": "Internal server error"
}
```

---

## Tips

- Use Stripe CLI instead for easier testing: `stripe trigger checkout.session.completed`
- Postman is useful for custom payload testing
- Always verify signature to ensure requests are from Stripe
- Check backend logs for processing details
