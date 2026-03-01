"""
OpenResQ Backend - Production-ready API server.
Handles incident reporting, responder coordination, and real-time updates.
"""
import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, HTTPException
from fastapi_utils.tasks import repeat_every
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import get_settings
from app.firebase_config import initialize_firebase, get_db, get_auth
from app.routers.auth_routes import router as auth_router
from app.routers.user_routes import router as user_router
from app.routers.reports import router as reports_router
from app.routers.alerts import router as alerts_router
from app.routers import admin, responders
from app.routers import admin_reports
from app.utils.ws_manager import ws_manager
from app.utils.logger import get_logger
from app.routers import votes
from app.routers import admin_analytics, admin_responders
from app.routers import teams  # <--- add teams router import
from app.services.live_responders_service import start_responder_listener
from app.services.duty_monitor_service import check_responder_activity
from app.routers.responders import router as responders_router
# from services.fcm_service import send_push_to_token

# Initialize logger
logger = get_logger(__name__)
settings = get_settings()

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title="OpenResQ API",
    description="Emergency incident reporting and responder coordination system",
    version="1.0.0",
)

@app.on_event("startup")
@repeat_every(seconds=300) # every 5 minutes 
def monitor_responder_activity(): 
    check_responder_activity()

@app.on_event("startup")
async def startup_event():
    logger.info("Starting OpenResQ backend")
    try:
        initialize_firebase()
        logger.info("Firebase initialized successfully")
        start_responder_listener()
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")
        raise

# Add rate limiter to app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, lambda request, exc: HTTPException(status_code=429, detail="Rate limit exceeded"))

# Configure CORS
cors_origins = settings.cors_origins.split(",") if settings.cors_origins else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== Health & Status Endpoints =====

@app.get("/", tags=["Health"])
def root():
    """Root endpoint - confirms API is running."""
    return {
        "status": "running",
        "name": "OpenResQ API",
        "environment": settings.app_env,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health", tags=["Health"])
def health_check():
    """
    Health check endpoint.
    Returns 200 if service is operational.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "openresq-api"
    }


@app.get("/readiness", tags=["Health"])
def readiness_check():
    """
    Readiness check endpoint.
    Verifies Firebase connectivity and configuration.
    Returns 200 only if ready to handle requests.
    """
    try:
        # Check Firebase connection
        db = get_db()
        auth = get_auth()
        
        # Verify Firestore is accessible by checking collections
        db.collection("users").limit(1).stream()
        
        return {
            "ready": True,
            "timestamp": datetime.utcnow().isoformat(),
            "firebase": "connected",
            "firestore": "accessible"
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {
            "ready": False,
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }, 503



# ===== API Routes =====

# Include routers
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(reports_router)
app.include_router(alerts_router)
app.include_router(admin.router)
app.include_router(votes.router)
app.include_router(admin_reports.router)
app.include_router(admin_analytics.router)
app.include_router(admin_responders.router)
app.include_router(teams.router)  # include teams endpoints
app.include_router(responders_router)

# ===== WebSocket Endpoint =====

@app.websocket("/ws/updates")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(None)
):
    """
    Secure WebSocket endpoint for real-time updates.
    
    Requires Firebase ID token as query parameter: /ws/updates?token=<id_token>
    
    Broadcasts:
    - New reports to responders in area
    - Status updates to interested users
    - Alerts to relevant responders
    """
    try:
        # Authenticate and connect
        query_params = {"token": token}
        await ws_manager.connect(websocket, query_params)
        
        try:
            while True:
                # Keep connection alive and handle incoming messages
                data = await websocket.receive_text()
                
                try:
                    import json
                    message = json.loads(data)
                    command = message.get("cmd")
                    
                    # Handle client commands (for future extensibility)
                    if command == "ping":
                        connection = ws_manager.get_connection_by_uid(
                            message.get("uid")
                        )
                        if connection:
                            await connection.send_json({"cmd": "pong"})
                    
                except json.JSONDecodeError:
                    pass
                except Exception as e:
                    logger.warning(f"Error handling WebSocket message: {e}")
                    
        except WebSocketDisconnect:
            ws_manager.disconnect(websocket)
            logger.info("WebSocket client disconnected")
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            ws_manager.disconnect(websocket)
            
    except Exception as e:
        logger.warning(f"WebSocket connection failed: {e}")
        # Connection already rejected in ws_manager.connect()


# ===== Error Handlers =====

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return {
        "error": "Internal server error",
        "timestamp": datetime.utcnow().isoformat()
    }, 500


# ===== Startup Script =====

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_development(),
        log_level=settings.log_level.lower()
    )

