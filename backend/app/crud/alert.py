from datetime import datetime, timezone
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.alert import Alert
from app.schemas.alert import AlertCreate


async def create(db: AsyncSession, data: AlertCreate) -> Alert:
    alert = Alert(**data.model_dump())
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    return alert


async def get_all(db: AsyncSession, include_resolved: bool = False) -> List[Alert]:
    query = select(Alert)
    if not include_resolved:
        query = query.where(Alert.is_resolved == False)  # noqa: E712
    result = await db.execute(query.order_by(Alert.created_at.desc()))
    return list(result.scalars().all())


async def resolve(db: AsyncSession, alert: Alert) -> Alert:
    alert.is_resolved = True
    alert.resolved_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(alert)
    return alert
