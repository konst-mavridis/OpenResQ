<<<<<<< HEAD
"""
WebSocket connection manager with authentication and role-based filtering.
Handles secure WebSocket connections, user identification, and event filtering.
"""
from typing import List, Dict, Any, Optional
from fastapi import WebSocket, HTTPException
import asyncio
import logging
import json
from datetime import datetime
from app.firebase_config import get_auth, get_db
from app.utils.geo import is_within_radius

logger = logging.getLogger(__name__)


class AuthenticatedConnection:
    """Represents an authenticated WebSocket connection."""
    
    def __init__(self, websocket: WebSocket, uid: str, role: str, area: Dict[str, Any]):
        self.websocket = websocket
        self.uid = uid
        self.role = role
        self.area = area
        self.connected_at = datetime.utcnow()
    
    async def send_json(self, data: dict):
        """Send JSON data to client."""
        try:
            await self.websocket.send_json(data)
        except Exception as e:
            logger.warning(f"Failed to send message to {self.uid}: {e}")
    
    async def send_text(self, text: str):
        """Send text data to client."""
        try:
            await self.websocket.send_text(text)
        except Exception as e:
            logger.warning(f"Failed to send text to {self.uid}: {e}")


class ConnectionManager:
    """Manages authenticated WebSocket connections with role/area-based filtering."""
    
    def __init__(self):
        self.active_connections: List[AuthenticatedConnection] = []
        self._auth = None
        self._db = None
    
    async def _verify_and_authenticate(self, query_params: dict) -> tuple[str, Dict[str, Any]]:
        """
        Verify WebSocket connection token and authenticate user.
        
        Args:
            query_params: Query parameters from WebSocket connection URL
        
        Returns:
            Tuple of (uid, user_data)
        
        Raises:
            Exception: If authentication fails
        """
        token = query_params.get("token") or query_params.get("access_token")
        
        if not token:
            raise Exception("Missing authentication token in WebSocket handshake")
        
        try:
            if not self._auth:
                from app.firebase_config import get_auth
                self._auth = get_auth()
            
            decoded = self._auth.verify_id_token(token)
            uid = decoded.get("uid") or decoded.get("sub")
            
            if not uid:
                raise Exception("Invalid token: no user ID")
            
            # Get user profile
            if not self._db:
                from app.firebase_config import get_db
                self._db = get_db()
            
            user_doc = self._db.collection("users").document(uid).get()
            if user_doc.exists:
                user_data = user_doc.to_dict()
            else:
                user_data = {
                    "uid": uid,
                    "role": "citizen",
                    "area": {
                        "latitude": 37.9838,
                        "longitude": 23.7275,
                        "radius_km": 20.0
                    }
                }
            
            return uid, user_data
        except Exception as e:
            logger.error(f"WebSocket authentication failed: {e}")
            raise
    
    async def connect(self, websocket: WebSocket, query_params: dict):
        """
        Accept and authenticate a WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            query_params: Query parameters with token
        """
        try:
            # Verify and authenticate
            uid, user_data = await self._verify_and_authenticate(query_params)
            
            # Accept connection
            await websocket.accept()
            
            # Create authenticated connection
            role = user_data.get("role", "citizen")
            area = user_data.get("area", {})
            conn = AuthenticatedConnection(websocket, uid, role, area)
            
            self.active_connections.append(conn)
            
            logger.info(f"WebSocket client connected: {uid} ({role})")
            
            # Send welcome message
            await conn.send_json({
                "type": "connection",
                "status": "connected",
                "uid": uid,
                "role": role
            })
            
        except Exception as e:
            logger.warning(f"WebSocket connection rejected: {e}")
            await websocket.close(code=1008, reason=str(e))
            raise
    
    def disconnect(self, websocket: WebSocket):
        """Disconnect a WebSocket connection."""
        self.active_connections = [
            conn for conn in self.active_connections
            if conn.websocket != websocket
        ]
    
    def get_connection_by_uid(self, uid: str) -> Optional[AuthenticatedConnection]:
        """Get connection by user ID."""
        for conn in self.active_connections:
            if conn.uid == uid:
                return conn
        return None
    
    async def broadcast(self, message: dict, filter_by_role: Optional[str] = None):
        """
        Broadcast message to connected clients.
        
        Args:
            message: Message data to broadcast
            filter_by_role: Optional role to filter recipients
        """
        if not self.active_connections:
            return
        
        recipients = self.active_connections
        
        # Filter by role if specified
        if filter_by_role:
            recipients = [
                conn for conn in recipients
                if conn.role == filter_by_role
            ]
        
        # Send concurrently
        coros = [conn.send_json(message) for conn in recipients]
        results = await asyncio.gather(*coros, return_exceptions=True)
        
        # Log any failures
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.warning(f"Broadcast to {recipients[i].uid} failed: {result}")
    
    async def broadcast_to_area(
        self,
        message: dict,
        latitude: float,
        longitude: float,
        radius_km: float,
        filter_by_role: Optional[str] = None
    ):
        """
        Broadcast message to users within a geographic area.
        
        Args:
            message: Message data to broadcast
            latitude: Center latitude
            longitude: Center longitude
            radius_km: Radius in kilometers
            filter_by_role: Optional role to filter recipients
        """
        recipients = []
        
        for conn in self.active_connections:
            # Check role filter
            if filter_by_role and conn.role != filter_by_role:
                continue
            
            # Check area filter
            user_lat = conn.area.get("latitude")
            user_lng = conn.area.get("longitude")
            
            if user_lat and user_lng:
                if is_within_radius(latitude, longitude, user_lat, user_lng, radius_km):
                    recipients.append(conn)
        
        # Send to filtered recipients
        coros = [conn.send_json(message) for conn in recipients]
        results = await asyncio.gather(*coros, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.warning(f"Area broadcast to {recipients[i].uid} failed: {result}")
    
    async def send_to_user(self, uid: str, message: dict):
        """Send message to specific user."""
        conn = self.get_connection_by_uid(uid)
        if conn:
            await conn.send_json(message)
        else:
            logger.debug(f"User {uid} not connected via WebSocket")
    
    def get_connected_responders(self) -> List[str]:
        """Get list of connected responder UIDs."""
        return [
            conn.uid for conn in self.active_connections
            if conn.role in ["responder", "admin"]
        ]
    
    def get_connection_count(self) -> int:
        """Get total number of connected clients."""
        return len(self.active_connections)


ws_manager = ConnectionManager()

=======
from typing import List
from fastapi import WebSocket
import asyncio
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        # send concurrently
        if not self.active_connections:
            return
        data = message
        coros = []
        for conn in self.active_connections:
            coros.append(conn.send_json(data))
        await asyncio.gather(*coros, return_exceptions=True)

ws_manager = ConnectionManager()
>>>>>>> 327748fd30086a4fd58a614cd888531a2bd9417a
