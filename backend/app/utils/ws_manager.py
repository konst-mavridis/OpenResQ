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
