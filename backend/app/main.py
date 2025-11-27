from fastapi import FastAPI
from app.routers import users, alerts, reports, hazards, admin

app = FastAPI(title="OpenResQ Backend")

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
app.include_router(reports.router, prefix="/reports", tags=["reports"])
app.include_router(hazards.router, prefix="/hazards", tags=["hazards"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
