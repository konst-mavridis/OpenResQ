# OpenResQ Backend - Quick Start Guide

Get the backend running in 5 minutes.

## Prerequisites

- Python 3.9+
- Firebase Account with Admin SDK
- Git

## Step 1: Get Firebase Credentials

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Select your OpenResQ project
3. Go to Settings (⚙️) > Project Settings > Service Accounts
4. Click "Generate New Private Key"
5. Save the JSON file content

## Step 2: Clone & Setup

```bash
# Clone repository
git clone <repo-url>
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 3: Configure Environment

```bash
# Copy template
cp .env.example .env

# Edit .env with your values
# Replace these with your Firebase credentials:
# - FIREBASE_PROJECT_ID
# - FIREBASE_STORAGE_BUCKET
# - FIREBASE_CREDENTIALS (the JSON key content)

nano .env  # or use your editor
```

Example `.env`:
```
APP_ENV=development
FIREBASE_PROJECT_ID=openresq-b4c5f
FIREBASE_STORAGE_BUCKET=gs://openresq-b4c5f.firebasestorage.app
FIREBASE_CREDENTIALS='{"type":"service_account","project_id":"..."}'
```

## Step 4: Run Server

```bash
python -m uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

## Step 5: Test API

### Option A: Interactive Docs
Visit `http://localhost:8000/docs` in your browser

### Option B: Command Line

**Register a user:**
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePassword123",
    "display_name": "Test User"
  }'
```

You should get:
```json
{
  "uid": "user_id_123",
  "email": "test@example.com",
  "display_name": "Test User",
  "role": "citizen"
}
```

## Common Issues

### Firebase Credentials Error
- Check `.env` file exists and is readable
- Ensure `FIREBASE_CREDENTIALS` is valid JSON
- Verify Firebase project is selected

### Port 8000 Already in Use
```bash
# Use different port
python -m uvicorn app.main:app --port 8001
```

### Missing Dependencies
```bash
# Reinstall all packages
pip install -r requirements.txt --force-reinstall
```

## Next Steps

1. **Read the API docs** at `http://localhost:8000/docs`
2. **Explore endpoints** in the Swagger UI
3. **Review** [README.md](README.md) for full API documentation
4. **Deploy** using [DEPLOYMENT.md](DEPLOYMENT.md)

## Available Endpoints

```
POST   /auth/register          # Register user
GET    /auth/me                # Get current user
DELETE /auth/delete            # Delete account

POST   /reports/               # Create report
GET    /reports/nearby         # Get nearby reports
GET    /reports/{id}           # Get specific report
PUT    /reports/{id}/status    # Update status

POST   /alerts/                # Create alert
GET    /alerts/                # Get alerts

GET    /user/me                # Get user profile
PUT    /user/me/area           # Update area

GET    /health                 # Health check
GET    /readiness              # Readiness check
```

## Docker (Alternative)

```bash
# Build image
docker build -t openresq-api .

# Run container
docker run -p 8000:8000 \
  -e FIREBASE_PROJECT_ID=your-project \
  -e FIREBASE_CREDENTIALS='...' \
  -e FIREBASE_STORAGE_BUCKET=your-bucket \
  openresq-api
```

## More Help

- **API Documentation**: [README.md](README.md)
- **Deployment Guide**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Architecture Overview**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Refactoring Details**: [REFACTORING_COMPLETE.md](REFACTORING_COMPLETE.md)

---

**Stuck?** Check the docs above or review the interactive API docs at `/docs`
