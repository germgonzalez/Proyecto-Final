from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.api.deps import get_db_session
from app.crud import alert as alert_crud
from app.schemas.alert import AlertResponse, AlertCreate
from app.models.alert import Alert

router = APIRouter()


@router.get("/", response_model=List[AlertResponse])
async def list_alerts(
    include_resolved: bool = False,
    db: AsyncSession = Depends(get_db_session),
):
    return await alert_crud.get_all(db, include_resolved)


@router.post("/", response_model=AlertResponse, status_code=201)
async def create_alert(data: AlertCreate, db: AsyncSession = Depends(get_db_session)):
    return await alert_crud.create(db, data)


@router.patch("/{alert_id}/resolve", response_model=AlertResponse)
async def resolve_alert(alert_id: int, db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
    return await alert_crud.resolve(db, alert)
