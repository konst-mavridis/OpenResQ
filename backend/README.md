# OpenResQ Backend API

A production-ready FastAPI backend for emergency incident reporting and responder coordination. Built with Firebase, WebSocket real-time updates, and role-based access control.

## Features

✅ **Firebase Authentication** - Secure user authentication without password storage  
✅ **Incident Reporting** - Citizens report emergencies with location and media  
✅ **Responder Coordination** - Real-time WebSocket updates for responders  
✅ **Role-Based Access Control** - Citizens, responders, and admin roles  
✅ **Geographic Filtering** - Area-based incident visibility  
✅ **Rate Limiting** - Protection against abuse  
✅ **Structured Logging** - JSON logs for monitoring  
✅ **Health Checks** - Readiness endpoints for deployment  
✅ **API Documentation** - Interactive Swagger UI  

## Quick Start

### 1. Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your Firebase credentials
# (Get from Firebase Console > Project Settings > Service Accounts)
```

### 2. Run Locally

```bash
python -m uvicorn app.main:app --reload
```

Access the API:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Architecture

### Directory Structure

```
app/
├── main.py              # FastAPI application, routes, WebSocket
├── config.py            # Environment configuration
├── firebase_config.py   # Firebase initialization
├── models/              # (DEPRECATED) SQLAlchemy models
├── schemas/             # Pydantic request/response schemas
├── services/            # Business logic layer
│   ├── auth_service.py      # User authentication & profiles
│   ├── report_service.py    # Incident/report operations
│   └── alert_service.py     # Alert management
├── routers/             # HTTP endpoints
│   ├── auth_routes.py       # Authentication endpoints
│   ├── reports.py           # Report/incident endpoints
│   ├── alerts.py            # Alert endpoints
│   └── user_routes.py       # User profile endpoints
└── utils/               # Helper utilities
    ├── verify.py            # Token verification
    ├── logger.py            # Structured logging
    ├── ws_manager.py        # WebSocket connection manager
    ├── geo.py               # Geographic calculations
    └── roles.py             # Role checking (DEPRECATED)
```

### Technology Stack

- **Framework**: FastAPI 0.104
- **Server**: Uvicorn
- **Database**: Firebase Firestore
- **Auth**: Firebase Authentication
- **Real-time**: WebSocket
- **Rate Limiting**: Slowapi
- **Configuration**: Pydantic Settings

## API Endpoints

### Authentication

```
POST   /auth/register              # Register new user
GET    /auth/me                    # Get current user profile
DELETE /auth/delete                # Delete current user
POST   /auth/users/{uid}/role/{role}  # Update user role (admin only)
```

### Reports/Incidents

```
POST   /reports/                   # Create incident report
GET    /reports/nearby             # Get nearby reports
GET    /reports/{report_id}        # Get specific report
PUT    /reports/{report_id}/status # Update report status (responder)
POST   /reports/{report_id}/notes  # Add responder notes
```

### Alerts

```
POST   /alerts/                    # Create alert (responder)
GET    /alerts/                    # Get active alerts
GET    /alerts/{alert_id}          # Get specific alert
PUT    /alerts/{alert_id}/status   # Update alert status
```

### User Profile

```
GET    /user/me                    # Get user profile
PUT    /user/me/area               # Update area of interest
```

### Health

```
GET    /health                     # Basic health check
GET    /readiness                  # Readiness check (with Firebase connectivity)
```

### WebSocket

```
WS     /ws/updates?token=<id_token>   # Real-time updates
```

## Authentication

All endpoints except registration require Firebase ID tokens in the `Authorization` header:

```
Authorization: Bearer <firebase_id_token>
```

### Getting an ID Token (Client-side)

```javascript
// Firebase JavaScript SDK
const idToken = await user.getIdToken();

// Send with requests
fetch('/api/reports', {
  headers: {
    'Authorization': `Bearer ${idToken}`
  }
});
```

## WebSocket Usage

Connect with Firebase ID token as query parameter:

```javascript
const token = await user.getIdToken();
const ws = new WebSocket(`ws://localhost:8000/ws/updates?token=${token}`);

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  // Handle different message types
  if (data.type === 'new_report') {
    console.log('New incident:', data.report);
  } else if (data.type === 'status_update') {
    console.log('Report updated:', data.report_id, data.status);
  }
};
```

## User Roles

- **citizen**: Can report incidents, view nearby reports, see alerts
- **responder**: Can update incident status, add notes, create alerts
- **admin**: Can do everything + manage user roles

## Request/Response Examples

### Register User

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "secure_password",
    "display_name": "John Doe"
  }'
```

Response:
```json
{
  "uid": "user_id_123",
  "email": "user@example.com",
  "display_name": "John Doe",
  "role": "citizen"
}
```

### Create Report

```bash
curl -X POST http://localhost:8000/reports/ \
  -H "Authorization: Bearer <id_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Fire in building",
    "description": "Fire on 2nd floor",
    "event_type": "fire",
    "severity": "critical",
    "latitude": 37.9838,
    "longitude": 23.7275,
    "media": []
  }'
```

Response:
```json
{
  "id": "report_uuid",
  "uid": "user_id",
  "title": "Fire in building",
  "description": "Fire on 2nd floor",
  "event_type": "fire",
  "severity": "critical",
  "latitude": 37.9838,
  "longitude": 23.7275,
  "status": "pending",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

## Environment Variables

### Required

- `FIREBASE_PROJECT_ID` - Your Firebase project ID
- `FIREBASE_STORAGE_BUCKET` - Storage bucket (e.g., gs://bucket.appspot.com)
- `FIREBASE_CREDENTIALS` - Service account JSON (base64 or raw JSON)

### Optional

- `APP_ENV` - Environment (development/production, default: development)
- `HOST` - Server host (default: 0.0.0.0)
- `PORT` - Server port (default: 8000)
- `LOG_LEVEL` - Logging level (default: INFO)
- `CORS_ORIGINS` - Allowed origins (default: *)
- `RATE_LIMIT_ENABLED` - Enable rate limiting (default: true)

See `.env.example` for all options.

## Development

### Install Dev Dependencies

```bash
pip install -r requirements.txt
pip install pytest pytest-asyncio httpx
```

### Run Tests

```bash
pytest tests/ -v
```

### Code Style

```bash
# Format code
black app/

# Lint
flake8 app/

# Type checking
mypy app/
```

## Deployment

### Quick Deploy to Render

1. Push code to GitHub
2. Connect GitHub repo to Render
3. Set environment variables in Render dashboard
4. Deploy!

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions for:
- Render
- Heroku
- Docker
- Custom servers

## Security

- ✅ No passwords stored (Firebase handles authentication)
- ✅ Credentials loaded from environment variables only
- ✅ WebSocket connections require authentication
- ✅ Role-based access control on all endpoints
- ✅ Rate limiting protects against abuse
- ✅ Structured logging for audit trail
- ✅ CORS configured by environment

## Monitoring

### Health Checks

```bash
# Basic health
curl http://localhost:8000/health

# Readiness (checks Firebase connectivity)
curl http://localhost:8000/readiness
```

### Logs

All critical actions are logged as structured JSON:
- User registration
- Report creation/updates
- Role changes
- Authentication failures
- System errors

View logs:
```bash
# Development
# Logs printed to console

# Render
# Dashboard > Service > Logs

# Docker
docker logs <container_id>
```

## Performance

- **Rate Limiting**: 60 requests/minute per IP
- **WebSocket**: Automatic area-based filtering
- **Database**: Firestore indexes optimized for common queries
- **Caching**: User profiles cached on authentication

## Contributing

1. Create feature branch: `git checkout -b feature/name`
2. Make changes and commit: `git commit -am "Add feature"`
3. Push to branch: `git push origin feature/name`
4. Open pull request

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Support

For issues and questions:
1. Check [DEPLOYMENT.md](DEPLOYMENT.md) for deployment issues
2. Review Firebase documentation: https://firebase.google.com/docs
3. Check logs for error details
4. Open an issue on GitHub

## License

MIT License - See LICENSE file for details

## Changelog

### v1.0.0 (Current)
- ✅ Firebase-based authentication
- ✅ Incident reporting system
- ✅ Responder coordination
- ✅ Real-time WebSocket updates
- ✅ Role-based access control
- ✅ Rate limiting
- ✅ Structured logging
- ✅ Health monitoring
- ✅ Production-ready deployment guides

---

**Status**: Production-ready for deployment  
**Last Updated**: January 2024  
**Maintainer**: OpenResQ Team
