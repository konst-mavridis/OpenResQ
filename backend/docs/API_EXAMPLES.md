# API Integration Examples

This file contains ready-to-use examples for integrating with the plan upgrade endpoints in different programming languages and frameworks.

## JavaScript / TypeScript (Client-side)

### Using Fetch API
```javascript
// Create checkout session
async function initiateUpgrade(planId, uid, token) {
  const response = await fetch('/billing/upgrade-plan', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      plan_id: planId,
      uid: uid,
      latitude: location.latitude,
      longitude: location.longitude,
    }),
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || 'Failed to create checkout session');
  }
  
  // Redirect to Stripe checkout
  window.location.href = data.url;
}

// Record upgrade (call after Stripe checkout)
async function recordUpgrade(uid, planId) {
  const response = await fetch('/billing/public/record-upgrade', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      uid: uid,
      plan_id: planId,
      org_name: userOrg?.name,
      admin_email: userEmail,
    }),
  });

  const data = await response.json();
  if (!response.ok) {
    console.error('Failed to record upgrade:', data);
  }
}
```

### Using Axios
```javascript
import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

async function upgradeWithAxios(planId, uid, token) {
  try {
    const response = await apiClient.post('/billing/upgrade-plan', {
      plan_id: planId,
      uid: uid,
    }, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
    window.location.href = response.data.url;
  } catch (error) {
    console.error('Upgrade failed:', error.response?.data?.detail);
  }
}
```

### React Hook
```javascript
import { useState } from 'react';

function usePlanUpgrade(token) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const upgradeToplan = async (planId, uid) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/billing/upgrade-plan', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ plan_id: planId, uid }),
      });

      if (!response.ok) {
        throw new Error('Failed to create checkout session');
      }

      const { url } = await response.json();
      window.location.href = url;
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return { upgradeToplan, loading, error };
}
```

## Python

### Using Requests
```python
import requests
import os

BASE_URL = os.getenv('BACKEND_API_URL', 'http://localhost:8000')

def create_upgrade_session(plan_id, uid, firebase_token):
    """Create Stripe checkout session for upgrade."""
    headers = {
        'Authorization': f'Bearer {firebase_token}',
        'Content-Type': 'application/json',
    }
    
    payload = {
        'plan_id': plan_id,
        'uid': uid,
        'latitude': 40.7128,
        'longitude': -74.0060,
    }
    
    response = requests.post(
        f'{BASE_URL}/billing/upgrade-plan',
        json=payload,
        headers=headers,
    )
    
    response.raise_for_status()
    return response.json()

def record_upgrade(uid, plan_id, org_name=None, admin_email=None):
    """Record upgrade in backend database."""
    payload = {
        'uid': uid,
        'plan_id': plan_id,
        'org_name': org_name,
        'admin_email': admin_email,
    }
    
    response = requests.post(
        f'{BASE_URL}/billing/public/record-upgrade',
        json=payload,
    )
    
    response.raise_for_status()
    return response.json()

# Usage
try:
    session = create_upgrade_session('pro', 'user123', 'firebase_token')
    print(f'Checkout URL: {session["url"]}')
    
    # After checkout completed
    record = record_upgrade('user123', 'pro', org_name='My Org')
    print(f'Upgrade recorded: {record}')
except requests.RequestException as e:
    print(f'Error: {e}')
```

### Using HTTPX (Async)
```python
import httpx
import asyncio

async def upgrade_async(plan_id, uid, firebase_token):
    """Async upgrade using HTTPX."""
    async with httpx.AsyncClient() as client:
        # Create checkout session
        response = await client.post(
            'http://localhost:8000/billing/upgrade-plan',
            json={'plan_id': plan_id, 'uid': uid},
            headers={'Authorization': f'Bearer {firebase_token}'},
        )
        
        session = response.json()
        print(f'Session URL: {session["url"]}')
        
        # Record upgrade
        response = await client.post(
            'http://localhost:8000/billing/public/record-upgrade',
            json={'uid': uid, 'plan_id': plan_id},
        )
        
        result = response.json()
        print(f'Recorded: {result}')

# Run async function
asyncio.run(upgrade_async('pro', 'user123', 'token'))
```

## cURL

### Create Checkout Session
```bash
curl -X POST http://localhost:8000/billing/upgrade-plan \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plan_id": "pro",
    "uid": "user_id_here",
    "latitude": 40.7128,
    "longitude": -74.0060
  }'
```

### Record Upgrade
```bash
curl -X POST http://localhost:8000/billing/public/record-upgrade \
  -H "Content-Type: application/json" \
  -d '{
    "uid": "user_id_here",
    "plan_id": "pro",
    "org_name": "My Organization",
    "admin_email": "admin@example.com",
    "latitude": 40.7128,
    "longitude": -74.0060
  }'
```

## PowerShell

```powershell
# Create checkout session
$headers = @{
    "Authorization" = "Bearer YOUR_FIREBASE_TOKEN"
    "Content-Type" = "application/json"
}

$body = @{
    plan_id = "pro"
    uid = "user_id"
    latitude = 40.7128
    longitude = -74.0060
} | ConvertTo-Json

$response = Invoke-RestMethod `
    -Uri "http://localhost:8000/billing/upgrade-plan" `
    -Method POST `
    -Headers $headers `
    -Body $body

Write-Host "Checkout URL: $($response.url)"

# Record upgrade
$body = @{
    uid = "user_id"
    plan_id = "pro"
    org_name = "My Org"
    admin_email = "admin@example.com"
} | ConvertTo-Json

$response = Invoke-RestMethod `
    -Uri "http://localhost:8000/billing/public/record-upgrade" `
    -Method POST `
    -Headers @{"Content-Type" = "application/json"} `
    -Body $body

Write-Host "Result: $($response.status)"
```

## Swift (iOS)

```swift
import Foundation

struct UpgradeRequest: Codable {
    let plan_id: String
    let uid: String
    let latitude: Double?
    let longitude: Double?
}

struct CheckoutResponse: Codable {
    let url: String
}

func createUpgradeSession(
    planId: String,
    uid: String,
    token: String,
    latitude: Double? = nil,
    longitude: Double? = nil
) async throws -> String {
    let request = UpgradeRequest(
        plan_id: planId,
        uid: uid,
        latitude: latitude,
        longitude: longitude
    )
    
    var urlRequest = URLRequest(
        url: URL(string: "http://localhost:8000/billing/upgrade-plan")!
    )
    urlRequest.httpMethod = "POST"
    urlRequest.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
    urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
    
    let encoder = JSONEncoder()
    urlRequest.httpBody = try encoder.encode(request)
    
    let (data, response) = try await URLSession.shared.data(for: urlRequest)
    
    guard (response as? HTTPURLResponse)?.statusCode == 200 else {
        throw NSError(domain: "HTTP", code: -1)
    }
    
    let decoder = JSONDecoder()
    let result = try decoder.decode(CheckoutResponse.self, from: data)
    return result.url
}
```

## Java

```java
import java.net.HttpURLConnection;
import java.net.URL;
import java.io.OutputStream;
import org.json.JSONObject;

public class PlanUpgradeClient {
    private static final String BASE_URL = "http://localhost:8000";
    
    public static String createUpgradeSession(
        String planId,
        String uid,
        String token
    ) throws Exception {
        String endpoint = BASE_URL + "/billing/upgrade-plan";
        
        JSONObject payload = new JSONObject();
        payload.put("plan_id", planId);
        payload.put("uid", uid);
        
        URL url = new URL(endpoint);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        
        conn.setRequestMethod("POST");
        conn.setRequestProperty("Authorization", "Bearer " + token);
        conn.setRequestProperty("Content-Type", "application/json");
        conn.setDoOutput(true);
        
        try (OutputStream os = conn.getOutputStream()) {
            os.write(payload.toString().getBytes());
            os.flush();
        }
        
        int code = conn.getResponseCode();
        if (code == 200) {
            // Read and return response
            JSONObject response = new JSONObject(
                new String(conn.getInputStream().readAllBytes())
            );
            return response.getString("url");
        } else {
            throw new Exception("Request failed with code: " + code);
        }
    }
}
```

## Go

```go
package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "net/http"
)

type UpgradeRequest struct {
    PlanID string  `json:"plan_id"`
    UID    string  `json:"uid"`
    Lat    float64 `json:"latitude,omitempty"`
    Lng    float64 `json:"longitude,omitempty"`
}

type CheckoutResponse struct {
    URL string `json:"url"`
}

func createUpgradeSession(
    planID, uid, token string,
) (string, error) {
    payload := UpgradeRequest{
        PlanID: planID,
        UID:    uid,
    }
    
    jsonData, _ := json.Marshal(payload)
    req, _ := http.NewRequest(
        "POST",
        "http://localhost:8000/billing/upgrade-plan",
        bytes.NewBuffer(jsonData),
    )
    
    req.Header.Set("Authorization", fmt.Sprintf("Bearer %s", token))
    req.Header.Set("Content-Type", "application/json")
    
    client := &http.Client{}
    resp, err := client.Do(req)
    if err != nil {
        return "", err
    }
    defer resp.Body.Close()
    
    var result CheckoutResponse
    json.NewDecoder(resp.Body).Decode(&result)
    
    return result.URL, nil
}
```

## GraphQL Query Example

If you're using GraphQL, here's how you might structure this:

```graphql
mutation CreateUpgradeSession(
    $planId: String!
    $uid: String!
    $token: String!
) {
    createUpgradeSession(
        planId: $planId
        uid: $uid
        authToken: $token
    ) {
        url
        sessionId
        status
    }
}

mutation RecordUpgrade(
    $uid: String!
    $planId: String!
) {
    recordUpgrade(
        uid: $uid
        planId: $planId
    ) {
        status
        message
    }
}
```

Variables:
```json
{
    "planId": "pro",
    "uid": "user_123",
    "token": "firebase_token_here"
}
```

## Response Examples

### Success Response - 200 OK
```json
{
    "url": "https://checkout.stripe.com/pay/cs_test_a1b2c3d4e5f6g7h8"
}
```

### Error Response - 401 Unauthorized
```json
{
    "detail": "Unauthorized - Invalid token"
}
```

### Error Response - 404 Not Found
```json
{
    "detail": "User not found"
}
```

### Error Response - 400 Bad Request
```json
{
    "detail": "Invalid plan ID"
}
```

### Error Response - 422 Unprocessable Entity
```json
{
    "detail": [
        {
            "loc": ["body", "uid"],
            "msg": "field required",
            "type": "value_error.missing"
        }
    ]
}
```

## Postman Collection

Import this into Postman for testing:

```json
{
  "info": {
    "name": "Plan Upgrade API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Create Upgrade Session",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{firebase_token}}"
          },
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\"plan_id\": \"pro\", \"uid\": \"{{user_id}}\"}"
        },
        "url": {
          "raw": "{{base_url}}/billing/upgrade-plan",
          "host": ["{{base_url}}"],
          "path": ["billing", "upgrade-plan"]
        }
      }
    },
    {
      "name": "Record Upgrade",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\"uid\": \"{{user_id}}\", \"plan_id\": \"pro\"}"
        },
        "url": {
          "raw": "{{base_url}}/billing/public/record-upgrade",
          "host": ["{{base_url}}"],
          "path": ["billing", "public", "record-upgrade"]
        }
      }
    }
  ],
  "variable": [
    {"key": "base_url", "value": "http://localhost:8000"},
    {"key": "firebase_token", "value": ""},
    {"key": "user_id", "value": ""}
  ]
}
```

---

Choose the example that best fits your tech stack and customize as needed for your application.
