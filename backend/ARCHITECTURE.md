# OpenResQ Backend - Architecture & Design

## Overview

OpenResQ backend is a production-ready FastAPI application built with clean architecture principles. The system separates concerns into distinct layers: HTTP handling (routers), business logic (services), and utility functions.

## Architecture Layers

### 1. **HTTP Layer** (Routers)
Located in `app/routers/`

Responsibilities:
- Accept HTTP requests
- Validate request format (Pydantic schemas handle this)
- Call appropriate service methods
- Return HTTP responses with proper status codes

Files:
- `auth_routes.py` - User registration, authentication endpoints
- `reports.py` - Incident reporting endpoints
- `alerts.py` - Alert management endpoints
- `user_routes.py` - User profile management

**Key Principle**: Routers are thin - they don't contain business logic.

```python
# Example: Router calls service
@router.post("/reports/")
def create_report(data: CreateReport, user=Depends(verify_token)):
    # Call service
    report = report_service.create_report(
        user_id=user["uid"],
        title=data.title,
        ...
    )
    return report
```

### 2. **Business Logic Layer** (Services)
Located in `app/services/`

Responsibilities:
- Implement all business logic
- Handle database operations
- Manage relationships between entities
- Enforce business rules
- Generate audit logs

Files:
- `auth_service.py` - User authentication and profile management
- `report_service.py` - Incident lifecycle management
- `alert_service.py` - Alert operations
- `validation_service.py` - Input validation rules

**Key Principle**: Services are reusable across different HTTP endpoints.

```python
# Example: Service encapsulates business logic
class ReportService:
    def create_report(self, user_id, title, ...):
        # Validate input
        # Create in Firestore
        # Send notifications
        # Log action
        # Return result
```

### 3. **Authentication Layer** (Utilities)
Located in `app/utils/verify.py`

Responsibilities:
- Verify Firebase ID tokens
- Extract user context
- Auto-create user profiles
- Provide role-based access control

**Key Feature**: All endpoints require Firebase authentication (except registration).

```python
# Example: Dependency injection for authentication
@router.get("/reports/{report_id}")
def get_report(report_id: str, user=Depends(verify_token)):
    # user is already authenticated and has role
    pass
```

### 4. **Configuration Layer** (Config)
Located in `app/config.py`

Responsibilities:
- Load all configuration from environment variables
- Validate configuration on startup
- Provide settings to application
- Support different environments (dev, staging, prod)

**Key Principle**: No hardcoded secrets or configuration values.

```python
settings = get_settings()
print(settings.firebase_project_id)  # Loaded from env
```

### 5. **Data Access Layer** (Firebase)
Located in `app/firebase_config.py`

Responsibilities:
- Initialize Firebase Admin SDK
- Provide database clients
- Handle Firebase credential loading

**Current Database**: Firestore (NoSQL document database)

```
Firestore Collections:
├── users/           - User profiles with roles and areas
├── reports/         - Incident reports
├── alerts/          - Active alerts
└── media/           - Media attachments
```

### 6. **Utility Functions**
Located in `app/utils/`

- `logger.py` - Structured JSON logging
- `ws_manager.py` - WebSocket connection management
- `geo.py` - Geographic distance calculations
- `verify.py` - Token verification

## Data Flow

### Example: Create Report

```
Client Request (HTTP POST /reports/)
    ↓
[Router Layer] reports.py
  - Validate schema (Pydantic)
  - Check authentication (verify_token dependency)
    ↓
[Service Layer] report_service.py
  - Validate business rules (validation_service)
  - Create in Firestore
  - Log action (logger)
  - Send notifications (ws_manager)
    ↓
[Database Layer] Firestore
  - Store report document
    ↓
[Response] HTTP 200 + report data
```

## Key Design Patterns

### 1. **Dependency Injection**

FastAPI's `Depends()` is used throughout:

```python
# Authentication dependency
@router.get("/user")
def get_user(user=Depends(verify_token)):
    pass

# Role-based access dependency
@router.put("/reports/{id}/status")
def update_status(responder=Depends(require_role("responder", "admin"))):
    pass
```

### 2. **Service Pattern**

Services encapsulate domain logic:

```python
class ReportService:
    def __init__(self):
        self.db = get_db()
        self.fcm = get_fcm()
    
    def create_report(self, ...):
        # Business logic here
        pass
```

### 3. **Validation Pattern**

Input validation in two places:

1. **Schema Level** - Pydantic handles format validation
   ```python
   class CreateReport(BaseModel):
       title: str = Field(..., min_length=1, max_length=200)
       latitude: float = Field(..., ge=-90, le=90)
   ```

2. **Business Logic Level** - Services validate business rules
   ```python
   InputValidator.validate_report(title, event_type, ...)
   ```

### 4. **Authentication Pattern**

Lightweight, stateless token verification:

```python
def verify_token(authorization: str = Header(None)):
    # 1. Extract token from header
    # 2. Verify with Firebase Admin SDK
    # 3. Get user profile from Firestore
    # 4. Return user context
```

## Database Schema

### Users Collection

```json
{
  "uid": "firebase_user_id",
  "email": "user@example.com",
  "display_name": "John Doe",
  "role": "citizen|responder|admin",
  "area": {
    "latitude": 37.9838,
    "longitude": 23.7275,
    "radius_km": 20.0
  },
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

### Reports Collection

```json
{
  "id": "uuid",
  "uid": "reporter_user_id",
  "title": "Fire in building",
  "description": "Fire on 2nd floor",
  "event_type": "fire",
  "severity": "critical",
  "latitude": 37.9838,
  "longitude": 23.7275,
  "media": [],
  "status": "pending|in_progress|resolved|closed",
  "responder_notes": [
    {
      "responder_id": "responder_uid",
      "text": "Dispatch sent",
      "timestamp": "2024-01-15T10:35:00"
    }
  ],
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

### Alerts Collection

```json
{
  "id": "uuid",
  "uid": "creator_user_id",
  "title": "Fire Warning",
  "message": "Multiple fires reported downtown",
  "level": "info|warning|critical",
  "status": "active|resolved|archived",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

## Security Architecture

### Authentication Flow

```
1. Client registers/logs in with Firebase (client-side)
2. Firebase returns ID token
3. Client sends token in Authorization header: "Bearer <id_token>"
4. Backend verifies token with Firebase Admin SDK
5. Backend creates/fetches user profile from Firestore
6. User context available in request
```

### Authorization

```
- Roles: citizen, responder, admin
- Role-based access control via require_role() dependency
- User location area defines visibility of reports
```

### Data Security

```
✓ No passwords stored in backend
✓ No sensitive data logged
✓ Firebase security rules enforce access control
✓ Rate limiting prevents abuse
✓ All credentials from environment variables
```

## Real-time Updates

### WebSocket Architecture

```
Client connects to /ws/updates?token=<id_token>
    ↓
WebSocket Manager authenticates user
    ↓
Connection stored with user metadata (role, area)
    ↓
New reports/alerts trigger broadcasts
    ↓
Manager filters recipients by:
  - Role (responders only, citizen only, etc.)
  - Geographic area (users within radius)
    ↓
Message sent only to relevant clients
```

### Message Types

```json
{
  "type": "new_report",
  "report_id": "uuid",
  "report": {...}
}

{
  "type": "status_update",
  "report_id": "uuid",
  "status": "in_progress"
}

{
  "type": "new_alert",
  "alert_id": "uuid",
  "alert": {...}
}
```

## Logging Architecture

### Structured Logging

All logs are JSON for easy parsing:

```json
{
  "timestamp": "2024-01-15T10:30:00.123Z",
  "level": "INFO",
  "logger": "app.services.report_service",
  "message": "report_creation: success",
  "action": "report_creation",
  "status": "success",
  "user_id": "user_123",
  "resource_id": "report_456"
}
```

### Critical Actions Logged

- User registration
- Report creation/updates
- Role changes
- Authentication failures
- WebSocket connections
- System errors

## Deployment Considerations

### Stateless Design

Each instance can handle any request:
- No session storage
- Authentication via JWT/Firebase token
- User context fetched per request
- WebSocket state local to instance

### Horizontal Scaling

- Multiple instances behind load balancer
- Each instance independent
- Shared Firestore database
- WebSocket connections per instance (local)

### Performance

- Firestore queries indexed
- User profiles cached on auth
- Rate limiting per IP
- WebSocket filters reduce message volume

## Technology Choices & Tradeoffs

### FastAPI
✓ Fast, modern Python framework
✓ Automatic API documentation
✓ Async/await support
✓ Built-in validation (Pydantic)
✗ Smaller ecosystem than Django

### Firebase
✓ No backend database management
✓ Built-in authentication
✓ Real-time capabilities
✓ Integrated storage
✗ Higher costs at scale
✗ Limited query flexibility

### Firestore
✓ Automatic scaling
✓ Real-time synchronization
✓ Built-in security rules
✗ Limited JOIN operations
✗ No complex transactions

### WebSocket
✓ Real-time push updates
✓ Reduced polling overhead
✓ Better UX
✗ Requires connection management
✗ More complex deployment

## Future Improvements

### Caching
- Redis layer for frequently accessed data
- User profile caching
- Report filtering results

### Message Queue
- Asynchronous task processing
- Notification queue
- Batch operations

### Search
- Elasticsearch for report search
- Full-text search capabilities
- Complex filtering

### Analytics
- User activity tracking
- Report trends analysis
- System performance monitoring

## File Structure Explained

```
app/
├── main.py
│   └── FastAPI app initialization, routes, WebSocket
│
├── config.py
│   └── Environment configuration (Settings class)
│
├── firebase_config.py
│   └── Firebase SDK initialization
│
├── models/
│   └── (DEPRECATED - kept for reference)
│       SQLAlchemy ORM models for SQL database
│
├── schemas/
│   └── Pydantic models for request/response validation
│       ├── report.py
│       ├── user.py
│       ├── alert.py
│       ├── hazard.py
│       └── media.py
│
├── services/
│   └── Business logic layer
│       ├── auth_service.py
│       ├── report_service.py
│       ├── alert_service.py
│       └── validation_service.py
│
├── routers/
│   └── HTTP endpoint handlers
│       ├── auth_routes.py
│       ├── reports.py
│       ├── alerts.py
│       ├── user_routes.py
│       └── (incident_routes.py - DEPRECATED)
│
└── utils/
    └── Shared utilities
        ├── verify.py        - Token verification
        ├── logger.py        - Structured logging
        ├── ws_manager.py    - WebSocket management
        ├── geo.py           - Geographic calculations
        └── roles.py         - (DEPRECATED)
```

## Best Practices Followed

1. **Separation of Concerns** - Each layer has single responsibility
2. **DRY** - Business logic in services, reused across endpoints
3. **Type Safety** - Pydantic for runtime validation, type hints throughout
4. **Error Handling** - Proper HTTP status codes, detailed error messages
5. **Logging** - Structured logging for troubleshooting
6. **Documentation** - Docstrings, type hints, API documentation
7. **Security** - Authentication on all endpoints, no secrets in code
8. **Testing** - Clear function interfaces enable unit testing
9. **Configuration** - Environment-based, no hardcoding
10. **Scalability** - Stateless design enables horizontal scaling

---

**Last Updated**: January 2024  
**Version**: 1.0.0  
**Status**: Production-ready
