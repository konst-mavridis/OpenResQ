# OpenResQ Backend - Deployment Guide

## Overview

This guide covers deploying the OpenResQ backend to production environments. The application is designed to run on cloud platforms like Render, Heroku, or similar PaaS providers.

## Prerequisites

- Python 3.9+
- Firebase Project with Admin SDK credentials
- Cloud platform account (Render, Heroku, etc.)
- Domain name (optional, for custom domains)

## Architecture

- **Framework**: FastAPI
- **Database**: Firebase Firestore
- **Authentication**: Firebase Authentication
- **Real-time Updates**: WebSocket
- **Rate Limiting**: Slowapi

## Local Development

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your Firebase credentials:

```bash
cp .env.example .env
```

Edit `.env` with your Firebase project details:
- `FIREBASE_PROJECT_ID`: Your Firebase project ID
- `FIREBASE_STORAGE_BUCKET`: Your storage bucket
- `FIREBASE_CREDENTIALS`: Service account JSON

### 3. Run Locally

```bash
python -m uvicorn app.main:app --reload
```

Server will start at `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

## Deployment to Render

### 1. Prepare Repository

Ensure the following files are in your repo:
- `requirements.txt` - Dependencies
- `app/` - Application code
- `.env.example` - Configuration template
- `.gitignore` - Excludes `.env` and sensitive files

### 2. Create Render Service

1. Go to [render.com](https://render.com)
2. Create new "Web Service"
3. Connect GitHub repository
4. Configure:
   - **Name**: `openresq-api`
   - **Environment**: Python 3.11
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Python Version**: 3.11

### 3. Set Environment Variables

In Render dashboard, add environment variables:

```
APP_ENV=production
DEBUG=false
LOG_LEVEL=INFO
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_STORAGE_BUCKET=gs://your-bucket.firebasestorage.app
FIREBASE_CREDENTIALS=<your-service-account-json>
LOG_FORMAT=json
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
WS_AUTH_REQUIRED=true
```

### 4. Deploy

- Push to main branch triggers automatic deployment
- Monitor logs in Render dashboard

## Deployment to Heroku

### 1. Install Heroku CLI

```bash
# macOS
brew tap heroku/brew && brew install heroku

# Windows
# Download from https://devcenter.heroku.com/articles/heroku-cli
```

### 2. Create Procfile

Create `Procfile` in root:

```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### 3. Create Heroku App

```bash
heroku login
heroku create openresq-api
```

### 4. Set Environment Variables

```bash
heroku config:set APP_ENV=production
heroku config:set FIREBASE_PROJECT_ID=your-project-id
heroku config:set FIREBASE_CREDENTIALS="$(cat path/to/serviceAccountKey.json)"
# ... set other variables
```

### 5. Deploy

```bash
git push heroku main
```

## Docker Deployment

### 1. Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Build and Run

```bash
docker build -t openresq-api .
docker run -p 8000:8000 --env-file .env openresq-api
```

## Firebase Configuration

### Getting Service Account Credentials

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Select your project
3. Go to Settings (gear icon) > Project Settings
4. Click "Service Accounts" tab
5. Click "Generate New Private Key"
6. This JSON file contains your credentials

### Setting Up Firestore

1. In Firebase Console, go to Firestore Database
2. Create a new Firestore database in:
   - **Location**: Choose closest to users
   - **Security Rules Mode**: Start in test mode (update for production)

### Firestore Security Rules (Production)

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can read/write their own profile
    match /users/{uid} {
      allow read: if request.auth.uid == uid;
      allow write: if request.auth.uid == uid || isAdmin(request.auth.uid);
    }
    
    // Reports
    match /reports/{document=**} {
      allow read: if isAuthenticated();
      allow create: if isAuthenticated();
      allow update: if isReporter(resource.data.uid) || isResponder(request.auth.uid);
    }
    
    // Alerts
    match /alerts/{document=**} {
      allow read: if isResponder(request.auth.uid);
      allow create: if isResponder(request.auth.uid);
      allow update: if isResponder(request.auth.uid);
    }
    
    // Helper functions
    function isAuthenticated() {
      return request.auth != null;
    }
    
    function isAdmin(uid) {
      return get(/databases/$(database)/documents/users/$(uid)).data.role == 'admin';
    }
    
    function isResponder(uid) {
      let userRole = get(/databases/$(database)/documents/users/$(uid)).data.role;
      return userRole in ['responder', 'admin'];
    }
    
    function isReporter(uid) {
      return request.auth.uid == uid;
    }
  }
}
```

## Health Monitoring

### Health Checks

The API provides health check endpoints for monitoring:

- `GET /health` - Basic health check
- `GET /readiness` - Readiness check (includes Firestore connectivity)

For Render/Heroku, configure health checks to:
```
Path: /readiness
Interval: 60 seconds
Timeout: 10 seconds
```

### Logging

All critical actions are logged with structured JSON logging:
- Report creation/updates
- Role changes
- Authentication failures
- System errors

View logs:
- **Render**: Dashboard > Service > Logs
- **Heroku**: `heroku logs --tail`
- **Docker**: `docker logs <container-id>`

## Performance Optimization

### Rate Limiting

Default rate limits per IP:
- General requests: 60/minute
- Write operations: 100/hour

Configure in `.env`:
```
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=60
RATE_LIMIT_WRITE_PER_HOUR=100
```

### WebSocket Optimization

- Connections require Firebase authentication
- Role and area-based filtering reduces message volume
- Heartbeat every 30 seconds (configurable)

## Security Checklist

- [ ] Firebase credentials loaded from environment variables only
- [ ] Never commit `.env` file
- [ ] CORS configured for allowed domains only
- [ ] WebSocket requires authentication
- [ ] Firestore security rules configured
- [ ] Admin API keys rotated regularly
- [ ] HTTPS enabled (automatic on Render/Heroku)
- [ ] Rate limiting enabled
- [ ] Logging enabled for audit trail
- [ ] API keys/tokens never logged

## Troubleshooting

### Firebase Connection Issues

```bash
# Test Firebase connectivity
curl https://your-api.com/readiness
```

Response should show `"firebase": "connected"`

### WebSocket Connection Failures

- Verify client sends valid Firebase ID token
- Check `/readiness` endpoint status
- Review server logs for authentication errors

### High Memory Usage

- Check for memory leaks in WebSocket connections
- Monitor concurrent connections: `curl https://your-api.com/ws/stats`
- Scale horizontally if needed

## Scaling

For production with high load:

1. **Horizontal Scaling** (Render, Heroku, Kubernetes)
   - Multiple instances handle load balancing
   - Each instance maintains separate WebSocket connections

2. **Database Scaling**
   - Firestore auto-scales
   - Create composite indexes for complex queries

3. **CDN for Static Content**
   - Put media files on Cloud Storage with CDN

## Support & Monitoring

- Monitor API endpoint: `https://your-api.com/health`
- Set up alerting on `/readiness` failures
- Review logs for errors daily
- Monitor WebSocket connection count

## Next Steps

1. Complete Firebase setup
2. Deploy to staging environment
3. Run integration tests
4. Configure monitoring/alerting
5. Deploy to production
6. Monitor for 24 hours

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Firebase Admin Python SDK](https://firebase.google.com/docs/database/admin/start-python)
- [Render Deployment Docs](https://render.com/docs)
- [Firestore Documentation](https://firebase.google.com/docs/firestore)
