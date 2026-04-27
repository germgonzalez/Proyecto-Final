from fastapi import APIRouter
from app.api.v1.endpoints import nodes, telemetry, commands, alerts

api_router = APIRouter()

api_router.include_router(nodes.router, prefix="/nodes", tags=["nodes"])
api_router.include_router(telemetry.router, prefix="/nodes", tags=["telemetry"])
api_router.include_router(commands.router, prefix="/nodes", tags=["commands"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
