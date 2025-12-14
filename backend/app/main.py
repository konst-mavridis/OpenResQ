from fastapi import FastAPI, WebSocket
from app.routers.auth_routes import router as auth_router
from app.routers.user_routes import router as user_router
from app.routers.incident_routes import router as incident_router
from app.routers.alerts import router as alert_router
from app.routers.reports import router as reports_router
from app.utils.ws_manager import ws_manager


app = FastAPI(title="OpenResQ API")

@app.get("/")
def root():
    return {"status": "OpenResQ backend running"}

app.include_router(auth_router, prefix="/auth")
app.include_router(user_router, prefix="/user")
app.include_router(incident_router, prefix="/incidents")
app.include_router(alert_router, prefix="/alerts")
app.include_router(auth_router)
app.include_router(reports_router)

@app.websocket("/ws/updates")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            # keep connection alive; recv to detect disconnects
            data = await websocket.receive_text()
            # clients can send {"cmd":"subscribe","topic":"responders"} etc (not handled now)
    except Exception:
        pass
    finally:
        ws_manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
