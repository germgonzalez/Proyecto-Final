from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.api.deps import get_db_session
from app.crud import node as node_crud, telemetry as telemetry_crud
from app.schemas.telemetry import TelemetryIngest, TelemetryResponse

router = APIRouter()


@router.post("/{device_code}/telemetry", response_model=TelemetryResponse)
async def ingest_telemetry(
    device_code: str,
    data: TelemetryIngest,
    db: AsyncSession = Depends(get_db_session),
):
    node = await node_crud.get_by_device_code(db, device_code)
    if not node:
        raise HTTPException(status_code=404, detail="Nodo no encontrado")
    await node_crud.update_last_seen(db, node, data.latitude, data.longitude)
    return await telemetry_crud.create(db, node.id, data)


@router.get("/{device_code}/telemetry", response_model=List[TelemetryResponse])
async def get_telemetry(
    device_code: str,
    limit: int = Query(default=100, le=1000),
    db: AsyncSession = Depends(get_db_session),
):
    node = await node_crud.get_by_device_code(db, device_code)
    if not node:
        raise HTTPException(status_code=404, detail="Nodo no encontrado")
    return await telemetry_crud.get_by_node(db, node.id, limit)
